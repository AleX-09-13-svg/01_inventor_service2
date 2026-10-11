import json
import threading
from pathlib import Path

from .excel import read_xlsx_column, write_json
from .parameters import (
    build_linked_parameters,
    linked_parameter_source_names,
    update_missing_parameter_suggestions,
)


DEFAULT_PARAMETER_NAMES_PATH = (
    "D:\\\u041a\u043e\u043f\u0438\u044f Google \u0434\u0438\u0441\u043a\u0430"
    "\\01\u0411\u0438\u0431\u043b\u0438\u043e\u0442\u0435\u043a\u0438 "
    "\u043d\u0430\u0441\u0442\u0440\u043e\u0435\u043a "
    "\u0418\u043d\u0432\u0435\u043d\u0442\u043e\u0440 \u0438 "
    "\u0411\u0430\u0437\u0438\u0441\\\u0418\u043d\u0432\u0435\u043d\u0442\u043e\u0440"
    "\\06_\u041f\u0430\u0440\u0430\u043c\u0435\u0442\u0440\u044b "
    "\u043f\u0440\u0438\u0441\u0430\u0434\u043a\u0438\\"
    "\u0422\u0430\u0431\u043b\u0438\u0446\u0430_"
    "\u043f\u0440\u0438\u0441\u0430\u0434\u043e\u043a.xlsx"
)


def _ordered_difference(left, right):
    right_set = set(right)
    return [name for name in left if name not in right_set]


def _migrate_aliases_to_safe_names(config):
    source_to_name = {
        item.get("source_name"): item.get("name")
        for item in config.get("linked_parameters", [])
        if item.get("source_name") and item.get("name")
    }
    available_names = {
        item["name"]
        for item in config.get("linked_parameters", [])
        if item.get("name")
    }
    aliases = config.setdefault("parameter_aliases", {})

    for key, value in list(aliases.items()):
        if value in available_names:
            continue
        if value in source_to_name:
            aliases[key] = source_to_name[value]


def refresh_linked_parameters_from_excel(
    json_path,
    parameter_names_path=DEFAULT_PARAMETER_NAMES_PATH,
    sheet_name=None,
    column=1,
    skip_header=False,
):
    json_path = Path(json_path)
    config = {}

    if json_path.exists():
        config = json.loads(json_path.read_text(encoding="utf-8"))
    old_names = linked_parameter_source_names(config)

    names = read_xlsx_column(
        parameter_names_path,
        sheet_name=sheet_name,
        column=column,
        skip_header=skip_header,
    )
    config["linked_parameters"] = build_linked_parameters(names)
    config.setdefault("parameter_aliases", {})
    _migrate_aliases_to_safe_names(config)
    config.setdefault("operations", [])

    config["parameter_name_changes"] = {
        "missing_names": _ordered_difference(old_names, names),
        "new_names": _ordered_difference(names, old_names),
    }
    update_missing_parameter_suggestions(config)

    return write_json(config, json_path)


def schedule_linked_parameters_refresh(
    json_path,
    parameter_names_path=DEFAULT_PARAMETER_NAMES_PATH,
    delay_seconds=60,
    sheet_name=None,
    column=1,
    skip_header=False,
    daemon=False,
):
    timer = threading.Timer(
        delay_seconds,
        refresh_linked_parameters_from_excel,
        kwargs={
            "json_path": json_path,
            "parameter_names_path": parameter_names_path,
            "sheet_name": sheet_name,
            "column": column,
            "skip_header": skip_header,
        },
    )
    timer.daemon = daemon
    timer.start()
    return timer
