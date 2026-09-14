from manim import *
import numpy as np

# ============================================================
# WHY DOES A MAGNETIC FIELD DO NO WORK?
# Vertical 9:16 Manim animation
# ============================================================

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_rate = 60


class MagneticFieldNoWork(Scene):

    def construct(self):

        # ----------------------------------------------------
        # 1. OPENING
        # ----------------------------------------------------

        title = Text(
            "A magnetic field can bend a particle...",
            font_size=42
        ).to_edge(UP, buff=0.8)

        subtitle = Text(
            "...without doing work on it.",
            font_size=38
        ).next_to(title, DOWN, buff=0.25)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(1)

        self.play(
            FadeOut(title),
            FadeOut(subtitle)
        )

        # ----------------------------------------------------
        # 2. PARTICLE MOVING STRAIGHT
        # ----------------------------------------------------

        particle = Dot(radius=0.10)
        particle.shift(LEFT * 4)

        velocity_arrow = Arrow(
            particle.get_center(),
            particle.get_center() + RIGHT * 1.3,
            buff=0,
            stroke_width=6
        )

        velocity_text = MathTex(r"\vec v").next_to(
            velocity_arrow, DOWN, buff=0.15
        )

        self.play(
            FadeIn(particle),
            GrowArrow(velocity_arrow),
            FadeIn(velocity_text)
        )

        self.play(
            particle.animate.shift(RIGHT * 7),
            velocity_arrow.animate.shift(RIGHT * 7),
            velocity_text.animate.shift(RIGHT * 7),
            run_time=2
        )

        self.play(
            FadeOut(velocity_arrow),
            FadeOut(velocity_text)
        )

        # ----------------------------------------------------
        # 3. MAGNETIC FIELD
        #
        # B points INTO the screen.
        #
        # Convention:
        #   × = into the page
        #   • = out of the page
        #
        # With v along +x and B into the page (-z):
        #
        #   v × B = (+x) × (-z) = +y
        #
        # Therefore the magnetic force points UP.
        # ----------------------------------------------------

        field_symbols = VGroup()

        xs = np.linspace(-4.5, 4.5, 5)
        ys = np.linspace(-2.5, 2.5, 6)

        for x in xs:
            for y in ys:
                cross = MathTex(
                    r"\times",
                    font_size=28
                ).move_to([x, y, 0])

                field_symbols.add(cross)

        field_label = MathTex(
            r"\vec B\ \text{into the page}"
        ).to_edge(RIGHT).shift(UP * 0.3)

        self.play(
            FadeIn(field_symbols),
            FadeIn(field_label),
            run_time=1
        )

        # ----------------------------------------------------
        # 4. LORENTZ FORCE
        # ----------------------------------------------------

        force_eq = MathTex(
            r"\vec F_B=q(\vec v\times\vec B)"
        ).scale(1.1)

        force_eq.to_edge(DOWN, buff=1.3)

        self.play(Write(force_eq))
        self.wait(1)

        # ----------------------------------------------------
        # 5. SHOW PERPENDICULAR FORCE
        # ----------------------------------------------------

        self.play(
            FadeOut(field_symbols),
            FadeOut(field_label)
        )

        particle.move_to(ORIGIN)

        velocity_arrow = Arrow(
            particle.get_center(),
            particle.get_center() + RIGHT * 1.5,
            buff=0,
            stroke_width=6
        )

        force_arrow = Arrow(
            particle.get_center(),
            particle.get_center() + UP * 1.5,
            buff=0,
            stroke_width=6
        )

        v_label = MathTex(r"\vec v").next_to(
            velocity_arrow, DOWN, buff=0.1
        )

        f_label = MathTex(r"\vec F_B").next_to(
            force_arrow, LEFT, buff=0.1
        )

        self.play(
            GrowArrow(velocity_arrow),
            GrowArrow(force_arrow),
            FadeIn(v_label),
            FadeIn(f_label)
        )

        perpendicular = MathTex(
            r"\vec F_B\perp\vec v"
        ).to_edge(UP, buff=1.5)

        self.play(Write(perpendicular))
        self.wait(1)

        # ----------------------------------------------------
        # 6. POWER = FORCE DOT VELOCITY
        # ----------------------------------------------------

        self.play(
            FadeOut(force_eq),
            FadeOut(perpendicular)
        )

        power_eq = MathTex(
            r"P=\vec F\cdot\vec v"
        ).scale(1.2)

        power_eq.to_edge(DOWN, buff=1.5)

        self.play(Write(power_eq))
        self.wait(0.7)

        magnetic_power = MathTex(
            r"P=q(\vec v\times\vec B)\cdot\vec v"
        ).next_to(power_eq, UP, buff=0.35)

        self.play(Write(magnetic_power))

        zero_eq = MathTex(
            r"=0"
        ).next_to(magnetic_power, RIGHT, buff=0.25)

        self.play(
            Write(zero_eq),
            run_time=0.7
        )

        self.wait(0.8)

        # ----------------------------------------------------
        # 7. PARTICLE CURVES WITHOUT SPEEDING UP
        # ----------------------------------------------------

        self.play(
            FadeOut(power_eq),
            FadeOut(magnetic_power),
            FadeOut(zero_eq),

            # IMPORTANT:
            # Remove the actual arrows, not only their labels.
            FadeOut(velocity_arrow),
            FadeOut(force_arrow),
            FadeOut(v_label),
            FadeOut(f_label)
        )

        # ----------------------------------------------------
        # Smooth circular path
        #
        # Circle starts at LEFT*4 after rotation by PI.
        # The particle therefore starts exactly where it is.
        # ----------------------------------------------------

        path = Circle(
            radius=4,
            color=WHITE
        ).rotate(PI)

        particle.move_to(LEFT * 4)

        velocity_text = MathTex(
            r"|\vec v|=\text{constant}"
        ).to_edge(UP, buff=1)

        self.play(Write(velocity_text))

        self.play(
            MoveAlongPath(
                particle,
                path,
                rate_func=linear
            ),
            run_time=4
        )

        # ----------------------------------------------------
        # 8. FINAL IDEA
        # ----------------------------------------------------

        self.play(
            FadeOut(velocity_text),
            FadeOut(particle),
            FadeOut(path)
        )

        final1 = Text(
            "The magnetic field",
            font_size=46
        )

        final2 = Text(
            "doesn't speed it up.",
            font_size=46
        ).next_to(
            final1,
            DOWN,
            buff=0.25
        )

        final3 = Text(
            "It turns it.",
            font_size=54
        ).next_to(
            final2,
            DOWN,
            buff=0.35
        )

        self.play(Write(final1))
        self.play(Write(final2))
        self.play(Write(final3))

        self.wait(2)
