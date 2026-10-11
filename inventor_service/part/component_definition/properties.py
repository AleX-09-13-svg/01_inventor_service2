class PartProperties:
    @property
    def part_document(self):
        return self.active_document

    @property
    def part_component_definition(self):
        return self.part_document.ComponentDefinition

    @property
    def parameters(self):
        return self.part_component_definition.Parameters

    @property
    def user_parameters(self):
        return self.parameters.UserParameters

    @property
    def model_parameters(self):
        return self.parameters.ModelParameters

    @property
    def features(self):
        return self.part_component_definition.Features

    @property
    def sketches(self):
        return self.part_component_definition.Sketches

    @property
    def surface_bodies(self):
        return self.part_component_definition.SurfaceBodies

    @property
    def work_planes(self):
        return self.part_component_definition.WorkPlanes

    @property
    def work_axes(self):
        return self.part_component_definition.WorkAxes

    @property
    def work_points(self):
        return self.part_component_definition.WorkPoints
