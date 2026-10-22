class PartSketchConstraintMethods:
    def fix_sketch_entity(self, sketch, entity):
        return self.add_ground_constraint(sketch, entity, ignore_errors=True)

    def fix_sketch_points(self, sketch, points):
        return [self.fix_sketch_entity(sketch, point) for point in points]

    @staticmethod
    def _add_geometric_constraint(
        sketch,
        method_name,
        *args,
        ignore_errors=True,
    ):
        try:
            method = getattr(sketch.GeometricConstraints, method_name)
            return method(*args)
        except Exception:
            if not ignore_errors:
                raise

            return None

    def add_ground_constraint(self, sketch, entity, ignore_errors=True):
        """Add GeometricConstraints.AddGround(entity)."""
        return self._add_geometric_constraint(
            sketch,
            "AddGround",
            entity,
            ignore_errors=ignore_errors,
        )

    def add_midpoint_constraint(
        self,
        sketch,
        point_or_line_point,
        line,
        ignore_errors=True,
    ):
        """Wrapper for GeometricConstraints.AddMidpoint."""
        return self._add_geometric_constraint(
            sketch,
            "AddMidpoint",
            point_or_line_point,
            line,
            ignore_errors=ignore_errors,
        )

    def add_coincident_constraint(self, sketch, entity1, entity2, ignore_errors=True):
        """Wrapper for GeometricConstraints.AddCoincident."""
        return self._add_geometric_constraint(
            sketch,
            "AddCoincident",
            entity1,
            entity2,
            ignore_errors=ignore_errors,
        )

    def add_perpendicular_constraint(self, sketch, line1, line2, ignore_errors=True):
        """Wrapper for GeometricConstraints.AddPerpendicular."""
        return self._add_geometric_constraint(
            sketch,
            "AddPerpendicular",
            line1,
            line2,
            ignore_errors=ignore_errors,
        )

    def add_parallel_constraint(self, sketch, line1, line2, ignore_errors=True):
        """Wrapper for GeometricConstraints.AddParallel."""
        return self._add_geometric_constraint(
            sketch,
            "AddParallel",
            line1,
            line2,
            ignore_errors=ignore_errors,
        )

    def add_symmetry_constraint(
        self,
        sketch,
        entity1,
        entity2,
        symmetry_line,
        ignore_errors=True,
    ):
        """Wrapper for GeometricConstraints.AddSymmetry."""
        return self._add_geometric_constraint(
            sketch,
            "AddSymmetry",
            entity1,
            entity2,
            symmetry_line,
            ignore_errors=ignore_errors,
        )
