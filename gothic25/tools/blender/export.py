"""Exports one action of a working .blend as the build source of the mod (spec 004 W1, ADR 0007):
<OUTDIR>/<ACTION>.anim (text) and <OUTDIR>/<ACTION>.blend (armature and this action, no game meshes).

  blender --background --factory-startup --python-exit-code 1 --python export.py -- \\
      WORK.blend OUTDIR WORKDIR MODEL [--action NAME] [--allow-derived]

WORKDIR holds <MODEL>.MDH and the original MAN files from the game (tools/anim.py extract). Without
--action the active action of the armature is exported. The working .blend itself is not changed.

An action imported from an original (origin "game", also when renamed) may go to the mod's sources
once it is changed (ADR 0009). An unchanged copy of the original never does (spec 004 W16,
constitution principle 6): export refuses it. --allow-derived exports it, but only into
gothic25/build, for local test data.
"""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig  # noqa: E402

BUILD_DIR = os.path.join(os.path.dirname(rig.TOOLS), "build")
# quaternion components of a MAN are quantized in steps of 2.1/65535; a change below two steps is no change
ROT_TOLERANCE = 2 * 2.1 / 65535


def write_anim(a, outdir):
    path = os.path.join(outdir, a.name + ".anim")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(rig.anim.to_text(a))
    return path


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


def inside(path: str, folder: str) -> bool:
    path, folder = os.path.normcase(os.path.abspath(path)), os.path.normcase(os.path.abspath(folder))
    return path == folder or path.startswith(folder + os.sep)


def original_of(act, workdir: str) -> str:
    """The original MAN file an imported action came from."""
    import json
    prop = json.loads(act.get(rig.PROP, "{}"))
    return os.path.join(workdir, f"{prop.get('model', '').upper()}-{prop.get('name', act.name).upper()}.MAN")


def unchanged_original(act, a, workdir: str) -> bool:
    """True when `a` (the MAN of an imported action) has the same nodes and samples as its original,
    within the quantization of the format: the positions may be quantized anew after a rename."""
    if rig.origin_of(act) != "game":
        return False
    path = original_of(act, workdir)
    if not os.path.exists(path):
        rig.fail(f"action {act.name} was imported from {os.path.basename(path)}, which is not in {workdir}: "
                 "run tools/anim.ps1 import again so the export can check that the animation was changed")
    orig = rig.anim.parse_man(open(path, "rb").read(), a.model)
    if orig.node_indices != a.node_indices or len(orig.samples) != len(a.samples):
        return False
    pos_tol = 2 * max(orig.quant[1] if orig.quant else 0.0, a.quant[1] if a.quant else 0.0) + 1e-9
    for row_o, row_a in zip(orig.samples, a.samples):
        for so, sa in zip(row_o, row_a):
            if any(abs(x - y) > ROT_TOLERANCE for x, y in zip(so[:4], sa[:4])):
                return False
            if any(abs(x - y) > pos_tol for x, y in zip(so[4:7], sa[4:7])):
                return False
    return True


def check_origin(act, a, outdir: str, workdir: str, allow_derived: bool):
    if not unchanged_original(act, a, workdir):
        return
    if not allow_derived:
        rig.fail(f"action {act.name} is an unchanged copy of the original {os.path.basename(original_of(act, workdir))} "
                 "and may not go into the mod (spec 004 W16): change it first. For local test data only, "
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
    mdh = rig.anim.parse_mdh(open(os.path.join(workdir, f"{model}.MDH"), "rb").read())
    a = rig.action_to_man(rig.RigMap(arm, mdh), act)
    check_origin(act, a, outdir, workdir, allow_derived)
    os.makedirs(outdir, exist_ok=True)
    anim_path = write_anim(a, outdir)
    blend_path = save_light(act, outdir)
    print(f"exported {act.name}: {a.frame_count} frames, {len(a.node_indices)} nodes -> {anim_path}, {blend_path}")


if __name__ == "__main__":
    main()
