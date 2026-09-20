"""
Inside a black hole, your future points toward the singularity.
A scientific visualization of Schwarzschild causal structure using Manim Community.
Format: 9:16 Vertical (1080x1920) | Duration: ~51 seconds
"""

from manim import *
import numpy as np

# ==============================================================================
# 1. CANVAS CONFIGURATION (9:16 VERTICAL, 1080x1920)
# ==============================================================================
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 30
config.background_color = "#040711"

# ==============================================================================
# 2. COLOR PALETTE & DESIGN CONSTANTS
# ==============================================================================
COLOR_BG = "#040711"
COLOR_HORIZON = "#00E5FF"        # Luminous cyan for null horizon
COLOR_SINGULARITY = "#FF3366"    # Crimson for r=0 spacelike curvature singularity
COLOR_CONE = "#38BDF8"           # Light cone sky blue
COLOR_WORLDLINE = "#FCD34D"      # Timelike observer worldline (amber gold)
COLOR_INVALID = "#EF4444"        # Unphysical spacelike path
COLOR_GRID = "#1E293B"           # Subtle background coordinate grid
COLOR_TEXT_MUTED = "#94A3B8"     # Supporting explanations
COLOR_TEXT_BRIGHT = "#F8FAFC"    # Primary labels

X_SINGULARITY = -3.1
X_HORIZON = -0.5
X_OUTER_MAX = 3.6
Y_MIN = -4.2
Y_MAX = 3.6

# ==============================================================================
# 3. HELPER FUNCTIONS FOR CAUSAL DIAGRAM
# ==============================================================================
def r_to_x(r_val, r_s=1.0):
    """Maps physical radial coordinate r (in units of r_s) to diagram X-coordinate."""
    # Maps r = 0 -> X_SINGULARITY (-3.1)
    # Maps r = 1 -> X_HORIZON (-0.5)
    # Maps r = 2.5 -> X_OUTER_MAX (3.4)
    if r_val <= r_s:
        return X_SINGULARITY + (X_HORIZON - X_SINGULARITY) * (r_val / r_s)
    else:
        return X_HORIZON + (X_OUTER_MAX - X_HORIZON) * ((r_val - r_s) / 1.5)

def make_light_cone(center_pos, r_val, r_s=1.0, height=0.85):
    """
    Constructs an exact pedagogical light cone in Painlevé-Gullstrand coordinates:
    dr/dt = -sqrt(r_s / r) +/- c.
    Returns a VGroup containing the shaded interior and null boundary rays.
    """
    r_clamped = max(r_val, 0.12)
    inflow = np.sqrt(r_s / r_clamped)
    
    # Scale factor mapping coordinate slope to visual diagram units
    scale_factor = 0.52
    
    # Left edge: ingoing null ray  dr/dt = - (inflow + 1)
    # Right edge: outgoing null ray dr/dt = - inflow + 1
    dx_right = (1.0 - inflow) * scale_factor * height
    dx_left = -(1.0 + inflow * 0.75) * scale_factor * height
    
    apex = np.array(center_pos)
    p_left = apex + np.array([dx_left, height, 0.0])
    p_right = apex + np.array([dx_right, height, 0.0])
    
    # Future interior polygon
    cone_fill = Polygon(
        apex, p_right, p_left,
        fill_color=COLOR_CONE,
        fill_opacity=0.28,
        stroke_width=0
    )
    ray_l = Line(apex, p_left, color=COLOR_CONE, stroke_width=2.2)
    ray_r = Line(apex, p_right, color=COLOR_CONE, stroke_width=2.2)
    apex_dot = Dot(apex, radius=0.038, color=COLOR_TEXT_BRIGHT)
    
    return VGroup(cone_fill, ray_l, ray_r, apex_dot)

# ==============================================================================
# 4. MAIN SCENE
# ==============================================================================
class BlackHoleCausalStructure(Scene):
    def construct(self):
        # ----------------------------------------------------------------------
        # SCENE 1: HOOK (0.0 - 5.0 s)
        # ----------------------------------------------------------------------
        hook_t1 = Text("Imagine falling into a black hole.", font="sans-serif", font_size=32, color=COLOR_TEXT_BRIGHT)
        hook_t1.move_to(UP * 1.5)
        
        hook_t2 = Text("Here is the strange part:", font="sans-serif", font_size=24, color=COLOR_TEXT_MUTED)
        hook_t2.next_to(hook_t1, DOWN, buff=0.45)
        
        hook_t3 = Text("Your future points toward it.", font="sans-serif", weight=BOLD, font_size=36, color=COLOR_HORIZON)
        hook_t3.next_to(hook_t2, DOWN, buff=0.55)

        self.play(FadeIn(hook_t1, shift=DOWN * 0.3), run_time=1.1)
        self.wait(0.6)
        self.play(FadeIn(hook_t2, shift=DOWN * 0.2), run_time=0.9)
        self.wait(0.5)
        self.play(FadeIn(hook_t3, scale=1.05), run_time=1.2)
        self.wait(1.0)
        self.play(FadeOut(hook_t1), FadeOut(hook_t2), FadeOut(hook_t3), run_time=0.7)

        # ----------------------------------------------------------------------
        # SCENE 2: OUTSIDE THE HORIZON & SPACETIME AXES (5.0 - 13.5 s)
        # ----------------------------------------------------------------------
        title_top = Text("SPACETIME CAUSAL STRUCTURE", font="sans-serif", weight=BOLD, font_size=26, color=COLOR_TEXT_BRIGHT)
        title_top.to_edge(UP, buff=0.85)
        subtitle = Text("Painlevé–Gullstrand Coordinates", font="sans-serif", font_size=18, color=COLOR_TEXT_MUTED)
        subtitle.next_to(title_top, DOWN, buff=0.18)

        # Spacetime Axes
        axis_r = Arrow(start=[X_SINGULARITY - 0.2, Y_MIN, 0], end=[X_OUTER_MAX + 0.5, Y_MIN, 0],
                       buff=0, color=COLOR_TEXT_MUTED, stroke_width=2.0, max_tip_length_to_length_ratio=0.04)
        label_r = Text("Radial Coordinate r", font="sans-serif", font_size=17, color=COLOR_TEXT_MUTED)
        label_r.next_to(axis_r, DOWN, buff=0.22)

        axis_t = Arrow(start=[X_OUTER_MAX + 0.3, Y_MIN, 0], end=[X_OUTER_MAX + 0.3, Y_MAX + 0.4, 0],
                       buff=0, color=COLOR_TEXT_MUTED, stroke_width=2.0, max_tip_length_to_length_ratio=0.04)
        label_t = Text("Time t", font="sans-serif", font_size=17, color=COLOR_TEXT_MUTED)
        label_t.next_to(axis_t, RIGHT, buff=0.18).shift(UP * 0.2)

        # Background reference lines
        grid_lines = VGroup()
        for x_val in np.linspace(X_SINGULARITY + 0.8, X_OUTER_MAX - 0.2, 5):
            grid_lines.add(DashedLine([x_val, Y_MIN, 0], [x_val, Y_MAX, 0],
                                      color=COLOR_GRID, stroke_width=1.0, dash_length=0.15))

        self.play(FadeIn(title_top), FadeIn(subtitle), run_time=0.8)
        self.play(Create(axis_r), FadeIn(label_r), Create(axis_t), FadeIn(label_t), Create(grid_lines), run_time=1.2)

        # Region label: Outside the horizon
        outside_tag = Text("OUTSIDE THE HORIZON (r > r_s)", font="sans-serif", weight=BOLD, font_size=19, color=COLOR_CONE)
        outside_tag.move_to([(X_HORIZON + X_OUTER_MAX) / 2.0, Y_MAX + 0.2, 0])
        self.play(FadeIn(outside_tag), run_time=0.8)

        # Stationary Observer at r = 2.0 r_s
        x_obs_outside = r_to_x(2.0)
        stat_worldline = Line([x_obs_outside, Y_MIN, 0], [x_obs_outside, Y_MAX - 0.5, 0],
                              color=COLOR_WORLDLINE, stroke_width=2.8)
        stat_label = Text("Stationary Observer\n(Requires outward thrust)", font="sans-serif", font_size=14, color=COLOR_WORLDLINE)
        stat_label.next_to(stat_worldline.get_top(), LEFT, buff=0.15)

        # Upright Light Cone at r = 2.0 r_s
        cone_outside = make_light_cone([x_obs_outside, -1.8, 0], r_val=2.0, height=0.95)
        cone_legend = Text("Future Light Cone:\nCan move inward, hold position, or move outward",
                           font="sans-serif", font_size=16, color=COLOR_TEXT_BRIGHT)
        cone_legend.to_edge(DOWN, buff=1.0)

        self.play(Create(stat_worldline), FadeIn(stat_label), run_time=1.4)
        self.play(FadeIn(cone_outside), FadeIn(cone_legend), run_time=1.2)
        self.wait(1.5)

        # Animate timelike paths branching into the cone
        path_inward = Line([x_obs_outside, -1.8, 0], [x_obs_outside - 0.6, -0.85, 0], color=COLOR_WORLDLINE, stroke_width=2.5)
        path_outward = Line([x_obs_outside, -1.8, 0], [x_obs_outside + 0.45, -0.85, 0], color=COLOR_WORLDLINE, stroke_width=2.5)
        self.play(Create(path_inward), Create(path_outward), run_time=1.2)
        self.wait(0.8)

        # ----------------------------------------------------------------------
        # SCENE 3: LIGHT CONES TILT TOWARD HORIZON (13.5 - 22.0 s)
        # ----------------------------------------------------------------------
        self.play(
            FadeOut(cone_legend), FadeOut(path_inward), FadeOut(path_outward),
            FadeOut(stat_worldline), FadeOut(stat_label), FadeOut(cone_outside),
            run_time=0.8
        )

        # Introduce the Event Horizon (r = r_s)
        horizon_line = DashedLine([X_HORIZON, Y_MIN, 0], [X_HORIZON, Y_MAX + 0.3, 0],
                                  color=COLOR_HORIZON, stroke_width=3.2, dash_length=0.18)
        horizon_glow = Line([X_HORIZON, Y_MIN, 0], [X_HORIZON, Y_MAX + 0.3, 0],
                            color=COLOR_HORIZON, stroke_width=7.0, stroke_opacity=0.3)
        horizon_tag = Text("EVENT HORIZON (r = r_s)", font="sans-serif", weight=BOLD, font_size=17, color=COLOR_HORIZON)
        horizon_tag.rotate(90 * DEGREES).next_to(horizon_line, RIGHT, buff=0.12).shift(DOWN * 0.4)
        horizon_sub = Text("Causal boundary (Null hypersurface)", font="sans-serif", font_size=14, color=COLOR_TEXT_MUTED)
        horizon_sub.to_edge(DOWN, buff=1.0)

        self.play(Create(horizon_glow), Create(horizon_line), FadeIn(horizon_tag), FadeIn(horizon_sub), run_time=1.4)

        # Draw light cones tilting progressively
        r_positions = [2.2, 1.4, 1.0]
        y_positions = [-2.4, -0.8, 0.8]
        tilting_cones = VGroup()

        for r_val, y_pos in zip(r_positions, y_positions):
            c_pos = [r_to_x(r_val), y_pos, 0]
            tilting_cones.add(make_light_cone(c_pos, r_val=r_val, height=0.85))

        tilt_explain = Text("As r decreases, inward spacetime flow tilts all future light cones.",
                            font="sans-serif", font_size=16, color=COLOR_TEXT_BRIGHT)
        tilt_explain.to_edge(DOWN, buff=1.0)

        self.play(ReplacementTransform(horizon_sub, tilt_explain), run_time=0.7)
        for cone in tilting_cones:
            self.play(FadeIn(cone), run_time=0.9)

        # Highlight the cone right at the horizon: outgoing ray is vertical (dr/dt = 0)
        horizon_cone_arrow = Arrow(start=[X_HORIZON + 1.2, 1.6, 0], end=[X_HORIZON + 0.05, 1.6, 0],
                                   buff=0.05, color=COLOR_HORIZON, stroke_width=2.4, max_tip_length_to_length_ratio=0.18)
        horizon_cone_text = Text("At horizon:\nOutgoing light ray has dr/dt = 0\n(Trapped at r = r_s)",
                                 font="sans-serif", font_size=14, color=COLOR_HORIZON)
        horizon_cone_text.next_to(horizon_cone_arrow, RIGHT, buff=0.15)

        self.play(Create(horizon_cone_arrow), FadeIn(horizon_cone_text), run_time=1.2)
        self.wait(1.5)

        # ----------------------------------------------------------------------
        # SCENE 4: CROSSING THE HORIZON (22.0 - 30.5 s)
        # ----------------------------------------------------------------------
        self.play(
            FadeOut(tilting_cones), FadeOut(horizon_cone_arrow),
            FadeOut(horizon_cone_text), FadeOut(tilt_explain),
            run_time=0.8
        )

        inside_tag = Text("INSIDE THE HORIZON (r < r_s)", font="sans-serif", weight=BOLD, font_size=18, color=COLOR_SINGULARITY)
        inside_tag.move_to([(X_SINGULARITY + X_HORIZON) / 2.0, Y_MAX + 0.2, 0])
        self.play(FadeIn(inside_tag), run_time=0.7)

        # Smooth infalling observer worldline crossing horizon
        infalling_path = VMobject(color=COLOR_WORLDLINE, stroke_width=3.2)
        infalling_path.set_points_smoothly([
            [r_to_x(2.3), Y_MIN, 0],
            [r_to_x(1.5), -2.2, 0],
            [X_HORIZON, -0.6, 0],
            [r_to_x(0.6), 0.9, 0],
            [X_SINGULARITY, 2.2, 0]
        ])

        crossing_note = Text("Free fall across r = r_s is completely smooth locally.\nNo wall. No infinite tidal forces at the horizon.",
                             font="sans-serif", font_size=15, color=COLOR_TEXT_BRIGHT)
        crossing_note.to_edge(DOWN, buff=0.95)

        self.play(Create(infalling_path), FadeIn(crossing_note), run_time=2.8)
        self.wait(0.8)

        # Light cone inside the horizon (r = 0.55 r_s)
        x_inside = r_to_x(0.55)
        cone_inside = make_light_cone([x_inside, 0.7, 0], r_val=0.55, height=0.90)

        dir_arrow = Arrow(start=[x_inside + 0.5, 0.2, 0], end=[x_inside - 0.7, 0.2, 0],
                          buff=0, color=COLOR_SINGULARITY, stroke_width=2.8)
        dir_label = Text("Future -> Strictly smaller r", font="sans-serif", weight=BOLD, font_size=16, color=COLOR_SINGULARITY)
        dir_label.next_to(dir_arrow, DOWN, buff=0.15)

        self.play(FadeIn(cone_inside), Create(dir_arrow), FadeIn(dir_label), run_time=1.3)
        self.wait(1.5)

        # ----------------------------------------------------------------------
        # SCENE 5: THE KEY REALIZATION (30.5 - 39.5 s)
        # ----------------------------------------------------------------------
        self.play(FadeOut(crossing_note), FadeOut(dir_arrow), FadeOut(dir_label), run_time=0.6)

        # Singularity Boundary at r = 0
        singularity_line = Line([X_SINGULARITY, Y_MIN, 0], [X_SINGULARITY, Y_MAX + 0.3, 0],
                                color=COLOR_SINGULARITY, stroke_width=4.5)
        singularity_tag = Text("r = 0 CURVATURE SINGULARITY", font="sans-serif", weight=BOLD, font_size=15, color=COLOR_SINGULARITY)
        singularity_tag.rotate(90 * DEGREES).next_to(singularity_line, LEFT, buff=0.12).shift(DOWN * 0.2)

        singularity_sub = Text("Spacelike terminal boundary — a moment in time, not a place.",
                               font="sans-serif", font_size=13, color=COLOR_TEXT_MUTED)
        singularity_sub.next_to(singularity_line, LEFT, buff=0.45).rotate(90 * DEGREES).shift(DOWN * 0.2)

        self.play(Create(singularity_line), FadeIn(singularity_tag), FadeIn(singularity_sub), run_time=1.2)

        # Divergent timelike trajectories starting from the same point inside
        p_event = np.array([x_inside, 0.7, 0])
        path_freefall = Line(p_event, [X_SINGULARITY, 2.3, 0], color=COLOR_WORLDLINE, stroke_width=2.4)
        path_thrust_in = Line(p_event, [X_SINGULARITY, 3.1, 0], color="#F59E0B", stroke_width=2.4)
        path_thrust_out = Line(p_event, [X_SINGULARITY, 1.4, 0], color="#FCD34D", stroke_width=2.4)

        paths_group = VGroup(path_freefall, path_thrust_in, path_thrust_out)

        realization_text = Text("Inside, different futures are possible...\nbut EVERY future-directed causal path hits r = 0.",
                                font="sans-serif", font_size=16, color=COLOR_TEXT_BRIGHT)
        realization_text.to_edge(DOWN, buff=0.95)

        self.play(Create(paths_group, lag_ratio=0.2), FadeIn(realization_text), run_time=2.2)
        self.wait(1.5)

        # Highlight unavoidable future
        future_thesis = Text("Smaller r is unavoidable.\nThe singularity is not in front of you — it is in your future.",
                             font="sans-serif", weight=BOLD, font_size=16, color="#FFE066")
        future_thesis.to_edge(DOWN, buff=0.90)

        self.play(ReplacementTransform(realization_text, future_thesis), run_time=0.9)
        self.wait(2.0)

        # ----------------------------------------------------------------------
        # SCENE 6: WHY YOU CANNOT JUST TURN AROUND (39.5 - 46.5 s)
        # ----------------------------------------------------------------------
        self.play(
            FadeOut(future_thesis), FadeOut(paths_group),
            FadeOut(infalling_path), run_time=0.7
        )

        # Attempted escape path toward larger r
        attempt_path = DashedLine(p_event, [p_event[0] + 0.95, p_event[1] + 0.95, 0],
                                  color=COLOR_INVALID, stroke_width=2.8, dash_length=0.12)
        attempt_label = Text("Attempted escape (dr > 0)\nLies outside the future light cone",
                             font="sans-serif", font_size=14, color=COLOR_INVALID)
        attempt_label.next_to(attempt_path.get_end(), RIGHT, buff=0.15)

        invalid_stamp = Text("FORBIDDEN: Requires v > c", font="sans-serif", weight=BOLD, font_size=16, color=COLOR_INVALID)
        invalid_stamp.to_edge(DOWN, buff=1.2)

        escape_explain = Text("Even outward-directed light falls to smaller r.\nFiring your engines only changes WHEN you hit r = 0, not IF.",
                              font="sans-serif", font_size=15, color=COLOR_TEXT_BRIGHT)
        escape_explain.next_to(invalid_stamp, DOWN, buff=0.25)

        self.play(Create(attempt_path), FadeIn(attempt_label), run_time=1.2)
        self.play(FadeIn(invalid_stamp), FadeIn(escape_explain), run_time=1.2)
        self.wait(2.2)

        # ----------------------------------------------------------------------
        # SCENE 7: FINAL SYNTHESIS & CLEAN CARD (46.5 - 52.0 s)
        # ----------------------------------------------------------------------
        self.play(
            FadeOut(attempt_path), FadeOut(attempt_label), FadeOut(invalid_stamp),
            FadeOut(escape_explain), FadeOut(cone_inside), FadeOut(outside_tag),
            FadeOut(inside_tag), FadeOut(grid_lines), FadeOut(axis_r), FadeOut(label_r),
            FadeOut(axis_t), FadeOut(label_t), FadeOut(title_top), FadeOut(subtitle),
            run_time=0.9
        )

        # Leave only the event horizon and singularity lines
        final_box = RoundedRectangle(corner_radius=0.15, width=8.2, height=6.2,
                                     fill_color="#080F24", fill_opacity=0.92,
                                     stroke_color=COLOR_HORIZON, stroke_width=1.5)
        final_box.move_to(ORIGIN)

        line1 = Text("OUTSIDE THE HORIZON:", font="sans-serif", weight=BOLD, font_size=20, color=COLOR_CONE)
        desc1 = Text("The future allows moving inward, holding still, or escaping.", font="sans-serif", font_size=16, color=COLOR_TEXT_BRIGHT)

        line2 = Text("INSIDE THE HORIZON:", font="sans-serif", weight=BOLD, font_size=20, color=COLOR_SINGULARITY)
        desc2 = Text("All future-directed causal paths lead to smaller r.", font="sans-serif", font_size=16, color=COLOR_TEXT_BRIGHT)

        line3 = Text("That is what makes an event horizon an event horizon.",
                     font="sans-serif", weight=BOLD, font_size=18, color="#FFE066")

        footer = Text("Schwarzschild Spacetime — General Relativity", font="sans-serif", font_size=14, color=COLOR_TEXT_MUTED)

        card_content = VGroup(line1, desc1, line2, desc2, line3, footer)
        card_content.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        card_content.move_to(final_box.get_center())
        line3.set_color("#FFE066")
        footer.align_to(card_content, RIGHT)

        self.play(FadeIn(final_box), FadeIn(card_content), run_time=1.6)
        self.wait(3.0)

        # Final fade to black
        self.play(FadeOut(final_box), FadeOut(card_content),
                  FadeOut(horizon_line), FadeOut(horizon_glow), FadeOut(horizon_tag),
                  FadeOut(singularity_line), FadeOut(singularity_tag), FadeOut(singularity_sub),
                  run_time=1.0)
        self.wait(0.5)
