import math
from contextlib import contextmanager


class PartSketchMethods:
    def add_sketch(self, planar_entity, name=None):
        sketch = self.sketches.Add(planar_entity)

        if name:
            sketch.Name = name

        return sketch

    def all_sketches(self, component_definition=None):
        """Return all sketches from a part component definition."""
        component_definition = component_definition or self.part_component_definition
        sketches = component_definition.Sketches

        return [sketches.Item(index) for index in range(1, sketches.Count + 1)]

    def sketches_by_prefix(self, prefix, component_definition=None):
        """Return sketches whose names start with prefix."""
        return [
            sketch
            for sketch in self.all_sketches(component_definition)
            if self.safe_getattr(sketch, "Name", "").startswith(prefix)
        ]

    def unique_sketch_name(self, base, sketches=None):
        """Return an available sketch name based on base."""
        sketches = sketches if sketches is not None else self.all_sketches()
        existing_names = {
            sketch.Name for sketch in sketches if hasattr(sketch, "Name")
        }

        if base not in existing_names:
            return base

        index = 1
        while True:
            name = f"{base}_{index}"
            if name not in existing_names:
                return name

            index += 1

    def sketch_on_face_plane(self, face, prefix=None, offsets=None, sketches=None):
        sketches = sketches or self.comp.Sketches

        for index in range(1, sketches.Count + 1):
            sketch = sketches.Item(index)

            try:
                if prefix is not None and not sketch.Name.startswith(prefix):
                    continue
                if self.same_plane_entity(sketch.PlanarEntity, face, offsets):
                    return sketch
            except Exception:
                continue

        return None

    def sketch_on_offset_face_plane(self, face, prefix, offset_value, sketches=None):
        return self.sketch_on_face_plane(
            face,
            prefix=prefix,
            offsets=[offset_value],
            sketches=sketches,
        )

    def get_or_create_sketch_on_face(
        self,
        face,
        name=None,
        prefix=None,
        offsets=None,
    ):
        sketch = self.sketch_on_face_plane(
            face,
            prefix=prefix,
            offsets=offsets,
        )

        if sketch is not None:
            return sketch

        return self.add_sketch(face, name=name)

    @staticmethod
    def model_to_sketch_point(sketch, point_3d):
        """Преобразовать одну 3D-точку модели в 2D-точку эскиза."""
        return sketch.ModelToSketchSpace(point_3d)

    def model_to_sketch_points(self, sketch, points_3d):
        """Преобразовать список 3D-точек модели в 2D-точки эскиза."""
        return [self.model_to_sketch_point(sketch, point) for point in points_3d]

    def face_vertex_points_in_sketch(self, face, sketch):
        """Вернуть вершины грани в координатах указанного эскиза."""
        return self.model_to_sketch_points(sketch, self.face_vertex_points(face))

    def selected_face_vertex_points_xy(
        self,
        sketch_name="Face vertices",
        debug=False,
    ):
        """Return selected face vertices as plain sketch-space (x, y) tuples."""
        face = self.selected_face(debug=debug)
        sketch = self.add_sketch(face, name=sketch_name)
        points = self.face_vertex_points_in_sketch(face, sketch)

        return [(point.X, point.Y) for point in points]

    def selected_face_vertex_report(
        self,
        sketch_name="Face vertices",
        debug=False,
    ):
        """Return document name and selected face vertices as plain Python data."""
        points = self.selected_face_vertex_points_xy(
            sketch_name=sketch_name,
            debug=debug,
        )

        return {
            "document": self.active_document_name(),
            "vertex_count": len(points),
            "points": points,
        }

    def model_to_sketch_points_from_vertices(self, sketch, vertices):
        """Convert vertices.Item(...).Point values to sketch 2D points."""
        return self.model_to_sketch_points(
            sketch,
            [vertices.Item(index).Point for index in range(1, vertices.Count + 1)],
        )

    @staticmethod
    def sketch_to_model_points(sketch, sketch_points):
        """Convert SketchPoint.Geometry values to model-space 3D points."""
        return [
            sketch.SketchToModelSpace(sketch_point.Geometry)
            for sketch_point in sketch_points
        ]

    @staticmethod
    def sketch_points_to_model(sketch, sketch_points):
        """Alias for converting SketchPoint objects to model-space 3D points."""
        return [
            sketch.SketchToModelSpace(sketch_point.Geometry)
            for sketch_point in sketch_points
        ]

    def face_bounds_in_sketch(self, face, sketch):
        """
        Вернуть границы грани в координатах эскиза:
        min_x, max_x, min_y, max_y.
        """
        points = self.face_vertex_points_in_sketch(face, sketch)

        if not points:
            raise ValueError("Face has no vertices")

        xs = [point.X for point in points]
        ys = [point.Y for point in points]

        return min(xs), max(xs), min(ys), max(ys)

    def face_center_in_sketch(self, face, sketch):
        """Вернуть геометрический центр вершин грани в координатах эскиза."""
        points = self.face_vertex_points_in_sketch(face, sketch)
        count = len(points)

        if count < 1:
            raise ValueError("Face has no vertices")

        center_x = sum(point.X for point in points) / count
        center_y = sum(point.Y for point in points) / count

        return self.create_point2d(center_x, center_y)

    @staticmethod
    def add_sketch_point(sketch, point_2d, hole_center=False):
        """Добавить точку в эскиз."""
        sketch_point = sketch.SketchPoints.Add(point_2d, hole_center)

        if hole_center:
            try:
                sketch_point.HoleCenter = True
            except Exception:
                pass

        return sketch_point

    def sketch_points(self, sketch, hole_center=None):
        """Return SketchPoint objects from sketch.SketchPoints."""
        points = [
            sketch.SketchPoints.Item(index)
            for index in range(1, sketch.SketchPoints.Count + 1)
        ]

        if hole_center is None:
            return points

        return [
            point
            for point in points
            if bool(self.safe_getattr(point, "HoleCenter", False)) is hole_center
        ]

    @staticmethod
    def sketch_point_count(sketch):
        """Return sketch.SketchPoints.Count."""
        return sketch.SketchPoints.Count

    @staticmethod
    def set_point_hole_center(point, hole_center=True):
        """Safely set point.HoleCenter."""
        try:
            point.HoleCenter = hole_center
        except Exception:
            return None

        return point

    def create_point2d(self, x, y):
        """Создать 2D-точку через TransientGeometry."""
        return self.transient_geometry.CreatePoint2d(x, y)

    def create_point3d(self, x, y, z):
        """Create a 3D point through TransientGeometry."""
        return self.transient_geometry.CreatePoint(x, y, z)

    @staticmethod
    def project_point_to_plane(point, planar_entity):
        """Project a 3D point to a planar entity, face, or work plane."""
        project_point = getattr(planar_entity, "ProjectPoint", None)
        if project_point is not None:
            return project_point(point)

        geometry = getattr(planar_entity, "Geometry", None)
        project_point = getattr(geometry, "ProjectPoint", None)
        if project_point is not None:
            return project_point(point)

        evaluator = getattr(planar_entity, "Evaluator", None)
        closest_point = getattr(evaluator, "GetClosestPointTo", None)
        if closest_point is not None:
            return closest_point(point)

        raise AttributeError("Planar entity does not support point projection")

    def project_points_to_plane(self, points, planar_entity):
        return [self.project_point_to_plane(point, planar_entity) for point in points]

    def offset_model_points_from_face(self, face, points, offset, direction=-1):
        normal = self.face_normal(face)
        signed_offset = offset * direction

        return [
            self.create_point3d(
                point.X + normal.X * signed_offset,
                point.Y + normal.Y * signed_offset,
                point.Z + normal.Z * signed_offset,
            )
            for point in points
        ]

    @staticmethod
    def solve_sketch(sketch, ignore_errors=True):
        """Выполнить Solve() для эскиза."""
        try:
            return sketch.Solve()
        except Exception:
            if not ignore_errors:
                raise

            return None

    def project_face_edges(self, sketch, face, ignore_errors=True):
        """Спроецировать ребра грани в эскиз и вернуть число успешных проекций."""
        projected_count = 0

        for edge in self.face_edges(face):
            if self.project_entity_to_sketch(
                sketch,
                edge,
                ignore_errors=ignore_errors,
            ):
                projected_count += 1

        return projected_count

    def project_entity_to_sketch(
        self,
        sketch,
        entity,
        construction=None,
        ignore_errors=False,
    ):
        """Project an edge, point, or entity into a sketch."""
        try:
            projected = sketch.AddByProjectingEntity(entity)
        except Exception:
            if not ignore_errors:
                raise

            return None

        if construction is not None:
            self.set_entity_construction(projected, construction)

        return projected

    @staticmethod
    def sketch_line_count(sketch):
        """Вернуть количество линий эскиза."""
        return sketch.SketchLines.Count

    @staticmethod
    def sketch_has_lines_or_points(sketch):
        """Return True when a sketch has lines or points."""
        return sketch.SketchLines.Count > 0 or sketch.SketchPoints.Count > 0

    def sketch_has_geometry_for_face(self, sketch, face, tol=0.01):
        return len(self.sketch_lines_for_face(sketch, face, tol=tol)) >= 2

    def sketch_lines(self, sketch, construction=None):
        """
        Вернуть линии эскиза.
        Если construction=True, только вспомогательные.
        Если construction=False, только обычные.
        Если None, все линии.
        """
        lines = [
            sketch.SketchLines.Item(index)
            for index in range(1, sketch.SketchLines.Count + 1)
        ]

        if construction is None:
            return lines

        return [
            line
            for line in lines
            if bool(self.safe_getattr(line, "Construction", False)) is construction
        ]

    def add_sketch_line(self, sketch, start_point, end_point, construction=False):
        """Create a sketch line through SketchLines.AddByTwoPoints."""
        line = sketch.SketchLines.AddByTwoPoints(start_point, end_point)
        self.set_entity_construction(line, construction)
        return line

    @staticmethod
    def set_entity_construction(entity, construction=True):
        """Safely set entity.Construction."""
        try:
            entity.Construction = construction
        except Exception:
            return None

        return entity

    def sketch_lines_for_face(self, sketch, face, first_new_line=0, tol=0.01):
        """Вернуть линии эскиза, относящиеся к указанной грани."""
        min_x, max_x, min_y, max_y = self.face_bounds_in_sketch(face, sketch)
        result = []

        for line in self.sketch_lines(sketch)[first_new_line:]:
            start = self.safe_getattr(line, "StartSketchPoint")
            end = self.safe_getattr(line, "EndSketchPoint")
            start_point = self.safe_getattr(start, "Geometry", start)
            end_point = self.safe_getattr(end, "Geometry", end)

            if start_point is None or end_point is None:
                continue

            if (
                min_x - tol <= start_point.X <= max_x + tol
                and min_y - tol <= start_point.Y <= max_y + tol
                and min_x - tol <= end_point.X <= max_x + tol
                and min_y - tol <= end_point.Y <= max_y + tol
            ):
                result.append(line)

        return result

    @staticmethod
    def distance_2d(point1, point2):
        """Расстояние между двумя 2D-точками."""
        return math.hypot(point2.X - point1.X, point2.Y - point1.Y)

    def line_length(self, line):
        """Длина линии эскиза."""
        return self.distance_2d(
            line.StartSketchPoint.Geometry,
            line.EndSketchPoint.Geometry,
        )

    def line_midpoint(self, line):
        """Середина линии эскиза как Point2d."""
        start = line.StartSketchPoint.Geometry
        end = line.EndSketchPoint.Geometry

        return self.create_point2d((start.X + end.X) / 2, (start.Y + end.Y) / 2)

    @staticmethod
    def vector_length2d(dx, dy):
        return math.hypot(dx, dy)

    @staticmethod
    def line_data(line):
        start = line.StartSketchPoint.Geometry
        end = line.EndSketchPoint.Geometry
        return start, end, end.X - start.X, end.Y - start.Y

    def line_midpoint_xy(self, line):
        midpoint = self.line_midpoint(line)
        return midpoint.X, midpoint.Y

    def closest_point_on_line(self, point, line):
        start = line.StartSketchPoint.Geometry
        end = line.EndSketchPoint.Geometry
        dx = end.X - start.X
        dy = end.Y - start.Y
        length_squared = dx * dx + dy * dy

        if length_squared == 0:
            return start

        t = ((point.X - start.X) * dx + (point.Y - start.Y) * dy) / length_squared
        t = max(0, min(1, t))
        return self.create_point2d(start.X + t * dx, start.Y + t * dy)

    @staticmethod
    def point_inside_sketch_bounds(point_or_x_y, bounds, tol=0.01):
        min_x, max_x, min_y, max_y = bounds

        try:
            x = point_or_x_y.X
            y = point_or_x_y.Y
        except Exception:
            x, y = point_or_x_y

        return min_x - tol <= x <= max_x + tol and min_y - tol <= y <= max_y + tol

    def add_aligned_dimension(self, sketch, point1, point2, text_point, driven=False):
        """Добавить выровненный размер между двумя точками."""
        return self.add_two_point_dimension(
            sketch,
            point1,
            point2,
            "aligned",
            text_point,
            driven,
        )

    def sketch_dimension_constraints(self, sketch):
        """Return DimensionConstraints as a Python list."""
        constraints = sketch.DimensionConstraints
        return [
            constraints.Item(index)
            for index in range(1, constraints.Count + 1)
        ]

    @staticmethod
    def sketch_dimension_count(sketch):
        """Return sketch.DimensionConstraints.Count."""
        return sketch.DimensionConstraints.Count

    def add_two_point_dimension(
        self,
        sketch,
        point1,
        point2,
        orientation,
        text_point,
        driven=False,
        expression=None,
    ):
        """Wrapper for DimensionConstraints.AddTwoPointDistance."""
        dimension = sketch.DimensionConstraints.AddTwoPointDistance(
            point1,
            point2,
            self.dimension_orientation(orientation),
            text_point,
            driven,
        )

        if expression is not None:
            parameter = self.safe_getattr(dimension, "Parameter")
            if parameter is not None:
                parameter.Expression = expression

        return dimension

    @staticmethod
    def set_sketch_defer_updates(sketch, value):
        """Safely set sketch.DeferUpdates and return its previous value."""
        try:
            previous = sketch.DeferUpdates
            sketch.DeferUpdates = value
        except Exception:
            return None

        return previous

    @contextmanager
    def deferred_sketch_updates(self, sketch):
        """Temporarily enable DeferUpdates and restore the original value."""
        previous = self.set_sketch_defer_updates(sketch, True)
        try:
            yield sketch
        finally:
            if previous is not None:
                self.set_sketch_defer_updates(sketch, previous)

    @staticmethod
    def set_sketch_dimensions_visible(sketch, visible):
        """Safely set sketch.DimensionsVisible."""
        try:
            sketch.DimensionsVisible = visible
        except Exception:
            return None

        return sketch

    def hide_sketch_dimensions(self, sketch):
        return self.set_sketch_dimensions_visible(sketch, False)

    def show_sketch_dimensions(self, sketch):
        return self.set_sketch_dimensions_visible(sketch, True)

    @staticmethod
    def set_sketch_visible(sketch, visible):
        """Safely set sketch.Visible."""
        try:
            sketch.Visible = visible
        except Exception:
            return None

        return sketch

    def sketch_hole_center_points(self, sketch):
        return self.sketch_points(sketch, hole_center=True)

    @staticmethod
    def try_share_sketch(sketch):
        for attr in ("Shared", "Visible"):
            try:
                setattr(sketch, attr, True)
            except Exception:
                pass

        try:
            sketch.ShareSketch()
        except Exception:
            pass

        return sketch

    def solve_or_update_sketch(self, sketch):
        result = self.solve_sketch(sketch, ignore_errors=True)
        if result is not None:
            return result

        try:
            return sketch.Parent.Document.Update()
        except Exception:
            return self.update()

    def fix_sketch_entity(self, sketch, entity):
        return self.add_ground_constraint(sketch, entity, ignore_errors=True)

    def fix_sketch_points(self, sketch, points):
        return [self.fix_sketch_entity(sketch, point) for point in points]

    @staticmethod
    def _add_geometric_constraint(
        sketch,
        method_name,
        *args,
        ignore_errors=True,
    ):
        try:
            method = getattr(sketch.GeometricConstraints, method_name)
            return method(*args)
        except Exception:
            if not ignore_errors:
                raise

            return None

    def add_ground_constraint(self, sketch, entity, ignore_errors=True):
        """Add GeometricConstraints.AddGround(entity)."""
        return self._add_geometric_constraint(
            sketch,
            "AddGround",
            entity,
            ignore_errors=ignore_errors,
        )

    def add_midpoint_constraint(
        self,
        sketch,
        point_or_line_point,
        line,
        ignore_errors=True,
    ):
        """Wrapper for GeometricConstraints.AddMidpoint."""
        return self._add_geometric_constraint(
            sketch,
            "AddMidpoint",
            point_or_line_point,
            line,
            ignore_errors=ignore_errors,
        )

    def add_coincident_constraint(self, sketch, entity1, entity2, ignore_errors=True):
        """Wrapper for GeometricConstraints.AddCoincident."""
        return self._add_geometric_constraint(
            sketch,
            "AddCoincident",
            entity1,
            entity2,
            ignore_errors=ignore_errors,
        )

    def add_perpendicular_constraint(self, sketch, line1, line2, ignore_errors=True):
        """Wrapper for GeometricConstraints.AddPerpendicular."""
        return self._add_geometric_constraint(
            sketch,
            "AddPerpendicular",
            line1,
            line2,
            ignore_errors=ignore_errors,
        )

    def add_parallel_constraint(self, sketch, line1, line2, ignore_errors=True):
        """Wrapper for GeometricConstraints.AddParallel."""
        return self._add_geometric_constraint(
            sketch,
            "AddParallel",
            line1,
            line2,
            ignore_errors=ignore_errors,
        )

    def add_symmetry_constraint(
        self,
        sketch,
        entity1,
        entity2,
        symmetry_line,
        ignore_errors=True,
    ):
        """Wrapper for GeometricConstraints.AddSymmetry."""
        return self._add_geometric_constraint(
            sketch,
            "AddSymmetry",
            entity1,
            entity2,
            symmetry_line,
            ignore_errors=ignore_errors,
        )

    def create_work_plane_by_line_plane_angle(
        self,
        line,
        plane,
        angle,
        construction=True,
        component_definition=None,
    ):
        """Wrapper for WorkPlanes.AddByLinePlaneAndAngle."""
        component_definition = component_definition or self.part_component_definition
        return component_definition.WorkPlanes.AddByLinePlaneAndAngle(
            line,
            plane,
            angle,
            construction,
        )

    def add_offset_work_plane(
        self,
        face_or_plane,
        offset,
        name=None,
        visible=False,
        component_definition=None,
    ):
        component_definition = component_definition or self.part_component_definition
        work_plane = component_definition.WorkPlanes.AddByPlaneAndOffset(
            face_or_plane,
            offset,
        )

        if name:
            work_plane.Name = self.unique_work_plane_name(
                name,
                component_definition.WorkPlanes,
            )

        try:
            work_plane.Visible = visible
        except Exception:
            pass

        return work_plane

    def add_face_center_point(
        self,
        face,
        sketch=None,
        hole_center=True,
        sketch_name=None,
        prefix=None,
        offsets=None,
    ):
        sketch = sketch or self.get_or_create_sketch_on_face(
            face,
            name=sketch_name,
            prefix=prefix,
            offsets=offsets,
        )
        center = self.face_center_in_sketch(face, sketch)
        sketch_point = self.add_sketch_point(sketch, center, hole_center)
        self.solve_sketch(sketch)

        return sketch_point

    @staticmethod
    def unique_points(points):
        result = []
        seen = set()

        for point in points:
            geo = point.Geometry
            key = (round(geo.X, 6), round(geo.Y, 6))
            if key in seen:
                continue

            seen.add(key)
            result.append(point)

        return result

    @staticmethod
    def mark_as_hole_centers(points):
        for point in points:
            try:
                point.HoleCenter = True
            except Exception:
                pass
