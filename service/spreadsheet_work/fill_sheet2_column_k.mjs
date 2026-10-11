import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const outputDir = "../outputs/sheet2_column_k";
const outputPath = `${outputDir}/Удобный слой над API python.xlsx`;

const explanations = {
  5: "Пояснение",
  6: "Ссылка на запущенное приложение Autodesk Inventor. Через нее можно обращаться к COM API Inventor напрямую.",
  7: "Активный документ Inventor. Обычно это открытая деталь, сборка или чертеж, с которым сейчас работает пользователь.",
  8: "Короткий алиас для active_document. Удобен, когда в коде часто нужен текущий документ.",
  9: "ComponentDefinition активного документа. В детали через него доступны эскизы, тела, фичи и рабочая геометрия.",
  10: "Короткий алиас для component_definition. Нужен для компактной записи вроде inventor.comp.Sketches.",
  11: "Фабрика временных объектов Inventor. Используется для создания ObjectCollection, цветов и других служебных объектов.",
  12: "Фабрика временной геометрии Inventor. Создает точки, векторы и другие геометрические объекты для операций API.",
  13: "Текущее выделение активного документа. Через него можно получить выбранные пользователем грани, ребра или другие объекты.",
  15: "Пояснение",
  16: "Принудительно обновляет активный документ Inventor после изменений в модели.",
  17: "Создает COM-коллекцию Inventor и добавляет в нее переданные Python-объекты. Нужна для методов API, которые ждут ObjectCollection.",
  18: "Возвращает список уникальных граней из текущего выделения Inventor. Если debug=True, дополнительно печатает диагностическую информацию.",
  19: "Запускает интерактивный выбор объекта в Inventor с указанным фильтром SelectionFilterEnum и текстом подсказки.",
  20: "Просит пользователя выбрать грань детали. По умолчанию planar=True ограничивает выбор плоскими гранями.",
  21: "Просит пользователя выбрать конечное вхождение компонента в сборке.",
  22: "Ищет уже существующий эскиз на той же плоскости, что и переданная грань, с учетом необязательного префикса имени и смещений.",
  23: "Создает ObjectCollection со всеми SurfaceBodies из ComponentDefinition. Полезно для операций в многотельной детали.",
  24: "Пытается назначить фичу на все тела компонента, чтобы отверстие или операция затрагивали все SurfaceBodies.",
  25: "Создает одно или несколько сверленых отверстий по точкам эскиза с заданными диаметром, глубиной и направлением.",
  26: "Создает отверстия с цековкой по точкам эскиза. Используется для крепежных отверстий с основным диаметром и диаметром цековки.",
  27: "Сбрасывает ручное оформление выбранных граней к внешнему виду, заданному на уровне фичи.",
};

await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItemAt(1);

for (const [row, text] of Object.entries(explanations)) {
  sheet.getRange(`K${row}`).values = [[text]];
}

sheet.getRange("K5").format = {
  fill: "#D9EAF7",
  font: { name: "Arial", size: 10, bold: true, color: "#111827" },
};
sheet.getRange("K15").format = {
  fill: "#D9EAF7",
  font: { name: "Arial", size: 10, bold: true, color: "#111827" },
};

const bodyRanges = ["K6:K13", "K16:K27"];
for (const address of bodyRanges) {
  const range = sheet.getRange(address);
  range.format.font = { name: "Arial", size: 10, color: "#111827" };
  range.format.wrapText = true;
  range.format.verticalAlignment = "top";
  range.format.borders = { preset: "all", style: "thin", color: "#D9D9D9" };
}

sheet.getRange("K:K").format.columnWidth = 72;
sheet.getRange("K5:K27").format.autofitRows();

workbook.recalculate();

const check = await workbook.inspect({
  kind: "table",
  sheetId: sheet.name,
  range: "B3:K27",
  maxChars: 30000,
  tableMaxRows: 25,
  tableMaxCols: 10,
  tableMaxCellChars: 220,
});
console.log("CHECK_B3_K27");
console.log(check.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log("ERROR_SCAN");
console.log(errors.ndjson);

const preview = await workbook.render({
  sheetName: sheet.name,
  range: "A1:K30",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  `${outputDir}/sheet2_column_k_after.png`,
  new Uint8Array(await preview.arrayBuffer()),
);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`SAVED ${outputPath}`);
