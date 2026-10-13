from contextlib import contextmanager


class InventorMethods:
    def update(self):
        self.active_document.Update()

    def active_document_name(self):
        """Вернуть DisplayName активного документа."""
        return self.active_document.DisplayName

    def active_part_name(self):
        """Алиас для имени активной детали."""
        return self.active_document_name()

    @staticmethod
    def mm(value):
        return value / 10

    @staticmethod
    def mm_text(value):
        if isinstance(value, str):
            return value

        return f"{value} mm"

    @classmethod
    def hole_direction(cls, name):
        directions = {
            "positive": cls.POSITIVE_EXTENT_DIRECTION,
            "+": cls.POSITIVE_EXTENT_DIRECTION,
            "negative": cls.NEGATIVE_EXTENT_DIRECTION,
            "-": cls.NEGATIVE_EXTENT_DIRECTION,
        }

        if isinstance(name, str):
            key = name.strip().lower()
            if key not in directions:
                raise ValueError(f"Unknown hole direction: {name}")

            return directions[key]

        return name

    @classmethod
    def opposite_hole_direction(cls, direction):
        direction = cls.hole_direction(direction)

        if direction == cls.POSITIVE_EXTENT_DIRECTION:
            return cls.NEGATIVE_EXTENT_DIRECTION
        if direction == cls.NEGATIVE_EXTENT_DIRECTION:
            return cls.POSITIVE_EXTENT_DIRECTION

        raise ValueError(f"Unknown hole direction: {direction}")

    @classmethod
    def dimension_orientation(cls, name):
        orientations = {
            "horizontal": cls.HORIZONTAL_DIMENSION,
            "vertical": cls.VERTICAL_DIMENSION,
            "aligned": cls.ALIGNED_DIMENSION,
        }

        if isinstance(name, str):
            key = name.strip().lower()
            if key not in orientations:
                raise ValueError(f"Unknown dimension orientation: {name}")

            return orientations[key]

        return name

    @staticmethod
    def safe_getattr(obj, attr, default=None):
        try:
            return getattr(obj, attr)
        except Exception:
            return default

    def object_collection(self, objects):
        collection = self.transient_objects.CreateObjectCollection()

        for obj in objects:
            collection.Add(obj)

        return collection

    def pick(self, selection_filter, prompt_text="Select object"):
        return self.app.CommandManager.Pick(selection_filter, prompt_text)

    @contextmanager
    def screen_updates_suspended(self):
        try:
            previous = self.app.ScreenUpdating
            self.app.ScreenUpdating = False
        except Exception:
            previous = None

        try:
            yield self
        finally:
            if previous is not None:
                try:
                    self.app.ScreenUpdating = previous
                except Exception:
                    pass

    @staticmethod
    def show_message(title, text, icon="info"):
        icons = {
            "info": 0x40,
            "warning": 0x30,
            "error": 0x10,
            "question": 0x20,
        }

        ctypes = __import__("ctypes")
        return ctypes.windll.user32.MessageBoxW(
            0,
            str(text),
            str(title),
            icons.get(icon, icons["info"]),
        )

    def show_missing_parameters_message(self, names, title="Missing parameters"):
        return self.show_message(title, "\n".join(names), icon="warning")
