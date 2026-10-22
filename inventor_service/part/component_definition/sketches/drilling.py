from .drilling_constants import (
    DRAWER_SKETCH_PREFIX,
    DRILLING_SKETCH_PREFIX,
    EDGE_OFFSET_DRAWER_PARAM,
    EDGE_OFFSET_FRAME_PARAM,
    EDGE_OFFSET_PARAM,
    GRID_STEP_CM,
    POINT_DISTANCE_PARAM,
)
from ....settings import drawer_edge_max_cm

SKETCH_YELLOW_RGB = (255, 220, 0)


class PartDrillingSketchMethods:
    def ensure_drilling_sketch_parameters(self):
        return not self.missing_parameters(
            (EDGE_OFFSET_FRAME_PARAM, EDGE_OFFSET_DRAWER_PARAM)
        )

    @staticmethod
    def edge_offset_param_for_length(long_edge_length):
        if long_edge_length <= drawer_edge_max_cm():
            return EDGE_OFFSET_DRAWER_PARAM

        return EDGE_OFFSET_FRAME_PARAM

    def create_construction_axes(self, sketch, short1, short2):
        center1 = self.line_midpoint(short1)
        center2 = self.line_midpoint(short2)
        distance = self.distance_2d(center1, center2)
        ux = (center2.X - center1.X) / distance
        uy = (center2.Y - center1.Y) / distance
        nx = -uy
        ny = ux

        axis = self.add_sketch_line(sketch, center1, center2, construction=True)
        self.add_midpoint_constraint(sketch, axis.StartSketchPoint, short1)
        self.add_midpoint_constraint(sketch, axis.EndSketchPoint, short2)

        center = self.create_point2d(
            (center1.X + center2.X) / 2,
            (center1.Y + center2.Y) / 2,
        )
        symmetry_axis = self.add_sketch_line(
            sketch,
            self.create_point2d(center.X - nx, center.Y - ny),
            self.create_point2d(center.X + nx, center.Y + ny),
            construction=True,
        )
        self.add_perpendicular_constraint(sketch, axis, symmetry_axis)
        self.add_midpoint_constraint(sketch, symmetry_axis.StartSketchPoint, axis)

        return axis, symmetry_axis, center, distance, ux, uy, nx, ny

    def create_drilling_points(self, sketch, center, ux, uy, point_distance_value):
        outer = point_distance_value / 2
        inner = outer - GRID_STEP_CM

        left_outer = self.add_sketch_point(
            sketch,
            self.create_point2d(center.X - ux * outer, center.Y - uy * outer),
        )
        right_outer = self.add_sketch_point(
            sketch,
            self.create_point2d(center.X + ux * outer, center.Y + uy * outer),
        )
        left_inner = self.add_sketch_point(
            sketch,
            self.create_point2d(center.X - ux * inner, center.Y - uy * inner),
        )
        right_inner = self.add_sketch_point(
            sketch,
            self.create_point2d(center.X + ux * inner, center.Y + uy * inner),
        )
        center_point = self.add_sketch_point(sketch, center)

        return left_outer, right_outer, left_inner, right_inner, center_point, outer

    def constrain_drilling_points(self, sketch, axis, symmetry_axis, points):
        left_outer, right_outer, left_inner, right_inner, center_point, _ = points

        for point in (left_outer, right_outer, left_inner, right_inner, center_point):
            self.add_coincident_constraint(sketch, point, axis)

        self.add_coincident_constraint(sketch, center_point, symmetry_axis)
        self.add_symmetry_constraint(sketch, left_outer, right_outer, symmetry_axis)
        self.add_symmetry_constraint(sketch, left_inner, right_inner, symmetry_axis)

    def add_side_plane_reference_line(self, sketch, axis, lines):
        long_edges = sorted(lines, key=self.line_length_squared, reverse=True)[:2]
        if not long_edges:
            return None

        start = axis.StartSketchPoint.Geometry
        end = axis.EndSketchPoint.Geometry
        reference = self.create_point2d((start.X + end.X) / 2, (start.Y + end.Y) / 2)
        target = min(
            long_edges,
            key=lambda line: self.closest_point_on_line(reference, line).Y,
        )
        end_point = self.closest_point_on_line(reference, target)
        line = self.add_sketch_line(sketch, reference, end_point, construction=True)

        self.add_perpendicular_constraint(sketch, line, axis)

        return line

    @staticmethod
    def set_parameter_name(parameter_owner, name):
        parameter_owner.Parameter.Name = name
        return parameter_owner.Parameter.Name

    @staticmethod
    def set_parameter_expression(parameter_owner, expression):
        parameter_owner.Parameter.Expression = expression
        return parameter_owner.Parameter.Expression

    def add_drilling_dimensions(
        self,
        sketch,
        axes,
        points,
        index,
        edge_offset_param,
    ):
        axis, _, center, _, ux, uy, nx, ny = axes
        left_outer, right_outer, left_inner, _, _, outer = points

        long_dim = self.add_aligned_dimension(
            sketch,
            axis.StartSketchPoint,
            axis.EndSketchPoint,
            self.create_point2d(center.X + nx * 4, center.Y + ny * 4),
            True,
        )
        point_distance_dim = self.add_aligned_dimension(
            sketch,
            right_outer,
            left_outer,
            self.create_point2d(center.X + nx * 2, center.Y + ny * 2),
        )
        inset_dim = self.add_aligned_dimension(
            sketch,
            left_outer,
            left_inner,
            self.create_point2d(
                center.X - ux * (outer - 1.6) + nx * 2,
                center.Y - uy * (outer - 1.6) + ny * 2,
            ),
        )

        long_dim.Parameter.Name = self.unique_parameter_name(
            f"Long_edge_{index}",
            self.parameters,
        )
        point_distance_dim.Parameter.Name = self.unique_parameter_name(
            POINT_DISTANCE_PARAM,
            self.parameters,
        )
        point_distance_dim.Parameter.Expression = (
            f"floor(({long_dim.Parameter.Name} - {edge_offset_param} * 2) / 32 mm) * 32 mm"
        )
        inset_dim.Parameter.Expression = "32 mm"

    @staticmethod
    def line_length_squared(line):
        start = line.StartSketchPoint.Geometry
        end = line.EndSketchPoint.Geometry
        dx = end.X - start.X
        dy = end.Y - start.Y
        return dx * dx + dy * dy

    def create_drilling_sketch(
        self,
        sketch,
        face,
        index,
        edge_offset_param=EDGE_OFFSET_PARAM,
    ):
        first_new_line = sketch.SketchLines.Count
        self.project_face_edges(sketch, face)
        lines = self.sketch_lines_for_face(sketch, face, first_new_line)

        if len(lines) < 2:
            return False

        short1, short2 = sorted(lines, key=self.line_length_squared)[:2]
        axes = self.create_construction_axes(sketch, short1, short2)
        _, _, _, long_edge_length, _, _, _, _ = axes
        if callable(edge_offset_param):
            edge_offset_param = edge_offset_param(long_edge_length)
        elif edge_offset_param is None:
            edge_offset_param = self.edge_offset_param_for_length(long_edge_length)

        edge_offset_value = self.parameter_value(edge_offset_param, 10)
        point_distance_value = (
            int((long_edge_length - edge_offset_value * 2) / GRID_STEP_CM)
            * GRID_STEP_CM
        )
        point_distance_value = max(point_distance_value, GRID_STEP_CM * 2)

        points = self.create_drilling_points(
            sketch,
            axes[2],
            axes[4],
            axes[5],
            point_distance_value,
        )
        self.constrain_drilling_points(sketch, axes[0], axes[1], points)
        self.add_side_plane_reference_line(sketch, axes[0], lines)
        self.add_drilling_dimensions(sketch, axes, points, index, edge_offset_param)

        return True

    def create_drilling_sketches_for_faces(
        self,
        faces,
        sketch_prefix=DRILLING_SKETCH_PREFIX,
        edge_offset_param=None,
        sketch_label="Drilling",
        face_label="Selected drilling",
        reuse_existing=True,
    ):
        groups = self.group_faces_by_plane(faces)

        print(f"{face_label} faces:", len(faces))
        print(f"{sketch_label} sketch planes:", len(groups))

        count = 0
        created_sketches = 0
        reused_sketches = 0
        skipped_faces = 0
        sketches = []

        for group_index, group in enumerate(groups, start=1):
            sketch = None
            if reuse_existing:
                sketch = self.sketch_on_face_plane(
                    group[0],
                    prefix=sketch_prefix,
                )
            if sketch is None:
                sketch = self.add_sketch(group[0])
                sketch.Name = self.unique_sketch_name(
                    f"{sketch_prefix}_{group_index}"
                )
                created_sketches += 1
            else:
                reused_sketches += 1
                print(f"Using existing {sketch_label} sketch on plane:", sketch.Name)

            sketches.append(sketch)

            if self.set_sketch_color_rgb(
                sketch,
                SKETCH_YELLOW_RGB,
                include_entities=False,
            ):
                print(f"  {sketch_label} sketch color set:", sketch.Name)
            else:
                print(f"  {sketch_label} sketch color not set:", sketch.Name)

            group_processed = 0
            with self.deferred_sketch_updates(sketch):
                for face in group:
                    if self.sketch_has_geometry_for_face(sketch, face):
                        skipped_faces += 1
                        print(f"  {sketch_label} face geometry already exists, skipped")
                        continue

                    if self.create_drilling_sketch(
                        sketch,
                        face,
                        count + 1,
                        edge_offset_param=edge_offset_param,
                    ):
                        count += 1
                        group_processed += 1

            if group_processed:
                self.hide_sketch_dimensions(sketch)

        print(f"{sketch_label} faces processed:", count)
        print(f"{sketch_label} sketches created:", created_sketches)
        print(f"{sketch_label} sketches reused:", reused_sketches)
        print(f"{sketch_label} faces skipped:", skipped_faces)

        return {
            "processed": count,
            "created_sketches": created_sketches,
            "reused_sketches": reused_sketches,
            "skipped_faces": skipped_faces,
            "sketches": sketches,
        }

    def create_drawer_drilling_sketches_for_faces(self, faces, **kwargs):
        kwargs.setdefault("sketch_prefix", DRAWER_SKETCH_PREFIX)
        kwargs.setdefault("sketch_label", "Drawer")
        kwargs.setdefault("face_label", "Selected drawer")
        return self.create_drilling_sketches_for_faces(faces, **kwargs)
