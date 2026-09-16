import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "/Users/thandoan/Desktop/Catalyst 8300 vs 8300 Series Secure.xlsx";
const outputDir = "/Users/thandoan/Documents/Presentations/DevOps/.codex-work/preview";
await fs.mkdir(outputDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const overview = await workbook.inspect({
  kind: "workbook,sheet,table,region,drawing",
  maxChars: 12000,
  tableMaxRows: 30,
  tableMaxCols: 20,
  tableMaxCellChars: 200,
});
console.log(overview.ndjson);
for (const sheet of workbook.worksheets.items) {
  const used = sheet.getUsedRange();
  console.log(`SHEET=${sheet.name} USED=${used?.address ?? "none"}`);
  if (used) {
    const inspection = await workbook.inspect({
      kind: "table",
      sheetId: sheet.name,
      range: used.address,
      include: "values,formulas",
      tableMaxRows: 100,
      tableMaxCols: 30,
      maxChars: 30000,
    });
    console.log(inspection.ndjson);
    const preview = await workbook.render({ sheetName: sheet.name, autoCrop: "all", scale: 1.5, format: "png" });
    await fs.writeFile(`${outputDir}/${sheet.name.replaceAll("/", "_")}.png`, new Uint8Array(await preview.arrayBuffer()));
  }
}
