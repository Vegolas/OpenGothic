#!/usr/bin/env python3
"""Pack, list and extract Gothic VDF/MOD archives (PSVDSC_V2.00, uncompressed).

Layout mirrors zenkit::Vfs::save (lib/ZenKit/src/Vfs.cc):
  header : comment[256] | signature[16] | entries | files | dos_time | data_size | catalog_offset | flags
  catalog: entries of 80 bytes; the children of one directory are contiguous, the last one carries
           0x40000000, directories carry 0x80000000 and point (by entry index) at their first child
  data   : raw file contents, in catalog order

Usage:
  vdf.py pack OUT --map SRC_DIR=ARCHIVE/PREFIX [--map ...] [--exclude GLOB ...] [--comment TEXT] [--g1]
  vdf.py list ARCHIVE
  vdf.py extract ARCHIVE OUT_DIR [--include GLOB ...]
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import shutil
import struct
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

SIGNATURE_G1 = b"PSVDSC_V2.00\r\n\r\n"
SIGNATURE_G2 = b"PSVDSC_V2.00\n\r\n\r"
SIGNATURE_VDFSTOOL = b"PSVDSC_V2.00\x1a\x1a\x1a\x1a"

HEADER = struct.Struct("<256s16s6I")
ENTRY = struct.Struct("<64s4I")

TYPE_DIR = 0x80000000
TYPE_LAST = 0x40000000
FLAG_NORMAL = 0x50
ATTR_ARCHIVE = 0x20
NAME_ENCODING = "cp1252"


@dataclass
class Node:
    name: str
    source: Path | None = None  # None for directories
    children: dict[str, "Node"] = field(default_factory=dict)

    @property
    def is_dir(self) -> bool:
        return self.source is None


def dos_time(unix: float) -> int:
    t = time.localtime(unix)
    return ((t.tm_year - 1980) << 25) | (t.tm_mon << 21) | (t.tm_mday << 16) \
        | (t.tm_hour << 11) | (t.tm_min << 5) | (t.tm_sec // 2)


def unix_time(dos: int) -> float:
    try:
        return time.mktime((((dos >> 25) & 0x7F) + 1980, (dos >> 21) & 0x0F, (dos >> 16) & 0x1F,
                            (dos >> 11) & 0x1F, (dos >> 5) & 0x3F, (dos & 0x1F) * 2, 0, 0, -1))
    except (OverflowError, ValueError):
        return 0.0


def archive_name(part: str) -> str:
    name = part.upper()
    encoded = name.encode(NAME_ENCODING)
    if len(encoded) > 64:
        raise SystemExit(f"error: name longer than 64 bytes: {part}")
    return name


def is_excluded(rel: str, patterns: list[str]) -> bool:
    """Case-insensitive fnmatch where '*' also crosses '/', and '**/' may match zero directories."""
    rel = rel.lower()
    for pattern in patterns:
        pattern = pattern.lower()
        variants = {pattern, pattern.replace("/**/", "/")}
        if pattern.startswith("**/"):
            variants.add(pattern[3:])
        if any(fnmatch.fnmatchcase(rel, v) for v in variants):
            return True
    return False


def build_tree(mappings: list[tuple[Path, str]], excludes: list[str]) -> Node:
    root = Node("")
    for src_dir, prefix in mappings:
        if not src_dir.is_dir():
            print(f"note: {src_dir} does not exist, skipped", file=sys.stderr)
            continue
        prefix_parts = [archive_name(p) for p in PurePosixPath(prefix).parts if p not in ("", "/")]
        for path in sorted(src_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(src_dir).as_posix()
            if is_excluded(rel, excludes):
                continue
            parts = prefix_parts + [archive_name(p) for p in PurePosixPath(rel).parts]
            node = root
            for part in parts[:-1]:
                child = node.children.get(part)
                if child is None:
                    child = node.children[part] = Node(part)
                elif not child.is_dir:
                    raise SystemExit(f"error: '{part}' is both a file and a directory ({path})")
                node = child
            leaf = parts[-1]
            previous = node.children.get(leaf)
            if previous is not None:
                if previous.is_dir:
                    raise SystemExit(f"error: '{leaf}' is both a file and a directory ({path})")
                print(f"override: {'/'.join(parts)} <- {path}", file=sys.stderr)
            node.children[leaf] = Node(leaf, source=path)
    return root


def prune(node: Node) -> bool:
    """Drop empty directories; returns True when the node itself is empty."""
    for name in list(node.children):
        child = node.children[name]
        if child.is_dir and prune(child):
            del node.children[name]
    return node.is_dir and not node.children


def pack(out: Path, root: Node, comment: str, signature: bytes, timestamp: float) -> tuple[int, int]:
    prune(root)
    if not root.children:
        raise SystemExit("error: nothing to pack (no files left in the mapped directories after excludes)")

    # Catalog order: all children of a directory, then each sub-directory recursively.
    catalog: list[list] = []  # [name, offset, size, type, attributes, node]
    files: list[tuple[int, Node]] = []

    def emit(node: Node) -> None:
        children = sorted(node.children.values(), key=lambda n: n.name.encode(NAME_ENCODING))
        dirs = []
        for i, child in enumerate(children):
            last = TYPE_LAST if i + 1 == len(children) else 0
            if child.is_dir:
                catalog.append([child.name, 0, 0, TYPE_DIR | last, 0, child])
                dirs.append(len(catalog) - 1)
            else:
                catalog.append([child.name, 0, child.source.stat().st_size, last, ATTR_ARCHIVE, child])
                files.append((len(catalog) - 1, child))
        for index in dirs:
            catalog[index][1] = len(catalog)
            emit(catalog[index][5])

    emit(root)

    offset = HEADER.size + len(catalog) * ENTRY.size
    for index, _ in files:
        catalog[index][1] = offset
        offset += catalog[index][2]
    data_size = offset - HEADER.size - len(catalog) * ENTRY.size

    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    with open(tmp, "wb") as f:
        f.write(HEADER.pack(comment.encode(NAME_ENCODING, "replace")[:256].ljust(256, b"\x1a"),
                            signature, len(catalog), len(files), dos_time(timestamp),
                            data_size, HEADER.size, FLAG_NORMAL))
        for name, off, size, typ, attr, _ in catalog:
            f.write(ENTRY.pack(name.encode(NAME_ENCODING).ljust(64, b" "), off, size, typ, attr))
        for _, node in files:
            with open(node.source, "rb") as src:
                shutil.copyfileobj(src, f, 1 << 20)
    os.replace(tmp, out)
    return len(catalog), len(files)


def read_catalog(path: Path):
    """Yields (archive_path, offset, size) for every file; returns header info via first item."""
    with open(path, "rb") as f:
        raw = f.read(HEADER.size)
        if len(raw) < HEADER.size:
            raise SystemExit(f"error: {path} is too small to be a VDF")
        comment, signature, entries, file_count, dos, data_size, catalog_offset, flags = HEADER.unpack(raw)
        if signature not in (SIGNATURE_G1, SIGNATURE_G2, SIGNATURE_VDFSTOOL):
            raise SystemExit(f"error: {path}: unknown signature {signature!r}")
        if flags not in (FLAG_NORMAL, 0):
            raise SystemExit(f"error: {path}: compressed volumes (flags 0x{flags:X}) are not supported")
        f.seek(catalog_offset or HEADER.size)
        table = [ENTRY.unpack(f.read(ENTRY.size)) for _ in range(entries)]

    info = {
        "comment": comment.split(b"\x1a", 1)[0].rstrip(b"\0").decode(NAME_ENCODING, "replace"),
        "signature": {SIGNATURE_G1: "G1", SIGNATURE_G2: "G2"}.get(signature, "VDFS tool"),
        "entries": entries, "files": file_count, "data_size": data_size, "time": unix_time(dos),
    }

    result = []

    def walk(start: int, prefix: str) -> None:
        index = start
        while index < len(table):
            name, off, size, typ, _ = table[index]
            name = name.decode(NAME_ENCODING).rstrip(" \0")
            if typ & TYPE_DIR:
                walk(off, f"{prefix}{name}/")
            else:
                result.append((f"{prefix}{name}", off, size))
            if typ & TYPE_LAST:
                break
            index += 1

    if table:
        walk(0, "")
    return info, result


def cmd_pack(args) -> None:
    mappings = []
    for item in args.map:
        src, sep, prefix = item.partition("=")
        if not sep:
            raise SystemExit(f"error: --map expects SRC=PREFIX, got '{item}'")
        mappings.append((Path(src), prefix))
    timestamp = float(os.environ.get("SOURCE_DATE_EPOCH", time.time()))
    root = build_tree(mappings, args.exclude or [])
    entries, files = pack(Path(args.out), root, args.comment,
                          SIGNATURE_G1 if args.g1 else SIGNATURE_G2, timestamp)
    size = Path(args.out).stat().st_size
    print(f"packed {files} files ({entries} entries, {size / 1048576:.1f} MiB) -> {args.out}")


def cmd_list(args) -> None:
    info, files = read_catalog(Path(args.archive))
    print(f"# {args.archive}: {info['signature']}, {info['files']} files, "
          f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info['time']))}, comment: {info['comment']!r}")
    for name, _, size in files:
        print(f"{size:>12}  {name}")


def cmd_extract(args) -> None:
    _, files = read_catalog(Path(args.archive))
    out_dir = Path(args.out_dir)
    count = 0
    with open(args.archive, "rb") as f:
        for name, off, size in files:
            if args.include and not any(fnmatch.fnmatch(name, p.upper()) for p in args.include):
                continue
            target = out_dir.joinpath(*name.split("/"))
            if out_dir.resolve() not in target.resolve().parents:
                raise SystemExit(f"error: entry escapes output directory: {name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            f.seek(off)
            with open(target, "wb") as dst:
                remaining = size
                while remaining:
                    chunk = f.read(min(remaining, 1 << 20))
                    if not chunk:
                        raise SystemExit(f"error: truncated archive at {name}")
                    dst.write(chunk)
                    remaining -= len(chunk)
            count += 1
    print(f"extracted {count} files -> {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("pack", help="pack directories into a VDF/MOD archive")
    p.add_argument("out")
    p.add_argument("--map", action="append", required=True, metavar="SRC=PREFIX",
                   help="directory to pack and its path inside the archive; later maps override earlier ones")
    p.add_argument("--exclude", action="append", metavar="GLOB", help="glob relative to a mapped directory")
    p.add_argument("--comment", default="")
    p.add_argument("--g1", action="store_true", help="write the Gothic 1 signature")
    p.set_defaults(func=cmd_pack)

    p = sub.add_parser("list", help="list files in an archive")
    p.add_argument("archive")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("extract", help="extract files from an archive")
    p.add_argument("archive")
    p.add_argument("out_dir")
    p.add_argument("--include", action="append", metavar="GLOB", help="e.g. '*/DIA_ADDON_*.WAV'")
    p.set_defaults(func=cmd_extract)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
