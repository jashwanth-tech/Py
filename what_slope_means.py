"""
What Does Slope REALLY Mean?
============================
A mathematically rigorous 9:16 vertical explainer (1080x1920) for Manim CE.
"""

from manim import *
import numpy as np

# Configure vertical 9:16 canvas
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0


class WhatSlopeReallyMeans(Scene):
    def construct(self):
        # -----------------------------------------------------------
        # Global Layout Anchors
        # -----------------------------------------------------------
        TOP_HEADER_Y = 7.1
        SUB_HEADER_Y = 6.25
        AXES_CENTER_Y = 1.3
        CARD_CENTER_Y = -4.5

        def replace_subtitle(current_sub, new_text, color=WHITE, font_size=18):
            next_sub = Text(
                new_text,
                font_size=font_size,
                weight=BOLD,
                color=color,
            ).move_to(np.array([0.0, SUB_HEADER_Y, 0.0]))
            self.play(
                FadeOut(current_sub, shift=UP * 0.12),
                FadeIn(next_sub, shift=UP * 0.12),
                run_time=0.55,
            )
            return next_sub

        # Persistent Top Header Pill
        header_pill = RoundedRectangle(
            corner_radius=0.25,
            width=7.6,
            height=0.68,
            fill_color=DARK_GRAY,
            fill_opacity=0.9,
            stroke_color=BLUE_E,
            stroke_width=2.5,
        ).move_to(np.array([0.0, TOP_HEADER_Y, 0.0]))

        header_text = Text(
            "THE INTUITION OF SLOPE",
            font_size=20,
            weight=BOLD,
            color=BLUE_B,
        ).move_to(header_pill.get_center())

        subtitle = Text(
            "What happens when one quantity changes?",
            font_size=18,
            color=WHITE,
        ).move_to(np.array([0.0, SUB_HEADER_Y, 0.0]))

        self.play(FadeIn(header_pill), FadeIn(header_text), Write(subtitle), run_time=1.0)

        # -----------------------------------------------------------
        # Coordinate Plane (Fixed: font_size directly in axis_config)
        # -----------------------------------------------------------
        axes = Axes(
            x_range=[0, 4.5, 1],
            y_range=[0, 6.0, 1],
            x_length=5.6,
            y_length=5.8,
            axis_config={
                "color": GRAY_C,
                "stroke_width": 2.5,
                "include_numbers": True,
                "font_size": 16,
            },
        ).move_to(np.array([0.0, AXES_CENTER_Y, 0.0]))

        x_axis_label = Text("x", font_size=18, weight=BOLD, color=GRAY_B).next_to(
            axes.x_axis, RIGHT, buff=0.15
        )
        y_axis_label = Text("y", font_size=18, weight=BOLD, color=GRAY_B).next_to(
            axes.y_axis, UP, buff=0.15
        )
        axes_group = VGroup(axes, x_axis_label, y_axis_label)

        self.play(Create(axes_group), run_time=1.2)

        # -----------------------------------------------------------
        # SCENE 1: Change in x & Change in y
        # -----------------------------------------------------------
        pt_x = Dot(axes.c2p(1.0, 0.0), radius=0.08, color=TEAL_A)
        pt_y = Dot(axes.c2p(0.0, 1.0), radius=0.08, color=GOLD_A)

        self.play(FadeIn(pt_x), FadeIn(pt_y), run_time=0.5)

        self.play(
            pt_x.animate.move_to(axes.c2p(3.0, 0.0)),
            pt_y.animate.move_to(axes.c2p(0.0, 5.0)),
            run_time=1.4,
            rate_func=smooth,
        )

        line_scene1 = axes.plot(
            lambda x: 2.0 * x - 1.0, x_range=[0.5, 3.5], color=BLUE_B, stroke_width=3.5
        )
        pt_combined = Dot(axes.c2p(1.0, 1.0), radius=0.09, color=YELLOW)

        self.play(
            FadeOut(pt_x),
            FadeOut(pt_y),
            Create(line_scene1),
            FadeIn(pt_combined),
            run_time=0.9,
        )

        q_card = RoundedRectangle(
            corner_radius=0.2,
            width=7.6,
            height=1.25,
            fill_color=DARK_GRAY,
            fill_opacity=0.92,
            stroke_color=BLUE_D,
            stroke_width=2.0,
        ).move_to(np.array([0.0, CARD_CENTER_Y, 0.0]))

        q_t1 = Text("When x changes, y responds by changing.", font_size=16, weight=BOLD, color=WHITE)
        q_t2 = Text("How quickly does y change compared to x?", font_size=15, color=GOLD_A)
        q_group = VGroup(q_t1, q_t2).arrange(DOWN, buff=0.18).move_to(q_card.get_center())

        self.play(FadeIn(q_card), FadeIn(q_group), run_time=0.8)
        self.wait(1.0)

        # -----------------------------------------------------------
        # SCENE 2: The Ratio Δy / Δx (A=(1,1), B=(3,5))
        # -----------------------------------------------------------
        subtitle = replace_subtitle(
            subtitle,
            "COMPARING CHANGES: The Ratio Δy / Δx",
            color=GOLD_A,
            font_size=18,
        )
        self.play(FadeOut(q_card), FadeOut(q_group), run_time=0.4)

        dot_A = Dot(axes.c2p(1.0, 1.0), radius=0.09, color=YELLOW)
        dot_B = Dot(axes.c2p(3.0, 5.0), radius=0.09, color=YELLOW)
        lbl_A = Text("A (1, 1)", font_size=14, color=YELLOW_A).next_to(dot_A, UL, buff=0.1)
        lbl_B = Text("B (3, 5)", font_size=14, color=YELLOW_A).next_to(dot_B, UL, buff=0.1)

        run_line = Line(axes.c2p(1.0, 1.0), axes.c2p(3.0, 1.0), color=TEAL_A, stroke_width=4.0)
        lbl_dx = Text("Δx = 2", font_size=15, weight=BOLD, color=TEAL_A).next_to(run_line, DOWN, buff=0.12)

        rise_line = Line(axes.c2p(3.0, 1.0), axes.c2p(3.0, 5.0), color=GOLD_A, stroke_width=4.0)
        lbl_dy = Text("Δy = 4", font_size=15, weight=BOLD, color=GOLD_A).next_to(rise_line, RIGHT, buff=0.12)

        triangle_group = VGroup(dot_A, dot_B, lbl_A, lbl_B, run_line, lbl_dx, rise_line, lbl_dy)

        self.play(
            FadeOut(pt_combined),
            FadeIn(dot_A),
            FadeIn(lbl_A),
            Create(run_line),
            FadeIn(lbl_dx),
            run_time=1.1,
        )
        self.play(
            Create(rise_line),
            FadeIn(lbl_dy),
            FadeIn(dot_B),
            FadeIn(lbl_B),
            run_time=1.1,
        )

        ratio_card = RoundedRectangle(
            corner_radius=0.2,
            width=7.8,
            height=2.0,
            fill_color=DARK_GRAY,
            fill_opacity=0.92,
            stroke_color=GOLD_B,
            stroke_width=2.0,
        ).move_to(np.array([0.0, CARD_CENTER_Y, 0.0]))

        f1 = Text("Slope = (Change in y) / (Change in x)", font_size=16, weight=BOLD, color=WHITE)
        f2 = Text("m = Δy / Δx = 4 / 2 = 2", font_size=19, weight=BOLD, color=GOLD_A)
        f3 = Text("For every +1 unit in x, y changes by +2 units.", font_size=15, color=TEAL_A)
        f_group = VGroup(f1, f2, f3).arrange(DOWN, buff=0.18).move_to(ratio_card.get_center())

        self.play(FadeIn(ratio_card), FadeIn(f_group), run_time=0.9)
        self.wait(1.0)

        step1_x = Line(axes.c2p(1.0, 1.0), axes.c2p(2.0, 1.0), color=TEAL_C, stroke_width=3.2)
        step1_y = Line(axes.c2p(2.0, 1.0), axes.c2p(2.0, 3.0), color=GOLD_C, stroke_width=3.2)
        step2_x = Line(axes.c2p(2.0, 3.0), axes.c2p(3.0, 3.0), color=TEAL_C, stroke_width=3.2)
        step2_y = Line(axes.c2p(3.0, 3.0), axes.c2p(3.0, 5.0), color=GOLD_C, stroke_width=3.2)
        step_mid_dot = Dot(axes.c2p(2.0, 3.0), radius=0.07, color=YELLOW)

        self.play(Create(step1_x), Create(step1_y), FadeIn(step_mid_dot), run_time=0.8)
        self.play(Create(step2_x), Create(step2_y), run_time=0.8)
        self.wait(0.8)

        # -----------------------------------------------------------
        # SCENE 3: Comparing Rates (Independent Δy bars from baseline)
        # -----------------------------------------------------------
        subtitle = replace_subtitle(
            subtitle,
            "SAME Δx, DIFFERENT SLOPES: Sensitivity",
            color=WHITE,
            font_size=17,
        )

        self.play(
            FadeOut(triangle_group),
            FadeOut(line_scene1),
            FadeOut(ratio_card),
            FadeOut(f_group),
            FadeOut(step1_x),
            FadeOut(step1_y),
            FadeOut(step2_x),
            FadeOut(step2_y),
            FadeOut(step_mid_dot),
            run_time=0.7,
        )

        line_m05 = axes.plot(lambda x: 0.5 * x, x_range=[0.0, 4.2], color=BLUE_B, stroke_width=3.0)
        line_m10 = axes.plot(lambda x: 1.0 * x, x_range=[0.0, 4.2], color=GREEN_B, stroke_width=3.0)
        line_m20 = axes.plot(lambda x: 2.0 * x, x_range=[0.0, 2.7], color=GOLD_A, stroke_width=3.0)

        tag_m05 = Text("m = 0.5", font_size=14, color=BLUE_B).move_to(axes.c2p(4.0, 2.4))
        tag_m10 = Text("m = 1.0", font_size=14, color=GREEN_B).move_to(axes.c2p(3.8, 4.2))
        tag_m20 = Text("m = 2.0", font_size=14, color=GOLD_A).move_to(axes.c2p(2.2, 5.0))

        self.play(
            Create(line_m05), FadeIn(tag_m05),
            Create(line_m10), FadeIn(tag_m10),
            Create(line_m20), FadeIn(tag_m20),
            run_time=1.2,
        )

        dx_base = Line(axes.c2p(0.0, 0.0), axes.c2p(2.0, 0.0), color=TEAL_A, stroke_width=4.5)
        lbl_dx_base = Text("Same Δx = 2", font_size=15, weight=BOLD, color=TEAL_A).next_to(dx_base, DOWN, buff=0.12)
        self.play(Create(dx_base), FadeIn(lbl_dx_base), run_time=0.7)

        dy_m05_full = Line(axes.c2p(1.88, 0.0), axes.c2p(1.88, 1.0), color=BLUE_B, stroke_width=3.8)
        dy_m10_full = Line(axes.c2p(2.00, 0.0), axes.c2p(2.00, 2.0), color=GREEN_B, stroke_width=3.8)
        dy_m20_full = Line(axes.c2p(2.12, 0.0), axes.c2p(2.12, 4.0), color=GOLD_A, stroke_width=3.8)

        lbl_dy05 = Text("Δy = 1", font_size=12, color=BLUE_B).next_to(dy_m05_full, LEFT, buff=0.08)
        lbl_dy10 = Text("Δy = 2", font_size=12, color=GREEN_B).next_to(dy_m10_full.get_top(), LEFT, buff=0.08)
        lbl_dy20 = Text("Δy = 4", font_size=12, color=GOLD_A).next_to(dy_m20_full, RIGHT, buff=0.08)

        self.play(
            Create(dy_m05_full), FadeIn(lbl_dy05),
            Create(dy_m10_full), FadeIn(lbl_dy10),
            Create(dy_m20_full), FadeIn(lbl_dy20),
            run_time=1.2,
        )

        rates_card = RoundedRectangle(
            corner_radius=0.2,
            width=7.8,
            height=2.0,
            fill_color=DARK_GRAY,
            fill_opacity=0.92,
            stroke_color=BLUE_C,
            stroke_width=2.0,
        ).move_to(np.array([0.0, CARD_CENTER_Y, 0.0]))

        r_hdr = Text("Given the exact same input Δx = 2:", font_size=15, color=TEAL_A)
        c_col1 = Text("m = 0.5 → Δy = 1", font_size=14, color=BLUE_B)
        c_col2 = Text("m = 1.0 → Δy = 2", font_size=14, color=GREEN_B)
        c_col3 = Text("m = 2.0 → Δy = 4", font_size=14, color=GOLD_A)
        col_group = VGroup(c_col1, c_col2, c_col3).arrange(RIGHT, buff=0.3)

        r_summary = Text("Larger slope = stronger response in y.", font_size=15, weight=BOLD, color=WHITE)
        rates_group = VGroup(r_hdr, col_group, r_summary).arrange(DOWN, buff=0.18).move_to(rates_card.get_center())

        self.play(FadeIn(rates_card), FadeIn(rates_group), run_time=0.9)
        self.wait(1.5)

        # -----------------------------------------------------------
        # SCENE 4: Negative Slope
        # -----------------------------------------------------------
        subtitle = replace_subtitle(
            subtitle,
            "NEGATIVE SLOPE: Opposite Direction",
            color=RED_A,
            font_size=17,
        )

        self.play(
            FadeOut(line_m05), FadeOut(tag_m05),
            FadeOut(line_m10), FadeOut(tag_m10),
            FadeOut(line_m20), FadeOut(tag_m20),
            FadeOut(dx_base), FadeOut(lbl_dx_base),
            FadeOut(dy_m05_full), FadeOut(lbl_dy05),
            FadeOut(dy_m10_full), FadeOut(lbl_dy10),
            FadeOut(dy_m20_full), FadeOut(lbl_dy20),
            FadeOut(rates_card), FadeOut(rates_group),
            run_time=0.7,
        )

        line_neg = axes.plot(lambda x: 5.5 - 1.0 * x, x_range=[0.5, 4.2], color=RED_C, stroke_width=3.5)
        pt_neg = Dot(axes.c2p(1.0, 4.5), radius=0.08, color=YELLOW)

        dx_neg = Line(axes.c2p(1.0, 4.5), axes.c2p(3.0, 4.5), color=TEAL_A, stroke_width=3.5)
        dy_neg = Line(axes.c2p(3.0, 4.5), axes.c2p(3.0, 2.5), color=RED_A, stroke_width=3.5)

        lbl_dx_neg = Text("Δx = +2", font_size=14, color=TEAL_A).next_to(dx_neg, UP, buff=0.1)
        lbl_dy_neg = Text("Δy = -2", font_size=14, color=RED_A).next_to(dy_neg, RIGHT, buff=0.1)

        neg_card = RoundedRectangle(
            corner_radius=0.18,
            width=7.6,
            height=1.4,
            fill_color=DARK_GRAY,
            fill_opacity=0.9,
            stroke_color=RED_C,
            stroke_width=2.0,
        ).move_to(np.array([0.0, CARD_CENTER_Y, 0.0]))

        neg_t1 = Text("m = Δy / Δx = -2 / +2 = -1.0", font_size=17, weight=BOLD, color=RED_A)
        neg_t2 = Text("Positive slope: y rises  |  Negative slope: y falls", font_size=15, color=WHITE)
        neg_text_group = VGroup(neg_t1, neg_t2).arrange(DOWN, buff=0.16).move_to(neg_card.get_center())

        self.play(Create(line_neg), FadeIn(pt_neg), run_time=0.7)
        self.play(
            Create(dx_neg), FadeIn(lbl_dx_neg),
            Create(dy_neg), FadeIn(lbl_dy_neg),
            pt_neg.animate.move_to(axes.c2p(3.0, 2.5)),
            FadeIn(neg_card), FadeIn(neg_text_group),
            run_time=1.3,
        )
        self.wait(1.0)

        # -----------------------------------------------------------
        # SCENE 5 & 6: Curves & The Derivative (Shrinking Interval)
        # -----------------------------------------------------------
        subtitle = replace_subtitle(
            subtitle,
            "CURVES: The rate changes at every point!",
            color=WHITE,
            font_size=17,
        )

        self.play(
            FadeOut(line_neg), FadeOut(pt_neg),
            FadeOut(dx_neg), FadeOut(lbl_dx_neg),
            FadeOut(dy_neg), FadeOut(lbl_dy_neg),
            FadeOut(neg_card), FadeOut(neg_text_group),
            run_time=0.7,
        )

        curve = axes.plot(lambda x: 0.25 * (x**2), x_range=[0.0, 4.4], color=BLUE_B, stroke_width=3.8)
        curve_label = Text("y = 0.25 x²", font_size=16, color=BLUE_B).move_to(axes.c2p(3.8, 4.4))

        self.play(Create(curve), FadeIn(curve_label), run_time=1.1)

        x0 = 1.5
        y0 = 0.25 * (x0**2)
        p0_dot = Dot(axes.c2p(x0, y0), radius=0.08, color=YELLOW)
        p0_lbl = Text("Point P", font_size=14, color=YELLOW_A).next_to(p0_dot, UL, buff=0.1)

        self.play(FadeIn(p0_dot), FadeIn(p0_lbl), run_time=0.5)

        def make_secant(x_target):
            y_target = 0.25 * (x_target**2)
            slope = (y_target - y0) / (x_target - x0)
            p_tgt = Dot(axes.c2p(x_target, y_target), radius=0.07, color=TEAL_A)
            line = axes.plot(
                lambda x: y0 + slope * (x - x0),
                x_range=[max(0.0, x0 - 0.9), min(4.4, x_target + 0.9)],
                color=GOLD_B,
                stroke_width=2.8,
            )
            dx_l = Line(axes.c2p(x0, y0), axes.c2p(x_target, y0), color=TEAL_A, stroke_width=3.0)
            dy_l = Line(axes.c2p(x_target, y0), axes.c2p(x_target, y_target), color=GOLD_A, stroke_width=3.0)
            return p_tgt, line, dx_l, dy_l

        p1_a, sec_a, dxa, dya = make_secant(3.5)

        sec_card = RoundedRectangle(
            corner_radius=0.18,
            width=7.8,
            height=1.8,
            fill_color=DARK_GRAY,
            fill_opacity=0.92,
            stroke_color=GOLD_B,
            stroke_width=2.0,
        ).move_to(np.array([0.0, CARD_CENTER_Y, 0.0]))

        st1 = Text("Secant Line (Average Rate of Change)", font_size=16, weight=BOLD, color=WHITE)
        st2 = Text("Δx = 2.00  →  Slope = Δy / Δx = 1.25", font_size=16, color=GOLD_A)
        st3 = Text("What is the rate of change at ONE point?", font_size=14, color=TEAL_A)
        sec_text_group = VGroup(st1, st2, st3).arrange(DOWN, buff=0.16).move_to(sec_card.get_center())

        self.play(FadeIn(p1_a), Create(sec_a), Create(dxa), Create(dya), FadeIn(sec_card), FadeIn(sec_text_group), run_time=1.1)
        self.wait(0.8)

        p1_b, sec_b, dxb, dyb = make_secant(2.5)
        st2_b = Text("Δx = 1.00  →  Slope = Δy / Δx = 1.00", font_size=16, color=GOLD_A).move_to(st2.get_center())

        self.play(
            ReplacementTransform(p1_a, p1_b),
            ReplacementTransform(sec_a, sec_b),
            ReplacementTransform(dxa, dxb),
            ReplacementTransform(dya, dyb),
            FadeOut(st2, shift=UP * 0.08),
            FadeIn(st2_b, shift=UP * 0.08),
            run_time=0.9,
        )
        self.wait(0.5)

        p1_c, sec_c, dxc, dyc = make_secant(1.8)
        st2_c = Text("Δx = 0.30  →  Slope = Δy / Δx = 0.83", font_size=16, color=GOLD_A).move_to(st2.get_center())

        self.play(
            ReplacementTransform(p1_b, p1_c),
            ReplacementTransform(sec_b, sec_c),
            ReplacementTransform(dxb, dxc),
            ReplacementTransform(dyb, dyc),
            FadeOut(st2_b, shift=UP * 0.08),
            FadeIn(st2_c, shift=UP * 0.08),
            run_time=0.9,
        )
        self.wait(0.5)

        # -----------------------------------------------------------
        # SCENE 7: The Tangent & Derivative (Clamped to Baseline)
        # -----------------------------------------------------------
        subtitle = replace_subtitle(
            subtitle,
            "THE DERIVATIVE: Instantaneous rate of change",
            color=GREEN_A,
            font_size=17,
        )

        tangent_line = axes.plot(
            lambda x: y0 + 0.75 * (x - x0),
            x_range=[0.75, 3.8],
            color=GREEN_B,
            stroke_width=4.0,
        )

        tangent_card = RoundedRectangle(
            corner_radius=0.2,
            width=7.8,
            height=2.0,
            fill_color=DARK_GRAY,
            fill_opacity=0.94,
            stroke_color=GREEN_C,
            stroke_width=2.2,
        ).move_to(np.array([0.0, CARD_CENTER_Y, 0.0]))

        d1 = Text("As Δx approaches 0: Secant becomes Tangent", font_size=16, weight=BOLD, color=WHITE)
        d2 = Text("lim (Δx → 0)  Δy / Δx  =  dy / dx", font_size=20, weight=BOLD, color=GREEN_A)
        d3 = Text("Instantaneous Rate of Change at point P = 0.75", font_size=15, color=GOLD_A)
        d_group = VGroup(d1, d2, d3).arrange(DOWN, buff=0.18).move_to(tangent_card.get_center())

        self.play(
            FadeOut(p1_c),
            FadeOut(dxc),
            FadeOut(dyc),
            FadeOut(sec_card),
            FadeOut(sec_text_group),
            ReplacementTransform(sec_c, tangent_line),
            FadeIn(tangent_card),
            FadeIn(d_group),
            run_time=1.3,
        )
        self.wait(1.5)

        # -----------------------------------------------------------
        # SCENE 8: Physics Connection (Position vs Time)
        # -----------------------------------------------------------
        subtitle = replace_subtitle(
            subtitle,
            "PHYSICS: Slope of Position vs Time IS Velocity",
            color=GOLD_A,
            font_size=17,
        )

        new_x_axis_label = Text("Time t (s)", font_size=16, weight=BOLD, color=TEAL_A).next_to(
            axes.x_axis, RIGHT, buff=0.15
        )
        new_y_axis_label = Text("Position x (m)", font_size=16, weight=BOLD, color=GOLD_A).next_to(
            axes.y_axis, UP, buff=0.15
        )

        physics_card = RoundedRectangle(
            corner_radius=0.2,
            width=7.8,
            height=2.0,
            fill_color=DARK_GRAY,
            fill_opacity=0.92,
            stroke_color=GOLD_B,
            stroke_width=2.0,
        ).move_to(np.array([0.0, CARD_CENTER_Y, 0.0]))

        ph1 = Text("Slope = Δposition / Δtime", font_size=17, weight=BOLD, color=WHITE)
        ph2 = Text("v(t) = dx / dt   (Velocity!)", font_size=21, weight=BOLD, color=GOLD_A)
        ph3 = Text("Steeper curve = moving faster. Flat = stationary.", font_size=14, color=TEAL_A)
        ph_group = VGroup(ph1, ph2, ph3).arrange(DOWN, buff=0.18).move_to(physics_card.get_center())

        self.play(
            FadeOut(x_axis_label, shift=UP * 0.1),
            FadeIn(new_x_axis_label, shift=UP * 0.1),
            FadeOut(y_axis_label, shift=UP * 0.1),
            FadeIn(new_y_axis_label, shift=UP * 0.1),
            FadeOut(tangent_card),
            FadeOut(d_group),
            FadeIn(physics_card),
            FadeIn(ph_group),
            run_time=1.1,
        )
        self.wait(1.5)

        # -----------------------------------------------------------
        # SCENE 9: Synthesis Chain & Final Realization
        # -----------------------------------------------------------
        self.play(
            FadeOut(axes_group),
            FadeOut(new_x_axis_label),
            FadeOut(new_y_axis_label),
            FadeOut(curve),
            FadeOut(curve_label),
            FadeOut(p0_dot),
            FadeOut(p0_lbl),
            FadeOut(tangent_line),
            FadeOut(physics_card),
            FadeOut(ph_group),
            run_time=0.7,
        )

        subtitle = replace_subtitle(
            subtitle,
            "THE CORE PROGRESSION",
            color=WHITE,
            font_size=19,
        )

        chain_box = RoundedRectangle(
            corner_radius=0.25,
            width=7.4,
            height=5.4,
            fill_color=DARK_GRAY,
            fill_opacity=0.92,
            stroke_color=BLUE_D,
            stroke_width=2.5,
        ).move_to(np.array([0.0, 1.2, 0.0]))

        c1 = Text("1. A quantity changes", font_size=17, color=WHITE)
        arrow1 = Text("↓", font_size=16, color=GRAY_B)
        c2 = Text("2. Compare the changes: Δy / Δx", font_size=17, color=TEAL_A)
        arrow2 = Text("↓", font_size=16, color=GRAY_B)
        c3 = Text("3. Slope = Rate of change", font_size=17, weight=BOLD, color=GOLD_A)
        arrow3 = Text("↓", font_size=16, color=GRAY_B)
        c4 = Text("4. Shrink the interval to zero", font_size=17, color=WHITE)
        arrow4 = Text("↓", font_size=16, color=GRAY_B)
        c5 = Text("5. Derivative = Instantaneous Rate", font_size=17, weight=BOLD, color=GREEN_A)

        chain_items = VGroup(c1, arrow1, c2, arrow2, c3, arrow3, c4, arrow4, c5).arrange(DOWN, buff=0.15)
        chain_items.move_to(chain_box.get_center())

        self.play(FadeIn(chain_box), run_time=0.5)
        for item in chain_items:
            self.play(FadeIn(item, shift=UP * 0.08), run_time=0.25)

        conclusion_card = RoundedRectangle(
            corner_radius=0.22,
            width=7.8,
            height=1.8,
            fill_color=DARK_GRAY,
            fill_opacity=0.95,
            stroke_color=GOLD_A,
            stroke_width=2.5,
        ).move_to(np.array([0.0, CARD_CENTER_Y, 0.0]))

        thesis1 = Text("“Slope is not just a geometry trick.”", font_size=16, slant=ITALIC, color=GRAY_B)
        thesis2 = Text("Slope is the mathematics of change.", font_size=20, weight=BOLD, color=GOLD_A)
        thesis_group = VGroup(thesis1, thesis2).arrange(DOWN, buff=0.22).move_to(conclusion_card.get_center())

        self.play(FadeIn(conclusion_card), FadeIn(thesis_group), run_time=1.0)
        self.wait(2.5)
