const $ = id => document.getElementById(id);
let samples = [];
let refreshTimer = null;
let collecting = false;

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
  if (name === "monitoring") requestAnimationFrame(drawCharts);
}
document.querySelectorAll(".tab").forEach(tab => tab.onclick = () => selectTab(tab.dataset.tab));

async function boot() {
  try { const status = await call("/api/setup/status"); $("setup").hidden = !status.setup_required; $("login").hidden = status.setup_required; }
  catch (error) { message(error.message); }
}

function escapeHtml(value) { const node = document.createElement("span"); node.textContent = value ?? ""; return node.innerHTML; }
function stopAutoRefresh() { if (refreshTimer) clearInterval(refreshTimer); refreshTimer = null; }
function startAutoRefresh(collectImmediately = false) {
  stopAutoRefresh();
  if (!$("router-select").value) return;
  refreshTimer = setInterval(collectMetrics, Number($("refresh-interval").value));
  if (collectImmediately) collectMetrics();
}

async function loadRouters() {
  try {
    const selectedRouter = $("router-select").value;
    const data = await call("/api/routers");
    $("application").hidden = false; $("login").hidden = true; $("setup").hidden = true; $("logout").hidden = false;
    $("routers").innerHTML = ""; $("router-select").innerHTML = ""; $("router-count").textContent = data.items.length;
    if (!data.items.length) {
      $("routers").innerHTML = '<div class="empty-state">No routers configured.</div>';
      $("router-select").innerHTML = '<option value="">Add a router in Inventory management</option>';
      $("collect").disabled = true; stopAutoRefresh(); return;
    }
    $("collect").disabled = false;
    data.items.forEach(router => {
      const row = document.createElement("div"); row.className = "router-row";
      row.innerHTML = `<div><strong>${escapeHtml(router.name)}</strong><span>${escapeHtml(router.host)}:${router.port}</span><small>${router.enabled ? "Enabled" : "Disabled"} · ${escapeHtml(router.username)}</small></div><button class="delete-button" aria-label="Delete ${escapeHtml(router.name)}">Delete</button>`;
      row.querySelector("button").onclick = async () => { if (confirm(`Delete ${router.name}?`)) { await call(`/api/routers/${router.id}`, {method: "DELETE"}); await loadRouters(); } };
      $("routers").append(row);
      const option = document.createElement("option"); option.value = router.id; option.textContent = `${router.name} — ${router.host}`; $("router-select").append(option);
    });
    if ([...$("router-select").options].some(option => option.value === selectedRouter)) $("router-select").value = selectedRouter;
    startAutoRefresh(samples.length === 0);
  } catch (error) { if (error.message !== "authentication required") message(error.message); }
}

$("setup-form").onsubmit = async event => { event.preventDefault(); try { await call("/api/setup/admin", {method: "POST", body: JSON.stringify(Object.fromEntries(new FormData(event.target)))}); $("setup").hidden = true; $("login").hidden = false; message("Administrator created. Sign in.", "success"); } catch (error) { message(error.message); } };
$("login-form").onsubmit = async event => { event.preventDefault(); try { await call("/api/session", {method: "POST", body: JSON.stringify(Object.fromEntries(new FormData(event.target)))}); message(); await loadRouters(); } catch (error) { message(error.message); } };
$("router-form").onsubmit = async event => { event.preventDefault(); const data = Object.fromEntries(new FormData(event.target)); data.port = Number(data.port); try { await call("/api/routers", {method: "POST", body: JSON.stringify(data)}); event.target.reset(); event.target.port.value = 443; await loadRouters(); message("Router added.", "success"); } catch (error) { message(error.message); } };

async function collectMetrics() {
  const id = $("router-select").value;
  if (!id) return message("Add and select a router first.");
  if (collecting) return;
  collecting = true; $("collect").disabled = true; $("collect").textContent = "Collecting…";
  $("connection-status").textContent = "Connecting"; $("connection-status").classList.add("working");
  try {
    const data = await call(`/api/routers/${id}/metrics`); samples.push(data); samples = samples.slice(-30);
    $("cpu-value").textContent = `${data.cpu_percent}%`; $("memory-value").textContent = `${data.memory_percent}%`;
    $("time-value").textContent = new Date(data.timestamp).toLocaleTimeString(); $("router-value").textContent = data.router;
    $("cpu-chart-empty").hidden = true; $("memory-chart-empty").hidden = true;
    $("connection-status").textContent = "Auto-refresh active"; drawCharts();
  } catch (error) { $("connection-status").textContent = "Collection failed"; message(error.message); }
  finally { collecting = false; $("connection-status").classList.remove("working"); $("collect").disabled = false; $("collect").textContent = "Collect now"; }
}

$("collect").onclick = collectMetrics;
$("refresh-interval").onchange = () => startAutoRefresh(true);
$("router-select").onchange = () => { samples = []; $("cpu-chart-empty").hidden = false; $("memory-chart-empty").hidden = false; startAutoRefresh(true); };
$("logout").onclick = async () => { stopAutoRefresh(); await call("/api/session", {method: "DELETE"}); location.reload(); };

function drawChart(canvasId, key, color) {
  const canvas = $(canvasId); if (!canvas || !samples.length || canvas.parentElement.clientWidth === 0) return;
  const ratio = devicePixelRatio || 1, width = canvas.parentElement.clientWidth, height = 280;
  canvas.width = width * ratio; canvas.height = height * ratio; canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
  const context = canvas.getContext("2d"); context.scale(ratio, ratio);
  const pad = {left: 44, right: 18, top: 18, bottom: 30}, plotW = width - pad.left - pad.right, plotH = height - pad.top - pad.bottom;
  context.font = "12px system-ui"; context.fillStyle = "#718096"; context.strokeStyle = "#e4eaf1"; context.lineWidth = 1;
  for (let value = 0; value <= 100; value += 25) { const y = pad.top + plotH - value * plotH / 100; context.beginPath(); context.moveTo(pad.left, y); context.lineTo(width - pad.right, y); context.stroke(); context.fillText(`${value}%`, 5, y + 4); }
  const points = samples.map((sample, index) => ({x: pad.left + (samples.length < 2 ? plotW / 2 : index * plotW / (samples.length - 1)), y: pad.top + plotH - Math.max(0, Math.min(100, Number(sample[key]) || 0)) * plotH / 100}));
  context.strokeStyle = color; context.lineWidth = 3; context.lineJoin = "round"; context.lineCap = "round"; context.beginPath();
  points.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y)); context.stroke();
  context.fillStyle = color;
  points.forEach(point => { context.beginPath(); context.arc(point.x, point.y, 5, 0, Math.PI * 2); context.fill(); context.strokeStyle = "#ffffff"; context.lineWidth = 2; context.stroke(); });
}

function drawCharts() { drawChart("cpu-chart", "cpu_percent", "#2563eb"); drawChart("memory-chart", "memory_percent", "#10b981"); }
window.addEventListener("resize", drawCharts);
boot(); loadRouters();
