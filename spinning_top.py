from manim import *
import numpy as np

# -----------------------------------------------------------------------------
# Configuration: Vertical 9:16 format (1080x1920, 60 FPS)
# -----------------------------------------------------------------------------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0
config.frame_rate = 60
config.background_color = "#0B0F17"


# -----------------------------------------------------------------------------
# 3D Vector & Projection Utilities (Perspective Projection)
# -----------------------------------------------------------------------------
def project_3d(point_3d, cam_phi, cam_theta, cam_dist=13.0, scale=1.35, center=(0, -2.2, 0)):
    x, y, z = point_3d
    # Azimuth rotation around vertical z-axis
    x1 = x * np.cos(cam_theta) + y * np.sin(cam_theta)
    y1 = -x * np.sin(cam_theta) + y * np.cos(cam_theta)
    z1 = z

    # Elevation rotation around horizontal x-axis
    x2 = x1
    y2 = y1 * np.cos(cam_phi) + z1 * np.sin(cam_phi)
    z2 = -y1 * np.sin(cam_phi) + z1 * np.cos(cam_phi)

    # Perspective foreshortening
    factor = cam_dist / (cam_dist - z2)
    xp = x2 * factor * scale + center[0]
    yp = y2 * factor * scale + center[1]
    return np.array([xp, yp, 0.0])


# -----------------------------------------------------------------------------
# Main Scene
# -----------------------------------------------------------------------------
class SpinningTopPhysics(Scene):
    def construct(self):
        # ---------------------------------------------------------------------
        # Precompute Instability Trajectory via NumPy
        # ---------------------------------------------------------------------
        fall_duration = 5.6
        dt_sim = 0.016
        t_fall = np.arange(0, fall_duration + 0.1, dt_sim)
        n_fall_steps = len(t_fall)

        fall_theta = np.zeros(n_fall_steps)
        fall_phi = np.zeros(n_fall_steps)
        fall_spin = np.zeros(n_fall_steps)

        th = 24.0 * np.pi / 180.0
        ph = 0.0
        base_prec_rate = 1.75

        for i, t in enumerate(t_fall):
            sp = 35.0 * np.exp(-0.38 * t)
            if t < 1.0:
                th_val = 24.0 * np.pi / 180.0
                pr = base_prec_rate
            else:
                elapsed = t - 1.0
                pr = base_prec_rate + 1.6 * (elapsed ** 1.3)
                wobble = 0.09 * np.sin(16.0 * elapsed) * (elapsed ** 0.8)
                runaway = 0.085 * (elapsed ** 2.3)
                th_val = min(78.0 * np.pi / 180.0, 24.0 * np.pi / 180.0 + runaway + wobble)

            ph += pr * dt_sim
            fall_theta[i] = th_val
            fall_phi[i] = ph
            fall_spin[i] = sp

        # ---------------------------------------------------------------------
        # State Trackers
        # ---------------------------------------------------------------------
        theta_tracker = ValueTracker(24.0 * np.pi / 180.0)
        phi_tracker = ValueTracker(0.0)
        spin_phase_tracker = ValueTracker(0.0)
        cam_theta_tracker = ValueTracker(-58.0 * np.pi / 180.0)
        cam_phi_tracker = ValueTracker(66.0 * np.pi / 180.0)

        # Visibility flags
        show_gravity = ValueTracker(0.0)
        show_r_vec = ValueTracker(0.0)
        show_torque = ValueTracker(0.0)
        show_L_vec = ValueTracker(0.0)
        show_dL_vec = ValueTracker(0.0)
        show_trace = ValueTracker(0.0)
        L_scale_tracker = ValueTracker(1.0)

        # Add state mobjects to the scene
        self.add(spin_phase_tracker, phi_tracker, cam_theta_tracker)

        # Pre-instantiate MathTex label templates to prevent font missing errors
        r_lbl_template = MathTex(r"\mathbf{r}", font_size=26, color="#10B981")
        fg_lbl_template = MathTex(r"\mathbf{F}_g", font_size=26, color="#F43F5E")
        tau_lbl_template = MathTex(r"\boldsymbol{\tau}", font_size=32, color="#F59E0B")
        L_lbl_template = MathTex(r"\mathbf{L}", font_size=32, color="#00F0FF")
        dL_lbl_template = MathTex(r"d\mathbf{L} = \boldsymbol{\tau}\,dt", font_size=24, color="#FDE047")

        # ---------------------------------------------------------------------
        # Dynamic Top Mesh Generator
        # ---------------------------------------------------------------------
        def create_top_mobject():
            th = theta_tracker.get_value()
            ph = phi_tracker.get_value()
            sp = spin_phase_tracker.get_value()
            c_th = cam_theta_tracker.get_value()
            c_ph = cam_phi_tracker.get_value()

            nx = np.sin(th) * np.cos(ph)
            ny = np.sin(th) * np.sin(ph)
            nz = np.cos(th)
            n_hat = np.array([nx, ny, nz])

            ref = np.array([0.0, 0.0, 1.0])
            if np.abs(np.dot(n_hat, ref)) > 0.92:
                ref = np.array([1.0, 0.0, 0.0])
            u_hat = np.cross(n_hat, ref)
            u_hat /= np.linalg.norm(u_hat)
            v_hat = np.cross(n_hat, u_hat)
            v_hat /= np.linalg.norm(v_hat)

            p_pivot = np.array([0.0, 0.0, 0.0])
            l_cm = 1.95
            l_rotor = 1.80
            l_shaft = 3.40
            r_rotor = 1.25

            p_cm = l_cm * n_hat
            p_rotor = l_rotor * n_hat
            p_tip = l_shaft * n_hat

            mobs = VGroup()

            # Ground grid
            ground_group = VGroup()
            for r in [1.2, 2.4, 3.6]:
                ring_pts = [
                    project_3d(np.array([r * np.cos(a), r * np.sin(a), 0.0]), c_ph, c_th)
                    for a in np.linspace(0, 2 * np.pi, 48)
                ]
                ring = VMobject(stroke_color="#1E293B", stroke_width=1.5, stroke_opacity=0.45)
                ring.set_points_smoothly(ring_pts)
                ground_group.add(ring)

            for a in np.linspace(0, 2 * np.pi, 8, endpoint=False):
                p_out = np.array([3.6 * np.cos(a), 3.6 * np.sin(a), 0.0])
                line = Line(
                    project_3d(p_pivot, c_ph, c_th),
                    project_3d(p_out, c_ph, c_th),
                    stroke_color="#1E293B",
                    stroke_width=1.2,
                    stroke_opacity=0.35,
                )
                ground_group.add(line)

            p_seat_2d = project_3d(p_pivot, c_ph, c_th)
            pivot_pad = Dot(p_seat_2d, radius=0.08, color="#64748B")
            ground_group.add(pivot_pad)
            mobs.add(ground_group)

            # Lower shaft
            p_rot_2d = project_3d(p_rotor, c_ph, c_th)
            p_tip_2d = project_3d(p_tip, c_ph, c_th)

            lower_shaft = Line(
                p_seat_2d, p_rot_2d,
                stroke_color="#94A3B8",
                stroke_width=4.5,
            )
            mobs.add(lower_shaft)

            # Rotor Disc
            n_seg = 36
            angles = np.linspace(0, 2 * np.pi, n_seg, endpoint=False)
            disc_rim_3d = [
                p_rotor + r_rotor * (np.cos(a) * u_hat + np.sin(a) * v_hat)
                for a in angles
            ]
            disc_rim_2d = [project_3d(p, c_ph, c_th) for p in disc_rim_3d]

            rotor_body = Polygon(
                *disc_rim_2d,
                fill_color="#0F172A",
                fill_opacity=0.82,
                stroke_color="#38BDF8",
                stroke_width=2.5,
            )
            mobs.add(rotor_body)

            # Spokes
            for k in range(4):
                psi = sp + k * (np.pi / 2.0)
                spoke_rim_3d = p_rotor + r_rotor * (np.cos(psi) * u_hat + np.sin(psi) * v_hat)
                spoke = Line(
                    p_rot_2d,
                    project_3d(spoke_rim_3d, c_ph, c_th),
                    stroke_color="#BAE6FD",
                    stroke_width=2.0,
                    stroke_opacity=0.85,
                )
                mobs.add(spoke)

            hub = Dot(p_rot_2d, radius=0.09, color="#E2E8F0")
            mobs.add(hub)

            # Upper shaft
            upper_shaft = Line(
                p_rot_2d, p_tip_2d,
                stroke_color="#CBD5E1",
                stroke_width=4.5,
            )
            mobs.add(upper_shaft)

            tip_cap = Dot(p_tip_2d, radius=0.06, color="#FFFFFF")
            mobs.add(tip_cap)

            # Educational Vectors
            p_cm_2d = project_3d(p_cm, c_ph, c_th)

            cm_dot = Dot(p_cm_2d, radius=0.085, color="#F59E0B")
            cm_glow = Dot(p_cm_2d, radius=0.15, color="#F59E0B", fill_opacity=0.3)
            mobs.add(cm_glow, cm_dot)

            # r vector
            w_r = show_r_vec.get_value()
            if w_r > 0.01:
                r_arrow = Arrow(
                    p_seat_2d, p_cm_2d,
                    buff=0.0,
                    color="#10B981",
                    stroke_width=4.5 * w_r,
                    max_tip_length_to_length_ratio=0.18,
                )
                r_lbl = r_lbl_template.copy()
                r_lbl.next_to(r_arrow.get_center(), LEFT, buff=0.15)
                mobs.add(r_arrow, r_lbl)

            # Gravity F_g
            w_g = show_gravity.get_value()
            if w_g > 0.01:
                p_fg_3d = p_cm + np.array([0.0, 0.0, -1.65])
                fg_arrow = Arrow(
                    p_cm_2d,
                    project_3d(p_fg_3d, c_ph, c_th),
                    buff=0.0,
                    color="#F43F5E",
                    stroke_width=4.8 * w_g,
                    max_tip_length_to_length_ratio=0.22,
                )
                fg_lbl = fg_lbl_template.copy()
                fg_lbl.next_to(fg_arrow.get_end(), DOWN, buff=0.12)
                mobs.add(fg_arrow, fg_lbl)

            # Torque tau
            w_tau = show_torque.get_value()
            tau_dir = np.array([-np.sin(ph), np.cos(ph), 0.0])
            tau_len = 1.9
            p_tau_3d = p_cm + tau_len * tau_dir

            if w_tau > 0.01:
                tau_arrow = Arrow(
                    p_cm_2d,
                    project_3d(p_tau_3d, c_ph, c_th),
                    buff=0.0,
                    color="#F59E0B",
                    stroke_width=5.0 * w_tau,
                    max_tip_length_to_length_ratio=0.22,
                )
                tau_lbl = tau_lbl_template.copy()
                tau_lbl.next_to(tau_arrow.get_end(), RIGHT, buff=0.12)
                mobs.add(tau_arrow, tau_lbl)

            # L vector
            w_L = show_L_vec.get_value()
            l_mag = 3.6 * L_scale_tracker.get_value()
            p_L_3d = p_cm + l_mag * n_hat

            if w_L > 0.01:
                p_L_2d = project_3d(p_L_3d, c_ph, c_th)
                L_arrow = Arrow(
                    p_cm_2d,
                    p_L_2d,
                    buff=0.0,
                    color="#00F0FF",
                    stroke_width=5.5 * w_L,
                    max_tip_length_to_length_ratio=0.18,
                )
                L_lbl = L_lbl_template.copy()
                L_lbl.next_to(p_L_2d, UP + RIGHT, buff=0.12)
                mobs.add(L_arrow, L_lbl)

                # dL vector
                w_dL = show_dL_vec.get_value()
                if w_dL > 0.01:
                    p_dL_3d = p_L_3d + 1.25 * tau_dir
                    dL_arrow = Arrow(
                        p_L_2d,
                        project_3d(p_dL_3d, c_ph, c_th),
                        buff=0.0,
                        color="#FDE047",
                        stroke_width=4.2 * w_dL,
                        max_tip_length_to_length_ratio=0.26,
                    )
                    dL_lbl = dL_lbl_template.copy()
                    dL_lbl.next_to(dL_arrow.get_end(), RIGHT, buff=0.1)
                    mobs.add(dL_arrow, dL_lbl)

            # Precession circular trace
            w_trace = show_trace.get_value()
            if w_trace > 0.01:
                z_tip_trace = p_cm[2] + l_mag * np.cos(th)
                r_trace = l_mag * np.sin(th)
                trace_pts = [
                    project_3d(np.array([r_trace * np.cos(a), r_trace * np.sin(a), z_tip_trace]), c_ph, c_th)
                    for a in np.linspace(0, 2 * np.pi, 64)
                ]
                trace_curve = VMobject(stroke_color="#38BDF8", stroke_width=2.5 * w_trace, stroke_opacity=0.65)
                trace_curve.set_points_smoothly(trace_pts)
                mobs.add(trace_curve)

            return mobs

        top_mesh = always_redraw(create_top_mobject)
        self.add(top_mesh)

        # Uses exact parameter name 'dt' with default dt=0 to ensure compatibility with Manim CE
        def spin_updater_func(mob, dt=0):
            mob.increment_value(32.0 * dt)

        spin_phase_tracker.add_updater(spin_updater_func, call_updater=False)

        # ---------------------------------------------------------------------
        # Scene 1: Hook (0.0s – 6.0s)
        # ---------------------------------------------------------------------
        hook_title = Text("Gravity is pulling it down.", font_size=36, color="#F1F5F9", weight=BOLD)
        hook_title.move_to(UP * 6.2)

        hook_question = Text("So why doesn't it fall?", font_size=42, color="#FDE047", weight=BOLD)
        hook_question.next_to(hook_title, DOWN, buff=0.35)

        self.play(FadeIn(hook_title, shift=DOWN * 0.3), run_time=1.0)
        self.wait(1.0)
        self.play(FadeIn(hook_question, scale=1.08), run_time=1.0)
        self.wait(2.2)
        self.play(FadeOut(hook_title), FadeOut(hook_question), run_time=0.8)

        # ---------------------------------------------------------------------
        # Scene 2: Gravity & Non-Zero Torque (6.0s – 13.2s)
        # ---------------------------------------------------------------------
        sec2_header = Text("1. Gravity Creates Torque", font_size=34, color="#94A3B8", weight=BOLD)
        sec2_header.move_to(UP * 6.5)

        tau_formula = MathTex(r"\boldsymbol{\tau} = \mathbf{r} \times \mathbf{F}_g", font_size=46, color="#F59E0B")
        tau_formula.next_to(sec2_header, DOWN, buff=0.35)

        tau_insight = Text("Torque is NOT zero — it acts horizontally!", font_size=26, color="#CBD5E1")
        tau_insight.next_to(tau_formula, DOWN, buff=0.3)

        self.play(FadeIn(sec2_header, shift=DOWN * 0.2), run_time=0.6)
        self.play(
            show_r_vec.animate.set_value(1.0),
            show_gravity.animate.set_value(1.0),
            run_time=1.2,
        )
        self.play(FadeIn(tau_formula, shift=UP * 0.2), run_time=0.8)
        self.play(
            show_torque.animate.set_value(1.0),
            FadeIn(tau_insight),
            run_time=1.2,
        )
        self.wait(2.8)
        self.play(FadeOut(tau_insight), FadeOut(sec2_header), run_time=0.6)

        # ---------------------------------------------------------------------
        # Scene 3: Angular Momentum (13.2s – 20.7s)
        # ---------------------------------------------------------------------
        sec3_header = Text("2. Rapid Spin = Massive Angular Momentum L", font_size=28, color="#38BDF8", weight=BOLD)
        sec3_header.move_to(UP * 6.5)

        law_formula = MathTex(r"\boldsymbol{\tau} = \frac{d\mathbf{L}}{dt}", font_size=48, color="#FDE047")
        law_formula.next_to(sec3_header, DOWN, buff=0.35)

        key_insight = VGroup(
            Text("Torque doesn't pull L down.", font_size=28, color="#94A3B8"),
            Text("It steers L sideways!", font_size=34, color="#00F0FF", weight=BOLD),
        ).arrange(DOWN, buff=0.2).next_to(law_formula, DOWN, buff=0.35)

        self.play(
            FadeOut(tau_formula),
            FadeIn(sec3_header),
            run_time=0.6,
        )
        self.play(show_L_vec.animate.set_value(1.0), run_time=1.0)
        self.play(FadeIn(law_formula, scale=1.05), run_time=0.8)
        self.play(
            show_dL_vec.animate.set_value(1.0),
            FadeIn(key_insight),
            run_time=1.4,
        )
        self.wait(3.0)
        self.play(
            FadeOut(sec3_header),
            FadeOut(law_formula),
            FadeOut(key_insight),
            run_time=0.7,
        )

        # ---------------------------------------------------------------------
        # Scene 4: Precession (20.7s – 30.1s)
        # ---------------------------------------------------------------------
        prec_badge = Text("PRECESSION", font_size=46, color="#38BDF8", weight=BOLD)
        prec_badge.move_to(UP * 6.4)

        prec_sub = Text("dL continuously turns the axis horizontally", font_size=25, color="#94A3B8")
        prec_sub.next_to(prec_badge, DOWN, buff=0.25)

        prec_rate_formula = VGroup(
            Text("Precession Rate:", font_size=26, color="#94A3B8"),
            MathTex(r"\Omega_p = \frac{\tau}{L}", font_size=32, color="#F1F5F9")
        ).arrange(RIGHT, buff=0.25).next_to(prec_sub, DOWN, buff=0.25)

        self.play(
            FadeIn(prec_badge, shift=DOWN * 0.2),
            FadeIn(prec_sub),
            FadeIn(prec_rate_formula),
            show_trace.animate.set_value(1.0),
            run_time=0.8,
        )

        # Native linear precession animation (eliminates extra updater logic)
        self.play(
            phi_tracker.animate.increment_value(1.55 * 8.0),
            cam_theta_tracker.animate.increment_value(0.08 * 8.0),
            run_time=8.0,
            rate_func=linear,
        )

        self.play(
            FadeOut(prec_badge),
            FadeOut(prec_sub),
            FadeOut(prec_rate_formula),
            show_dL_vec.animate.set_value(0.0),
            run_time=0.6,
        )

        # ---------------------------------------------------------------------
        # Scene 5: Slow Spin & Destabilization (30.1s – 37.0s)
        # ---------------------------------------------------------------------
        slow_title = Text("When spin slows down...", font_size=36, color="#F43F5E", weight=BOLD)
        slow_title.move_to(UP * 6.3)

        slow_sub = Text("L shrinks   →   Gyroscopic stability is lost", font_size=26, color="#CBD5E1")
        slow_sub.next_to(slow_title, DOWN, buff=0.28)

        self.play(
            FadeIn(slow_title, shift=DOWN * 0.2),
            FadeIn(slow_sub),
            run_time=0.8,
        )

        # Stop regular spin updater
        spin_phase_tracker.remove_updater(spin_updater_func)

        # Smooth continuous interpolation of fall physics
        fall_clock = ValueTracker(0.0)
        self.add(fall_clock)

        def fall_playback_updater(mob, dt=0):
            mob.increment_value(dt)
            t_cur = mob.get_value()
            if t_cur <= fall_duration:
                th_val = float(np.interp(t_cur, t_fall, fall_theta))
                ph_val = float(np.interp(t_cur, t_fall, fall_phi))
                sp_val = float(np.interp(t_cur, t_fall, fall_spin))

                theta_tracker.set_value(th_val)
                phi_tracker.set_value(ph_val)
                spin_phase_tracker.increment_value(sp_val * dt)
                norm_spin = max(0.1, sp_val / 35.0)
                L_scale_tracker.set_value(norm_spin)

        fall_clock.add_updater(fall_playback_updater, call_updater=False)
        self.wait(fall_duration)
        fall_clock.remove_updater(fall_playback_updater)
        self.wait(0.4)

        # ---------------------------------------------------------------------
        # Final Frame: Core Physics Insight (37.0s – 45.5s)
        # ---------------------------------------------------------------------
        self.play(
            FadeOut(top_mesh),
            FadeOut(slow_title),
            FadeOut(slow_sub),
            run_time=1.0,
        )

        line1 = Text("Gravity doesn't disappear.", font_size=34, color="#94A3B8")
        line2 = Text("It changes angular momentum.", font_size=40, color="#FDE047", weight=BOLD)
        line3 = Text("That's why a spinning top stays upright.", font_size=34, color="#F1F5F9", weight=BOLD)

        final_group = VGroup(line1, line2, line3).arrange(DOWN, buff=0.55)
        final_group.move_to(ORIGIN)

        self.play(FadeIn(line1, shift=DOWN * 0.2), run_time=0.9)
        self.wait(0.4)
        self.play(FadeIn(line2, scale=1.06), run_time=1.1)
        self.wait(0.5)
        self.play(FadeIn(line3, shift=UP * 0.2), run_time=1.0)
        self.wait(2.8)

        self.play(FadeOut(final_group), run_time=0.8)
