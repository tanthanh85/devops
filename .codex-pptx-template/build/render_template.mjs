import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const source = "/Users/thandoan/Downloads/BKACAD - Presentation Template.pptx";
const deck = await PresentationFile.importPptx(await FileBlob.load(source));
for (let i = 0; i < deck.slides.items.length; i += 1) {
  const png = await deck.slides.items[i].export({ format: "png", scale: 1.5 });
  await fs.writeFile(`template-slide-${i + 1}.png`, new Uint8Array(await png.arrayBuffer()));
  const layout = await deck.slides.items[i].export({ format: "layout" });
  await fs.writeFile(`template-slide-${i + 1}.layout.json`, await layout.text());
}
