from manim import *

config.background_color = WHITE

# ---------------------------------------------------------------------------
# The "Pjotr process" (perturbation + compression on fraction graphs, see
# main_v2.pdf) visualised on the C5 square-packing.
#
#   E_{5/2} x E_{5/2}     5x5 torus, 5 cubes
#     -- Baumert expansion --------------->  E_{7/2} x E_{7/2}     7x7, 10 cubes
#     -- scale the grid lines x10 -------->  70x70 grid, 20x20 cubes
#     -- shift cubes on integer lines ---->  perturb coord 1 by n_{1,x} = 9..0
#     -- scale the cubes ---------------->   20x21
#     -- scale the grid lines x7 wider -->   E_{10/3} x E_{7/2}    10x70, 3x20
#     -- same on coordinate 2 ---------->    E_{10/3} x E_{10/3}   10x10, 3x3
#
# One coarse cube keeps a fixed screen size; the OUTER grid lines are drawn
# past the board edge and their spacing is what scales (x10 finer, then x7
# wider) when the modulus p changes.
# ---------------------------------------------------------------------------

U0 = 0.64                 # screen size of one cube-half cell (7x7 resolution)
BCX, BCY = 0.0, -0.35     # board centre
EXT = 0.34                # how far the grid lines poke outside the board

POS7 = {"A": (0, 0), "B": (0, 2), "C": (2, 0), "D": (2, 2), "E": (1, 5),
        "F": (6, 5), "G": (3, 4), "H": (4, 1), "I": (5, 3), "J": (4, 6)}
N1 = {"A": 0, "B": 7, "C": 1, "D": 8, "E": 4, "F": 3, "G": 5, "H": 9, "I": 6, "J": 2}
POS_10x7 = {n: ((10 * POS7[n][0] + N1[n]) // 7, POS7[n][1]) for n in POS7}
N2 = {"A": 8, "B": 9, "C": 1, "D": 2, "E": 0, "F": 7, "G": 3, "H": 5, "I": 6, "J": 4}
COL10 = {"A": 1, "B": 4, "C": 0, "D": 3, "E": 7, "F": 8, "G": 6, "H": 2, "I": 5, "J": 9}
POS_10x10 = {n: (POS_10x7[n][0], COL10[n]) for n in POS7}

PERTURB1 = ["H", "D", "B", "I", "G", "E", "F", "J", "C"]     # reverse chain, coord 1
PERTURB2 = ["B", "A", "F", "I", "H", "J", "G", "D", "C"]     # reverse chain, coord 2


def _split(start, length, total):
    end = start + length
    if end <= total + 1e-9:
        return [(start, min(end, total))]
    return [(start, total), (0.0, end - total)]


class PjotrProcess(Scene):

    # -- geometry ----------------------------------------------------------
    def bw(self):
        return self.fnc * self.uc

    def bh(self):
        return self.fnr * self.ur

    def fp(self, r, c):
        return np.array([BCX - self.bw() / 2 + c * self.uc,
                         BCY + self.bh() / 2 - r * self.ur, 0.0])

    def screen_hatch(self, spacing=0.19):
        g = VGroup()
        xl, xr, yb, yt = -8.6, 8.6, -5.3, 5.3
        k, step = xl - yt, spacing * np.sqrt(2.0)
        while k <= xr - yb:
            x0, x1 = max(xl, k + yb), min(xr, k + yt)
            if x1 - x0 > 1e-6:
                g.add(Line([x0, x0 - k, 0.0], [x1, x1 - k, 0.0],
                           stroke_width=1.0, color=BLACK))
            k += step
        g.set_z_index(-1)
        return g

    def make_mask(self):
        SX, SY = 8.6, 5.3
        t, b = BCY + self.bh() / 2, BCY - self.bh() / 2
        l, r = BCX - self.bw() / 2, BCX + self.bw() / 2
        parts = [
            Rectangle(width=2 * SX, height=max(SY - t, 0.01)).move_to([0, (t + SY) / 2, 0]),
            Rectangle(width=2 * SX, height=max(b + SY, 0.01)).move_to([0, (b - SY) / 2, 0]),
            Rectangle(width=max(l + SX, 0.01), height=2 * SY).move_to([(l - SX) / 2, 0, 0]),
            Rectangle(width=max(SX - r, 0.01), height=2 * SY).move_to([(SX + r) / 2, 0, 0]),
        ]
        m = VGroup(*parts).set_fill(WHITE, 1).set_stroke(width=0)
        m.set_z_index(0.5)
        return m

    def make_border(self):
        return Rectangle(width=self.bw(), height=self.bh(), stroke_color=BLACK,
                         stroke_width=3, fill_opacity=0).move_to([BCX, BCY, 0]).set_z_index(1.2)

    def make_grid(self):
        g = VGroup()
        ec, er = EXT / self.uc, EXT / self.ur
        for i in range(self.fnr + 1):                       # horizontal lines
            bold = (i % self.cr == 0)
            g.add(Line(self.fp(i, -ec), self.fp(i, self.fnc + ec),
                       stroke_width=1.8 if bold else 0.7,
                       color=GREY_B if bold else "#d8d8d8"))
        for j in range(self.fnc + 1):                       # vertical lines
            bold = (j % self.cc == 0)
            g.add(Line(self.fp(-er, j), self.fp(self.fnr + er, j),
                       stroke_width=1.8 if bold else 0.7,
                       color=GREY_B if bold else "#d8d8d8"))
        g.set_z_index(1.0)
        return g

    def build_cube(self, row, col, h, w):
        g = VGroup()
        for (r0, r1) in _split(row, h, self.fnr):
            for (c0, c1) in _split(col, w, self.fnc):
                p0, p1 = self.fp(r0, c0), self.fp(r1, c1)
                g.add(Rectangle(width=abs(p1[0] - p0[0]), height=abs(p1[1] - p0[1]),
                                fill_color=WHITE, fill_opacity=1.0,
                                stroke_color=BLACK, stroke_width=2.4).move_to((p0 + p1) / 2))
        g.set_z_index(3)
        return g

    # -- helpers ------------------------------------------------------
    def morph(self, new_states):
        anims = []
        for n, st in new_states.items():
            self.cs[n] = list(st)
            anims.append(Transform(self.cm[n], self.build_cube(*self.cs[n])))
        return anims

    def status_to(self, tex):
        return Transform(self.status, MathTex(tex, color=BLACK).scale(0.8).move_to(self.status))

    def set_caption(self, s):
        new = Text(s, font_size=21, color=BLACK).move_to([0, -4.0, 0]).set_z_index(10)
        self.play(FadeOut(self.cap), FadeIn(new), run_time=0.5)
        self.cap = new

    # -- main -------------------------------------------------------
    def construct(self):
        self.add(self.screen_hatch())
        self.fnr = self.fnc = 5
        self.ur = self.uc = U0
        self.cr = self.cc = 1
        self.mask, self.border, self.grid = self.make_mask(), self.make_border(), self.make_grid()
        self.add(self.mask, self.border, self.grid)

        self.title = Text("Pjotr process — cube packing", font_size=27, color=BLACK).to_edge(UP, buff=0.26)
        self.status = MathTex(r"E_{5/2}\boxtimes E_{5/2}", color=BLACK).scale(0.8).next_to(self.title, DOWN, buff=0.12)
        self.cap = Text("C₅ packing on a 5×5 torus", font_size=21, color=BLACK).move_to([0, -4.0, 0])
        for m in (self.title, self.status, self.cap):
            m.set_z_index(10)

        # ---- stage 0: 5x5 C5 packing --------------------------------
        self.cs = {"D": [0, 0, 2, 2], "G": [1, 2, 2, 2], "J": [2, 4, 2, 2],
                   "I": [3, 1, 2, 2], "F": [4, 3, 2, 2]}
        self.cm = {n: self.build_cube(*st) for n, st in self.cs.items()}
        self.play(FadeIn(self.title), FadeIn(self.status), FadeIn(self.border),
                  FadeIn(self.grid), *[FadeIn(m) for m in self.cm.values()], run_time=1.1)
        self.play(FadeIn(self.cap), run_time=0.5)
        self.wait(0.8)

        # ---- stage 1: Baumert expansion 5x5 -> 7x7 ----------------
        self.set_caption("Baumert expansion: duplicate the first 2 rows & columns")
        self.fnr = self.fnc = 7
        ng = self.make_grid()
        self.play(FadeOut(self.grid), FadeIn(ng),
                  Transform(self.mask, self.make_mask()), Transform(self.border, self.make_border()),
                  *self.morph({n: (POS7[n][0], POS7[n][1], 2, 2) for n in ("D", "G", "J", "I", "F")}),
                  run_time=2.0)
        self.grid = ng
        for n in ("A", "B", "C", "E", "H"):
            self.cs[n] = [POS7[n][0], POS7[n][1], 2, 2]
            self.cm[n] = self.build_cube(*self.cs[n])
        self.play(*[FadeIn(self.cm[n]) for n in ("A", "B", "C", "E", "H")],
                  self.status_to(r"E_{7/2}\boxtimes E_{7/2}"), run_time=1.4)
        self.wait(0.7)

        # ---- stage 2: scale the grid lines x10 -> 70x70 ---------
        self.set_caption("scale the grid lines ×10:  70×70 grid,  cubes 20×20")
        self.fnr = self.fnc = 70
        self.ur = self.uc = U0 / 10
        self.cr = self.cc = 10
        ng = self.make_grid()
        self.play(FadeOut(self.grid),
                  *self.morph({n: (r * 10, c * 10, 20, 20) for n, (r, c, *_ ) in
                               [(k, self.cs[k]) for k in self.cs]}), run_time=0.9)
        self.grid = ng
        self.play(LaggedStartMap(FadeIn, self.grid, lag_ratio=0.004), run_time=1.7)
        self.wait(0.5)

        # ---- stage 3: shift the cubes (still on integer lines) --
        self.set_caption("shift each cube down by 9, 8, 7, …, 0  —  onto integer lines")
        for n in PERTURB1:
            self.cs[n][0] += N1[n]
            tgt = self.build_cube(*self.cs[n])
            if n in ("F", "J"):
                self.play(Transform(self.cm[n], tgt), run_time=0.45)
            else:
                hl = SurroundingRectangle(self.cm[n], color=YELLOW, stroke_width=4, buff=0.03).set_z_index(6)
                self.play(Create(hl), run_time=0.14)
                self.play(Transform(self.cm[n], tgt), run_time=0.46)
                self.play(FadeOut(hl), run_time=0.12)
            self.wait(0.05)
        self.wait(0.4)

        # ---- stage 4: scale the cubes -> 20x21 ------------------
        self.set_caption("scale the cubes:  20×21  (they are stuck again)")
        self.play(*self.morph({n: (self.cs[n][0], self.cs[n][1], 21, 20) for n in self.cs}),
                  self.status_to(r"E_{70/21}\boxtimes E_{7/2}"), run_time=1.5)
        self.wait(0.5)

        # ---- stage 5: scale the grid lines x7 wider (rows) -----
        self.set_caption("scale the row grid lines ×7 wider  (keep every 7th)")
        kill = VGroup(*[self.grid[i] for i in range(self.fnr + 1) if i % 7 != 0])
        self.play(FadeOut(kill), run_time=1.5)
        self.fnr = 10
        self.ur = U0 / 10 * 7
        self.cr = 1
        self.cs = {n: [self.cs[n][0] // 7, self.cs[n][1], 3, self.cs[n][3]] for n in self.cs}
        ng = self.make_grid()
        self.play(FadeOut(self.grid), FadeIn(ng), *self.morph(dict(self.cs)),
                  Transform(self.border, self.make_border()), Transform(self.mask, self.make_mask()),
                  self.status_to(r"E_{10/3}\boxtimes E_{7/2}"), run_time=0.9)
        self.grid = ng
        self.wait(0.7)

        # ---- stage 6: same on coordinate 2 -> 10x10 -----------
        self.set_caption("coordinate 2:  shift the cubes right by  9, 8, …, 0")
        for n in PERTURB2:
            self.cs[n][1] += N2[n]
            tgt = self.build_cube(*self.cs[n])
            if n in ("F", "J"):
                self.play(Transform(self.cm[n], tgt), run_time=0.4)
            else:
                hl = SurroundingRectangle(self.cm[n], color=YELLOW, stroke_width=4, buff=0.03).set_z_index(6)
                self.play(Create(hl), run_time=0.12)
                self.play(Transform(self.cm[n], tgt), run_time=0.4)
                self.play(FadeOut(hl), run_time=0.1)
            self.wait(0.04)

        self.set_caption("scale the cubes:  21 wide,  then align to integer lines")
        self.play(*self.morph({n: (self.cs[n][0], self.cs[n][1], 3, 21) for n in self.cs}), run_time=1.0)
        self.play(*self.morph({n: (self.cs[n][0], self.cs[n][1] - 1, 3, 21) for n in self.cs}), run_time=0.4)

        self.set_caption("scale the column grid lines ×7 wider  (keep every 7th)")
        kill = VGroup(*[self.grid[self.fnr + 1 + j] for j in range(self.fnc + 1) if j % 7 != 0])
        self.play(FadeOut(kill), run_time=1.4)
        self.fnc = 10
        self.uc = U0 / 10 * 7
        self.cc = 1
        self.cs = {n: [self.cs[n][0], self.cs[n][1] // 7, 3, 3] for n in self.cs}
        ng = self.make_grid()
        self.play(FadeOut(self.grid), FadeIn(ng), *self.morph(dict(self.cs)),
                  Transform(self.border, self.make_border()), Transform(self.mask, self.make_mask()),
                  self.status_to(r"E_{10/3}\boxtimes E_{10/3}"), run_time=0.9)
        self.grid = ng
        self.set_caption("done:  10 cubes of 3×3 on a 10×10 torus")
        self.wait(2.0)
