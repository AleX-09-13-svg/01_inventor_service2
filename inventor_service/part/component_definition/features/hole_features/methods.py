from .....general import kPositiveExtentDirection


class PartHoleMethods:
    @staticmethod
    def unique_feature_name(features, base):
        name = base
        index = 1

        while True:
            try:
                features.Item(name)
                index += 1
                name = f"{base} {index}"
            except Exception:
                return name

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
