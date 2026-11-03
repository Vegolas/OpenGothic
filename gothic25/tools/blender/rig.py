"""Blender side of the mod animation tools (spec 004, decisions/0007-zrodla-i-budowanie-animacji-moda.md).

Started by tools/anim.ps1 with Blender 5.2 in background mode and the pinned KrxImpExp add-on:

  blender --background --factory-startup --python-exit-code 1 --python rig.py -- <command> ...
    import    WORKDIR MODEL MAN_NAME OUT.blend [--mesh MDM]   rig + action from an original MAN (reference)
    new       WORKDIR MODEL NAME OUT.blend [--mesh MDM] [--frames N]
                                                               rig + a new animation of the mod (rest pose)
    open      LIGHT.blend WORKDIR MODEL OUT.blend [--mesh MDM] working copy of a source .blend with the body
    roundtrip WORKDIR MODEL                                    MAN -> action -> MAN for every animation

WORKDIR holds the original files (tools/anim.py extract): <MODEL>.MDH, the MDM and the MAN files.
MAN_NAME is the file name without extension, e.g. HUMANS-S_FISTATTACK or HUMANS_1HST1-T_1HATTACKL.

Conventions, checked on S_RUN and S_1HATTACK (MAN -> Blender -> MAN gives the same bytes):
  - KrxImpExp keeps ZenGin node transforms row-major (v' = v @ M, translation in row 3); MDH floats
    are rows of the column-vector matrix, so local = Matrix(rows).transposed().
  - world = local @ parent_world. The MDH root gets T(root translation) @ RotX(-90) @ ScaleY(-1) @
    RotZ(180). MAN root samples are absolute (OpenGothic does not add the root translation), so
    animated roots use RotX(-90) @ ScaleY(-1) @ RotZ(180).
  - The engine lays the sample quaternion out transposed, so in this row-major form the rotation block
    is Quaternion((w, x, y, z)).to_matrix() and row 3 is the sample position.
  - Edit bones are A^-1 @ W^T @ O_b (X->Y alignment and KrxImpExp's roll). O_b comes from the rest
    pose, so pose matrices are A^-1 @ W_anim^T @ O_b. Positions are scaled by 0.01 (cm -> m).
Fields that Blender does not edit (header, raw chunks, slot samples of non-bone nodes) are kept in the
action's "g25_anim" property, so originals come back unchanged.
"""

import base64
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Quaternion, Vector

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import anim  # noqa: E402

SCALE = 0.01
C_ANIM = Matrix.Rotation(-math.pi / 2, 4, "X") @ Matrix.Scale(-1, 4, (0, 1, 0)) @ Matrix.Rotation(math.pi, 4, "Z")
C_ANIM_INV = C_ANIM.inverted()
PROP = "g25_anim"
BLENDER_VERSION = (5, 2)


def fail(msg: str):
    raise SystemExit(f"error: {msg}")


def require_blender():
    if tuple(bpy.app.version[:2]) != BLENDER_VERSION:
        fail(f"Blender {BLENDER_VERSION[0]}.{BLENDER_VERSION[1]}.x is required, this is {bpy.app.version_string}. "
             "Set blender in gothic25/local.json.")


def enable_krx():
    import addon_utils
    # --factory-startup with --addons loads the module but leaves it out of preferences.addons, and the
    # KrxImpExp operators read bpy.context.preferences.addons["krximpexp"]
    if "krximpexp" not in bpy.context.preferences.addons:
        addon_utils.enable("krximpexp", default_set=True, handle_error=None)
    mod = sys.modules.get("krximpexp")
    scripts = os.environ.get("BLENDER_USER_SCRIPTS", "")
    if mod is None or not hasattr(bpy.ops.import_scene, "batmdmimp"):
        fail("KrxImpExp is not installed. Run tools/get-krx.ps1.")
    if scripts and not os.path.normcase(mod.__file__).startswith(os.path.normcase(os.path.abspath(scripts))):
        fail(f"KrxImpExp is loaded from {mod.__file__}, not from BLENDER_USER_SCRIPTS={scripts}")


# --- ZenGin <-> Blender transforms -----------------------------------------------------------------------

def row_local(floats) -> Matrix:
    return Matrix([floats[0:4], floats[4:8], floats[8:12], floats[12:16]]).transposed()


def sample_local(s) -> Matrix:
    w, x, y, z, px, py, pz = s
    m = Quaternion((w, x, y, z)).to_matrix().to_4x4()
    m.row[3] = (px, py, pz, 1.0)
    return m


def scaled(m: Matrix, k: float = SCALE) -> Matrix:
    m = m.copy()
    m.row[3] = (m[3][0] * k, m[3][1] * k, m[3][2] * k, 1.0)
    return m


def worlds(mdh, locals_, root_fix):
    out = [None] * len(mdh.nodes)
    for i, n in enumerate(mdh.nodes):  # MDH parents precede their children
        out[i] = locals_[i] @ (root_fix if n.parent < 0 else out[n.parent])
    return out


class RigMap:
    """Bone offsets of one armature against one MDH."""

    def __init__(self, arm, mdh):
        self.arm, self.mdh = arm, mdh
        self.names = [n.name for n in mdh.nodes]
        self.rest_l = [row_local(n.matrix) for n in mdh.nodes]
        self.A = arm.matrix_world.copy()
        self.Ainv = self.A.inverted()
        c_rest = Matrix.Translation(Vector(mdh.root_translation)).transposed() @ C_ANIM
        rest_w = [scaled(w) for w in worlds(mdh, self.rest_l, c_rest)]
        bones = arm.data.bones
        self.bone_ids = [i for i, n in enumerate(self.names) if n in bones]
        self.offsets = {i: (self.Ainv @ rest_w[i].transposed()).inverted() @ bones[self.names[i]].matrix_local
                        for i in self.bone_ids}
        self.offsets_inv = {i: o.inverted() for i, o in self.offsets.items()}

    def pose_targets(self, locals_):
        """Armature-space pose matrices of the bones for ZenGin node locals (cm)."""
        w = [scaled(m) for m in worlds(self.mdh, locals_, C_ANIM)]
        return {i: self.Ainv @ w[i].transposed() @ self.offsets[i] for i in self.bone_ids}

    def frame_locals(self):
        """ZenGin locals (cm) of the bones for the evaluated pose."""
        pb = self.arm.pose.bones
        world = {i: scaled((self.A @ pb[self.names[i]].matrix @ self.offsets_inv[i]).transposed(), 1.0 / SCALE)
                 for i in self.bone_ids}
        out = {}
        for i in self.bone_ids:
            p = self.mdh.nodes[i].parent
            out[i] = world[i] @ (C_ANIM_INV if p < 0 else world[p].inverted())
        return out


def local_to_sample(m: Matrix) -> tuple:
    q = m.to_3x3().to_quaternion().normalized()
    return (q.w, q.x, q.y, q.z, m[3][0], m[3][1], m[3][2])


# --- scene -------------------------------------------------------------------------------------------------

def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    bpy.data.orphans_purge(do_recursive=True)


def import_rig(workdir: str, model: str, mesh: str | None):
    d = os.path.abspath(workdir).replace("\\", "/").rstrip("/") + "/"
    mdh = f"{model}.MDH"
    files = [{"name": mdh}] + ([{"name": mesh}] if mesh else [])
    res = bpy.ops.import_scene.batmdmimp(filepath=d + mdh, directory=d, files=files)
    if res != {"FINISHED"}:
        fail(f"KrxImpExp could not import {d}{mdh}: {res}")
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    if len(arms) != 1:
        fail(f"expected one armature after the import, got {[a.name for a in arms]}")
    return arms[0], anim.parse_mdh(open(d + mdh, "rb").read())


def strip_game_meshes():
    """Removes meshes from the game (the body); keeps the armature and the slot objects of KrxImpExp."""
    for o in list(bpy.data.objects):
        if o.type == "MESH" and not o.name.startswith("ZS_"):
            bpy.data.objects.remove(o)
    bpy.data.orphans_purge(do_recursive=True)


def save_blend(path: str):
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)  # Blender does not create folders
    bpy.ops.wm.save_as_mainfile(filepath=path, compress=True)


def set_scene_range(frames: int, fps: float):
    sc = bpy.context.scene
    sc.render.fps, sc.render.fps_base = int(round(fps)), 1.0
    sc.frame_start, sc.frame_end = 0, frames - 1


def assign_action(arm, act):
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act
    slot = arm.animation_data.action_slot
    if slot is None:
        slot = act.slots[0] if len(act.slots) else act.slots.new(id_type="OBJECT", name=arm.name)
        arm.animation_data.action_slot = slot
    return slot


# --- MAN <-> action ----------------------------------------------------------------------------------------

def header_of(a, origin: str) -> dict:
    # origin "game": imported from an original (local reference only, spec 004 W16); "mod": our own keys
    return {"origin": origin, "model": a.model, "name": a.name, "next": a.next, "version": a.version,
            "layer": a.layer, "fps": a.fps, "fps_source": a.fps_source, "checksum": a.checksum,
            "bbox": list(a.bbox), "quant": list(a.quant) if a.quant is not None else None, "layout": a.layout,
            "raw": {f"{k:04X}": base64.b64encode(v).decode("ascii") for k, v in a.raw.items()},
            "frames": a.frame_count,
            "node_indices": a.node_indices, "node_names": a.node_names}


def origin_of(act) -> str:
    # actions without the mark come from imports made before it existed
    return json.loads(act.get(PROP, "{}")).get("origin", "game")


def key_bones(rig: RigMap, act, keys: dict, frames: list):
    """keys[node] = (locations, rotations), one per frame of `frames`; LINEAR keys on the action."""
    from bpy_extras import anim_utils
    slot = assign_action(rig.arm, act)
    bag = anim_utils.action_ensure_channelbag_for_slot(act, slot)
    n = len(frames)
    for i in rig.bone_ids:
        name = rig.names[i]
        for comp, path, vals in ((3, f'pose.bones["{name}"].location', keys[i][0]),
                                 (4, f'pose.bones["{name}"].rotation_quaternion', keys[i][1])):
            for c in range(comp):
                fc = bag.fcurves.new(path, index=c, group_name=name)
                fc.keyframe_points.add(n)
                co = [0.0] * (2 * n)
                co[0::2] = frames
                co[1::2] = [v[c] for v in vals]
                fc.keyframe_points.foreach_set("co", co)
                set_linear(fc)
                fc.update()


def reset_pose(arm):
    arm.rotation_mode = "QUATERNION"
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
        pb.location, pb.rotation_quaternion, pb.scale = (0, 0, 0), (1, 0, 0, 0), (1, 1, 1)


def new_action(rig: RigMap, model: str, name: str, frames: int):
    """Action of a new animation of the mod on the bare skeleton: the rest pose keyed on the first and
    last frame, a header from the model hierarchy and no data of any original (spec 004 W2, W16)."""
    reset_pose(rig.arm)
    act = bpy.data.actions.new(name.upper())
    act.use_fake_user = True
    rest = ([Vector((0, 0, 0))] * 2, [Quaternion((1, 0, 0, 0))] * 2)
    key_bones(rig, act, {i: rest for i in rig.bone_ids}, [0, frames - 1])
    a = anim.Man(model=model, name=act.name, version=12, layer=1, checksum=rig.mdh.checksum)
    a.node_indices = list(rig.bone_ids)
    a.node_names = [rig.names[i] for i in rig.bone_ids]
    prop = header_of(a, "mod")
    prop["frames"], prop["slots"] = frames, {}
    act[PROP] = json.dumps(prop, separators=(",", ":"))
    act.use_frame_range = True
    act.frame_range = (0, max(frames - 1, 1))
    set_scene_range(frames, 25.0)
    return act


def man_to_action(rig: RigMap, a, action_name: str | None = None, origin: str = "game"):
    """Keys the bones of the MAN on a new action. Samples of non-bone nodes go to the property."""
    arm, bones = rig.arm, rig.arm.data.bones
    reset_pose(arm)
    act = bpy.data.actions.new(action_name or a.name)
    act.use_fake_user = True

    sampled = {ni: k for k, ni in enumerate(a.node_indices)}
    slots = {str(k): [] for k, ni in enumerate(a.node_indices) if ni not in rig.offsets}
    keys = {i: ([], []) for i in rig.bone_ids}
    for row in a.samples:
        loc = list(rig.rest_l)
        for ni, k in sampled.items():
            loc[ni] = sample_local(row[k])
            if str(k) in slots:
                slots[str(k)].append(list(row[k]))
        M = rig.pose_targets(loc)
        for i in rig.bone_ids:
            b = bones[rig.names[i]]
            if b.parent is not None:
                pi = rig.names.index(b.parent.name)
                basis = b.matrix_local.inverted() @ b.parent.matrix_local @ M[pi].inverted() @ M[i]
            else:
                basis = b.matrix_local.inverted() @ M[i]
            t, r, _ = basis.decompose()
            locs, rots = keys[i]
            if rots and rots[-1].dot(r) < 0:
                r.negate()
            locs.append(t)
            rots.append(r)

    n = a.frame_count
    key_bones(rig, act, keys, list(range(n)))

    prop = header_of(a, origin)
    prop["slots"] = slots
    act[PROP] = json.dumps(prop, separators=(",", ":"))
    act.use_frame_range = True
    act.frame_range = (0, max(n - 1, 1))
    set_scene_range(n, a.fps)
    return act


def set_linear(fc):
    # LINEAR like the engine between frames; foreach_set takes the enum index where supported
    try:
        fc.keyframe_points.foreach_set("interpolation", [1] * len(fc.keyframe_points))
    except (TypeError, AttributeError):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def action_frames(act) -> tuple:
    """First and last frame to export. Blender needs end > start, so one-frame originals keep their
    frame count in the property."""
    start, end = (int(round(v)) for v in act.frame_range)
    prop = json.loads(act.get(PROP, "{}"))
    if prop.get("name") == act.name and prop.get("frames") == 1:
        end = start
    return start, end


def action_to_man(rig: RigMap, act):
    """MAN of an action: bones from the evaluated pose, the rest from the property.

    An action renamed against its property is a new animation: it keeps the node list, bbox and slot
    samples, but not the name, raw chunks and quantization of the property. Whether the data may go
    into the mod's sources is decided by its origin (origin_of, export.py).
    """
    prop = json.loads(act.get(PROP, "{}"))
    if not prop:
        fail(f"action {act.name} has no {PROP} property; start from tools/anim.ps1 new")
    a = anim.Man()
    original = prop["name"] == act.name
    a.model, a.name = prop["model"], act.name
    a.next = prop["next"] if original else ""
    a.version, a.layer = prop["version"], prop["layer"]
    a.fps, a.fps_source, a.checksum = prop["fps"], prop["fps_source"], prop["checksum"]
    a.bbox = tuple(prop["bbox"])
    if original:
        a.quant = tuple(prop["quant"]) if prop["quant"] is not None else None
        a.layout = list(prop["layout"])
        a.raw = {int(k, 16): base64.b64decode(v) for k, v in prop["raw"].items()}
    a.node_indices, a.node_names = list(prop["node_indices"]), list(prop["node_names"])
    for ni in a.node_indices:
        if ni >= len(rig.names):
            fail(f"{act.name}: node index {ni} is outside the model hierarchy ({len(rig.names)} nodes)")
    slots = {int(k): v for k, v in prop["slots"].items()}

    start, end = action_frames(act)
    assign_action(rig.arm, act)
    sc = bpy.context.scene
    for f in range(start, end + 1):
        sc.frame_set(f)
        loc = rig.frame_locals()
        row = []
        for k, ni in enumerate(a.node_indices):
            if ni in loc:
                row.append(local_to_sample(loc[ni]))
            elif k in slots and slots[k]:
                row.append(tuple(slots[k][(f - start) % len(slots[k])]))
            else:
                row.append(local_to_sample(rig.rest_l[ni]))
        a.samples.append(row)
    return anim.snap(a)


# --- commands ----------------------------------------------------------------------------------------------

def cmd_import(workdir, model, man_name, out, mesh):
    clear_scene()
    arm, mdh = import_rig(workdir, model, mesh)
    rig = RigMap(arm, mdh)
    path = os.path.join(workdir, man_name + ".MAN")
    a = anim.parse_man(open(path, "rb").read(), anim.man_model(man_name))
    a.node_names = [rig.names[i] for i in a.node_indices]
    act = man_to_action(rig, a)
    save_blend(out)
    print(f"imported {man_name}: action {act.name}, {a.frame_count} frames, {len(a.node_indices)} nodes -> {out}")


def cmd_new(workdir, model, name, out, mesh, frames):
    clear_scene()
    arm, mdh = import_rig(workdir, model, mesh)
    act = new_action(RigMap(arm, mdh), model, name, frames)
    save_blend(out)
    print(f"new animation {act.name}: {frames} frames on the bare {model} skeleton -> {out}")


def cmd_open(light, workdir, model, out, mesh):
    clear_scene()
    arm, _ = import_rig(workdir, model, mesh)
    with bpy.data.libraries.load(os.path.abspath(light), link=False) as (src, dst):
        dst.actions = list(src.actions)
    acts = [a for a in bpy.data.actions if PROP in a]
    if not acts:
        fail(f"{light} has no action with the {PROP} property")
    for a in acts:
        a.use_fake_user = True
    act = acts[0]
    assign_action(arm, act)
    start, end = action_frames(act)
    set_scene_range(end - start + 1, json.loads(act[PROP])["fps"])
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = start, end
    save_blend(out)
    print(f"opened {light}: actions {[a.name for a in acts]} -> {out}")


def cmd_roundtrip(workdir, model):
    clear_scene()
    arm, mdh = import_rig(workdir, model, None)
    rig = RigMap(arm, mdh)
    prefix = (f"{model}-", f"{model}_")
    mans = sorted(f for f in os.listdir(workdir) if f.upper().endswith(".MAN") and f.upper().startswith(prefix))
    diffs = []
    for i, f in enumerate(mans):
        data = open(os.path.join(workdir, f), "rb").read()
        base = f[:-4].upper()
        a = anim.parse_man(data, anim.man_model(base))
        a.node_names = [rig.names[n] if n < len(rig.names) else "" for n in a.node_indices]
        act = man_to_action(rig, a)
        back = anim.write_man(action_to_man(rig, act))
        arm.animation_data.action = None
        bpy.data.actions.remove(act)
        if back != data:
            b = anim.parse_man(back)
            worst = max((max(abs(p - q) for p, q in zip(s1, s2)), fr, k)
                        for fr, (r1, r2) in enumerate(zip(a.samples, b.samples)) for k, (s1, s2) in enumerate(zip(r1, r2)))
            diffs.append(f"{f}: differs, largest sample difference {worst[0]:.6f} at frame {worst[1]} node {worst[2]}")
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(mans)}", flush=True)
    print(f"round trip MAN -> Blender -> MAN: {len(mans)} animations of {model} and its overlays, "
          f"{len(mans) - len(diffs)} identical, {len(diffs)} different")
    for d in diffs:
        print("  " + d)
    if not mans or diffs:
        raise SystemExit(1)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    mesh, frames = None, 30
    for flag in ("--mesh", "--frames"):
        if flag in argv:
            i = argv.index(flag)
            if flag == "--mesh":
                mesh = argv[i + 1]
            else:
                frames = int(argv[i + 1])
            del argv[i:i + 2]
    require_blender()
    enable_krx()
    cmd, args = (argv[0], argv[1:]) if argv else ("", [])
    if cmd == "import" and len(args) == 4:
        cmd_import(*args, mesh)
    elif cmd == "new" and len(args) == 4:
        if frames < 2:
            fail("a new animation needs at least 2 frames")
        cmd_new(*args, mesh, frames)
    elif cmd == "open" and len(args) == 4:
        cmd_open(*args, mesh)
    elif cmd == "roundtrip" and len(args) == 2:
        cmd_roundtrip(*args)
    else:
        fail("usage: rig.py -- import WORKDIR MODEL MAN_NAME OUT.blend [--mesh MDM] | "
             "new WORKDIR MODEL NAME OUT.blend [--mesh MDM] [--frames N] | "
             "open LIGHT.blend WORKDIR MODEL OUT.blend [--mesh MDM] | roundtrip WORKDIR MODEL")


if __name__ == "__main__":
    main()
