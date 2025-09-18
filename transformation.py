import numpy as np
from manim import *
import math
import os
input_path = os.getenv("MANIM_INPUT_PATH", "user_input.txt")


def check_zero_decimal(coords):
    s = str(coords)
    s = s.split('.')[1]
    return int(coords) if int(s) == 0 else coords

def get_inputs_from_file():
    with open(input_path, "r") as f:
        matrix = eval(f.readline().strip())
        vector = eval(f.readline().strip())
        return matrix, vector

class Transformation_Clean(LinearTransformationScene):
    def __init__(self, **kwargs):
        super().__init__(include_background_plane=False,
                         include_foreground_plane=False,
                         show_coordinates=False,
                         show_basis_vectors=False,
                         **kwargs)
        

    def construct(self):
        matrix, vector = get_inputs_from_file()
        vecx, vecy = abs(vector[0]), abs(vector[1])
        vector_length = math.sqrt(vecx ** 2 + vecy ** 2)
        plane_length_fake = max(vector_length * 5, 8)
        plane_length_show = plane_length_fake * 4
        scale = 7 / plane_length_fake
        grid_gaps = max(1, int(plane_length_fake // 7))

        matrix_array, vector_array = np.array(matrix), np.array(vector)
        transformed_vector = matrix_array.dot(vector_array)
        transformed_x, transformed_y = transformed_vector

        custom_grid = NumberPlane(
            x_range=[-plane_length_show, plane_length_show, grid_gaps],
            y_range=[-plane_length_show, plane_length_show, grid_gaps],
            background_line_style={"stroke_color": GREY, "stroke_width": 2, "stroke_opacity": 0.85}
        ).scale(scale)

        origin = custom_grid.coords_to_point(0, 0)
        user_vector = Vector(vector, color=YELLOW, buff=0, tip_length=0)
        user_vector.put_start_and_end_on(origin, custom_grid.coords_to_point(*vector))

        updated_plane_length = math.sqrt(transformed_x**2 + transformed_y**2) + 10 * grid_gaps
        updated_grid = NumberPlane(
            x_range=[-updated_plane_length, updated_plane_length, grid_gaps],
            y_range=[-updated_plane_length, updated_plane_length, grid_gaps],
            background_line_style={"stroke_color": GREY, "stroke_width": 2, "stroke_opacity": 0.85}
        ).scale(scale)

        i_vector = Vector([grid_gaps, 0], color=RED, buff=0, tip_length=0)
        j_vector = Vector([0, grid_gaps], color=GREEN, buff=0, tip_length=0)
        i_vector.put_start_and_end_on(origin, updated_grid.coords_to_point(grid_gaps, 0))
        j_vector.put_start_and_end_on(origin, updated_grid.coords_to_point(0, grid_gaps))

        vector_text = MathTex(f"({check_zero_decimal(round(transformed_x, 2))},"
                              f"{check_zero_decimal(round(transformed_y, 2))})")
        group_transformable = Group(i_vector, j_vector, user_vector)
        group_all = Group(updated_grid, group_transformable)

        self.add(updated_grid)
        self.add_transformable_mobject(group_transformable)
        updated_grid.set_z_index(-1).add_coordinates()

        self.wait(0.4)
        self.apply_matrix(matrix, run_time=4)

        offset_x = 1 if transformed_x >= 0 else -1
        offset_y = 1 if transformed_y >= 0 else -1
        vector_text.set_x(offset_x)
        vector_text.set_y(offset_y)

        new_position = updated_grid.coords_to_point(-transformed_x, -transformed_y, 0)
        self.play(ApplyMethod(group_all.move_to, new_position, run_time=1.5))
        self.play(GrowFromPoint(vector_text, ORIGIN, run_time=1))
        self.wait()