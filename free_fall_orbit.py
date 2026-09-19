"""
Orbital Motion as Continuous Free Fall: "You can fall forever and never hit the ground."
Target: Manim Community Edition (9:16 Vertical Format, 1080x1920, 60 FPS)
Physics: Numerical integration of Newtonian two-body gravitational acceleration (a = -GM r / |r|^3).

Visual language: Newton's cannonball figure (Principia / System of the World).
Three launches from ONE point with increasing sideways speed, all kept on screen
as ghost paths, ending in the closed orbit. The payoff frame shows the motion as
"straight-line inertia + a fall toward Earth" (dots on the straight path vs dots
on the real path, joined by the fall).
"""

from manim import *
import numpy as np

# -------------------------------------------------------------------------
# 1. Configuration & Canvas Setup (9:16 Vertical Video)
# -------------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#030712"


# -------------------------------------------------------------------------
# 2. Physics Engine: Numerical Integration (Velocity-Verlet)
# -------------------------------------------------------------------------
SCALE = 1.25                     # bigger Earth/orbit so they fill the 9-unit-wide frame
GM = 10.0 * SCALE**3             # scaled so the orbital period stays ~7.62 s
R_EARTH = 1.45 * SCALE           # Earth radius
R_ORBIT = 2.45 * SCALE           # release distance from Earth center
R_CONTACT = R_EARTH + 0.10       # satellite "touches down" slightly above the drawn surface
V_CIRC = np.sqrt(GM / R_ORBIT)   # exact circular orbital speed
V_SUB_FRAC = 0.58                # suborbital launch speed as a fraction of V_CIRC
ORBIT_PERIOD = 2.0 * np.pi * np.sqrt(R_ORBIT**3 / GM)

DT = 0.001                       # integrator step (s). One array index == one step.

# One consistent clock for every case. Falls and the suborbital arc play in slow motion
# (they only last ~1 s of simulated time), the orbit plays at real simulated speed.
RATE_FALL = 0.5                  # simulated seconds per video second, cases 1 and 2
RATE_ORBIT = 1.0                 # simulated seconds per video second, orbit scenes


class Trajectory:
    """Sampled trajectory. Index i is simulated time i * DT."""

    def __init__(self, r, v, a):
        self.r, self.v, self.a = np.array(r), np.array(v), np.array(a)
        self.t_max = (len(self.r) - 1) * DT

    def at(self, tau):
        i = int(round(min(max(tau, 0.0), self.t_max) / DT))
        return self.r[i], self.v[i], self.a[i]


def integrate_trajectory(r0, v0, t_max, stop_radius=None):
    """
    Velocity-Verlet under a = -GM * r / |r|^3.
    If stop_radius is given, integration ends on the first step that reaches it.
    """
    def acc(p):
        return -GM * p / np.linalg.norm(p) ** 3

    r = np.array(r0, dtype=float)
    v = np.array(v0, dtype=float)
    a = acc(r)
    R, V, A = [r.copy()], [v.copy()], [a.copy()]

    for _ in range(int(round(t_max / DT))):
        r_new = r + v * DT + 0.5 * a * DT**2
        a_new = acc(r_new)
        v_new = v + 0.5 * (a + a_new) * DT
        r, v, a = r_new, v_new, a_new
        R.append(r.copy())
        V.append(v.copy())
        A.append(a.copy())
        if stop_radius is not None and np.linalg.norm(r) <= stop_radius:
            break

    return Trajectory(R, V, A)


START = [0.0, R_ORBIT, 0.0]

# Three regimes, same release point, increasing sideways speed
RAD = integrate_trajectory(START, [0.0, 0.0, 0.0], t_max=5.0, stop_radius=R_CONTACT)
SUB = integrate_trajectory(START, [V_SUB_FRAC * V_CIRC, 0.0, 0.0], t_max=5.0, stop_radius=R_CONTACT)
ORB = integrate_trajectory(START, [V_CIRC, 0.0, 0.0], t_max=ORBIT_PERIOD + 0.05)


def _sanity_checks():
    """Fail loudly at import if the physics is wrong."""
    # Case 1 and 2 must end on the surface, not run out of time
    assert np.linalg.norm(RAD.r[-1]) <= R_CONTACT, "radial fall never reached the surface"
    assert np.linalg.norm(SUB.r[-1]) <= R_CONTACT, "suborbital arc never reached the surface"
    # Suborbital periapsis (from apoapsis speed) must be below the surface
    k2 = V_SUB_FRAC**2
    assert R_ORBIT * k2 / (2.0 - k2) < R_EARTH, "0.58 V_circ would not actually hit Earth"
    # Case 3: constant radius and conserved energy, and it closes after one period
    rad = np.linalg.norm(ORB.r, axis=1)
    assert np.max(np.abs(rad - R_ORBIT)) < 1e-5, "orbit is not circular"
    energy = 0.5 * np.sum(ORB.v**2, axis=1) - GM / rad
    assert np.ptp(energy) < 1e-6, "energy not conserved"
    i_p = int(round(ORBIT_PERIOD / DT))
    assert np.linalg.norm(ORB.r[i_p] - ORB.r[0]) < 1e-2, "orbit does not close after one period"


_sanity_checks()


# -------------------------------------------------------------------------
# 3. Visual Constructors (Earth, Satellite, Text)
# -------------------------------------------------------------------------
def create_earth(center, radius=R_EARTH):
    """Multi-layered Earth: atmosphere, ocean, continents, soft day/night terminator, limb light."""
    earth = VGroup()

    # Atmospheric glow rings
    halo_radii = np.linspace(radius * 1.35, radius * 1.02, 8)
    halo_alphas = np.linspace(0.02, 0.22, 8)
    for hr, ha in zip(halo_radii, halo_alphas):
        earth.add(
            Circle(radius=hr, fill_color="#00B4D8", fill_opacity=ha, stroke_width=0).move_to(center)
        )

    # Deep ocean base
    ocean = Circle(
        radius=radius,
        fill_color="#14527A",
        fill_opacity=1.0,
        stroke_color="#48CAE4",
        stroke_width=1.5,
    ).move_to(center)
    ocean.set_sheen(-0.45, RIGHT)
    earth.add(ocean)

    # Stylized continental landmasses
    continents = VGroup()
    c1 = Polygon(
        [-0.45, 0.55, 0], [-0.15, 0.85, 0], [0.35, 0.70, 0],
        [0.55, 0.25, 0], [0.15, 0.05, 0], [-0.25, 0.20, 0],
        fill_color="#2D6A4F", fill_opacity=0.92, stroke_width=0,
    )
    c2 = Polygon(
        [-0.75, -0.15, 0], [-0.35, 0.10, 0], [-0.15, -0.45, 0],
        [-0.45, -0.85, 0], [-0.85, -0.55, 0],
        fill_color="#40916C", fill_opacity=0.92, stroke_width=0,
    )
    c3 = Polygon(
        [0.25, -0.20, 0], [0.75, -0.10, 0], [0.65, -0.75, 0],
        [0.15, -0.65, 0],
        fill_color="#1B4332", fill_opacity=0.90, stroke_width=0,
    )
    c4 = Polygon(
        [-0.20, 1.05, 0], [0.15, 1.15, 0], [0.05, 0.95, 0],
        fill_color="#52B788", fill_opacity=0.92, stroke_width=0,
    )
    continents.add(c1, c2, c3, c4).scale(radius / 1.45).move_to(center)
    earth.add(continents)

    # Soft terminator: stacked crescents on the right side (light comes from the left).
    # Boolean ops need skia-pathops; fall back to a correctly centred half-disc if missing.
    try:
        for shift, alpha in [(0.30, 0.16), (0.55, 0.16), (0.80, 0.18)]:
            night = Difference(
                Circle(radius=radius).move_to(center),
                Circle(radius=radius).move_to(center + LEFT * shift * radius),
                fill_color="#020617", fill_opacity=alpha, stroke_width=0,
            )
            earth.add(night)
    except Exception:
        earth.add(
            Sector(
                radius=radius, angle=PI, start_angle=-PI / 2, arc_center=center,
                fill_color="#020617", fill_opacity=0.40, stroke_width=0,
            )
        )

    # Sunlit limb
    earth.add(
        Arc(
            radius=radius, start_angle=PI / 2, angle=PI, arc_center=center,
            stroke_color="#CAF0F8", stroke_width=2.2, stroke_opacity=0.75,
        )
    )
    return earth


def create_satellite():
    """Satellite with solar arrays and antenna. A soft glow sits behind it so it reads on a phone."""
    satellite = VGroup()

    glow = VGroup(
        *[
            Circle(radius=r, fill_color="#64DFDF", fill_opacity=o, stroke_width=0)
            for r, o in [(0.55, 0.05), (0.40, 0.08), (0.27, 0.12)]
        ]
    )

    bus = RoundedRectangle(
        corner_radius=0.03, height=0.14, width=0.20,
        fill_color="#E0E1DD", fill_opacity=1.0, stroke_color="#778DA9", stroke_width=1.0,
    )
    panel_l = Rectangle(
        height=0.10, width=0.24, fill_color="#1D3557", fill_opacity=0.95,
        stroke_color="#64DFDF", stroke_width=1.2,
    ).next_to(bus, LEFT, buff=0.03)
    panel_r = Rectangle(
        height=0.10, width=0.24, fill_color="#1D3557", fill_opacity=0.95,
        stroke_color="#64DFDF", stroke_width=1.2,
    ).next_to(bus, RIGHT, buff=0.03)
    div_l = Line(panel_l.get_top(), panel_l.get_bottom(), stroke_color="#64DFDF", stroke_width=0.8)
    div_r = Line(panel_r.get_top(), panel_r.get_bottom(), stroke_color="#64DFDF", stroke_width=0.8)
    antenna_rod = Line(bus.get_top(), bus.get_top() + UP * 0.08, stroke_color="#E0E1DD", stroke_width=1.2)
    dish = Arc(radius=0.07, angle=PI, stroke_color="#FFD166", stroke_width=1.4).next_to(antenna_rod, UP, buff=0)

    satellite.add(glow, bus, panel_l, panel_r, div_l, div_r, antenna_rod, dish)
    satellite.scale(1.5)
    return satellite


def label(text, size, color, y, weight=BOLD, line_spacing=1.2, max_w=8.2):
    """Text that can never run off the 9-unit-wide frame."""
    t = Text(text, font_size=size, font="sans-serif", weight=weight, color=color, line_spacing=line_spacing)
    if t.width > max_w:
        t.scale_to_fit_width(max_w)
    return t.move_to([0, y, 0])


# -------------------------------------------------------------------------
# 4. Master Animation Scene
# -------------------------------------------------------------------------
class FreeFallOrbitMaster(Scene):
    def construct(self):
        EARTH_POS = np.array([0.0, -0.7, 0.0])
        TOP_TEXT_Y = 5.5
        MID_TEXT_Y = 4.7
        sat_start_pos = EARTH_POS + np.array(START)
        self.sat_angle = 0.0

        # Background cosmic starfield with a slow twinkle
        starfield = VGroup()
        rng = np.random.RandomState(42)
        bases, phases = [], []
        for _ in range(85):
            base = rng.uniform(0.2, 0.7)
            starfield.add(
                Dot(
                    point=[rng.uniform(-4.3, 4.3), rng.uniform(-7.8, 7.8), 0],
                    radius=rng.uniform(0.012, 0.026),
                    color=WHITE,
                ).set_opacity(base)
            )
            bases.append(base)
            phases.append(rng.uniform(0, 2 * np.pi))
        tw = {"t": 0.0}

        def twinkle(group, dt):
            tw["t"] += dt
            for d, b, p in zip(group, bases, phases):
                d.set_opacity(b * (0.7 + 0.3 * np.sin(1.6 * tw["t"] + p)))

        starfield.add_updater(twinkle)
        self.add(starfield)

        earth = create_earth(EARTH_POS, radius=R_EARTH)
        self.add(earth)

        satellite = create_satellite()
        satellite.move_to(sat_start_pos)
        self.add(satellite)

        # ---- helpers -----------------------------------------------------
        def face(mob, direction):
            """Rotate mob so its solar-panel axis follows the velocity direction."""
            if np.linalg.norm(direction) < 1e-9:
                return
            ang = np.arctan2(direction[1], direction[0])
            mob.rotate(ang - self.sat_angle)
            self.sat_angle = ang

        def reset_satellite():
            satellite.clear_updaters()
            satellite.rotate(-self.sat_angle)
            self.sat_angle = 0.0
            satellite.move_to(sat_start_pos)

        A0 = GM / R_ORBIT**2

        def gravity_arrow():
            """Acceleration arrow that points at Earth and grows as gravity strengthens (1/r^2)."""
            def build():
                c = satellite.get_center()
                d = EARTH_POS - c
                dist = np.linalg.norm(d)
                length = 0.95 * (GM / dist**2) / A0
                return Arrow(
                    start=c, end=c + d / dist * length, buff=0,
                    color="#FF9F1C", stroke_width=3.6, max_tip_length_to_length_ratio=0.35,
                )
            return always_redraw(build)

        def impact(point, color):
            """Ring plus debris burst at the touchdown point, thrown along the surface normal."""
            normal = (point - EARTH_POS) / np.linalg.norm(point - EARTH_POS)
            ring = Circle(radius=0.1, color=color, stroke_width=3.0).move_to(point)
            debris = VGroup(*[Dot(point, radius=0.035, color=color) for _ in range(12)])
            anims = [ring.animate.scale(3.0).set_opacity(0.0)]
            for i, d in enumerate(debris):
                spread = np.radians(-70 + 140 * i / (len(debris) - 1))
                c, s = np.cos(spread), np.sin(spread)
                direction = np.array([normal[0] * c - normal[1] * s, normal[0] * s + normal[1] * c, 0])
                anims.append(d.animate.shift(direction * (0.5 + 0.35 * (i % 3))).set_opacity(0.0))
            return ring, debris, anims

        # =================================================================
        # SCENE 1 — THE HOOK (0.0s - 6.0s)
        # =================================================================
        hook_1 = label("What if you fell forever...", 38, "#FFFFFF", TOP_TEXT_Y)
        hook_2 = label("...without ever hitting\nthe ground?", 36, "#00F5D4", TOP_TEXT_Y - 0.2)

        self.play(FadeIn(hook_1, shift=UP * 0.3), run_time=1.0)
        self.wait(1.4)
        self.play(ReplacementTransform(hook_1, hook_2), run_time=0.8)
        self.wait(1.8)
        self.play(FadeOut(hook_2), run_time=0.6)

        # =================================================================
        # SCENE 2 — CASE 1: STRAIGHT VERTICAL FALL (6.0s - 12.0s)
        # =================================================================
        c1_title = label("CASE 1: ZERO SIDEWAYS VELOCITY", 25, "#FF5964", TOP_TEXT_Y + 0.3)
        c1_sub = label(
            "Gravity pulls straight down.\nYou collide with the surface.",
            23, "#E0E1DD", MID_TEXT_Y, weight=NORMAL,
        )
        a_vec = gravity_arrow()

        self.play(
            FadeIn(c1_title, shift=UP * 0.2),
            FadeIn(c1_sub, shift=UP * 0.2),
            FadeIn(a_vec),
            run_time=0.8,
        )

        trace1 = TracedPath(satellite.get_center, stroke_color="#FF5964", stroke_width=2.6, stroke_opacity=0.9)
        self.add(trace1)

        rad_clock = ValueTracker(0.0)
        satellite.add_updater(lambda m: m.move_to(EARTH_POS + RAD.at(rad_clock.get_value())[0]))
        self.play(
            rad_clock.animate.set_value(RAD.t_max),
            run_time=RAD.t_max / RATE_FALL,
            rate_func=linear,
        )
        satellite.clear_updaters()
        trace1.clear_updaters()

        ring1, debris1, anims1 = impact(satellite.get_center(), "#FF5964")
        self.add(ring1, debris1)
        a_vec.clear_updaters()
        self.play(
            FadeOut(a_vec),
            FadeOut(satellite, scale=0.3),
            trace1.animate.set_stroke(opacity=0.45),
            *anims1,
            run_time=0.7,
        )
        self.remove(ring1, debris1)
        self.wait(0.5)

        self.play(FadeOut(c1_title), FadeOut(c1_sub), run_time=0.5)

        # =================================================================
        # SCENE 3 — CASE 2: ADD SIDEWAYS VELOCITY (12.0s - 18.0s)
        # =================================================================
        reset_satellite()

        c2_title = label("CASE 2: MODERATE SIDEWAYS VELOCITY", 25, "#F4A261", TOP_TEXT_Y + 0.3)
        c2_sub = label(
            "The trajectory bends into an arc...\n...but still impacts Earth downrange.",
            23, "#E0E1DD", MID_TEXT_Y, weight=NORMAL,
        )

        # Arrow lengths are proportional to launch speed (0.58 of orbital)
        V_ARROW = 1.7
        v_sub_arrow = Arrow(
            start=sat_start_pos, end=sat_start_pos + RIGHT * V_ARROW * V_SUB_FRAC,
            buff=0, color="#00F5D4", stroke_width=3.5,
        )
        v_sub_label = Text("v_sideways", font_size=19, color="#00F5D4").next_to(v_sub_arrow, UP, buff=0.1)

        self.play(
            FadeIn(satellite),
            FadeIn(c2_title, shift=UP * 0.2),
            FadeIn(c2_sub, shift=UP * 0.2),
            GrowArrow(v_sub_arrow),
            FadeIn(v_sub_label),
            run_time=0.8,
        )
        self.wait(0.5)
        self.play(FadeOut(v_sub_arrow), FadeOut(v_sub_label), run_time=0.4)

        trace2 = TracedPath(satellite.get_center, stroke_color="#F4A261", stroke_width=2.6, stroke_opacity=0.9)
        self.add(trace2)

        sub_clock = ValueTracker(0.0)

        def update_sub_flight(mob):
            pos, vel, _ = SUB.at(sub_clock.get_value())
            mob.move_to(EARTH_POS + pos)
            face(mob, vel)

        satellite.add_updater(update_sub_flight)
        self.play(
            sub_clock.animate.set_value(SUB.t_max),
            run_time=SUB.t_max / RATE_FALL,
            rate_func=linear,
        )
        satellite.clear_updaters()
        trace2.clear_updaters()

        ring2, debris2, anims2 = impact(satellite.get_center(), "#F4A261")
        self.add(ring2, debris2)
        self.play(
            FadeOut(satellite, scale=0.3),
            trace2.animate.set_stroke(opacity=0.45),
            *anims2,
            run_time=0.6,
        )
        self.remove(ring2, debris2)
        self.wait(0.4)

        self.play(FadeOut(c2_title), FadeOut(c2_sub), run_time=0.6)

        # =================================================================
        # SCENE 4 — REACHING ORBITAL VELOCITY (18.0s - 27.0s)
        # =================================================================
        reset_satellite()

        c3_title = label("CASE 3: ORBITAL VELOCITY", 28, "#00F5D4", TOP_TEXT_Y + 0.4)
        eq_orbit = MathTex(r"v = \sqrt{\frac{GM}{r}}", font_size=42, color="#FFE66D").move_to(
            [0, TOP_TEXT_Y - 0.4, 0]
        )
        eq_note = label(
            "Fast enough that as you fall,\nEarth curves away at the exact same rate.",
            22, "#E0E1DD", MID_TEXT_Y - 0.7, weight=NORMAL,
        )

        v_orb_arrow = Arrow(
            start=sat_start_pos, end=sat_start_pos + RIGHT * V_ARROW,
            buff=0, color="#00F5D4", stroke_width=4.0,
        )

        self.play(
            FadeIn(satellite),
            FadeIn(c3_title, shift=UP * 0.2),
            FadeIn(eq_orbit, shift=UP * 0.2),
            FadeIn(eq_note, shift=UP * 0.2),
            GrowArrow(v_orb_arrow),
            run_time=1.0,
        )
        self.wait(1.0)
        self.play(FadeOut(v_orb_arrow), run_time=0.4)

        # One continuous simulated clock drives the orbit, so it keeps moving under every caption.
        orb_clock = ValueTracker(0.0)
        orb_rate = {"v": 0.0}
        orb_clock.add_updater(lambda m, dt: m.increment_value(dt * orb_rate["v"]))
        self.add(orb_clock)

        def update_orbital_motion(mob):
            pos, vel, _ = ORB.at(orb_clock.get_value() % ORBIT_PERIOD)
            mob.move_to(EARTH_POS + pos)
            face(mob, vel)

        satellite.add_updater(update_orbital_motion)

        # Orbit ring is revealed exactly as fast as the satellite sweeps it (clockwise from the top)
        ring_full = Arc(radius=R_ORBIT, start_angle=PI / 2, angle=-TAU, arc_center=EARTH_POS)
        orbit_ring = VMobject().set_stroke(color="#00F5D4", width=1.8, opacity=0.5)

        def update_ring(m):
            frac = min(orb_clock.get_value() / ORBIT_PERIOD, 1.0)
            if frac > 1e-4:
                m.pointwise_become_partial(ring_full, 0, frac)
            m.set_stroke(color="#00F5D4", width=1.8, opacity=0.5)

        orbit_ring.add_updater(update_ring)
        self.add(orbit_ring)

        # Comet tail
        comet = TracedPath(
            satellite.get_center, stroke_color="#72EFDD", stroke_width=4.0,
            dissipating_time=1.3, stroke_opacity=[0, 1],
        )
        self.add(comet)

        orb_rate["v"] = RATE_ORBIT
        self.wait(4.6)

        # =================================================================
        # SCENE 5 — THE INTELLECTUAL PAYOFF: FALLING VS CURVATURE (27.0s - 36.0s)
        # =================================================================
        self.play(FadeOut(c3_title), FadeOut(eq_orbit), FadeOut(eq_note), run_time=0.6)

        # Let the satellite finish its first lap (the ring closes), then freeze just past the top of
        # the orbit: velocity points sideways, gravity points down, the textbook picture.
        self.wait_until(lambda: orb_clock.get_value() >= ORBIT_PERIOD + 0.08)
        orb_rate["v"] = 0.0
        tau0 = orb_clock.get_value() % ORBIT_PERIOD
        p0, v0, a0 = ORB.at(tau0)
        curr_sat_pos = EARTH_POS + p0
        v_hat = v0 / np.linalg.norm(v0)
        a_hat = a0 / np.linalg.norm(a0)

        v_tangent = Arrow(
            start=curr_sat_pos, end=curr_sat_pos + v_hat * 1.5,
            buff=0, color="#00F5D4", stroke_width=3.5,
        )
        v_tag = Text("Velocity", font_size=20, color="#00F5D4").next_to(v_tangent.get_end(), UR, buff=0.1)

        a_inward = Arrow(
            start=curr_sat_pos, end=curr_sat_pos + a_hat * 1.2,
            buff=0, color="#FF9F1C", stroke_width=3.5,
        )
        a_tag = Text("Gravity (Falling)", font_size=20, color="#FF9F1C").next_to(a_inward, LEFT, buff=0.15)

        # Where inertia alone would carry the satellite (straight line at constant velocity)
        STEP, K = 0.35, 3
        tangent_drift = DashedLine(
            start=curr_sat_pos, end=curr_sat_pos + v0 * (K * STEP) + v_hat * 0.35,
            dash_length=0.12, color="#72EFDD", stroke_width=2.0,
        )

        # Equal time steps: straight-line position vs the real (numerically integrated) position.
        # The orange link between them is the fall.
        step_groups = []
        for k in range(1, K + 1):
            tk = k * STEP
            inertial = curr_sat_pos + v0 * tk
            actual = EARTH_POS + ORB.at((tau0 + tk) % ORBIT_PERIOD)[0]
            fall_link = Line(inertial, actual, color="#FF9F1C", stroke_width=3.2)
            d_in = Dot(inertial, radius=0.07, color="#72EFDD")
            d_act = Dot(actual, radius=0.08, color="#FF9F1C")
            step_groups.append(VGroup(fall_link, d_in, d_act))

        core_insight1 = label("Gravity pulls it downward continually...", 26, "#FFFFFF", TOP_TEXT_Y + 0.3)
        core_insight2 = label(
            "...while Earth's surface curves away\nbeneath it at the exact same rate.",
            24, "#72EFDD", MID_TEXT_Y, weight=NORMAL, line_spacing=1.3,
        )

        self.play(
            GrowArrow(v_tangent),
            FadeIn(v_tag),
            GrowArrow(a_inward),
            FadeIn(a_tag),
            Create(tangent_drift),
            FadeIn(core_insight1, shift=UP * 0.2),
            run_time=1.2,
        )
        self.play(
            LaggedStart(*[FadeIn(g) for g in step_groups], lag_ratio=0.4),
            run_time=1.4,
        )
        self.play(FadeIn(core_insight2, shift=UP * 0.2), run_time=1.0)
        self.wait(2.2)

        self.play(
            FadeOut(v_tangent), FadeOut(v_tag), FadeOut(a_inward), FadeOut(a_tag),
            FadeOut(tangent_drift), *[FadeOut(g) for g in step_groups],
            FadeOut(core_insight1), FadeOut(core_insight2),
            run_time=0.8,
        )

        orb_rate["v"] = RATE_ORBIT

        # =================================================================
        # SCENE 6 — THE COSMIC EXTENSION (36.0s - 42.0s)
        # =================================================================
        cosmic_title = label("THE UNIVERSAL PRINCIPLE", 28, "#FFD166", TOP_TEXT_Y + 0.4)

        cosmic_card = RoundedRectangle(
            corner_radius=0.18, height=2.2, width=7.8,
            fill_color="#0A1128", fill_opacity=0.90, stroke_color="#3A86FF", stroke_width=1.4,
        ).move_to([0, TOP_TEXT_Y - 1.2, 0])

        p1 = Text("Space Station around Earth", font_size=20, color="#FFFFFF")
        p2 = Text("Moon around Earth", font_size=20, color="#A8DADC")
        p3 = Text("Earth around the Sun", font_size=20, color="#FFD166")
        prog_group = VGroup(p1, p2, p3).arrange(DOWN, buff=0.22).move_to(cosmic_card.get_center())

        self.play(
            FadeIn(cosmic_title, shift=UP * 0.2),
            FadeIn(cosmic_card),
            FadeIn(prog_group),
            run_time=1.6,
        )

        cosmic_sub = label(
            "Every orbit in the universe is simply\nan object falling forever.",
            24, "#00F5D4", -4.8,
        )
        self.play(FadeIn(cosmic_sub, shift=UP * 0.2), run_time=2.2)

        self.play(
            FadeOut(cosmic_title), FadeOut(cosmic_card), FadeOut(prog_group), FadeOut(cosmic_sub),
            run_time=0.8,
        )

        # =================================================================
        # SCENE 7 — FINAL PAYOFF & CONCLUSION (42.0s - 49.0s)
        # =================================================================
        final_line1 = label("An orbit isn't the\nabsence of gravity.", 36, "#FFFFFF", TOP_TEXT_Y + 0.4)
        final_line2 = label(
            "It's falling forever without\never reaching the ground.",
            28, "#72EFDD", TOP_TEXT_Y - 1.1, weight=NORMAL, line_spacing=1.3,
        )
        verdict_badge = label("CONTINUOUS FREE FALL", 25, "#FFE66D", -4.8)

        self.play(FadeIn(final_line1, shift=UP * 0.2), run_time=1.2)
        self.play(FadeIn(final_line2, shift=UP * 0.2), run_time=2.0)
        self.play(FadeIn(verdict_badge, shift=UP * 0.15), run_time=2.5)

        # Freeze the orbit before the fade so nothing jitters while objects leave
        orb_rate["v"] = 0.0
        self.play(
            FadeOut(final_line1), FadeOut(final_line2), FadeOut(verdict_badge),
            FadeOut(orbit_ring), FadeOut(comet), FadeOut(trace1), FadeOut(trace2),
            FadeOut(satellite), FadeOut(earth), FadeOut(starfield),
            run_time=1.5,
        )
        self.wait(0.5)
