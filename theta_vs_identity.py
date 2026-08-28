"""Manim animation: the gap between p/q and vartheta(p, q) on p/q in [2, 10].

Stages:
  1. axes with p/q on the x-axis (integer labels) and vartheta on the y-axis
     (integer labels);
  2. draw y = x (black) and vartheta(p, q) (red);
  3. highlight the vertical gap at p/q = 2.5 and leave it in place;
  4. transform the picture into a difference plot: the y = x line rotates down
     onto the x-axis while vartheta morphs into the curve p/q - vartheta (red),
     then that difference plot moves up;
  5. mark the differences at 3.4 and 4.4 and compare them with a horizontal
     line from the top of the 4.4 bar across to the 3.4 bar.

Render with:
    uv run manim -pql theta_vs_identity.py ThetaVsIdentity
"""

import math
from functools import lru_cache

from manim import *

config.background_color = WHITE

Q = 200  # grid resolution: p = x * Q
X_MIN, X_MAX = 2, 10
X_HIGHLIGHT = 2.4
X_A = 3.4  # its difference is compared against the one at X_HIGHLIGHT

# smaller axis arrowheads
TIP_CFG = {"tip_width": 0.16, "tip_height": 0.16}


def theta(p, q):
    """Copied verbatim from Niet_presentatie/Gemini_poging2.py.

    Inlined here so this animation does not pull in that module's pandas/numpy
    import chain.
    """
    summ = 0
    for i in range(q):
        multi = 1
        for j in range(1, q):
            c_i = math.cos(2 * math.pi * i / q)
            a_j = math.cos(2 * math.pi / p * math.floor(j * p / q))
            multi = multi * (c_i - a_j) / (1 - a_j)
        summ = summ + multi
    return summ * p / q


@lru_cache(maxsize=None)
def _theta_int(p):
    return theta(p, Q)


def vth(x):
    """vartheta at the ratio x = p / q, linearly interpolated between the two
    bracketing integer values of p so the swept bars move smoothly."""
    t = x * Q
    lo = math.floor(t)
    frac = t - lo
    if frac == 0.0:
        return _theta_int(lo)
    return (1.0 - frac) * _theta_int(lo) + frac * _theta_int(lo + 1)


def gap(x):
    """The difference p/q - vartheta(p, q)."""
    return x - vth(x)


class ThetaVsIdentity(Scene):
    def construct(self):
        # ---------------------------------------------------------------
        # 1. axes
        # ---------------------------------------------------------------
        axes = Axes(
            x_range=[X_MIN, X_MAX, 1],
            y_range=[X_MIN, X_MAX, 1],
            x_length=10.0,
            y_length=6.0,
            tips=True,
            axis_config={
                "color": BLACK,
                "numbers_to_include": list(range(X_MIN, X_MAX + 1)),
                "decimal_number_config": {"num_decimal_places": 0},
                **TIP_CFG,
            },
        )
        axes.set_color(BLACK)
        axes.to_edge(DOWN, buff=0.65)

        x_axis_label = MathTex(r"p/q", color=BLACK).scale(0.9)
        x_axis_label.next_to(axes.x_axis.get_end(), RIGHT, buff=0.2)
        y_axis_label = MathTex(r"\vartheta", color=BLACK).scale(1.0)
        y_axis_label.next_to(axes.y_axis.get_end(), UP, buff=0.2)

        self.play(Create(axes), FadeIn(x_axis_label), FadeIn(y_axis_label))

        # ---------------------------------------------------------------
        # 2. y = x (black) and vartheta (red)
        # ---------------------------------------------------------------
        identity = axes.plot(lambda x: x, x_range=[X_MIN, X_MAX], color=BLACK, stroke_width=4)
        identity_label = MathTex(r"y = x", color=BLACK).scale(0.8)
        identity_label.next_to(axes.c2p(9.3, 9.3), UL, buff=0.1)
        self.play(Create(identity), run_time=2)
        self.play(FadeIn(identity_label))

        vth_graph = axes.plot(
            vth, x_range=[X_MIN, X_MAX, 0.01], color=RED, use_smoothing=False
        )
        vth_label = MathTex(r"\vartheta(p, q)", color=RED).scale(0.8)
        vth_label.next_to(axes.c2p(8.5, vth(8.5)), DR, buff=0.15)
        self.play(Create(vth_graph), run_time=3)
        self.play(FadeIn(vth_label))
        self.wait(0.5)

        # ---------------------------------------------------------------
        # 3. highlight the gap at p/q = 2.4 and leave it
        # ---------------------------------------------------------------
        xh = X_HIGHLIGHT
        highlight = Line(
            axes.c2p(xh, vth(xh)), axes.c2p(xh, xh), color=GREEN_E, stroke_width=6
        )
        highlight_label = MathTex(r"p/q - \vartheta", color=GREEN_E).scale(0.7)
        highlight_label.move_to(axes.c2p(4.4, 3.4))
        highlight_arrow = Arrow(
            highlight_label.get_left(), highlight.get_center(),
            buff=0.15, color=GREEN_E, stroke_width=3, max_tip_length_to_length_ratio=0.1,
        )
        self.play(Create(highlight))
        self.play(GrowArrow(highlight_arrow), FadeIn(highlight_label))
        self.wait(1)

        # ---------------------------------------------------------------
        # 4. transform into the difference plot  p/q - vartheta
        # ---------------------------------------------------------------
        diff_axes = Axes(
            x_range=[X_MIN, X_MAX, 1],
            y_range=[0, 0.38, 0.1],
            x_length=10.0,
            y_length=4.2,
            tips=True,
            axis_config={"color": BLACK, **TIP_CFG},
            x_axis_config={
                "numbers_to_include": list(range(X_MIN, X_MAX + 1)),
                "decimal_number_config": {"num_decimal_places": 0},
            },
            y_axis_config={
                "numbers_to_include": [0.0, 0.1, 0.2, 0.3],
                "decimal_number_config": {"num_decimal_places": 1},
            },
        )
        diff_axes.set_color(BLACK)
        # Align the difference plot's origin with the old plot's (2, 2) corner,
        # so the y = x line appears to rotate straight down onto its x-axis.
        diff_axes.shift(axes.c2p(X_MIN, X_MIN) - diff_axes.c2p(X_MIN, 0))

        flat_identity = Line(
            diff_axes.c2p(X_MIN, 0), diff_axes.c2p(X_MAX, 0), color=BLACK, stroke_width=4
        )
        diff_curve = diff_axes.plot(
            gap, x_range=[X_MIN, X_MAX, 0.01], color=RED, use_smoothing=False
        )
        highlight_target = Line(
            diff_axes.c2p(xh, 0), diff_axes.c2p(xh, gap(xh)), color=GREEN_E, stroke_width=8
        )

        diff_x_label = MathTex(r"p/q", color=BLACK).scale(0.9)
        diff_x_label.next_to(diff_axes.x_axis.get_end(), RIGHT, buff=0.2)
        diff_y_label = MathTex(r"p/q - \vartheta", color=BLACK).scale(0.7)
        diff_y_label.next_to(diff_axes.y_axis.get_end(), UP, buff=0.2)

        self.play(
            FadeOut(axes),
            FadeOut(x_axis_label),
            FadeOut(y_axis_label),
            FadeOut(identity_label),
            FadeOut(vth_label),
            FadeOut(highlight_label),
            FadeOut(highlight_arrow),
            Transform(identity, flat_identity),
            Transform(vth_graph, diff_curve),
            Transform(highlight, highlight_target),
            run_time=2.5,
        )
        self.play(FadeIn(diff_axes), FadeIn(diff_x_label), FadeIn(diff_y_label))
        self.wait(0.5)

        # ---------------------------------------------------------------
        # 5. compare the difference at 3.4 with the one at 2.4
        # ---------------------------------------------------------------
        bar_a = Line(
            diff_axes.c2p(X_A, 0), diff_axes.c2p(X_A, gap(X_A)), color=GREEN_E, stroke_width=8
        )
        tick_a = MathTex("3.4", color=BLACK).scale(0.5).next_to(diff_axes.c2p(X_A, 0), DOWN, buff=0.15)
        tick_h = MathTex("2.4", color=BLACK).scale(0.5).next_to(
            diff_axes.c2p(X_HIGHLIGHT, 0), DOWN, buff=0.15
        )
        self.play(Create(bar_a), FadeIn(tick_a), FadeIn(tick_h))

        top_a = diff_axes.c2p(X_A, gap(X_A))              # 3.4 bar (shorter, right)
        top_h = diff_axes.c2p(X_HIGHLIGHT, gap(X_HIGHLIGHT))  # 2.4 bar (taller, left)
        level = np.array([top_h[0], top_a[1], 0.0])       # point on the 2.4 bar at 3.4's height
        compare_line = DashedLine(top_a, level, color=BLACK, stroke_width=2)
        stub = Line(level, top_h, color=ORANGE, stroke_width=8)
        delta_label = MathTex(
            rf"\Delta = {gap(X_HIGHLIGHT) - gap(X_A):.3f}", color=BLACK
        ).scale(0.65)
        delta_label.move_to(diff_axes.c2p(5.0, 0.33))
        delta_arrow = Arrow(
            delta_label.get_left(), stub.get_center(),
            buff=0.1, color=ORANGE, stroke_width=3, max_tip_length_to_length_ratio=0.08,
        )

        self.play(Create(compare_line))
        self.play(Create(stub), GrowArrow(delta_arrow), FadeIn(delta_label))
        self.wait(2)

        # ---------------------------------------------------------------
        # 6. the whole "n + s" family of differences is a descending staircase
        # ---------------------------------------------------------------
        # Drop the single-pair annotation; keep the green bars (2.4 and 3.4)
        # and grow the family to every interval [n, n + 1].
        self.play(
            FadeOut(compare_line),
            FadeOut(stub),
            FadeOut(delta_arrow),
            FadeOut(delta_label),
        )

        NS = list(range(X_MIN, X_MAX))  # intervals [2,3], [3,4], ... , [9,10]
        S0 = 0.4
        S_MIN, S_MAX = 0.08, 0.92
        frac = ValueTracker(S0)

        def x_of(n):
            s = min(max(frac.get_value(), S_MIN), S_MAX)
            return n + s

        # the bars that do not exist yet (n = 2 is highlight, n = 3 is bar_a)
        extra_bars = VGroup()
        extra_ticks = VGroup()
        for n in NS:
            if n in (2, 3):
                continue
            x = n + S0
            extra_bars.add(
                Line(
                    diff_axes.c2p(x, 0),
                    diff_axes.c2p(x, gap(x)),
                    color=GREEN_E,
                    stroke_width=8,
                )
            )
            extra_ticks.add(
                MathTex(f"{n}.4", color=BLACK)
                .scale(0.5)
                .next_to(diff_axes.c2p(x, 0), DOWN, buff=0.15)
            )
        self.play(
            LaggedStart(*[Create(b) for b in extra_bars], lag_ratio=0.15),
            LaggedStart(*[FadeIn(t) for t in extra_ticks], lag_ratio=0.15),
            run_time=2,
        )

        # dashed staircase: a horizontal tread at each bar's height reaching the
        # next bar, so the drop to the next (shorter) bar is a visible step.
        static_steps = VGroup()
        for n in NS[:-1]:
            xl, xr = n + S0, n + 1 + S0
            static_steps.add(
                DashedLine(
                    diff_axes.c2p(xl, gap(xl)),
                    diff_axes.c2p(xr, gap(xl)),
                    color=BLACK,
                    stroke_width=2,
                    dash_length=0.08,
                )
            )
        self.play(
            LaggedStart(*[Create(s) for s in static_steps], lag_ratio=0.2),
            run_time=2,
        )
        self.wait(1)

        # ---------------------------------------------------------------
        # 7. sweep the shared offset s across (0, 1): the ordering never breaks
        # ---------------------------------------------------------------
        def make_bar(n):
            x = x_of(n)
            return Line(
                diff_axes.c2p(x, 0),
                diff_axes.c2p(x, gap(x)),
                color=GREEN_E,
                stroke_width=8,
            )

        def make_step(n):
            xl, xr = x_of(n), x_of(n + 1)
            return DashedLine(
                diff_axes.c2p(xl, gap(xl)),
                diff_axes.c2p(xr, gap(xl)),
                color=BLACK,
                stroke_width=2,
                dash_length=0.08,
            )

        dyn_bars = VGroup(*[always_redraw(lambda n=n: make_bar(n)) for n in NS])
        dyn_steps = VGroup(*[always_redraw(lambda n=n: make_step(n)) for n in NS[:-1]])

        # swap the static pieces for the frac-driven ones (identical at s = 0.4)
        self.remove(bar_a, highlight, *extra_bars, *static_steps)
        self.add(dyn_bars, dyn_steps)
        self.play(FadeOut(tick_a), FadeOut(tick_h), FadeOut(extra_ticks))

        self.play(frac.animate.set_value(0.90), run_time=2.5)
        self.play(frac.animate.set_value(0.12), run_time=3)
        self.play(frac.animate.set_value(0.50), run_time=2.5)
        self.wait(2)
