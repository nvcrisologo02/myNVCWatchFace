"""Shared Blender helpers for the 3D watch face sketches (studio, materials, geometry).

Units: 1 Blender unit = 10 watch px. Origin = dial centre, +Y up (watch y is down).
Orthographic camera straight above: renders line up pixel for pixel with the watch face.
"""
import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "art/blender/build"
HDRI = Path("C:/Users/criso/.claude/tools/blender/hdri/studio_small_09_2k.hdr")
LOGO = ROOT / "art/out/logo.png"
BARLOW = ROOT / "watchface/src/main/res/font/barlow_condensed_semibold.ttf"
BODONI = Path(__file__).resolve().parents[2] / "nocturne/src/main/res/font/bodoni_moda.ttf"  # SIL OFL
SYMBOLS = Path("C:/Windows/Fonts/seguisym.ttf")
SIZE = 46.6  # full screen width in units

scene = None


def W(x, y):
    """watch px (origin at dial centre, y down) -> Blender units"""
    return x / 10.0, -y / 10.0


def setup(samples, world_strength=0.5, key_energy=14000, strip_energy=2500):
    global scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 932
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"

    cam_data = bpy.data.cameras.new("cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = SIZE
    cam = bpy.data.objects.new("cam", cam_data)
    cam.location = (0, 0, 60)
    scene.collection.objects.link(cam)
    scene.camera = cam

    world = bpy.data.worlds.new("studio")
    scene.world = world
    world.use_nodes = True
    wn, wl = world.node_tree.nodes, world.node_tree.links
    wn.clear()
    tex = wn.new("ShaderNodeTexEnvironment")
    tex.image = bpy.data.images.load(str(HDRI))
    mapn = wn.new("ShaderNodeMapping")
    mapn.inputs["Rotation"].default_value = (0, 0, math.radians(135))
    coord = wn.new("ShaderNodeTexCoord")
    bg = wn.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = world_strength
    outw = wn.new("ShaderNodeOutputWorld")
    wl.new(coord.outputs["Generated"], mapn.inputs["Vector"])
    wl.new(mapn.outputs["Vector"], tex.inputs["Vector"])
    wl.new(tex.outputs["Color"], bg.inputs["Color"])
    # camera rays see black (the screen is black outside the dial); reflections see the studio
    mix = wn.new("ShaderNodeMixShader")
    lp = wn.new("ShaderNodeLightPath")
    black = wn.new("ShaderNodeBackground")
    black.inputs["Color"].default_value = (0, 0, 0, 1)
    wl.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    wl.new(bg.outputs["Background"], mix.inputs[1])
    wl.new(black.outputs["Background"], mix.inputs[2])
    wl.new(mix.outputs["Shader"], outw.inputs["Surface"])

    # key softbox top left (design §5.2) and a strip light on the right
    for name, size, energy, loc, rot in [
        ("key", (40, 25), key_energy, (-38, 40, 45), (-40, -35, 0)),
        ("strip", (4, 50), strip_energy, (45, 0, 30), (0, 55, 0)),
    ]:
        ld = bpy.data.lights.new(name, "AREA")
        ld.shape = "RECTANGLE"
        ld.size, ld.size_y = size
        ld.energy = energy
        lo = bpy.data.objects.new(name, ld)
        lo.location = loc
        lo.rotation_euler = tuple(math.radians(a) for a in rot)
        scene.collection.objects.link(lo)
    return scene


def render(out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    print("rendered", out)


# ------------------------------------------------------------------ materials
def nodes_of(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    return nt.nodes, nt.links


def principled(n, **kw):
    p = n.new("ShaderNodeBsdfPrincipled")
    for k, v in kw.items():
        p.inputs[k].default_value = v
    return p


def projected(n, l, path, colorspace="sRGB"):
    """Image projected straight down in watch coordinates."""
    geo = n.new("ShaderNodeNewGeometry")
    mp = n.new("ShaderNodeMapping")
    mp.vector_type = "POINT"
    mp.inputs["Scale"].default_value = (1 / SIZE, 1 / SIZE, 1)
    mp.inputs["Location"].default_value = (0.5, 0.5, 0)
    img = n.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(path), check_existing=True)
    img.image.colorspace_settings.name = colorspace
    img.extension = "CLIP"
    l.new(geo.outputs["Position"], mp.inputs["Vector"])
    l.new(mp.outputs["Vector"], img.inputs["Vector"])
    return img


def add_ink(n, l, shader, print_path):
    ink = projected(n, l, print_path)
    paint = principled(n, **{"Roughness": 0.45, "Specular IOR Level": 0.4})
    l.new(ink.outputs["Color"], paint.inputs["Base Color"])
    mx = n.new("ShaderNodeMixShader")
    l.new(ink.outputs["Alpha"], mx.inputs["Fac"])
    l.new(shader, mx.inputs[1])
    l.new(paint.outputs["BSDF"], mx.inputs[2])
    return mx.outputs["Shader"]


def finish_material(name, base_kw, print_path=None, radial_tangent=False, inlay=None, height=None,
                    height_strength=0.6, height_distance=0.02):
    """Base finish (+ optional steel inlay mask, height map bump, ink print)."""
    mat = bpy.data.materials.new(name)
    n, l = nodes_of(mat)
    out = n.new("ShaderNodeOutputMaterial")
    base = principled(n, **base_kw)
    if radial_tangent:
        t = n.new("ShaderNodeTangent")
        t.direction_type = "RADIAL"
        t.axis = "Z"
        l.new(t.outputs["Tangent"], base.inputs["Tangent"])
    if height:
        hm = projected(n, l, height, "Non-Color")
        bump = n.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = height_strength
        bump.inputs["Distance"].default_value = height_distance
        l.new(hm.outputs["Color"], bump.inputs["Height"])
        l.new(bump.outputs["Normal"], base.inputs["Normal"])
    shader = base.outputs["BSDF"]
    if inlay:
        mask_path, steel_kw = inlay
        m = projected(n, l, mask_path, "Non-Color")
        steel = principled(n, **steel_kw)
        bump = n.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 1.0
        bump.inputs["Distance"].default_value = 0.04
        l.new(m.outputs["Color"], bump.inputs["Height"])
        l.new(bump.outputs["Normal"], steel.inputs["Normal"])
        if not height:
            l.new(bump.outputs["Normal"], base.inputs["Normal"])
        mx = n.new("ShaderNodeMixShader")
        l.new(m.outputs["Color"], mx.inputs["Fac"])
        l.new(shader, mx.inputs[1])
        l.new(steel.outputs["BSDF"], mx.inputs[2])
        shader = mx.outputs["Shader"]
    if print_path:
        shader = add_ink(n, l, shader, print_path)
    l.new(shader, out.inputs["Surface"])
    return mat


def snail_material(name, base_kw, print_path, scale=18.0):
    """Recessed sub-dial floor with concentric snailing (azurage) around its own centre."""
    mat = bpy.data.materials.new(name)
    n, l = nodes_of(mat)
    out = n.new("ShaderNodeOutputMaterial")
    base = principled(n, **base_kw)
    tc = n.new("ShaderNodeTexCoord")
    wave = n.new("ShaderNodeTexWave")
    wave.wave_type = "RINGS"
    wave.rings_direction = "SPHERICAL"
    wave.inputs["Scale"].default_value = scale
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.01
    l.new(tc.outputs["Object"], wave.inputs["Vector"])
    l.new(wave.outputs["Fac"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], base.inputs["Normal"])
    l.new(add_ink(n, l, base.outputs["BSDF"], print_path), out.inputs["Surface"])
    return mat


def projected_color_material(name, path, kw):
    """Colour from a projected image (moon sky), with a principled finish."""
    mat = bpy.data.materials.new(name)
    n, l = nodes_of(mat)
    out = n.new("ShaderNodeOutputMaterial")
    img = projected(n, l, path)
    p = principled(n, **kw)
    l.new(img.outputs["Color"], p.inputs["Base Color"])
    l.new(p.outputs["BSDF"], out.inputs["Surface"])
    return mat


def simple(name, **kw):
    mat = bpy.data.materials.new(name)
    n, l = nodes_of(mat)
    out = n.new("ShaderNodeOutputMaterial")
    p = principled(n, **kw)
    l.new(p.outputs["BSDF"], out.inputs["Surface"])
    return mat


def logo_material(gold=(0.92, 0.74, 0.43, 1), roughness=0.16):
    mat = bpy.data.materials.new("logo")
    n, l = nodes_of(mat)
    out = n.new("ShaderNodeOutputMaterial")
    tc = n.new("ShaderNodeTexCoord")
    img = n.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(LOGO))
    p = principled(n, **{"Base Color": gold, "Metallic": 1.0, "Roughness": roughness})
    bump = n.new("ShaderNodeBump")
    bump.inputs["Distance"].default_value = 0.05
    l.new(tc.outputs["UV"], img.inputs["Vector"])
    l.new(img.outputs["Alpha"], p.inputs["Alpha"])
    l.new(img.outputs["Color"], bump.inputs["Height"])
    l.new(bump.outputs["Normal"], p.inputs["Normal"])
    l.new(p.outputs["BSDF"], out.inputs["Surface"])
    return mat


# ------------------------------------------------------------------ geometry
def link(obj):
    scene.collection.objects.link(obj)
    return obj


def lathe(name, profile, mat, steps=256):
    """Revolve a (radius in watch px, z in units) profile around Z."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new((r / 10.0, 0, z)) for r, z in profile]
    for a, b in zip(vs, vs[1:]):
        bm.edges.new((a, b))
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    sc = ob.modifiers.new("lathe", "SCREW")
    sc.angle = 2 * math.pi
    sc.steps = sc.render_steps = steps
    sc.axis = "Z"
    sc.use_smooth_shade = True
    sc.use_merge_vertices = True
    ob.data.materials.append(mat)
    return ob


def cylinder(name, x, y, r, z0, z1, mat, verts=128):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r / 10.0, depth=z1 - z0,
                                        location=(*W(x, y), (z0 + z1) / 2))
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def torus(name, x, y, r, minor, z, mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=r / 10.0, minor_radius=minor, major_segments=192,
                                     minor_segments=24, location=(*W(x, y), z))
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


def box(name, cx, cy, w, h, z0, z1, rot_deg, mat, bevel=0.03):
    """Box centred on watch (cx, cy), w x h watch px, rotated clockwise by rot_deg."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(*W(cx, cy), (z0 + z1) / 2))
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (w / 10.0, h / 10.0, z1 - z0)
    ob.rotation_euler = (0, 0, -math.radians(rot_deg))
    if bevel:
        bv = ob.modifiers.new("bevel", "BEVEL")
        bv.width = bevel
        bv.segments = 3
    ob.data.materials.append(mat)
    return ob


def radial_box(name, deg, r0, r1, w, z0, z1, mat, cx=0.0, cy=0.0, bevel=0.03):
    rm = (r0 + r1) / 2
    a = math.radians(deg)
    return box(name, cx + rm * math.sin(a), cy - rm * math.cos(a), w, r1 - r0, z0, z1, deg, mat, bevel)


def boolean_cut(target, cutter):
    m = target.modifiers.new("cut_" + cutter.name, "BOOLEAN")
    m.operation = "DIFFERENCE"
    m.object = cutter
    m.solver = "EXACT"
    cutter.hide_render = True
    cutter.hide_viewport = True


def _place(ob, deg, pivot):
    # meshes are built pointing along +X; 0 deg = 12 o'clock, clockwise
    ob.rotation_euler = (0, 0, math.radians(90 - deg))
    ob.location = (*W(*pivot), 0)


def hand(name, deg, length, tail, w_base, w_tip, z, thick, mat, pivot=(0.0, 0.0), lume=None, lume_mat=None,
         tip=0.80):
    """Faceted hand (two facets either side of a raised ridge), lengths in units; the point starts at tip."""
    prof = [(-tail, w_base * 0.55), (0, w_base), (length * tip, w_tip), (length, 0.0)]
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    left = [bm.verts.new((s, -w / 2, z)) for s, w in prof]
    right = [bm.verts.new((s, w / 2, z)) for s, w in prof]
    ridge = [bm.verts.new((s, 0, z + thick)) for s, _ in prof]
    for i in range(len(prof) - 1):
        bm.faces.new((left[i], left[i + 1], ridge[i + 1], ridge[i]))
        bm.faces.new((ridge[i], ridge[i + 1], right[i + 1], right[i]))
    bm.faces.new((left[0], ridge[0], right[0]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    ob.data.materials.append(mat)
    _place(ob, deg, pivot)
    if lume:
        s0, s1, lw = lume
        lb = bpy.data.meshes.new(name + "_lume")
        bm = bmesh.new()
        pts = [(length * s0, -lw / 2), (length * s1, -lw / 4), (length * s1, lw / 4), (length * s0, lw / 2)]
        bm.faces.new([bm.verts.new((x, y, z + thick + 0.005)) for x, y in pts])
        bm.to_mesh(lb)
        bm.free()
        lo = link(bpy.data.objects.new(name + "_lume", lb))
        lo.data.materials.append(lume_mat)
        _place(lo, deg, pivot)
    return ob


def breguet_hand(name, deg, length, w, ring_at, ring_r, ring_w, z, thick, mat):
    """Breguet hand: tapered shaft with an open ring ("pomme") near the tip."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    # shaft: two facets either side of a ridge, interrupted by the ring
    def shaft(s0, w0, s1, w1):
        l0, l1 = bm.verts.new((s0, -w0 / 2, z)), bm.verts.new((s1, -w1 / 2, z))
        r0, r1 = bm.verts.new((s0, w0 / 2, z)), bm.verts.new((s1, w1 / 2, z))
        k0, k1 = bm.verts.new((s0, 0, z + thick)), bm.verts.new((s1, 0, z + thick))
        bm.faces.new((l0, l1, k1, k0))
        bm.faces.new((k0, k1, r1, r0))
    wr = lambda s: w * (1 - 0.55 * max(s, 0) / length)  # noqa: E731
    shaft(-1.6, w * 0.8, ring_at - ring_r + 0.02, wr(ring_at - ring_r))
    shaft(ring_at + ring_r - 0.02, wr(ring_at + ring_r), length, 0.02)
    # ring: rounded annulus
    seg = 64
    outer = [bm.verts.new((ring_at + ring_r * math.cos(2 * math.pi * i / seg),
                           ring_r * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)]
    mid = [bm.verts.new((ring_at + (ring_r - ring_w / 2) * math.cos(2 * math.pi * i / seg),
                         (ring_r - ring_w / 2) * math.sin(2 * math.pi * i / seg), z + thick)) for i in range(seg)]
    inner = [bm.verts.new((ring_at + (ring_r - ring_w) * math.cos(2 * math.pi * i / seg),
                           (ring_r - ring_w) * math.sin(2 * math.pi * i / seg), z)) for i in range(seg)]
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((outer[i], outer[j], mid[j], mid[i]))
        bm.faces.new((mid[i], mid[j], inner[j], inner[i]))
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    ob = link(bpy.data.objects.new(name, me))
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    _place(ob, deg, (0.0, 0.0))
    return ob


def text_obj(name, body, font_path, size, x, y, z, mat, extrude=0.0, rot=0.0):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(str(font_path), check_existing=True)
    cu.size = size / 10.0
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.extrude = extrude
    ob = link(bpy.data.objects.new(name, cu))
    ob.location = (*W(x, y), z)
    ob.rotation_euler = (0, 0, -math.radians(rot))
    ob.data.materials.append(mat)
    return ob


def logo(x, y, width, z, mat):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(*W(x, y), z))
    ob = bpy.context.active_object
    ob.name = "logo"
    ob.scale = (width / 10.0, width / 10.0 * 124 / 144, 1)
    ob.data.materials.append(mat)
    return ob


def hand_angles(time):
    h, m, s = time
    return (h % 12 + m / 60) * 30, (m + s / 60) * 6, s * 6
