from .excel import read_xlsx_column, read_xlsx_table, write_json
from .parameters import build_linked_parameters, update_missing_parameter_suggestions


def build_part_config_from_excel(
    excel_path,
    json_path=None,
    parameter_sheet="InventorParameters",
    operation_sheet="Operations",
    parameter_names_path=None,
    parameter_names_sheet=None,
):
    if parameter_names_path:
        parameters = build_linked_parameters(
            read_xlsx_column(
                parameter_names_path,
                sheet_name=parameter_names_sheet,
                column=1,
                skip_header=False,
            )
        )
    else:
        parameters = read_xlsx_table(excel_path, parameter_sheet)

    operations = read_xlsx_table(excel_path, operation_sheet)

    config = {
        "linked_parameters": [
            {
                "name": row["name"],
                **{
                    key: value
                    for key, value in row.items()
                    if key != "name" and value not in (None, "")
                },
            }
            for row in parameters
            if row.get("name")
        ],
        "operations": [
            {
                key: value
                for key, value in row.items()
                if value not in (None, "")
            }
            for row in operations
        ],
    }
    config["parameter_aliases"] = {}
    update_missing_parameter_suggestions(config)

    if json_path:
        write_json(config, json_path)

    return config
