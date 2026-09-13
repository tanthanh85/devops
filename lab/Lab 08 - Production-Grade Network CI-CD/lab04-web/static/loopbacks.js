const rows=document.getElementById("rows"),status=document.getElementById("status");
const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
async function load(){status.textContent="Loading…";rows.innerHTML="";try{const r=await fetch("/api/loopbacks",{cache:"no-store"}),d=await r.json();if(!r.ok)throw new Error(d.error||`HTTP ${r.status}`);rows.innerHTML=d.items.map(x=>`<tr><td>${esc(x.device)}</td><td>${esc(x.interface)}</td><td>${esc(x.addresses.join(", "))}</td><td>${x.enabled?"Yes":"No"}</td></tr>`).join("");status.textContent=`${d.items.length} loopback interface(s) retrieved.`}catch(e){status.textContent=e.message}}
document.getElementById("refresh").onclick=load;load();

