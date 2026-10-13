class PartFaceMethods:
    COLOR_KEYWORDS = {
        "red": ("red", "\u043a\u0440\u0430\u0441"),
        "green": ("green", "\u0437\u0435\u043b\u0435\u043d", "\u0437\u0435\u043b\u0451\u043d"),
        "yellow": ("yellow", "\u0436\u0435\u043b\u0442", "\u0436\u0451\u043b\u0442"),
        "blue": ("blue", "\u0441\u0438\u043d", "\u0433\u043e\u043b\u0443\u0431"),
    }

    COLOR_RGB = {
        "red": (255, 0, 0),
        "green": (0, 176, 80),
        "yellow": (255, 255, 0),
        "blue": (0, 112, 192),
    }

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

    def all_faces(self, component_definition=None):
        component_definition = component_definition or self.comp
        faces = []

        for body in self._collection_items(component_definition.SurfaceBodies):
            faces.extend(self._collection_items(body.Faces))

        return faces

    @staticmethod
    def face_key(face):
        try:
            return face.ReferenceKey
        except Exception:
            return id(face)

    @classmethod
    def face_appearance_text(cls, face):
        appearance = cls.safe_getattr(face, "Appearance")
        parent = cls.safe_getattr(face, "Parent")
        parent_appearance = cls.safe_getattr(parent, "Appearance")
        values = []

        for source in (appearance, face, parent_appearance, parent):
            if source is None:
                continue
            for attr in ("DisplayName", "Name"):
                value = cls.safe_getattr(source, attr)
                if value:
                    values.append(str(value))

        return " ".join(values)

    @classmethod
    def face_appearance_key(cls, face):
        text = cls.face_appearance_text(face).strip().lower()

        for color_name, keywords in cls.COLOR_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return color_name

        return text

    @classmethod
    def _color_rgb(cls, color):
        if color is None:
            return None

        for attrs in (("Red", "Green", "Blue"), ("R", "G", "B")):
            try:
                return tuple(int(getattr(color, attr)) for attr in attrs)
            except Exception:
                pass

        return None

    @classmethod
    def face_color(cls, face):
        appearance = cls.safe_getattr(face, "Appearance")
        parent = cls.safe_getattr(face, "Parent")
        parent_appearance = cls.safe_getattr(parent, "Appearance")

        for source in (appearance, face, parent_appearance, parent):
            if source is None:
                continue
            for attr in ("Color", "DiffuseColor"):
                color = cls.safe_getattr(source, attr)
                if color is not None:
                    return color

        return None

    @classmethod
    def face_color_rgb(cls, face):
        return cls._color_rgb(cls.face_color(face))

    @classmethod
    def detected_face_rgb(cls, face):
        rgb = cls.face_color_rgb(face)
        if rgb is not None:
            return rgb

        return cls.COLOR_RGB.get(cls.face_appearance_key(face))

    @classmethod
    def is_face_color(cls, face, color_name):
        color_name = color_name.strip().lower()
        keywords = cls.COLOR_KEYWORDS.get(color_name, (color_name,))
        text = cls.face_appearance_text(face).lower()

        if any(keyword in text for keyword in keywords):
            return True

        expected_rgb = cls.COLOR_RGB.get(color_name)
        return expected_rgb is not None and cls.detected_face_rgb(face) == expected_rgb

    def faces_by_color(self, component_definition=None):
        result = {}

        for face in self.all_faces(component_definition):
            key = self.face_appearance_key(face) or "unknown"
            result.setdefault(key, []).append(face)

        return result

    def colored_faces(self, color_name, component_definition=None):
        return [
            face
            for face in self.all_faces(component_definition)
            if self.is_face_color(face, color_name)
        ]

    def _inventor_color(self, color):
        if isinstance(color, str):
            color = self.COLOR_RGB[color.strip().lower()]

        if isinstance(color, (tuple, list)):
            return self.transient_objects.CreateColor(
                int(color[0]),
                int(color[1]),
                int(color[2]),
            )

        return color

    @staticmethod
    def _set_object_color(obj, color):
        try:
            obj.Color = color
            return obj
        except Exception:
            return None

    def set_sketch_color(self, sketch, color, include_entities=True):
        color = self._inventor_color(color)
        self._set_object_color(sketch, color)

        if include_entities:
            for entity in self.sketch_lines(sketch):
                self._set_object_color(entity, color)
            for point in self.sketch_points(sketch):
                self._set_object_color(point, color)

        return sketch

    def set_sketch_color_rgb(self, sketch, rgb, include_entities=True):
        return self.set_sketch_color(sketch, rgb, include_entities)

    def set_sketch_color_from_face(self, sketch, face, include_entities=True):
        rgb = self.detected_face_rgb(face)
        if rgb is None:
            return sketch

        return self.set_sketch_color_rgb(sketch, rgb, include_entities)

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

    def require_selected_faces(self, min_count=1, planar=True, debug=False):
        """Вернуть выбранные грани или поднять понятную ошибку."""
        faces = self.selected_faces(debug=debug)

        if planar:
            faces = [face for face in faces if self.is_planar_face(face)]

        if len(faces) < min_count:
            raise RuntimeError(
                f"Сначала выдели минимум {min_count} грань(и) детали в Inventor."
            )

        return faces

    def selected_faces_by_color(self, color_name=None):
        faces = self.selected_faces()
        if color_name is None:
            return faces

        return [face for face in faces if self.is_face_color(face, color_name)]

    def selected_faces_grouped_by_plane(self):
        return self.group_faces_by_plane(self.selected_faces())

    def selected_faces_grouped_by_plane_and_appearance(self):
        groups = {}

        for plane_group in self.selected_faces_grouped_by_plane():
            key = self.face_appearance_key(plane_group[0])
            groups.setdefault(key, []).append(plane_group)

        return groups

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

    def pick_faces_until_cancel(self, prompt_text="Select face", planar=True):
        faces = []

        while True:
            try:
                face = self.pick_face(prompt_text, planar=planar)
            except Exception:
                break

            if face is None:
                break

            faces.append(face)

        return self.unique_faces(faces)

    @classmethod
    def is_planar_face(cls, face):
        try:
            geometry = cls.plane_geometry(face)
            geometry.Normal
            geometry.RootPoint
            return True
        except Exception:
            return False

    def face_vertices(self, face):
        """Вернуть список вершин грани."""
        return self._collection_items(face.Vertices)

    def face_vertex_points(self, face):
        """Вернуть 3D-точки вершин грани."""
        return [vertex.Point for vertex in self.face_vertices(face)]

    def selected_face_vertex_points_xy(
        self,
        sketch_name="Face vertices",
        debug=False,
    ):
        """Return selected planar face vertices as plain sketch-space XY tuples."""
        face = self.selected_planar_face(debug=debug)
        sketch = self.add_sketch(face, name=self.unique_sketch_name(sketch_name))
        points = self.face_vertex_points_in_sketch(face, sketch)
        result = [(point.X, point.Y) for point in points]

        if debug:
            print("Sketch:", sketch.Name)
            print("Face vertices:", len(result))

        return result

    def selected_face_vertex_report(
        self,
        sketch_name="Face vertices",
        debug=False,
    ):
        """Return printable data for vertices of the currently selected face."""
        points = self.selected_face_vertex_points_xy(
            sketch_name=sketch_name,
            debug=debug,
        )

        return {
            "document": self.active_document_name(),
            "vertex_count": len(points),
            "points": points,
        }

    @staticmethod
    def face_vertex_count(face):
        """Вернуть количество вершин грани."""
        return face.Vertices.Count

    def face_edges(self, face):
        """Вернуть список ребер грани."""
        return self._collection_items(face.Edges)

    def edge_faces(self, edge):
        for attr in ("Faces", "TangentiallyConnectedFaces"):
            faces = self.safe_getattr(edge, attr)
            if faces is not None:
                return self._collection_items(faces)

        return []

    def shared_face_edge(self, face1, face2):
        face2_edges = {self.face_key(edge) for edge in self.face_edges(face2)}

        for edge in self.face_edges(face1):
            if self.face_key(edge) in face2_edges:
                return edge

        return None

    def adjacent_faces(self, face):
        result = []

        for edge in self.face_edges(face):
            for other_face in self.edge_faces(edge):
                if self.face_key(other_face) != self.face_key(face):
                    result.append(other_face)

        return self.unique_faces(result)

    def adjacent_face_count(self, faces, other_faces):
        count = 0

        for face in faces:
            for other_face in other_faces:
                if self.shared_face_edge(face, other_face) is not None:
                    count += 1
                    break

        return count

    @staticmethod
    def face_area(face):
        for source in (face, getattr(face, "Evaluator", None)):
            if source is None:
                continue

            try:
                value = getattr(source, "Area")
                return value() if callable(value) else value
            except Exception:
                pass

        return None

    def faces_area(self, faces):
        return sum((self.face_area(face) or 0) for face in faces)

    def face_model_bounds(self, face):
        points = self.face_vertex_points(face)
        xs = [point.X for point in points]
        ys = [point.Y for point in points]
        zs = [point.Z for point in points]
        return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)

    @staticmethod
    def point_inside_model_bounds(point, bounds, tol=0.01):
        min_x, max_x, min_y, max_y, min_z, max_z = bounds
        return (
            min_x - tol <= point.X <= max_x + tol
            and min_y - tol <= point.Y <= max_y + tol
            and min_z - tol <= point.Z <= max_z + tol
        )

    def candidate_faces_by_normal_axis(
        self,
        axis,
        coordinate,
        tol=0.001,
        component_definition=None,
    ):
        axis = axis.strip().lower()
        axis_index = {"x": 0, "y": 1, "z": 2}[axis]
        result = []

        for face in self.all_faces(component_definition):
            if not self.is_planar_face(face):
                continue

            normal = self.face_normal(face)
            root = self.plane_root_point(face)
            normal_values = (abs(normal.X), abs(normal.Y), abs(normal.Z))
            root_values = (root.X, root.Y, root.Z)

            if normal_values[axis_index] >= 1 - tol and abs(
                root_values[axis_index] - coordinate
            ) <= tol:
                result.append(face)

        return result

    def reset_faces_to_feature_appearance(self, faces):
        reset_count = 0

        for face in self.unique_faces(faces):
            try:
                face.AppearanceSourceType = self.FEATURE_APPEARANCE
            except Exception:
                continue

            reset_count += 1

        return reset_count
