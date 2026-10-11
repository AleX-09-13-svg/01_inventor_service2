from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


INPUT = Path("../infa/Удобный слой над API python.xlsx")
OUTPUT_DIR = Path("../outputs/part_methods_legacy_notes")
OUTPUT = OUTPUT_DIR / "Удобный слой над API python.xlsx"

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"

ET.register_namespace("", NS_MAIN)
ET.register_namespace("", NS_REL)
ET.register_namespace("", NS_CT)


def xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def clean_comment_text(text: str) -> str:
    marker = "Comment:"
    if marker in text:
        return text.split(marker, 1)[1].strip()
    return text.strip()


def update_comments(xml_data: bytes) -> bytes:
    root = ET.fromstring(xml_data)

    authors = root.find(f"{{{NS_MAIN}}}authors")
    if authors is not None:
        authors.clear()
        author = ET.SubElement(authors, f"{{{NS_MAIN}}}author")
        author.text = "Пояснение"

    for comment in root.findall(f".//{{{NS_MAIN}}}comment"):
        comment.set("authorId", "0")
        text_node = comment.find(f".//{{{NS_MAIN}}}t")
        if text_node is not None and text_node.text:
            text_node.text = clean_comment_text(text_node.text)

    return xml_bytes(root)


def remove_relationships(xml_data: bytes, blocked_type_fragments: tuple[str, ...]) -> bytes:
    root = ET.fromstring(xml_data)
    for rel in list(root):
        rel_type = rel.attrib.get("Type", "")
        if any(fragment in rel_type for fragment in blocked_type_fragments):
            root.remove(rel)
    return xml_bytes(root)


def remove_content_types(xml_data: bytes, blocked_part_names: tuple[str, ...]) -> bytes:
    root = ET.fromstring(xml_data)
    for child in list(root):
        part_name = child.attrib.get("PartName", "")
        if part_name in blocked_part_names:
            root.remove(child)
    return xml_bytes(root)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temp = OUTPUT.with_suffix(".tmp.xlsx")

    skip_parts = {
        "xl/threadedcomments/threadedcomment.xml",
        "xl/persons/person.xml",
    }

    with zipfile.ZipFile(INPUT, "r") as source, zipfile.ZipFile(
        temp, "w", compression=zipfile.ZIP_DEFLATED
    ) as target:
        for info in source.infolist():
            if info.filename in skip_parts:
                continue

            data = source.read(info.filename)

            if info.filename == "xl/comments2.xml":
                data = update_comments(data)
            elif info.filename == "xl/worksheets/_rels/sheet6.xml.rels":
                data = remove_relationships(data, ("threadedComment",))
            elif info.filename == "xl/_rels/workbook.xml.rels":
                data = remove_relationships(data, ("/person",))
            elif info.filename == "[Content_Types].xml":
                data = remove_content_types(
                    data,
                    (
                        "/xl/threadedcomments/threadedcomment.xml",
                        "/xl/persons/person.xml",
                    ),
                )

            target.writestr(info, data)

    shutil.move(temp, OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
