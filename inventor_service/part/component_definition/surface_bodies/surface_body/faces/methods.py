class PartFaceMethods:
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

    def pick_face(self, prompt_text="Select face", planar=True):
        selection_filter = (
            self.PART_FACE_PLANAR_FILTER if planar else self.PART_FACE_FILTER
        )
        return self.face_from_selection_object(self.pick(selection_filter, prompt_text))

    def reset_faces_to_feature_appearance(self, faces):
        reset_count = 0

        for face in self.unique_faces(faces):
            try:
                face.AppearanceSourceType = self.FEATURE_APPEARANCE
            except Exception:
                continue

            reset_count += 1

        return reset_count
