class InventorDirectionMethods:
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
