class PartCoreMethods:
    def update_part(self):
        self.part_document.Update()
        return self.part_document

    def save_part(self):
        self.part_document.Save()
        return self.part_document

    def save_part_as(self, file_name, save_copy_as=False):
        self.part_document.SaveAs(file_name, save_copy_as)
        return self.part_document

    def parameter(self, name):
        return self.parameters.Item(name)

    def user_parameter(self, name):
        return self.user_parameters.Item(name)

    def model_parameter(self, name):
        return self.model_parameters.Item(name)

    def set_parameter(self, name, expression):
        parameter = self.parameter(name)
        parameter.Expression = expression
        return parameter

    def add_user_parameter(self, name, expression, units="mm"):
        return self.user_parameters.AddByExpression(name, expression, units)

    def feature(self, name):
        return self.features.Item(name)

    def work_plane(self, index_or_name):
        return self.work_planes.Item(index_or_name)

    def work_axis(self, index_or_name):
        return self.work_axes.Item(index_or_name)

    def work_point(self, index_or_name):
        return self.work_points.Item(index_or_name)
