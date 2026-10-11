import math


class PartSketchMethods:
    def add_sketch(self, planar_entity, name=None):
        sketch = self.sketches.Add(planar_entity)

        if name:
            sketch.Name = name

        return sketch

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

    def create_point2d(self, x, y):
        """Создать 2D-точку через TransientGeometry."""
        return self.transient_geometry.CreatePoint2d(x, y)

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
            try:
                sketch.AddByProjectingEntity(edge)
            except Exception:
                if not ignore_errors:
                    raise
                continue

            projected_count += 1

        return projected_count

    @staticmethod
    def sketch_line_count(sketch):
        """Вернуть количество линий эскиза."""
        return sketch.SketchLines.Count

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

    def add_aligned_dimension(self, sketch, point1, point2, text_point, driven=False):
        """Добавить выровненный размер между двумя точками."""
        return sketch.DimensionConstraints.AddTwoPointDistance(
            point1,
            point2,
            self.ALIGNED_DIMENSION,
            text_point,
            driven,
        )

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
