import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
await fs.mkdir("./inspect_sheet2_k", { recursive: true });

const sheets = await workbook.inspect({
  kind: "sheet",
  include: "id,name",
  maxChars: 4000,
});
console.log("SHEETS");
console.log(sheets.ndjson);

const sheet = workbook.worksheets.getItemAt(1);
console.log(`SECOND_SHEET=${sheet.name}`);

const region = await workbook.inspect({
  kind: "table,region",
  sheetId: sheet.name,
  range: "A1:K120",
  maxChars: 30000,
  tableMaxRows: 120,
  tableMaxCols: 11,
  tableMaxCellChars: 220,
});
console.log("REGION_A1_K120");
console.log(region.ndjson);

const preview = await workbook.render({
  sheetName: sheet.name,
  range: "A1:K30",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  "./inspect_sheet2_k/before.png",
  new Uint8Array(await preview.arrayBuffer()),
);
