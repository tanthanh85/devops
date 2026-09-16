import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "/Users/thandoan/Desktop/Catalyst 8300 vs 8300 Series Secure.xlsx";
const outputDir = "/Users/thandoan/Documents/Presentations/DevOps/outputs/voice_gateway_router_comparison";
const outputPath = `${outputDir}/Catalyst 8300 vs 8300 Series Secure - completed.xlsx`;

const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const sheet = workbook.worksheets.getItem("Catalyst 8300 vs  8300 Series");

const comparison = [
  ["Primary voice-gateway fit", "Strong fit for a smaller modular voice gateway", "Strong fit when more voice/WAN modules are required", "Strong fit when more voice/WAN modules are required", "CUBE/SRST capable from IOS XE 17.18.2; confirm release and autonomous-mode design"],
  ["Integrated data interfaces", "4 × 1G RJ-45 + 2 × 10G SFP/SFP+", "4 × 1G RJ-45 + 2 × 1G SFP", "4T2X: 4 × 1G RJ-45 + 2 × 10G SFP/SFP+; 6T: 4 × 1G RJ-45 + 2 × 1G SFP", "4 × 2.5G RJ-45 + 2 × 10G SFP/SFP+"],
  ["Native NIM slots", 1, 2, 2, "1 native; optional 2-NIM carrier can use the SM slot (up to 3 total)"],
  ["Service-module (SM) slots", 1, 2, 2, 1],
  ["CUBE / SIP border element", "Supported from IOS XE 17.3.2", "Supported from IOS XE 17.3.2", "Supported from IOS XE 17.3.2", "Supported from IOS XE 17.18.2 with vDSP; autonomous mode"],
  ["SRST / local call survivability", "Supported; size to IOS XE release, license and endpoint count", "Supported; more module headroom", "Supported; more module headroom", "Supported from IOS XE 17.18.2; validate autonomous-mode feature limits"],
  ["DSP / media resources", "Physical PVDM/NIM/SM options; validate codec and session sizing", "Physical PVDM/NIM/SM options; more expansion capacity", "Physical PVDM/NIM/SM options; more expansion capacity", "Software-based vDSP for CUBE media services; no traditional PVDM required for vDSP"],
  ["Analog / TDM voice connectivity", "Voice NIM/SM options supported; one NIM slot limits combinations", "Voice NIM/SM options supported; best expansion flexibility", "Voice NIM/SM options supported; best expansion flexibility", "Do not assume legacy voice-module parity; verify each analog/TDM module PID and IOS XE release"],
  ["Voice security", "SIP-TLS and SRTP through IOS XE/CUBE; certificate and license dependent", "SIP-TLS and SRTP through IOS XE/CUBE; certificate and license dependent", "SIP-TLS and SRTP through IOS XE/CUBE; certificate and license dependent", "SIP-TLS and SRTP through IOS XE/CUBE; confirm 17.18.2+ feature support"],
  ["IPsec acceleration", "Hardware-accelerated IPsec", "Hardware-accelerated IPsec", "Hardware-accelerated IPsec", "Hardware-accelerated IPsec with higher secure-edge capacity"],
  ["Published IPsec performance", "Published figures vary by packet profile/release; commonly up to 5 Gbps IMIX—validate license", "Published figures vary by packet profile/release; commonly up to 5 Gbps IMIX—validate license", "Published figures vary by packet profile/release; commonly up to 5 Gbps IMIX—validate license", "Up to 20 Gbps IPsec at 512-byte packets; not directly comparable with IMIX figures"],
  ["Voice + IPsec design note", "Good when one NIM plus one SM covers voice interfaces and DSP needs", "Preferred when concurrent IPsec, DSP and several voice/WAN modules are needed", "Preferred when concurrent IPsec, DSP and several voice/WAN modules are needed", "Highest IPsec headroom, but requires newer IOS XE and careful validation of voice/module compatibility"],
  ["Recommended use", "Choose for a compact CUBE/SRST gateway with modest analog/TDM expansion", "Choose for the most flexible traditional voice-gateway build", "Choose 4T2X for 10G uplinks; choose 6T for 1G-only handoffs", "Choose for high IPsec demand and IP voice; avoid as a drop-in legacy TDM replacement without validation"],
];

sheet.getRange("C5:G17").values = comparison;
sheet.getRange("C5:G17").format.wrapText = true;
sheet.getRange("C5:G17").format.verticalAlignment = "center";
sheet.getRange("C5:C17").format.font = { bold: true };
sheet.getRange("C5:C17").format.fill = "#EAF2F8";
sheet.getRange("C5:G17").format.font = { name: "Arial", size: 10 };
sheet.getRange("C5:C17").format.font = { name: "Arial", size: 10, bold: true };
sheet.getRange("C5:G17").format.rowHeight = 45;
sheet.getRange("C5:C17").format.columnWidth = 27;
sheet.getRange("D5:G17").format.columnWidth = 38;
sheet.getRange("D7:G8").format.horizontalAlignment = "center";
sheet.getRange("D7:G8").format.numberFormat = "0";
sheet.freezePanes.freezeRows(4);
sheet.freezePanes.freezeColumns(3);

workbook.recalculate();

const check = await workbook.inspect({
  kind: "table",
  sheetId: sheet.name,
  range: "C3:G17",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 8,
  maxChars: 25000,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

await fs.mkdir(outputDir, { recursive: true });
const preview = await workbook.render({ sheetName: sheet.name, range: "C3:G17", scale: 1.5, format: "png" });
await fs.writeFile(`${outputDir}/comparison-preview.png`, new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`OUTPUT=${outputPath}`);
