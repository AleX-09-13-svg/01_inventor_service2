class PartSketchCoreMethods:
    def add_sketch(self, planar_entity, name=None):
        sketch = self.sketches.Add(planar_entity)

        if name:
            sketch.Name = name

        return sketch

    def all_sketches(self, component_definition=None):
        """Return all sketches from a part component definition."""
        component_definition = component_definition or self.part_component_definition
        sketches = component_definition.Sketches

        return [sketches.Item(index) for index in range(1, sketches.Count + 1)]

    def sketches_by_prefix(self, prefix, component_definition=None):
        """Return sketches whose names start with prefix."""
        return [
            sketch
            for sketch in self.all_sketches(component_definition)
            if self.safe_getattr(sketch, "Name", "").startswith(prefix)
        ]

    def unique_sketch_name(self, base, sketches=None):
        """Return an available sketch name based on base."""
        sketches = sketches if sketches is not None else self.all_sketches()
        existing_names = {
            sketch.Name for sketch in sketches if hasattr(sketch, "Name")
        }

        if base not in existing_names:
            return base

        index = 1
        while True:
            name = f"{base}_{index}"
            if name not in existing_names:
                return name

            index += 1

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

    def sketch_on_offset_face_plane(self, face, prefix, offset_value, sketches=None):
        return self.sketch_on_face_plane(
            face,
            prefix=prefix,
            offsets=[offset_value],
            sketches=sketches,
        )

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
