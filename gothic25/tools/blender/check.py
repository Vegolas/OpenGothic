"""Checks that every source .blend of a model matches its .anim (spec 004 W1): exports the action named
like the file again and compares the text. Exits with 1 on a difference or a missing .anim.

  blender --background --factory-startup --python-exit-code 1 --python check.py -- SRCDIR WORKDIR MODEL
"""

import difflib
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export  # noqa: E402
import rig  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(argv) != 3:
        rig.fail("usage: check.py -- SRCDIR WORKDIR MODEL")
    srcdir, workdir, model = argv
    rig.require_blender()
    rig.enable_krx()
    mdh = rig.anim.parse_mdh(open(os.path.join(workdir, f"{model}.MDH"), "rb").read())
    blends = sorted(f for f in os.listdir(srcdir) if f.lower().endswith(".blend"))
    problems = []
    for f in blends:
        stem = f[:-len(".blend")]
        anim_path = os.path.join(srcdir, stem + ".anim")
        if not os.path.exists(anim_path):
            problems.append(f"{f}: no {stem}.anim next to it (run tools/anim.ps1 export)")
            continue
        bpy.ops.wm.open_mainfile(filepath=os.path.abspath(os.path.join(srcdir, f)))
        act = bpy.data.actions.get(stem)
        if act is None:
            problems.append(f"{f}: no action {stem}")
            continue
        a = rig.action_to_man(rig.RigMap(export.find_armature(), mdh), act)
        if export.unchanged_original(act, a, workdir) and not export.inside(srcdir, export.BUILD_DIR):
            problems.append(f"{f}: the action is an unchanged copy of an original (spec 004 W16)")
            continue
        text = rig.anim.to_text(a)
        with open(anim_path, encoding="utf-8") as fin:
            stored = fin.read()
        if text != stored:
            diff = list(difflib.unified_diff(stored.splitlines(), text.splitlines(), lineterm="", n=0))
            problems.append(f"{f}: differs from {stem}.anim ({len(diff)} diff lines), first: "
                            + "; ".join(diff[2:5]))
    print(f"checked {len(blends)} .blend files in {srcdir}: {len(blends) - len(problems)} match their .anim")
    for p in problems:
        print("  " + p)
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
