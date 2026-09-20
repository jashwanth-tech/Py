from manim import *
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    "frame_width": 9,
    "frame_height": 16,
    "pixel_width": 1080,
    "pixel_height": 1920,
    "frame_rate": 30,
    "preview_quality": "l",       # l, m, h, p, k
    "duration": 52.0,
    "galaxy_particles": 180,
    "galaxy_seed": 7,
}

# Vertical format. The scene itself uses normalized Manim coordinates.
config.pixel_width = CONFIG["pixel_width"]
config.pixel_height = CONFIG["pixel_height"]
config.frame_rate = CONFIG["frame_rate"]
config.frame_width = CONFIG["frame_width"]
config.frame_height = CONFIG["frame_height"]

# ============================================================
# SCIENTIFIC MODEL
# ============================================================
# This is a hierarchical, normalized visualization model.
#
# Heliocentric frame:
#     r_earth_sun(t) = a [cos(w t + phase), sin(w t + phase)]
#
# Galactic frame:
#     R_solar_galaxy(t) = A [cos(Omega t + phase),
#                            sin(Omega t + phase)]
#
# Combined galactic-frame Earth position:
#     r_earth_galaxy(t) = R_solar_galaxy(t) + r_earth_sun(t)
#
# The two angular velocities are deliberately chosen for visual
# clarity, not for an astronomical ephemeris. A real calculation
# would require the Milky Way's gravitational potential, the Sun's
# 3-D phase-space state, perturbations, and a consistent time unit.
# The galactic path is therefore illustrative rather than precise.
#
# The local orbit remains physically meaningful in the heliocentric
# model even after the larger-scale translation is applied.

A_GAL = 2.65
A_EARTH = 0.58
OMEGA_GAL = 0.34
OMEGA_EARTH = 4.6
GAL_PHASE = 0.0
EARTH_PHASE = 0.35

def galactic_position(t):
    angle = OMEGA_GAL * t + GAL_PHASE
    return A_GAL * np.array([np.cos(angle), np.sin(angle), 0.0])

def earth_local_position(t):
    angle = OMEGA_EARTH * t + EARTH_PHASE
    # Slight eccentricity is included to avoid implying that every
    # heliocentric orbit is perfectly circular.
    eccentricity = 0.07
    radius = A_EARTH * (1 - eccentricity**2) / (
        1 + eccentricity * np.cos(angle)
    )
    return radius * np.array([np.cos(angle), np.sin(angle), 0.0])

def earth_galactic_position(t):
    return galactic_position(t) + earth_local_position(t)

def v2(p):
    return np.array([p[0], p[1], 0.0])

# ============================================================
# VISUAL HELPERS
# ============================================================

BG = "#070B18"
WHITE = "#F5F7FF"
MUTED = "#AAB4D0"
SUN_COLOR = "#FFC857"
EARTH_COLOR = "#55B8FF"
GALAXY_COLOR = "#6577C8"
ACCENT = "#8BE9FD"
GREEN = "#8AFF80"
PINK = "#FF91C8"

def title_text(text, size=0.52):
    return Text(
        text,
        font="DejaVu Sans",
        weight=BOLD,
        font_size=size,
        color=WHITE,
        stroke_width=0,
    )

def body_text(text, size=0.30, color=MUTED):
    return Text(
        text,
        font="DejaVu Sans",
        font_size=size,
        color=color,
        stroke_width=0,
    )

def make_sun(radius=0.18):
    glow = Circle(radius=radius * 1.65, color=SUN_COLOR,
                  fill_opacity=0.08, stroke_opacity=0)
    core = Circle(radius=radius, color=SUN_COLOR,
                  fill_color=SUN_COLOR, fill_opacity=1,
                  stroke_width=1.5, stroke_color="#FFE7A0")
    return VGroup(glow, core)

def make_earth(radius=0.075):
    ocean = Circle(radius=radius, color=EARTH_COLOR,
                   fill_color=EARTH_COLOR, fill_opacity=1,
                   stroke_width=1.2, stroke_color=WHITE)
    land = VMobject(color="#8AFF80", fill_color="#8AFF80",
                    fill_opacity=0.85, stroke_width=0)
    land.set_points_as_corners([
        [-0.035, 0.018, 0], [-0.005, 0.040, 0],
        [0.020, 0.010, 0], [0.038, -0.010, 0],
        [0.005, -0.032, 0], [-0.022, -0.018, 0],
        [-0.035, 0.018, 0],
    ])
    land.scale(radius / 0.075)
    return VGroup(ocean, land)

def orbit_path(radius, eccentricity=0.0, color=WHITE,
               opacity=0.45, stroke_width=1.5):
    points = []
    for theta in np.linspace(0, TAU, 240):
        r = radius * (1 - eccentricity**2) / (
            1 + eccentricity * np.cos(theta)
        )
        points.append([r * np.cos(theta), r * np.sin(theta), 0])
    path = VMobject()
    path.set_points_as_corners(points + [points[0]])
    path.set_stroke(color=color, width=stroke_width, opacity=opacity)
    return path

def galaxy_curve(radius, turns=1.6, phase=0.0, color=GALAXY_COLOR,
                 opacity=0.25, width=1.2):
    points = []
    theta_values = np.linspace(0.15, turns * TAU, 220)
    for theta in theta_values:
        r = radius * theta / (turns * TAU)
        x = r * np.cos(theta + phase)
        y = 0.62 * r * np.sin(theta + phase)
        points.append([x, y, 0])
    curve = VMobject()
    curve.set_points_as_corners(points)
    curve.set_stroke(color=color, width=width, opacity=opacity)
    return curve

def galaxy_group(seed=7, count=180):
    rng = np.random.default_rng(seed)
    dots = VGroup()
    for _ in range(count):
        radius = np.sqrt(rng.random()) * 3.2
        theta = rng.random() * TAU
        arm_bias = rng.choice([-1, 1])
        theta += arm_bias * 0.55 * radius
        x = radius * np.cos(theta)
        y = 0.62 * radius * np.sin(theta)
        if rng.random() < 0.12:
            color = WHITE
            opacity = 0.55
        else:
            color = GALAXY_COLOR
            opacity = 0.16 + 0.24 * rng.random()
        dot = Dot([x, y, 0], radius=0.012 + 0.018 * rng.random(),
                  color=color, fill_opacity=opacity, stroke_opacity=0)
        dots.add(dot)
    return dots

def arrow_between(start, end, color=ACCENT):
    return Arrow(
        start, end, buff=0.04, stroke_width=2.4,
        max_tip_length_to_length_ratio=0.18, color=color
    )

def safe_position(mob, y):
    mob.move_to([0, y, 0])
    return mob

# ============================================================
# MAIN SCENE
# ============================================================

class EarthReferenceFrames(Scene):
    def construct(self):
        self.camera.background_color = BG

        # The complete story is timed to approximately 52 seconds.
        self.scene_one()
        self.scene_two()
        self.scene_three()
        self.scene_four()
        self.scene_five()
        self.scene_six()

    # --------------------------------------------------------
    # SCENE 1: textbook heliocentric model, 0–8 seconds
    # --------------------------------------------------------
    def scene_one(self):
        heading = title_text("Earth orbits the Sun", 0.52)
        frame_label = body_text("Heliocentric reference frame", 0.27, ACCENT)
        heading.to_edge(UP, buff=0.48)
        frame_label.next_to(heading, DOWN, buff=0.14)

        sun = make_sun(0.18)
        orbit = orbit_path(A_EARTH, eccentricity=0.07,
                           color=WHITE, opacity=0.58, stroke_width=1.7)
        earth = make_earth(0.075)

        self.play(FadeIn(heading, shift=DOWN * 0.15),
                  FadeIn(frame_label, shift=DOWN * 0.1), run_time=0.7)
        self.play(Create(orbit), FadeIn(sun), FadeIn(earth), run_time=0.9)

        phase = ValueTracker(0.0)

        def update_earth(m):
            t = phase.get_value()
            m.move_to(earth_local_position(t))
        earth.add_updater(update_earth)

        self.play(phase.animate.set_value(2.0 * TAU / OMEGA_EARTH),
                  run_time=6.1, rate_func=linear)
        earth.clear_updaters()
        self.wait(0.3)

        self._sun = sun
        self._earth = earth
        self._orbit = orbit
        self._heading = heading
        self._frame_label = frame_label

    # --------------------------------------------------------
    # SCENE 2: question the picture, 8–14 seconds
    # --------------------------------------------------------
    def scene_two(self):
        question = title_text("But is the Sun standing still?", 0.43)
        question.next_to(self._frame_label, DOWN, buff=0.55)

        sub = body_text("The model is valid — but the frame is local.", 0.27, MUTED)
        sub.next_to(question, DOWN, buff=0.18)

        self.play(
            self._earth.animate.scale(0.96),
            FadeIn(question, shift=UP * 0.15),
            FadeIn(sub, shift=UP * 0.1),
            run_time=1.0
        )
        self.wait(2.0)

        frame_shift = body_text("Change the reference frame.", 0.32, ACCENT)
        frame_shift.next_to(sub, DOWN, buff=0.28)
        self.play(FadeIn(frame_shift, shift=UP * 0.1), run_time=0.7)
        self.wait(1.2)

        self.play(FadeOut(question), FadeOut(sub), FadeOut(frame_shift),
                  run_time=0.6)

    # --------------------------------------------------------
    # SCENE 3: simplified Milky Way, 14–24 seconds
    # --------------------------------------------------------
    def scene_three(self):
        self.play(
            FadeOut(self._heading),
            FadeOut(self._frame_label),
            FadeOut(self._sun),
            FadeOut(self._earth),
            FadeOut(self._orbit),
            run_time=0.7
        )

        heading = title_text("Milky Way — simplified model", 0.43)
        heading.to_edge(UP, buff=0.46)
        label = body_text("The Solar System also moves around the galaxy.", 0.25, MUTED)
        label.next_to(heading, DOWN, buff=0.14)

        galaxy = VGroup()
        galaxy.add(galaxy_group(CONFIG["galaxy_seed"], CONFIG["galaxy_particles"]))
        for radius, phase in [(3.1, 0.0), (2.7, 1.8), (2.3, 3.6)]:
            galaxy.add(galaxy_curve(radius, phase=phase))
        bulge = Ellipse(width=0.9, height=0.55, color=SUN_COLOR,
                        fill_color=SUN_COLOR, fill_opacity=0.17,
                        stroke_width=1.2, stroke_opacity=0.65)
        galaxy.add(bulge)

        galactic_orbit = Circle(radius=A_GAL, color=ACCENT,
                                stroke_width=1.5, stroke_opacity=0.55)
        solar_marker = Dot(galactic_position(0), radius=0.085, color=SUN_COLOR)
        solar_label = body_text("Solar System", 0.25, SUN_COLOR)
        solar_label.next_to(solar_marker, RIGHT, buff=0.13)

        self.play(FadeIn(heading), FadeIn(label), run_time=0.6)
        self.play(FadeIn(galaxy), Create(galactic_orbit), run_time=1.4)
        self.play(FadeIn(solar_marker), FadeIn(solar_label), run_time=0.5)

        galactic_tracker = ValueTracker(0.0)

        def update_marker(m):
            m.move_to(galactic_position(galactic_tracker.get_value()))

        def update_label(m):
            m.next_to(solar_marker, RIGHT, buff=0.13)

        solar_marker.add_updater(update_marker)
        solar_label.add_updater(update_label)

        self.play(galactic_tracker.animate.set_value(2.2 * TAU / OMEGA_GAL),
                  run_time=5.8, rate_func=linear)
        solar_marker.clear_updaters()
        solar_label.clear_updaters()
        self.wait(0.3)

        self._galaxy = galaxy
        self._galactic_orbit = galactic_orbit
        self._solar_marker = solar_marker
        self._solar_label = solar_label
        self._galactic_tracker = galactic_tracker
        self._galaxy_heading = heading
        self._galaxy_label = label

    # --------------------------------------------------------
    # SCENE 4: combine the motions, 24–39 seconds
    # --------------------------------------------------------
    def scene_four(self):
        equation = MathTex(
            r"\vec r_{\mathrm{Earth,galaxy}}(t)",
            r"=",
            r"\vec R_{\mathrm{Solar\,System,galaxy}}(t)",
            r"+",
            r"\vec r_{\mathrm{Earth,Sun}}(t)",
            font_size=28,
            color=WHITE
        )
        equation.scale(0.72)
        equation.to_edge(DOWN, buff=0.55)

        explanation = body_text(
            "Galactic motion + local orbital motion", 0.27, ACCENT
        )
        explanation.next_to(equation, UP, buff=0.18)

        # Use a compact inset to keep both scales readable.
        inset = RoundedRectangle(
            corner_radius=0.08, width=3.8, height=3.8,
            stroke_color=WHITE, stroke_opacity=0.35,
            fill_color=BG, fill_opacity=0.92, stroke_width=1.2
        )
        inset.to_edge(RIGHT, buff=0.35).shift(DOWN * 0.15)

        inset_sun = make_sun(0.13)
        inset_sun.move_to(inset.get_center())
        inset_orbit = orbit_path(A_EARTH * 1.55, eccentricity=0.07,
                                 color=WHITE, opacity=0.5, stroke_width=1.2)
        inset_orbit.move_to(inset.get_center())
        inset_earth = make_earth(0.055)

        self.play(FadeOut(self._galaxy_heading), FadeOut(self._galaxy_label),
                  FadeOut(self._galaxy), FadeOut(self._galactic_orbit),
                  FadeOut(self._solar_label), run_time=0.8)
        self.play(FadeIn(inset), FadeIn(inset_sun), Create(inset_orbit),
                  FadeIn(inset_earth), run_time=0.8)

        # Main combined path is shown as a precomputed curve. This
        # avoids rebuilding a large Mobject every frame.
        combined_points = []
        for t in np.linspace(0, 2.1 * TAU / OMEGA_GAL, 900):
            p = earth_galactic_position(t)
            combined_points.append([p[0], p[1], 0])
        combined_path = VMobject()
        combined_path.set_points_as_corners(combined_points)
        combined_path.set_stroke(color=ACCENT, width=2.0, opacity=0.85)
        combined_path.scale(0.72)
        combined_path.shift(LEFT * 1.15 + DOWN * 0.05)

        galactic_center = Dot(LEFT * 1.15 + DOWN * 0.05, radius=0.06,
                              color=SUN_COLOR)
        moving_earth = make_earth(0.06)
        moving_sun = make_sun(0.12)
        moving_sun.move_to(LEFT * 1.15 + DOWN * 0.05)

        t_tracker = ValueTracker(0.0)

        def update_combined_earth(m):
            p = earth_galactic_position(t_tracker.get_value())
            m.move_to(v2(p) * 0.72 + LEFT * 1.15 + DOWN * 0.05)

        def update_combined_sun(m):
            p = galactic_position(t_tracker.get_value())
            m.move_to(v2(p) * 0.72 + LEFT * 1.15 + DOWN * 0.05)

        def update_inset_earth(m):
            p = earth_local_position(t_tracker.get_value())
            center = inset.get_center()
            m.move_to(center + v2(p) * 1.55)

        moving_earth.add_updater(update_combined_earth)
        moving_sun.add_updater(update_combined_sun)
        inset_earth.add_updater(update_inset_earth)

        self.play(Create(combined_path), FadeIn(galactic_center),
                  FadeIn(moving_sun), FadeIn(moving_earth),
                  FadeIn(explanation), FadeIn(equation), run_time=1.2)

        self.play(t_tracker.animate.set_value(2.1 * TAU / OMEGA_GAL),
                  run_time=10.2, rate_func=linear)

        moving_earth.clear_updaters()
        moving_sun.clear_updaters()
        inset_earth.clear_updaters()
        self.wait(0.4)

        self._equation = equation
        self._explanation = explanation
        self._inset = inset
        self._inset_sun = inset_sun
        self._inset_orbit = inset_orbit
        self._inset_earth = inset_earth
        self._combined_path = combined_path
        self._moving_earth = moving_earth
        self._moving_sun = moving_sun
        self._galactic_center = galactic_center

    # --------------------------------------------------------
    # SCENE 5: compare reference frames, 39–48 seconds
    # --------------------------------------------------------
    def scene_five(self):
        self.play(
            FadeOut(self._equation),
            FadeOut(self._explanation),
            FadeOut(self._combined_path),
            FadeOut(self._galactic_center),
            FadeOut(self._moving_earth),
            FadeOut(self._moving_sun),
            FadeOut(self._inset),
            FadeOut(self._inset_sun),
            FadeOut(self._inset_orbit),
            FadeOut(self._inset_earth),
            run_time=0.8
        )

        heading = title_text("Same physics. Different reference frames.", 0.40)
        heading.to_edge(UP, buff=0.48)

        left_panel = RoundedRectangle(
            corner_radius=0.08, width=3.7, height=5.1,
            stroke_color=ACCENT, stroke_opacity=0.65,
            fill_color="#0D1429", fill_opacity=0.9, stroke_width=1.3
        ).shift(LEFT * 2.0 + DOWN * 0.25)

        right_panel = RoundedRectangle(
            corner_radius=0.08, width=3.7, height=5.1,
            stroke_color=SUN_COLOR, stroke_opacity=0.65,
            fill_color="#0D1429", fill_opacity=0.9, stroke_width=1.3
        ).shift(RIGHT * 2.0 + DOWN * 0.25)

        left_label = body_text("Local reference frame", 0.27, ACCENT)
        right_label = body_text("Galactic reference frame", 0.27, SUN_COLOR)
        left_label.next_to(left_panel, DOWN, buff=0.18)
        right_label.next_to(right_panel, DOWN, buff=0.18)

        local_sun = make_sun(0.13).move_to(left_panel.get_center())
        local_orbit = orbit_path(0.9, eccentricity=0.07,
                                 color=WHITE, opacity=0.6, stroke_width=1.4)
        local_orbit.move_to(left_panel.get_center())
        local_earth = make_earth(0.055)

        right_galaxy = VGroup(galaxy_group(13, 65)).scale(0.42)
        right_galaxy.move_to(right_panel.get_center())
        right_path = Circle(radius=0.78, color=ACCENT,
                            stroke_width=1.2, stroke_opacity=0.7)
        right_path.move_to(right_panel.get_center())
        right_solar = Dot(right_panel.get_center(), radius=0.06, color=SUN_COLOR)

        self.play(FadeIn(heading), FadeIn(left_panel), FadeIn(right_panel),
                  run_time=0.7)
        self.play(FadeIn(local_sun), Create(local_orbit),
                  FadeIn(local_earth), FadeIn(right_galaxy),
                  Create(right_path), FadeIn(right_solar),
                  FadeIn(left_label), FadeIn(right_label), run_time=1.1)

        local_tracker = ValueTracker(0.0)
        gal_tracker = ValueTracker(0.0)

        def update_local(m):
            m.move_to(left_panel.get_center() + earth_local_position(
                local_tracker.get_value()) * 1.55)

        def update_gal(m):
            m.move_to(right_panel.get_center() + v2(
                galactic_position(gal_tracker.get_value())) * 0.29)

        local_earth.add_updater(update_local)
        right_solar.add_updater(update_gal)

        self.play(
            local_tracker.animate.set_value(2.0 * TAU / OMEGA_EARTH),
            gal_tracker.animate.set_value(1.6 * TAU / OMEGA_GAL),
            run_time=5.0, rate_func=linear
        )

        local_earth.clear_updaters()
        right_solar.clear_updaters()

        conclusion = body_text("Both descriptions can be useful.", 0.34, WHITE)
        conclusion.to_edge(DOWN, buff=0.78)
        self.play(FadeIn(conclusion, shift=UP * 0.1), run_time=0.7)
        self.wait(0.7)

        self._frame_heading = heading
        self._frame_panels = VGroup(
            left_panel, right_panel, local_sun, local_orbit, local_earth,
            right_galaxy, right_path, right_solar, left_label, right_label,
            conclusion
        )

    # --------------------------------------------------------
    # SCENE 6: final conclusion, 48–52 seconds
    # --------------------------------------------------------
    def scene_six(self):
        final_title = title_text("The path depends on the reference frame.", 0.44)
        final_title.to_edge(UP, buff=0.65)

        final_subtitle = body_text(
            "Earth has no single universal visual path.", 0.31, ACCENT
        )
        final_subtitle.next_to(final_title, DOWN, buff=0.22)

        self.play(
            FadeOut(self._frame_heading),
            FadeOut(self._frame_panels),
            FadeIn(final_title, shift=DOWN * 0.1),
            FadeIn(final_subtitle, shift=DOWN * 0.1),
            run_time=0.9
        )

        final_line = body_text(
            "The textbook model was not wrong. It was local.", 0.28, MUTED
        )
        final_line.next_to(final_subtitle, DOWN, buff=0.28)

        self.play(FadeIn(final_line, shift=UP * 0.1), run_time=0.8)
        self.wait(2.2)


# ============================================================
# OPTIONAL LOCAL TEST
# ============================================================
# Render with:
#     manim -pql earth_reference_frames.py EarthReferenceFrames
#
# The script intentionally uses normalized visual units. It is not
# a precision astronomical simulation or a 3-D galactic ephemeris.
