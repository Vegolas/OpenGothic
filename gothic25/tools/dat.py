#!/usr/bin/env python3
"""Inspect and compare compiled Daedalus scripts (*.DAT).

Format mirrors zenkit::DaedalusScript::load / DaedalusSymbol::load (lib/ZenKit/src/DaedalusScript.cc).

Usage:
  dat.py info FILE
  dat.py symbols FILE [--filter SUBSTRING]
  dat.py disasm FILE SYMBOL
  dat.py diff EXPECTED ACTUAL [--limit N] [--with-positions]
"""

from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass, field

TYPES = ["void", "float", "int", "string", "class", "func", "prototype", "instance"]
F_CONST, F_RETURN, F_MEMBER, F_EXTERNAL, F_MERGED = 1, 2, 4, 8, 16
ENCODING = "cp1250"


@dataclass
class Symbol:
    index: int
    name: str
    vary: int
    count: int
    type: int
    flags: int
    position: tuple  # file_index, line_start, line_count, char_start, char_count
    value: tuple = ()
    address: int | None = None
    parent: int = -1

    def describe(self) -> str:
        flags = "".join(c for c, f in (("c", F_CONST), ("r", F_RETURN), ("m", F_MEMBER),
                                        ("e", F_EXTERNAL), ("M", F_MERGED)) if self.flags & f)
        t = TYPES[self.type] if self.type < len(TYPES) else str(self.type)
        return f"{self.name} [{t}{'[' + str(self.count) + ']' if self.count > 1 else ''} {flags or '-'}]"


@dataclass
class Script:
    version: int
    sort_table: list[int]
    symbols: list[Symbol]
    code: bytes
    size: int
    by_name: dict[str, Symbol] = field(default_factory=dict)


class Reader:
    def __init__(self, data: bytes):
        self.data, self.pos = data, 0

    def u8(self) -> int:
        self.pos += 1
        return self.data[self.pos - 1]

    def u32(self) -> int:
        v = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return v

    def i32(self) -> int:
        v = struct.unpack_from("<i", self.data, self.pos)[0]
        self.pos += 4
        return v

    def f32(self) -> float:
        v = struct.unpack_from("<f", self.data, self.pos)[0]
        self.pos += 4
        return v

    def line(self) -> str:
        end = self.data.index(b"\n", self.pos)
        s = self.data[self.pos:end]
        self.pos = end + 1
        return s.decode(ENCODING, "replace")

    def bytes(self, n: int) -> bytes:
        self.pos += n
        return self.data[self.pos - n:self.pos]


def load(path: str) -> Script:
    with open(path, "rb") as f:
        data = f.read()
    r = Reader(data)
    version = r.u8()
    n = r.u32()
    sort_table = [r.u32() for _ in range(n)]
    symbols = []
    for i in range(n):
        name = r.line() if r.u32() else ""
        if name.startswith("\xff") or name.startswith("˙"):  # compiler-generated (0xFF in cp1250)
            name = "$" + name[1:]
        vary, props = r.u32(), r.u32()
        sym = Symbol(i, name, vary, props & 0xFFF, (props >> 12) & 0xF, (props >> 16) & 0x3F,
                     tuple(r.u32() for _ in range(5)))
        if not sym.flags & F_MEMBER:
            if sym.type == 1:
                sym.value = tuple(r.f32() for _ in range(sym.count))
            elif sym.type == 2:
                sym.value = tuple(r.i32() for _ in range(sym.count))
            elif sym.type == 3:
                sym.value = tuple(r.line() for _ in range(sym.count))
            elif sym.type in (4, 5, 6, 7):
                sym.address = r.i32()
        sym.parent = r.i32()
        symbols.append(sym)
    code = r.bytes(r.u32())
    script = Script(version, sort_table, symbols, code, len(data))
    script.by_name = {s.name.upper(): s for s in symbols}
    return script


def cmd_info(args) -> None:
    s = load(args.file)
    counts = {}
    for sym in s.symbols:
        key = TYPES[sym.type] + (" extern" if sym.flags & F_EXTERNAL else "")
        counts[key] = counts.get(key, 0) + 1
    print(f"{args.file}: version {s.version}, {len(s.symbols)} symbols, code {len(s.code)} bytes, file {s.size} bytes")
    for key in sorted(counts):
        print(f"  {key:<16} {counts[key]}")


def cmd_symbols(args) -> None:
    s = load(args.file)
    for sym in s.symbols:
        if args.filter and args.filter.upper() not in sym.name.upper():
            continue
        extra = ""
        if sym.type == 5:
            extra = f" returns {TYPES[sym.vary] if sym.vary < len(TYPES) else sym.vary}"
        params = [p for p in s.symbols[sym.index + 1:sym.index + 1 + sym.count]] if sym.type == 5 else []
        if params:
            extra += " (" + ", ".join(f"{TYPES[p.type]} {p.name.split('.')[-1]}" for p in params) + ")"
        print(f"{sym.index:>6}  {sym.describe()}{extra}")


# Opcodes as in zenkit::DaedalusOpcode
OPS = {0: "ADD", 1: "SUB", 2: "MUL", 3: "DIV", 4: "MOD", 5: "OR", 6: "ANDB", 7: "LT", 8: "GT", 9: "MOVI",
       11: "ORR", 12: "AND", 13: "LSL", 14: "LSR", 15: "LTE", 16: "EQ", 17: "NEQ", 18: "GTE", 19: "ADDMOVI",
       20: "SUBMOVI", 21: "MULMOVI", 22: "DIVMOVI", 30: "PLUS", 31: "NEGATE", 32: "NOT", 33: "CMPL", 45: "NOP",
       60: "RSR", 61: "BL", 62: "BE", 64: "PUSHI", 65: "PUSHV", 67: "PUSHVI", 70: "MOVS", 71: "MOVSS",
       72: "MOVVF", 73: "MOVF", 74: "MOVVI", 75: "B", 76: "BZ", 80: "GMOVI", 245: "PUSHVV"}
OP_INT = {61, 62, 64, 75, 76}
OP_SYM = {65, 67, 80}


def disassemble(s: Script, address: int, limit: int = 200) -> list[str]:
    out, pc = [], address
    while len(out) < limit and pc < len(s.code):
        op = s.code[pc]
        pc += 1
        name = OPS.get(op, f"op{op}")
        if op in OP_INT:
            out.append(f"{name} {struct.unpack_from('<i', s.code, pc)[0]}")
            pc += 4
        elif op in OP_SYM:
            idx = struct.unpack_from("<I", s.code, pc)[0]
            pc += 4
            out.append(f"{name} {s.symbols[idx].name if idx < len(s.symbols) else idx}")
        elif op == 245:
            idx = struct.unpack_from("<I", s.code, pc)[0]
            out.append(f"{name} {s.symbols[idx].name if idx < len(s.symbols) else idx}[{s.code[pc + 4]}]")
            pc += 5
        else:
            out.append(name)
        if op == 60:
            break
    return out


def cmd_disasm(args) -> None:
    s = load(args.file)
    sym = s.by_name.get(args.symbol.upper())
    if sym is None or sym.address is None:
        raise SystemExit(f"error: no code symbol '{args.symbol}'")
    for line in disassemble(s, sym.address, args.limit):
        print(f"  {line}")


def cmd_diff(args) -> None:
    a, b = load(args.expected), load(args.actual)
    print(f"expected: {args.expected}: {len(a.symbols)} symbols, code {len(a.code)} B, file {a.size} B")
    print(f"actual  : {args.actual}: {len(b.symbols)} symbols, code {len(b.code)} B, file {b.size} B")

    names_a = [s.name.upper() for s in a.symbols]
    names_b = [s.name.upper() for s in b.symbols]
    missing = [n for n in names_a if n not in b.by_name]
    extra = [n for n in names_b if n not in a.by_name]
    order_same = names_a == names_b

    diffs = {"definition": [], "value": [], "address": [], "parent": [], "position": []}
    for sa in a.symbols:
        sb = b.by_name.get(sa.name.upper())
        if sb is None:
            continue
        if (sa.type, sa.flags, sa.count, sa.vary if not sa.flags & F_MEMBER else 0) != \
                (sb.type, sb.flags, sb.count, sb.vary if not sb.flags & F_MEMBER else 0):
            diffs["definition"].append(f"{sa.describe()} vary={sa.vary}  vs  {sb.describe()} vary={sb.vary}")
        if sa.value != sb.value:
            diffs["value"].append(f"{sa.name}: {sa.value[:3]!r}  vs  {sb.value[:3]!r}")
        if sa.address != sb.address:
            diffs["address"].append(f"{sa.name}: {sa.address}  vs  {sb.address}")
        pa = a.symbols[sa.parent].name if 0 <= sa.parent < len(a.symbols) else None
        pb = b.symbols[sb.parent].name if 0 <= sb.parent < len(b.symbols) else None
        if (pa or "").upper() != (pb or "").upper():
            diffs["parent"].append(f"{sa.name}: {pa}  vs  {pb}")
        if sa.position != sb.position:
            diffs["position"].append(f"{sa.name}: {sa.position}  vs  {sb.position}")

    print()
    print(f"symbol order identical : {order_same}")
    print(f"missing in actual      : {len(missing)}")
    print(f"extra in actual        : {len(extra)}")
    for key, items in diffs.items():
        print(f"{key + ' differences':<23}: {len(items)}")
    print(f"bytecode identical     : {a.code == b.code}")
    print(f"sort table identical   : {a.sort_table == b.sort_table}")
    print(f"file identical         : {open(args.expected, 'rb').read() == open(args.actual, 'rb').read()}")

    def show(title, items):
        if items:
            print(f"\n{title} (first {min(len(items), args.limit)} of {len(items)}):")
            for item in items[:args.limit]:
                print(f"  {item}")

    show("missing in actual", missing)
    show("extra in actual", extra)
    for key, items in diffs.items():
        if key != "position" or args.with_positions:
            show(f"{key} differences", items)
    if not order_same and not missing and not extra:
        first = next(i for i, (x, y) in enumerate(zip(names_a, names_b)) if x != y)
        print(f"\nfirst order difference at index {first}: {names_a[first]} vs {names_b[first]}")


def main() -> None:
    sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("info")
    p.add_argument("file")
    p.set_defaults(func=cmd_info)
    p = sub.add_parser("symbols")
    p.add_argument("file")
    p.add_argument("--filter")
    p.set_defaults(func=cmd_symbols)
    p = sub.add_parser("disasm")
    p.add_argument("file")
    p.add_argument("symbol")
    p.add_argument("--limit", type=int, default=200)
    p.set_defaults(func=cmd_disasm)
    p = sub.add_parser("diff")
    p.add_argument("expected")
    p.add_argument("actual")
    p.add_argument("--limit", type=int, default=15)
    p.add_argument("--with-positions", action="store_true", help="also list source position differences")
    p.set_defaults(func=cmd_diff)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
