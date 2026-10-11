from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


INPUT = Path("../infa/Удобный слой над API python.xlsx")
OUTPUT_DIR = Path("../outputs/part_methods_add_sketch")
OUTPUT = OUTPUT_DIR / "Удобный слой над API python.xlsx"

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
ET.register_namespace("", NS_MAIN)


VISIBLE_VALUES = {
    "A3": "PartCoreMethods",
    "A4": "update_part",
    "A5": "save_part",
    "A6": "save_part_as",
    "A7": "parameter",
    "A8": "user_parameter",
    "A9": "model_parameter",
    "A10": "set_parameter",
    "A11": "add_user_parameter",
    "A12": "feature",
    "A13": "surface_body",
    "A14": "work_plane",
    "A15": "work_axis",
    "A16": "work_point",
    "C3": "PartGeometryMethods",
    "C4": "plane_geometry",
    "C5": "same_plane_entity",
    "C6": "same_plane",
    "C7": "group_faces_by_plane",
    "E3": "PartFaceMethods",
    "E4": "unique_faces",
    "E5": "is_face_like",
    "E6": "face_from_selection",
    "E7": "selection_object_label",
    "E8": "selected_faces",
    "E9": "pick_face",
    "E10": "reset_faces_to_feature_appearance",
    "G3": "PartSketchMethods",
    "G4": "add_sketch",
    "G5": "sketch_on_face_plane",
    "G6": "get_or_create_sketch_on_face",
    "G7": "unique_points",
    "G8": "mark_as_hole_centers",
    "I3": "PartHoleMethods",
    "I4": "unique_feature_name",
    "I5": "all_surface_bodies",
    "I6": "set_all_bodies_affected",
    "I7": "add_holes",
    "I8": "add_counterbore_holes",
}

COMMENTS = {
    "A4": "Обновляет активную деталь после изменения параметров, эскизов или операций.",
    "A5": "Сохраняет текущую деталь в существующий файл.",
    "A6": "Сохраняет деталь под новым именем. Можно сохранить как копию.",
    "A7": "Возвращает параметр детали по имени из общей коллекции Parameters.",
    "A8": "Возвращает пользовательский параметр по имени.",
    "A9": "Возвращает модельный параметр операции или эскиза по имени.",
    "A10": "Меняет выражение параметра, например 25 mm или d0 * 2.",
    "A11": "Создает новый пользовательский параметр по выражению и единицам.",
    "A12": "Возвращает операцию модели по имени из Features.",
    "A13": "Возвращает тело детали по номеру. По умолчанию первое тело.",
    "A14": "Возвращает рабочую плоскость по номеру или имени.",
    "A15": "Возвращает рабочую ось по номеру или имени.",
    "A16": "Возвращает рабочую точку по номеру или имени.",
    "C4": "Достает объект плоскости из грани, эскиза или рабочей плоскости.",
    "C5": "Проверяет, лежат ли два объекта в одной или параллельной плоскости с учетом смещения.",
    "C6": "Проверяет, лежат ли две грани в одной плоскости.",
    "C7": "Группирует список граней по совпадающим плоскостям.",
    "E4": "Убирает повторяющиеся грани из списка.",
    "E5": "Проверяет, похож ли объект на грань Inventor.",
    "E6": "Преобразует выбранный объект в грань, если грань спрятана внутри NativeObject или ContainingFace.",
    "E7": "Формирует короткое диагностическое описание выбранного объекта.",
    "E8": "Возвращает уникальные грани из текущего выделения Inventor.",
    "E9": "Запускает выбор грани пользователем. Можно ограничить выбор плоскими гранями.",
    "E10": "Сбрасывает ручной цвет граней к внешнему виду операции.",
    "G4": "Создает новый эскиз на грани, рабочей плоскости или другом planar entity.",
    "G5": "Ищет существующий эскиз на той же плоскости, что и выбранная грань.",
    "G6": "Возвращает существующий эскиз на грани или создает новый, если подходящего эскиза нет.",
    "G7": "Убирает повторяющиеся точки эскиза по координатам.",
    "G8": "Помечает точки эскиза как центры отверстий.",
    "I4": "Подбирает свободное имя операции, если имя уже занято.",
    "I5": "Собирает все тела детали в ObjectCollection.",
    "I6": "Назначает операцию на все тела многотельной детали.",
    "I7": "Создает сверленые отверстия по точкам эскиза.",
    "I8": "Создает отверстия с цековкой по точкам эскиза.",
}


def cell_to_row_col(address: str) -> tuple[int, int]:
    match = re.fullmatch(r"([A-Z]+)([0-9]+)", address)
    if match is None:
        raise ValueError(address)

    letters, row_text = match.groups()
    col = 0
    for letter in letters:
        col = col * 26 + (ord(letter) - ord("A") + 1)

    return int(row_text), col


def a1_to_zero(address: str) -> tuple[int, int]:
    row, col = cell_to_row_col(address)
    return row - 1, col - 1


def set_inline_string(root: ET.Element, address: str, text: str) -> None:
    row_number, _ = cell_to_row_col(address)
    row = root.find(f".//{{{NS_MAIN}}}row[@r='{row_number}']")
    if row is None:
        sheet_data = root.find(f"{{{NS_MAIN}}}sheetData")
        row = ET.SubElement(sheet_data, f"{{{NS_MAIN}}}row", {"r": str(row_number)})

    cell = row.find(f"{{{NS_MAIN}}}c[@r='{address}']")
    if cell is None:
        cell = ET.SubElement(row, f"{{{NS_MAIN}}}c", {"r": address, "s": "24"})

    for child in list(cell):
        cell.remove(child)

    cell.set("t", "inlineStr")
    if "s" not in cell.attrib:
        cell.set("s", "24")

    inline = ET.SubElement(cell, f"{{{NS_MAIN}}}is")
    t = ET.SubElement(inline, f"{{{NS_MAIN}}}t")
    t.text = text


def clear_cell(root: ET.Element, address: str) -> None:
    row_number, _ = cell_to_row_col(address)
    row = root.find(f".//{{{NS_MAIN}}}row[@r='{row_number}']")
    if row is None:
        return

    cell = row.find(f"{{{NS_MAIN}}}c[@r='{address}']")
    if cell is None:
        return

    for child in list(cell):
        cell.remove(child)
    cell.attrib.pop("t", None)


def update_sheet(xml_data: bytes) -> bytes:
    root = ET.fromstring(xml_data)

    for address, value in VISIBLE_VALUES.items():
        set_inline_string(root, address, value)

    for address in ("G9", "G10", "G11", "G12", "G13", "G14", "G15", "G16"):
        if address not in VISIBLE_VALUES:
            clear_cell(root, address)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def build_comments() -> bytes:
    comments = ET.Element(f"{{{NS_MAIN}}}comments")
    authors = ET.SubElement(comments, f"{{{NS_MAIN}}}authors")
    author = ET.SubElement(authors, f"{{{NS_MAIN}}}author")
    author.text = "Пояснение"

    comment_list = ET.SubElement(comments, f"{{{NS_MAIN}}}commentList")
    for address, text in COMMENTS.items():
        comment = ET.SubElement(
            comment_list,
            f"{{{NS_MAIN}}}comment",
            {"ref": address, "authorId": "0", "shapeId": "0"},
        )
        text_node = ET.SubElement(comment, f"{{{NS_MAIN}}}text")
        run = ET.SubElement(text_node, f"{{{NS_MAIN}}}r")
        run_props = ET.SubElement(run, f"{{{NS_MAIN}}}rPr")
        ET.SubElement(run_props, f"{{{NS_MAIN}}}sz", {"val": "11"})
        ET.SubElement(run_props, f"{{{NS_MAIN}}}color", {"theme": "1"})
        ET.SubElement(run_props, f"{{{NS_MAIN}}}rFont", {"val": "Calibri"})
        t = ET.SubElement(run, f"{{{NS_MAIN}}}t")
        t.text = text

    return ET.tostring(comments, encoding="utf-8", xml_declaration=True)


def build_vml() -> bytes:
    lines = [
        '<xml xmlns:v="urn:schemas-microsoft-com:vml"',
        ' xmlns:o="urn:schemas-microsoft-com:office:office"',
        ' xmlns:x="urn:schemas-microsoft-com:office:excel">',
        ' <o:shapelayout v:ext="edit">',
        '  <o:idmap v:ext="edit" data="1"/>',
        ' </o:shapelayout>',
        ' <v:shapetype id="_x0000_t202" coordsize="21600,21600" o:spt="202"',
        '  path="m,l,21600r21600,l21600,xe">',
        '  <v:stroke joinstyle="miter"/>',
        '  <v:path gradientshapeok="t" o:connecttype="rect"/>',
        ' </v:shapetype>',
    ]

    for index, address in enumerate(COMMENTS, start=1):
        row, col = a1_to_zero(address)
        shape_id = f"_x0000_s{1024 + index}"
        anchor = f"{col + 1}, 15, {row}, 2, {col + 3}, 15, {row + 4}, 16"
        lines.extend(
            [
                f' <v:shape id="{shape_id}" type="#_x0000_t202"',
                "  style='position:absolute;margin-left:80pt;margin-top:5pt;"
                f"width:220pt;height:90pt;z-index:{index};visibility:hidden'",
                '  fillcolor="#ffffe1" o:insetmode="auto">',
                '  <v:fill color2="#ffffe1"/>',
                '  <v:shadow on="t" type="single" color="black" obscured="t"/>',
                '  <v:path o:connecttype="none"/>',
                '  <o:lock v:ext="edit" selection="f"/>',
                "  <v:textbox style='mso-direction-alt:auto'>",
                "   <div style='text-align:left'></div>",
                "  </v:textbox>",
                '  <x:ClientData ObjectType="Note">',
                "   <x:MoveWithCells/>",
                "   <x:SizeWithCells/>",
                f"   <x:Anchor>{anchor}</x:Anchor>",
                "   <x:AutoFill>False</x:AutoFill>",
                f"   <x:Row>{row}</x:Row>",
                f"   <x:Column>{col}</x:Column>",
                "  </x:ClientData>",
                " </v:shape>",
            ]
        )

    lines.append("</xml>")
    return "\r\n".join(lines).encode("utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temp = OUTPUT.with_suffix(".tmp.xlsx")

    with zipfile.ZipFile(INPUT, "r") as source, zipfile.ZipFile(
        temp, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename == "xl/worksheets/sheet6.xml":
                data = update_sheet(data)
            elif info.filename == "xl/comments2.xml":
                data = build_comments()
            elif info.filename == "xl/drawings/vmlDrawing2.vml":
                data = build_vml()
            target.writestr(info, data)

    shutil.move(temp, OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
