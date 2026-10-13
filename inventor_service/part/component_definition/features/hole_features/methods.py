from .....general import kPositiveExtentDirection


class PartHoleMethods:
    def set_all_bodies_affected(self, feature, component_definition=None):
        component_definition = component_definition or self.comp

        try:
            if component_definition.SurfaceBodies.Count <= 1:
                return
        except Exception:
            pass

        try:
            feature.SetAffectedBodies(component_definition.SurfaceBodies)
        except Exception:
            try:
                feature.SetAffectedBodies(self.all_surface_bodies(component_definition))
            except Exception:
                pass

    def add_holes(
        self,
        points,
        diameter,
        depth,
        direction=kPositiveExtentDirection,
        name=None,
        flat_bottom=True,
        affect_all_bodies=True,
        component_definition=None,
    ):
        component_definition = component_definition or self.comp
        points = self.unique_points(points)
        self.mark_as_hole_centers(points)

        hole_features = component_definition.Features.HoleFeatures
        placement = hole_features.CreateSketchPlacementDefinition(
            self.object_collection(points)
        )
        feature = hole_features.AddDrilledByDistanceExtent(
            placement,
            diameter,
            depth,
            self.hole_direction(direction),
            flat_bottom,
        )

        if name:
            try:
                feature.Name = self.unique_feature_name(hole_features, name)
            except Exception:
                pass

        if affect_all_bodies:
            self.set_all_bodies_affected(feature, component_definition)

        return feature

    def add_counterbore_holes(
        self,
        points,
        hole_diameter,
        hole_depth,
        direction,
        counterbore_diameter,
        counterbore_depth,
        name=None,
        affect_all_bodies=True,
        component_definition=None,
    ):
        component_definition = component_definition or self.comp
        points = self.unique_points(points)
        self.mark_as_hole_centers(points)

        hole_features = component_definition.Features.HoleFeatures
        placement = hole_features.CreateSketchPlacementDefinition(
            self.object_collection(points)
        )

        try:
            feature = hole_features.AddCBoreByDistanceExtent2(
                placement,
                hole_diameter,
                hole_depth,
                self.hole_direction(direction),
                counterbore_diameter,
                counterbore_depth,
            )
        except Exception:
            feature = hole_features.AddCBoreByDistanceExtent(
                placement,
                hole_diameter,
                hole_depth,
                self.hole_direction(direction),
                counterbore_diameter,
                counterbore_depth,
                True,
            )

        if name:
            try:
                feature.Name = self.unique_feature_name(hole_features, name)
            except Exception:
                pass

        if affect_all_bodies:
            self.set_all_bodies_affected(feature, component_definition)

        return feature

    def add_hole_batch(
        self,
        points,
        diameter,
        depth,
        direction=kPositiveExtentDirection,
        name=None,
        **kwargs,
    ):
        return self.add_holes(
            points,
            diameter,
            depth,
            direction=direction,
            name=name,
            **kwargs,
        )

    def add_counterbore_batch(
        self,
        points,
        hole_diameter,
        hole_depth,
        direction,
        counterbore_diameter,
        counterbore_depth,
        name=None,
        **kwargs,
    ):
        return self.add_counterbore_holes(
            points,
            hole_diameter,
            hole_depth,
            direction,
            counterbore_diameter,
            counterbore_depth,
            name=name,
            **kwargs,
        )

    def create_hole_batch_with_fallback(
        self,
        jobs,
        points_key,
        settings,
        defaults=None,
        label="Hole",
    ):
        defaults = defaults or {}
        created = []

        all_points = []
        for job in jobs:
            all_points.extend(job.get(points_key, []))

        if all_points:
            try:
                created.append(self.add_hole_batch(all_points, **defaults, **settings))
                return created
            except Exception:
                pass

        for index, job in enumerate(jobs, start=1):
            points = job.get(points_key, [])
            if not points:
                continue

            job_settings = {**defaults, **settings}
            job_settings.update(job.get("settings", {}))
            job_settings.setdefault("name", f"{label}_{index}")
            created.append(self.add_hole_batch(points, **job_settings))

        return created

    def create_confirmat_features(
        self,
        sketches=None,
        faces=None,
        face_label="red",
        direction=None,
    ):
        from .....confirmat import create_confirmat_features

        return create_confirmat_features(
            self,
            sketches=sketches,
            faces=faces,
            face_label=face_label,
            direction=direction,
        )

    def create_confirmat_2_features(
        self,
        sketches=None,
        faces=None,
        face_label="yellow",
        direction=None,
    ):
        from .....confirmat import create_confirmat_2_features

        return create_confirmat_2_features(
            self,
            sketches=sketches,
            faces=faces,
            face_label=face_label,
            direction=direction,
        )
