import numpy as np
from manim import *
import os
input_path = os.getenv("MANIM_INPUT_PATH", "user_input.txt")


def check_zero_decimal(coords):
    s = str(coords)
    s = s.split('.')[1]
    return int(coords) if int(s) == 0 else coords

class ChangeOfBasis_Clean(LinearTransformationScene):
    def __init__(self, **kwargs):
        super().__init__(include_background_plane=False,
                         include_foreground_plane=False,
                         show_coordinates=False,
                         show_basis_vectors=False,
                         **kwargs)
        

    def get_matrix_from_file(self):
        with open(input_path, "r") as f:
            matrix = eval(f.readline().strip())
            return matrix

    def construct(self):
        matrix = self.get_matrix_from_file()
        grid_gaps = 1
        scale = 1

        custom_grid = NumberPlane(
            x_range=[-9, 9, grid_gaps],
            y_range=[-9, 9, grid_gaps],
            background_line_style={"stroke_color": GREY, "stroke_width": 2, "stroke_opacity": 0.85}
        ).scale(scale)

        foreground_plane = NumberPlane(
            x_range=[-20, 20, grid_gaps],
            y_range=[-20, 20, grid_gaps],
            background_line_style={"stroke_color": BLUE, "stroke_width": 2, "stroke_opacity": 0.8}
        ).scale(scale)

        origin = custom_grid.coords_to_point(0, 0)
        i_vector = Vector([grid_gaps, 0], color=RED, buff=0, tip_length=0)
        j_vector = Vector([0, grid_gaps], color=GREEN, buff=0, tip_length=0)
        i_vector.put_start_and_end_on(origin, custom_grid.coords_to_point(grid_gaps, 0))
        j_vector.put_start_and_end_on(origin, custom_grid.coords_to_point(0, grid_gaps))

        self.add(custom_grid)
        self.add_transformable_mobject(Group(foreground_plane, i_vector, j_vector))
        foreground_plane.set_z_index(0)
        custom_grid.set_z_index(-1).add_coordinates()

        self.wait(0.4)
        self.apply_matrix(matrix, run_time=4)
        self.wait()