class PartGeometryMethods:
    @staticmethod
    def plane_geometry(entity):
        try:
            return entity.Geometry
        except Exception:
            return entity.Plane

    @classmethod
    def same_plane_entity(cls, entity1, entity2, offsets=None, tol=0.001):
        g1 = cls.plane_geometry(entity1)
        g2 = cls.plane_geometry(entity2)
        n1 = g1.Normal
        n2 = g2.Normal
        p1 = g1.RootPoint
        p2 = g2.RootPoint
        dot = n1.X * n2.X + n1.Y * n2.Y + n1.Z * n2.Z
        dist = (
            (p2.X - p1.X) * n1.X
            + (p2.Y - p1.Y) * n1.Y
            + (p2.Z - p1.Z) * n1.Z
        )

        if abs(abs(dot) - 1) > tol:
            return False

        for offset in offsets or [0]:
            try:
                if abs(abs(dist) - abs(offset)) <= tol:
                    return True
            except Exception:
                continue

        return False

    @classmethod
    def same_plane(cls, face1, face2, tol=0.001):
        return cls.same_plane_entity(face1, face2, [0], tol)

    @classmethod
    def group_faces_by_plane(cls, faces):
        groups = []

        for face in faces:
            for group in groups:
                if cls.same_plane(group[0], face):
                    group.append(face)
                    break
            else:
                groups.append([face])

        return groups
