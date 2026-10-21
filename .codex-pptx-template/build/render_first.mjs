import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";
const deck = await PresentationFile.importPptx(await FileBlob.load(process.argv[2]));
const png = await deck.slides.items[0].export({ format: "png", scale: 1.5 });
await fs.writeFile("source-first.png", new Uint8Array(await png.arrayBuffer()));
const layout = await deck.slides.items[0].export({ format: "layout" });
await fs.writeFile("source-first.layout.json", await layout.text());
