const $=id=>document.getElementById(id);let samples=[];
async function call(url,options={}){const r=await fetch(url,{cache:"no-store",headers:{"Content-Type":"application/json"},...options});const d=r.status===204?{}:await r.json();if(!r.ok)throw new Error(d.error||`HTTP ${r.status}`);return d}
function message(t=""){$("message").textContent=t}
async function identity(){try{const d=await call("/instance");$("instance").querySelector("span").textContent=`${d.container_name} · ${d.ip_address}`}catch(e){$("instance").querySelector("span").textContent="Identity unavailable"}}
async function boot(){await identity();try{const s=await call("/api/setup/status");$("setup").hidden=!s.setup_required;$("login").hidden=s.setup_required}catch(e){message(e.message)}}
async function routers(){try{const d=await call("/api/routers");$("application").hidden=false;$("login").hidden=true;$("setup").hidden=true;$("routers").innerHTML="";$("router-select").innerHTML="";d.items.forEach(r=>{const li=document.createElement("li");li.textContent=`${r.name} — ${r.host}:${r.port} — Vault`;$("routers").append(li);const o=document.createElement("option");o.value=r.name;o.textContent=r.name;$("router-select").append(o)})}catch(e){if(e.message!=="authentication required")message(e.message)}}
$("setup-form").onsubmit=async e=>{e.preventDefault();try{await call("/api/setup/admin",{method:"POST",body:JSON.stringify(Object.fromEntries(new FormData(e.target)))});$("setup").hidden=true;$("login").hidden=false}catch(x){message(x.message)}};
$("login-form").onsubmit=async e=>{e.preventDefault();try{await call("/api/session",{method:"POST",body:JSON.stringify(Object.fromEntries(new FormData(e.target)))});await routers()}catch(x){message(x.message)}};
$("refresh-routers").onclick=routers;
$("collect").onclick=async()=>{try{const d=await call(`/api/routers/${$("router-select").value}/metrics`);samples.push(d);samples=samples.slice(-30);$("values").textContent=`CPU ${d.cpu_percent}% · Memory ${d.memory_percent}%`;draw()}catch(x){message(x.message)}};
$("logout").onclick=async()=>{await call("/api/session",{method:"DELETE"});location.reload()};
function draw(){const c=$("chart"),x=c.getContext("2d"),w=c.width=c.clientWidth*devicePixelRatio,h=c.height=180*devicePixelRatio;x.clearRect(0,0,w,h);[["cpu_percent","#0878bd"],["memory_percent","#18a47a"]].forEach(([k,color])=>{x.strokeStyle=color;x.lineWidth=3*devicePixelRatio;x.beginPath();samples.forEach((s,i)=>{const px=samples.length<2?0:i*w/(samples.length-1),py=h-s[k]*h/100;i?x.lineTo(px,py):x.moveTo(px,py)});x.stroke()})}
boot();routers();
