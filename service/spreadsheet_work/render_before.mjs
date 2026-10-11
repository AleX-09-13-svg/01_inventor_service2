import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "../infa/Удобный слой над API python.xlsx";
const outputDir = "../outputs/part_methods_explanations";
await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const preview = await workbook.render({
  sheetName: "Методы Part",
  range: "A1:J16",
  scale: 1,
  format: "png",
});
await fs.writeFile(`${outputDir}/before.png`, new Uint8Array(await preview.arrayBuffer()));
console.log(`${outputDir}/before.png`);
