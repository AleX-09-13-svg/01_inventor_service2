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
        vertices = face.Vertices
        count = vertices.Count

        if count < 1:
            raise ValueError("Face has no vertices")

        center_x = 0
        center_y = 0

        for index in range(1, count + 1):
            point = sketch.ModelToSketchSpace(vertices.Item(index).Point)
            center_x += point.X
            center_y += point.Y

        center = self.transient_geometry.CreatePoint2d(
            center_x / count,
            center_y / count,
        )
        sketch_point = sketch.SketchPoints.Add(center, hole_center)

        if hole_center:
            try:
                sketch_point.HoleCenter = True
            except Exception:
                pass

        try:
            sketch.Solve()
        except Exception:
            pass

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
