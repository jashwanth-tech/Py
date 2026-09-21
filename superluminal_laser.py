from manim import *
import numpy as np

# Configure vertical video format for 1080x1920
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16

class ContinuousBeam(VGroup):
    """
    Simulates a continuous stream of photons.
    Instead of a rigid line, it calculates the position of photons emitted over time,
    creating the correct physical curve (spiral) at high rotation speeds.
    """
    def __init__(self, theta_tracker, c=15.0):
        super().__init__()
        self.theta_tracker = theta_tracker
        self.c = c
        self.history = []  # Stores (emission_time, angle)
        self.current_t = 0.0
        
        # Create true Gaussian bloom with exponential thickness/opacity
        self.layers = VGroup()
        for i in range(5):
            opacity = 0.9 * (0.5 ** i)
            width = 3 + 18 * (i / 4.0)**1.5
            self.layers.add(VMobject(stroke_color=GREEN_C, stroke_opacity=opacity, stroke_width=width))
        self.add(self.layers)
        
        self.spot_pos = np.array([0, 6.0, 0])
        self.is_active = True

    # THE FIX: Added 'mob' to accept Manim's mobject argument
    def update_beam(self, mob, dt):
        if not self.is_active: 
            return
            
        self.current_t += dt
        current_th = self.theta_tracker.get_value()
        self.history.append((self.current_t, current_th))
        
        # Prune photons that hit the screen long ago (max travel time is ~0.8s)
        while len(self.history) > 2 and (self.current_t - self.history[1][0]) > 1.5:
            self.history.pop(0)
            
        points = []
        # Iterate from oldest to newest photons
        for i in range(len(self.history)):
            pt_t, pt_th = self.history[i]
            age = self.current_t - pt_t
            px = self.c * age * np.sin(pt_th)
            py = -6 + self.c * age * np.cos(pt_th)
            
            if py >= 6.0:
                # Photon passed the screen. Wait for the boundary crossing.
                pass 
            else:
                # Photon is in flight. If the previous (older) photon passed the screen,
                # interpolate the exact intersection at y=6 for continuous rendering.
                if i > 0:
                    prev_t, prev_th = self.history[i-1]
                    prev_age = self.current_t - prev_t
                    ppx = self.c * prev_age * np.sin(prev_th)
                    ppy = -6 + self.c * prev_age * np.cos(prev_th)
                    if ppy >= 6.0 and ppy != py:
                        ratio = (6.0 - py) / (ppy - py)
                        ix = px + ratio * (ppx - px)
                        self.spot_pos = np.array([ix, 6.0, 0])
                        points.append(self.spot_pos)
                
                points.append(np.array([px, py, 0]))
                
        # Draw from screen to emitter
        if len(points) >= 2:
            for layer in self.layers:
                layer.set_points_as_corners(points)

class SpotTrail(VGroup):
    """Creates a comet-like afterglow trail on the projection surface."""
    def __init__(self, beam):
        super().__init__()
        self.beam = beam
        self.trail_dots = []

    # THE FIX: Added 'mob' to accept Manim's mobject argument
    def update_trail(self, mob, dt):
        if not self.beam.is_active:
            return
        
        # Spawn new glowing dot at current physical intersection
        new_dot = Dot(self.beam.spot_pos, radius=0.15, color=GREEN_B, fill_opacity=1.0)
        self.add(new_dot)
        self.trail_dots.append(new_dot)
        
        # Fade and shrink older dots
        for d in self.trail_dots[:]:
            op = d.get_fill_opacity() - dt * 2.5  # Fades in 0.4s
            if op <= 0:
                self.remove(d)
                self.trail_dots.remove(d)
            else:
                d.set_fill(opacity=op)
                d.scale(0.9)

class Packet(VGroup):
    """A discrete photon packet (laser burst) travelling outward at exactly c."""
    def __init__(self, angle, c=15.0, length=2.0):
        super().__init__()
        self.angle = angle
        self.c = c
        self.length = length
        self.age = 0
        self.max_age = 12.0 / (c * np.cos(angle)) # Time to hit screen
        
        self.layers = VGroup()
        for i in range(4):
            opacity = 1.0 * (0.5 ** i)
            width = 3 + 12 * (i / 3.0)
            self.layers.add(VMobject(stroke_color=GREEN_C, stroke_opacity=opacity, stroke_width=width))
        self.add(self.layers)
        
        self.impact_glow = Dot(np.array([12 * np.tan(angle), 6, 0]), radius=0, color=GREEN_B)
        self.add(self.impact_glow)

    # THE FIX: Added 'mob' to accept Manim's mobject argument
    def update_packet(self, mob, dt):
        self.age += dt
        h_age = min(self.age, self.max_age)
        t_age = min(max(0, self.age - self.length/self.c), self.max_age)
        
        hx = self.c * h_age * np.sin(self.angle)
        hy = -6 + self.c * h_age * np.cos(self.angle)
        tx = self.c * t_age * np.sin(self.angle)
        ty = -6 + self.c * t_age * np.cos(self.angle)
        
        if t_age == self.max_age:
            # Packet fully absorbed
            for layer in self.layers:
                layer.set_stroke(opacity=0)
            self.impact_glow.set_fill(opacity=0)
        else:
            # Draw packet in flight
            for layer in self.layers:
                layer.set_points_as_corners([[tx, ty, 0], [hx, hy, 0]])
            
            # Impact flare when head touches screen
            if h_age == self.max_age:
                self.impact_glow.set_radius(0.3 * (1 - (self.age - self.max_age)*3))

class VelocityCounter(VGroup):
    """Live telemetry calculating the physical derivative of the spot vs c."""
    def __init__(self, beam):
        super().__init__()
        self.beam = beam
        self.last_pos = None
        
        self.label = Tex(r"$v_{spot} = $", font_size=55, color=WHITE)
        self.num = DecimalNumber(0, num_decimal_places=2, font_size=55, color=RED)
        self.c_label = Tex(r"$c$", font_size=55, color=WHITE)
        
        self.group = VGroup(self.label, self.num, self.c_label).arrange(RIGHT, buff=0.2)
        self.add(self.group)

    # THE FIX: Added 'mob' to accept Manim's mobject argument
    def update_val(self, mob, dt):
        if self.last_pos is not None and dt > 0 and self.beam.is_active:
            dx = np.linalg.norm(self.beam.spot_pos - self.last_pos)
            v = dx / dt
            ratio = v / self.beam.c
            self.num.set_value(ratio)
            
            if ratio > 1.0:
                self.num.set_color(YELLOW)
            else:
                self.num.set_color(RED)
        self.last_pos = self.beam.spot_pos.copy()


class SuperluminalLaser(ThreeDScene):
    def construct(self):
        # --------------------------------------------------
        # SCENE SETUP
        # --------------------------------------------------
        c_speed = 15.0
        max_angle = 25 * DEGREES
        
        emitter_pos = DOWN * 6
        
        emitter = Sector(radius=0.5, angle=PI, start_angle=0, color=DARK_GRAY, fill_opacity=1).move_to(emitter_pos)
        emitter_core = Circle(radius=0.1, color=GREEN_B, fill_opacity=1).move_to(emitter_pos + UP*0.1)
        
        # Thick glowing projection surface
        screen = Line(LEFT * 8 + UP * 6, RIGHT * 8 + UP * 6, color=BLUE_E, stroke_width=15, stroke_opacity=0.6)
        screen_core = Line(LEFT * 8 + UP * 6, RIGHT * 8 + UP * 6, color=BLUE_C, stroke_width=4)
        
        self.add(screen, screen_core, emitter, emitter_core)

        # Trackers and Dynamics
        theta = ValueTracker(-max_angle)
        beam = ContinuousBeam(theta_tracker=theta, c=c_speed)
        trail = SpotTrail(beam)
        v_counter = VelocityCounter(beam).move_to(DOWN * 2)
        
        beam.add_updater(beam.update_beam)
        trail.add_updater(trail.update_trail)
        v_counter.add_updater(v_counter.update_val)

        # --------------------------------------------------
        # PART 1: THE HOOK (0 - 6s)
        # --------------------------------------------------
        self.add(beam, trail)
        
        text_hook1 = Text("THIS SPOT CAN MOVE", weight=BOLD).scale_to_fit_width(7.5).move_to(UP * 1.5)
        text_hook2 = Text("FASTER THAN LIGHT", weight=BOLD, color=YELLOW).scale_to_fit_width(7.5).next_to(text_hook1, DOWN)

        self.play(Write(text_hook1), run_time=1)
        
        # Fast sweep. 50 degrees in 0.6s guarantees v > c due to geometry.
        self.play(theta.animate.set_value(max_angle), Write(text_hook2), FadeIn(v_counter), run_time=0.6, rate_func=linear)
        self.wait(1)
        
        self.play(FadeOut(text_hook1), FadeOut(text_hook2))

        # --------------------------------------------------
        # PART 2: BUILD THE IMPOSSIBILITY (6 - 18s)
        # --------------------------------------------------
        self.play(theta.animate.set_value(0), run_time=1)
        
        text_small = Text("SMALL ANGLE", color=YELLOW).scale_to_fit_width(5).move_to(DOWN * 3.5)
        text_huge = Text("HUGE DISPLACEMENT", color=RED).scale_to_fit_width(6).move_to(UP * 3.5)
        
        # Draw Angle Arc with correct signage
        arc = always_redraw(lambda: Arc(
            radius=3.0, start_angle=PI/2, angle=theta.get_value(), 
            arc_center=emitter_pos, color=YELLOW, stroke_width=6
        ))
        
        self.add(arc)
        self.play(theta.animate.set_value(10 * DEGREES), Write(text_small), run_time=1)
        self.play(theta.animate.set_value(max_angle), Write(text_huge), run_time=1.5, rate_func=smooth)
        
        self.wait(1)
        
        # Prep for reveal
        beam.is_active = False
        v_counter.clear_updaters()
        trail.clear_updaters()
        
        self.play(
            FadeOut(beam), FadeOut(trail), FadeOut(arc), 
            FadeOut(text_small), FadeOut(text_huge), FadeOut(v_counter)
        )

        # --------------------------------------------------
        # PART 3: THE REVEAL (18 - 32s)
        # --------------------------------------------------
        # Shift perspective to show depth and time
        self.move_camera(phi=65 * DEGREES, theta=-90 * DEGREES, run_time=2)
        
        text_reveal1 = Text("The spot is not an object.", font_size=40).move_to(UP * 1.5)
        text_reveal2 = Text("SEPARATE RAYS", weight=BOLD, color=YELLOW).scale_to_fit_width(6).next_to(text_reveal1, DOWN)
        
        # Ensure 3D camera doesn't distort the overlay text
        self.add_fixed_in_frame_mobjects(text_reveal1, text_reveal2)
        self.play(Write(text_reveal1), Write(text_reveal2))

        # Fire staggered packets to visibly form the sweeping spot
        angles = np.linspace(-20 * DEGREES, 20 * DEGREES, 12)
        for ang in angles:
            packet = Packet(angle=ang, c=c_speed, length=2.0)
            packet.add_updater(packet.update_packet)
            self.add(packet)
            self.wait(0.12) # Stagger time creates the spiral structure in flight
            
        self.wait(1.5)
        self.play(FadeOut(text_reveal1), FadeOut(text_reveal2))

        # --------------------------------------------------
        # PART 4: THE INFORMATION TEST (32 - 42s)
        # --------------------------------------------------
        text_info1 = Text("Information must travel physically.").scale_to_fit_width(7.5).move_to(UP * 1.5)
        self.add_fixed_in_frame_mobjects(text_info1)
        self.play(Write(text_info1))

        # Distinct locations
        pt_A = np.array([12 * np.tan(-15 * DEGREES), 6, 0])
        pt_B = np.array([12 * np.tan(15 * DEGREES), 6, 0])
        
        dot_a = Dot(pt_A, color=WHITE)
        dot_b = Dot(pt_B, color=WHITE)
        
        lbl_a = Text("A", font_size=40).next_to(dot_a, UP)
        lbl_b = Text("B", font_size=40).next_to(dot_b, UP)
        
        # Render directly in 3D space
        self.play(FadeIn(dot_a), FadeIn(lbl_a), FadeIn(dot_b), FadeIn(lbl_b))

        # Show independent causality
        packet_a = Packet(angle=-15 * DEGREES, c=c_speed)
        packet_a.add_updater(packet_a.update_packet)
        self.add(packet_a)
        self.wait(0.8) # Wait for impact

        text_info2 = Text("Spot B comes from the source,", color=YELLOW).scale_to_fit_width(7).next_to(text_info1, DOWN, buff=0.5)
        text_info3 = Text("NOT sideways from A.", color=RED).scale_to_fit_width(5).next_to(text_info2, DOWN)
        self.add_fixed_in_frame_mobjects(text_info2, text_info3)
        
        self.play(Write(text_info2))
        packet_b = Packet(angle=15 * DEGREES, c=c_speed)
        packet_b.add_updater(packet_b.update_packet)
        self.add(packet_b)
        
        self.play(Write(text_info3))
        self.wait(1.5)
        
        self.play(
            FadeOut(text_info1), FadeOut(text_info2), FadeOut(text_info3),
            FadeOut(dot_a), FadeOut(dot_b), FadeOut(lbl_a), FadeOut(lbl_b)
        )

        # --------------------------------------------------
        # PART 5: FINAL PAYOFF (42 - 52s)
        # --------------------------------------------------
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, run_time=1.5)
        
        # Re-initialize continuous beam
        theta.set_value(-max_angle)
        beam.history.clear()
        beam.current_t = 0
        beam.is_active = True
        trail.trail_dots.clear()
        v_counter.add_updater(v_counter.update_val)
        trail.add_updater(trail.update_trail)
        
        self.add(beam, trail, v_counter)

        text_final1 = Text("A PATTERN CAN MOVE", weight=BOLD).scale_to_fit_width(7.5).move_to(UP * 1.5)
        text_final2 = Text("FASTER THAN LIGHT.", weight=BOLD, color=YELLOW).scale_to_fit_width(7.5).next_to(text_final1, DOWN)
        text_final3 = Text("INFORMATION CANNOT.", weight=BOLD, color=RED).scale_to_fit_width(7.5).next_to(text_final2, DOWN * 1.5)

        # Final sweep demonstrating >1.5c
        self.play(theta.animate.set_value(max_angle), Write(text_final1), run_time=0.6, rate_func=linear)
        self.play(theta.animate.set_value(-max_angle), Write(text_final2), run_time=0.6, rate_func=linear)
        self.play(theta.animate.set_value(max_angle), Write(text_final3), run_time=0.6, rate_func=linear)
        
        self.play(theta.animate.set_value(0), run_time=1, rate_func=smooth)
        self.wait(2)
