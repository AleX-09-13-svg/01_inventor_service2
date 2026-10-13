from difflib import get_close_matches
import json
import re
from pathlib import Path


PARAMETER_REFERENCE_KEYS = (
    "diameter",
    "depth",
    "diameter_parameter",
    "depth_parameter",
    "hole_diameter_parameter",
    "hole_depth_parameter",
    "counterbore_diameter_parameter",
    "counterbore_depth_parameter",
)
TECHNOLOGY_BLOCKS = ("stiajka", "confirmat")

CYRILLIC_TRANSLIT = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "h",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "sch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def safe_parameter_name(source_name):
    result = []

    for char in str(source_name).strip():
        lower = char.lower()
        if lower in CYRILLIC_TRANSLIT:
            result.append(CYRILLIC_TRANSLIT[lower])
        elif char.isascii() and char.isalnum():
            result.append(char.lower())
        else:
            result.append("_")

    name = re.sub(r"_+", "_", "".join(result)).strip("_")

    if not name:
        name = "parameter"
    if name[0].isdigit():
        name = f"p_{name}"

    return name


def build_linked_parameters(source_names):
    result = []
    used = {}

    for source_name in source_names:
        base_name = safe_parameter_name(source_name)
        count = used.get(base_name, 0) + 1
        used[base_name] = count
        name = base_name if count == 1 else f"{base_name}_{count}"
        result.append(
            {
                "name": name,
                "source_name": source_name,
            }
        )

    return result


def linked_parameter_names(config):
    return [
        item["name"]
        for item in config.get("linked_parameters", [])
        if item.get("name")
    ]


def linked_parameter_source_names(config):
    return [
        item.get("source_name", item.get("name"))
        for item in config.get("linked_parameters", [])
        if item.get("source_name") or item.get("name")
    ]


def resolve_parameter_name(name, config):
    aliases = config.get("parameter_aliases", {})
    available = set(linked_parameter_names(config))
    resolved = aliases.get(name, name)

    if resolved in available:
        return resolved

    return name


def operation_parameter_references(config):
    references = []

    for operation in config.get("operations", []):
        for key in PARAMETER_REFERENCE_KEYS:
            value = operation.get(key)
            if value:
                references.append(value)

    return references


def _parameter_references(value):
    references = []

    if isinstance(value, dict):
        for key, child in value.items():
            if key in PARAMETER_REFERENCE_KEYS and isinstance(child, str) and child:
                references.append(child)
            elif isinstance(child, (dict, list)):
                references.extend(_parameter_references(child))
    elif isinstance(value, list):
        for child in value:
            references.extend(_parameter_references(child))

    return references


def technology_parameter_references(config):
    references = []

    for block_name in TECHNOLOGY_BLOCKS:
        references.extend(_parameter_references(config.get(block_name, {})))

    return references


def library_parameter_references(config):
    return operation_parameter_references(config) + technology_parameter_references(config)


def missing_library_parameter_references(config):
    available = set(linked_parameter_names(config))
    aliases = config.get("parameter_aliases", {})
    missing = []
    seen = set()

    for name in library_parameter_references(config):
        resolved = aliases.get(name, name)
        if resolved in available:
            continue
        if name in seen:
            continue
        seen.add(name)
        missing.append(name)

    return missing


def validate_library_config(config):
    missing = missing_library_parameter_references(config)

    if missing:
        raise ValueError(
            "В библиотеке не найдены параметры:\n"
            + "\n".join(missing)
            + "\n\nПроверьте Excel-библиотеку или обновите part_config.json."
        )

    return True


def build_missing_parameter_suggestions(config, limit=5):
    available = linked_parameter_names(config)
    aliases = config.get("parameter_aliases", {})
    missing = {}

    for name in library_parameter_references(config):
        resolved = aliases.get(name, name)
        if resolved in available:
            continue

        suggestions = get_close_matches(
            resolved,
            available,
            n=limit,
            cutoff=0,
        )
        missing[name] = suggestions

    return missing


def update_missing_parameter_suggestions(config):
    suggestions = build_missing_parameter_suggestions(config)

    if suggestions:
        config["missing_parameter_suggestions"] = suggestions
    else:
        config.pop("missing_parameter_suggestions", None)

    return config


def set_parameter_alias(json_path, logical_name, real_name):
    json_path = Path(json_path)
    config = json.loads(json_path.read_text(encoding="utf-8"))
    config.setdefault("parameter_aliases", {})[logical_name] = real_name
    update_missing_parameter_suggestions(config)
    json_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return config
