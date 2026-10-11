import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const apiPath = "../../inventor_service/inventor_api.py";
const outputDir = "../outputs/current_methods_sheet";
const outputPath = `${outputDir}/Удобный слой над API python.xlsx`;

const constantRows = [
  ["kPartDocumentObject = 12290", "DocumentTypeEnum: документ-деталь", "Сравнивать с doc.DocumentType, чтобы понять, что открыт документ детали .ipt."],
  ["kPositiveExtentDirection = 20993", "PartFeatureExtentDirectionEnum: положительное направление", "Передавать в операции отверстий или выдавливания, когда построение идет в положительную сторону."],
  ["kNegativeExtentDirection = 20994", "PartFeatureExtentDirectionEnum: отрицательное направление", "Передавать в операции отверстий или выдавливания, когда построение идет в отрицательную сторону."],
  ["kHorizontalDim = 19201", "DimensionOrientationEnum: горизонтальный размер", "Использовать для создания или выбора горизонтального размера."],
  ["kVerticalDim = 19202", "DimensionOrientationEnum: вертикальный размер", "Использовать для создания или выбора вертикального размера."],
  ["kAlignedDim = 19203", "DimensionOrientationEnum: выровненный размер", "Использовать для размера, выровненного по линии или двум точкам."],
  ["kPartFaceFilter = 15877", "SelectionFilterEnum: грань детали", "Фильтр интерактивного выбора любой грани детали через CommandManager.Pick."],
  ["kPartFacePlanarFilter = 15878", "SelectionFilterEnum: плоская грань детали", "Фильтр интерактивного выбора только плоской грани детали."],
  ["kAssemblyLeafOccurrenceFilter = 16643", "SelectionFilterEnum: конечный экземпляр компонента в сборке", "Фильтр выбора конкретной детали или конечного вхождения внутри сборки."],
  ["kFeatureAppearance = 100610", "AppearanceSourceTypeEnum: внешний вид элемента", "Возвращать грань к внешнему виду, заданному на уровне элемента модели."],
];

const aliasRows = [
  ["PART_DOCUMENT_OBJECT", "Алиас класса для kPartDocumentObject", "Писать Inventor.PART_DOCUMENT_OBJECT вместо числового значения 12290."],
  ["POSITIVE_EXTENT_DIRECTION", "Алиас класса для kPositiveExtentDirection", "Используется как направление по умолчанию для отверстий."],
  ["NEGATIVE_EXTENT_DIRECTION", "Алиас класса для kNegativeExtentDirection", "Используется для обратного направления отверстия или операции."],
  ["HORIZONTAL_DIMENSION", "Алиас класса для kHorizontalDim", "Удобное имя для горизонтальной ориентации размера."],
  ["VERTICAL_DIMENSION", "Алиас класса для kVerticalDim", "Удобное имя для вертикальной ориентации размера."],
  ["ALIGNED_DIMENSION", "Алиас класса для kAlignedDim", "Удобное имя для выровненной ориентации размера."],
  ["PART_FACE_FILTER", "Алиас класса для kPartFaceFilter", "Используется в pick_face, если можно выбрать любую грань."],
  ["PART_FACE_PLANAR_FILTER", "Алиас класса для kPartFacePlanarFilter", "Используется в pick_face по умолчанию для плоской грани."],
  ["ASSEMBLY_LEAF_OCCURRENCE_FILTER", "Алиас класса для kAssemblyLeafOccurrenceFilter", "Используется в pick_part для выбора детали в сборке."],
  ["FEATURE_APPEARANCE", "Алиас класса для kFeatureAppearance", "Используется при сбросе внешнего вида граней к внешнему виду элемента."],
];

const memberInfo = {
  __init__: ["Подключает обертку к уже запущенному Autodesk Inventor.", "Создать объект Inventor() и дальше работать с активным документом через короткие методы."],
  get_application: ["Получает COM-объект Inventor.Application и при необходимости задает видимость окна.", "Используется внутри __init__, если приложение Inventor уже запущено."],
  active_document: ["Возвращает self.app.ActiveDocument.", "Быстро получить текущий открытый документ Inventor."],
  doc: ["Алиас для active_document.", "Короткая запись inv.doc вместо inv.active_document."],
  component_definition: ["Возвращает ComponentDefinition активного документа.", "Доступ к эскизам, телам, фичам и другим данным детали."],
  comp: ["Алиас для component_definition.", "Короткая запись inv.comp для частых обращений к ComponentDefinition."],
  transient_objects: ["Возвращает app.TransientObjects.", "Создавать временные коллекции Inventor, например ObjectCollection."],
  transient_geometry: ["Возвращает app.TransientGeometry.", "Создавать временные точки, векторы и другую геометрию Inventor."],
  select_set: ["Возвращает ActiveDocument.SelectSet.", "Читать текущее выделение в Inventor."],
  update: ["Обновляет активный документ.", "Принудительно пересчитать модель после изменений."],
  mm: ["Переводит миллиметры во внутренние единицы Inventor.", "Передавать координаты и числовые размеры в API без ручного деления на 10."],
  mm_text: ["Готовит размер как выражение Inventor в миллиметрах.", "Передавать 5 как '5 mm', а готовую строку оставить без изменений."],
  hole_direction: ["Преобразует 'positive', '+', 'negative', '-' в константу направления отверстия.", "Позволяет вызывать методы с понятным текстовым направлением."],
  opposite_hole_direction: ["Возвращает противоположное направление отверстия.", "Автоматически сменить positive на negative и наоборот."],
  dimension_orientation: ["Преобразует 'horizontal', 'vertical', 'aligned' в константу ориентации размера.", "Использовать текстовые имена вместо чисел DimensionOrientationEnum."],
  safe_getattr: ["Безопасно читает атрибут COM-объекта и возвращает default при ошибке.", "Проверять разные объекты Inventor без падения скрипта на COM-исключении."],
  object_collection: ["Создает ObjectCollection и добавляет в нее переданные объекты.", "Передать набор точек или тел в методы Inventor, которые ждут COM-коллекцию."],
  unique_faces: ["Убирает повторяющиеся грани из списка.", "Очистить результат выделения, если одна грань пришла несколько раз."],
  is_face_like: ["Проверяет, похож ли объект на грань по Geometry, Edges и Vertices.", "Отфильтровать из выделения только объекты, с которыми можно работать как с гранями."],
  face_from_selection_object: ["Пытается получить грань из выбранного объекта, NativeObject, ContainingFace или SourceObject.", "Нормализовать разные варианты выделения в одну грань."],
  selection_object_label: ["Собирает диагностическую подпись выбранного объекта.", "Печатать понятную отладочную информацию, если объект не распознан как грань."],
  selected_faces: ["Возвращает уникальные грани из текущего SelectSet.", "Обработать сразу все выделенные грани, например для сброса внешнего вида."],
  pick: ["Вызывает интерактивный выбор Inventor CommandManager.Pick.", "Попросить пользователя выбрать объект с нужным SelectionFilterEnum."],
  pick_face: ["Интерактивно выбирает грань, по умолчанию плоскую.", "Получить грань от пользователя без предварительного выделения."],
  pick_part: ["Интерактивно выбирает конечное вхождение компонента в сборке.", "Попросить выбрать конкретную деталь внутри сборки."],
  plane_geometry: ["Возвращает Geometry объекта или Plane, если Geometry недоступен.", "Единообразно получить геометрию плоскости у грани или эскиза."],
  same_plane_entity: ["Проверяет, лежат ли две плоские сущности в одной или параллельной плоскости с допустимым смещением.", "Найти эскиз на той же плоскости, что и выбранная грань."],
  same_plane: ["Проверяет, находятся ли две грани в одной плоскости.", "Группировать выбранные грани по общей плоскости."],
  group_faces_by_plane: ["Разбивает список граней на группы по общей плоскости.", "Обрабатывать выбранные грани пачками по плоскостям."],
  sketch_on_face_plane: ["Ищет существующий эскиз на плоскости выбранной грани.", "Переиспользовать уже созданный эскиз вместо создания нового."],
  unique_feature_name: ["Подбирает свободное имя фичи на основе базового имени.", "Назвать новое отверстие или операцию без конфликта с уже существующими именами."],
  unique_points: ["Убирает повторяющиеся точки эскиза по координатам.", "Не создавать дубли отверстий в одной и той же точке."],
  mark_as_hole_centers: ["Помечает точки эскиза как центры отверстий.", "Подготовить точки для HoleFeatures Inventor."],
  all_surface_bodies: ["Создает коллекцию всех SurfaceBodies из ComponentDefinition.", "Передать все тела в SetAffectedBodies, когда деталь многотельная."],
  set_all_bodies_affected: ["Пытается назначить фичу на все тела компонента.", "Сделать отверстие или операцию применимой ко всем телам многотельной детали."],
  add_holes: ["Создает сверленые отверстия по точкам эскиза.", "Добавить одно или несколько отверстий с диаметром, глубиной и направлением."],
  add_counterbore_holes: ["Создает отверстия с цековкой по точкам эскиза.", "Добавить крепежные отверстия с основным диаметром и цековкой."],
  reset_faces_to_feature_appearance: ["Сбрасывает выбранные грани к внешнему виду элемента.", "Убрать ручную окраску граней и вернуть внешний вид от фичи."],
};

function extractMembers(source) {
  const lines = source.split(/\r?\n/);
  const members = [];
  let decorators = [];

  for (const line of lines) {
    const decorator = line.match(/^    @(property|classmethod|staticmethod)$/);
    if (decorator) {
      decorators.push(decorator[1]);
      continue;
    }

    const method = line.match(/^    def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(/);
    if (!method) continue;

    let kind = "Метод";
    if (decorators.includes("property")) kind = "Свойство";
    else if (decorators.includes("classmethod")) kind = "Метод класса";
    else if (decorators.includes("staticmethod")) kind = "Статический метод";

    members.push({ name: method[1], kind });
    decorators = [];
  }

  return members;
}

function section(title) {
  return [title, "", ""];
}

await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItemAt(1);
const source = await fs.readFile(apiPath, "utf8");
const members = extractMembers(source);

sheet.getRange("A1:C140").clear({ applyTo: "all" });
sheet.showGridLines = false;

const rows = [
  ["inventor_api.py: текущий справочник", "", ""],
  ["Константы, алиасы класса, свойства и методы из текущего файла inventor_api.py.", "", ""],
  ["", "", ""],
  ["Элемент", "Пояснение", "Практическое применение"],
  section("Константы Inventor API"),
  ...constantRows,
  section("Алиасы класса Inventor"),
  ...aliasRows,
  section("Свойства и методы класса Inventor"),
  ...members.map(({ name, kind }) => {
    const [explanation, practical] = memberInfo[name] ?? [
      `${kind} из текущего inventor_api.py.`,
      "Используется в сценариях работы с Autodesk Inventor через Python.",
    ];
    return [name, `${kind}: ${explanation}`, practical];
  }),
];

const range = sheet.getRangeByIndexes(0, 0, rows.length, 3);
range.values = rows;
range.format.font = { name: "Arial", size: 10, color: "#111827" };
range.format.verticalAlignment = "center";
range.format.wrapText = true;

sheet.getRange("A1:C1").format = {
  font: { name: "Arial", size: 14, bold: true, color: "#1F2937" },
};
sheet.getRange("A2:C2").format = {
  font: { name: "Arial", size: 10, italic: true, color: "#4B5563" },
};

const header = sheet.getRange("A4:C4");
header.format = {
  fill: "#374151",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
};
header.format.horizontalAlignment = "center";
header.format.borders = { preset: "all", style: "thin", color: "#FFFFFF" };

for (let rowIndex = 4; rowIndex < rows.length; rowIndex += 1) {
  const excelRow = rowIndex + 1;
  const current = rows[rowIndex];
  const rowRange = sheet.getRange(`A${excelRow}:C${excelRow}`);

  if (current[1] === "" && current[2] === "") {
    rowRange.format = {
      fill: "#E5E7EB",
      font: { name: "Arial", size: 10, bold: true, color: "#111827" },
    };
    rowRange.format.borders = { preset: "outside", style: "thin", color: "#9CA3AF" };
  } else {
    rowRange.format.fill = excelRow % 2 === 0 ? "#FFFFFF" : "#EAF2F8";
    rowRange.format.borders = { preset: "all", style: "thin", color: "#D1D5DB" };
  }
}

sheet.getRange("A:C").format.verticalAlignment = "center";
sheet.getRange("A:A").format.columnWidth = 34;
sheet.getRange("B:B").format.columnWidth = 58;
sheet.getRange("C:C").format.columnWidth = 66;
sheet.getRange(`A1:C${rows.length}`).format.autofitRows();
sheet.freezePanes.freezeRows(4);

workbook.recalculate();

const check = await workbook.inspect({
  kind: "table",
  sheetId: sheet.name,
  range: `A1:C${rows.length}`,
  maxChars: 22000,
  tableMaxRows: rows.length,
  tableMaxCols: 3,
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
  sheetName: sheet.name,
  range: `A1:C${Math.min(rows.length, 75)}`,
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/second_sheet_after.png`, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`SAVED ${outputPath}`);
