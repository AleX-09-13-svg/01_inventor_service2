class AssemblyProperties:
    @property
    def assembly_document(self):
        return self.active_document

    @property
    def assembly_component_definition(self):
        return self.assembly_document.ComponentDefinition

    @property
    def occurrences(self):
        return self.assembly_component_definition.Occurrences
