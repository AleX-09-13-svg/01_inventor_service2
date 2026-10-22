class PartSketchDimensionMethods:
    def add_aligned_dimension(self, sketch, point1, point2, text_point, driven=False):
        """Добавить выровненный размер между двумя точками."""
        return self.add_two_point_dimension(
            sketch,
            point1,
            point2,
            "aligned",
            text_point,
            driven,
        )

    def sketch_dimension_constraints(self, sketch):
        """Return DimensionConstraints as a Python list."""
        constraints = sketch.DimensionConstraints
        return [
            constraints.Item(index)
            for index in range(1, constraints.Count + 1)
        ]

    @staticmethod
    def sketch_dimension_count(sketch):
        """Return sketch.DimensionConstraints.Count."""
        return sketch.DimensionConstraints.Count

    def add_two_point_dimension(
        self,
        sketch,
        point1,
        point2,
        orientation,
        text_point,
        driven=False,
        expression=None,
    ):
        """Wrapper for DimensionConstraints.AddTwoPointDistance."""
        dimension = sketch.DimensionConstraints.AddTwoPointDistance(
            point1,
            point2,
            self.dimension_orientation(orientation),
            text_point,
            driven,
        )

        if expression is not None:
            parameter = self.safe_getattr(dimension, "Parameter")
            if parameter is not None:
                parameter.Expression = expression

        return dimension
