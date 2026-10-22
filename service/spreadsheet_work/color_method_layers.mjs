import fs from 'node:fs/promises';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(process.argv.includes('--verify')?'../outputs/method_layers/Удобный слой над API python.xlsx':'../infa/Удобный слой над API python.xlsx'));
const out='../outputs/method_layers';
await fs.mkdir(out,{recursive:true});
console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:2000})).ndjson);
if(process.argv.includes('--verify')) {
 for(const [i,range] of [[0,'B123:G142'],[1,'H5:H7'],[1,'B8:C17']]) {
  const s=wb.worksheets.getItemAt(i);
  const p=await wb.render({sheetName:s.name,range,scale:1.5,format:'png'});
  await fs.writeFile(`${out}/after_${i}_${range.replace(':','_')}.png`,new Uint8Array(await p.arrayBuffer()));
 }
 console.log((await wb.inspect({kind:'table',sheetId:'Лист1',range:'H5:H7',maxChars:1000,tableMaxRows:3,tableMaxCols:1})).ndjson);
} else if(process.argv.includes('--inspect')) {
 console.log(wb.help('range rich text', {search:'richText|runs',maxChars:2500}).ndjson);
 for(let i=0;i<2;i++) {
  const s=wb.worksheets.getItemAt(i);
  const range=i===0?'B123:G142':'B7:C17';
  const p=await wb.render({sheetName:s.name,range,scale:1,format:'png'});
  await fs.writeFile(`${out}/before_${i}.png`,new Uint8Array(await p.arrayBuffer()));
 }
} else {
 const spec=JSON.parse(await fs.readFile('method_layers.json','utf8'));
 for(const item of spec.cells) wb.worksheets.getItem(item.sheet).getRange(item.cell).format.fill=spec.colors[item.category];
 wb.recalculate();
 await (await SpreadsheetFile.exportXlsx(wb)).save(`${out}/styled.xlsx`);
 console.log('Styled cells:',spec.cells.length);
}
