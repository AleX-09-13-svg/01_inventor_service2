import math


class PartSketchPointMethods:
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

    def sketch_hole_center_points(self, sketch):
        return self.sketch_points(sketch, hole_center=True)

    def add_face_center_point(
        self,
        face,
        sketch=None,
        hole_center=True,
        sketch_name=None,
        prefix=None,
        offsets=None,
    ):
        """Добавить зависимый центр прямоугольной грани или параллелограмма.

        Центр привязан к середине вспомогательной диагонали проекций ребер.
        Существующие эскизы не ищутся. Параметры prefix и offsets
        сохранены для совместимости и не используются.
        """
        edges = self._face_center_boundary_edges(face)
        transaction = self.app.TransactionManager.StartTransaction(
            self.active_document, "Add constrained face center"
        )
        try:
            if sketch is None:
                sketch = self.add_sketch(face, name=sketch_name)
            projected = [
                self.project_entity_to_sketch(sketch, edge) for edge in edges
            ]
            corners = []
            for line in projected:
                for point in (line.StartSketchPoint, line.EndSketchPoint):
                    if not any(
                        self.distance_2d(point.Geometry, other.Geometry) < 1e-7
                        for other in corners
                    ):
                        corners.append(point)
            if len(corners) != 4:
                raise ValueError("Face boundary must have four distinct corners")

            center_x = sum(point.Geometry.X for point in corners) / 4
            center_y = sum(point.Geometry.Y for point in corners) / 4
            corners.sort(key=lambda point: math.atan2(
                point.Geometry.Y - center_y, point.Geometry.X - center_x
            ))
            midpoint1 = self.create_point2d(
                (corners[0].Geometry.X + corners[2].Geometry.X) / 2,
                (corners[0].Geometry.Y + corners[2].Geometry.Y) / 2,
            )
            midpoint2 = self.create_point2d(
                (corners[1].Geometry.X + corners[3].Geometry.X) / 2,
                (corners[1].Geometry.Y + corners[3].Geometry.Y) / 2,
            )
            scale = max(
                self.distance_2d(corners[0].Geometry, point.Geometry)
                for point in corners[1:]
            )
            if self.distance_2d(midpoint1, midpoint2) > max(1e-7, scale * 1e-7):
                raise ValueError("Face boundary must be a rectangle or parallelogram")

            diagonal = self.add_sketch_line(
                sketch, corners[0], corners[2], construction=True
            )
            sketch_point = self.add_sketch_point(sketch, midpoint1, hole_center)
            self.add_midpoint_constraint(
                sketch, sketch_point, diagonal, ignore_errors=False
            )
            self.solve_sketch(sketch, ignore_errors=False)
            transaction.End()
        except Exception:
            transaction.Abort()
            raise

        return sketch_point

    @staticmethod
    def _face_center_boundary_edges(face):
        """Проверить внешний четырехсторонний прямолинейный контур."""
        loops = face.EdgeLoops
        outer_loops = [
            loops.Item(index)
            for index in range(1, loops.Count + 1)
            if loops.Item(index).IsOuterEdgeLoop
        ]
        if len(outer_loops) != 1:
            raise ValueError("Face must have a single outer boundary")
        boundary = outer_loops[0].Edges
        edges = [boundary.Item(index) for index in range(1, boundary.Count + 1)]
        # CurveTypeEnum: kLineCurve = 5122, kLineSegmentCurve = 5123.
        if len(edges) != 4 or any(edge.GeometryType not in (5122, 5123) for edge in edges):
            raise ValueError("Face boundary must have four straight edges")
        return edges

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
