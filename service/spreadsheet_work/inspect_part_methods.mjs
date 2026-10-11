import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const sheet = workbook.worksheets.getItem("Методы Part");

const used = sheet.getUsedRange();
console.log(JSON.stringify(used.values, null, 2));

const style = await workbook.inspect({
  kind: "computedStyle",
  sheetId: sheet.name,
  range: "A1:J16",
  maxChars: 6000,
});
console.log(style.ndjson);
