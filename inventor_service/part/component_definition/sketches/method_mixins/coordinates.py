class PartSketchCoordinateMethods:
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

    def create_point2d(self, x, y):
        """Создать 2D-точку через TransientGeometry."""
        return self.transient_geometry.CreatePoint2d(x, y)

    def create_point3d(self, x, y, z):
        """Create a 3D point through TransientGeometry."""
        return self.transient_geometry.CreatePoint(x, y, z)
