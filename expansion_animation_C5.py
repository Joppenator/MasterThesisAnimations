from manim import *

config.background_color = WHITE

# --- geometry ---------------------------------------------------------------
CELL = 0.82
SLOW = 1.4
LABEL_GAP = 0.33
# top-left outer corner of the final 7x7 board, centred on the origin
FINAL_TOP_LEFT = LEFT * 3.5 * CELL + UP * 3.5 * CELL


def cell_center(r, c):
    """Centre of grid cell (row r from the top, col c from the left) in the 7x7 lattice."""
    return FINAL_TOP_LEFT + RIGHT * (c + 0.5) * CELL + DOWN * (r + 0.5) * CELL


def grid_cell(r, c, hatched=False):
    center = cell_center(r, c)
    shape = Rectangle(
        width=CELL,
        height=CELL,
        stroke_width=3,
        stroke_color=BLACK,
        fill_color=WHITE,
        fill_opacity=1,
    ).move_to(center)
    if not hatched:
        return VGroup(shape)

    hatches = VGroup()
    half_cell = CELL / 2
    for offset in np.linspace(-0.7, 0.7, 18):
        start_x = max(-half_cell, -half_cell - offset)
        end_x = min(half_cell, half_cell - offset)
        hatches.add(
            Line(
                center + RIGHT * start_x + UP * (start_x + offset),
                center + RIGHT * end_x + UP * (end_x + offset),
                stroke_width=2,
                color=BLACK,
            )
        )
    return VGroup(shape, hatches)


def rect_cells(gr, gc, h, w):
    """Solid white rectangle covering grid rows gr..gr+h-1 and cols gc..gc+w-1."""
    center = cell_center(gr, gc)
    center += RIGHT * (w - 1) * 0.5 * CELL + DOWN * (h - 1) * 0.5 * CELL
    rect = Rectangle(
        width=w * CELL,
        height=h * CELL,
        stroke_width=3,
        stroke_color=BLACK,
        fill_color=WHITE,
        fill_opacity=1,
    ).move_to(center)
    rect.set_z_index(1)  # boxes always sit above the plain grid cells
    return rect


class ExpandC5Packing(Scene):
    def construct(self):
        # ---- start board: the 5x5 packing occupying grid rows/cols 2..6 -----
        start_hatch = {(2, 4), (3, 6), (4, 3), (5, 5), (6, 2)}

        rows = [
            VGroup(
                *[
                    grid_cell(gr, gc, hatched=(gr, gc) in start_hatch)
                    for gc in range(2, 7)
                ]
            )
            for gr in range(2, 7)
        ]
        board_rows = VGroup(*rows)

        # non-wrapping boxes -- identical grid position in the 5x5 and the 7x7
        box_00 = rect_cells(2, 2, 2, 2)  # start (0,0) -> end (2,2)
        box_12 = rect_cells(3, 4, 2, 2)  # start (1,2) -> end (3,4)
        box_31 = rect_cells(5, 3, 2, 2)  # start (3,1) -> end (5,3)

        # box that wraps left/right: start (2,4) -> end (4,6)
        lr_right = rect_cells(4, 6, 2, 1)  # right stub, stays put
        lr_left = rect_cells(4, 2, 2, 1)   # left stub, rides out to col 0
        # box that wraps top/bottom: start (4,3) -> end (6,5)
        tb_bottom = rect_cells(6, 5, 1, 2)  # bottom stub, stays put
        tb_top = rect_cells(2, 5, 1, 2)     # top stub, rides up to row 0

        start_boxes = VGroup(box_00, box_12, box_31, lr_right, lr_left, tb_bottom, tb_top)

        # axis labels 0..4 for the 5x5
        start_col_labels = VGroup(
            *[
                MathTex(str(i), color=BLACK)
                .scale(0.8)
                .move_to(cell_center(2, 2 + i) + UP * (0.5 * CELL + LABEL_GAP))
                for i in range(5)
            ]
        )
        start_row_labels = VGroup(
            *[
                MathTex(str(i), color=BLACK)
                .scale(0.8)
                .move_to(cell_center(2 + i, 2) + LEFT * (0.5 * CELL + LABEL_GAP))
                for i in range(5)
            ]
        )
        start_labels = VGroup(start_col_labels, start_row_labels)

        grid = VGroup(board_rows, start_boxes)
        grid.shift(LEFT * CELL + UP * CELL)  # 5x5 centred on screen
        start_labels.shift(LEFT * CELL + UP * CELL)

        # ---- start straight from the finished 5x5 packing -----------------
        self.add(grid, start_labels)
        self.wait(0.6 * SLOW)

        # ---- fade the axis labels, then slide onto the 7x7 lattice --------
        self.play(FadeOut(start_labels), run_time=0.6 * SLOW)
        self.play(grid.animate.shift(RIGHT * CELL + DOWN * CELL), run_time=1 * SLOW)

        # ---- duplicate the top row twice, upward (grid cells only) -------
        top = rows[0]  # grid row 2
        highlight = SurroundingRectangle(top, buff=0.05, color=YELLOW, stroke_width=7)
        highlight.set_z_index(5)  # highlighter stays in front of every box
        self.play(Create(highlight), run_time=0.7 * SLOW)
        self.play(Indicate(highlight, color=YELLOW, scale_factor=1.08), run_time=0.7 * SLOW)

        new_rows = {}
        for gr in (1, 0):
            new_row = VGroup(
                *[grid_cell(gr, gc, hatched=(gc == 4)) for gc in range(2, 7)]
            )
            self.play(TransformFromCopy(top, new_row), run_time=1 * SLOW)
            new_rows[gr] = new_row
        self.play(FadeOut(highlight), run_time=0.5 * SLOW)

        # ---- duplicate the left column twice, leftward (grid cells only) -
        left_col = VGroup(
            new_rows[0][0], new_rows[1][0], *[rows[i][0] for i in range(5)]
        )  # grid col 2, all seven rows
        highlight = SurroundingRectangle(
            left_col, buff=0.05, color=YELLOW, stroke_width=7
        )
        highlight.set_z_index(5)
        self.play(Create(highlight), run_time=0.7 * SLOW)
        self.play(Indicate(highlight, color=YELLOW, scale_factor=1.08), run_time=0.7 * SLOW)

        for gc in (1, 0):
            new_col = VGroup(
                *[grid_cell(gr, gc, hatched=(gr == 6)) for gr in range(7)]
            )
            self.play(TransformFromCopy(left_col, new_col), run_time=1 * SLOW)
            left_col = new_col
        self.play(FadeOut(highlight), run_time=0.5 * SLOW)

        # ---- only now: fill in the 2x2 boxes of the 7x7 packing ---------
        # the two wrapping boxes' stubs ride out to the new torus edges
        self.bring_to_front(tb_top, lr_left)
        self.play(
            tb_top.animate.shift(UP * 2 * CELL),
            lr_left.animate.shift(LEFT * 2 * CELL),
            run_time=1 * SLOW,
        )

        box_02 = rect_cells(0, 2, 2, 2)
        box_20 = rect_cells(2, 0, 2, 2)
        corner = rect_cells(0, 0, 2, 2)
        box_15 = rect_cells(1, 5, 2, 2)
        box_41 = rect_cells(4, 1, 2, 2)
        self.play(
            LaggedStart(
                Create(box_02),
                Create(box_20),
                Create(corner),
                Create(box_15),
                Create(box_41),
                lag_ratio=0.45,
            ),
            run_time=2.5 * SLOW,
        )
        self.wait(0.4 * SLOW)

        # ---- relabel the axes 0..6 --------------------------------------
        new_col_labels = VGroup(
            *[
                MathTex(str(i), color=BLACK)
                .scale(0.8)
                .move_to(cell_center(0, i) + UP * (0.5 * CELL + LABEL_GAP))
                for i in range(7)
            ]
        )
        new_row_labels = VGroup(
            *[
                MathTex(str(i), color=BLACK)
                .scale(0.8)
                .move_to(cell_center(i, 0) + LEFT * (0.5 * CELL + LABEL_GAP))
                for i in range(7)
            ]
        )
        self.play(
            FadeIn(VGroup(new_col_labels, new_row_labels)),
            run_time=1 * SLOW,
        )
        self.wait(2 * SLOW)
