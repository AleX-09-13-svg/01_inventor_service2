import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const outputPath = "../outputs/methods_sheet/Удобный слой над API python.xlsx";
const input = await FileBlob.load(outputPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const sheets = await workbook.inspect({
  kind: "workbook,sheet",
  include: "name,index,range",
  maxChars: 4000,
});
console.log(sheets.ndjson);

const methods = await workbook.inspect({
  kind: "table,region",
  sheetId: "Методы API",
  range: "A1:B60",
  tableMaxRows: 60,
  tableMaxCols: 2,
  maxChars: 20000,
});
console.log(methods.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  maxChars: 12000,
});
console.error(errors.ndjson);

const preview = await workbook.render({
  sheetName: "Методы API",
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  "../outputs/methods_sheet/methods_sheet_saved_preview.png",
  new Uint8Array(await preview.arrayBuffer()),
);
