#!/usr/bin/env python3
"""Report on the melee fight log written by the engine (spec 003, format: gothic25/tests/README.md).

The log is JSON Lines (fightlog.jsonl). Script strings (names) keep their legacy codepage bytes
as \\u00XX escapes; they are decoded here with --codepage (cp1250 by default).

Usage:
  fightlog.py report RUN_DIR|FIGHTLOG [--out REPORT] [--codepage CP] [--constants AI_CONSTANTS_D]
"""

from __future__ import annotations

import argparse
import json
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

    for ev in events:
        kind = ev["ev"]
        mine = ev.get("who_id") in ids
        if kind == "attack" and mine:
            attacks_by_char[ev["who_id"]].append(ev)
            m["attacks"] += 1
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
    return dict(m)


def fmt(v: float | None) -> str:
    if v is None:
        return "–"
    if float(v).is_integer():
        return str(int(v))
    return f"{v:.1f}"


def tactic_name(ids: set[int], tactics: dict[int, str]) -> str:
    return ", ".join(f"{tactics.get(t, '?')} ({t})" for t in sorted(ids)) or "–"


def describe(ev: dict) -> str:
    parts = [ev["what"], ev.get("text") or "", Path(ev["file"]).name if ev.get("file") else ""]
    line = f"linia {ev['line']}: " if ev.get("line") is not None else ""
    return line + " ".join(p for p in parts if p)


def report(events: list[dict], tactics: dict[int, str], source: Path, status: dict | None) -> str:
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
            out.append("| Etap combo | Trafienia | Średnie obrażenia |")
            out.append("|---|---|---|")
            for s in stages:
                out.append(f"| {s} | {fmt(m[f'damage.stage.{s}.count'])} | {fmt(m[f'damage.stage.{s}.avg'])} |")
        out.append("")

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


def cmd_report(args) -> None:
    log, status_file = resolve(Path(args.path))
    if not log.is_file():
        raise SystemExit(f"no fight log: {log}")
    events = load_log(log, args.codepage)
    status = json.loads(status_file.read_text(encoding="utf-8")) if status_file else None
    text = report(events, load_tactics(Path(args.constants)), log, status)
    out = Path(args.out) if args.out else log.with_name("report.md")
    out.write_text(text + "\n", encoding="utf-8")
    print(f"report: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("report", help="write report.md for a run directory or a fight log")
    p.add_argument("path", help="run directory with fightlog.jsonl, or the fight log itself")
    p.add_argument("--out", help="report file (default: report.md next to the log)")
    p.add_argument("--codepage", default="cp1250", help="codepage of script strings (default: cp1250)")
    p.add_argument("--constants", default=str(AI_CONSTANTS), help="AI_Constants.d with the FAI_* tactic names")
    p.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    sys.exit(main())
