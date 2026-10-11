import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const input = await FileBlob.load("../infa/Удобный слой над API python.xlsx");
const workbook = await SpreadsheetFile.importXlsx(input);

const sheets = await workbook.inspect({
  kind: "workbook,sheet",
  include: "name,index,range",
  maxChars: 4000,
});
console.log(sheets.ndjson);

const methods = await workbook.inspect({
  kind: "region",
  sheetId: "Методы API",
  range: "A1:B10",
  tableMaxRows: 10,
  tableMaxCols: 2,
  maxChars: 4000,
});
console.log(methods.ndjson);
