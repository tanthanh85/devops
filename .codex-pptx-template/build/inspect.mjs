import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const inputs = process.argv.slice(2);
for (const input of inputs) {
  const deck = await PresentationFile.importPptx(await FileBlob.load(input));
  const info = {
    file: input,
    slideCount: deck.slides.items.length,
    masterCount: deck.masters.items.length,
    layoutCount: deck.layouts.items.length,
    masters: deck.masters.items.map((m) => ({ id: m.id, name: m.name })),
    layouts: deck.layouts.items.map((l) => ({
      id: l.id,
      name: l.name,
      placeholders: l.placeholders?.summary?.() ?? null,
    })),
  };
  console.log(JSON.stringify(info));
  const montage = await deck.export({ format: "png", montage: true, scale: 0.35 });
  const out = path.join(process.cwd(), `${path.basename(input, ".pptx")}-montage.png`);
  await fs.writeFile(out, new Uint8Array(await montage.arrayBuffer()));
  console.log(JSON.stringify({ montage: out }));
}
