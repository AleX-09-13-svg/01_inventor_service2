class PartFaceMethods:
    @staticmethod
    def _collection_items(collection):
        return [collection.Item(index) for index in range(1, collection.Count + 1)]

    @staticmethod
    def unique_faces(faces):
        result = []
        seen = set()

        for face in faces:
            try:
                key = face.ReferenceKey
            except Exception:
                key = id(face)

            if key in seen:
                continue

            seen.add(key)
            result.append(face)

        return result

    @staticmethod
    def is_face_like(obj):
        try:
            obj.Geometry
            obj.Edges.Count
            obj.Vertices.Count
        except Exception:
            return False

        return True

    @classmethod
    def face_from_selection_object(cls, obj):
        if cls.is_face_like(obj):
            return obj

        for attr in ("NativeObject", "ContainingFace", "SourceObject"):
            candidate = cls.safe_getattr(obj, attr)
            if cls.is_face_like(candidate):
                return candidate

        return None

    @staticmethod
    def selection_object_label(obj):
        labels = []

        for attr in ("Type", "ObjectType", "DisplayName", "Name"):
            try:
                labels.append(f"{attr}={getattr(obj, attr)}")
            except Exception:
                pass

        try:
            labels.append(f"class={obj.__class__.__name__}")
        except Exception:
            pass

        return ", ".join(labels) or "unknown object"

    def selected_faces(self, debug=False):
        faces = []

        try:
            count = self.select_set.Count
        except Exception as exc:
            if debug:
                print("Selection read failed:", exc)
            return faces

        if debug:
            print("Selected objects:", count)

        for index in range(1, count + 1):
            try:
                selected = self.select_set.Item(index)
            except Exception as exc:
                if debug:
                    print(f"  selection {index} read failed:", exc)
                continue

            face = self.face_from_selection_object(selected)
            if face is None:
                if debug:
                    print(
                        f"  selection {index} skipped:",
                        self.selection_object_label(selected),
                    )
                continue

            faces.append(face)

        return self.unique_faces(faces)

    def require_selected_faces(self, min_count=1, debug=False):
        """Вернуть выбранные грани или поднять понятную ошибку."""
        faces = self.selected_faces(debug=debug)

        if len(faces) < min_count:
            raise RuntimeError(
                f"Сначала выдели минимум {min_count} грань(и) детали в Inventor."
            )

        return faces

    def selected_face(self, debug=False):
        """Вернуть одну выбранную грань."""
        return self.require_selected_faces(1, debug=debug)[0]

    def selected_planar_face(self, debug=False):
        """Вернуть одну выбранную плоскую грань."""
        face = self.selected_face(debug=debug)

        try:
            geometry = self.plane_geometry(face)
            geometry.Normal
            geometry.RootPoint
        except Exception as exc:
            raise RuntimeError("Выбранная грань не является плоской.") from exc

        return face

    def pick_face(self, prompt_text="Select face", planar=True):
        selection_filter = (
            self.PART_FACE_PLANAR_FILTER if planar else self.PART_FACE_FILTER
        )
        return self.face_from_selection_object(self.pick(selection_filter, prompt_text))

    def face_vertices(self, face):
        """Вернуть список вершин грани."""
        return self._collection_items(face.Vertices)

    def face_vertex_points(self, face):
        """Вернуть 3D-точки вершин грани."""
        return [vertex.Point for vertex in self.face_vertices(face)]

    @staticmethod
    def face_vertex_count(face):
        """Вернуть количество вершин грани."""
        return face.Vertices.Count

    def face_edges(self, face):
        """Вернуть список ребер грани."""
        return self._collection_items(face.Edges)

    def reset_faces_to_feature_appearance(self, faces):
        reset_count = 0

        for face in self.unique_faces(faces):
            try:
                face.AppearanceSourceType = self.FEATURE_APPEARANCE
            except Exception:
                continue

            reset_count += 1

        return reset_count
