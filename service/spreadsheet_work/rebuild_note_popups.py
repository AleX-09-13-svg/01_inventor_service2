from __future__ import annotations

import re
import shutil
import zipfile
from html import escape
from pathlib import Path
from xml.etree import ElementTree as ET


INPUT = Path("../infa/Удобный слой над API python.xlsx")
OUTPUT_DIR = Path("../outputs/part_methods_normal_note_popups")
OUTPUT = OUTPUT_DIR / "Удобный слой над API python.xlsx"

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def cell_to_row_col(address: str) -> tuple[int, int]:
    match = re.fullmatch(r"([A-Z]+)([0-9]+)", address)
    if match is None:
        raise ValueError(address)

    letters, row_text = match.groups()
    col = 0
    for letter in letters:
        col = col * 26 + (ord(letter) - ord("A") + 1)

    return int(row_text) - 1, col - 1


def comment_refs(comments_xml: bytes) -> list[str]:
    root = ET.fromstring(comments_xml)
    return [
        comment.attrib["ref"]
        for comment in root.findall(f".//{{{NS_MAIN}}}comment")
    ]


def build_vml(refs: list[str]) -> str:
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

    for index, ref in enumerate(refs, start=1):
        row, col = cell_to_row_col(ref)
        shape_id = f"_x0000_s{1024 + index}"
        z_index = index
        anchor = f"{col + 1}, 15, {row}, 2, {col + 3}, 15, {row + 4}, 16"

        lines.extend(
            [
                f' <v:shape id="{escape(shape_id)}" type="#_x0000_t202"',
                "  style='position:absolute;margin-left:80pt;margin-top:5pt;"
                f"width:220pt;height:90pt;z-index:{z_index};visibility:hidden'",
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
    return "\r\n".join(lines)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    temp = OUTPUT.with_suffix(".tmp.xlsx")

    with zipfile.ZipFile(INPUT, "r") as source:
        refs = comment_refs(source.read("xl/comments2.xml"))
        vml = build_vml(refs).encode("utf-8")

        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for info in source.infolist():
                data = source.read(info.filename)
                if info.filename == "xl/drawings/vmlDrawing2.vml":
                    data = vml
                target.writestr(info, data)

    shutil.move(temp, OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
