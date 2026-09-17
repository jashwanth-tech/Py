"""
Earth's Orbit: From Newtonian Pull to Relativistic Geodesics
Target: Manim Community Edition (9:16 Vertical Video, 1080x1920)
Physics: Numerical integration of Sun-Earth two-body system via Velocity-Verlet.
"""

from manim import *
import numpy as np

# -------------------------------------------------------------------------
# Global Video Configuration (9:16 Vertical Format for Shorts/Reels)
# -------------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.background_color = "#040814"


# -------------------------------------------------------------------------
# 1. Numerical Physics Engine (Velocity-Verlet Two-Body Simulation)
# -------------------------------------------------------------------------
def simulate_kepler_orbit(
    gm=14.0,
    r0=np.array([0.0, -1.85, 0.0]),
    e=0.22,
    dt=0.0005,
    steps=16000,
):
    """
    Numerically integrates a bound, eccentric Keplerian orbit using Velocity-Verlet.
    Returns precomputed time, position, velocity, and acceleration arrays.
    """
    r_mag0 = np.linalg.norm(r0)
    # Vis-viva equation for initial tangential velocity at periapsis
    vp = np.sqrt((gm / r_mag0) * (1.0 + e))
    v0 = np.array([vp, 0.0, 0.0])

    t_arr = np.zeros(steps)
    r_arr = np.zeros((steps, 3))
    v_arr = np.zeros((steps, 3))
    a_arr = np.zeros((steps, 3))

    def get_acc(pos):
        d = np.linalg.norm(pos)
        if d < 1e-5:
            return np.zeros(3)
        return -gm * pos / (d**3)

    r = r0.copy()
    v = v0.copy()
    a = get_acc(r)

    for i in range(steps):
        t_arr[i] = i * dt
        r_arr[i] = r
        v_arr[i] = v
        a_arr[i] = a

        # Velocity-Verlet step
        r_next = r + v * dt + 0.5 * a * (dt**2)
        a_next = get_acc(r_next)
        v_next = v + 0.5 * (a + a_next) * dt

        r, v, a = r_next, v_next, a_next

    # Identify orbital period via periapsis return
    y_vals = r_arr[1000:, 1]
    min_idx = 1000 + np.argmin(y_vals)
    orbital_period = t_arr[min_idx]

    return orbital_period, t_arr[:min_idx], r_arr[:min_idx], v_arr[:min_idx], a_arr[:min_idx]


# Precompute orbit table once at load time
ORBIT_PERIOD, T_TABLE, R_TABLE, V_TABLE, A_TABLE = simulate_kepler_orbit()
TABLE_LEN = len(T_TABLE)


def get_orbital_state(t_sim):
    """Interpolates precomputed orbit arrays for arbitrary continuous time."""
    tau = (t_sim % ORBIT_PERIOD) / ORBIT_PERIOD
    idx = int(tau * (TABLE_LEN - 1))
    return R_TABLE[idx], V_TABLE[idx], A_TABLE[idx]


# -------------------------------------------------------------------------
# 2. Visual Component Builders (Sun, Earth, Spacetime Grid)
# -------------------------------------------------------------------------
def create_sun(center):
    """Builds a multi-layered incandescent Sun with glowing corona."""
    sun = VGroup()
    # Deep corona glow rings
    radii = np.linspace(1.25, 0.52, 10)
    alphas = np.linspace(0.02, 0.28, 10)
    for r, a in zip(radii, alphas):
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
        radius=0.50,
        fill_color="#FFCA3A",
        fill_opacity=1.0,
        stroke_color="#FFEAA7",
        stroke_width=2.5,
    ).move_to(center)
    # White-hot inner core
    core = Circle(
        radius=0.34,
        fill_color="#FFFFFF",
        fill_opacity=0.92,
        stroke_width=0,
    ).move_to(center)

    sun.add(photosphere, core)
    return sun


def create_earth_mobject():
    """Builds a detailed Earth graphic with stylized continents and atmosphere."""
    earth = VGroup()

    # Deep ocean sphere
    ocean = Circle(
        radius=0.23,
        fill_color="#1E6091",
        fill_opacity=1.0,
        stroke_width=0,
    )
    # Stylized landmass continents
    c1 = Polygon(
        [-0.08, 0.08, 0], [-0.02, 0.16, 0], [0.09, 0.12, 0],
        [0.12, 0.02, 0], [0.03, -0.02, 0],
        fill_color="#40916C", fill_opacity=0.95, stroke_width=0,
    )
    c2 = Polygon(
        [-0.14, -0.02, 0], [-0.06, 0.04, 0], [-0.02, -0.08, 0],
        [-0.08, -0.16, 0], [-0.14, -0.10, 0],
        fill_color="#52B788", fill_opacity=0.95, stroke_width=0,
    )
    c3 = Polygon(
        [0.05, -0.05, 0], [0.15, -0.03, 0], [0.13, -0.14, 0],
        [0.04, -0.12, 0],
        fill_color="#2D6A4F", fill_opacity=0.95, stroke_width=0,
    )
    # Atmosphere rim
    atmosphere = Circle(
        radius=0.25,
        stroke_color="#72EFDD",
        stroke_width=2.0,
        stroke_opacity=0.65,
        fill_opacity=0,
    )

    earth.add(ocean, c1, c2, c3, atmosphere)
    return earth


def create_spacetime_grid(sun_center, warped=False):
    """
    Creates a coordinate mesh representing the spatial metric.
    In the warped version, lines bend inward toward the mass, visualizing
    the contraction of spatial geometry without rubber-sheet funnel artifacts.
    """
    grid = VGroup()
    x_coords = np.linspace(-3.6, 3.6, 17)
    y_coords = np.linspace(-4.4, 2.2, 15)

    def deform_point(pt):
        if not warped:
            return pt
        diff = pt - sun_center
        r = np.linalg.norm(diff[:2])
        if r < 0.25:
            r = 0.25
        # Coordinate contraction toward mass
        dr = -0.32 * diff / (r**1.45 + 0.65)
        return pt + np.array([dr[0], dr[1], 0.0])

    # Horizontal coordinate lines
    for y in y_coords:
        pts = [deform_point(np.array([x, y, 0.0])) for x in np.linspace(-3.6, 3.6, 36)]
        color = "#1D3557" if not warped else "#2A6F97"
        opacity = 0.35 if not warped else 0.50
        grid.add(VMobject().set_points_smoothly(pts).set_stroke(color, width=1.3, opacity=opacity))

    # Vertical coordinate lines
    for x in x_coords:
        pts = [deform_point(np.array([x, y, 0.0])) for y in np.linspace(-4.4, 2.2, 36)]
        color = "#1D3557" if not warped else "#2A6F97"
        opacity = 0.35 if not warped else 0.50
        grid.add(VMobject().set_points_smoothly(pts).set_stroke(color, width=1.3, opacity=opacity))

    return grid


# -------------------------------------------------------------------------
# 3. Main Master Scene
# -------------------------------------------------------------------------
class GeodesicOrbitMaster(Scene):
    def construct(self):
        # Anchor positions tuned for 9:16 vertical view
        SUN_POS = np.array([0.0, -1.1, 0.0])
        TEXT_ZONE_Y = 5.2

        # -----------------------------------------------------------------
        # BACKGROUND & CELESTIAL INITIALIZATION
        # -----------------------------------------------------------------
        starfield = VGroup()
        np.random.seed(42)
        for _ in range(85):
            sx = np.random.uniform(-4.3, 4.3)
            sy = np.random.uniform(-7.8, 7.8)
            s_rad = np.random.uniform(0.015, 0.035)
            s_alpha = np.random.uniform(0.2, 0.7)
            starfield.add(Dot(point=[sx, sy, 0], radius=s_rad, color=WHITE).set_opacity(s_alpha))
        self.add(starfield)

        sun = create_sun(SUN_POS)
        earth = create_earth_mobject()

        # Orbital trail path from precalculated points
        orbit_pts = [pt + SUN_POS for pt in R_TABLE]
        orbit_pts.append(orbit_pts[0])
        orbit_path = VMobject()
        orbit_path.set_points_smoothly(orbit_pts)
        orbit_path.set_stroke(color="#4A5568", width=1.5, opacity=0.45)

        self.add(orbit_path, sun)

        # Simulation clock tracker
        sim_clock = ValueTracker(0.0)

        # Day/Night terminator that automatically rotates away from Sun
        terminator = Sector(
            radius=0.23,
            angle=PI,
            start_angle=0,
            fill_color="#02040A",
            fill_opacity=0.62,
            stroke_width=0,
        )

        def update_earth_rig(mob):
            r_rel, _, _ = get_orbital_state(sim_clock.get_value())
            pos = r_rel + SUN_POS
            mob.move_to(pos)
            # Continents rotate slowly as Earth orbits
            mob[1:4].rotate(0.018, about_point=pos)

        def update_terminator(mob):
            r_rel, _, _ = get_orbital_state(sim_clock.get_value())
            pos = r_rel + SUN_POS
            to_sun = SUN_POS - pos
            angle_to_sun = np.arctan2(to_sun[1], to_sun[0])
            mob.move_to(pos)
            # Orient dark semi-circle facing away from Sun
            mob.become(
                Sector(
                    radius=0.232,
                    angle=PI,
                    start_angle=angle_to_sun + PI / 2,
                    fill_color="#02040A",
                    fill_opacity=0.62,
                    stroke_width=0,
                ).move_to(pos)
            )

        earth.add_updater(update_earth_rig)
        terminator.add_updater(update_terminator)
        self.add(earth, terminator)

        # =================================================================
        # SCENE 1 — THE HOOK (0.0s - 6.0s)
        # =================================================================
        hook_1 = Text(
            "Why doesn't Earth\nfall into the Sun?",
            font_size=40,
            font="sans-serif",
            weight=BOLD,
            color="#FFFFFF",
            line_spacing=1.2,
        ).move_to([0, TEXT_ZONE_Y, 0])

        self.play(FadeIn(hook_1, shift=UP * 0.3), run_time=1.0)
        self.play(sim_clock.animate.increment_value(1.8), run_time=1.8, rate_func=linear)

        hook_2 = Text(
            "It actually is.",
            font_size=44,
            font="sans-serif",
            weight=BOLD,
            color="#FF5964",
        ).move_to([0, TEXT_ZONE_Y, 0])

        self.play(ReplacementTransform(hook_1, hook_2), run_time=0.7)
        self.play(sim_clock.animate.increment_value(1.4), run_time=1.4, rate_func=linear)

        hook_3 = Text(
            "But there's a deeper\nway to describe it.",
            font_size=36,
            font="sans-serif",
            color="#A8DADC",
            line_spacing=1.2,
        ).move_to([0, TEXT_ZONE_Y, 0])

        self.play(ReplacementTransform(hook_2, hook_3), run_time=0.7)
        self.play(sim_clock.animate.increment_value(1.4), run_time=1.4, rate_func=linear)

        # =================================================================
        # SCENE 2 — NEWTONIAN ORBIT & VECTORS (6.0s - 14.0s)
        # =================================================================
        v_vector = always_redraw(
            lambda: Arrow(
                start=earth.get_center(),
                end=earth.get_center() + 0.32 * get_orbital_state(sim_clock.get_value())[1],
                buff=0,
                color="#00F5D4",
                stroke_width=3.5,
                max_tip_length_to_length_ratio=0.35,
            )
        )

        a_vector = always_redraw(
            lambda: Arrow(
                start=earth.get_center(),
                end=earth.get_center() + 0.38 * get_orbital_state(sim_clock.get_value())[2],
                buff=0,
                color="#FF9F1C",
                stroke_width=3.5,
                max_tip_length_to_length_ratio=0.35,
            )
        )

        v_tag = always_redraw(
            lambda: Text("v", font_size=24, color="#00F5D4", weight=BOLD).next_to(
                v_vector.get_end(), UP * 0.4 + RIGHT * 0.2
            )
        )

        a_tag = always_redraw(
            lambda: Text("g", font_size=24, color="#FF9F1C", weight=BOLD).next_to(
                a_vector.get_end(), DOWN * 0.3 + LEFT * 0.3
            )
        )

        newton_title = Text(
            "NEWTONIAN PICTURE",
            font_size=32,
            font="sans-serif",
            weight=BOLD,
            color="#E0E1DD",
        ).move_to([0, TEXT_ZONE_Y + 0.8, 0])

        newton_sub = Text(
            "Tangential velocity moves sideways.\nGravity pulls inward continually.",
            font_size=26,
            font="sans-serif",
            color="#A8DADC",
            line_spacing=1.3,
        ).move_to([0, TEXT_ZONE_Y - 0.2, 0])

        self.play(
            ReplacementTransform(hook_3, newton_title),
            FadeIn(newton_sub, shift=UP * 0.2),
            FadeIn(v_vector),
            FadeIn(a_vector),
            FadeIn(v_tag),
            FadeIn(a_tag),
            run_time=1.0,
        )

        # Orbit through periapsis showing continuous vector realignment
        self.play(sim_clock.animate.increment_value(4.2), run_time=4.2, rate_func=linear)

        # =================================================================
        # SCENE 3 — WHY EARTH DOESN'T HIT THE SUN (14.0s - 21.0s)
        # =================================================================
        r_snap, v_snap, _ = get_orbital_state(sim_clock.get_value())
        curr_pos = r_snap + SUN_POS
        v_unit = v_snap / np.linalg.norm(v_snap)

        straight_line = DashedLine(
            start=curr_pos - v_unit * 0.5,
            end=curr_pos + v_unit * 3.2,
            dash_length=0.12,
            color="#00F5D4",
            stroke_width=2.5,
        )

        straight_label = Text(
            "Without gravity:\nstraight inertial drift",
            font_size=22,
            font="sans-serif",
            color="#00F5D4",
        ).next_to(straight_line.get_end(), RIGHT, buff=0.15)

        why_text = Text(
            "Earth is constantly falling toward the Sun…\n…while constantly moving sideways.",
            font_size=26,
            font="sans-serif",
            color="#FFFFFF",
            line_spacing=1.3,
        ).move_to([0, TEXT_ZONE_Y - 0.2, 0])

        self.play(
            ReplacementTransform(newton_sub, why_text),
            FadeIn(straight_line),
            FadeIn(straight_label),
            sim_clock.animate.increment_value(0.5),
            run_time=1.2,
            rate_func=linear,
        )

        self.play(sim_clock.animate.increment_value(2.6), run_time=2.6, rate_func=linear)
        self.play(FadeOut(straight_line), FadeOut(straight_label), run_time=0.6)

        # =================================================================
        # SCENE 4 — INTRODUCE GEODESIC & CURVED GEOMETRY (21.0s - 29.0s)
        # =================================================================
        flat_grid = create_spacetime_grid(SUN_POS, warped=False)
        curved_grid = create_spacetime_grid(SUN_POS, warped=True)

        gr_title = Text(
            "GENERAL RELATIVITY",
            font_size=32,
            font="sans-serif",
            weight=BOLD,
            color="#F4A261",
        ).move_to([0, TEXT_ZONE_Y + 0.8, 0])

        gr_sub1 = Text(
            "There is no gravitational pull.",
            font_size=30,
            font="sans-serif",
            weight=BOLD,
            color="#E76F51",
        ).move_to([0, TEXT_ZONE_Y, 0])

        # Detach always_redraw updaters so opacity fades smoothly instead of popping
        for m in (v_vector, a_vector, v_tag, a_tag):
            m.clear_updaters()

        self.play(
            FadeOut(v_vector),
            FadeOut(a_vector),
            FadeOut(v_tag),
            FadeOut(a_tag),
            ReplacementTransform(newton_title, gr_title),
            ReplacementTransform(why_text, gr_sub1),
            FadeIn(flat_grid, run_time=1.2),
            sim_clock.animate.increment_value(1.2),
            run_time=1.2,
            rate_func=linear,
        )

        gr_sub2 = Text(
            "The Sun's mass warps spacetime.\nEarth follows the straightest possible path.",
            font_size=25,
            font="sans-serif",
            color="#A8DADC",
            line_spacing=1.3,
        ).move_to([0, TEXT_ZONE_Y - 0.1, 0])

        # Morph flat grid into curved coordinate metric
        self.play(
            ReplacementTransform(flat_grid, curved_grid),
            ReplacementTransform(gr_sub1, gr_sub2),
            sim_clock.animate.increment_value(2.0),
            run_time=2.0,
            rate_func=linear,
        )

        geodesic_badge = Text(
            "Earth follows a GEODESIC",
            font_size=32,
            font="sans-serif",
            weight=BOLD,
            color="#FFE66D",
        ).move_to([0, TEXT_ZONE_Y - 0.1, 0])

        # Emphasize the orbit path as a geodesic
        orbit_glow = orbit_path.copy().set_stroke(color="#FFE66D", width=3.5, opacity=0.9)

        self.play(
            ReplacementTransform(gr_sub2, geodesic_badge),
            FadeIn(orbit_glow),
            sim_clock.animate.increment_value(2.2),
            run_time=2.2,
            rate_func=linear,
        )
        self.play(FadeOut(orbit_glow), run_time=0.8)

        # =================================================================
        # SCENE 5 — THE CONCEPTUAL BRIDGE (29.0s - 35.0s)
        # =================================================================
        card_box = RoundedRectangle(
            corner_radius=0.2,
            height=3.8,
            width=7.6,
            fill_color="#0A1128",
            fill_opacity=0.92,
            stroke_color="#457B9D",
            stroke_width=1.5,
        ).move_to([0, TEXT_ZONE_Y - 0.4, 0])

        c_newton_head = Text("NEWTONIAN DESCRIPTION", font_size=21, color="#00F5D4", weight=BOLD)
        c_newton_body = Text("Mass  →  Gravitational Force  →  Curved Acceleration", font_size=19, color="#E0E1DD")

        c_arrow = MathTex(r"\Downarrow", font_size=30, color="#A8DADC")

        c_gr_head = Text("EINSTEINIAN DESCRIPTION", font_size=21, color="#FFE66D", weight=BOLD)
        c_gr_body = Text("Mass  →  Curved Spacetime  →  Geodesic Free Fall", font_size=19, color="#E0E1DD")

        card_content = VGroup(
            c_newton_head,
            c_newton_body,
            c_arrow,
            c_gr_head,
            c_gr_body,
        ).arrange(DOWN, buff=0.22).move_to(card_box.get_center())

        comparison_card = VGroup(card_box, card_content)

        self.play(
            FadeOut(gr_title),
            FadeOut(geodesic_badge),
            FadeIn(comparison_card, shift=UP * 0.3),
            sim_clock.animate.increment_value(1.2),
            run_time=1.2,
            rate_func=linear,
        )

        self.play(sim_clock.animate.increment_value(3.6), run_time=3.6, rate_func=linear)

        # =================================================================
        # SCENE 6 — MATHEMATICAL FORMULATION (35.0s - 41.0s)
        # =================================================================
        eq_newton = MathTex(
            r"\mathbf{a} = -\frac{GM}{r^3}\mathbf{r}",
            font_size=36,
            color="#00F5D4",
        )
        eq_newton_label = Text("External Force Required", font_size=20, color="#A8DADC")
        newton_group = VGroup(eq_newton, eq_newton_label).arrange(DOWN, buff=0.2).move_to(card_box.get_center())

        self.play(
            ReplacementTransform(card_content, newton_group),
            sim_clock.animate.increment_value(1.0),
            run_time=1.0,
            rate_func=linear,
        )
        self.play(sim_clock.animate.increment_value(1.5), run_time=1.5, rate_func=linear)

        eq_geodesic = MathTex(
            r"\frac{d^2 x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta} \frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0",
            font_size=32,
            color="#FFE66D",
        )
        eq_geodesic_label = Text(
            "Zero Force: Pure Geometry of Spacetime",
            font_size=20,
            color="#A8DADC",
        )
        gr_eq_group = VGroup(eq_geodesic, eq_geodesic_label).arrange(DOWN, buff=0.25).move_to(card_box.get_center())

        self.play(
            ReplacementTransform(newton_group, gr_eq_group),
            sim_clock.animate.increment_value(1.0),
            run_time=1.0,
            rate_func=linear,
        )
        self.play(sim_clock.animate.increment_value(2.0), run_time=2.0, rate_func=linear)

        # =================================================================
        # SCENE 7 — FINAL PAYOFF & CONCLUSION (41.0s - 48.0s)
        # =================================================================
        # Single clean fadeout: comparison_card now contains gr_eq_group via nested ReplacementTransforms
        self.play(
            FadeOut(comparison_card),
            run_time=0.8,
        )

        final_line1 = Text(
            "Earth isn't being pulled.",
            font_size=38,
            font="sans-serif",
            weight=BOLD,
            color="#FFFFFF",
        ).move_to([0, TEXT_ZONE_Y + 0.5, 0])

        final_line2 = Text(
            "It is freely falling through\ncurved spacetime.",
            font_size=32,
            font="sans-serif",
            color="#72EFDD",
            line_spacing=1.3,
        ).move_to([0, TEXT_ZONE_Y - 0.4, 0])

        self.play(
            FadeIn(final_line1, shift=UP * 0.2),
            sim_clock.animate.increment_value(1.0),
            run_time=1.0,
            rate_func=linear,
        )
        self.play(
            FadeIn(final_line2, shift=UP * 0.2),
            sim_clock.animate.increment_value(2.0),
            run_time=2.0,
            rate_func=linear,
        )

        # Final minimalist synthesis banner
        verdict = Text(
            "ORBIT = FREE FALL ALONG A GEODESIC",
            font_size=24,
            font="sans-serif",
            weight=BOLD,
            color="#FFD166",
        ).move_to([0, -3.8, 0])

        self.play(
            FadeIn(verdict, shift=UP * 0.15),
            sim_clock.animate.increment_value(2.5),
            run_time=2.5,
            rate_func=linear,
        )

        # Gentle cinematic fadeout
        self.play(
            FadeOut(final_line1),
            FadeOut(final_line2),
            FadeOut(verdict),
            FadeOut(curved_grid),
            FadeOut(orbit_path),
            FadeOut(sun),
            FadeOut(earth),
            FadeOut(terminator),
            FadeOut(starfield),
            run_time=1.5,
        )
        self.wait(0.5)
