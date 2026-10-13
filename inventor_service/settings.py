import json
import os
from pathlib import Path

from .config import validate_library_config
from .general import (
    kAlignedDim,
    kHorizontalDim,
    kNegativeExtentDirection,
    kPositiveExtentDirection,
    kVerticalDim,
)

DEFAULT_LIBRARY_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
    / "service"
    / "infa"
    / "part_config.example.json"
)

DEFAULT_SETTINGS = {
    "drilling": {
        "drawer_edge_max_cm": 30.0,
    },
    "confirmat": {},
    "stiajka": {
        "side_offset": 3.4,
        "parameters": {},
    },
}

_SETTINGS = None


def _merge_dict(base, override):
    result = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def _load_json(path):
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def _configured_library_path(settings):
    path = os.environ.get("INVENTOR_SERVICE_LIBRARY_CONFIG")
    if path:
        return path

    path = settings.get("library_config_path")
    if path:
        return path

    if DEFAULT_LIBRARY_CONFIG_PATH.exists():
        return DEFAULT_LIBRARY_CONFIG_PATH

    return None


def _load_library_settings(settings):
    library_path = _configured_library_path(settings)
    if not library_path:
        return settings

    library = _load_json(library_path)
    validate_library_config(library)

    merged = _merge_dict(settings, library)
    merged["library_config_path"] = str(library_path)
    return merged


def load_settings(path=None):
    if path is None:
        path = os.environ.get("INVENTOR_SERVICE_SETTINGS")

    if not path:
        path = os.environ.get("INVENTOR_SERVICE_WORKFLOW_SETTINGS")

    settings = dict(DEFAULT_SETTINGS)
    if not path:
        return _load_library_settings(settings)

    local_settings = _load_json(path)
    settings = _merge_dict(settings, local_settings)
    return _load_library_settings(settings)


def configure_settings(values=None, path=None):
    global _SETTINGS

    settings = load_settings(path)
    if values:
        settings = _merge_dict(settings, values)
        if settings.get("linked_parameters"):
            validate_library_config(settings)

    _SETTINGS = settings
    return _SETTINGS


def service_settings():
    global _SETTINGS

    if _SETTINGS is None:
        _SETTINGS = load_settings()

    return _SETTINGS


def setting(*keys, default=None):
    value = service_settings()

    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]

    return value


def linked_parameters():
    return setting("linked_parameters", default=[])


def linked_parameter_options():
    return [
        item["name"]
        for item in linked_parameters()
        if isinstance(item, dict) and item.get("name")
    ]


def drawer_edge_max_cm():
    value = setting("drilling", "drawer_edge_max_cm")
    if value is not None:
        return value

    return setting("drawer_edge_max_cm", default=30.0)


def hole_direction(name):
    directions = {
        "positive": kPositiveExtentDirection,
        "+": kPositiveExtentDirection,
        "negative": kNegativeExtentDirection,
        "-": kNegativeExtentDirection,
    }

    if isinstance(name, str):
        key = name.strip().lower()
        if key not in directions:
            raise ValueError(f"Unknown hole direction: {name}")
        return directions[key]

    return name


def dimension_orientation(name):
    orientations = {
        "horizontal": kHorizontalDim,
        "vertical": kVerticalDim,
        "aligned": kAlignedDim,
    }

    if isinstance(name, str):
        key = name.strip().lower()
        if key not in orientations:
            raise ValueError(f"Unknown dimension orientation: {name}")
        return orientations[key]

    return name
