from manim import *
import numpy as np

class CrossProduct(Scene):
    def construct(self):


        vector_a = np.array([1, 2, 3])
        vector_b = np.array([4, 5, 6])

        
        max_len = max(np.linalg.norm(vector_a[:2]), np.linalg.norm(vector_b[:2]))
        scale = 3 / max_len if max_len > 0 else 1  

        a_scaled = vector_a[:2] * scale
        b_scaled = vector_b[:2] * scale

        
        arrow_a = Arrow(start=ORIGIN, end=[a_scaled[0], a_scaled[1], 0], buff=0, color=GREEN)
        arrow_b = Arrow(start=ORIGIN, end=[b_scaled[0], b_scaled[1], 0], buff=0, color=RED)

        self.play(GrowArrow(arrow_a))
        self.play(GrowArrow(arrow_b))

        
        result = vector_a[0]*vector_b[1] - vector_a[1]*vector_b[0]

        
        parallelogram = Polygon(
            ORIGIN,
            [a_scaled[0], a_scaled[1], 0],
            [a_scaled[0]+b_scaled[0], a_scaled[1]+b_scaled[1], 0],
            [b_scaled[0], b_scaled[1], 0],
            color=YELLOW,
            fill_opacity=0.3
        )
        self.play(Create(parallelogram))

        
        cross_text = MathTex(f"{result}").move_to(parallelogram.get_center())
        self.play(Write(cross_text))
