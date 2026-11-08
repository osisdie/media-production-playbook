"""Procedural 3D turntable: a stylised plant pot with leaves and an extruded
"Verdalo" wordmark (the fictional app from examples/promo-demo).

Everything is generated in code; no external assets. Renders an RGBA PNG
sequence with a transparent background, ready to composite in Remotion.

Run through the wrapper (finds Blender, handles WSL paths, waits for completion):
    scripts/blender/run_blender.sh scripts/blender/render_scene.py <out_dir> \
        --orientation portrait --width 1080 --height 1920 --samples 16
Direct use:
    blender -b --factory-startup -P scripts/blender/render_scene.py -- --out <dir> [options]

Options (after "--"):
    --out DIR             output folder (frame_0001.png ...); writes DIR/.done when finished
    --orientation O       portrait (plant above wordmark) | landscape (side by side)
    --width/--height PX   resolution (default 1080x1920 portrait, 1920x1080 landscape)
    --seconds S --fps F   turntable length (default 6 s at 30 fps; loops seamlessly)
    --samples N           EEVEE TAA samples or Cycles samples (default 16)
    --engine E            eevee | cycles | workbench (default eevee)
    --frames A-B          render only this frame range (for quick checks)
Tested with Blender 5.2 LTS; uses only long-stable bpy APIs.
"""
import json
import math
import os
import sys
import time
import traceback

import bmesh
import bpy
from mathutils import Matrix, Vector


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opts = {"out": None, "orientation": "portrait", "width": 0, "height": 0, "seconds": 6.0,
            "fps": 30, "samples": 16, "engine": "eevee", "frames": ""}
    i = 0
    while i < len(argv):
        key = argv[i].lstrip("-")
        if key in opts and i + 1 < len(argv):
            cur = opts[key]
            val = argv[i + 1]
            opts[key] = type(cur)(val) if cur is not None and not isinstance(cur, str) else val
            i += 2
        else:
            raise SystemExit(f"unknown or incomplete option: {argv[i]}")
    if not opts["out"]:
        raise SystemExit("--out is required")
    portrait = opts["orientation"] == "portrait"
    opts["width"] = opts["width"] or (1080 if portrait else 1920)
    opts["height"] = opts["height"] or (1920 if portrait else 1080)
    return opts


# --- materials ----------------------------------------------------------------

def material(name, color, roughness=0.5, sheen=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    for key, val in (("Sheen Weight", sheen), ("Coat Weight", coat)):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = val
    return m


def srgb(h):
    """Hex colour -> linear RGB tuple (Blender colour inputs are linear)."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


# --- geometry -----------------------------------------------------------------

def lathe(name, profile, segments=64, mat=None):
    """Revolve a list of (radius, z) points around Z into a smooth closed mesh."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        ring = []
        for k in range(segments):
            a = 2 * math.pi * k / segments
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(segments):
            bm.faces.new((r0[k], r0[(k + 1) % segments], r1[(k + 1) % segments], r1[k]))
    bm.faces.new(list(reversed(rings[0])))  # bottom cap
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    if mat:
        ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    return ob


def leaf(name, length, width, mat):
    """A single curved leaf: midrib rises then droops, edges cup slightly upwards."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    nu, nv = 18, 7
    grid = []
    for i in range(nu + 1):
        t = i / nu
        w = width * math.sin(math.pi * min(1.0, t ** 0.75)) * (1.0 - 0.15 * t)
        x = length * t
        z = length * (1.15 * t - 0.95 * t * t)
        row = []
        for j in range(nv + 1):
            s = -1 + 2 * j / nv
            row.append(bm.verts.new((x, s * w, z + 0.35 * w * s * s)))
        grid.append(row)
    for i in range(nu):
        for j in range(nv):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    mod = ob.modifiers.new("thickness", "SOLIDIFY")
    mod.thickness = 0.015
    ob.modifiers.new("smooth", "SUBSURF").levels = 1
    bpy.context.collection.objects.link(ob)
    return ob


def build_plant(parent):
    terracotta = material("Terracotta", srgb("#D9774A"), roughness=0.7)
    rim = material("Rim", srgb("#E88A5C"), roughness=0.65)
    soil = material("Soil", srgb("#3B2A20"), roughness=0.95)
    greens = [material(f"Leaf{i}", srgb(c), roughness=0.45, sheen=0.2)
              for i, c in enumerate(["#3E9C5A", "#58B86F", "#2F8F5B", "#6CCB7E"])]

    pot = lathe("Pot", [(0.62, 0.0), (0.70, 0.05), (0.86, 0.95), (0.80, 0.95), (0.79, 0.90)], mat=terracotta)
    lip = lathe("PotLip", [(0.84, 0.86), (0.98, 0.88), (1.0, 1.08), (0.96, 1.12), (0.86, 1.10)], mat=rim)
    dirt = lathe("Soil", [(0.0, 0.98), (0.86, 0.98), (0.86, 1.0), (0.0, 1.0)], mat=soil)
    for ob in (pot, lip, dirt):
        ob.parent = parent

    # Leaves radiate from the soil centre at golden-angle spacing.
    golden = math.radians(137.5)
    for i in range(9):
        L = 1.35 + 0.35 * math.sin(i * 1.7)
        lf = leaf(f"Leaf{i}", L, 0.34 + 0.05 * (i % 3), greens[i % len(greens)])
        tilt = math.radians(-(6 + 14 * (i % 3)))  # small lift; the leaf's own curve does the rest
        lf.matrix_world = (Matrix.Translation((0, 0, 1.0)) @ Matrix.Rotation(i * golden, 4, "Z")
                           @ Matrix.Rotation(tilt, 4, "Y"))
        lf.parent = parent
        # keep world transform after parenting
        lf.matrix_parent_inverse = parent.matrix_world.inverted()


def build_wordmark():
    cream = material("Wordmark", srgb("#E8E2D2"), roughness=0.5)
    cu = bpy.data.curves.new("Verdalo", "FONT")
    cu.body = "Verdalo"
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.size = 1.0
    cu.extrude = 0.12
    cu.bevel_depth = 0.018
    cu.bevel_resolution = 2
    ob = bpy.data.objects.new("Wordmark", cu)
    ob.data.materials.append(cream)
    bpy.context.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(90), 0, 0)
    return ob


# --- scene --------------------------------------------------------------------

def setup_scene(o):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = o["width"], o["height"]
    sc.render.resolution_percentage = 100
    sc.render.fps = o["fps"]
    sc.frame_start = 1
    sc.frame_end = int(round(o["seconds"] * o["fps"]))
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.image_settings.color_depth = "8"
    sc.view_settings.view_transform = "Standard"  # graphic colours, matches the 2D palette
    sc.view_settings.look = "None"

    engines = {e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items}
    want = {"eevee": ["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"], "cycles": ["CYCLES"],
            "workbench": ["BLENDER_WORKBENCH"]}[o["engine"]]
    sc.render.engine = next(e for e in want if e in engines)
    if sc.render.engine.startswith("BLENDER_EEVEE"):
        sc.eevee.taa_render_samples = o["samples"]
    elif sc.render.engine == "CYCLES":
        sc.cycles.samples = o["samples"]
        sc.cycles.device = "CPU"
        sc.cycles.use_denoising = True

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (*srgb("#DCE8DF"), 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
    sc.world = world
    return sc


def add_light(name, kind, loc, energy, size, color="#FFFFFF"):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = srgb(color)
    if kind == "AREA":
        ld.size = size
    else:
        ld.shadow_soft_size = size
    ob = bpy.data.objects.new(name, ld)
    ob.location = loc
    bpy.context.collection.objects.link(ob)
    # aim at the origin area
    direction = Vector((0, 0, 1.2)) - ob.location
    ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return ob


def main():
    o = parse_args()
    out = o["out"]
    os.makedirs(out, exist_ok=True)
    portrait = o["orientation"] == "portrait"
    sc = setup_scene(o)

    pivot = bpy.data.objects.new("PlantPivot", None)
    bpy.context.collection.objects.link(pivot)
    build_plant(pivot)
    word = build_wordmark()

    # Layout: portrait stacks the wordmark under the pot; landscape puts it to the right.
    if portrait:
        pivot.location = (0, 0, 0.55)
        word.location = (0, -0.6, -0.55)
        word.scale = (1.05, 1.05, 1.05)
        target, dist, lens = Vector((0, 0, 0.72)), 12.25, 50
    else:
        pivot.location = (-2.3, 0, 0)
        word.location = (1.25, -0.3, 1.2)
        word.scale = (1.05, 1.05, 1.05)
        target, dist, lens = Vector((-0.2, 0, 1.15)), 10.5, 45

    cam_d = bpy.data.cameras.new("Camera")
    cam_d.lens = lens
    cam = bpy.data.objects.new("Camera", cam_d)
    bpy.context.collection.objects.link(cam)
    cam.location = target + Vector((0, -dist, dist * 0.32))
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam

    add_light("Key", "AREA", (4.0, -4.5, 6.0), 750, 4.0, "#FFF4E2")
    add_light("Fill", "AREA", (-5.0, -3.0, 3.0), 300, 5.0, "#E2F0FF")
    add_light("Rim", "AREA", (0.0, 5.0, 5.0), 600, 3.0, "#FFFFFF")

    # Seamless loop: the plant turns 360 degrees; the wordmark sways gently so it stays readable.
    n = sc.frame_end
    for f in (1, n + 1):
        pivot.rotation_euler = (0, 0, 2 * math.pi * (f - 1) / n)
        pivot.keyframe_insert("rotation_euler", index=2, frame=f)
    for fc in _fcurves(pivot):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    base_z = word.rotation_euler.z
    for k in range(0, 5):
        f = 1 + k * n / 4
        word.rotation_euler.z = base_z + math.radians(12) * math.sin(2 * math.pi * k / 4)
        word.keyframe_insert("rotation_euler", index=2, frame=f)

    if o["frames"]:
        a, b = (int(x) for x in o["frames"].split("-"))
        sc.frame_start, sc.frame_end = a, b
    sc.render.filepath = os.path.join(out, "frame_")
    t0 = time.time()
    bpy.ops.render.render(animation=True)
    info = {"frames": sc.frame_end - sc.frame_start + 1, "fps": o["fps"], "width": o["width"],
            "height": o["height"], "engine": sc.render.engine, "samples": o["samples"],
            "seconds_wall": round(time.time() - t0, 1), "blender": bpy.app.version_string}
    with open(os.path.join(out, ".done"), "w") as f:
        json.dump(info, f)
    print("render_scene done", info)


def _fcurves(ob):
    """F-curves of an object's action (Blender 5 layered actions or the legacy list)."""
    act = ob.animation_data.action
    if hasattr(act, "fcurves") and len(getattr(act, "fcurves", [])):
        return list(act.fcurves)
    curves = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                curves.extend(bag.fcurves)
    return curves


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        o_dir = None
        if "--out" in sys.argv:
            o_dir = sys.argv[sys.argv.index("--out") + 1]
        if o_dir:
            os.makedirs(o_dir, exist_ok=True)
            with open(os.path.join(o_dir, ".failed"), "w") as f:
                f.write(traceback.format_exc())
        raise
