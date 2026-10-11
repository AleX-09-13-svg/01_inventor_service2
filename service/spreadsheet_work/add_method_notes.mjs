import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const outputDir = "../outputs/part_methods_notes";
const outputPath = `${outputDir}/Удобный слой над API python.xlsx`;
await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("Методы Part");
workbook.comments.setSelf({ displayName: "User" });

const notesByCell = {
  B4: "Обновляет активную деталь после изменения параметров, эскизов или операций.",
  B5: "Сохраняет текущую деталь в существующий файл.",
  B6: "Сохраняет деталь под новым именем. Можно сохранить как копию.",
  B7: "Возвращает параметр детали по имени из общей коллекции Parameters.",
  B8: "Возвращает пользовательский параметр по имени.",
  B9: "Возвращает модельный параметр операции или эскиза по имени.",
  B10: "Меняет выражение параметра, например 25 mm или d0 * 2.",
  B11: "Создает новый пользовательский параметр по выражению и единицам.",
  B12: "Возвращает операцию модели по имени из Features.",
  B13: "Возвращает тело детали по номеру. По умолчанию первое тело.",
  B14: "Возвращает рабочую плоскость по номеру или имени.",
  B15: "Возвращает рабочую ось по номеру или имени.",
  B16: "Возвращает рабочую точку по номеру или имени.",

  D4: "Достает объект плоскости из грани, эскиза или рабочей плоскости.",
  D5: "Проверяет, лежат ли два объекта в одной или параллельной плоскости с учетом смещения.",
  D6: "Проверяет, лежат ли две грани в одной плоскости.",
  D7: "Группирует список граней по совпадающим плоскостям.",

  F4: "Убирает повторяющиеся грани из списка.",
  F5: "Проверяет, похож ли объект на грань Inventor.",
  F6: "Преобразует выбранный объект в грань, если грань спрятана внутри NativeObject или ContainingFace.",
  F7: "Формирует короткое диагностическое описание выбранного объекта.",
  F8: "Возвращает уникальные грани из текущего выделения Inventor.",
  F9: "Запускает выбор грани пользователем. Можно ограничить выбор плоскими гранями.",
  F10: "Сбрасывает ручной цвет граней к внешнему виду операции.",

  H4: "Ищет существующий эскиз на той же плоскости, что и выбранная грань.",
  H5: "Убирает повторяющиеся точки эскиза по координатам.",
  H6: "Помечает точки эскиза как центры отверстий.",

  J4: "Подбирает свободное имя операции, если имя уже занято.",
  J5: "Собирает все тела детали в ObjectCollection.",
  J6: "Назначает операцию на все тела многотельной детали.",
  J7: "Создает сверленые отверстия по точкам эскиза.",
  J8: "Создает отверстия с цековкой по точкам эскиза.",
};

const visibleValues = {
  B: [
    "PartCoreMethods",
    "update_part",
    "save_part",
    "save_part_as",
    "parameter",
    "user_parameter",
    "model_parameter",
    "set_parameter",
    "add_user_parameter",
    "feature",
    "surface_body",
    "work_plane",
    "work_axis",
    "work_point",
  ],
  D: [
    "PartGeometryMethods",
    "plane_geometry",
    "same_plane_entity",
    "same_plane",
    "group_faces_by_plane",
  ],
  F: [
    "PartFaceMethods",
    "unique_faces",
    "is_face_like",
    "face_from_selection",
    "selection_object_label",
    "selected_faces",
    "pick_face",
    "reset_faces_to_feature_appearance",
  ],
  H: [
    "PartSketchMethods",
    "sketch_on_face_plane",
    "unique_points",
    "mark_as_hole_centers",
  ],
  J: [
    "PartHoleMethods",
    "unique_feature_name",
    "all_surface_bodies",
    "set_all_bodies_affected",
    "add_holes",
    "add_counterbore_holes",
  ],
};

for (const column of ["C", "E", "G", "I", "K"]) {
  sheet.getRange(`${column}3:${column}16`).clear({ applyTo: "contents" });
  sheet.getRange(`${column}3:${column}16`).format.columnWidth = 3;
}

for (const [column, values] of Object.entries(visibleValues)) {
  const range = sheet.getRange(`${column}3:${column}${values.length + 2}`);
  range.values = values.map((value) => [value]);
  range.format.wrapText = true;
  range.format.columnWidth = 34;
}

for (const [address, body] of Object.entries(notesByCell)) {
  workbook.comments.addThread({ cell: sheet.getRange(address) }, body);
}

workbook.recalculate();

const check = await workbook.inspect({
  kind: "table",
  sheetId: "Методы Part",
  range: "B3:J16",
  include: "values,formulas",
  tableMaxRows: 16,
  tableMaxCols: 9,
  tableMaxCellChars: 120,
});
console.log(check.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const comments = await workbook.inspect({
  kind: "thread",
  sheetId: "Методы Part",
  maxChars: 10000,
});
console.log(comments.ndjson);

const preview = await workbook.render({
  sheetName: "Методы Part",
  range: "B3:J16",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/after.png`, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
