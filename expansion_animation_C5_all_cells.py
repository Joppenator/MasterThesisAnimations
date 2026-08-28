from manim import *

config.background_color = WHITE

# --- geometry -------------------------------------------------------------
CELL = 0.78
GRID_RIGHT_X = 5.2                       # x of the fixed 7x7 grid's right edge
GRID_MID_Y = -0.2                        # y of the fixed 7x7 grid's centre
GRID_LEFT_X = GRID_RIGHT_X - 7 * CELL
GRID_TOP_Y = GRID_MID_Y + 3.5 * CELL
HATCH_N = 15

# 5x5 C5 torus packing: empty (hatched) cell column per row, and the 5 boxes
HATCH_COL = {r: (2 + 2 * r) % 5 for r in range(5)}
BASE_BOXES = [                           # (br, bc, wraps_rows, wraps_cols)
    (0, 0, False, False),
    (1, 2, False, False),
    (2, 4, False, True),
    (3, 1, False, False),
    (4, 3, True, False),
]


def gcc(gr, gc):
    """Centre of grid cell (row gr from top, col gc from left) of the fixed 7x7."""
    return np.array([GRID_LEFT_X + (gc + 0.5) * CELL,
                     GRID_TOP_Y - (gr + 0.5) * CELL, 0.0])


def rest_center(r, c):
    """A 5x5 cell (r, c) rests in the bottom-right 5x5 block -> grid (r+2, c+2)."""
    return gcc(r + 2, c + 2)


def make_cell(hatched):
    sq = Rectangle(width=CELL, height=CELL, stroke_width=2.5, stroke_color=BLACK,
                   fill_color=WHITE, fill_opacity=1)
    if not hatched:
        return VGroup(sq)
    hatch = VGroup()
    half = CELL / 2
    for off in np.linspace(-0.66, 0.66, HATCH_N):
        sx = max(-half, -half - off)
        ex = min(half, half - off)
        hatch.add(Line([sx, sx + off, 0], [ex, ex + off, 0],
                       stroke_width=1.5, color=BLACK))
    return VGroup(sq, hatch)


def clone_cell(r, c):
    return make_cell(c == HATCH_COL[r])


def _seg(gr, nrows, gc, ncols):
    """Solid white rectangle covering nrows x ncols grid cells from top-left (gr, gc)."""
    center = gcc(gr, gc) + np.array([(ncols - 1) * 0.5 * CELL,
                                     -(nrows - 1) * 0.5 * CELL, 0.0])
    return Rectangle(width=ncols * CELL, height=nrows * CELL, stroke_width=3,
                     stroke_color=BLACK, fill_color=WHITE, fill_opacity=1).move_to(center)


def rest_box(br, bc, rw, cw):
    """A base 5x5 box, split at the 5x5 torus seam (grid rows/cols 2 and 6)."""
    r0 = min(br + 2, (br + 1) % 5 + 2)
    c0 = min(bc + 2, (bc + 1) % 5 + 2)
    g = VGroup()
    if rw:
        g.add(_seg(6, 1, c0, 2)), g.add(_seg(2, 1, c0, 2))
    elif cw:
        g.add(_seg(r0, 2, 6, 1)), g.add(_seg(r0, 2, 2, 1))
    else:
        g.add(_seg(r0, 2, c0, 2))
    g.set_z_index(2)
    return g


# --- expansion combinatorics -------------------------------------------
def _map_rows(k, er):
    if k < er:
        return [k]
    if k == er:
        return [er, er + 1, er + 2]
    return [k + 2]


def _map_cols(k, ec):
    if k < ec:
        return [k]
    if k == ec:
        return [ec, ec + 1, ec + 2]
    return [k + 2]


def _run(mapper, b, e):
    return mapper(b % 5, e) + mapper((b + 1) % 5, e)


def _chunks(run):
    return [run[i:i + 2] for i in range(0, len(run), 2)]


def placements_for(er, ec):
    """Box placements (grid-row pair, grid-col pair) after tripling row er and col ec."""
    out = []
    for (br, bc, rw, cw) in BASE_BOXES:
        rrun = _run(_map_rows, br, er)
        crun = _run(_map_cols, bc, ec)
        for rp in _chunks(rrun):
            for cp in _chunks(crun):
                out.append((rp, cp))
    fill = ([er, er + 1], [ec, ec + 1]) if ec == HATCH_COL[er] else None
    assert len(out) + (1 if fill else 0) == 10, (er, ec, len(out))
    return out, fill


def exp_box(rp, cp):
    """A box on the expanded 7x7 torus, split at the 7x7 seam (grid rows/cols 6 and 0)."""
    row_wrap = rp[1] != rp[0] + 1
    col_wrap = cp[1] != cp[0] + 1
    g = VGroup()
    if row_wrap and not col_wrap:
        g.add(_seg(rp[0], 1, cp[0], 2)), g.add(_seg(0, 1, cp[0], 2))
    elif col_wrap and not row_wrap:
        g.add(_seg(rp[0], 2, cp[0], 1)), g.add(_seg(rp[0], 2, 0, 1))
    elif not row_wrap and not col_wrap:
        g.add(_seg(rp[0], 2, cp[0], 2))
    else:
        g.add(_seg(rp[0], 1, cp[0], 1)), g.add(_seg(0, 1, cp[0], 1))
        g.add(_seg(rp[0], 1, 0, 1)), g.add(_seg(0, 1, 0, 1))
    g.set_z_index(2)
    return g


class ExpandFromEveryCell(Scene):
    def construct(self):
        # ---- fixed 7x7 backdrop -------------------------------------
        backdrop = VGroup()
        for gr in range(8):
            y = GRID_TOP_Y - gr * CELL
            backdrop.add(Line([GRID_LEFT_X, y, 0], [GRID_LEFT_X + 7 * CELL, y, 0],
                              stroke_width=1, color=GREY_B))
        for gc in range(8):
            x = GRID_LEFT_X + gc * CELL
            backdrop.add(Line([x, GRID_TOP_Y, 0], [x, GRID_TOP_Y - 7 * CELL, 0],
                              stroke_width=1, color=GREY_B))
        border = Rectangle(width=7 * CELL, height=7 * CELL, stroke_width=2, color=GREY_B,
                           fill_opacity=0).move_to([GRID_LEFT_X + 3.5 * CELL, GRID_MID_Y, 0])

        # ---- persistent 5x5 packing -------------------------------
        cells5 = {}
        for r in range(5):
            for c in range(5):
                cell = clone_cell(r, c).move_to(rest_center(r, c))
                cell.set_z_index(1)
                cells5[(r, c)] = cell
        base_cells = VGroup(*cells5.values())
        boxes5 = [rest_box(*b) for b in BASE_BOXES]

        title = Text("Expanding the C₅ packing from every cell", font_size=26,
                     color=BLACK).to_edge(UP, buff=0.32)

        cur_label = Text("Cubes", font_size=21, color=BLACK)
        current_num = Integer(5, font_size=54, color=BLACK)
        tot_label = Text("Running total", font_size=21, color=BLACK)
        total_num = Integer(0, font_size=54, color=BLACK)
        counter = VGroup(cur_label, current_num, tot_label, total_num).arrange(DOWN, buff=0.26)
        counter.move_to([GRID_LEFT_X - 3.1, GRID_MID_Y + 0.3, 0])

        self.play(FadeIn(backdrop), FadeIn(border), FadeIn(title), FadeIn(counter),
                  run_time=1.0)
        self.play(FadeIn(base_cells), run_time=0.8)
        self.play(*[FadeIn(b) for b in boxes5], run_time=0.6)
        self.wait(0.4)

        cap_pos = np.array([GRID_LEFT_X + 3.5 * CELL, GRID_TOP_Y + 0.4, 0])
        order = [(r, c) for r in range(5) for c in range(5)]

        for i, (er, ec) in enumerate(order):
            slow = i < 3
            T = 4.0 if slow else 1.0
            use_phase_c = (i == 2)          # first empty cell in row-major order: (0, 2)

            # ---- Phase A: mark the cell we expand from ----
            caption = Text(f"expand from cell ({er}, {ec})", font_size=24,
                           color=BLACK).move_to(cap_pos)
            hl = SurroundingRectangle(cells5[(er, ec)], buff=0.04, color=YELLOW,
                                      stroke_width=5)
            hl.set_z_index(6)
            # the 2x2 cubes are hidden for the whole expansion; only the grid of
            # cells moves and duplicates, so hatched (empty) cells stay visible
            self.play(FadeIn(caption), Create(hl),
                      *[FadeOut(b) for b in boxes5],
                      run_time=1.0 if slow else 0.12)

            # ---- build the ephemeral pieces of this expansion ----
            # selected row duplicated straight up, at rest column positions (a 5x7 grid);
            # the copies left of the selected column slide left later, with the column step.
            row_copies = VGroup()
            left_row_copies = []
            for c in range(5):
                for k in (1, 2):
                    rc = clone_cell(er, c).move_to(
                        rest_center(er, c) + np.array([0, k * CELL, 0]))
                    row_copies.add(rc)
                    if c < ec:
                        left_row_copies.append(rc)
            col_copies = VGroup()
            for r in range(5):
                bdy = 2 * CELL if r < er else 0.0
                for k in (1, 2):
                    col_copies.add(clone_cell(r, ec).move_to(
                        rest_center(r, ec) + np.array([-k * CELL, bdy, 0])))
            corner_copies = VGroup()
            for k in (1, 2):
                for j in (1, 2):
                    corner_copies.add(clone_cell(er, ec).move_to(
                        rest_center(er, ec) + np.array([-k * CELL, j * CELL, 0])))
            for grp in (row_copies, col_copies, corner_copies):
                grp.set_z_index(1)

            placements, fill = placements_for(er, ec)
            box_items = list(placements)
            fill_box = None
            if fill is not None and not use_phase_c:
                box_items.append(fill)
            place_group = VGroup(*[exp_box(rp, cp) for (rp, cp) in box_items])
            if fill is not None and use_phase_c:
                fill_box = exp_box(*fill)

            moved = []
            for (r, c), cell in cells5.items():
                dx = -2 * CELL if c < ec else 0.0
                dy = 2 * CELL if r < er else 0.0
                if dx or dy:
                    moved.append((cell, dx, dy))

            n_B = 9 if use_phase_c else 10
            tot_B = 10 * i + n_B

            # ---- Phase B: grow to 7x7 ----
            if slow:
                # step 1 -> 5x7 grid: slide the rows above the selected row up to
                # their final place, then duplicate the selected row into the gap
                if er > 0:
                    self.play(*[cell.animate.shift([0, dy, 0])
                                for (cell, dx, dy) in moved if dy], run_time=0.7)
                self.play(FadeIn(row_copies), run_time=0.8)
                self.wait(0.25)
                # step 2 -> 7x7 grid: slide the columns left of the selected column
                # out to their final place, then duplicate the selected column
                if ec > 0:
                    self.play(*[cell.animate.shift([dx, 0, 0])
                                for (cell, dx, dy) in moved if dx],
                              *[m.animate.shift([-2 * CELL, 0, 0])
                                for m in left_row_copies], run_time=0.7)
                self.play(FadeIn(col_copies), FadeIn(corner_copies), run_time=0.8)
                self.wait(0.2)
                # step 3: only now, fill in the ten 2x2 cubes
                self.play(FadeIn(place_group),
                          ChangeDecimalToValue(current_num, n_B),
                          ChangeDecimalToValue(total_num, tot_B), run_time=0.9)
            else:
                for m in left_row_copies:
                    m.shift([-2 * CELL, 0, 0])
                self.play(*[cell.animate.shift([dx, dy, 0])
                            for (cell, dx, dy) in moved],
                          FadeIn(row_copies), FadeIn(col_copies), FadeIn(corner_copies),
                          run_time=0.22)
                self.play(FadeIn(place_group), run_time=0.18)
                current_num.set_value(n_B)
                total_num.set_value(tot_B)

            eph = [row_copies, col_copies, corner_copies, place_group, hl, caption]

            # ---- Phase C: explain the 3x3 empty patch (first empty cell only) ----
            if use_phase_c:
                region = Rectangle(width=3 * CELL, height=3 * CELL, color=YELLOW,
                                   stroke_width=6, fill_opacity=0).move_to(
                    (gcc(er, ec) + gcc(er + 2, ec + 2)) / 2)
                region.set_z_index(6)
                cap2 = Text("a 3×3 empty patch holds one 2×2 cube (+ 5 empty cells)",
                            font_size=22, color=BLACK).move_to(
                    [GRID_LEFT_X + 3.5 * CELL, GRID_TOP_Y - 7 * CELL - 0.45, 0])
                self.play(Create(region), FadeIn(cap2), run_time=1.0)
                self.play(FadeIn(fill_box),
                          ChangeDecimalToValue(current_num, 10),
                          ChangeDecimalToValue(total_num, 10 * i + 10), run_time=0.8)
                self.wait(0.5)
                self.play(FadeOut(region), FadeOut(cap2), run_time=0.5)
                eph.append(fill_box)

            self.wait(0.6 if slow else 0.25)

            # ---- reset back to the plain 5x5 ----
            resets = [cell.animate.move_to(rest_center(r, c))
                      for (r, c), cell in cells5.items() if (c < ec or r < er)]
            self.play(*[FadeOut(m) for m in eph], *resets,
                      *[FadeIn(b) for b in boxes5], run_time=0.4 if slow else 0.22)
            current_num.set_value(5)

        self.wait(1.5)
