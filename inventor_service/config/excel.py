import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {
    "a": MAIN_NS,
    "rel": REL_NS,
    "r": DOC_REL_NS,
}


def _column_index(cell_ref):
    letters = re.match(r"[A-Z]+", cell_ref).group(0)
    index = 0

    for char in letters:
        index = index * 26 + ord(char) - 64

    return index - 1


def _shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    result = []

    for item in root.findall("a:si", NS):
        result.append("".join(node.text or "" for node in item.findall(".//a:t", NS)))

    return result


def _sheet_path(archive, sheet_name=None):
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in relationships.findall("rel:Relationship", NS)
    }
    sheets = workbook.findall("a:sheets/a:sheet", NS)

    if sheet_name is None:
        sheet = sheets[0]
        rel_id = sheet.attrib[f"{{{DOC_REL_NS}}}id"]
        target = targets[rel_id]
        if not target.startswith("xl/"):
            target = f"xl/{target}"
        return target

    for sheet in sheets:
        if sheet.attrib["name"] != sheet_name:
            continue

        rel_id = sheet.attrib[f"{{{DOC_REL_NS}}}id"]
        target = targets[rel_id]
        if not target.startswith("xl/"):
            target = f"xl/{target}"
        return target

    raise KeyError(f"Worksheet not found: {sheet_name}")


def _cell_value(cell, shared_strings):
    value = cell.find("a:v", NS)
    cell_type = cell.attrib.get("t")

    if cell_type == "s" and value is not None:
        return shared_strings[int(value.text)]

    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//a:t", NS))

    if value is None:
        return None

    text = value.text
    if text is None:
        return None

    try:
        number = float(text)
    except ValueError:
        return text

    if number.is_integer():
        return int(number)
    return number


def read_xlsx_table(path, sheet_name, header_row=None):
    path = Path(path)

    with zipfile.ZipFile(path) as archive:
        shared_strings = _shared_strings(archive)
        sheet = ET.fromstring(archive.read(_sheet_path(archive, sheet_name)))

    rows = []

    for row in sheet.findall(".//a:sheetData/a:row", NS):
        values = {}
        for cell in row.findall("a:c", NS):
            values[_column_index(cell.attrib["r"])] = _cell_value(cell, shared_strings)

        if values:
            rows.append([values.get(index) for index in range(max(values) + 1)])

    if not rows:
        return []

    if header_row is None:
        header_index = 0
        for index, row in enumerate(rows):
            non_empty = sum(value not in (None, "") for value in row)
            if non_empty >= 2:
                header_index = index
                break
    else:
        header_index = header_row - 1

    headers = [
        str(value).strip() if value is not None else ""
        for value in rows[header_index]
    ]
    result = []

    for row in rows[header_index + 1 :]:
        item = {}
        for index, header in enumerate(headers):
            if not header:
                continue
            item[header] = row[index] if index < len(row) else None

        if any(value not in (None, "") for value in item.values()):
            result.append(item)

    return result


def read_xlsx_column(path, sheet_name=None, column=1, skip_header=True):
    path = Path(path)
    column_index = column - 1

    with zipfile.ZipFile(path) as archive:
        shared_strings = _shared_strings(archive)
        sheet = ET.fromstring(archive.read(_sheet_path(archive, sheet_name)))

    values = []

    for row in sheet.findall(".//a:sheetData/a:row", NS):
        for cell in row.findall("a:c", NS):
            if _column_index(cell.attrib["r"]) != column_index:
                continue

            value = _cell_value(cell, shared_strings)
            if value not in (None, ""):
                values.append(str(value).strip())
            break

    if skip_header and values:
        return values[1:]

    return values


def write_json(data, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return data
