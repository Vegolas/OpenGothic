"""Exports one action of a working .blend as the build source of the mod (spec 004 W1, ADR 0007):
<OUTDIR>/<ACTION>.anim (text) and <OUTDIR>/<ACTION>.blend (armature and this action, no game meshes).

  blender --background --factory-startup --python-exit-code 1 --python export.py -- \\
      WORK.blend OUTDIR WORKDIR MODEL [--action NAME] [--allow-derived]

WORKDIR holds <MODEL>.MDH from the game (tools/anim.py extract). Without --action the active action
of the armature is exported. The working .blend itself is not changed.

An action imported from an original (origin "game", also when renamed) never goes to the mod's
sources (spec 004 W16): export refuses it. --allow-derived exports it, but only into gothic25/build,
for local test data.
"""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402


def export_action(rmap, act, outdir):
    a = rig.action_to_man(rmap, act)
    text = rig.anim.to_text(a)
    path = os.path.join(outdir, act.name + ".anim")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return a, path


def save_light(act, outdir):
    """Armature, slot objects and only this action, saved as a copy."""
    rig.strip_game_meshes()
    for other in list(bpy.data.actions):
        if other != act:
            bpy.data.actions.remove(other)
    bpy.data.orphans_purge(do_recursive=True)
    path = os.path.join(outdir, act.name + ".blend")
    bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, compress=True)
    return path


def find_armature():
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(arms) != 1:
        rig.fail(f"{bpy.data.filepath}: expected one armature, got {[a.name for a in arms]}")
    return arms[0]


BUILD_DIR = os.path.join(os.path.dirname(rig.TOOLS), "build")


def inside(path: str, folder: str) -> bool:
    path, folder = os.path.normcase(os.path.abspath(path)), os.path.normcase(os.path.abspath(folder))
    return path == folder or path.startswith(folder + os.sep)


def check_origin(act, outdir: str, allow_derived: bool):
    if rig.origin_of(act) != "game":
        return
    if not allow_derived:
        rig.fail(f"action {act.name} comes from an imported original and may not go into the mod "
                 "(spec 004 W16). Start the animation with tools/anim.ps1 new; for local test data only, "
                 "export with -AllowDerived into gothic25/build.")
    if not inside(outdir, BUILD_DIR):
        rig.fail(f"-AllowDerived exports only into {BUILD_DIR}, not {outdir}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    name = None
    allow_derived = "--allow-derived" in argv
    if allow_derived:
        argv.remove("--allow-derived")
    if "--action" in argv:
        i = argv.index("--action")
        name = argv[i + 1]
        del argv[i:i + 2]
    if len(argv) != 4:
        rig.fail("usage: export.py -- WORK.blend OUTDIR WORKDIR MODEL [--action NAME] [--allow-derived]")
    work, outdir, workdir, model = argv
    rig.require_blender()
    rig.enable_krx()
    bpy.ops.wm.open_mainfile(filepath=os.path.abspath(work))
    arm = find_armature()
    if name:
        act = bpy.data.actions.get(name)
        if act is None:
            rig.fail(f"{work}: no action {name}")
    else:
        act = arm.animation_data.action if arm.animation_data else None
        if act is None:
            rig.fail(f"{work}: the armature has no active action, pass --action")
    check_origin(act, outdir, allow_derived)
    mdh = rig.anim.parse_mdh(open(os.path.join(workdir, f"{model}.MDH"), "rb").read())
    os.makedirs(outdir, exist_ok=True)
    a, anim_path = export_action(rig.RigMap(arm, mdh), act, outdir)
    blend_path = save_light(act, outdir)
    print(f"exported {act.name}: {a.frame_count} frames, {len(a.node_indices)} nodes -> {anim_path}, {blend_path}")


if __name__ == "__main__":
    main()
