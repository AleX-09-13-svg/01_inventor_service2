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
    def same_offset_plane_entity(cls, entity, face, offset_value, tol=0.001):
        return cls.same_plane_entity(entity, face, [offset_value], tol)

    @classmethod
    def plane_key(cls, entity, tol=0.001):
        geometry = cls.plane_geometry(entity)
        normal = geometry.Normal
        root = geometry.RootPoint
        values = [normal.X, normal.Y, normal.Z]

        for value in values:
            if abs(value) > tol:
                sign = -1 if value < 0 else 1
                break
        else:
            sign = 1

        nx, ny, nz = (value * sign for value in values)
        distance = (nx * root.X + ny * root.Y + nz * root.Z)
        precision = max(0, len(str(tol).split(".")[-1]))

        return (
            round(nx, precision),
            round(ny, precision),
            round(nz, precision),
            round(distance, precision),
        )

    @classmethod
    def group_faces_by_plane(cls, faces):
        groups_by_key = {}
        fallback_faces = []

        for face in faces:
            try:
                key = cls.plane_key(face)
            except Exception:
                fallback_faces.append(face)
                continue

            groups_by_key.setdefault(key, []).append(face)

        groups = list(groups_by_key.values())

        for face in fallback_faces:
            for group in groups:
                if cls.same_plane(group[0], face):
                    group.append(face)
                    break
            else:
                groups.append([face])

        return groups

    @classmethod
    def plane_normal(cls, entity):
        return cls.plane_geometry(entity).Normal

    @classmethod
    def face_normal(cls, face):
        return cls.plane_normal(face)

    @classmethod
    def plane_root_point(cls, entity):
        return cls.plane_geometry(entity).RootPoint
