import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const outputDir = "../outputs/excel_explanations";
const outputPath = `${outputDir}/Удобный слой над API python_с_пояснениями.xlsx`;

const explanations = [
  ["Пояснение"],
  [""],
  ["Корневая папка проекта с библиотекой и вспомогательными материалами."],
  ["Описание пакета, зависимостей, версии Python и настроек сборки."],
  ["Краткое описание назначения библиотеки, установки и базовых примеров."],
  ["Папка с готовыми сценариями использования API."],
  ["Пример создания новой детали Inventor из Python."],
  ["Пример применения цвета к выбранной грани модели."],
  ["Пример создания отверстий на выбранной грани или по точкам эскиза."],
  ["Основной пакет библиотеки поверх Inventor API."],
  ["Публичные импорты: Inventor, константы и часто используемые функции."],
  ["Главный фасад подключения к Inventor и доступ к подсистемам библиотеки."],
  ["Именованные константы Inventor API вместо числовых значений в коде."],
  ["Функции перевода единиц, например миллиметры в внутренние единицы Inventor."],
  ["Исключения библиотеки: ошибки подключения, выбора объектов и операций API."],
  ["Контекстные менеджеры для безопасных транзакций Inventor."],
  ["Protocol-типы для COM-объектов, чтобы IDE подсказывала свойства и методы."],
  ["Создание, открытие, сохранение и обновление документов Inventor."],
  ["Работа с SelectSet и интерактивным выбором деталей, граней и других объектов."],
  ["Создание эскизов и базовых 2D-примитивов: линии, прямоугольники, окружности."],
  ["Операции модели: отверстия, выдавливания, фаски, скругления и другие features."],
  ["Работа с внешними видами, материалами, цветами и AppearanceAssets."],
  ["Вспомогательная геометрия: точки, коллекции, вершины, грани и обход COM-коллекций."],
  ["Папка с автоматическими тестами для независимых частей библиотеки."],
  ["Тесты для функций перевода единиц измерения."],
  ["Тесты для помощников обхода и обработки коллекций Inventor API."],
];

await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("Лист1");

sheet.getRange("E1:E26").values = explanations;
sheet.getRange("E1").format.font = { bold: true };
sheet.getRange("E1:E26").format.wrapText = true;
sheet.getRange("E1:E26").format.verticalAlignment = "center";
sheet.getRange("E1:E26").format.columnWidth = 58;

workbook.recalculate();

const check = await workbook.inspect({
  kind: "table",
  sheetId: "Лист1",
  range: "B1:E26",
  maxChars: 10000,
  tableMaxRows: 26,
  tableMaxCols: 4,
  tableMaxCellChars: 180,
});
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
  sheetName: "Лист1",
  range: "B1:E26",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/after.png`, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`SAVED ${outputPath}`);
