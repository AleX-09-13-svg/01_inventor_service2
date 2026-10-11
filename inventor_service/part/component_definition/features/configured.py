import json
from pathlib import Path

from ....config import resolve_parameter_name, update_missing_parameter_suggestions


class PartConfiguredMethods:
    def load_part_config(self, path):
        path = Path(path)
        return json.loads(path.read_text(encoding="utf-8"))

    def validate_linked_parameters(self, names):
        missing = []

        for name in names:
            try:
                self.parameter(name)
            except Exception:
                missing.append(name)

        if missing:
            raise ValueError(
                "Missing Inventor parameters: " + ", ".join(missing)
            )

        return True

    def resolve_config_parameter_name(self, name, config):
        resolved = resolve_parameter_name(name, config)
        self.parameter(resolved)
        return resolved

    def apply_part_config(self, config):
        if isinstance(config, (str, Path)):
            config = self.load_part_config(config)

        parameter_names = [
            item["name"]
            for item in config.get("linked_parameters", [])
            if item.get("name")
        ]
        self.validate_linked_parameters(parameter_names)
        update_missing_parameter_suggestions(config)

        if config.get("missing_parameter_suggestions"):
            raise ValueError(
                "Missing operation parameters. Check "
                "missing_parameter_suggestions in the config."
            )

        features = []
        for operation in config.get("operations", []):
            features.append(self.apply_part_operation(operation, config=config))

        self.update_part()
        return features

    def apply_part_operation(self, operation, config=None):
        config = config or {}
        operation_type = operation.get("type")

        if operation_type == "center_hole_on_selected_face":
            return self._apply_center_hole_on_selected_face(operation, config)

        raise ValueError(f"Unknown part operation type: {operation_type}")

    def _apply_center_hole_on_selected_face(self, operation, config):
        faces = self.selected_faces()
        if not faces:
            face = self.pick_face(
                operation.get("pick_prompt", "Select planar face"),
                planar=True,
            )
        else:
            face = faces[0]

        sketch = self.get_or_create_sketch_on_face(
            face,
            name=operation.get("sketch_name"),
            prefix=operation.get("sketch_prefix"),
        )
        point = self.add_face_center_point(face, sketch)

        return self.add_holes(
            [point],
            diameter=self.resolve_config_parameter_name(
                operation["diameter_parameter"],
                config,
            ),
            depth=self.resolve_config_parameter_name(
                operation["depth_parameter"],
                config,
            ),
            direction=operation.get("direction", "positive"),
            name=operation.get("feature_name"),
        )
