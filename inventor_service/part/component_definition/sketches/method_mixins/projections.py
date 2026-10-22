class PartSketchProjectionMethods:
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
