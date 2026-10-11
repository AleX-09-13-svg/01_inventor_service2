import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const input = await FileBlob.load("../infa/Удобный слой над API python.xlsx");
const workbook = await SpreadsheetFile.importXlsx(input);

const check = await workbook.inspect({
  kind: "table",
  sheetId: "Лист1",
  range: "B1:E26",
  maxChars: 6000,
  tableMaxRows: 26,
  tableMaxCols: 4,
  tableMaxCellChars: 120,
});

console.log(check.ndjson);
