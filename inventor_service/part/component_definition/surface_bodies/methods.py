class PartSurfaceBodiesMethods:
    def surface_body(self, index=1):
        return self.surface_bodies.Item(index)

    def all_surface_bodies(self, component_definition=None):
        component_definition = component_definition or self.comp
        bodies = self.transient_objects.CreateObjectCollection()

        for index in range(1, component_definition.SurfaceBodies.Count + 1):
            bodies.Add(component_definition.SurfaceBodies.Item(index))

        return bodies
