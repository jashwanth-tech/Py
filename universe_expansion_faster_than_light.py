from manim import *
import numpy as np

# ============================================================
# THE UNIVERSE CAN EXPAND FASTER THAN LIGHT
# Vertical 9:16 Manim animation
# ============================================================

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 60


class UniverseExpansion(Scene):

    def construct(self):

        # ----------------------------------------------------
        # 1. OPENING
        # ----------------------------------------------------

        opening = Text(
            "Imagine you're floating",
            font_size=46
        )

        opening2 = Text(
            "somewhere in the universe.",
            font_size=46
        ).next_to(
            opening,
            DOWN,
            buff=0.25
        )

        self.play(Write(opening))
        self.play(Write(opening2))
        self.wait(1)

        self.play(
            FadeOut(opening),
            FadeOut(opening2)
        )

        # ----------------------------------------------------
        # 2. COSMIC FIELD
        # ----------------------------------------------------

        np.random.seed(4)

        galaxies = VGroup()

        for _ in range(100):

            x = np.random.uniform(-5, 5)
            y = np.random.uniform(-7, 7)

            galaxy = Dot(
                np.array([x, y, 0]),
                radius=np.random.uniform(0.025, 0.06)
            )

            galaxies.add(galaxy)

        self.play(
            LaggedStart(
                *[FadeIn(g) for g in galaxies],
                lag_ratio=0.015
            ),
            run_time=2
        )

        self.wait(1)

        # ----------------------------------------------------
        # 3. SCALE FACTOR
        # ----------------------------------------------------

        scale_text = MathTex(
            r"a(t)"
        ).to_edge(
            UP,
            buff=0.8
        )

        self.play(Write(scale_text))

        # ----------------------------------------------------
        # 4. COMOVING GRID
        # ----------------------------------------------------

        grid = NumberPlane(
            x_range=[-6, 6, 1],
            y_range=[-7, 7, 1],
            background_line_style={
                "stroke_opacity": 0.25,
                "stroke_width": 1
            }
        )

        self.play(
            FadeIn(grid),
            run_time=1
        )

        # ----------------------------------------------------
        # 5. OBSERVER + SELECTED GALAXY
        # ----------------------------------------------------

        observer = Dot(
            ORIGIN,
            radius=0.13
        )

        observer_label = Text(
            "you",
            font_size=30
        ).next_to(
            observer,
            DOWN,
            buff=0.15
        )

        selected_galaxy = Dot(
            LEFT * 4,
            radius=0.12
        )

        selected_label = Text(
            "galaxy",
            font_size=28
        ).next_to(
            selected_galaxy,
            UP,
            buff=0.15
        )

        self.play(
            FadeIn(observer),
            FadeIn(observer_label),
            FadeIn(selected_galaxy),
            FadeIn(selected_label)
        )

        # ----------------------------------------------------
        # 6. EXPANSION
        # ----------------------------------------------------

        original_positions = [
            g.get_center().copy()
            for g in galaxies
        ]

        def expand_galaxies(scale):

            animations = []

            for galaxy, pos in zip(
                galaxies,
                original_positions
            ):
                animations.append(
                    galaxy.animate.move_to(
                        pos * scale
                    )
                )

            return animations

        # IMPORTANT:
        # selected_galaxy now expands with the cosmic grid.
        self.play(
            *expand_galaxies(1.6),

            selected_galaxy.animate.move_to(
                LEFT * 4 * 1.6
            ),

            selected_label.animate.next_to(
                LEFT * 4 * 1.6,
                UP,
                buff=0.15
            ),

            grid.animate.scale(1.6),

            run_time=3
        )

        self.wait(0.7)

        # ----------------------------------------------------
        # 7. HUBBLE LAW
        # ----------------------------------------------------

        self.play(
            FadeOut(galaxies),
            FadeOut(grid),
            FadeOut(selected_galaxy),
            FadeOut(selected_label),
            FadeOut(observer),
            FadeOut(observer_label),
            FadeOut(scale_text)
        )

        hubble = MathTex(
            r"v_{\rm rec}=H_0d"
        ).scale(1.3)

        self.play(Write(hubble))
        self.wait(1)

        distance = MathTex(
            r"d\uparrow"
        ).next_to(
            hubble,
            DOWN,
            buff=0.5
        )

        speed = MathTex(
            r"v_{\rm rec}\uparrow"
        ).next_to(
            distance,
            DOWN,
            buff=0.3
        )

        self.play(
            Write(distance),
            Write(speed)
        )

        self.wait(1)

        # ----------------------------------------------------
        # 8. LIGHT SPEED THRESHOLD
        # ----------------------------------------------------

        self.play(
            FadeOut(hubble),
            FadeOut(distance),
            FadeOut(speed)
        )

        threshold = MathTex(
            r"d=\frac{c}{H_0}"
        ).scale(1.2)

        threshold_text = Text(
            "At this distance:",
            font_size=38
        ).next_to(
            threshold,
            UP,
            buff=0.4
        )

        velocity = MathTex(
            r"v_{\rm rec}=c"
        ).next_to(
            threshold,
            DOWN,
            buff=0.5
        )

        self.play(
            Write(threshold_text),
            Write(threshold),
            Write(velocity)
        )

        self.wait(1)

        # ----------------------------------------------------
        # 9. BEYOND c
        # ----------------------------------------------------

        self.play(
            FadeOut(threshold_text),
            FadeOut(threshold),
            FadeOut(velocity)
        )

        beyond = MathTex(
            r"d>\frac{c}{H_0}"
        ).scale(1.2)

        receding = MathTex(
            r"v_{\rm rec}>c"
        ).scale(1.4)

        receding.next_to(
            beyond,
            DOWN,
            buff=0.5
        )

        self.play(Write(beyond))
        self.play(Write(receding))

        self.wait(1)

        # ----------------------------------------------------
        # 10. DID RELATIVITY BREAK?
        # ----------------------------------------------------

        self.play(
            FadeOut(beyond),
            FadeOut(receding)
        )

        question = Text(
            "Did relativity break?",
            font_size=52
        )

        self.play(Write(question))
        self.wait(1)

        self.play(FadeOut(question))

        # ----------------------------------------------------
        # 11. LOCAL SPEED
        # ----------------------------------------------------

        local = Text(
            "Locally...",
            font_size=42
        ).to_edge(
            UP,
            buff=1
        )

        light = MathTex(
            r"v_{\rm light}=c"
        ).scale(1.3)

        self.play(
            Write(local),
            Write(light)
        )

        self.wait(1)

        self.play(
            FadeOut(local),
            FadeOut(light)
        )

        # ----------------------------------------------------
        # 12. TWO-GALAXY RECESSION DEMO
        # ----------------------------------------------------

        galaxy1 = Dot(
            LEFT * 3,
            radius=0.12
        )

        galaxy2 = Dot(
            RIGHT * 3,
            radius=0.12
        )

        galaxy1_label = Text(
            "galaxy A",
            font_size=28
        ).next_to(
            galaxy1,
            DOWN
        )

        galaxy2_label = Text(
            "galaxy B",
            font_size=28
        ).next_to(
            galaxy2,
            DOWN
        )

        line = Line(
            galaxy1.get_center(),
            galaxy2.get_center()
        )

        distance_label = MathTex(
            r"d"
        ).next_to(
            line,
            UP,
            buff=0.2
        )

        self.play(
            FadeIn(galaxy1),
            FadeIn(galaxy2),
            Create(line),
            FadeIn(galaxy1_label),
            FadeIn(galaxy2_label),
            Write(distance_label)
        )

        self.wait(0.5)

        # Both galaxies separate.
        # There is no privileged central observer here.
        self.play(
            galaxy1.animate.shift(LEFT * 2),
            galaxy2.animate.shift(RIGHT * 2),

            galaxy1_label.animate.shift(LEFT * 2),
            galaxy2_label.animate.shift(RIGHT * 2),

            line.animate.put_start_and_end_on(
                LEFT * 5,
                RIGHT * 5
            ),

            distance_label.animate.move_to(
                UP * 0.5
            ),

            run_time=2
        )

        self.wait(0.7)

        # ----------------------------------------------------
        # 13. FINAL EQUATIONS
        # ----------------------------------------------------

        self.play(
            FadeOut(galaxy1),
            FadeOut(galaxy2),
            FadeOut(galaxy1_label),
            FadeOut(galaxy2_label),
            FadeOut(line),
            FadeOut(distance_label)
        )

        local_speed = MathTex(
            r"\text{local speed}\leq c"
        ).scale(1.1)

        cosmic_distance = MathTex(
            r"\text{cosmic recession rate}>c"
        ).scale(1.1)

        cosmic_distance.next_to(
            local_speed,
            DOWN,
            buff=0.6
        )

        self.play(
            Write(local_speed),
            Write(cosmic_distance)
        )

        self.wait(1)

        # ----------------------------------------------------
        # 14. FINAL LINE
        # ----------------------------------------------------

        self.play(
            FadeOut(local_speed),
            FadeOut(cosmic_distance)
        )

        final1 = Text(
            "The universe isn't",
            font_size=48
        )

        final2 = Text(
            "outrunning light.",
            font_size=48
        ).next_to(
            final1,
            DOWN,
            buff=0.2
        )

        final3 = Text(
            "It's changing the distance",
            font_size=40
        ).next_to(
            final2,
            DOWN,
            buff=0.4
        )

        final4 = Text(
            "light has to cross.",
            font_size=40
        ).next_to(
            final3,
            DOWN,
            buff=0.15
        )

        self.play(Write(final1))
        self.play(Write(final2))
        self.play(Write(final3))
        self.play(Write(final4))

        self.wait(2)
