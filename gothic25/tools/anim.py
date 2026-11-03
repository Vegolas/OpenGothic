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
  anim.py defs MODEL [ANI...] --gothic DIR [--ext FILE.EXT.MDS | --no-ext]
  anim.py mds-check FOLDER --gothic DIR      *.mds sources against the game MSB, through both parsers
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

    def line(self, skipws: bool = False) -> str:
        # zenkit::Read::read_line: stops at \0, \r or \n; skipws also eats the whitespace after it
        end = self.pos
        while end < len(self.data) and self.data[end] not in (0, 10, 13):
            end += 1
        text = self.data[self.pos:end].decode(ENCODING)
        self.pos = min(end + 1, len(self.data))
        if skipws and end < len(self.data) and self.data[end] != 0:
            while self.pos < len(self.data) and self.data[self.pos] in b" \t\r\n\v\f":
                self.pos += 1
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


# --- model scripts (MSB binary, MDS text) ---------------------------------------------------------------
# Both parsers mirror lib/ZenKit/src/ModelScript.cc (parse_binary_script) and ModelScriptDsl.cc (MdsParser)
# and fill the same data model, so a mod extension (<MODEL>.EXT.MDS, ADR 0008) can be merged and
# checked the way the engine sees it.

# event type names are matched exactly, like zenkit's event_types map
FRAME_EVENTS = {"DEF_DAM_MULTIPLY", "DEF_PAR_FRAME", "DEF_OPT_FRAME", "DEF_HIT_END", "DEF_WINDOW"}
SLOT_ITEM_EVENTS = {"DEF_CREATE_ITEM", "DEF_EXCHANGE_ITEM"}
# events with one slot string: the text parser (make_event_tag) keeps fewer than the binary one
SLOT_EVENTS_TEXT = {"DEF_INSERT_ITEM", "DEF_PLACE_MUNITION", "DEF_HIT_LIMB", "HIT_LIMB"}
SLOT_EVENTS_BINARY = SLOT_EVENTS_TEXT | {"DEF_HIT_DIR", "DEF_DIR", "DEF_DRAWSOUND", "DEF_UNDRAWSOUND",
                                         "DEF_REMOVE_MUNITION", "DEF_DESTROY_ITEM", "DEF_INV_TORCH",
                                         "DEF_REMOVE_ITEM"}
FLAG_LETTERS = "MREFIP"  # move, rotate, queue, fly, idle, in place
C_SPACE = " \t\n\v\f\r"  # std::isspace in the C locale


def zk_frames(text: str) -> list:
    """Frame list of an event the way zenkit reads it with std::istringstream (a trailing blank or an
    empty string yields one more 0)."""
    out, pos = [], 0
    while True:
        while pos < len(text) and text[pos].isspace():
            pos += 1
        start = pos
        if pos < len(text) and text[pos] in "+-":
            pos += 1
        while pos < len(text) and text[pos].isdigit():
            pos += 1
        if pos == start or text[start:pos] in ("+", "-"):
            out.append(0)  # failed extraction stores 0 and ends the loop
            return out
        out.append(int(text[start:pos]))
        if pos >= len(text):
            return out


def flags_of(text: str) -> str:
    return "".join(c for c in FLAG_LETTERS if c in text)


@dataclass
class MdsEvent:
    frame: int
    type: str
    slot: str = ""
    slot2: str = ""
    item: str = ""
    frames: list = field(default_factory=list)
    fight_mode: str = ""
    raw: tuple = ()  # the event's argument strings as written, for write_mds
    attached: bool = False

    def key(self) -> tuple:
        # fields both zenkit parsers fill; the slot of a few event types only comes from binary scripts
        slot = self.slot.upper() if self.type in SLOT_EVENTS_TEXT or self.type in SLOT_ITEM_EVENTS \
            or self.type == "DEF_SWAPMESH" else ""
        return (self.frame, self.type, slot, self.slot2.upper(), self.item.upper(), tuple(self.frames),
                self.fight_mode)


def fight_mode(text: str) -> str:
    return {"FIST": "FIST", "1H": "1H", "1h": "1H", "2H": "2H", "2h": "2H", "BOW": "BOW", "CBOW": "CBOW",
            "MAG": "MAG"}.get(text, "NONE")


def make_event(frame: int, etype: str, a: str | None, b: str | None, binary: bool = False,
               attached: bool = False) -> MdsEvent:
    e = MdsEvent(frame, etype, raw=tuple(x for x in (a, b) if x is not None), attached=attached)
    if etype in SLOT_ITEM_EVENTS:
        e.slot, e.item = a or "", b or ""
    elif etype == "DEF_SWAPMESH":
        e.slot, e.slot2 = a or "", b or ""
    elif etype == "DEF_FIGHTMODE":
        e.fight_mode = fight_mode(a or "")
    elif etype in FRAME_EVENTS:
        e.frames = zk_frames(a or "")
    elif etype in (SLOT_EVENTS_BINARY if binary else SLOT_EVENTS_TEXT):
        e.slot = a or ""
    return e


@dataclass
class MdsAni:
    name: str
    layer: int = 1
    next: str = ""
    blend_in: float = 0.0
    blend_out: float = 0.0
    flags: str = ""
    model: str = ""
    direction: str = "F"
    first_frame: int = 0
    last_frame: int = 0
    fps: float = 25.0
    cvs: float = 1.0
    events: list = field(default_factory=list)
    sfx: list = field(default_factory=list)  # (frame, name, range, empty_slot)
    sfx_ground: list = field(default_factory=list)
    pfx: list = field(default_factory=list)  # (frame, index, name, position, attached)
    pfx_stop: list = field(default_factory=list)  # (frame, index)
    morph: list = field(default_factory=list)  # (frame, animation, node)
    tremors: list = field(default_factory=list)  # (frame, f1, f2, f3, f4)
    origin: str = "game"


@dataclass
class ModelScript:
    animations: list = field(default_factory=list)
    aliases: list = field(default_factory=list)  # dicts: name, layer, next, blend_in, blend_out, flags, alias, direction
    blends: list = field(default_factory=list)  # dicts: name, next, blend_in, blend_out
    combinations: list = field(default_factory=list)  # dicts: name, layer, next, blend_in, blend_out, flags, model, last_frame
    disabled: list = field(default_factory=list)
    model_tags: list = field(default_factory=list)  # bone names


def f32r(v: float) -> float:
    return round(f32(v), 6)


def parse_msb(data: bytes) -> ModelScript:
    s = ModelScript()
    for ctype, payload in chunks(data):
        r = Reader(payload)
        if ctype == 0xF520:
            name = r.line()
            layer = r.unpack("I")[0]
            nxt = r.line()
            bi, bo = r.unpack("2f")
            flags = flags_of(r.line())
            model = r.line()
            direction = "R" if r.line().startswith("R") else "F"
            first, last = r.unpack("2i")
            fps, _speed, cvs = r.unpack("3f")
            s.animations.append(MdsAni(name, layer, nxt, f32r(bi), f32r(bo), flags, model, direction, first, last,
                                       f32r(fps), f32r(cvs)))
        elif ctype == 0xF530:
            name = r.line()
            layer = r.unpack("I")[0]
            nxt = r.line()
            bi, bo = r.unpack("2f")
            flags = flags_of(r.line())
            alias = r.line()
            direction = "R" if r.line().startswith("R") else "F"
            s.aliases.append({"name": name, "layer": layer, "next": nxt, "blend_in": f32r(bi), "blend_out": f32r(bo),
                              "flags": flags, "alias": alias, "direction": direction})
        elif ctype == 0xF540:
            name, nxt = r.line(), r.line()
            bi, bo = r.unpack("2f")
            s.blends.append({"name": name, "next": nxt, "blend_in": f32r(bi), "blend_out": f32r(bo)})
        elif ctype == 0xF570:
            name = r.line()
            layer = r.unpack("I")[0]
            nxt = r.line()
            bi, bo = r.unpack("2f")
            flags = flags_of(r.line())
            model = r.line()
            last = r.unpack("i")[0]
            s.combinations.append({"name": name, "layer": layer, "next": nxt, "blend_in": f32r(bi),
                                   "blend_out": f32r(bo), "flags": flags, "model": model, "last_frame": last})
        elif ctype == 0xF580:
            s.disabled.append(r.line())
        elif ctype == 0xF590:
            r.unpack("i")
            r.line()
            s.model_tags.append(r.line(True))
        elif ctype in (0xF5A1, 0xF5A2, 0xF5A3, 0xF5A4, 0xF5A5, 0xF5A9, 0xF5AA):
            if not s.animations:
                raise ValueError(f"event chunk {ctype:04X} before the first animation")
            ani = s.animations[-1]
            if ctype in (0xF5A1, 0xF5A2):
                frame = r.unpack("i")[0]
                name = r.line()
                rng = r.unpack("f")[0]
                empty = r.unpack("I")[0] != 0
                (ani.sfx if ctype == 0xF5A1 else ani.sfx_ground).append((frame, name, f32r(rng), empty))
            elif ctype == 0xF5A3:
                frame = r.unpack("i")[0]
                etype = r.line()
                a = b = None
                if etype in SLOT_ITEM_EVENTS or etype == "DEF_SWAPMESH":
                    a, b = r.line(True), r.line(True)
                elif etype in SLOT_EVENTS_BINARY or etype == "DEF_FIGHTMODE" or etype in FRAME_EVENTS:
                    a = r.line(True)
                ani.events.append(make_event(frame, etype, a, b, binary=True))
            elif ctype == 0xF5A4:
                frame, index = r.unpack("2i")
                name, position = r.line(), r.line()
                ani.pfx.append((frame, index, name, position, r.unpack("I")[0] != 0))
            elif ctype == 0xF5A5:
                ani.pfx_stop.append(tuple(r.unpack("2i")))
            elif ctype == 0xF5A9:
                frame = r.unpack("i")[0]
                ani.morph.append((frame, r.line(), r.line()))
            else:
                ani.tremors.append(tuple(r.unpack("5i")))
    return s


class MdsTokens:
    """Tokenizer of zenkit::MdsTokenizer: parens and semicolons are blanks, // starts a comment."""

    def __init__(self, text: str, source: str):
        self.text, self.source, self.pos, self.mark = text, source, 0, 0

    def where(self) -> str:
        return f"{self.source}:{self.text.count(chr(10), 0, self.pos) + 1}"

    def next(self):
        t = self.text
        alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        digits = "0123456789"
        self.mark = self.pos  # backtracking from the end of the text stays at the end
        while self.pos < len(t):
            self.mark = self.pos
            c = t[self.pos]
            self.pos += 1
            if c in C_SPACE or c in "();":
                continue
            if c == "/":
                end = t.find("\n", self.pos)
                self.pos = len(t) if end < 0 else end + 1
                continue
            if c in alpha or c in "*_.":
                start = self.pos - 1
                while self.pos < len(t) and (t[self.pos] in alpha or t[self.pos] in digits or t[self.pos] in "_-."):
                    self.pos += 1
                return "KEYWORD", t[start:self.pos]
            if c == '"':
                start = self.pos
                while self.pos < len(t) and t[self.pos] not in '"\n':
                    self.pos += 1
                value = t[start:self.pos]
                if self.pos < len(t) and t[self.pos] == '"':
                    self.pos += 1
                # zenkit drops the last character when the last non-blank one is ')'
                last = value.rstrip(C_SPACE)
                if last.endswith(")"):
                    value = value[:-1]
                return "STRING", value
            if c in digits or c == "-":
                start = self.pos - 1
                floating = False
                while self.pos < len(t):
                    if t[self.pos] == ".":
                        floating = True
                        self.pos += 1
                    if self.pos < len(t) and t[self.pos] in digits:
                        self.pos += 1
                    else:
                        break
                return ("FLOAT" if floating else "INTEGER"), t[start:self.pos]
            if c in "{}:":
                return {"{": "LBRACE", "}": "RBRACE", ":": "COLON"}[c], c
            raise ValueError(f"{self.where()}: illegal character {c!r}")
        return "EOF", ""

    def maybe(self, kind: str, value: str | None = None):
        k, v = self.next()
        if k == kind and (value is None or v.upper() == value.upper()):
            return v
        self.pos = self.mark
        return None

    def expect(self, kind: str, value: str | None = None) -> str:
        v = self.maybe(kind, value)
        if v is None:
            raise ValueError(f"{self.where()}: expected {value or kind}")
        return v

    def number(self) -> float:
        k, v = self.next()
        if k not in ("INTEGER", "FLOAT"):
            raise ValueError(f"{self.where()}: expected a number")
        return float(v)

    def maybe_number(self):
        k, v = self.next()
        if k in ("INTEGER", "FLOAT"):
            return float(v)
        self.pos = self.mark
        return None

    def maybe_named(self, name: str):
        if self.maybe("KEYWORD", name) is None:
            return None
        self.expect("COLON")
        return self.number()


def parse_mds(text: str, source: str = "<mds>", origin: str = "game") -> ModelScript:
    s = ModelScript()
    p = MdsTokens(text, source)
    p.expect("KEYWORD", "Model")
    p.expect("STRING")
    p.expect("LBRACE")
    while True:
        if p.maybe("RBRACE") is not None or p.maybe("EOF") is not None:
            break
        kw = p.expect("KEYWORD").upper()
        if kw == "MESHANDTREE":
            p.expect("STRING")
            p.maybe("KEYWORD", "DONT_USE_MESH")
        elif kw == "REGISTERMESH":
            p.expect("STRING")
        elif kw == "ANIENUM":
            parse_ani_enum(p, s, origin)
        else:
            break  # zenkit ignores the rest of the script
    return s


def parse_ani_enum(p: MdsTokens, s: ModelScript, origin: str):
    p.expect("LBRACE")
    while True:
        if p.maybe("RBRACE") is not None or p.maybe("EOF") is not None:
            return
        kw = p.expect("KEYWORD").upper()
        if kw == "ANI":
            s.animations.append(parse_ani(p, origin))
        elif kw == "ANIBLEND":
            name = p.expect("STRING")
            p.maybe("INTEGER")
            nxt = p.expect("STRING")
            bi = p.maybe_number() or 0.0
            bo = p.maybe_number() or 0.0
            k, v = p.next()
            if not (k == "KEYWORD" and "ani" not in v and "model" not in v):
                p.pos = p.mark
            else:
                p.maybe("COLON")
            if p.maybe("LBRACE") is not None:
                skip_block(p)
            s.blends.append({"name": name, "next": nxt, "blend_in": f32r(bi), "blend_out": f32r(bo)})
        elif kw == "ANIALIAS":
            name = p.expect("STRING")
            layer = int(p.expect("INTEGER"))
            nxt = p.expect("STRING")
            bi, bo = p.number(), p.number()
            flags = flags_of(p.expect("KEYWORD"))
            p.maybe("COLON")
            alias = p.expect("STRING")
            direction = "F"
            if p.maybe("KEYWORD", "R") is not None:
                direction = "R"
            else:
                p.maybe("KEYWORD", "F")
            s.aliases.append({"name": name, "layer": layer, "next": nxt, "blend_in": f32r(bi), "blend_out": f32r(bo),
                              "flags": flags, "alias": alias, "direction": direction})
        elif kw == "ANICOMB":
            name = p.expect("STRING")
            layer = int(p.expect("INTEGER"))
            nxt = p.expect("STRING")
            bi, bo = p.number(), p.number()
            flags = flags_of(p.expect("KEYWORD"))
            p.maybe("COLON")
            model = p.expect("STRING")
            last = int(p.expect("INTEGER"))
            if p.maybe("LBRACE") is not None:
                skip_block(p)
            s.combinations.append({"name": name, "layer": layer, "next": nxt, "blend_in": f32r(bi),
                                   "blend_out": f32r(bo), "flags": flags, "model": model, "last_frame": last})
        elif kw == "ANIDISABLE":
            s.disabled.append(p.expect("STRING"))
        elif kw == "MODELTAG":
            if p.expect("STRING").upper() != "DEF_HIT_LIMB":
                raise ValueError(f"{p.where()}: modelTag expects DEF_HIT_LIMB")
            s.model_tags.append(p.expect("STRING"))
        else:
            end = p.text.find("\n", p.pos)  # zenkit warns and skips the line
            p.pos = len(p.text) if end < 0 else end + 1


def skip_block(p: MdsTokens):
    while p.next()[0] not in ("RBRACE", "EOF"):
        pass


def parse_ani(p: MdsTokens, origin: str) -> MdsAni:
    a = MdsAni(p.expect("STRING"), origin=origin)
    a.layer = int(p.expect("INTEGER"))
    a.next = p.expect("STRING")
    a.blend_in, a.blend_out = f32r(p.number()), f32r(p.number())
    a.flags = flags_of(p.expect("KEYWORD"))
    p.maybe("COLON")
    a.model = p.expect("STRING")
    d = p.expect("KEYWORD").upper()
    if d not in ("F", "R"):
        raise ValueError(f"{p.where()}: expected F or R")
    a.direction = d
    a.first_frame, a.last_frame = int(p.expect("INTEGER")), int(p.expect("INTEGER"))
    fps = p.maybe_named("FPS")
    cvs = p.maybe_named("CVS")
    a.fps = f32r(fps if fps is not None else 25.0)
    a.cvs = f32r(cvs if cvs is not None else 1.0)
    p.maybe("LBRACE")
    while True:
        if p.maybe("RBRACE") is not None or p.maybe("EOF") is not None:
            break
        k, kw = p.next()
        if k != "KEYWORD":
            p.pos = p.mark
            break
        kw = kw.upper()
        if kw == "*EVENTTAG":
            fr = p.maybe("INTEGER")
            etype = p.expect("STRING")
            ea = p.maybe("STRING")
            eb = p.maybe("STRING")
            attach = p.maybe("KEYWORD", "ATTACH") is not None
            a.events.append(make_event(int(fr) if fr is not None else 0, etype, ea, eb, attached=attach))
        elif kw in ("*EVENTSFX", "*EVENTSFXGRND"):
            fr = int(p.expect("INTEGER"))
            name = p.expect("STRING")
            if kw == "*EVENTSFX":
                rng = p.maybe_named("R")
                empty = p.maybe("KEYWORD", "EMPTY_SLOT") is not None or p.maybe("KEYWORD", "EMTPY_SLOT") is not None
                a.sfx.append((fr, name, f32r(rng if rng is not None else 1000.0), empty))
            else:
                p.maybe("KEYWORD", "EMPTY_SLOT")
                a.sfx_ground.append((fr, name, 0.0, False))
        elif kw == "*EVENTPFX":
            fr = int(p.expect("INTEGER"))
            idx = p.maybe("INTEGER")
            name, pos = p.expect("STRING"), p.expect("STRING")
            attached = p.maybe("KEYWORD", "ATTACH") is not None or p.maybe("STRING") is not None
            a.pfx.append((fr, int(idx) if idx is not None else 0, name, pos, attached))
        elif kw == "*EVENTPFXSTOP":
            a.pfx_stop.append((int(p.expect("INTEGER")), int(p.expect("INTEGER"))))
        elif kw == "*EVENTMMSTARTANI":
            fr = int(p.expect("INTEGER"))
            a.morph.append((fr, p.expect("STRING"), p.maybe("STRING") or ""))
        elif kw == "*EVENTCAMTREMOR":
            a.tremors.append(tuple(int(p.expect("INTEGER")) for _ in range(5)))
        else:
            p.pos = p.mark
            break
    return a


def merge_scripts(base: ModelScript, ext: ModelScript) -> tuple:
    """ADR 0008: entries of the extension replace entries of the same name (case-insensitive) or are
    appended. Returns (merged, added, replaced)."""
    out = ModelScript(list(base.animations), list(base.aliases), list(base.blends), list(base.combinations),
                      list(base.disabled), list(base.model_tags))
    added = replaced = 0

    def put(items, entry, key):
        nonlocal added, replaced
        k = key(entry)
        for i, old in enumerate(items):
            if key(old) == k:
                items[i] = entry
                replaced += 1
                return
        items.append(entry)
        added += 1

    for a in ext.animations:
        put(out.animations, a, lambda x: x.name.upper())
    for a in ext.aliases:
        put(out.aliases, a, lambda x: x["name"].upper())
    for b in ext.blends:
        put(out.blends, b, lambda x: (x["name"].upper(), x["next"].upper()))
    for c in ext.combinations:
        put(out.combinations, c, lambda x: x["name"].upper())
    out.disabled += ext.disabled
    out.model_tags += ext.model_tags
    return out, added, replaced


def fmt_num(v: float) -> str:
    return f"{v:g}"


def fmt_f(v: float) -> str:
    # plain decimal (no exponent), which the MDS tokenizer reads as a number
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def write_mds(s: ModelScript, model: str, header: str = "") -> str:
    """MDS text of a model script, in the syntax parse_mds and zenkit read back to the same data."""
    out = [f"// {line}".rstrip() for line in header.splitlines()]
    out += [f'Model ("{model}")', "{", "\taniEnum", "\t{"]
    for a in s.animations:
        extra = (f" FPS:{fmt_f(a.fps)}" if a.fps != 25.0 else "") + (f" CVS:{fmt_f(a.cvs)}" if a.cvs != 1.0 else "")
        out.append(f'\t\tani ("{a.name}" {a.layer} "{a.next}" {fmt_f(a.blend_in)} {fmt_f(a.blend_out)} '
                   f'{a.flags or "."} "{a.model}" {a.direction} {a.first_frame} {a.last_frame}{extra})')
        out.append("\t\t{")
        for e in a.events:
            args = "".join(f' "{x}"' for x in e.raw)
            out.append(f'\t\t\t*eventTag ({e.frame} "{e.type}"{args}{" ATTACH" if e.attached else ""})')
        for f, n, r, empty in a.sfx:
            rng = "" if r == 1000.0 else f" R:{fmt_f(r)}"
            out.append(f'\t\t\t*eventSFX ({f} "{n}"{rng}{" EMPTY_SLOT" if empty else ""})')
        out += [f'\t\t\t*eventSFXGrnd ({f} "{n}")' for f, n, _, _ in a.sfx_ground]
        out += [f'\t\t\t*eventPFX ({f} {i} "{n}" "{p}"{" ATTACH" if at else ""})' for f, i, n, p, at in a.pfx]
        out += [f"\t\t\t*eventPFXStop ({f} {i})" for f, i in a.pfx_stop]
        out += [f'\t\t\t*eventMMStartAni ({f} "{n}"{f" {chr(34)}{nd}{chr(34)}" if nd else ""})' for f, n, nd in a.morph]
        out += [f"\t\t\t*eventCamTremor ({' '.join(str(v) for v in t)})" for t in a.tremors]
        out.append("\t\t}")
    for x in s.aliases:
        out.append(f'\t\taniAlias ("{x["name"]}" {x["layer"]} "{x["next"]}" {fmt_f(x["blend_in"])} '
                   f'{fmt_f(x["blend_out"])} {x["flags"] or "."} "{x["alias"]}" {x["direction"]})')
    for x in s.blends:
        out.append(f'\t\taniBlend ("{x["name"]}" "{x["next"]}" {fmt_f(x["blend_in"])} {fmt_f(x["blend_out"])})')
    for x in s.combinations:
        out.append(f'\t\taniComb ("{x["name"]}" {x["layer"]} "{x["next"]}" {fmt_f(x["blend_in"])} '
                   f'{fmt_f(x["blend_out"])} {x["flags"] or "."} "{x["model"]}" {x["last_frame"]})')
    out += [f'\t\taniDisable ("{x}")' for x in s.disabled]
    out += [f'\t\tmodelTag ("DEF_HIT_LIMB" "{x}")' for x in s.model_tags]
    out += ["\t}", "}"]
    return "\r\n".join(out) + "\r\n"


def describe_ani(a: MdsAni, man_frames: int | None = None) -> list:
    """Canonical text of one animation, the same lines as the 'ani info' console command."""
    head = (f"ani {a.name.upper()} origin {a.origin} layer {a.layer} next {a.next.upper() or '-'} "
            f"blend {fmt_num(a.blend_in)} {fmt_num(a.blend_out)} flags {a.flags or '-'} dir {a.direction} "
            f"frames {a.first_frame}-{a.last_frame} fps {fmt_num(a.fps)}")
    if man_frames is not None:
        head += f" man {man_frames}"
    out = [head]
    for e in a.events:
        detail = " ".join(f"{k}={v}" for k, v in (("slot", e.slot), ("slot2", e.slot2), ("item", e.item),
                                                  ("mode", e.fight_mode)) if v)
        if e.frames:
            detail = (detail + " " if detail else "") + "frames=" + ",".join(str(f) for f in e.frames)
        out.append(f"  tag {e.frame} {e.type.upper()} {detail}".rstrip())
    out += [f"  sfx {f} {n.upper()} range={fmt_num(r)}{' empty' if e else ''}" for f, n, r, e in a.sfx]
    out += [f"  sfxground {f} {n.upper()}" for f, n, _, _ in a.sfx_ground]
    out += [f"  pfx {f} {i} {n.upper()} {pos.upper()}{' attach' if at else ''}" for f, i, n, pos, at in a.pfx]
    out += [f"  pfxstop {f} {i}" for f, i in a.pfx_stop]
    out += [f"  morph {f} {n.upper()} {nd.upper()}".rstrip() for f, n, nd in a.morph]
    out += [f"  tremor {' '.join(str(v) for v in t)}" for t in a.tremors]
    return out


def pfx_index(v: int) -> int:
    # compiled scripts store the effect index as a float, which zenkit reads as an int
    if v > 0xFFFF:
        return int(struct.unpack("<f", struct.pack("<i", v))[0])
    return v


def compare_scripts(left: ModelScript, right: ModelScript, known: dict | None = None) -> list:
    """Differences between two parsed model scripts, ignoring order and fields the text format does
    not carry (speed); names compare without case.

    Known differences of zenkit's two parsers are counted in `known` instead of reported: the sound
    range and slot flag (text: 1000 and EMPTY_SLOT, binary: the compiled values) and the effect index
    read from a float."""
    diffs = []
    known = known if known is not None else {}

    def by_name(items, key):
        return {key(x): x for x in items}

    la = by_name(left.animations, lambda x: x.name.upper())
    ra = by_name(right.animations, lambda x: x.name.upper())
    for name in sorted(set(la) | set(ra)):
        if name not in la or name not in ra:
            diffs.append(f"ani {name}: only in {'right' if name not in la else 'left'}")
            continue
        l, r = la[name], ra[name]
        for f in ("layer", "next", "blend_in", "blend_out", "flags", "direction", "first_frame", "last_frame",
                  "fps", "cvs", "sfx", "sfx_ground", "pfx", "pfx_stop", "morph", "tremors"):
            lv, rv = getattr(l, f), getattr(r, f)
            if f == "next":
                lv, rv = lv.upper(), rv.upper()
            if f in ("sfx", "sfx_ground"):
                if f == "sfx" and [t[:2] for t in lv] == [t[:2] for t in rv] and lv != rv:
                    known["sfx range/slot"] = known.get("sfx range/slot", 0) + 1
                lv, rv = [t[:2] for t in lv], [t[:2] for t in rv]
            if f in ("pfx", "pfx_stop", "tremors"):
                # floats of compiled scripts read as ints (effect index, tremor parameters)
                fixed = [(t[0],) + tuple(pfx_index(x) if isinstance(x, int) else x for x in t[1:])
                         if f == "tremors" else (t[0], pfx_index(t[1])) + tuple(t[2:]) for t in lv]
                if fixed != lv and fixed == rv:
                    known["floats read as ints"] = known.get("floats read as ints", 0) + 1
                lv = fixed
            if f in ("sfx", "sfx_ground", "pfx", "morph"):
                # the compiler trims blanks inside quotes, the text parser keeps them
                strip = [tuple(x.strip(C_SPACE) if isinstance(x, str) else x for x in t) for t in rv]
                lstrip = [tuple(x.strip(C_SPACE) if isinstance(x, str) else x for x in t) for t in lv]
                if strip != rv and lstrip == lv and \
                        [tuple(str(x).upper() if isinstance(x, str) else x for x in t) for t in strip] == \
                        [tuple(str(x).upper() if isinstance(x, str) else x for x in t) for t in lv]:
                    known["blanks in quotes"] = known.get("blanks in quotes", 0) + 1
                lv, rv = lstrip, strip
            if f in ("sfx", "sfx_ground", "pfx", "morph"):
                lv = [tuple(str(x).upper() if isinstance(x, str) else x for x in t) for t in lv]
                rv = [tuple(str(x).upper() if isinstance(x, str) else x for x in t) for t in rv]
            if lv != rv:
                diffs.append(f"ani {name}: {f} {lv!r} != {rv!r}")
        le, re_ = sorted(e.key() for e in l.events), sorted(e.key() for e in r.events)
        if le != re_:
            diffs.append(f"ani {name}: events {sorted(set(le) - set(re_))!r} != {sorted(set(re_) - set(le))!r}")
    for what, key in (("aliases", lambda x: x["name"].upper()), ("combinations", lambda x: x["name"].upper()),
                      ("blends", lambda x: (x["name"].upper(), x["next"].upper()))):
        lm, rm = by_name(getattr(left, what), key), by_name(getattr(right, what), key)
        for k in sorted(set(lm) | set(rm), key=str):
            lv = {f: (v.strip(C_SPACE).upper() if isinstance(v, str) else v) for f, v in lm.get(k, {}).items()}
            rv = {f: (v.strip(C_SPACE).upper() if isinstance(v, str) else v) for f, v in rm.get(k, {}).items()}
            if lv != rv:
                diffs.append(f"{what} {k}: {lv or 'missing'} != {rv or 'missing'}")
    if sorted(x.upper() for x in left.disabled) != sorted(x.upper() for x in right.disabled):
        diffs.append(f"disabled: {sorted(left.disabled)} != {sorted(right.disabled)}")
    if sorted(x.upper() for x in left.model_tags) != sorted(x.upper() for x in right.model_tags):
        diffs.append(f"model tags: {sorted(left.model_tags)} != {sorted(right.model_tags)}")
    return diffs


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


def default_ext(model: str) -> Path | None:
    """The mod's extension of a model script, gothic25/anims/<base model>/<MODEL>.EXT.MDS, if it exists."""
    base = model.split("_", 1)[0]
    p = Path(__file__).resolve().parent.parent / "anims" / base / f"{model}.EXT.MDS"
    return p if p.exists() else None


def load_merged(gothic: Path, model: str, ext: Path | None) -> tuple:
    files = game_files(gothic, [f"{model}.MSB", f"{model}-*.MAN"])
    msb = files.get(f"{model}.MSB")
    if msb is None:
        raise ValueError(f"no {model}.MSB in the game archives of {gothic}")
    script = parse_msb(read_entry(msb))
    added = replaced = 0
    if ext is not None:
        mod = parse_mds(ext.read_text(encoding=ENCODING), str(ext), origin="mod")
        script, added, replaced = merge_scripts(script, mod)
    return script, files, added, replaced


def man_frames(files: dict, model: str, ani: str) -> int | None:
    entry = files.get(f"{model}-{ani.upper()}.MAN")
    if entry is None:
        return None
    for ctype, payload in chunks(read_entry(entry)):
        if ctype == MAN_HEADER:
            r = Reader(payload)
            r.unpack("H")
            r.line()
            return r.unpack("3I")[1]
    return None


def cmd_defs(args) -> int:
    """Definitions of a model as the engine sees them: original MSB plus the mod extension (ADR 0008)."""
    model = args.model.upper()
    ext = Path(args.ext) if args.ext else (None if args.no_ext else default_ext(model))
    script, files, added, replaced = load_merged(Path(args.gothic), model, ext)
    wanted = {a.upper() for a in args.ani}
    found = 0
    for a in script.animations:
        if wanted and a.name.upper() not in wanted:
            continue
        found += 1
        print("\n".join(describe_ani(a, man_frames(files, model, a.name))))
    if ext is not None:
        print(f"# {ext.name}: {added} added, {replaced} replaced", file=sys.stderr)
    missing = wanted - {a.name.upper() for a in script.animations}
    for m in sorted(missing):
        print(f"error: no animation {m} in {model}", file=sys.stderr)
    return 1 if missing or not found else 0


def cmd_mds_check(args) -> int:
    """Parses every *.mds under a folder and the game's MSB of the same name with both parsers and
    reports the differences (a check of the parsers against each other and of an MDK against the game)."""
    gothic = Path(args.gothic)
    sources = sorted(Path(args.folder).rglob("*.mds"), key=lambda p: p.name.upper())
    names = [p.stem.upper() for p in sources]
    files = game_files(gothic, [f"{n}.MSB" for n in names])
    total_diffs = checked = animations = 0
    errors = []
    known: dict = {}
    for src, name in zip(sources, names):
        entry = files.get(f"{name}.MSB")
        if entry is None:
            continue
        try:
            text = parse_mds(src.read_text(encoding=ENCODING), str(src))
            binary = parse_msb(read_entry(entry))
        except ValueError as e:
            errors.append(f"{src.name}: {e}")
            continue
        checked += 1
        animations += len(binary.animations)
        # the writer must give the same data back
        again = parse_mds(write_mds(text, name), f"write_mds({src.name})")
        writer_diffs = compare_scripts(text, again)
        errors += [f"{src.name}: write_mds round trip: {d}" for d in writer_diffs[:3]]
        diffs = compare_scripts(binary, text, known)
        if not diffs and not args.all:
            continue
        total_diffs += len(diffs)
        print(f"{name}: {len(binary.animations)} animations in MSB, {len(text.animations)} in {src.name}, "
              f"{len(diffs)} differences")
        for d in diffs[:args.max]:
            print("  " + d)
        if len(diffs) > args.max:
            print(f"  ... {len(diffs) - args.max} more")
    for e in errors:
        print("error: " + e)
    print(f"checked {checked} model scripts ({animations} animations), {total_diffs} differences, "
          f"{len(errors)} parse errors; known parser differences: "
          + (", ".join(f"{k} {v}" for k, v in sorted(known.items())) or "none"))
    return 1 if errors or not checked else 0


# --- build (spec 004 W4) -------------------------------------------------------------------------------
# Sources: <src>/anims.json lists the models; <src>/<MODEL>/ holds <SCRIPT>.EXT.MDS (definitions of the
# mod for the model or an overlay) and <NAME>.anim (animations, the 'model' line names the script).
# Output: <out>/_COMPILED/<SCRIPT>-<NAME>.MAN and <SCRIPT>.EXT.MDS, which pack.ps1 puts under
# _WORK/DATA/ANIMS/_COMPILED. Event frames are checked the way the engine reads them
# (common/graphics/mesh/animation.cpp): DEF_HIT_END, DEF_WINDOW and DEF_PAR_FRAME are frames from the
# start of the animation (setupTime), DEF_OPT_FRAME and effects are frames of the definition's range
# (frameClamp).

RELATIVE_EVENTS = {"DEF_HIT_END", "DEF_WINDOW", "DEF_PAR_FRAME"}
BUILD_MARKER = ".anim-build"


def find_ani(script: ModelScript | None, name: str) -> MdsAni | None:
    if script is None:
        return None
    return next((a for a in script.animations if a.name.upper() == name.upper()), None)


def check_definition(where: str, d: MdsAni, frames: int | None) -> list:
    """Problems of one definition of the mod against the length of its MAN (when known)."""
    errors = []
    lo, hi = d.first_frame, d.last_frame
    if hi < lo:
        errors.append(f"{where}: frame range {lo}-{hi} is empty")
        return errors
    n = hi - lo + 1
    if frames is not None and frames != n:
        errors.append(f"{where}: the animation has {frames} frames, the definition {lo}-{hi} needs {n}")
    for e in d.events:
        if e.type == "DEF_OPT_FRAME":
            bad = [f for f in e.frames if not lo <= f <= hi]
            if bad:
                errors.append(f"{where}: DEF_OPT_FRAME {bad} outside frames {lo}-{hi}")
        elif e.type in RELATIVE_EVENTS:
            bad = [f for f in e.frames if not 0 <= f <= n]
            if bad:
                errors.append(f"{where}: {e.type} {bad} outside 0-{n} (frames from the start)")
            if e.type == "DEF_WINDOW" and len(e.frames) % 2:
                errors.append(f"{where}: DEF_WINDOW needs pairs of frames, got {e.frames}")
    effects = [("sound", t[0]) for t in d.sfx + d.sfx_ground] + [("effect", t[0]) for t in d.pfx + d.pfx_stop]
    effects += [("morph", t[0]) for t in d.morph] + [("tremor", t[0]) for t in d.tremors]
    for what, f in effects:
        if not lo <= f <= hi:
            errors.append(f"{where}: {what} at frame {f} outside frames {lo}-{hi}")
    return errors


def check_skeleton(where: str, a: Man, skel: dict) -> list:
    """Node list of an animation of the mod against the model hierarchy: every bone once, known slots."""
    errors = []
    nodes = [n["name"] for n in skel["nodes"]]
    if f"{a.checksum:08X}" != skel["checksum"].upper():
        errors.append(f"{where}: checksum {a.checksum:08X}, the model has {skel['checksum']}")
    seen = set()
    for index, name in zip(a.node_indices, a.node_names):
        if index >= len(nodes) or nodes[index] != name:
            expected = nodes[index] if index < len(nodes) else "nothing"
            errors.append(f"{where}: node {index} is {name!r}, the model has {expected!r}")
        seen.add(index)
    missing = [n for i, n in enumerate(nodes) if not n.upper().startswith("ZS_") and i not in seen]
    if missing:
        errors.append(f"{where}: bones without samples: {', '.join(missing)}")
    if len(seen) != len(a.node_indices):
        errors.append(f"{where}: a node is sampled twice")
    return errors


def build(src: Path, extras: list, gothic: Path | None) -> tuple:
    """Returns (outputs {file name: bytes}, errors, notes)."""
    manifest_path = src / "anims.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    outputs, errors, notes = {}, [], []
    for model, cfg in sorted(manifest.get("models", {}).items()):
        model = model.upper()
        skel = json.loads((manifest_path.parent / cfg["skeleton"]).read_text(encoding="utf-8"))
        dirs = [src / model] + [Path(e) / model for e in extras if (Path(e) / model).is_dir()]

        exts: dict = {}
        for d in dirs:
            for p in sorted(d.glob("*.EXT.MDS"), key=lambda p: p.name.upper()):
                script = p.name[:-len(".EXT.MDS")].upper()
                try:
                    exts.setdefault(script, []).append(parse_mds(p.read_text(encoding=ENCODING), str(p), "mod"))
                except ValueError as e:
                    errors.append(f"{p}: {e}")
        mod_defs = {}
        for script, parts in exts.items():
            merged = ModelScript()
            for part in parts:  # the repository first, extra folders after, later entries win
                merged, _, _ = merge_scripts(merged, part)
            mod_defs[script] = merged

        game_defs, game_mans = {}, set()
        if gothic is not None:
            files = game_files(gothic, model_patterns(model))
            game_mans = {b for b in files if b.endswith(".MAN")}
            for b in files:
                if b.endswith(".MSB"):
                    game_defs[b[:-4]] = parse_msb(read_entry(files[b]))

        built = {}
        for d in dirs:
            for p in sorted(d.glob("*.anim"), key=lambda p: p.name.upper()):
                try:
                    a = from_text(p.read_text(encoding="utf-8"), str(p))
                except ValueError as e:
                    errors.append(str(e))
                    continue
                script, name = a.model.upper(), a.name.upper()
                where = f"{p.name} ({script}-{name})"
                if not script.startswith(model):
                    errors.append(f"{where}: model {script} is not {model} or one of its overlays")
                    continue
                errors += check_skeleton(where, a, skel)
                definition = find_ani(mod_defs.get(script), name) or find_ani(game_defs.get(script), name)
                if definition is None:
                    if gothic is None and script not in mod_defs:
                        notes.append(f"{where}: no definition in the mod; the game's is not checked (no --gothic)")
                    else:
                        errors.append(f"{where}: no definition of {name} in {script}.EXT.MDS or the game")
                else:
                    a.layer, a.next = definition.layer, definition.next.upper()
                    errors += check_definition(where, definition, a.frame_count)
                a.name = name
                try:
                    built[f"{script}-{name}.MAN"] = write_man(a)
                except ValueError as e:
                    errors.append(f"{where}: {e}")

        for script, defs in sorted(mod_defs.items()):
            merged_names = {x.name.upper() for x in defs.animations}
            merged_names |= {x.name.upper() for x in game_defs.get(script, ModelScript()).animations}
            for d in defs.animations:
                man = f"{script}-{d.name.upper()}.MAN"
                where = f"{script}.EXT.MDS ({d.name})"
                if man in built:
                    continue  # checked with its animation above
                if man in game_mans:
                    errors += check_definition(where, d, man_frames(files, script, d.name))
                elif gothic is None:
                    notes.append(f"{where}: no animation in the mod; the game's is not checked (no --gothic)")
                    errors += check_definition(where, d, None)
                else:
                    errors.append(f"{where}: the definition points to a missing animation {man}")
            for x in defs.aliases:
                if gothic is not None and x["alias"].upper() not in merged_names:
                    errors.append(f"{script}.EXT.MDS (alias {x['name']}): no animation {x['alias']}")
            outputs[f"{script}.EXT.MDS"] = write_mds(
                defs, script, f"Animation definitions of the Gothic 2.5 mod for {script}, merged into the\n"
                              "original model by the engine (ADR 0008). Generated by tools/anim.py build."
            ).encode(ENCODING)
        outputs.update(built)
    return outputs, errors, notes


def cmd_build(args) -> int:
    root = Path(__file__).resolve().parent.parent
    src = Path(args.src) if args.src else root / "anims"
    out = Path(args.out) if args.out else root / "build" / "anims"
    gothic = Path(args.gothic) if args.gothic else None
    outputs, errors, notes = build(src, args.extra, gothic)
    for n in notes:
        print("note: " + n)
    if errors:
        for e in errors:
            print("error: " + e, file=sys.stderr)
        print(f"build failed: {len(errors)} errors", file=sys.stderr)
        return 1
    compiled = out / "_COMPILED"
    if out.exists() and not (out / BUILD_MARKER).exists() and any(out.iterdir()):
        print(f"error: {out} is not a folder of anim.py build, not cleaning it", file=sys.stderr)
        return 1
    if compiled.exists():
        for old in compiled.iterdir():
            old.unlink()
    compiled.mkdir(parents=True, exist_ok=True)
    (out / BUILD_MARKER).write_text("output of tools/anim.py build\n", encoding="utf-8")
    for name in sorted(outputs):
        (compiled / name).write_bytes(outputs[name])
    print(f"built {len(outputs)} files -> {compiled}")
    return 0


def default_archive() -> Path:
    root = Path(__file__).resolve().parent.parent
    manifest = json.loads((root / "mod.json").read_text(encoding="utf-8"))
    return root / "build" / "game" / "Data" / "ModVDF" / manifest["archive"]


def cmd_check_pack(args) -> int:
    """Animation files of the mod archive against the game (spec 004 W7, K7): no model script of the
    game, no file equal to a game file, no MAN with the samples of the original of the same name."""
    import hashlib
    archive = Path(args.archive) if args.archive else default_archive()
    _, entries = vdf.read_catalog(archive)
    anims = [(n, off, size) for n, off, size in entries if n.upper().startswith("_WORK/DATA/ANIMS/")]
    game = game_files(Path(args.gothic), ["*.MAN", "*.MSB", "*.MDS", "*.MDH", "*.MDM", "*.MMB", "*.MDL"])
    game_hashes = {}
    for base, entry in game.items():
        game_hashes.setdefault(hashlib.sha256(read_entry(entry)).hexdigest(), base)
    errors = []
    print(f"{archive.name}: {len(anims)} animation files")
    for name, off, size in sorted(anims):
        base = name.rsplit("/", 1)[-1].upper()
        data = read_entry((archive, off, size))
        verdict = "ok"
        if base.endswith(".MSB") or (base.endswith(".MDS") and not base.endswith(".EXT.MDS")):
            verdict = "model script: the mod may only ship <MODEL>.EXT.MDS (ADR 0008)"
        elif hashlib.sha256(data).hexdigest() in game_hashes:
            verdict = f"identical to the game file {game_hashes[hashlib.sha256(data).hexdigest()]}"
        elif base.endswith(".MAN") and base in game:
            try:
                mine, orig = parse_man(data), parse_man(read_entry(game[base]))
                if mine.samples == orig.samples:
                    verdict = f"same samples as the game's {base}"
            except ValueError as e:
                verdict = f"not a valid animation: {e}"
        print(f"  {size:8d}  {name}  {verdict}")
        if verdict != "ok":
            errors.append(f"{name}: {verdict}")
    for e in errors:
        print("error: " + e, file=sys.stderr)
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check-pack", help="animation files of the mod archive against the game (W7, K7)")
    p.add_argument("archive", nargs="?", help="mod archive (default: build/game/Data/ModVDF/<archive>)")
    p.add_argument("--gothic", required=True, help="Gothic II folder")
    p.set_defaults(func=cmd_check_pack)

    p = sub.add_parser("build", help="MAN and definition files of the mod from gothic25/anims (spec 004 W4)")
    p.add_argument("--src", help="source folder with anims.json (default: gothic25/anims)")
    p.add_argument("--out", help="output folder (default: gothic25/build/anims)")
    p.add_argument("--extra", action="append", default=[], help="another source folder, e.g. local test data")
    p.add_argument("--gothic", help="Gothic II folder, to check definitions against the game")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("defs", help="definitions of a model: game MSB plus the mod extension (ADR 0008)")
    p.add_argument("model", help="model or overlay script name, e.g. HUMANS or HUMANS_1HST1")
    p.add_argument("ani", nargs="*", help="only these animations")
    p.add_argument("--gothic", required=True, help="Gothic II folder")
    p.add_argument("--ext", help="extension file (default: gothic25/anims/<MODEL>/<MODEL>.EXT.MDS)")
    p.add_argument("--no-ext", action="store_true", help="only the game definitions")
    p.set_defaults(func=cmd_defs)

    p = sub.add_parser("mds-check", help="compare *.mds sources with the game MSB through both parsers")
    p.add_argument("folder")
    p.add_argument("--gothic", required=True, help="Gothic II folder")
    p.add_argument("--max", type=int, default=10, help="differences shown per model")
    p.add_argument("--all", action="store_true", help="also list models without differences")
    p.set_defaults(func=cmd_mds_check)

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
