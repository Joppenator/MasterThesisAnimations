"""1D -> 2D -> 3D view of the C5 packing.

Render:  uv run manim render 1D_to_3d_C5grid.py OneDto3DC5Grid -pql
"""

import random

from manim import *

config.background_color = WHITE

U = 0.7                      # cell size
N = 5
DARK = BLACK
GRID_GREY = GREY_B
FRONT_Z = -U - 0.05          # front cube layer centre (just behind the flat front face)
BACK_Z = -3 * U - 0.05       # back cube layer centre
CUBE_FILL = "#ECECEC"        # near-white, but visible / occluding on the white background

# C5 torus packing: 2x2 boxes (top-left row, col) and wrap direction; empty cells
C5_BOXES = [(0, 0, None), (1, 2, None), (2, 4, "col"), (3, 1, None), (4, 3, "row")]
C5_HATCH = [(0, 2), (1, 4), (2, 1), (3, 3), (4, 0)]


def c2d(r, c):
    """Centre of 2D cell (row r from the top, col c from the left)."""
    return np.array([(c - (N - 1) / 2) * U, ((N - 1) / 2 - r) * U, 0.0])


def hatch_lines(center, size):
    g = VGroup()
    half = size / 2
    for off in np.linspace(-0.66 * size, 0.66 * size, 13):
        sx = max(-half, -half - off)
        ex = min(half, half - off)
        g.add(Line(center + np.array([sx, sx + off, 0]),
                   center + np.array([ex, ex + off, 0]),
                   stroke_width=1.4, color=DARK))
    return g


def cell_2d(r, c, hatched=False):
    sq = Square(side_length=U, stroke_width=2, stroke_color=DARK,
                fill_color=WHITE, fill_opacity=1).move_to(c2d(r, c))
    return VGroup(sq, hatch_lines(c2d(r, c), U)) if hatched else VGroup(sq)


def box_center_2d(r, c):
    return c2d(r, c) + np.array([0.5 * U, -0.5 * U, 0])


def box_2d(r, c, wrap):
    st = dict(stroke_width=3, stroke_color=DARK, fill_color=WHITE, fill_opacity=1)
    if wrap is None:
        return VGroup(Rectangle(width=2 * U, height=2 * U, **st).move_to(box_center_2d(r, c)))
    if wrap == "col":                                  # cols {c, (c+1)%N} == {4, 0}
        a = Rectangle(width=U, height=2 * U, **st).move_to(c2d(r, N - 1) + [0, -0.5 * U, 0])
        b = Rectangle(width=U, height=2 * U, **st).move_to(c2d(r, 0) + [0, -0.5 * U, 0])
        return VGroup(a, b)
    a = Rectangle(width=2 * U, height=U, **st).move_to(c2d(N - 1, c) + [0.5 * U, 0, 0])
    b = Rectangle(width=2 * U, height=U, **st).move_to(c2d(0, c) + [0.5 * U, 0, 0])
    return VGroup(a, b)


def box_cells(r, c, wrap):
    if wrap is None:
        return [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]
    if wrap == "col":
        return [(r, N - 1), (r + 1, N - 1), (r, 0), (r + 1, 0)]
    return [(N - 1, c), (N - 1, c + 1), (0, c), (0, c + 1)]


def cube_3d(r, c, wrap, zc):
    st = dict(fill_color=CUBE_FILL, fill_opacity=1.0, stroke_width=3, stroke_color=DARK)
    bx, by, _ = box_center_2d(r, c)
    if wrap is None:
        return Cube(side_length=2 * U, **st).move_to([bx, by, zc])
    if wrap == "col":
        yy = c2d(r, N - 1)[1] - 0.5 * U
        a = Prism(dimensions=[U, 2 * U, 2 * U], **st).move_to([c2d(r, N - 1)[0], yy, zc])
        b = Prism(dimensions=[U, 2 * U, 2 * U], **st).move_to([c2d(r, 0)[0], yy, zc])
        return VGroup(a, b)
    xx = c2d(N - 1, c)[0] + 0.5 * U
    a = Prism(dimensions=[2 * U, U, 2 * U], **st).move_to([xx, c2d(N - 1, c)[1], zc])
    b = Prism(dimensions=[2 * U, U, 2 * U], **st).move_to([xx, c2d(0, c)[1], zc])
    return VGroup(a, b)


def box_wire_5x5x5():
    lo, hi = -2.5 * U, 2.5 * U
    zf, zb = 0.0, -5 * U
    edge = dict(stroke_width=1.8, color=GRID_GREY)
    faint = dict(stroke_width=0.8, color=GREY_C)
    g = VGroup()
    verts = [np.array([x, y, z]) for x in (lo, hi) for y in (lo, hi) for z in (zf, zb)]
    for i, p in enumerate(verts):
        for q in verts[i + 1:]:
            if sum(1 for a, b in zip(p, q) if abs(a - b) > 1e-6) == 1:
                g.add(Line(p, q, **edge))
    for i in range(1, N):                              # a few faint depth ticks along the base
        t = lo + i * U
        g.add(Line([lo, lo, -i * U], [hi, lo, -i * U], **faint))
        g.add(Line([lo, lo, -i * U], [lo, hi, -i * U], **faint))
    return g


class OneDto3DC5Grid(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

        title = Text("C₅ packing:  1D → 2D → 3D", font_size=26, color=DARK)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)

        # ---------- 1D: a 1x5 row, two length-2 boxes, empty (hatched) middle ----
        row0_cells = VGroup(*[
            Square(side_length=U, stroke_width=2, stroke_color=DARK,
                   fill_color=WHITE, fill_opacity=1).move_to([(c - 2) * U, 0, 0])
            for c in range(N)
        ])
        dom_st = dict(width=2 * U, height=U, stroke_width=3, stroke_color=DARK,
                      fill_color=WHITE, fill_opacity=1)
        dom1 = Rectangle(**dom_st).move_to([-1.5 * U, 0, 0])
        dom2 = Rectangle(**dom_st).move_to([1.5 * U, 0, 0])
        hatch0 = hatch_lines(np.array([0.0, 0.0, 0.0]), U)

        self.play(LaggedStartMap(Create, row0_cells, lag_ratio=0.2), run_time=1.2)
        self.play(Create(dom1), Create(dom2), FadeIn(hatch0), run_time=1.0)
        self.wait(0.8)

        # ---------- smooth top-down transition: 1x5 rises to be row 0, 5x5 grows down
        one_d = VGroup(row0_cells, dom1, dom2, hatch0)
        self.play(one_d.animate.shift(UP * 2 * U), run_time=0.9)

        box00 = box_2d(0, 0, None)                         # dom1 grows into this
        box43 = box_2d(4, 3, "row")                        # row-0 stub == dom2
        lower_rows = []
        for r in range(1, N):
            parts = VGroup(*[cell_2d(r, c, (r, c) in C5_HATCH) for c in range(N)])
            for (br, bc, w) in C5_BOXES:
                if br == r:
                    parts.add(box_2d(br, bc, w))
            if r == N - 1:
                parts.add(box43[0])                        # the row-4 stub of box (4,3)
            lower_rows.append(FadeIn(parts, shift=DOWN * 0.25))

        self.play(
            LaggedStart(*lower_rows, lag_ratio=0.4),
            ReplacementTransform(dom1, box00),
            ReplacementTransform(dom2, box43[1]),
            run_time=2.8,
        )
        self.wait(1.0)

        # ---------- to 3D: the full config is instantly there, then we turn it ----
        # the flat 2D C5 packing stays untouched as the front 5x5 face
        random.seed(7)
        picks = sorted(random.sample(range(len(C5_BOXES)), 2))

        wire3d = box_wire_5x5x5()
        front_cubes = [cube_3d(r, c, w, FRONT_Z) for (r, c, w) in C5_BOXES]
        back_cubes = [cube_3d(r, c, w, BACK_Z) for (r, c, w) in C5_BOXES]
        for p in picks:                                    # nudge 4 cubes one cell deeper
            front_cubes[p].shift([0, 0, -U])
            back_cubes[p].shift([0, 0, -U])

        self.play(
            FadeIn(wire3d),
            FadeIn(VGroup(*front_cubes)), FadeIn(VGroup(*back_cubes)),
            run_time=0.7,
        )
        self.move_camera(phi=20 * DEGREES, theta=-68 * DEGREES, run_time=2.2)
        self.wait(0.5)
        self.move_camera(phi=62 * DEGREES, theta=-15 * DEGREES, run_time=3.2)
        self.wait(0.4)
        self.move_camera(phi=78 * DEGREES, theta=-190 * DEGREES, run_time=4.0)
        self.wait(0.4)
        self.move_camera(phi=16 * DEGREES, theta=-90 * DEGREES, run_time=3.2)
        self.wait(1.4)
