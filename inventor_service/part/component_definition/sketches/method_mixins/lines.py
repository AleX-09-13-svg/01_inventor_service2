import math


class PartSketchLineMethods:
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
