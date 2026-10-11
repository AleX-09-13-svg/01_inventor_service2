import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const outputDir = "./inspect_current";

await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const sheets = await workbook.inspect({
  kind: "sheet",
  include: "id,name",
  maxChars: 4000,
});
console.log("SHEETS");
console.log(sheets.ndjson);

const secondSheet = workbook.worksheets.getItemAt(1);
console.log(`SECOND_SHEET=${secondSheet.name}`);

const region = await workbook.inspect({
  kind: "region,table",
  sheetId: secondSheet.name,
  range: "A1:H80",
  maxChars: 20000,
  tableMaxRows: 80,
  tableMaxCols: 8,
  tableMaxCellChars: 180,
});
console.log("SECOND_SHEET_REGION");
console.log(region.ndjson);

const preview = await workbook.render({
  sheetName: secondSheet.name,
  autoCrop: "all",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  `${outputDir}/second_sheet_before.png`,
  new Uint8Array(await preview.arrayBuffer()),
);
