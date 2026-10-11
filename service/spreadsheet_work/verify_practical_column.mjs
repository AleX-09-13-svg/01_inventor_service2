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
  range: "A4:C12",
  tableMaxRows: 12,
  tableMaxCols: 3,
  maxChars: 6000,
});
console.log(methods.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  maxChars: 12000,
});
console.error(errors.ndjson);
