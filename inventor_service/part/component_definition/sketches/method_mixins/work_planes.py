class PartSketchWorkPlaneMethods:
    def create_work_plane_by_line_plane_angle(
        self,
        line,
        plane,
        angle,
        construction=True,
        component_definition=None,
    ):
        """Wrapper for WorkPlanes.AddByLinePlaneAndAngle."""
        component_definition = component_definition or self.part_component_definition
        return component_definition.WorkPlanes.AddByLinePlaneAndAngle(
            line,
            plane,
            angle,
            construction,
        )

    def add_offset_work_plane(
        self,
        face_or_plane,
        offset,
        name=None,
        visible=False,
        component_definition=None,
    ):
        component_definition = component_definition or self.part_component_definition
        work_plane = component_definition.WorkPlanes.AddByPlaneAndOffset(
            face_or_plane,
            offset,
        )

        if name:
            work_plane.Name = self.unique_work_plane_name(
                name,
                component_definition.WorkPlanes,
            )

        try:
            work_plane.Visible = visible
        except Exception:
            pass

        return work_plane
