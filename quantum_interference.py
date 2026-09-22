"""
Quantum Interference: How Individual Particles Form an Interference Pattern
===========================================================================
A mathematically self-consistent 9:16 vertical explainer for Manim Community Edition.

Physics & Simulation Notes:
---------------------------
1. A single de Broglie wavelength (LAMBDA = 0.75) drives both:
   - The spatial wave functions plotted between slits and detector.
   - The statistical probability distribution sampling detections on screen.
2. The dark fringe position is computed numerically from the exact path-length
   difference: Delta_r(x) = |r1(x) - r2(x)| = LAMBDA / 2.
3. In two-slit mode, particles are NOT animated taking a classical resolved
   trajectory through a single slit. Both paths are engaged by the quantum
   amplitude before a localized collapse occurs at the detector.
4. Single-slit diffraction uses a Gaussian envelope modeling the central lobe
   of the aperture diffraction pattern without confusing secondary maxima.
"""

from manim import *
import numpy as np

# Set vertical 9:16 mobile format (1080x1920)
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0


class QuantumInterferenceScene(Scene):
    def construct(self):
        np.random.seed(42)

        # -----------------------------------------------------------
        # GLOBAL PHYSICAL PARAMETERS (Self-consistent geometry & wave)
        # -----------------------------------------------------------
        LAMBDA = 0.75          # Global de Broglie wavelength
        SLIT_SEP = 1.8         # Distance between slit centers (d)
        Y_SOURCE = 5.0         # Source nozzle y-coordinate
        Y_BARRIER = 2.4        # Barrier y-coordinate
        Y_SCREEN = 0.2         # Detector screen y-coordinate
        L = Y_BARRIER - Y_SCREEN  # Propagation distance (2.2 units)

        SLIT_1_X = -SLIT_SEP / 2.0  # -0.90
        SLIT_2_X = SLIT_SEP / 2.0   # +0.90
        S1_POS = np.array([SLIT_1_X, Y_BARRIER, 0.0])
        S2_POS = np.array([SLIT_2_X, Y_BARRIER, 0.0])

        # Grid of screen positions
        xs = np.linspace(-3.5, 3.5, 701)
        r1_vals = np.sqrt((xs - SLIT_1_X) ** 2 + L**2)
        r2_vals = np.sqrt((xs - SLIT_2_X) ** 2 + L**2)
        delta_r_vals = np.abs(r1_vals - r2_vals)

        # Exact dark fringe position where Delta_r = lambda / 2
        idx_dark = np.argmin(np.abs(delta_r_vals - LAMBDA / 2.0))
        x_dark = float(xs[idx_dark])  # ~ 0.46

        # Probability distributions (properly normalized)
        # Single slit: Central diffraction lobe (Gaussian envelope approximation)
        p_single = np.exp(-(xs**2) / (2.0 * (0.85**2)))
        p_single /= np.sum(p_single)

        # Two slits: Envelope * interference factor cos^2(Delta_phi / 2)
        delta_phi = (2.0 * np.pi / LAMBDA) * (r1_vals - r2_vals)
        envelope_2slit = np.exp(-(xs**2) / (2.0 * (1.65**2)))
        p_double = envelope_2slit * (np.cos(delta_phi / 2.0) ** 2)
        p_double /= np.sum(p_double)

        # -----------------------------------------------------------
        # Visual Helpers: Glows & Amplitude Curves
        # -----------------------------------------------------------
        def make_glow_dot(center, radius=0.08, color=YELLOW):
            """Creates a multi-layered luminous quantum detection dot."""
            core = Dot(point=center, radius=radius * 0.5, color=WHITE)
            inner = Dot(point=center, radius=radius, color=color, fill_opacity=0.85)
            outer = Dot(point=center, radius=radius * 2.2, color=color, fill_opacity=0.25)
            return VGroup(outer, inner, core)

        def make_amplitude_wave(start, end, wavelength=LAMBDA, amp=0.14, color=TEAL_B):
            """
            Builds a spatial amplitude wave whose cycle count and phase are
            strictly derived from distance / wavelength.
            """
            vec = end - start
            dist = np.linalg.norm(vec)
            u = vec / dist
            normal = np.array([-u[1], u[0], 0.0])

            num_pts = 120
            pts = []
            for t in np.linspace(0.0, 1.0, num_pts):
                s = t * dist
                base = start + t * vec
                # Spatial phase phi(s) = 2*pi * (s / lambda)
                wiggle = amp * np.sin(2.0 * np.pi * (s / wavelength))
                pts.append(base + wiggle * normal)

            curve = VMobject(color=color, stroke_width=3.2)
            curve.set_points_smoothly(pts)
            return curve

        # -----------------------------------------------------------
        # Top Header & Narrative Subtitle Banners
        # -----------------------------------------------------------
        header_pill = RoundedRectangle(
            corner_radius=0.25,
            width=7.0,
            height=0.68,
            fill_color=DARK_GRAY,
            fill_opacity=0.85,
            stroke_color=BLUE_E,
            stroke_width=2.5,
        ).move_to(np.array([0.0, 7.2, 0.0]))

        header_text = Text(
            "QUANTUM INTERFERENCE",
            font_size=20,
            weight=BOLD,
            color=BLUE_B,
        ).move_to(header_pill.get_center())

        subtitle = Text(
            "Firing particles one at a time...",
            font_size=19,
            color=WHITE,
        ).move_to(np.array([0.0, 6.35, 0.0]))

        self.play(FadeIn(header_pill), FadeIn(header_text), Write(subtitle), run_time=1.0)

        # -----------------------------------------------------------
        # Apparatus Setup: SOURCE -> BARRIER -> DETECTOR
        # -----------------------------------------------------------
        source_box = RoundedRectangle(
            corner_radius=0.15,
            width=3.0,
            height=0.75,
            fill_color=BLUE_E,
            fill_opacity=0.45,
            stroke_color=BLUE_C,
            stroke_width=2.5,
        ).move_to(np.array([0.0, Y_SOURCE, 0.0]))

        source_label = Text(
            "SINGLE-PARTICLE SOURCE",
            font_size=15,
            weight=BOLD,
            color=WHITE,
        ).move_to(source_box.get_center())

        nozzle = Dot(point=np.array([0.0, Y_SOURCE - 0.38, 0.0]), radius=0.09, color=TEAL_A)

        # Screen detector
        detector_bar = Rectangle(
            width=7.2,
            height=0.22,
            fill_color=DARK_GRAY,
            fill_opacity=0.9,
            stroke_color=GRAY_B,
            stroke_width=2.0,
        ).move_to(np.array([0.0, Y_SCREEN, 0.0]))

        detector_label = Text(
            "DETECTION SCREEN",
            font_size=14,
            color=GRAY_C,
        ).next_to(detector_bar, DOWN, buff=0.12)

        # Probability baseline
        prob_axis = Line(
            start=np.array([-3.5, -2.5, 0.0]),
            end=np.array([3.5, -2.5, 0.0]),
            color=GRAY_D,
            stroke_width=2.0,
        )
        prob_label = Text(
            "Detection Probability P(x)",
            font_size=15,
            color=GRAY_C,
        ).next_to(prob_axis, DOWN, buff=0.15)

        # One-slit barrier (aperture around x = 0)
        wall_left_1 = Rectangle(
            width=3.2,
            height=0.14,
            fill_color=GRAY_D,
            fill_opacity=0.95,
            stroke_color=GRAY_B,
            stroke_width=1.5,
        ).move_to(np.array([-1.95, Y_BARRIER, 0.0]))

        wall_right_1 = Rectangle(
            width=3.2,
            height=0.14,
            fill_color=GRAY_D,
            fill_opacity=0.95,
            stroke_color=GRAY_B,
            stroke_width=1.5,
        ).move_to(np.array([1.95, Y_BARRIER, 0.0]))

        single_barrier = VGroup(wall_left_1, wall_right_1)
        slit1_label = Text("ONE SLIT", font_size=15, color=BLUE_C).next_to(
            single_barrier, UP, buff=0.12
        )

        self.play(
            FadeIn(source_box),
            FadeIn(source_label),
            FadeIn(nozzle),
            FadeIn(single_barrier),
            FadeIn(slit1_label),
            FadeIn(detector_bar),
            FadeIn(detector_label),
            FadeIn(prob_axis),
            FadeIn(prob_label),
            run_time=1.4,
        )

        # -----------------------------------------------------------
        # SCENE 1: The Naive Picture (Particles arrive one at a time)
        # -----------------------------------------------------------
        detection_dots = VGroup()

        def fire_single_particle(target_x, flight_time=0.65):
            p = Dot(point=nozzle.get_center(), radius=0.07, color=YELLOW)
            self.add(p)
            # Source to single slit
            self.play(
                p.animate.move_to(np.array([0.0, Y_BARRIER, 0.0])),
                rate_func=linear,
                run_time=flight_time * 0.45,
            )
            # Slit to screen
            hit_pos = np.array([target_x, Y_SCREEN + np.random.uniform(-0.03, 0.03), 0.0])
            self.play(
                p.animate.move_to(hit_pos),
                rate_func=linear,
                run_time=flight_time * 0.55,
            )
            glow = make_glow_dot(hit_pos, radius=0.06, color=YELLOW)
            detection_dots.add(glow)
            self.remove(p)
            self.add(glow)
            self.wait(0.08)

        # Three individual localized hits
        for target in [0.25, -0.65, 0.85]:
            fire_single_particle(target, flight_time=0.5)

        note_single = Text(
            "Each particle is registered as a single point.",
            font_size=16,
            color=YELLOW_A,
        ).move_to(np.array([0.0, -4.2, 0.0]))
        self.play(FadeIn(note_single), run_time=0.6)
        self.wait(0.6)

        # -----------------------------------------------------------
        # SCENE 2: One Slit Distribution (Broad spread)
        # -----------------------------------------------------------
        new_sub = Text(
            "ONE SLIT: Accumulation builds a broad central lobe",
            font_size=18,
            color=WHITE,
        ).move_to(subtitle.get_center())

        self.play(Transform(subtitle, new_sub), FadeOut(note_single), run_time=0.6)

        # Sample 30 particles from single-slit distribution
        sampled_single = np.random.choice(xs, size=30, p=p_single)
        rapid_single_dots = []
        for x_val in sampled_single:
            h_pos = np.array([x_val, Y_SCREEN + np.random.uniform(-0.03, 0.03), 0.0])
            g = make_glow_dot(h_pos, radius=0.05, color=YELLOW_B)
            rapid_single_dots.append(FadeIn(g, scale=0.5, run_time=0.08))
            detection_dots.add(g)

        self.play(AnimationGroup(*rapid_single_dots, lag_ratio=0.04), run_time=1.8)

        # Draw smooth single-slit distribution curve
        single_curve_pts = [
            np.array([x, -2.5 + 1.25 * np.exp(-(x**2) / (2.0 * (0.85**2))), 0.0])
            for x in xs
        ]
        single_curve = VMobject(color=BLUE_B, stroke_width=3.5)
        single_curve.set_points_smoothly(single_curve_pts)
        single_curve_label = Text("P₁(x)", font_size=18, color=BLUE_B).next_to(
            single_curve, UP, buff=0.1
        )

        single_note = Text(
            "Individual hits are random — their statistics form P₁(x).",
            font_size=16,
            color=GRAY_B,
        ).move_to(np.array([0.0, -4.2, 0.0]))

        self.play(Create(single_curve), FadeIn(single_curve_label), FadeIn(single_note), run_time=1.2)
        self.wait(0.8)

        # -----------------------------------------------------------
        # SCENE 3: Two Slits — The Mystery Stripes
        # -----------------------------------------------------------
        wall_left_2 = Rectangle(
            width=2.2,
            height=0.14,
            fill_color=GRAY_D,
            fill_opacity=0.95,
            stroke_color=GRAY_B,
            stroke_width=1.5,
        ).move_to(np.array([-2.40, Y_BARRIER, 0.0]))

        wall_center_2 = Rectangle(
            width=1.4,
            height=0.14,
            fill_color=GRAY_D,
            fill_opacity=0.95,
            stroke_color=GRAY_B,
            stroke_width=1.5,
        ).move_to(np.array([0.0, Y_BARRIER, 0.0]))

        wall_right_2 = Rectangle(
            width=2.2,
            height=0.14,
            fill_color=GRAY_D,
            fill_opacity=0.95,
            stroke_color=GRAY_B,
            stroke_width=1.5,
        ).move_to(np.array([2.40, Y_BARRIER, 0.0]))

        double_barrier = VGroup(wall_left_2, wall_center_2, wall_right_2)

        slits_labels = VGroup(
            Text("Slit 1", font_size=14, color=TEAL_B).move_to(np.array([SLIT_1_X, 2.72, 0.0])),
            Text("Slit 2", font_size=14, color=GOLD_B).move_to(np.array([SLIT_2_X, 2.72, 0.0])),
        )

        new_sub2 = Text(
            "TWO SLITS: Particles still emitted one at a time...",
            font_size=18,
            color=WHITE,
        ).move_to(subtitle.get_center())

        self.play(
            Transform(subtitle, new_sub2),
            FadeOut(detection_dots),
            FadeOut(single_curve),
            FadeOut(single_curve_label),
            FadeOut(single_note),
            FadeOut(slit1_label),
            ReplacementTransform(single_barrier, double_barrier),
            FadeIn(slits_labels),
            run_time=1.2,
        )
        detection_dots = VGroup()

        # QUANTUM-CORRECT PROPAGATION: Coherent wave packet illuminates both slits
        # rather than assigning a classical trajectory to one slit!
        def fire_quantum_detection(target_x):
            hit_pos = np.array([target_x, Y_SCREEN + np.random.uniform(-0.03, 0.03), 0.0])

            # Packet from source to barrier
            pulse_source = Dot(point=nozzle.get_center(), radius=0.08, color=YELLOW_A)
            self.add(pulse_source)
            self.play(
                pulse_source.animate.move_to(np.array([0.0, Y_BARRIER, 0.0])),
                rate_func=linear,
                run_time=0.25,
            )
            self.remove(pulse_source)

            # Two coherent wavelets pass both slits toward detector
            w1 = Dot(point=S1_POS, radius=0.06, color=TEAL_A, fill_opacity=0.7)
            w2 = Dot(point=S2_POS, radius=0.06, color=GOLD_A, fill_opacity=0.7)
            self.add(w1, w2)
            self.play(
                w1.animate.move_to(hit_pos),
                w2.animate.move_to(hit_pos),
                rate_func=linear,
                run_time=0.35,
            )
            self.remove(w1, w2)

            glow = make_glow_dot(hit_pos, radius=0.05, color=YELLOW)
            detection_dots.add(glow)
            self.add(glow)

        # Show 4 initial detections
        init_samples = np.random.choice(xs, size=4, p=p_double)
        for val in init_samples:
            fire_quantum_detection(val)

        noisy_note = Text(
            "Individual detections look entirely random...",
            font_size=16,
            color=GRAY_B,
        ).move_to(np.array([0.0, -4.2, 0.0]))
        self.play(FadeIn(noisy_note), run_time=0.5)

        # Rapid accumulation of 90 particles
        many_samples = np.random.choice(xs, size=90, p=p_double)
        rapid_double_dots = []
        for x_val in many_samples:
            h_pos = np.array([x_val, Y_SCREEN + np.random.uniform(-0.03, 0.03), 0.0])
            g = make_glow_dot(h_pos, radius=0.045, color=YELLOW_B)
            rapid_double_dots.append(FadeIn(g, scale=0.5, run_time=0.06))
            detection_dots.add(g)

        self.play(
            AnimationGroup(*rapid_double_dots, lag_ratio=0.02),
            FadeOut(noisy_note),
            run_time=2.2,
        )

        puzzle_card = RoundedRectangle(
            corner_radius=0.18,
            width=7.6,
            height=1.4,
            fill_color=DARK_GRAY,
            fill_opacity=0.9,
            stroke_color=GOLD_C,
            stroke_width=2.0,
        ).move_to(np.array([0.0, -4.2, 0.0]))

        puzzle_title = Text(
            "Alternating Bright & Dark Stripes!",
            font_size=18,
            weight=BOLD,
            color=GOLD_A,
        ).move_to(np.array([0.0, -3.85, 0.0]))

        puzzle_desc = Text(
            "Where do stripes come from?\nParticles arrived one by one — never colliding!",
            font_size=15,
            color=WHITE,
            line_spacing=1.2,
        ).move_to(np.array([0.0, -4.4, 0.0]))

        puzzle_group = VGroup(puzzle_card, puzzle_title, puzzle_desc)
        self.play(FadeIn(puzzle_group), run_time=0.8)
        self.wait(1.2)

        # -----------------------------------------------------------
        # SCENE 4: Introduce Amplitudes & Interference
        # -----------------------------------------------------------
        new_sub3 = Text(
            "THE EXPLANATION: Quantum Probability Amplitudes",
            font_size=18,
            weight=BOLD,
            color=TEAL_A,
        ).move_to(subtitle.get_center())

        self.play(Transform(subtitle, new_sub3), FadeOut(puzzle_group), run_time=0.6)

        # Case A: Constructive Interference at Center (x = 0.0)
        t_center = np.array([0.0, Y_SCREEN, 0.0])
        wave1_c = make_amplitude_wave(S1_POS, t_center, wavelength=LAMBDA, color=TEAL_B)
        wave2_c = make_amplitude_wave(S2_POS, t_center, wavelength=LAMBDA, color=GOLD_B)

        lbl_psi1 = Text("amplitude ψ₁", font_size=15, color=TEAL_B).move_to(
            np.array([-1.7, 1.3, 0.0])
        )
        lbl_psi2 = Text("amplitude ψ₂", font_size=15, color=GOLD_B).move_to(
            np.array([1.7, 1.3, 0.0])
        )

        constructive_card = RoundedRectangle(
            corner_radius=0.18,
            width=7.6,
            height=1.35,
            fill_color=DARK_GRAY,
            fill_opacity=0.9,
            stroke_color=GREEN_C,
            stroke_width=2.0,
        ).move_to(np.array([0.0, -4.2, 0.0]))

        constructive_title = Text(
            "CONSTRUCTIVE: Δr = 0  (In Phase)",
            font_size=16,
            weight=BOLD,
            color=GREEN_B,
        ).move_to(np.array([0.0, -3.8, 0.0]))

        constructive_desc = Text(
            "Equal path lengths → Waves arrive crest-to-crest.\nAmplitudes reinforce: ψ₁ + ψ₂ is LARGE → High probability!",
            font_size=14,
            color=WHITE,
            line_spacing=1.2,
        ).move_to(np.array([0.0, -4.38, 0.0]))

        constructive_group = VGroup(
            constructive_card, constructive_title, constructive_desc
        )

        self.play(
            Create(wave1_c),
            Create(wave2_c),
            FadeIn(lbl_psi1),
            FadeIn(lbl_psi2),
            FadeIn(constructive_group),
            run_time=1.4,
        )
        self.wait(1.2)

        # Case B: Destructive Interference at exact dark fringe x_dark
        t_dark = np.array([x_dark, Y_SCREEN, 0.0])
        wave1_d = make_amplitude_wave(S1_POS, t_dark, wavelength=LAMBDA, color=TEAL_B)
        wave2_d = make_amplitude_wave(S2_POS, t_dark, wavelength=LAMBDA, color=GOLD_B)

        destructive_card = RoundedRectangle(
            corner_radius=0.18,
            width=7.6,
            height=1.35,
            fill_color=DARK_GRAY,
            fill_opacity=0.9,
            stroke_color=RED_C,
            stroke_width=2.0,
        ).move_to(np.array([0.0, -4.2, 0.0]))

        destructive_title = Text(
            f"DESTRUCTIVE: Δr = λ/2  (Out of Phase)",
            font_size=16,
            weight=BOLD,
            color=RED_B,
        ).move_to(np.array([0.0, -3.8, 0.0]))

        destructive_desc = Text(
            "Path difference is exactly ½ wavelength.\nCrest meets trough: ψ₁ + ψ₂ = 0 → Zero probability!",
            font_size=14,
            color=WHITE,
            line_spacing=1.2,
        ).move_to(np.array([0.0, -4.38, 0.0]))

        destructive_group = VGroup(
            destructive_card, destructive_title, destructive_desc
        )

        self.play(
            Transform(wave1_c, wave1_d),
            Transform(wave2_c, wave2_d),
            ReplacementTransform(constructive_group, destructive_group),
            run_time=1.4,
        )
        self.wait(1.2)

        clarification_note = Text(
            "ψ is a mathematical amplitude of probability, not a mechanical wave.",
            font_size=14,
            color=BLUE_A,
            weight=BOLD,
        ).move_to(np.array([0.0, -5.2, 0.0]))
        self.play(FadeIn(clarification_note), run_time=0.6)
        self.wait(0.8)

        # -----------------------------------------------------------
        # SCENE 5: The Equation (Born's Rule & Superposition)
        # -----------------------------------------------------------
        new_sub4 = Text(
            "THE LAW: Add amplitudes first, square magnitude after",
            font_size=17,
            weight=BOLD,
            color=GOLD_A,
        ).move_to(subtitle.get_center())

        self.play(
            Transform(subtitle, new_sub4),
            FadeOut(wave1_c),
            FadeOut(wave2_c),
            FadeOut(lbl_psi1),
            FadeOut(lbl_psi2),
            FadeOut(destructive_group),
            FadeOut(clarification_note),
            run_time=0.7,
        )

        # Use distinct uppercase Ψ to avoid substring prefix collisions in Text t2c
        eq_psi = Text(
            "Total Amplitude:   Ψ = ψ₁ + ψ₂",
            font_size=21,
            weight=BOLD,
            t2c={"ψ₁": TEAL_B, "ψ₂": GOLD_B, "Ψ": WHITE},
        ).move_to(np.array([0.0, -3.6, 0.0]))

        eq_prob = Text(
            "Detection Probability:   P(x) = |Ψ|² = |ψ₁ + ψ₂|²",
            font_size=20,
            weight=BOLD,
            t2c={"ψ₁": TEAL_B, "ψ₂": GOLD_B, "P(x)": BLUE_B, "Ψ": WHITE},
        ).move_to(np.array([0.0, -4.3, 0.0]))

        expansion = Text(
            "|ψ₁ + ψ₂|²  =  |ψ₁|² + |ψ₂|² + 2·Re(ψ₁* ψ₂)",
            font_size=18,
            weight=BOLD,
            t2c={
                "|ψ₁|²": TEAL_B,
                "|ψ₂|²": GOLD_B,
                "2·Re(ψ₁* ψ₂)": RED_B,
            },
        ).move_to(np.array([0.0, -5.1, 0.0]))

        cross_term_tag = Text(
            "↑ Quantum interference cross-term produces the stripes!",
            font_size=14,
            weight=BOLD,
            color=RED_B,
        ).move_to(np.array([0.0, -5.65, 0.0]))

        self.play(FadeIn(eq_psi), run_time=0.6)
        self.play(FadeIn(eq_prob), run_time=0.8)
        self.play(FadeIn(expansion), FadeIn(cross_term_tag), run_time=1.1)
        self.wait(1.5)

        # -----------------------------------------------------------
        # SCENE 6: The Final Realization (Emergence of Order)
        # -----------------------------------------------------------
        new_sub5 = Text(
            "THE RESULT: Statistical order emerges from random hits",
            font_size=17,
            weight=BOLD,
            color=WHITE,
        ).move_to(subtitle.get_center())

        self.play(
            Transform(subtitle, new_sub5),
            FadeOut(eq_psi),
            FadeOut(eq_prob),
            FadeOut(expansion),
            FadeOut(cross_term_tag),
            run_time=0.7,
        )

        # Full theoretical double-slit interference curve
        double_curve_pts = [
            np.array(
                [
                    x,
                    -2.5
                    + 1.35
                    * np.exp(-(x**2) / (2.0 * (1.65**2)))
                    * (np.cos(((2.0 * np.pi / LAMBDA) * (r1_vals[i] - r2_vals[i])) / 2.0) ** 2),
                    0.0,
                ]
            )
            for i, x in enumerate(xs)
        ]
        double_curve = VMobject(color=GOLD_A, stroke_width=3.6)
        double_curve.set_points_smoothly(double_curve_pts)

        double_curve_label = Text(
            "P(x) = |ψ₁ + ψ₂|²", font_size=18, weight=BOLD, color=GOLD_A
        ).next_to(double_curve, UP, buff=0.1)

        # 110 additional particle detections accumulating rapidly
        final_samples = np.random.choice(xs, size=110, p=p_double)
        final_dots_anim = []
        for x_val in final_samples:
            h_pos = np.array([x_val, Y_SCREEN + np.random.uniform(-0.03, 0.03), 0.0])
            g = make_glow_dot(h_pos, radius=0.045, color=YELLOW_A)
            final_dots_anim.append(FadeIn(g, scale=0.5, run_time=0.05))
            detection_dots.add(g)

        self.play(
            Create(double_curve),
            FadeIn(double_curve_label),
            AnimationGroup(*final_dots_anim, lag_ratio=0.012),
            run_time=2.4,
        )

        # Final Summary Takeaways
        takeaway_card = RoundedRectangle(
            corner_radius=0.2,
            width=7.6,
            height=2.2,
            fill_color=DARK_GRAY,
            fill_opacity=0.92,
            stroke_color=BLUE_D,
            stroke_width=2.0,
        ).move_to(np.array([0.0, -4.8, 0.0]))

        t1 = Text("• Individual localized detections.", font_size=17, weight=BOLD, color=WHITE)
        t2 = Text("• Superposition of quantum amplitudes.", font_size=17, weight=BOLD, color=TEAL_B)
        t3 = Text("• Emergent macroscopic interference.", font_size=17, weight=BOLD, color=GOLD_A)

        takeaways = VGroup(t1, t2, t3).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        takeaways.move_to(takeaway_card.get_center() + np.array([0.0, 0.35, 0.0]))

        final_quote = Text(
            "Quantum mechanics predicts probabilities — never individual clicks.",
            font_size=14,
            weight=BOLD,
            color=BLUE_B,
        ).move_to(takeaway_card.get_center() + np.array([0.0, -0.65, 0.0]))

        self.play(
            FadeIn(takeaway_card),
            FadeIn(takeaways),
            FadeIn(final_quote),
            run_time=1.2,
        )

        self.wait(2.5)
