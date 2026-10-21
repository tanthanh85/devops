import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";
const deck = await PresentationFile.importPptx(await FileBlob.load(process.argv[2]));
for (const index of [0, 1, deck.slides.items.length - 1]) {
  const png = await deck.slides.items[index].export({ format: "png", scale: 1.5 });
  await fs.writeFile(`qa-slide-${index + 1}.png`, new Uint8Array(await png.arrayBuffer()));
}
