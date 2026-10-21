import { FileBlob, PresentationFile } from "@oai/artifact-tool";
const deck = await PresentationFile.importPptx(await FileBlob.load(process.argv[2]));
const snapshot = await deck.inspect({
  kind: "slide,textbox,shape,image,table,chart,layout",
  include: "id,slide,name,bbox,textPreview,title,isPlaceholder",
  maxChars: 30000,
});
console.log(snapshot.ndjson);
