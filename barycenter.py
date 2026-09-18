"""
The Sun Isn't Where You Think It Is: The Physics of Barycenters
Target: Manim Community Edition (9:16 Vertical Video, 1080x1920, 60 FPS)
Physics: Two-body center-of-mass mechanics (Sun-Earth vs. Sun-Jupiter systems).
"""

from manim import *
import numpy as np

# -------------------------------------------------------------------------
# 1. Configuration & Canvas Setup (9:16 Vertical Format)
# -------------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = "#030712"


# -------------------------------------------------------------------------
# 2. Physical Constants & Dynamic Mass/Radius Relationships
# -------------------------------------------------------------------------
M_SUN = 1.0
M_EARTH = 3.003e-6          # M_earth / M_sun (~1 / 333,000)
M_JUPITER = 0.0009543        # M_jupiter / M_sun (~1 / 1047)

# Distance of Sun's center to barycenter in units of Solar Radii (R_sun):
# r_bary_Earth / R_sun ≈ 0.00064 (deep inside core, ~450 km from center)
# r_bary_Jupiter / R_sun ≈ 1.068 ≈ 1.07 (7% outside the photosphere)
R_BARY_EARTH_RATIO = 0.00064
R_BARY_JUPITER_RATIO = 1.07

# Dynamic ratios derived directly from constants
MASS_RATIO_SUN_EARTH = int(round(M_SUN / M_EARTH))        # 333,000
MASS_RATIO_JUP_EARTH = int(round(M_JUPITER / M_EARTH))    # 318
INV_JUP_MASS_RATIO = int(round(M_SUN / M_JUPITER))        # 1047


# -------------------------------------------------------------------------
# 3. Celestial Body Constructors
# -------------------------------------------------------------------------
def create_sun(radius=0.6, center=ORIGIN):
    """Builds an incandescent Sun with radial corona glow."""
    sun = VGroup()
    # Corona layers
    glow_radii = np.linspace(radius * 1.9, radius * 1.05, 7)
    glow_alphas = np.linspace(0.03, 0.25, 7)
    for r, a in zip(glow_radii, glow_alphas):
        sun.add(
            Circle(
                radius=r,
                fill_color="#FF7A00",
                fill_opacity=a,
                stroke_width=0,
            ).move_to(center)
        )
    # Bright photosphere
    photosphere = Circle(
        radius=radius,
        fill_color="#FFCA3A",
        fill_opacity=1.0,
        stroke_color="#FFEAA7",
        stroke_width=2.0,
    ).move_to(center)
    # Core illumination
    core = Circle(
        radius=radius * 0.65,
        fill_color="#FFFFFF",
        fill_opacity=0.88,
        stroke_width=0,
    ).move_to(center)

    sun.add(photosphere, core)
    return sun


def create_earth(radius=0.16):
    """Builds Earth with stylized continents and atmosphere."""
    earth = VGroup()
    ocean = Circle(radius=radius, fill_color="#1E6091", fill_opacity=1.0, stroke_width=0)
    c1 = Polygon(
        [-0.05, 0.06, 0], [0.02, 0.10, 0], [0.08, 0.04, 0],
        [0.05, -0.02, 0], [-0.03, -0.02, 0],
        fill_color="#40916C", fill_opacity=0.95, stroke_width=0,
    )
    c2 = Polygon(
        [-0.10, -0.02, 0], [-0.04, 0.03, 0], [-0.02, -0.07, 0],
        [-0.07, -0.11, 0],
        fill_color="#52B788", fill_opacity=0.95, stroke_width=0,
    )
    atmosphere = Circle(
        radius=radius * 1.15,
        stroke_color="#72EFDD",
        stroke_width=1.8,
        stroke_opacity=0.6,
        fill_opacity=0,
    )
    earth.add(ocean, c1, c2, atmosphere)
    return earth


def create_jupiter(radius=0.36):
    """Builds Jupiter with planetary atmospheric cloud bands."""
    jupiter = VGroup()
    base = Circle(radius=radius, fill_color="#D4A373", fill_opacity=1.0, stroke_width=0)
    bands = VGroup()
    band_specs = [
        (0.20, 0.06, "#BC6C25"),
        (0.08, 0.05, "#8C4A16"),
        (-0.04, 0.07, "#BC6C25"),
        (-0.16, 0.05, "#A0522D"),
    ]
    for y_rel, h, col in band_specs:
        y_pos = y_rel * (radius / 0.36)
        band_h = h * (radius / 0.36)
        half_w = np.sqrt(max(0.01, radius**2 - y_pos**2)) * 0.96
        bands.add(
            RoundedRectangle(
                corner_radius=0.03,
                height=band_h,
                width=half_w * 2,
                fill_color=col,
                fill_opacity=0.75,
                stroke_width=0,
            ).move_to([0, y_pos, 0])
        )
    # Great Red Spot
    grs = Ellipse(
        width=radius * 0.36,
        height=radius * 0.22,
        fill_color="#9B2226",
        fill_opacity=0.85,
        stroke_width=0,
    ).move_to([radius * 0.32, -radius * 0.26, 0])

    rim = Circle(
        radius=radius,
        stroke_color="#FAEDCD",
        stroke_width=1.2,
        stroke_opacity=0.4,
        fill_opacity=0,
    )
    jupiter.add(base, bands, grs, rim)
    return jupiter


def create_barycenter_marker(color="#00F5D4"):
    """Builds a technical crosshair representing the Center of Mass."""
    marker = VGroup()
    outer_ring = DashedVMobject(
        Circle(radius=0.18, stroke_color=color, stroke_width=1.8),
        num_dashes=14,
    )
    ch_h = Line([-0.24, 0, 0], [0.24, 0, 0], stroke_color=color, stroke_width=1.8)
    ch_v = Line([0, -0.24, 0], [0, 0.24, 0], stroke_color=color, stroke_width=1.8)
    center_dot = Dot(radius=0.045, color=color)
    marker.add(outer_ring, ch_h, ch_v, center_dot)
    return marker


# -------------------------------------------------------------------------
# 4. Master Animation Scene
# -------------------------------------------------------------------------
class SunBarycenterReel(Scene):
    def construct(self):
        SYS_CENTER = np.array([0.0, -0.6, 0.0])
        TOP_TEXT_Y = 5.6
        MID_TEXT_Y = 4.7

        # Background starfield
        starfield = VGroup()
        np.random.seed(137)
        for _ in range(95):
            sx = np.random.uniform(-4.3, 4.3)
            sy = np.random.uniform(-7.8, 7.8)
            starfield.add(
                Dot(
                    point=[sx, sy, 0],
                    radius=np.random.uniform(0.012, 0.028),
                    color=WHITE,
                ).set_opacity(np.random.uniform(0.15, 0.65))
            )
        self.add(starfield)

        # =================================================================
        # SCENE 1 — THE HOOK (0.0s - 7.0s)
        # =================================================================
        sun_radius = 0.58
        sun = create_sun(radius=sun_radius, center=SYS_CENTER)
        earth = create_earth(radius=0.16)

        r_orbit_earth = 2.9
        theta_earth = ValueTracker(0.0)

        def earth_orbit_updater(mob):
            t = theta_earth.get_value()
            pos = SYS_CENTER + np.array([r_orbit_earth * np.cos(t), r_orbit_earth * np.sin(t), 0.0])
            mob.move_to(pos)
            mob[1:3].rotate(0.02, about_point=pos)

        earth.add_updater(earth_orbit_updater)

        earth_trail = DashedVMobject(
            Circle(radius=r_orbit_earth, stroke_color="#457B9D", stroke_width=1.2).move_to(SYS_CENTER),
            num_dashes=44,
        ).set_opacity(0.4)

        hook_line1 = Text(
            "You think Earth\norbits the Sun.",
            font_size=38,
            font="sans-serif",
            weight=BOLD,
            color="#FFFFFF",
            line_spacing=1.2,
        ).move_to([0, TOP_TEXT_Y, 0])

        self.add(earth_trail, sun, earth)
        self.play(FadeIn(hook_line1, shift=UP * 0.3), run_time=1.0)
        self.play(theta_earth.animate.increment_value(1.8), run_time=2.2, rate_func=linear)

        hook_line2 = Text(
            "Look closer.",
            font_size=42,
            font="sans-serif",
            weight=BOLD,
            color="#FF5964",
        ).move_to([0, TOP_TEXT_Y, 0])

        self.play(ReplacementTransform(hook_line1, hook_line2), run_time=0.6)
        self.play(theta_earth.animate.increment_value(1.5), run_time=1.8, rate_func=linear)

        hook_line3 = Text(
            "The Sun is not motionless.",
            font_size=32,
            font="sans-serif",
            color="#A8DADC",
        ).move_to([0, TOP_TEXT_Y, 0])

        self.play(ReplacementTransform(hook_line2, hook_line3), run_time=0.6)
        self.play(theta_earth.animate.increment_value(0.8), run_time=1.0, rate_func=linear)

        # =================================================================
        # SCENE 2 — REVEAL THE BARYCENTER (7.0s - 14.0s)
        # =================================================================
        earth.clear_updaters()

        bary_marker = create_barycenter_marker(color="#00F5D4").move_to(SYS_CENTER)
        bary_label = Text(
            "CENTER OF MASS\n(BARYCENTER)",
            font_size=21,
            font="sans-serif",
            weight=BOLD,
            color="#00F5D4",
            line_spacing=1.2,
        ).next_to(bary_marker, UP, buff=0.25)

        explain_text = Text(
            "Every gravitational system orbits\na single shared balance point.",
            font_size=26,
            font="sans-serif",
            color="#FFFFFF",
            line_spacing=1.3,
        ).move_to([0, TOP_TEXT_Y, 0])

        connecting_rod = always_redraw(
            lambda: Line(
                sun.get_center(),
                earth.get_center(),
                stroke_color="#457B9D",
                stroke_width=1.2,
                stroke_opacity=0.5,
            )
        )

        self.play(
            ReplacementTransform(hook_line3, explain_text),
            FadeIn(bary_marker),
            FadeIn(bary_label),
            FadeIn(connecting_rod),
            run_time=1.2,
        )

        sim_angle = ValueTracker(theta_earth.get_value())

        def earth_bary_updater(mob):
            a = sim_angle.get_value()
            pos = SYS_CENTER + np.array([r_orbit_earth * np.cos(a), r_orbit_earth * np.sin(a), 0.0])
            mob.move_to(pos)

        earth.add_updater(earth_bary_updater)

        sub_note = Text(
            f"For Sun + Earth: the barycenter lies\n{R_BARY_EARTH_RATIO * 100:.3f}% of R_sun from the center (inside the core).",
            font_size=23,
            font="sans-serif",
            color="#FFE66D",
            line_spacing=1.2,
        ).move_to([0, -4.8, 0])

        self.play(FadeIn(sub_note, shift=UP * 0.2), run_time=0.8)
        self.play(sim_angle.animate.increment_value(2.8), run_time=3.5, rate_func=linear)

        # =================================================================
        # SCENE 3 — THE PHYSICS OF BALANCE (14.0s - 22.0s)
        # =================================================================
        math_card = RoundedRectangle(
            corner_radius=0.18,
            height=3.2,
            width=7.6,
            fill_color="#0D1B2A",
            fill_opacity=0.92,
            stroke_color="#415A77",
            stroke_width=1.4,
        ).move_to([0, TOP_TEXT_Y - 0.5, 0])

        eq_bary = MathTex(r"m_1 r_1 = m_2 r_2", font_size=42, color="#00F5D4")
        eq_note1 = Text("Mass × Distance from Barycenter is equal", font_size=20, color="#E0E1DD")
        eq_note2 = Text(
            f"Sun is {MASS_RATIO_SUN_EARTH:,}× more massive than Earth.\nSo the Sun barely moves at all.",
            font_size=21,
            font="sans-serif",
            color="#A8DADC",
            line_spacing=1.2,
        )

        card_group = VGroup(eq_bary, eq_note1, eq_note2).arrange(DOWN, buff=0.24).move_to(math_card.get_center())

        self.play(
            FadeOut(explain_text),
            FadeOut(bary_label),
            FadeIn(math_card),
            FadeIn(card_group),
            run_time=1.0,
        )
        self.play(sim_angle.animate.increment_value(3.2), run_time=4.0, rate_func=linear)
        self.play(
            FadeOut(math_card),
            FadeOut(card_group),
            FadeOut(sub_note),
            run_time=0.8,
        )

        # =================================================================
        # SCENE 4 — TRANSITION TO SUN–JUPITER (22.0s - 31.0s)
        # =================================================================
        earth.clear_updaters()
        connecting_rod.clear_updaters()

        jupiter = create_jupiter(radius=0.38)
        r_orbit_jup = 3.3

        jup_title = Text(
            "Now enter JUPITER.",
            font_size=36,
            font="sans-serif",
            weight=BOLD,
            color="#F4A261",
        ).move_to([0, TOP_TEXT_Y + 0.2, 0])

        jup_stat = Text(
            f"{MASS_RATIO_JUP_EARTH}× Earth's mass\n(1/{INV_JUP_MASS_RATIO}th the mass of the Sun)",
            font_size=24,
            font="sans-serif",
            color="#E0E1DD",
            line_spacing=1.2,
        ).move_to([0, MID_TEXT_Y, 0])

        jup_start_pos = SYS_CENTER + np.array([
            r_orbit_jup * np.cos(sim_angle.get_value()),
            r_orbit_jup * np.sin(sim_angle.get_value()),
            0.0
        ])
        jupiter.move_to(jup_start_pos)

        # Fade out connecting_rod at the transition to avoid hanging stale lines
        self.play(
            ReplacementTransform(earth, jupiter),
            FadeOut(connecting_rod),
            ReplacementTransform(earth_trail, DashedVMobject(
                Circle(radius=r_orbit_jup, stroke_color="#F4A261", stroke_width=1.2).move_to(SYS_CENTER),
                num_dashes=46,
            ).set_opacity(0.4)),
            FadeIn(jup_title, shift=UP * 0.2),
            FadeIn(jup_stat, shift=UP * 0.2),
            run_time=1.2,
        )

        sun_orbit_r = sun_radius * R_BARY_JUPITER_RATIO

        shift_text = Text(
            "Watch the barycenter drift outward...",
            font_size=24,
            font="sans-serif",
            color="#FFE66D",
        ).move_to([0, -4.8, 0])

        self.play(FadeIn(shift_text), run_time=0.6)

        # Compute targets from current phase to prevent snapping
        a0 = sim_angle.get_value()
        bary_offset = np.array([sun_orbit_r, 0.0, 0.0])
        new_bary_pos = SYS_CENTER + bary_offset
        jup_target = new_bary_pos + np.array([r_orbit_jup * np.cos(a0), r_orbit_jup * np.sin(a0), 0.0])
        sun_target = new_bary_pos + np.array([sun_orbit_r * np.cos(a0 + PI), sun_orbit_r * np.sin(a0 + PI), 0.0])

        self.play(
            bary_marker.animate.move_to(new_bary_pos),
            jupiter.animate.move_to(jup_target),
            sun.animate.move_to(sun_target),
            run_time=1.8,
            rate_func=smooth,
        )

        # Attach updaters only after smooth repositioning completes
        def jupiter_updater(mob):
            a = sim_angle.get_value()
            mob.move_to(new_bary_pos + np.array([r_orbit_jup * np.cos(a), r_orbit_jup * np.sin(a), 0.0]))

        def sun_wobble_updater(mob):
            a = sim_angle.get_value()
            mob.move_to(new_bary_pos + np.array([sun_orbit_r * np.cos(a + PI), sun_orbit_r * np.sin(a + PI), 0.0]))

        jupiter.add_updater(jupiter_updater)
        sun.add_updater(sun_wobble_updater)

        self.play(sim_angle.animate.increment_value(2.8), run_time=3.2, rate_func=linear)

        # =================================================================
        # SCENE 5 — THE SURPRISING REVEAL: OUTSIDE THE SUN (31.0s - 40.0s)
        # =================================================================
        jupiter.clear_updaters()
        sun.clear_updaters()

        self.play(
            FadeOut(jup_title),
            FadeOut(jup_stat),
            FadeOut(shift_text),
            FadeOut(jupiter),
            run_time=0.8,
        )

        ZOOM_CENTER = np.array([-0.6, -0.8, 0.0])
        zoom_sun_radius = 2.05
        zoom_sun = create_sun(radius=zoom_sun_radius, center=ZOOM_CENTER)

        zoom_bary_dist = zoom_sun_radius * R_BARY_JUPITER_RATIO
        zoom_bary_pos = ZOOM_CENTER + np.array([zoom_bary_dist, 0.0, 0.0])

        zoom_bary_marker = create_barycenter_marker(color="#00F5D4").scale(1.2).move_to(zoom_bary_pos)

        surface_dash = Arc(
            radius=zoom_sun_radius,
            start_angle=-PI / 3,
            angle=2 * PI / 3,
            arc_center=ZOOM_CENTER,
            stroke_color="#FFFFFF",
            stroke_width=2.5,
        )

        surface_label = Text(
            "Sun's Visible Surface\n(Photosphere)",
            font_size=20,
            font="sans-serif",
            color="#FFFFFF",
            line_spacing=1.2,
        ).next_to(surface_dash.point_from_proportion(0.78), UR, buff=0.15)

        dist_bracket = DoubleArrow(
            start=ZOOM_CENTER,
            end=zoom_bary_pos,
            color="#FFD166",
            buff=0,
            tip_length=0.18,
            stroke_width=2.5,
        )
        dist_tag = Text(
            f"{R_BARY_JUPITER_RATIO:.2f} Solar Radii",
            font_size=22,
            font="sans-serif",
            weight=BOLD,
            color="#FFD166",
        ).next_to(dist_bracket, UP, buff=0.12)

        reveal_title = Text(
            "THE SURPRISE",
            font_size=36,
            font="sans-serif",
            weight=BOLD,
            color="#FF5964",
        ).move_to([0, TOP_TEXT_Y + 0.3, 0])

        reveal_sub = Text(
            "The Sun–Jupiter barycenter lies\nOUTSIDE the surface of the Sun.",
            font_size=28,
            font="sans-serif",
            weight=BOLD,
            color="#00F5D4",
            line_spacing=1.3,
        ).move_to([0, TOP_TEXT_Y - 0.7, 0])

        self.play(
            FadeOut(sun),
            FadeOut(bary_marker),
            FadeIn(zoom_sun),
            FadeIn(surface_dash),
            FadeIn(surface_label),
            FadeIn(zoom_bary_marker),
            FadeIn(dist_bracket),
            FadeIn(dist_tag),
            FadeIn(reveal_title, shift=UP * 0.2),
            FadeIn(reveal_sub, shift=UP * 0.2),
            run_time=1.5,
        )

        bary_callout = Text(
            "Empty space!\nThe Sun orbits THIS point.",
            font_size=23,
            font="sans-serif",
            weight=BOLD,
            color="#FFE66D",
            line_spacing=1.2,
        ).next_to(zoom_bary_marker, RIGHT, buff=0.25)

        self.play(FadeIn(bary_callout, shift=RIGHT * 0.2), run_time=1.0)
        self.wait(2.2)

        self.play(
            FadeOut(zoom_sun),
            FadeOut(surface_dash),
            FadeOut(surface_label),
            FadeOut(zoom_bary_marker),
            FadeOut(dist_bracket),
            FadeOut(dist_tag),
            FadeOut(reveal_title),
            FadeOut(reveal_sub),
            FadeOut(bary_callout),
            run_time=1.0,
        )

        # =================================================================
        # SCENE 6 — FINAL CINEMATIC PAYOFF (40.0s - 48.0s)
        # =================================================================
        FINAL_BARY = np.array([0.0, -1.2, 0.0])
        final_bary_marker = create_barycenter_marker(color="#00F5D4").move_to(FINAL_BARY)

        final_sun_radius = 0.48
        final_sun_orbit_r = final_sun_radius * R_BARY_JUPITER_RATIO
        final_jup_orbit_r = 3.1

        sun_final = create_sun(
            radius=final_sun_radius,
            center=FINAL_BARY + np.array([-final_sun_orbit_r, 0, 0])
        )
        jup_final = create_jupiter(radius=0.28).move_to(
            FINAL_BARY + np.array([final_jup_orbit_r, 0, 0])
        )

        sun_orbit_circle = DashedVMobject(
            Circle(radius=final_sun_orbit_r, stroke_color="#FFCA3A", stroke_width=1.5).move_to(FINAL_BARY),
            num_dashes=24,
        ).set_opacity(0.5)

        jup_orbit_circle = DashedVMobject(
            Circle(radius=final_jup_orbit_r, stroke_color="#F4A261", stroke_width=1.5).move_to(FINAL_BARY),
            num_dashes=48,
        ).set_opacity(0.4)

        final_clock = ValueTracker(0.0)

        def sun_final_updater(mob):
            phi = final_clock.get_value()
            pos = FINAL_BARY + np.array([
                final_sun_orbit_r * np.cos(phi + PI),
                final_sun_orbit_r * np.sin(phi + PI),
                0.0
            ])
            mob.move_to(pos)

        def jup_final_updater(mob):
            phi = final_clock.get_value()
            pos = FINAL_BARY + np.array([
                final_jup_orbit_r * np.cos(phi),
                final_jup_orbit_r * np.sin(phi),
                0.0
            ])
            mob.move_to(pos)

        sun_final.add_updater(sun_final_updater)
        jup_final.add_updater(jup_final_updater)

        concl_1 = Text(
            "Planets don't orbit\na stationary Sun.",
            font_size=36,
            font="sans-serif",
            weight=BOLD,
            color="#FFFFFF",
            line_spacing=1.2,
        ).move_to([0, TOP_TEXT_Y + 0.5, 0])

        concl_2 = Text(
            "Both objects orbit their\ncommon center of mass.",
            font_size=30,
            font="sans-serif",
            color="#72EFDD",
            line_spacing=1.3,
        ).move_to([0, TOP_TEXT_Y - 0.7, 0])

        bary_anchor_tag = Text(
            "BARYCENTER",
            font_size=18,
            font="sans-serif",
            weight=BOLD,
            color="#00F5D4",
        ).next_to(final_bary_marker, DOWN, buff=0.18)

        self.add(sun_orbit_circle, jup_orbit_circle, final_bary_marker, bary_anchor_tag, sun_final, jup_final)

        self.play(
            FadeIn(concl_1, shift=UP * 0.2),
            final_clock.animate.increment_value(1.2),
            run_time=1.2,
            rate_func=linear,
        )
        self.play(
            FadeIn(concl_2, shift=UP * 0.2),
            final_clock.animate.increment_value(2.0),
            run_time=2.0,
            rate_func=linear,
        )

        verdict = Text(
            "THE SUN WOBBLES THROUGH SPACE",
            font_size=23,
            font="sans-serif",
            weight=BOLD,
            color="#FFD166",
        ).move_to([0, -4.8, 0])

        self.play(
            FadeIn(verdict, shift=UP * 0.15),
            final_clock.animate.increment_value(2.8),
            run_time=2.8,
            rate_func=linear,
        )

        sun_final.clear_updaters()
        jup_final.clear_updaters()

        self.play(
            FadeOut(concl_1),
            FadeOut(concl_2),
            FadeOut(verdict),
            FadeOut(bary_anchor_tag),
            FadeOut(sun_orbit_circle),
            FadeOut(jup_orbit_circle),
            FadeOut(final_bary_marker),
            FadeOut(sun_final),
            FadeOut(jup_final),
            FadeOut(starfield),
            run_time=1.5,
        )
        self.wait(0.5)
