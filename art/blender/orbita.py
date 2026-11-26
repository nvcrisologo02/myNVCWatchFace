"""NVC Orbita (sketch, 2026-11-26): the user's own design, docs/referencias/orbita-referencia.png.

Knurled grey rim (r 226..233), silver ring (r 200..226) with two coloured sectors (the colour is
chosen on the watch), step bars and steps at the top, battery and heart rate at the bottom; dark zone
with the hour ticks; a big silver globe (sphere r 190, the user's relief map on a black sea) seen
through a window of r 152; the user's satellite over its right edge; the glucose value in a sub-dial
at 6; hollow baton hands. All measured on the reference picture, see
art/blender/build/orbita_ref_grid.png.

  python art/blender/make_prints.py
  python art/satellite_sprite.py docs/referencias/satelite.png art/blender/build/orbita_satellite.png 218 190 112 8
  blender -b -P art/blender/orbita.py -- <out.png> [samples] [colour] [mode]

colour: verde (default) | naranja | rojo | amarillo | azul
mode: sketch (default) | bg: production dial, no dynamic content, sectors in neutral silver |
      ring: only the coloured sectors in white anodised aluminium, transparent elsewhere and under
      the printed numerals, for the watch to tint (design 2026-11-26-orbita §4 A) |
      ref: as bg but with the sectors really in <colour>, the target the tint is fitted to
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watchkit as wk  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = Path(argv[0]) if argv else wk.ROOT / "docs/mockup/propuestas/orbita_3d.png"
SAMPLES = int(argv[1]) if len(argv) > 1 else 128
COLOUR = argv[2] if len(argv) > 2 else "verde"
MODE = argv[3] if len(argv) > 3 else "sketch"  # sketch | bg (production dial) | ring (tint layer) | ref
BG = MODE in ("bg", "ring", "ref")
TIME = (10, 8, 37)  # as in the reference picture
PRINT = wk.BUILD / ("orbita_print_bg.png" if BG else "orbita_print.png")

RING_COLOURS = {  # linear RGB, anodised aluminium look
    "verde": (0.14, 0.38, 0.15, 1),
    "naranja": (0.80, 0.22, 0.03, 1),
    "rojo": (0.55, 0.03, 0.03, 1),
    "amarillo": (0.85, 0.60, 0.05, 1),
    "azul": (0.03, 0.12, 0.50, 1),
}
RING_WHITE = (0.9, 0.9, 0.9, 1)  # ring mode: white anodised, the watch multiplies it by the chosen colour
RIM_IN, RING_IN, WINDOW = 226.0, 200.0, 170.0
GLOBE_R = WINDOW / 10  # a full hemisphere filling the window: real limb shading, like the reference
GLOBE_Z = 0.0

wk.setup(SAMPLES, world_strength=1.0, key_energy=15000)
wk.scene.view_settings.exposure = 0.8  # the reference is high-key: whites must be white
if MODE == "ring":
    wk.scene.render.film_transparent = True

STEEL = wk.simple("steel", **{"Base Color": (0.78, 0.78, 0.80, 1), "Metallic": 1.0, "Roughness": 0.22})
STEEL_POL = wk.simple("steel_pol", **{"Base Color": (0.85, 0.85, 0.87, 1), "Metallic": 1.0, "Roughness": 0.08})
WHITE_M = wk.simple("white_m", **{"Base Color": (0.93, 0.93, 0.92, 1), "Metallic": 0.1, "Roughness": 0.4,
                                  "Emission Color": (1, 1, 1, 1), "Emission Strength": 0.08})
HAND_M = wk.simple("hand_m", **{"Base Color": (0.95, 0.95, 0.95, 1), "Metallic": 0.5, "Roughness": 0.25,
                                "Emission Color": (1, 1, 1, 1), "Emission Strength": 0.15})
DARK = wk.simple("dark", **{"Base Color": (0.04, 0.04, 0.045, 1), "Roughness": 0.45})
BLACK = wk.simple("black", **{"Base Color": (0.008, 0.008, 0.01, 1), "Roughness": 0.5, "Specular IOR Level": 0.15})
ORANGE = wk.simple("orange", **{"Base Color": (0.90, 0.18, 0.03, 1), "Roughness": 0.35})
TXT = wk.simple("txt", **{"Base Color": (0.92, 0.92, 0.90, 1), "Roughness": 0.4,
                          "Emission Color": (1, 1, 1, 1), "Emission Strength": 0.25})
GLASS = wk.simple("crystal", **{"Roughness": 0.0, "Transmission Weight": 1.0, "IOR": 1.77})
SILVER_KW = {"Base Color": (0.88, 0.88, 0.88, 1), "Metallic": 0.25, "Roughness": 0.38, "Anisotropic": 0.5}


def ring_material(colour):
    """Ring: anodised colour on the two sectors, brushed silver elsewhere, ink on top. In bg mode the
    sectors are silver too; in ring mode only the sectors are opaque (white, to be tinted) and the
    printed numerals are holes, so the dial's own numerals show through the tinted layer."""
    mat = bpy.data.materials.new("ring")
    n, l = wk.nodes_of(mat)
    out = n.new("ShaderNodeOutputMaterial")
    mask = wk.projected(n, l, wk.BUILD / "orbita_ring_mask.png", "Non-Color")
    sector = SILVER_KW if MODE == "bg" else {"Base Color": colour, "Metallic": 0.8, "Roughness": 0.25,
                                             "Coat Weight": 0.3, "Anisotropic": 0.6}
    col = wk.principled(n, **sector)
    silver = wk.principled(n, **SILVER_KW)
    t = n.new("ShaderNodeTangent")
    t.direction_type = "RADIAL"
    t.axis = "Z"
    for p in (col, silver):
        l.new(t.outputs["Tangent"], p.inputs["Tangent"])
    if MODE == "ring":
        ink = wk.projected(n, l, PRINT)
        keep = n.new("ShaderNodeMath")
        keep.operation = "SUBTRACT"
        keep.inputs[0].default_value = 1.0
        l.new(ink.outputs["Alpha"], keep.inputs[1])
        fac = n.new("ShaderNodeMath")
        fac.operation = "MULTIPLY"
        l.new(mask.outputs["Color"], fac.inputs[0])
        l.new(keep.outputs["Value"], fac.inputs[1])
        tr = n.new("ShaderNodeBsdfTransparent")
        mx = n.new("ShaderNodeMixShader")
        l.new(fac.outputs["Value"], mx.inputs["Fac"])
        l.new(tr.outputs["BSDF"], mx.inputs[1])
        l.new(col.outputs["BSDF"], mx.inputs[2])
        l.new(mx.outputs["Shader"], out.inputs["Surface"])
        return mat
    mx = n.new("ShaderNodeMixShader")
    l.new(mask.outputs["Color"], mx.inputs["Fac"])
    l.new(silver.outputs["BSDF"], mx.inputs[1])
    l.new(col.outputs["BSDF"], mx.inputs[2])
    l.new(wk.add_ink(n, l, mx.outputs["Shader"], PRINT), out.inputs["Surface"])
    return mat


def globe_material():
    """The user's relief map (silver, alpha = land) projected from above on the sphere, in relief
    under the key light, over a black sea; both darkened towards the window edge so the dome reads
    as a sphere."""
    mat = bpy.data.materials.new("globe")
    n, l = wk.nodes_of(mat)
    out = n.new("ShaderNodeOutputMaterial")
    img = wk.projected(n, l, wk.BUILD / "orbita_map.png")
    hgt = wk.projected(n, l, wk.BUILD / "orbita_map_height.png", "Non-Color")
    # vignette: 1 - 0.55 * (r / r_window) ^ 2.5 from the object-space radius
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ")
    l.new(tc.outputs["Object"], sep.inputs["Vector"])
    flat = n.new("ShaderNodeCombineXYZ")
    l.new(sep.outputs["X"], flat.inputs["X"])
    l.new(sep.outputs["Y"], flat.inputs["Y"])
    rad = n.new("ShaderNodeVectorMath")
    rad.operation = "LENGTH"
    l.new(flat.outputs["Vector"], rad.inputs[0])

    def math_node(op, a, val):
        m = n.new("ShaderNodeMath")
        m.operation = op
        l.new(a, m.inputs[0])
        m.inputs[1].default_value = val
        return m.outputs[0]

    fall = math_node("MULTIPLY", math_node("POWER", math_node("DIVIDE", rad.outputs["Value"], WINDOW / 10), 3.0), 0.35)
    vig = n.new("ShaderNodeMath")
    vig.operation = "SUBTRACT"
    vig.inputs[0].default_value = 1.0
    l.new(fall, vig.inputs[1])
    shade = n.new("ShaderNodeVectorMath")
    shade.operation = "SCALE"
    l.new(img.outputs["Color"], shade.inputs[0])
    l.new(vig.outputs["Value"], shade.inputs["Scale"])
    land = wk.principled(n, **{"Metallic": 0.35, "Roughness": 0.38, "Emission Strength": 0.12})
    l.new(shade.outputs["Vector"], land.inputs["Base Color"])
    l.new(shade.outputs["Vector"], land.inputs["Emission Color"])
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 1.0
    bump.inputs["Distance"].default_value = 0.18
    l.new(hgt.outputs["Color"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], land.inputs["Normal"])
    sea_col = n.new("ShaderNodeVectorMath")
    sea_col.operation = "SCALE"
    sea_col.inputs[0].default_value = (0.02, 0.02, 0.022)
    l.new(vig.outputs["Value"], sea_col.inputs["Scale"])
    sea = wk.principled(n, **{"Metallic": 0.0, "Roughness": 0.18, "Specular IOR Level": 0.3})  # black lacquer
    l.new(sea_col.outputs["Vector"], sea.inputs["Base Color"])
    mx = n.new("ShaderNodeMixShader")
    l.new(img.outputs["Alpha"], mx.inputs["Fac"])
    l.new(sea.outputs["BSDF"], mx.inputs[1])
    l.new(land.outputs["BSDF"], mx.inputs[2])
    l.new(mx.outputs["Shader"], out.inputs["Surface"])
    return mat


def sprite_layer(name, path, z):
    """Full-frame picture (932 px, alpha) as a flat self-lit layer at height z."""
    mat = bpy.data.materials.new(name)
    n, l = wk.nodes_of(mat)
    out = n.new("ShaderNodeOutputMaterial")
    tc = n.new("ShaderNodeTexCoord")
    img = n.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(path))
    img.extension = "CLIP"
    l.new(tc.outputs["UV"], img.inputs["Vector"])
    em = n.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = 1.0
    l.new(img.outputs["Color"], em.inputs["Color"])
    tr = n.new("ShaderNodeBsdfTransparent")
    mx = n.new("ShaderNodeMixShader")
    l.new(img.outputs["Alpha"], mx.inputs["Fac"])
    l.new(tr.outputs["BSDF"], mx.inputs[1])
    l.new(em.outputs["Emission"], mx.inputs[2])
    l.new(mx.outputs["Shader"], out.inputs["Surface"])
    bpy.ops.mesh.primitive_plane_add(size=wk.SIZE, location=(0, 0, z))
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    ob.visible_shadow = False
    return ob


DIAL = wk.finish_material("dial", {"Base Color": (0.035, 0.035, 0.038, 1), "Metallic": 0.0, "Roughness": 0.5,
                                   "Specular IOR Level": 0.15}, PRINT)
SUBRING = wk.finish_material("subring", SILVER_KW, PRINT, radial_tangent=True)
RIM = wk.finish_material("rim", {"Base Color": (0.32, 0.32, 0.33, 1), "Metallic": 0.9, "Roughness": 0.45,
                                 "Anisotropic": 0.6}, PRINT, radial_tangent=True)

# knurled rim (r 226..233), ring (r 200..226) with its silver edges, dark zone with the hour ticks, window
rim = wk.cylinder("rim", 0, 0, 233, -0.3, 0.30, RIM, verts=256)
wk.boolean_cut(rim, wk.cylinder("cut_rim", 0, 0, RIM_IN, -1, 1, BLACK, verts=256))
wk.torus("rim_edge", 0, 0, RIM_IN + 0.2, 0.06, 0.28, STEEL_POL)
ring = wk.cylinder("ring", 0, 0, RIM_IN + 0.3, -0.3, 0.25, ring_material(RING_WHITE if MODE == "ring" else RING_COLOURS[COLOUR]), verts=256)
wk.boolean_cut(ring, wk.cylinder("cut_ring", 0, 0, RING_IN, -1, 1, BLACK, verts=256))
wk.torus("ring_edge", 0, 0, RING_IN + 0.3, 0.06, 0.22, STEEL_POL)
wk.cylinder("dial", 0, 0, RING_IN + 0.5, -0.4, 0.02, DIAL, verts=256)
wk.torus("window_edge", 0, 0, WINDOW + 0.6, 0.07, 0.06, STEEL_POL)

# globe: a big sphere, mostly sunk under the dial, showing through the window
bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=GLOBE_R, location=(0, 0, GLOBE_Z))
globe = bpy.context.active_object
globe.name = "globe"
globe.data.materials.append(globe_material())
for p in globe.data.polygons:
    p.use_smooth = True
GLOBE_TOP = GLOBE_Z + GLOBE_R

# satellite: the user's PNG, made white and placed by art/satellite_sprite.py, over the globe
SZ = GLOBE_TOP + 0.3
sprite_layer("satellite_shadow", wk.BUILD / "orbita_satellite_shadow.png", SZ - 0.1)
sprite_layer("satellite", wk.BUILD / "orbita_satellite.png", SZ)

# glucose sub-dial at 6: silver tick ring around a recessed dark disc, over the globe
GX, GY, GO, GI = 0, 134, 62, 46
GZ = GLOBE_Z + math.sqrt(GLOBE_R ** 2 - ((GY - GO) / 10) ** 2) + 0.6  # clear of the globe under its top edge
sub = wk.cylinder("sub_ring", GX, GY, GO, GZ - 0.3, GZ, SUBRING, verts=192)
wk.boolean_cut(sub, wk.cylinder("cut_sub", GX, GY, GI, GZ - 1, GZ + 1, BLACK))
wk.cylinder("sub_disc", GX, GY, GI + 0.5, GZ - 0.3, GZ - 0.18, BLACK)
wk.torus("sub_rim", GX, GY, GI + 0.3, 0.05, GZ - 0.02, STEEL_POL)
wk.torus("sub_rim_out", GX, GY, GO + 0.3, 0.10, GZ - 0.05, STEEL_POL)
wk.cylinder("sub_skirt", GX, GY, GO, 0, GZ - 0.3, STEEL)
for ob in bpy.data.objects:
    if ob.name.startswith("sub_"):
        ob.visible_shadow = False

if not BG:
    wk.text_obj("gval", "112", wk.BARLOW, 48, GX, GY, GZ - 0.17, TXT)
    hd, md_, sd = wk.hand_angles(TIME)
    HZ = SZ + 0.5
    wk.outlined_shoulder_hand("hour", hd, *wk.ORBITA_HOUR, HZ, HAND_M, BLACK)
    wk.outlined_shoulder_hand("minute", md_, *wk.ORBITA_MINUTE, HZ + 0.45, HAND_M, BLACK)
    wk.hand("second", sd, 22.1, 4.3, 0.40, 0.16, HZ + 0.75, 0.06, ORANGE)
    wk.cylinder("cap_ring", 0, 0, 9.5, HZ + 0.50, HZ + 0.80, BLACK, verts=64)
    wk.cylinder("cap", 0, 0, 8.0, HZ + 0.52, HZ + 0.84, ORANGE, verts=64)
    wk.cylinder("cap_in", 0, 0, 4.5, HZ + 0.84, HZ + 0.88, DARK, verts=48)
    wk.cylinder("cap_pin", 0, 0, 2.2, HZ + 0.88, HZ + 0.94, WHITE_M, verts=48)

if MODE == "ring":  # the other parts still cast light/shadow context but are not seen
    for ob in bpy.data.objects:
        if ob.type in ("MESH", "CURVE", "FONT") and ob.name != "ring":
            ob.hide_render = True

wk.render(OUT)
