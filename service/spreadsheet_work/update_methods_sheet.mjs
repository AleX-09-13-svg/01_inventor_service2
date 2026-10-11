import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const apiPath = "../../inventor_service/inventor_api.py";
const outputDir = "../outputs/methods_sheet";
const outputPath = `${outputDir}/Удобный слой над API python.xlsx`;

const explanations = {
  __init__: "Подключается к уже запущенному Autodesk Inventor через COM и делает окно Inventor видимым.",
  mm: "Переводит миллиметры во внутренние единицы Inventor, используемые в модели.",
  mm_text: "Готовит размер для Inventor: строку оставляет как есть, число превращает в выражение в миллиметрах.",
  create_part: "Создает новый документ детали Inventor.",
  create_sketch: "Создает базовый 2D-эскиз на плоскости XY активной или переданной детали.",
  create_sketch_on_face: "Создает эскиз на выбранной или переданной плоской грани, при необходимости проецирует ребра.",
  create_rectangle: "Рисует прямоугольник в эскизе по ширине, высоте и центру.",
  create_circle: "Рисует окружность в эскизе по центру и радиусу.",
  _feature_operation: "Преобразует текстовое имя операции фичи в числовую константу Inventor.",
  _extent_direction: "Преобразует текстовое направление выдавливания или отверстия в константу Inventor.",
  create_profile: "Создает твердотельный профиль из замкнутой геометрии эскиза.",
  create_extrude: "Создает выдавливание профиля эскиза с операцией join, cut, intersect или new body.",
  create_feature: "Общий фасад для создания фич; сейчас направляет запросы на выдавливание.",
  cut_extrude: "Создает выдавливание-вырез по эскизу.",
  join_extrude: "Создает выдавливание с добавлением материала по эскизу.",
  create_hole_point: "Добавляет в эскиз точку, помеченную как центр отверстия.",
  create_hole_point_on_face: "Ставит центр отверстия в эскизе по точке, лежащей на выбранной грани.",
  create_hole: "Создает сверленое отверстие по точкам эскиза или коллекции точек.",
  create_hole_on_face: "Создает эскиз на грани, ставит центр отверстия и сразу строит отверстие.",
  ActiveDocument: "Возвращает активный документ Inventor.",
  active_document: "Алиас для ActiveDocument в стиле snake_case.",
  ComponentDefinition: "Возвращает ComponentDefinition активного документа.",
  component_definition: "Алиас для ComponentDefinition в стиле snake_case.",
  SelectSet: "Возвращает текущее выделение активного документа.",
  select_set: "Алиас для SelectSet в стиле snake_case.",
  get_selected: "Возвращает объект из текущего выделения по индексу Inventor, начиная с 1.",
  get_selected_native: "Возвращает NativeObject для выбранного объекта, если он доступен.",
  safe_getattr: "Безопасно читает свойство COM-объекта и возвращает значение по умолчанию при ошибке.",
  object_type: "Возвращает COM-тип объекта Inventor, если он доступен.",
  native_object: "Нормализует proxy-объект Inventor до NativeObject, если это возможно.",
  containing_occurrence: "Возвращает вхождение сборки, которому принадлежит объект, если оно есть.",
  is_com_collection: "Проверяет, похож ли объект на COM-коллекцию Inventor с Count и Item.",
  selection_items: "Перебирает все объекты текущего SelectSet, опционально приводя их к NativeObject.",
  is_part_like: "Проверяет, похож ли объект на деталь или ComponentDefinition.",
  is_face_like: "Проверяет, похож ли объект на грань Inventor по ключевым свойствам.",
  is_sketch_like: "Проверяет, похож ли объект на эскиз с точками и профилями.",
  as_face: "Преобразует объект, proxy или source object к грани Inventor либо сообщает об ошибке.",
  get_selected_part: "Возвращает выбранную деталь или вхождение детали из текущего выделения.",
  get_selected_face: "Возвращает выбранную грань по индексу, с возможностью получить native-объект.",
  selected_faces: "Возвращает список всех граней, найденных в текущем выделении.",
  find_selected_face: "Находит первую грань в текущем выделении.",
  pick_face: "Интерактивно просит пользователя выбрать грань, по умолчанию только плоскую.",
  pick_part: "Интерактивно просит пользователя выбрать деталь или листовое вхождение сборки.",
  pick: "Вызывает стандартный интерактивный выбор Inventor CommandManager.Pick.",
  get_appearance: "Ищет внешний вид в документе по DisplayName или Name.",
  find_appearance: "Алиас для get_appearance.",
  print_appearances: "Печатает доступные внешние виды активного или переданного документа.",
  create_color_appearance: "Создает или возвращает внешний вид с заданным RGB-цветом.",
  get_face_document: "Определяет документ детали, которому принадлежит грань.",
  get_face_part_document: "Алиас для get_face_document.",
  apply_appearance: "Назначает объекту внешний вид и включает переопределение внешнего вида.",
  set_selected_face_appearance: "Красит выбранную грань существующим внешним видом по имени.",
  set_selected_face_color: "Создает RGB-внешний вид и применяет его к выбранной грани.",
  debug_selected: "Печатает диагностическую информацию о выбранном объекте Inventor.",
};

function extractMethods(source) {
  const lines = source.split(/\r?\n/);
  const seen = new Set();
  const methods = [];

  for (const line of lines) {
    const match = line.match(/^    def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/);
    if (!match) continue;

    const name = match[1];
    if (seen.has(name)) continue;

    seen.add(name);
    methods.push(name);
  }

  return methods;
}

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const source = await fs.readFile(apiPath, "utf8");
const methodNames = extractMethods(source);

let sheet = workbook.worksheets.getItemOrNullObject("Методы API");
if (sheet.isNullObject) {
  sheet = workbook.worksheets.add("Методы API");
}

sheet.getRange("A1:D200").clear({ applyTo: "all" });
sheet.showGridLines = false;

sheet.getRange("A1").values = [["Методы inventor_api.py"]];
sheet.getRange("A1").format.font = { name: "Arial", size: 14, bold: true, color: "#1F2937" };
sheet.getRange("A2").values = [["Список методов класса Inventor и краткие пояснения к ним."]];
sheet.getRange("A2").format.font = { name: "Arial", size: 10, italic: true, color: "#4B5563" };

const rows = [
  ["Метод", "Пояснение"],
  ...methodNames.map((name) => [name, explanations[name] ?? "Метод из inventor_api.py. Требуется уточнить назначение по коду."]),
];

const tableRange = sheet.getRangeByIndexes(3, 0, rows.length, 2);
tableRange.values = rows;
tableRange.format.font = { name: "Arial", size: 10, color: "#111827" };
tableRange.format.verticalAlignment = "center";
tableRange.format.borders = { preset: "all", style: "thin", color: "#D1D5DB" };

const header = sheet.getRange("A4:B4");
header.format = {
  fill: "#374151",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
};
header.format.horizontalAlignment = "center";

const body = sheet.getRangeByIndexes(4, 0, methodNames.length, 2);
body.format.wrapText = true;
body.format.verticalAlignment = "top";
sheet.getRangeByIndexes(4, 0, methodNames.length, 1).format.font = {
  name: "Consolas",
  size: 10,
  color: "#111827",
};

sheet.getRange("A:A").format.columnWidth = 27;
sheet.getRange("B:B").format.columnWidth = 95;
sheet.getRange("A1:B1").format.borders = {
  bottom: { style: "medium", color: "#9CA3AF" },
};
sheet.getRange("A4:B4").format.rowHeight = 24;
sheet.getRangeByIndexes(4, 0, methodNames.length, 2).format.rowHeight = 34;
sheet.freezePanes.freezeRows(4);

try {
  sheet.tables.add(`A4:B${methodNames.length + 4}`, true, "InventorApiMethods");
} catch (error) {
  // If the table already exists after re-import, the formatted range still provides the requested list.
}

workbook.recalculate();

const check = await workbook.inspect({
  kind: "table,region",
  sheetId: "Методы API",
  range: `A1:B${Math.min(methodNames.length + 4, 25)}`,
  tableMaxRows: 25,
  tableMaxCols: 2,
  maxChars: 12000,
});
console.log(check.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
  maxChars: 12000,
});
console.error(errors.ndjson);

await fs.mkdir(outputDir, { recursive: true });
const preview = await workbook.render({
  sheetName: "Методы API",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  `${outputDir}/methods_sheet_preview.png`,
  new Uint8Array(await preview.arrayBuffer()),
);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.error(`saved=${outputPath}`);
