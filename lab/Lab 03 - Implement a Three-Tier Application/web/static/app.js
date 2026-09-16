const $ = id => document.getElementById(id);
let samples = [];

async function call(url, options = {}) {
  const response = await fetch(url, {headers: {"Content-Type": "application/json"}, ...options});
  const data = response.status === 204 ? {} : await response.json();
  if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
  return data;
}

function message(text = "", type = "error") {
  const box = $("message"); box.textContent = text; box.className = `toast ${type}`; box.hidden = !text;
  if (text) setTimeout(() => { box.hidden = true; }, 5000);
}

function selectTab(name) {
  document.querySelectorAll(".tab").forEach(tab => tab.classList.toggle("active", tab.dataset.tab === name));
  $("monitoring-panel").hidden = name !== "monitoring"; $("inventory-panel").hidden = name !== "inventory";
  if (name === "monitoring") requestAnimationFrame(draw);
}
document.querySelectorAll(".tab").forEach(tab => tab.onclick = () => selectTab(tab.dataset.tab));

async function boot() {
  try { const status = await call("/api/setup/status"); $("setup").hidden = !status.setup_required; $("login").hidden = status.setup_required; }
  catch (error) { message(error.message); }
}

function escapeHtml(value) { const node = document.createElement("span"); node.textContent = value ?? ""; return node.innerHTML; }

async function loadRouters() {
  try {
    const data = await call("/api/routers");
    $("application").hidden = false; $("login").hidden = true; $("setup").hidden = true; $("logout").hidden = false;
    $("routers").innerHTML = ""; $("router-select").innerHTML = ""; $("router-count").textContent = data.items.length;
    if (!data.items.length) {
      $("routers").innerHTML = '<div class="empty-state">No routers configured.</div>';
      $("router-select").innerHTML = '<option value="">Add a router in Inventory management</option>';
      $("collect").disabled = true; return;
    }
    $("collect").disabled = false;
    data.items.forEach(router => {
      const row = document.createElement("div"); row.className = "router-row";
      row.innerHTML = `<div><strong>${escapeHtml(router.name)}</strong><span>${escapeHtml(router.host)}:${router.port}</span><small>${router.enabled ? "Enabled" : "Disabled"} · ${escapeHtml(router.username)}</small></div><button class="delete-button" aria-label="Delete ${escapeHtml(router.name)}">Delete</button>`;
      row.querySelector("button").onclick = async () => { if (confirm(`Delete ${router.name}?`)) { await call(`/api/routers/${router.id}`, {method: "DELETE"}); await loadRouters(); } };
      $("routers").append(row);
      const option = document.createElement("option"); option.value = router.id; option.textContent = `${router.name} — ${router.host}`; $("router-select").append(option);
    });
  } catch (error) { if (error.message !== "authentication required") message(error.message); }
}

$("setup-form").onsubmit = async event => { event.preventDefault(); try { await call("/api/setup/admin", {method: "POST", body: JSON.stringify(Object.fromEntries(new FormData(event.target)))}); $("setup").hidden = true; $("login").hidden = false; message("Administrator created. Sign in.", "success"); } catch (error) { message(error.message); } };
$("login-form").onsubmit = async event => { event.preventDefault(); try { await call("/api/session", {method: "POST", body: JSON.stringify(Object.fromEntries(new FormData(event.target)))}); message(); await loadRouters(); } catch (error) { message(error.message); } };
$("router-form").onsubmit = async event => { event.preventDefault(); const data = Object.fromEntries(new FormData(event.target)); data.port = Number(data.port); try { await call("/api/routers", {method: "POST", body: JSON.stringify(data)}); event.target.reset(); event.target.port.value = 443; await loadRouters(); message("Router added.", "success"); } catch (error) { message(error.message); } };

$("collect").onclick = async () => {
  const id = $("router-select").value; if (!id) return message("Add and select a router first.");
  $("collect").disabled = true; $("collect").textContent = "Collecting…"; $("connection-status").textContent = "Connecting"; $("connection-status").classList.add("working");
  try {
    const data = await call(`/api/routers/${id}/metrics`); samples.push(data); samples = samples.slice(-30);
    $("cpu-value").textContent = `${data.cpu_percent}%`; $("memory-value").textContent = `${data.memory_percent}%`;
    $("time-value").textContent = new Date(data.timestamp).toLocaleTimeString(); $("router-value").textContent = data.router;
    $("chart-empty").hidden = true; $("connection-status").textContent = "Connected"; draw(); message("Metrics collected.", "success");
  } catch (error) { $("connection-status").textContent = "Collection failed"; message(error.message); }
  finally { $("connection-status").classList.remove("working"); $("collect").disabled = false; $("collect").textContent = "Collect now"; }
};

$("logout").onclick = async () => { await call("/api/session", {method: "DELETE"}); location.reload(); };

function draw() {
  const canvas = $("chart"); if (!canvas || !samples.length || canvas.parentElement.clientWidth === 0) return;
  const ratio = devicePixelRatio || 1, width = canvas.parentElement.clientWidth, height = 280;
  canvas.width = width * ratio; canvas.height = height * ratio; canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
  const context = canvas.getContext("2d"); context.scale(ratio, ratio); context.clearRect(0, 0, width, height);
  const pad = {left: 44, right: 18, top: 18, bottom: 30}, plotW = width - pad.left - pad.right, plotH = height - pad.top - pad.bottom;
  context.font = "12px system-ui"; context.fillStyle = "#718096"; context.strokeStyle = "#e4eaf1"; context.lineWidth = 1;
  for (let value = 0; value <= 100; value += 25) { const y = pad.top + plotH - value * plotH / 100; context.beginPath(); context.moveTo(pad.left, y); context.lineTo(width - pad.right, y); context.stroke(); context.fillText(`${value}%`, 5, y + 4); }
  [["cpu_percent", "#2563eb"], ["memory_percent", "#10b981"]].forEach(([key, color]) => { context.strokeStyle = color; context.lineWidth = 3; context.lineJoin = "round"; context.beginPath(); samples.forEach((sample, index) => { const x = pad.left + (samples.length < 2 ? plotW : index * plotW / (samples.length - 1)); const y = pad.top + plotH - Math.max(0, Math.min(100, sample[key])) * plotH / 100; index ? context.lineTo(x, y) : context.moveTo(x, y); }); context.stroke(); });
}

window.addEventListener("resize", draw);
boot(); loadRouters();
