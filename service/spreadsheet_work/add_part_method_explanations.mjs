import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const outputDir = "../outputs/part_methods_explanations";
const outputPath = `${outputDir}/Удобный слой над API python.xlsx`;
await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("Методы Part");

const explanations = {
  C: [
    "Пояснение",
    "Обновляет активную деталь после изменения параметров, эскизов или операций.",
    "Сохраняет текущую деталь в существующий файл.",
    "Сохраняет деталь под новым именем. Можно сохранить как копию.",
    "Возвращает параметр детали по имени из общей коллекции Parameters.",
    "Возвращает пользовательский параметр по имени.",
    "Возвращает модельный параметр операции или эскиза по имени.",
    "Меняет выражение параметра, например 25 mm или d0 * 2.",
    "Создает новый пользовательский параметр по выражению и единицам.",
    "Возвращает операцию модели по имени из Features.",
    "Возвращает тело детали по номеру. По умолчанию первое тело.",
    "Возвращает рабочую плоскость по номеру или имени.",
    "Возвращает рабочую ось по номеру или имени.",
    "Возвращает рабочую точку по номеру или имени.",
  ],
  E: [
    "Пояснение",
    "Достает объект плоскости из грани, эскиза или рабочей плоскости.",
    "Проверяет, лежат ли два объекта в одной или параллельной плоскости с учетом смещения.",
    "Проверяет, лежат ли две грани в одной плоскости.",
    "Группирует список граней по совпадающим плоскостям.",
  ],
  G: [
    "Пояснение",
    "Убирает повторяющиеся грани из списка.",
    "Проверяет, похож ли объект на грань Inventor.",
    "Преобразует выбранный объект в грань, если грань спрятана внутри NativeObject или ContainingFace.",
    "Формирует короткое диагностическое описание выбранного объекта.",
    "Возвращает уникальные грани из текущего выделения Inventor.",
    "Запускает выбор грани пользователем. Можно ограничить выбор плоскими гранями.",
    "Сбрасывает ручной цвет граней к внешнему виду операции.",
  ],
  I: [
    "Пояснение",
    "Ищет существующий эскиз на той же плоскости, что и выбранная грань.",
    "Убирает повторяющиеся точки эскиза по координатам.",
    "Помечает точки эскиза как центры отверстий.",
  ],
  K: [
    "Пояснение",
    "Подбирает свободное имя операции, если имя уже занято.",
    "Собирает все тела детали в ObjectCollection.",
    "Назначает операцию на все тела многотельной детали.",
    "Создает сверленые отверстия по точкам эскиза.",
    "Создает отверстия с цековкой по точкам эскиза.",
  ],
};

for (const [column, values] of Object.entries(explanations)) {
  const endRow = values.length + 2;
  const range = sheet.getRange(`${column}3:${column}${endRow}`);
  range.values = values.map((value) => [value]);
  range.format.wrapText = true;
  range.format.verticalAlignment = "top";
  range.format.columnWidth = 42;
}

for (const column of ["B", "D", "F", "H", "J"]) {
  const methodRange = sheet.getRange(`${column}3:${column}16`);
  methodRange.format.columnWidth = 34;
  methodRange.format.wrapText = true;
}

for (const column of ["C", "E", "G", "I", "K"]) {
  const header = sheet.getRange(`${column}3`);
  header.format.font = { bold: true };
  header.format.fill = "#E2F0D9";
}

sheet.getRange("B3:K16").format.verticalAlignment = "top";
sheet.getRange("B3:K16").format.autofitRows();

workbook.recalculate();

const check = await workbook.inspect({
  kind: "table",
  sheetId: "Методы Part",
  range: "B3:K16",
  include: "values,formulas",
  tableMaxRows: 16,
  tableMaxCols: 10,
  tableMaxCellChars: 160,
});
console.log(check.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

const preview = await workbook.render({
  sheetName: "Методы Part",
  range: "B3:K16",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/after.png`, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(outputPath);
