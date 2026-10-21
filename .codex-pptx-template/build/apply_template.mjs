import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "/Users/thandoan/Documents/Presentations/DevOps";
const skillDir = "/Users/thandoan/.codex/plugins/cache/openai-primary-runtime/presentations/26.909.12148/skills/presentations";
const pythonExecutable = "/Users/thandoan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
const sourceDir = path.join(workspaceDir, "presentations");
const stagingRoot = path.join(workspaceDir, ".codex-pptx-template", "staging");
const outputDir = path.join(workspaceDir, "presentations", "BKACAD-template");
const templatePath = "/Users/thandoan/Downloads/BKACAD - Presentation Template.pptx";
const templateFooterPath = path.join(workspaceDir, ".codex-pptx-template", "build", "template-footer.png");
const templateHeaderPath = path.join(workspaceDir, ".codex-pptx-template", "build", "template-header-motif.png");
const templateFooterBytes = new Uint8Array(await fs.readFile(templateFooterPath));
const templateHeaderBytes = new Uint8Array(await fs.readFile(templateHeaderPath));
const { finalizePresentation } = await import(pathToFileURL(
  path.join(skillDir, "container_tools", "artifact_tool_utils.mjs"),
).href);

await fs.mkdir(stagingRoot, { recursive: true });
await fs.mkdir(outputDir, { recursive: true });

const requested = process.argv.slice(2);
const allFiles = (await fs.readdir(sourceDir))
  .filter((name) => name.toLowerCase().endsWith(".pptx"))
  .filter((name) => !name.startsWith("~$"))
  .sort();
const files = requested.length ? allFiles.filter((name) => requested.includes(name)) : allFiles;

for (const name of files) {
  const sourcePath = path.join(sourceDir, name);
  const deck = await PresentationFile.importPptx(await FileBlob.load(sourcePath));
  const originalSlideCount = deck.slides.items.length;

  for (const slide of deck.slides.items) {
    for (const shape of slide.shapes.items) {
      const frame = shape.frame;
      if (!frame) continue;
      const isTopBar = frame.top <= 1 && frame.height <= 40 && frame.width >= 500;
      if (isTopBar) {
        shape.fill = "#116F8E";
        shape.line = { fill: "none", width: 0 };
      }
    }

    slide.images.add({
      blob: templateHeaderBytes,
      contentType: "image/png",
      alt: "BKACAD template header motif",
      fit: "contain",
      position: { left: 1105, top: 0, width: 175, height: 34 },
    });

    slide.images.add({
      blob: templateFooterBytes,
      contentType: "image/png",
      alt: "BKACAD template footer",
      fit: "contain",
      position: { left: 0, top: 667, width: 1280, height: 53 },
    });
  }

  const stem = path.basename(name, ".pptx");
  const stagingDir = path.join(stagingRoot, stem);
  await fs.mkdir(stagingDir, { recursive: true });
  const candidatePath = path.join(stagingDir, "candidate.pptx");
  const finalPath = path.join(outputDir, `${stem}-BKACAD.pptx`);
  const receiptPath = path.join(stagingDir, "validation.json");
  await fs.rm(finalPath, { force: true });
  await fs.rm(receiptPath, { force: true });
  await (await PresentationFile.exportPptx(deck)).save(candidatePath);

  await finalizePresentation({
    workspaceDir,
    candidatePath,
    finalPath,
    pythonExecutable,
    integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
    layoutArgs: [
      "--expected-slide-size-emu", "12192000,6858000",
      "--validate-bullet-geometry",
      "--validate-heading-fit",
    ],
    explicitTotalSlideCount: originalSlideCount,
    requiredNativeTableOwnerSlides: [],
    requiredNativeChartOwnerSlides: [],
    sourceTemplatePath: templatePath,
    verifyArtifactToolImport: true,
    receiptPath,
  });

  const finalDeck = await PresentationFile.importPptx(await FileBlob.load(finalPath));
  const montage = await finalDeck.export({ format: "png", montage: true, scale: 0.35 });
  await fs.writeFile(path.join(stagingDir, "montage.png"), new Uint8Array(await montage.arrayBuffer()));
  console.log(JSON.stringify({ source: sourcePath, output: finalPath, slides: originalSlideCount }));
}
