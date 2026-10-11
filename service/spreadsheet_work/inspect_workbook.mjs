import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const sheets = await workbook.inspect({
  kind: "sheet",
  include: "id,name",
  maxChars: 8000,
});
console.log("SHEETS");
console.log(sheets.ndjson);

const summary = await workbook.inspect({
  kind: "workbook,sheet,table",
  maxChars: 12000,
  tableMaxRows: 8,
  tableMaxCols: 12,
  tableMaxCellChars: 120,
});
console.log("SUMMARY");
console.log(summary.ndjson);

const fifth = workbook.worksheets.getItemAt(4);
console.log("FIFTH_SHEET", fifth.name);
const used = fifth.getUsedRange();
console.log("USED_VALUES");
console.log(JSON.stringify(used.values, null, 2));
