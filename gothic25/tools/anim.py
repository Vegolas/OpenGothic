#!/usr/bin/env python3
"""Animations of the mod: ZenGin MAN and MDH files and the .anim text format (spec 004, ADR 0007).

Standard library only. Binary layouts mirror lib/ZenKit/src/ModelAnimation.cc and ModelHierarchy.cc:
every file is a list of chunks "uint16 type | uint32 size | payload".

  MAN 0xA020 header : uint16 version | name\\n | layer u32 | frame_count u32 | node_count u32
                      | fps f32 | fps_source f32 | pos_min f32 | pos_scale f32 | bbox 6 x f32 | next\\n
  MAN 0xA090 samples: checksum u32 | node_count x u32 node index | frame-major samples,
                      each rotation 3 x u16 then position 3 x u16
  MAN other chunks  : 0xA000 marker, 0xA010 source, 0xA030 events (the engine takes events from MSB)
  MDH 0xD100        : version u32 | node count u16 | per node: name\\n | parent i16 | 16 x f32
                      | bbox 6 x f32 | collision bbox 6 x f32 | root translation 3 x f32 | checksum u32

The .anim text keeps every MAN field, so MAN -> .anim -> MAN gives the same bytes:

  g25-anim 1
  model HUMANS                     model script name, the MAN file is <model>-<name>.MAN
  name S_RUN
  next S_RUN
  version 12
  layer 1
  fps 25.0 25.0                    fps and source fps
  checksum C63488C2                checksum of the model hierarchy (MDH)
  bbox <6 floats>
  quant <min> <scale>              position quantization; omitted: fitted to the samples
  layout A000 A020 A010 A090       chunk order; omitted: A000 A020 A090
  raw A010 <base64>                chunks kept as they are (source, events)
  nodes 34
  node 0 BIP01                     MDH node index and name, in sample order
  frames 50
  frame 0
  1.0000000 0.0000000 0.0000000 0.0000000 0.00000 97.71300 7.37700
                                   one line per node: quaternion w x y z, position in cm

Floats of the header are written with repr(), which reads back to the same float32. Sample values
are rounded far below the quantization step, so they encode to the same codes.

Usage:
  anim.py to-text FILE.MAN [--model NAME] [--out FILE.anim]
  anim.py from-text FILE.anim --out FILE.MAN
  anim.py skeleton FILE.MDH [--out FILE.json]
  anim.py extract MODEL --gothic DIR [--out DIR] [--mesh NAME.MDM]
  anim.py roundtrip MODEL --gothic DIR
"""

from __future__ import annotations

import argparse
import base64
import fnmatch
import json
import math
import os
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vdf  # noqa: E402

ROT_RANGE = float((1 << 16) - 1)
ROT_SCALE = (1.0 / ROT_RANGE) * 2.1
ROT_MID = (1 << 15) - 1

MAN_MARKER, MAN_SOURCE, MAN_HEADER, MAN_EVENTS, MAN_SAMPLES = 0xA000, 0xA010, 0xA020, 0xA030, 0xA090
MDH_HIERARCHY, MDH_SOURCE, MDH_END = 0xD100, 0xD110, 0xD120
DEFAULT_LAYOUT = [MAN_MARKER, MAN_HEADER, MAN_SAMPLES]
ANIM_MAGIC = "g25-anim 1"
ANIMS_DIR = "_WORK/DATA/ANIMS/_COMPILED/"
ENCODING = "cp1252"


class Reader:
    def __init__(self, data: bytes):
        self.data, self.pos = data, 0

    def unpack(self, fmt: str):
        s = struct.Struct("<" + fmt)
        v = s.unpack_from(self.data, self.pos)
        self.pos += s.size
        return v

    def line(self) -> str:
        # zenkit::Read::read_line: stops at \0, \r or \n
        end = self.pos
        while end < len(self.data) and self.data[end] not in (0, 10, 13):
            end += 1
        text = self.data[self.pos:end].decode(ENCODING)
        self.pos = min(end + 1, len(self.data))
        return text


def chunks(data: bytes):
    pos = 0
    while pos + 6 <= len(data):
        ctype, size = struct.unpack_from("<HI", data, pos)
        yield ctype, data[pos + 6:pos + 6 + size]
        pos += 6 + size
    if pos != len(data):
        raise ValueError(f"trailing {len(data) - pos} bytes after the last chunk")


def chunk(ctype: int, payload: bytes) -> bytes:
    return struct.pack("<HI", ctype, len(payload)) + payload


# --- MDH --------------------------------------------------------------------------------------------

@dataclass
class MdhNode:
    name: str
    parent: int  # -1 for a root
    matrix: tuple  # 16 floats as stored


@dataclass
class Mdh:
    version: int = 0
    nodes: list = field(default_factory=list)
    bbox: tuple = ()
    collision_bbox: tuple = ()
    root_translation: tuple = ()
    checksum: int = 0


def parse_mdh(data: bytes) -> Mdh:
    m = Mdh()
    for ctype, payload in chunks(data):
        if ctype != MDH_HIERARCHY:
            continue
        r = Reader(payload)
        m.version = r.unpack("I")[0]
        for _ in range(r.unpack("H")[0]):
            name = r.line()
            parent = r.unpack("h")[0]
            m.nodes.append(MdhNode(name, parent, r.unpack("16f")))
        m.bbox = r.unpack("6f")
        m.collision_bbox = r.unpack("6f")
        m.root_translation = r.unpack("3f")
        m.checksum = r.unpack("I")[0]
    return m


# --- MAN --------------------------------------------------------------------------------------------

@dataclass
class Man:
    model: str = ""
    name: str = ""
    next: str = ""
    version: int = 0
    layer: int = 0
    fps: float = 25.0
    fps_source: float = 25.0
    checksum: int = 0
    bbox: tuple = (0.0,) * 6
    quant: tuple | None = None  # (pos_min, pos_scale) as stored
    layout: list = field(default_factory=lambda: list(DEFAULT_LAYOUT))
    raw: dict = field(default_factory=dict)  # chunk type -> payload kept as it is
    node_indices: list = field(default_factory=list)
    node_names: list = field(default_factory=list)
    # samples[frame][k] = (w, x, y, z, px, py, pz); w is implicit in the file
    samples: list = field(default_factory=list)

    @property
    def frame_count(self) -> int:
        return len(self.samples)


def parse_man(data: bytes, model: str = "") -> Man:
    a = Man(model=model, layout=[])
    frame_count = node_count = 0
    for ctype, payload in chunks(data):
        a.layout.append(ctype)
        r = Reader(payload)
        if ctype == MAN_HEADER:
            a.version = r.unpack("H")[0]
            a.name = r.line()
            a.layer, frame_count, node_count = r.unpack("3I")
            a.fps, a.fps_source, pos_min, pos_scale = r.unpack("4f")
            a.quant = (pos_min, pos_scale)
            a.bbox = r.unpack("6f")
            a.next = r.line()
            if r.pos != len(payload):
                raise ValueError(f"{a.name}: {len(payload) - r.pos} unknown bytes in the header")
        elif ctype == MAN_SAMPLES:
            a.checksum = r.unpack("I")[0]
            a.node_indices = list(r.unpack(f"{node_count}I"))
            codes = r.unpack(f"{node_count * frame_count * 6}H")
            if r.pos != len(payload):
                raise ValueError(f"{a.name}: {len(payload) - r.pos} unknown bytes in the samples")
            pos_min, pos_scale = a.quant
            for f in range(frame_count):
                row = []
                for k in range(node_count):
                    rx, ry, rz, px, py, pz = codes[(f * node_count + k) * 6:(f * node_count + k) * 6 + 6]
                    # unnormalized x, y, z keep the codes exact; zenkit normalizes |xyz| > 1 at load
                    x, y, z = ((v - ROT_MID) * ROT_SCALE for v in (rx, ry, rz))
                    w = math.sqrt(max(0.0, 1.0 - (x * x + y * y + z * z)))
                    row.append((w, x, y, z) + tuple(v * pos_scale + pos_min for v in (px, py, pz)))
                a.samples.append(row)
        elif ctype != MAN_MARKER or payload:
            a.raw[ctype] = payload
    if MAN_HEADER not in a.layout or MAN_SAMPLES not in a.layout:
        raise ValueError("not an animation: no header or no samples chunk")
    return a


def f32(v: float) -> float:
    return struct.unpack("<f", struct.pack("<f", v))[0]


def fit_quant(samples: list) -> tuple:
    flat = [c for row in samples for s in row for c in s[4:7]]
    lo, hi = min(flat), max(flat)
    return f32(lo), f32((hi - lo) / 65535.0 if hi > lo else 1.0)


def encode_rot(w: float, x: float, y: float, z: float) -> tuple:
    if w < 0:  # w is implicit and always read back as >= 0
        x, y, z = -x, -y, -z
    return tuple(min(65535, max(0, int(round(v / ROT_SCALE + ROT_MID)))) for v in (x, y, z))


def write_man(a: Man) -> bytes:
    if not a.samples:
        raise ValueError(f"{a.name}: animation has no frames")
    node_count = len(a.node_indices)
    if any(len(row) != node_count for row in a.samples):
        raise ValueError(f"{a.name}: every frame needs {node_count} samples")
    pos_min, pos_scale = a.quant if a.quant is not None else fit_quant(a.samples)

    def line(s: str) -> bytes:
        return s.encode(ENCODING) + b"\n"

    hdr = struct.pack("<H", a.version) + line(a.name)
    hdr += struct.pack("<3I", a.layer, a.frame_count, node_count)
    hdr += struct.pack("<4f", a.fps, a.fps_source, pos_min, pos_scale)
    hdr += struct.pack("<6f", *a.bbox) + line(a.next)

    def encode_pos(v: float) -> int:
        # scale 0: every position is pos_min, original files store code 0
        if pos_scale == 0:
            return 0
        return min(65535, max(0, int(round((v - pos_min) / pos_scale))))

    body = bytearray(struct.pack("<I", a.checksum))
    body += struct.pack(f"<{node_count}I", *a.node_indices)
    for row in a.samples:
        for w, x, y, z, px, py, pz in row:
            body += struct.pack("<3H", *encode_rot(w, x, y, z))
            body += struct.pack("<3H", encode_pos(px), encode_pos(py), encode_pos(pz))

    out = bytearray()
    for ctype in a.layout:
        if ctype == MAN_HEADER:
            out += chunk(ctype, hdr)
        elif ctype == MAN_SAMPLES:
            out += chunk(ctype, bytes(body))
        elif ctype == MAN_MARKER and ctype not in a.raw:
            out += chunk(ctype, b"")
        else:
            out += chunk(ctype, a.raw[ctype])
    return bytes(out)


def quant_covers(quant: tuple, samples: list) -> bool:
    lo, scale = quant
    hi = lo + 65535 * scale
    return all(lo - scale <= c <= hi + scale for row in samples for s in row for c in s[4:7])


def snap(a: Man) -> Man:
    """Replaces every sample with the value its MAN code decodes to, so the text is canonical: an
    unchanged animation gives the same .anim as to-text of its MAN, without float noise."""
    if a.quant is None or not quant_covers(a.quant, a.samples):
        a.quant = fit_quant(a.samples)
    a.samples = parse_man(write_man(a), a.model).samples
    return a


# --- .anim text --------------------------------------------------------------------------------------

def pos_digits(quant: tuple | None) -> int:
    # 20 times finer than the quantization step, at least 5 decimals (0.00001 cm)
    if quant is None or quant[1] <= 0:
        return 5
    return max(5, math.ceil(-math.log10(quant[1] / 20.0)))


def to_text(a: Man) -> str:
    out = [ANIM_MAGIC, f"model {a.model}", f"name {a.name}", f"next {a.next}".rstrip(),
           f"version {a.version}", f"layer {a.layer}", f"fps {a.fps!r} {a.fps_source!r}",
           f"checksum {a.checksum:08X}", "bbox " + " ".join(repr(v) for v in a.bbox)]
    if a.quant is not None:
        out.append(f"quant {a.quant[0]!r} {a.quant[1]!r}")
    if a.layout != DEFAULT_LAYOUT:
        out.append("layout " + " ".join(f"{c:04X}" for c in a.layout))
    for ctype in sorted(a.raw):
        out.append(f"raw {ctype:04X} {base64.b64encode(a.raw[ctype]).decode('ascii')}".rstrip())
    out.append(f"nodes {len(a.node_indices)}")
    for index, name in zip(a.node_indices, a.node_names or [""] * len(a.node_indices)):
        out.append(f"node {index} {name}".rstrip())
    out.append(f"frames {a.frame_count}")
    pd = pos_digits(a.quant)
    for f, row in enumerate(a.samples):
        out.append(f"frame {f}")
        for w, x, y, z, px, py, pz in row:
            out.append(f"{w:.7f} {x:.7f} {y:.7f} {z:.7f} {px:.{pd}f} {py:.{pd}f} {pz:.{pd}f}")
    return "\n".join(out) + "\n"


def from_text(text: str, source: str = "<text>") -> Man:
    lines = text.splitlines()
    if not lines or lines[0].strip() != ANIM_MAGIC:
        raise ValueError(f"{source}: not a .anim file (first line must be '{ANIM_MAGIC}')")
    a = Man(raw={})
    i, frames = 1, None

    def fail(msg: str):
        raise ValueError(f"{source}:{i + 1}: {msg}")

    while i < len(lines):
        key, _, rest = lines[i].partition(" ")
        if key == "model":
            a.model = rest
        elif key == "name":
            a.name = rest
        elif key == "next":
            a.next = rest
        elif key == "version":
            a.version = int(rest)
        elif key == "layer":
            a.layer = int(rest)
        elif key == "fps":
            a.fps, a.fps_source = (float(v) for v in rest.split())
        elif key == "checksum":
            a.checksum = int(rest, 16)
        elif key == "bbox":
            a.bbox = tuple(float(v) for v in rest.split())
            if len(a.bbox) != 6:
                fail("bbox needs 6 values")
        elif key == "quant":
            a.quant = tuple(float(v) for v in rest.split())
        elif key == "layout":
            a.layout = [int(c, 16) for c in rest.split()]
        elif key == "raw":
            ctype, _, payload = rest.partition(" ")
            a.raw[int(ctype, 16)] = base64.b64decode(payload)
        elif key == "nodes":
            pass
        elif key == "node":
            index, _, name = rest.partition(" ")
            a.node_indices.append(int(index))
            a.node_names.append(name)
        elif key == "frames":
            frames = int(rest)
            i += 1
            break
        elif key:
            fail(f"unknown key '{key}'")
        i += 1
    if frames is None:
        fail("no 'frames' line")
    n = len(a.node_indices)
    for f in range(frames):
        if i >= len(lines) or lines[i] != f"frame {f}":
            fail(f"expected 'frame {f}'")
        i += 1
        row = []
        for _ in range(n):
            if i >= len(lines):
                fail("file ends inside a frame")
            values = lines[i].split()
            if len(values) != 7:
                fail("a sample needs 7 values: w x y z px py pz")
            row.append(tuple(float(v) for v in values))
            i += 1
        a.samples.append(row)
    if i != len(lines):
        fail("unexpected lines after the last frame")
    return a


# --- game archives ------------------------------------------------------------------------------------

def game_archives(gothic: Path) -> list[Path]:
    """Original archives in the order the engine searches them (Resources::mountVdfs): newer first."""
    found = []
    for p in sorted((gothic / "Data").glob("*.vdf"), key=lambda p: p.name.upper()):
        if p.stat().st_size == 0:
            continue
        try:
            info, _ = vdf.read_catalog(p)
        except SystemExit as e:  # vdf.py reports unsupported archives this way
            print(f"warning: skipped {p.name}: {e}", file=sys.stderr)
            continue
        found.append((info["time"], p))
    # stable sort by time, newest first; equal times keep directory order like 'ord'
    return [p for _, p in sorted(found, key=lambda t: -t[0])]


def game_files(gothic: Path, patterns: list[str]) -> dict[str, tuple[Path, int, int]]:
    """Upper-case base name -> (archive, offset, size) of the file the game would load."""
    files: dict[str, tuple[Path, int, int]] = {}
    for archive in game_archives(gothic):
        _, entries = vdf.read_catalog(archive)
        for name, off, size in entries:
            base = name.rsplit("/", 1)[-1].upper()
            if base in files or not any(fnmatch.fnmatch(base, p.upper()) for p in patterns):
                continue
            files[base] = (archive, off, size)
    return files


def read_entry(entry: tuple[Path, int, int]) -> bytes:
    archive, off, size = entry
    with open(archive, "rb") as f:
        f.seek(off)
        return f.read(size)


def model_patterns(model: str) -> list[str]:
    # the model, its overlays (HUMANS_1HST1, HUMANS_TORCH...) and their animations
    return [f"{model}.MDH", f"{model}.MSB", f"{model}-*.MAN", f"{model}_*.MSB", f"{model}_*-*.MAN"]


def man_model(base: str) -> str:
    return base.rsplit("-", 1)[0] if "-" in base else base.rsplit(".", 1)[0]


# --- commands -----------------------------------------------------------------------------------------

def cmd_to_text(args) -> int:
    path = Path(args.file)
    model = args.model or man_model(path.name.upper())
    a = parse_man(path.read_bytes(), model)
    if args.mdh:
        names = [n.name for n in parse_mdh(Path(args.mdh).read_bytes()).nodes]
        a.node_names = [names[i] if i < len(names) else "" for i in a.node_indices]
    text = to_text(a)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)
    return 0


def cmd_from_text(args) -> int:
    path = Path(args.file)
    a = from_text(path.read_text(encoding="utf-8"), str(path))
    Path(args.out).write_bytes(write_man(a))
    return 0


def skeleton_json(m: Mdh, model: str) -> dict:
    return {"model": model, "checksum": f"{m.checksum:08X}",
            "nodes": [{"name": n.name, "parent": n.parent} for n in m.nodes]}


def cmd_skeleton(args) -> int:
    path = Path(args.file)
    m = parse_mdh(path.read_bytes())
    text = json.dumps(skeleton_json(m, path.stem.upper()), indent=2, ensure_ascii=False) + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(text)
    return 0


def cmd_extract(args) -> int:
    gothic = Path(args.gothic)
    out = Path(args.out or Path(__file__).resolve().parent.parent / "build" / "anims-work" / args.model.upper())
    patterns = model_patterns(args.model.upper()) + [m.upper() for m in args.mesh]
    files = game_files(gothic, patterns)
    out.mkdir(parents=True, exist_ok=True)
    for base in sorted(files):
        (out / base).write_bytes(read_entry(files[base]))
    sources = sorted({files[b][0].name for b in files})
    print(f"extracted {len(files)} files from {', '.join(sources)} -> {out}")
    return 0 if files else 1


def cmd_roundtrip(args) -> int:
    """MAN -> .anim -> MAN for every animation of a model and its overlays; byte compare."""
    model = args.model.upper()
    files = game_files(Path(args.gothic), model_patterns(model))
    mdh = files.get(f"{model}.MDH")
    names = [n.name for n in parse_mdh(read_entry(mdh)).nodes] if mdh else []
    mans = sorted(b for b in files if b.endswith(".MAN"))
    diffs = []
    for base in mans:
        data = read_entry(files[base])
        try:
            a = parse_man(data, man_model(base))
            a.node_names = [names[i] if i < len(names) else "" for i in a.node_indices]
            back = write_man(from_text(to_text(a), base))
        except ValueError as e:
            diffs.append(f"{base}: {e}")
            continue
        if back != data:
            first = next((i for i, (x, y) in enumerate(zip(back, data)) if x != y), min(len(back), len(data)))
            diffs.append(f"{base}: differs at byte {first} (size {len(back)} vs {len(data)})")
    print(f"round trip MAN -> .anim -> MAN: {len(mans)} animations of {model} and its overlays, "
          f"{len(mans) - len(diffs)} identical, {len(diffs)} different")
    for d in diffs:
        print("  " + d)
    return 0 if mans and not diffs else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("to-text", help="MAN -> .anim")
    p.add_argument("file")
    p.add_argument("--model", help="model script name (default: from the file name)")
    p.add_argument("--mdh", help="MDH with node names for the 'node' lines")
    p.add_argument("--out")
    p.set_defaults(func=cmd_to_text)

    p = sub.add_parser("from-text", help=".anim -> MAN")
    p.add_argument("file")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_from_text)

    p = sub.add_parser("skeleton", help="node list and checksum of an MDH as JSON")
    p.add_argument("file")
    p.add_argument("--out")
    p.set_defaults(func=cmd_skeleton)

    p = sub.add_parser("extract", help="original model files from the game archives (game priority)")
    p.add_argument("model")
    p.add_argument("--gothic", required=True, help="Gothic II folder")
    p.add_argument("--out", help="default: gothic25/build/anims-work/<MODEL>")
    p.add_argument("--mesh", action="append", default=[], help="also extract this file, e.g. HUM_BODY_NAKED0.MDM")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("roundtrip", help="MAN -> .anim -> MAN for every animation of a model (K1)")
    p.add_argument("model")
    p.add_argument("--gothic", required=True, help="Gothic II folder")
    p.set_defaults(func=cmd_roundtrip)

    args = ap.parse_args()
    try:
        return args.func(args)
    except (ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
