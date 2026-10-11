class AssemblyMethods:
    def pick_part(self, prompt_text="Select part"):
        return self.pick(self.ASSEMBLY_LEAF_OCCURRENCE_FILTER, prompt_text)
