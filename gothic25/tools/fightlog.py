#!/usr/bin/env python3
"""Report on the melee fight log written by the engine (spec 003, format: gothic25/tests/README.md).

The log is JSON Lines (fightlog.jsonl). Script strings (names) keep their legacy codepage bytes
as \\u00XX escapes; they are decoded here with --codepage (cp1250 by default).

"check" also evaluates the "expect <who> <metric> <op> <value>" lines of the scenario, adds them to
the report and exits with 1 when an expectation or the scenario itself failed.

Usage:
  fightlog.py report RUN_DIR|FIGHTLOG [--out REPORT] [--codepage CP] [--constants AI_CONSTANTS_D]
  fightlog.py check  RUN_DIR|FIGHTLOG [--scenario FILE] [--out REPORT] [--codepage CP] [--constants AI_CONSTANTS_D]
"""

from __future__ import annotations

import argparse
import json
import operator
import re
import statistics
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

MOD_ROOT = Path(__file__).resolve().parent.parent
AI_CONSTANTS = MOD_ROOT / "content" / "Scripts" / "Content" / "AI" / "AI_Intern" / "AI_Constants.d"

SERIES_KINDS = ["attack", "side", "front", "triple", "whirl", "master", "combo"]
RESULTS = ["hit", "block", "jumpback", "miss"]
DOWN_STATES = ["stumble", "fly", "lie", "unconscious", "dead"]

# metric names of tests/README.md; counters are 0 when nothing happened, statistics have no data then
KNOWN_METRIC = re.compile(
    r"^(attacks|attacks\.tgt_down|attacks\.dir\.\w+|res\.(hit|block|jumpback|miss)|res\.miss\.\w+|taken\.(hit|block|jumpback)"
    r"|combo\.max|combo\.count\.\d+|series\.(attack|side|front|triple|whirl|master|combo|multi)|break\.\w+"
    r"|skip\.(max_ms|avg_ms)|link\.(min_pct|avg_pct)|damage\.stage\.\d+\.(avg|count|max)|damage\.(min|max)"
    r"|state\.\w+|bonus\.stage\.\d+\.(min|max)|bonus\.dir\.\w+\.max)$")
STATISTIC = re.compile(r"^(combo\.max|skip\.\w+|link\.\w+|damage\.stage\.\d+\.(avg|max)|damage\.(min|max)"
                       r"|bonus\.\S+)$")
OPS = {"==": operator.eq, "!=": operator.ne, "<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}


def decode(text: str | None, codepage: str) -> str | None:
    """Turn \\u00XX escapes of legacy bytes back into text."""
    if text is None or all(ord(c) < 0x80 for c in text):
        return text
    try:
        return text.encode("latin-1").decode(codepage, errors="replace")
    except UnicodeEncodeError:
        return text


def load_log(path: Path, codepage: str) -> list[dict]:
    events = []
    with path.open(encoding="utf-8") as f:
        for num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{num}: invalid JSON: {e}")
            if "name" in ev:
                ev["name"] = decode(ev["name"], codepage)
            for key in ("text", "file"):
                if key in ev:
                    ev[key] = decode(ev[key], "utf-8")
            events.append(ev)
    return events


def load_tactics(path: Path) -> dict[int, str]:
    """FAI_* constants of the scripts: fight tactic id -> name."""
    if not path.is_file():
        return {}
    ret = {}
    text = path.read_text(encoding="cp1250", errors="replace")
    for name, value in re.findall(r"(?im)^\s*const\s+int\s+(FAI_\w+)\s*=\s*(\d+)\s*;", text):
        ret.setdefault(int(value), name)
    return ret


@dataclass
class Character:
    id: int
    who: str
    player: bool
    name: str = ""
    tactics: set[int] = field(default_factory=set)
    weapons: Counter = field(default_factory=Counter)
    talent_pct: set[int] = field(default_factory=set)


def characters(events: list[dict]) -> dict[int, Character]:
    ret: dict[int, Character] = {}
    for ev in events:
        if "who_id" in ev:
            if ev["who_id"] not in ret:
                ret[ev["who_id"]] = Character(ev["who_id"], ev["who"], ev["player"])
            # characters seen first as a target don't carry the player flag
            ret[ev["who_id"]].player |= ev["player"]
        for key, inst in (("tgt_id", "tgt"), ("by_id", "by")):
            if ev.get(key) is not None and ev[key] not in ret:
                ret[ev[key]] = Character(ev[key], ev[inst], False)
        if ev["ev"] == "attack":
            c = ret[ev["who_id"]]
            c.name = ev["name"]
            c.tactics.add(ev["tactic"])
            c.weapons[ev["weapon"]] += 1
            if ev["weapon"] in ("1h", "2h"):
                c.talent_pct.add(ev["talent_pct"])
    return ret


def combo_chains(attacks: list[dict]) -> list[int]:
    """Length of each forward combo: a chain starts with a new or side-linked hit."""
    chains = []
    current = None
    for a in attacks:
        if a["link"] == "fwd" and current is not None:
            current = a["combo"]
            continue
        if current is not None:
            chains.append(current)
        current = a["combo"]
    if current is not None:
        chains.append(current)
    return chains


def metrics(events: list[dict], ids: set[int]) -> dict[str, float]:
    """All metrics of the characters `ids` (see gothic25/tests/README.md, "Oczekiwania")."""
    m: dict[str, float] = defaultdict(float)
    attacks_by_char: dict[int, list[dict]] = defaultdict(list)
    series_seen: dict[tuple[int, int], str] = {}
    skips, links = [], []
    damage: dict[int, list[int]] = defaultdict(list)
    # combo damage bonus of hits (002) by combo stage and by attack direction
    bonus_stage: dict[int, list[int]] = defaultdict(list)
    bonus_dir: dict[str, list[int]] = defaultdict(list)
    attack_dir: dict[tuple[int, int], str] = {}

    for ev in events:
        kind = ev["ev"]
        mine = ev.get("who_id") in ids
        if kind == "attack" and mine:
            attacks_by_char[ev["who_id"]].append(ev)
            attack_dir[(ev["who_id"], ev["n"])] = ev["dir"]
            m["attacks"] += 1
            m[f"attacks.dir.{ev['dir']}"] += 1
            if ev["tgt_down"]:
                m["attacks.tgt_down"] += 1
            if ev["series"] == "combo":
                m["series.combo"] += 1
            elif ev["series"] is not None and ev["series_id"] is not None:
                key = (ev["who_id"], ev["series_id"])
                if key not in series_seen:
                    series_seen[key] = ev["series"]
                    m[f"series.{ev['series']}"] += 1
                    if ev["series_len"] > 1:
                        m["series.multi"] += 1
            if ev["link"] == "fwd":
                skips.append(ev["skip_ms"])
            if ev["link"] in ("fwd", "side") and ev["win_pct"] is not None:
                links.append(ev["win_pct"])
        elif kind == "result":
            if mine:
                m[f"res.{ev['res']}"] += 1
                if ev["res"] == "miss" and ev["why"]:
                    m[f"res.miss.{ev['why']}"] += 1
                if ev["res"] == "hit":
                    damage[ev["combo"]].append(ev["dmg"])
                    if ev.get("bonus") is not None:
                        bonus_stage[ev["combo"]].append(ev["bonus"])
                        direction = attack_dir.get((ev["who_id"], ev["n"]))
                        if direction is not None:
                            bonus_dir[direction].append(ev["bonus"])
            if ev.get("tgt_id") in ids and ev["res"] != "miss":
                m[f"taken.{ev['res']}"] += 1
        elif kind == "break" and mine:
            m[f"break.{ev['why']}"] += 1
        elif kind == "state" and mine:
            m[f"state.{ev['state']}"] += 1

    chains = [n for a in attacks_by_char.values() for n in combo_chains(a)]
    if chains:
        m["combo.max"] = max(chains)
        for n, count in Counter(chains).items():
            m[f"combo.count.{n}"] = count
    if skips:
        m["skip.max_ms"] = max(skips)
        m["skip.avg_ms"] = statistics.mean(skips)
    if links:
        m["link.min_pct"] = min(links)
        m["link.avg_pct"] = statistics.mean(links)
    for stage, values in damage.items():
        m[f"damage.stage.{stage}.avg"] = statistics.mean(values)
        m[f"damage.stage.{stage}.count"] = len(values)
        m[f"damage.stage.{stage}.max"] = max(values)
    hits = [v for values in damage.values() for v in values]
    if hits:
        m["damage.min"] = min(hits)
        m["damage.max"] = max(hits)
    for stage, values in bonus_stage.items():
        m[f"bonus.stage.{stage}.min"] = min(values)
        m[f"bonus.stage.{stage}.max"] = max(values)
    for direction, values in bonus_dir.items():
        m[f"bonus.dir.{direction}.max"] = max(values)
    return dict(m)


@dataclass
class Expectation:
    line: int
    text: str
    who: str = ""
    metric: str = ""
    op: str = ""
    value: float = 0
    actual: float | None = None
    ok: bool = False
    note: str = ""


def parse_expectations(path: Path) -> list[Expectation]:
    ret = []
    for num, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        parts = line.split()
        if not parts or parts[0].lower() != "expect":
            continue
        exp = Expectation(num, line.strip())
        try:
            _, exp.who, exp.metric, exp.op, value = parts
            exp.value = float(value)
        except ValueError:
            exp.note = "niepoprawny zapis: expect <kto> <miara> <op> <wartość>"
        if not exp.note and exp.op not in OPS:
            exp.note = f"nieznany operator {exp.op}"
        ret.append(exp)
    return ret


def evaluate(exp: Expectation, events: list[dict], chars: dict[int, Character]) -> None:
    if exp.note:
        return
    if not KNOWN_METRIC.match(exp.metric):
        exp.note = "nieznana miara"
        return
    if exp.who.lower() == "hero":
        ids = {c.id for c in chars.values() if c.player}
    else:
        ids = {c.id for c in chars.values() if c.who.lower() == exp.who.lower()}
    if not ids:
        exp.note = "brak tej postaci w dzienniku"
        return
    value = metrics(events, ids).get(exp.metric)
    if value is None:
        if STATISTIC.match(exp.metric):
            exp.note = "brak danych"
            return
        value = 0
    exp.actual = value
    exp.ok = OPS[exp.op](value, exp.value)


def expectations_section(exps: list[Expectation], status: dict | None, scenario: Path) -> tuple[str, bool]:
    passed = sum(e.ok for e in exps)
    scenario_ok = status is None or status.get("result") == "ok"
    ok = scenario_ok and passed == len(exps)
    out = ["## Oczekiwania", ""]
    out.append(f"- Scenariusz: `{scenario}`")
    if not scenario_ok and status.get("result") == "running":
        out.append("- Scenariusz się nie skończył: gra zamknęła się albo została zamknięta w trakcie")
    elif not scenario_ok:
        out.append(f"- Scenariusz nie zakończył się poprawnie: {status.get('result')}")
    if exps:
        out.append(f"- Zaliczone: {passed} z {len(exps)}")
        out.append("")
        out.append("| Linia | Kto | Miara | Oczekiwanie | Wartość | Wynik |")
        out.append("|---|---|---|---|---|---|")
        for e in exps:
            result   = "zaliczone" if e.ok else "**niezaliczone**"
            expected = f"{e.op} {fmt(e.value)}" if e.op in OPS else "–"
            actual   = fmt(e.actual) if e.actual is not None else e.note
            out.append(f"| {e.line} | {e.who or '–'} | {e.metric or '–'} | {expected} | {actual} | {result} |")
    else:
        out.append("- Scenariusz nie ma oczekiwań.")
    out.append("")
    out.append(f"**Wynik przebiegu: {'zaliczony' if ok else 'niezaliczony'}**")
    out.append("")
    return "\n".join(out), ok


def fmt(v: float | None) -> str:
    if v is None:
        return "–"
    if float(v).is_integer():
        return str(int(v))
    return f"{v:.1f}"


def bonus_range(m: dict[str, float], stage: int) -> str:
    """Combo damage bonus of a combo stage: one value or the range, '–' for logs without it."""
    lo, hi = m.get(f"bonus.stage.{stage}.min"), m.get(f"bonus.stage.{stage}.max")
    if lo is None:
        return "–"
    return f"{fmt(lo)}%" if lo == hi else f"{fmt(lo)}–{fmt(hi)}%"


def tactic_name(ids: set[int], tactics: dict[int, str]) -> str:
    return ", ".join(f"{tactics.get(t, '?')} ({t})" for t in sorted(ids)) or "–"


def describe(ev: dict) -> str:
    parts = [ev["what"], ev.get("text") or "", Path(ev["file"]).name if ev.get("file") else ""]
    line = f"linia {ev['line']}: " if ev.get("line") is not None else ""
    return line + " ".join(p for p in parts if p)


# hero techniques of spec 002 K4/K6: a pause longer than this ends a run of attacks
SEGMENT_GAP_MS = 2000
SEGMENT_MIN_ATTACKS = 3
TECHNIQUES = {"combo": "pełne combo", "side": "lewo-prawo", "first": "pierwszy cios"}
TALENT_LEVELS = {0: "nowicjusz", 1: "wojownik", 2: "mistrz"}
MIN_DAMAGE = 5


@dataclass
class Segment:
    technique: str
    weapon: str
    talent: int
    talent_pct: int
    attacks: list[dict] = field(default_factory=list)


def hero_segments(events: list[dict]) -> list[Segment]:
    """Runs of hero attacks of one technique: full forward combos, left-right, repeated first hit."""
    hero = [e for e in events if e["ev"] == "attack" and e["player"]]
    segments: list[Segment] = []
    for i, a in enumerate(hero):
        nxt = hero[i + 1] if i + 1 < len(hero) else None
        if a["dir"] in ("left", "right"):
            technique = "side"
        elif a["dir"] == "fwd" and (a["link"] == "fwd" or (nxt is not None and nxt["link"] == "fwd")):
            technique = "combo"
        elif a["dir"] == "fwd":
            technique = "first"
        else:
            continue  # run attacks and finishing moves are no technique of K4
        cur = segments[-1] if segments else None
        if (cur is None or cur.technique != technique or cur.weapon != a["weapon"] or cur.talent != a["talent"]
                or a["t"] - cur.attacks[-1]["t"] > SEGMENT_GAP_MS):
            cur = Segment(technique, a["weapon"], a["talent"], a["talent_pct"])
            segments.append(cur)
        cur.attacks.append(a)
    return [s for s in segments if len(s.attacks) >= SEGMENT_MIN_ATTACKS]


def hit_damage(result: dict | None, attack: dict, bonus: list[int] | None) -> int:
    """Damage of a hit; with `bonus` the forward combo bonus is replaced by that table (percent per hit)."""
    if result is None or result["res"] != "hit":
        return 0
    dmg = result["dmg"]
    if bonus is None or attack["dir"] != "fwd" or not result.get("bonus"):
        return dmg
    base = dmg * 100 / result["bonus"]
    stage = min(result["combo"], len(bonus)) - 1
    return max(round(base * bonus[stage] / 100), MIN_DAMAGE)


def techniques_section(events: list[dict], bonus: list[int] | None) -> list[str]:
    """K4/K6 of spec 002: damage per second of each hero technique, per weapon and talent level."""
    segments = hero_segments(events)
    if not segments:
        return []
    results = {(e["who_id"], e["n"]): e for e in events if e["ev"] == "result" and e["player"]}

    groups: dict[tuple, dict] = {}
    for s in segments:
        gaps = [b["t"] - a["t"] for a, b in zip(s.attacks, s.attacks[1:])]
        g = groups.setdefault((s.weapon, s.talent, s.technique),
                              {"pct": s.talent_pct, "runs": 0, "attacks": 0, "ms": 0.0, "dmg": 0, "gaps": []})
        g["runs"] += 1
        g["attacks"] += len(s.attacks)
        g["ms"] += s.attacks[-1]["t"] - s.attacks[0]["t"] + statistics.median(gaps)  # the last attack takes a step too
        g["gaps"] += gaps
        g["dmg"] += sum(hit_damage(results.get((a["who_id"], a["n"])), a, bonus) for a in s.attacks)

    out = ["## Techniki bohatera", ""]
    out.append(f"Odcinki co najmniej {SEGMENT_MIN_ATTACKS} ciosów bohatera jednej techniki; przerwa dłuższa niż "
               f"{SEGMENT_GAP_MS / 1000:g} s kończy odcinek. Obrażenia na sekundę: suma obrażeń przez czas odcinków.")
    if bonus is not None:
        out.append(f"Premie ciosów do przodu przeliczone dla `--bonus {','.join(str(b) for b in bonus)}`.")
    out.append("")
    out.append("| Broń | Talent | Technika | Odcinki | Ciosy | Czas na cios (s) | Odstępy (s): mediana, min–max "
               "| Obrażenia na cios | Obrażenia na sekundę |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    order = list(TECHNIQUES)
    dps: dict[tuple, float] = {}
    for key in sorted(groups, key=lambda k: (k[0], k[1], order.index(k[2]))):
        weapon, talent, technique = key
        g = groups[key]
        rate = g["dmg"] / (g["ms"] / 1000) if g["ms"] > 0 else 0.0
        dps[key] = rate
        level = "pięści" if weapon == "fist" else f"{TALENT_LEVELS.get(talent, talent)} ({g['pct']}%)"
        out.append(f"| {weapon} | {level} | {TECHNIQUES[technique]} | {g['runs']} | {g['attacks']} "
                   f"| {g['ms'] / 1000 / g['attacks']:.2f} | {statistics.median(g['gaps']) / 1000:.2f}, "
                   f"{min(g['gaps']) / 1000:.2f}–{max(g['gaps']) / 1000:.2f} | {g['dmg'] / g['attacks']:.1f} "
                   f"| {rate:.1f} |")
    out.append("")
    for weapon, talent in sorted({(w, t) for w, t, _ in dps}):
        combo = dps.get((weapon, talent, "combo"))
        others = [dps[(weapon, talent, t)] for t in ("side", "first") if (weapon, talent, t) in dps]
        if combo is not None and others and max(others) > 0:  # a run without hits has no rate to compare
            gain = (combo / max(others) - 1) * 100
            level = "pięści" if weapon == "fist" else TALENT_LEVELS.get(talent, talent)
            out.append(f"- {weapon}, {level}: przewaga pełnego combo nad lepszą z pozostałych technik "
                       f"{gain:+.0f}% (W5: co najmniej +20% u mistrza)")
    out.append("")
    return out


def report(events: list[dict], tactics: dict[int, str], source: Path, status: dict | None,
           bonus: list[int] | None = None) -> str:
    out: list[str] = []
    meta = next((e for e in events if e["ev"] == "meta"), {})
    start = next((e for e in events if e["ev"] == "marker" and e["what"] == "scenario_start"), None)
    duration = max((e["t"] for e in events), default=0)
    chars = characters(events)

    out.append("# Raport walki")
    out.append("")
    out.append(f"- Dziennik: `{source}`")
    out.append(f"- Świat: {meta.get('world') or '–'}, mod: {meta.get('mod') or 'bez moda'}")
    if start is not None:
        out.append(f"- Scenariusz: `{start.get('text')}`")
    if status is not None:
        msg = f" (linia {status['line']}: {status['message']})" if status.get("line") is not None else ""
        out.append(f"- Wynik scenariusza: **{status.get('result')}**{msg}")
    out.append(f"- Czas gry w dzienniku: {duration / 1000:.1f} s")
    out.append("")

    out.append("## Postacie")
    out.append("")
    out.append("| # | Instancja | Imię | Styl walki | Broń | Talent % | Ciosy | Trafienia | Bloki/odskoki | Pudła | Najdłuższe combo |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    per_char = {}
    for cid in sorted(chars):
        c = chars[cid]
        m = metrics(events, {cid})
        per_char[cid] = m
        who = c.who + (" (bohater)" if c.player else "")
        weapons = ", ".join(w for w, _ in c.weapons.most_common()) or "–"
        talent = ", ".join(str(t) for t in sorted(c.talent_pct)) or "–"
        out.append(f"| {cid} | {who} | {c.name or '–'} | {tactic_name(c.tactics, tactics)} | {weapons} | {talent} | "
                   f"{fmt(m.get('attacks', 0))} | {fmt(m.get('res.hit', 0))} | "
                   f"{fmt(m.get('res.block', 0) + m.get('res.jumpback', 0))} | {fmt(m.get('res.miss', 0))} | "
                   f"{fmt(m.get('combo.max'))} |")
    out.append("")

    for cid in sorted(chars):
        c, m = chars[cid], per_char[cid]
        if not m:
            continue
        out.append(f"## {c.who} (#{cid}{', ' + c.name if c.name else ''})")
        out.append("")
        series = [(k, m.get(f"series.{k}", 0)) for k in SERIES_KINDS]
        if any(v for _, v in series):
            out.append("- Serie: " + ", ".join(f"{k} {fmt(v)}" for k, v in series if v)
                       + ("  (combo: ciosy z kontynuacji)" if m.get("series.combo") else ""))
        combos = sorted((int(k.rsplit(".", 1)[1]), v) for k, v in m.items() if k.startswith("combo.count."))
        if combos:
            out.append("- Combo do przodu (długość: liczba): " + ", ".join(f"{n}: {fmt(v)}" for n, v in combos))
        if "skip.max_ms" in m or "link.min_pct" in m:
            out.append(f"- Połączenia: chwila w oknie min {fmt(m.get('link.min_pct'))}%, "
                       f"średnio {fmt(m.get('link.avg_pct'))}%; pominięte ms średnio {fmt(m.get('skip.avg_ms'))}, "
                       f"najwięcej {fmt(m.get('skip.max_ms'))}")
        res = [(r, m.get(f"res.{r}", 0)) for r in RESULTS]
        if any(v for _, v in res):
            why = ", ".join(f"{k.split('.')[-1]} {fmt(v)}" for k, v in sorted(m.items()) if k.startswith("res.miss."))
            out.append("- Wyniki ciosów: " + ", ".join(f"{r} {fmt(v)}" for r, v in res if v)
                       + (f" (pudła: {why})" if why else ""))
        taken = [(r, m.get(f"taken.{r}", 0)) for r in RESULTS[:3]]
        if any(v for _, v in taken):
            out.append("- Ciosy przyjęte: " + ", ".join(f"{r} {fmt(v)}" for r, v in taken if v))
        breaks = sorted((k.split(".", 1)[1], v) for k, v in m.items() if k.startswith("break."))
        if breaks:
            out.append("- Przerwania: " + ", ".join(f"{k} {fmt(v)}" for k, v in breaks))
        states = [(s, m.get(f"state.{s}", 0)) for s in DOWN_STATES]
        if any(v for _, v in states):
            out.append("- Stany: " + ", ".join(f"{s} {fmt(v)}" for s, v in states if v))
        stages = sorted(int(k.split(".")[2]) for k in m if k.startswith("damage.stage.") and k.endswith(".count"))
        if stages:
            out.append("")
            out.append("| Etap combo | Trafienia | Średnie obrażenia | Premia |")
            out.append("|---|---|---|---|")
            for s in stages:
                out.append(f"| {s} | {fmt(m[f'damage.stage.{s}.count'])} | {fmt(m[f'damage.stage.{s}.avg'])} "
                           f"| {bonus_range(m, s)} |")
        out.append("")

    out += techniques_section(events, bonus)

    markers = [e for e in events if e["ev"] == "marker" and e["what"] not in ("line", "scenario_start")]
    if markers:
        out.append("## Znaczniki")
        out.append("")
        for e in markers:
            out.append(f"- {e['t'] / 1000:.1f} s: {describe(e)}")
        out.append("")
    return "\n".join(out)


def resolve(path: Path) -> tuple[Path, Path | None]:
    """Fight log and scenario.json of a run directory, or a fight log file alone."""
    if path.is_dir():
        log = path / "fightlog.jsonl"
        status = path / "scenario.json"
        return log, status if status.is_file() else None
    return path, None


def load_run(args) -> tuple[Path, list[dict], dict | None]:
    log, status_file = resolve(Path(args.path))
    if not log.is_file():
        raise SystemExit(f"no fight log: {log}")
    events = load_log(log, args.codepage)
    status = json.loads(status_file.read_text(encoding="utf-8")) if status_file else None
    return log, events, status


def find_scenario(args, log: Path, events: list[dict]) -> Path:
    """--scenario, the copy in the run directory (tools/test.ps1), or the file the engine ran."""
    if args.scenario:
        return Path(args.scenario)
    copy = log.with_name("scenario.txt")
    if copy.is_file():
        return copy
    start = next((e for e in events if e["ev"] == "marker" and e["what"] == "scenario_start"), None)
    if start is not None and start.get("text") and Path(start["text"]).is_file():
        return Path(start["text"])
    raise SystemExit("no scenario file: pass --scenario")


def cmd_report(args) -> None:
    log, events, status = load_run(args)
    bonus = [int(v) for v in args.bonus.split(",")] if args.bonus else None
    text = report(events, load_tactics(Path(args.constants)), log, status, bonus)
    out = Path(args.out) if args.out else log.with_name("report.md")
    out.write_text(text + "\n", encoding="utf-8")
    print(f"report: {out}")


def cmd_check(args) -> int:
    log, events, status = load_run(args)
    scenario = find_scenario(args, log, events)
    exps = parse_expectations(scenario)
    chars = characters(events)
    for e in exps:
        evaluate(e, events, chars)

    section, ok = expectations_section(exps, status, scenario)
    text = report(events, load_tactics(Path(args.constants)), log, status)
    out = Path(args.out) if args.out else log.with_name("report.md")
    out.write_text(text + "\n" + section, encoding="utf-8")

    for e in exps:
        actual = fmt(e.actual) if e.actual is not None else e.note
        print(f"{'ok  ' if e.ok else 'FAIL'} line {e.line}: {e.who} {e.metric} {e.op} {fmt(e.value)} (actual: {actual})")
    if status is not None and status.get("result") == "running":
        print("FAIL scenario: did not finish, the game ended or was closed during it")
    elif status is not None and status.get("result") != "ok":
        print(f"FAIL scenario: {status.get('result')} at line {status.get('line')}: {status.get('message')}")
    print(f"report: {out}")
    print("result: " + ("passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("report", help="write report.md for a run directory or a fight log")
    p.add_argument("path", help="run directory with fightlog.jsonl, or the fight log itself")
    p.add_argument("--out", help="report file (default: report.md next to the log)")
    p.add_argument("--codepage", default="cp1250", help="codepage of script strings (default: cp1250)")
    p.add_argument("--constants", default=str(AI_CONSTANTS), help="AI_Constants.d with the FAI_* tactic names")
    p.add_argument("--bonus", help="combo damage bonus per forward hit in percent, e.g. 100,175,275,400: "
                                  "hero techniques are recomputed with it (spec 002)")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("check", help="report plus the expectations of the scenario; exit code 1 on failure")
    p.add_argument("path", help="run directory with fightlog.jsonl, or the fight log itself")
    p.add_argument("--scenario", help="scenario file (default: scenario.txt of the run, or the file the engine ran)")
    p.add_argument("--out", help="report file (default: report.md next to the log)")
    p.add_argument("--codepage", default="cp1250", help="codepage of script strings (default: cp1250)")
    p.add_argument("--constants", default=str(AI_CONSTANTS), help="AI_Constants.d with the FAI_* tactic names")
    p.set_defaults(func=cmd_check)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
