class PartCoreMethods:
    @staticmethod
    def unique_collection_name(collection, base, separator="_"):
        name = base
        index = 1

        while True:
            try:
                collection.Item(name)
                index += 1
                name = f"{base}{separator}{index}"
                continue
            except Exception:
                pass

            try:
                existing_names = {
                    collection.Item(i).Name
                    for i in range(1, collection.Count + 1)
                }
            except Exception:
                return name

            if name not in existing_names:
                return name

            index += 1
            name = f"{base}{separator}{index}"

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

    def unique_parameter_name(self, base, parameters=None, separator="_"):
        parameters = parameters or self.parameters
        return self.unique_collection_name(parameters, base, separator=separator)

    def parameter_exists(self, name, component_definition=None):
        component_definition = component_definition or self.comp

        try:
            component_definition.Parameters.Item(name)
            return True
        except Exception:
            return False

    def missing_parameters(self, names, component_definition=None):
        return [
            name
            for name in names
            if not self.parameter_exists(name, component_definition)
        ]

    def parameter_value(self, name, default=None, component_definition=None):
        component_definition = component_definition or self.comp

        try:
            return component_definition.Parameters.Item(name).Value
        except Exception:
            return default

    def parameter_expression(self, name, default=None, component_definition=None):
        component_definition = component_definition or self.comp

        try:
            return component_definition.Parameters.Item(name).Expression
        except Exception:
            return default

    def set_parameter_expression(self, name, expression, component_definition=None):
        component_definition = component_definition or self.comp
        parameter = component_definition.Parameters.Item(name)
        parameter.Expression = expression
        return parameter

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

    def ensure_user_parameter(
        self,
        name,
        expression,
        units="mm",
        component_definition=None,
    ):
        component_definition = component_definition or self.comp
        parameters = component_definition.Parameters

        try:
            return parameters.Item(name)
        except Exception:
            return parameters.UserParameters.AddByExpression(name, expression, units)

    def parameter_expressions(self, names, component_definition=None):
        return {
            name: self.parameter_expression(name, component_definition=component_definition)
            for name in names
            if self.parameter_exists(name, component_definition)
        }

    def restore_missing_parameters(
        self,
        expressions,
        units="mm",
        component_definition=None,
    ):
        restored = False

        for name, expression in expressions.items():
            if self.parameter_exists(name, component_definition):
                continue

            self.ensure_user_parameter(
                name,
                expression,
                units=units,
                component_definition=component_definition,
            )
            restored = True

        return restored

    def ensure_keep_parameter(
        self,
        name,
        referenced_parameter_names,
        units="mm",
        component_definition=None,
    ):
        expression = " + ".join(f"{param} * 0" for param in referenced_parameter_names)
        if not expression:
            expression = "0"

        parameter = self.ensure_user_parameter(
            name,
            expression,
            units=units,
            component_definition=component_definition,
        )

        parameter.Expression = expression
        return parameter

    def feature(self, name):
        return self.features.Item(name)

    def work_plane(self, index_or_name):
        return self.work_planes.Item(index_or_name)

    def unique_feature_name(self, base, features=None):
        if hasattr(base, "Item") and isinstance(features, str):
            base, features = features, base

        features = features or self.features
        return self.unique_collection_name(features, base, separator="_")

    def unique_work_plane_name(self, base, work_planes=None):
        work_planes = work_planes or self.work_planes
        return self.unique_collection_name(work_planes, base, separator="_")

    def work_axis(self, index_or_name):
        return self.work_axes.Item(index_or_name)

    def work_point(self, index_or_name):
        return self.work_points.Item(index_or_name)
