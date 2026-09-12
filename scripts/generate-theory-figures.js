const fs = require('fs');
const path = require('path');
const sharp = require('/Users/thandoan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const { icons } = require('/Users/thandoan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/lucide');

const OUT = path.resolve(__dirname, '../theory/assets/course-figures');
fs.mkdirSync(OUT, { recursive: true });
const C = { navy:'#0b315f', blue:'#0878c9', pale:'#eef6fc', teal:'#11958e', green:'#20a36a', orange:'#f28a22', purple:'#6657c7', red:'#dc4c4c', ink:'#102f55', muted:'#597089', line:'#b9d3e5', white:'#ffffff' };
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
function icon(name, x, y, size, color=C.white) {
  const nodes = icons[name] || icons.CircleHelp;
  const body = nodes.map(([tag,a]) => `<${tag} ${Object.entries(a).map(([k,v])=>`${k}="${v}"`).join(' ')}/>`).join('');
  return `<g transform="translate(${x} ${y}) scale(${size/24})" fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${body}</g>`;
}
function lines(text, x, y, cls='label', anchor='middle', gap=22) {
  return String(text).split('\n').map((t,i)=>`<text x="${x}" y="${y+i*gap}" text-anchor="${anchor}" class="${cls}">${esc(t)}</text>`).join('');
}
function card(item, x, y, w, h) {
  const color=item.color||C.blue, cx=x+w/2;
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="14" fill="${C.pale}" stroke="${color}" stroke-width="1.5"/>
  <circle cx="${cx}" cy="${y+45}" r="27" fill="${color}"/>${icon(item.icon||'Box',cx-15,y+30,30)}
  ${lines(item.title,cx,y+92,'label')}${item.sub?lines(item.sub,cx,y+120,'sub'):''}`;
}
function arrow(x1,y1,x2,y2,color=C.blue) { return `<line x1="${x1}" y1="${y1}" x2="${x2-11}" y2="${y2}" stroke="${color}" stroke-width="3"/><path d="M${x2-12} ${y2-7} L${x2} ${y2} L${x2-12} ${y2+7}Z" fill="${color}"/>`; }
function base(body,h=390){return `<svg xmlns="http://www.w3.org/2000/svg" width="1184" height="${h}" viewBox="0 0 1184 ${h}"><rect width="100%" height="100%" fill="white"/><style>.label{font:700 18px Arial,sans-serif;fill:${C.ink}}.sub{font:400 14px Arial,sans-serif;fill:${C.muted}}.band{font:700 16px Arial,sans-serif;fill:${C.ink}}.small{font:600 14px Arial,sans-serif;fill:${C.ink}}</style>${body}</svg>`;}
function flow(items, note, opts={}) {
  const h=opts.h||390, margin=28, gap=20, y=36, ch=210, w=(1184-2*margin-gap*(items.length-1))/items.length;
  let b=''; items.forEach((it,i)=>{const x=margin+i*(w+gap); b+=card(it,x,y,w,ch); if(i<items.length-1)b+=arrow(x+w,y+ch/2,x+w+gap,y+ch/2);});
  if(note)b+=`<rect x="28" y="${h-90}" width="1128" height="58" rx="9" fill="#dff2ff"/>${lines(note,592,h-54,'band')}`;
  return base(b,h);
}
function split(left,right,note){
  let b=`<line x1="592" y1="30" x2="592" y2="292" stroke="${C.line}" stroke-width="2"/>`;
  [[left,24],[right,616]].forEach(([g,x])=>{b+=`<text x="${x+272}" y="46" text-anchor="middle" class="label">${esc(g.title)}</text>`; g.items.forEach((it,i)=>{const y=72+i*62;b+=`<circle cx="${x+34}" cy="${y+18}" r="18" fill="${it.color||C.blue}"/>${icon(it.icon||'Check',x+23,y+7,22)}${lines(it.text,x+66,y+23,'small','start')}`;});});
  b+=`<rect x="28" y="316" width="1128" height="58" rx="9" fill="#dff2ff"/>${lines(note,592,352,'band')}`; return base(b,400);
}
const defs = {
 'docker-architecture': [['Terminal','Docker CLI','Build and run',C.blue],['PanelsTopLeft','Engine API','Control plane',C.teal],['Hammer','BuildKit','Build images',C.orange],['Boxes','Container runtime','Run workloads',C.purple],['Database','Registry / storage','Persist artifacts',C.green]],
 'docker-image-container-lifecycle': [['Files','Build context','Source + Dockerfile',C.blue],['Layers','Image','Immutable layers',C.orange],['Container','Container','Writable runtime',C.teal],['RotateCcw','Replace','Recreate safely',C.green]],
 'container-network-planes': [['AppWindow','Application','Service traffic',C.blue],['Network','Container network','Internal routing',C.teal],['ShieldCheck','Controlled egress','Policy boundary',C.purple],['Router','Management network','Approved targets',C.orange]],
 'container-runtime-boundary': [['Package','Image','Code + dependencies',C.blue],['SlidersHorizontal','Runtime config','Environment',C.teal],['KeyRound','Secrets','Injected securely',C.purple],['Database','Persistent state','External volume',C.orange]],
 'image-evidence-lineage': [['GitCommit','Commit','Source identity',C.blue],['PackageCheck','Image digest','Built artifact',C.orange],['ShieldCheck','Attestation','Tests + scan',C.purple],['Rocket','Deployment','Exact digest',C.teal],['FileCheck2','Evidence','Observed result',C.green]],
 'secure-image-supply-chain': [['FileCode2','Source','Reviewed change',C.blue],['Hammer','Build','Pinned inputs',C.orange],['ScanSearch','Scan','Known risks',C.red],['BadgeCheck','Sign','Provenance',C.purple],['PackageCheck','Registry','Trusted image',C.green]],
 'compose-automation-services': [['Laptop','Client','Request',C.blue],['ServerCog','API','Validate job',C.teal],['ListTodo','Queue','Buffer work',C.orange],['Cog','Worker','Execute safely',C.purple],['Router','Targets','Network / API',C.green]],
 'network-job-trust-sequence': [['FileCheck2','Approved job','Validated intent',C.blue],['ListTodo','Queue','Job reference',C.orange],['ShieldCheck','Protected worker','Restricted identity',C.purple],['KeyRound','Secret service','Short-lived access',C.teal],['Router','Target','Execute + verify',C.green]],
 'service-readiness-chain': [['HeartPulse','API ready','Accept requests',C.blue],['DatabaseZap','Queue ready','Store jobs',C.orange],['Cog','Worker ready','Consume safely',C.purple],['Router','Target reachable','Authorized path',C.teal],['BadgeCheck','Service ready','End-to-end proof',C.green]],
 'artifact-vs-cache': 'split',
 'runner-trust-model': [['GitMerge','Merge request','Untrusted input',C.blue],['TestTube2','General runner','Lint + test',C.teal],['PackageCheck','Artifact','Digest + evidence',C.orange],['ShieldCheck','Protected runner','Restricted identity',C.purple],['Rocket','Environment','Deploy + verify',C.green]],
 'three-network-states': [['FileJson','Intended state','What should exist',C.orange],['Settings','Configured state','What was applied',C.blue],['Activity','Operational state','What is happening',C.green]],
 'network-change-state': [['ClipboardCheck','Approved','Ready to change',C.blue],['Settings','Applying','Scoped execution',C.orange],['SearchCheck','Verifying','Compare outcomes',C.purple],['BadgeCheck','Validated','Service works',C.green]],
 'rollback-decision': [['TriangleAlert','Failure detected','Preserve evidence',C.red],['Search','Assess cause','Known and reversible?',C.orange],['Undo2','Rollback','Restore baseline',C.purple],['Wrench','Remediate','Forward fix',C.blue],['BadgeCheck','Revalidate','Confirm service',C.green]],
 'iac-tool-ownership': [['CloudCog','Provision','Terraform',C.purple],['Settings','Configure','Ansible',C.blue],['Code2','Integrate','Python',C.teal],['TestTube2','Validate','Test framework',C.orange]],
 'drift-reconciliation': [['ScanSearch','Collect','Actual state',C.blue],['GitCompare','Compare','Intent vs actual',C.orange],['Tags','Classify','Expected or drift',C.purple],['UserCheck','Assign owner','Resolve cause',C.teal],['RefreshCw','Reconcile','Controlled change',C.green]],
 'test-environment-lifecycle': [['PlusSquare','Create','Isolated environment',C.blue],['FileCheck2','Plan','Review changes',C.orange],['TestTube2','Test','Exercise behavior',C.purple],['Archive','Evidence','Retain results',C.teal],['Trash2','Destroy','Remove resources',C.green]],
 'monitoring-observability-telemetry': [['Radio','Telemetry','Emit signals',C.blue],['ChartNoAxesCombined','Monitoring','Known conditions',C.teal],['Search','Observability','Explain behavior',C.purple],['BellRing','Action','Respond + learn',C.orange]],
 'observability-architecture': [['Router','Network signals','State + traffic',C.blue],['AppWindow','Application signals','Logs + traces',C.teal],['GitCommit','Delivery signals','Change metadata',C.orange],['Waypoints','Correlation','Shared context',C.purple],['ChartNoAxesCombined','Operational view','Decision support',C.green]],
 'netdevops-trust-boundaries': [['GitBranch','Source zone','Code + policy',C.blue],['TestTube2','Validation zone','No target access',C.teal],['PackageCheck','Artifact boundary','Digest + evidence',C.orange],['ShieldCheck','Execution zone','Restricted identity',C.purple],['ScrollText','Audit zone','Independent record',C.green]],
 'kubernetes-automation-platform': [['Users','Clients','Submit jobs',C.blue],['ServerCog','API service','Validate requests',C.teal],['ListTodo','Queue','Decouple work',C.orange],['Boxes','Worker pods','Execute jobs',C.purple],['Router','Targets','Restricted path',C.green]],
 'kubernetes-suitability': 'split2',
 'automation-platform-options': 'split3',
 'kubernetes-worker-device-security': [['ListChecks','Validated job','Approved scope',C.blue],['BadgeCheck','Service account','Workload identity',C.teal],['Box','Isolated pod','Runtime boundary',C.purple],['ShieldCheck','Network policy','Explicit egress',C.orange],['Router','Authorized targets','Least privilege',C.green]],
 'platform-vs-network-pipeline': 'split4'
};
function render(name,def){
  if(def==='split') return split({title:'Pipeline artifact',items:[{text:'Authoritative output',icon:'PackageCheck',color:C.green},{text:'Passed between stages',icon:'ArrowRightLeft',color:C.blue},{text:'Retained as evidence',icon:'Archive',color:C.purple}]},{title:'Pipeline cache',items:[{text:'Disposable acceleration',icon:'Gauge',color:C.orange},{text:'May be stale or absent',icon:'RefreshCw',color:C.red},{text:'Never a release record',icon:'CircleX',color:C.red}]},'Promote artifacts. Rebuild caches.');
  if(def==='split2') return split({title:'Kubernetes is justified when',items:[{text:'Multiple services must scale',icon:'Boxes',color:C.blue},{text:'Self-healing is required',icon:'HeartPulse',color:C.green},{text:'A platform team operates it',icon:'Users',color:C.teal}]},{title:'Use a simpler platform when',items:[{text:'One protected job runner is enough',icon:'ShieldCheck',color:C.purple},{text:'Compose meets service needs',icon:'Container',color:C.orange},{text:'Cluster cost exceeds value',icon:'Scale',color:C.red}]},'Choose the smallest platform that meets the operating requirement.');
  if(def==='split3') return split({title:'Smaller operating model',items:[{text:'Protected runner — scheduled jobs',icon:'ShieldCheck',color:C.purple},{text:'Docker Compose — several services',icon:'Container',color:C.orange},{text:'Lower platform overhead',icon:'Gauge',color:C.green}]},{title:'Kubernetes operating model',items:[{text:'Many services and workers',icon:'Boxes',color:C.blue},{text:'Scaling and self-healing',icon:'RefreshCw',color:C.teal},{text:'Dedicated platform capability',icon:'Users',color:C.purple}]},'Architecture follows workload and operational maturity—not fashion.');
  if(def==='split4') return split({title:'Platform delivery pipeline',items:[{text:'Build and scan application image',icon:'PackageCheck',color:C.orange},{text:'Deploy platform components',icon:'Boxes',color:C.blue},{text:'Verify platform health',icon:'HeartPulse',color:C.green}]},{title:'Network job pipeline',items:[{text:'Validate intent and policy',icon:'FileCheck2',color:C.teal},{text:'Run through protected worker',icon:'ShieldCheck',color:C.purple},{text:'Verify network outcome',icon:'Router',color:C.green}]},'A healthy platform does not prove that a network change is correct.');
  const items=def.map(([icon,title,sub,color])=>({icon,title,sub,color})); return flow(items, name.includes('docker')?'Build once. Run the same identified artifact in every environment.':'Each boundary has one clear responsibility.');
}
(async()=>{for(const [name,def] of Object.entries(defs)){const svg=render(name,def);fs.writeFileSync(path.join(OUT,`${name}.svg`),svg);await sharp(Buffer.from(svg)).png().toFile(path.join(OUT,`${name}.png`));} console.log(`Generated ${Object.keys(defs).length} figures in ${OUT}`);})();
