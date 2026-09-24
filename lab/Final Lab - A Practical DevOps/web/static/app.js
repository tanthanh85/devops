const $ = id => document.getElementById(id);
let samples = [];
let refreshTimer = null;
let syntheticRefreshTimer = null;
let syntheticResults = [];
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
  $("monitoring-panel").hidden = name !== "monitoring"; $("inventory-panel").hidden = name !== "inventory"; $("synthetic-panel").hidden = name !== "synthetic";
  if (name === "monitoring") requestAnimationFrame(drawCharts);
  if (name === "synthetic") { loadSynthetic(); requestAnimationFrame(drawSyntheticChart); }
}
document.querySelectorAll(".tab").forEach(tab => tab.onclick = () => selectTab(tab.dataset.tab));

async function boot() {
  try {
    $("setup").hidden = true; $("login").hidden = true; $("application").hidden = true; $("logout").hidden = true;
    const status = await call("/api/setup/status");
    if (status.setup_required) {
      $("setup").hidden = false;
    } else {
      const currentSession = await call("/api/session");
      if (currentSession.authenticated) await loadRouters();
      else $("login").hidden = false;
    }
    await loadInstanceInfo();
  }
  catch (error) { message(error.message); }
}

async function loadInstanceInfo() {
  try {
    const [web, app] = await Promise.all([call("/instance"), call("/api/instance")]);
    $("web-instance").textContent = `Web Pod: ${web.instance}`;
    $("app-instance").textContent = `App Pod: ${app.instance}`;
  } catch (error) {
    $("web-instance").textContent = "Web Pod: unavailable";
    $("app-instance").textContent = "App Pod: unavailable";
  }
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
      $("routers").innerHTML = '<div class="empty-state">No active NetBox devices retrieved.</div>';
      $("router-select").innerHTML = '<option value="">Retrieve inventory from NetBox first</option>';
      $("collect").disabled = true; stopAutoRefresh(); return;
    }
    $("collect").disabled = false;
    data.items.forEach(router => {
      const row = document.createElement("div"); row.className = "router-row";
      row.innerHTML = `<div><strong>${escapeHtml(router.name)}</strong><span>Management: ${escapeHtml(router.host)} · RESTCONF: ${router.port}</span><small>${router.enabled ? "Active in NetBox" : "No longer active in NetBox"}</small></div><div class="router-actions"><button class="view-button" aria-label="View loopbacks for ${escapeHtml(router.name)}">Loopbacks</button></div>`;
      row.querySelector(".view-button").onclick = () => loadLoopbacks(router);
      $("routers").append(row);
      const option = document.createElement("option"); option.value = router.id; option.textContent = `${router.name} — ${router.host}`; $("router-select").append(option);
    });
    if ([...$("router-select").options].some(option => option.value === selectedRouter)) $("router-select").value = selectedRouter;
    startAutoRefresh(samples.length === 0);
  } catch (error) { if (error.message !== "authentication required") message(error.message); }
}

async function loadLoopbacks(router) {
  const panel = $("loopback-panel");
  panel.hidden = false;
  $("loopback-title").textContent = `${router.name} loopback interfaces`;
  $("loopbacks").innerHTML = '<div class="empty-state">Loading loopback interfaces…</div>';
  panel.scrollIntoView({behavior: "smooth", block: "start"});
  try {
    const data = await call(`/api/routers/${router.id}/loopbacks`);
    if (!data.items.length) {
      $("loopbacks").innerHTML = '<div class="empty-state">No loopback interfaces found.</div>';
      return;
    }
    const rows = data.items.map(item => `<tr><td>${escapeHtml(item.name)}</td><td class="status-${escapeHtml(item.admin_status)}">${escapeHtml(item.admin_status)}</td><td class="status-${escapeHtml(item.protocol_status)}">${escapeHtml(item.protocol_status)}</td><td>${escapeHtml(item.ip)}</td><td>${escapeHtml(item.mask)}</td></tr>`).join("");
    $("loopbacks").innerHTML = `<table class="loopback-table"><thead><tr><th>Name</th><th>Admin status</th><th>Protocol status</th><th>IP address</th><th>Mask</th></tr></thead><tbody>${rows}</tbody></table>`;
  } catch (error) {
    $("loopbacks").innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
  }
}

$("close-loopbacks").onclick = () => { $("loopback-panel").hidden = true; };

async function loadSynthetic() {
  try {
    const data = await call("/api/synthetic/config");
    syntheticResults = data.results || [];
    if (data.configured) {
      $("synthetic-form").username.value = data.username;
      $("synthetic-interval").value = String(data.interval_seconds);
      $("synthetic-config-status").textContent = `Active as ${data.username}; checking every ${formatInterval(data.interval_seconds)}.`;
    }
    const result = data.last_result;
    if (result) {
      $("synthetic-last-outcome").textContent = result.outcome === "success" ? "Success" : "Failure";
      $("synthetic-last-outcome").className = result.outcome === "success" ? "result-success" : "result-failure";
      const code = result.status_code == null ? "no HTTP status" : `HTTP ${result.status_code}`;
      $("synthetic-last-detail").textContent = `${code} · ${result.response_time_ms.toFixed(2)} ms · ${new Date(result.timestamp).toLocaleString()}`;
    }
    $("synthetic-chart-empty").hidden = syntheticResults.length > 0;
    drawSyntheticChart();
    if (!syntheticRefreshTimer) syntheticRefreshTimer = setInterval(loadSynthetic, 5000);
  } catch (error) {
    if (error.message !== "administrator access required") message(error.message);
  }
}

function formatInterval(seconds) {
  if (seconds < 60) return `${seconds} seconds`;
  return `${seconds / 60} minute${seconds === 60 ? "" : "s"}`;
}

$("setup-form").onsubmit = async event => { event.preventDefault(); try { await call("/api/setup/admin", {method: "POST", body: JSON.stringify(Object.fromEntries(new FormData(event.target)))}); $("setup").hidden = true; $("login").hidden = false; message("Administrator created. Sign in.", "success"); } catch (error) { message(error.message); } };
$("login-form").onsubmit = async event => { event.preventDefault(); try { await call("/api/session", {method: "POST", body: JSON.stringify(Object.fromEntries(new FormData(event.target)))}); message(); await loadRouters(); } catch (error) { message(error.message); } };
$("netbox-form").onsubmit = async event => {
  event.preventDefault();
  const button = $("sync-netbox");
  button.disabled = true; button.textContent = "Retrieving…";
  try {
    const payload = Object.fromEntries(new FormData(event.target));
    const result = await call("/api/inventory/netbox", {method: "POST", body: JSON.stringify(payload)});
    await loadRouters();
    message(`Retrieved ${result.imported} active device${result.imported === 1 ? "" : "s"} from NetBox.`, "success");
  } catch (error) { message(error.message); }
  finally {
    event.target.netbox_api_token.value = "";
    button.disabled = false; button.textContent = "Retrieve inventory from NetBox";
  }
};
$("synthetic-form").onsubmit = async event => { event.preventDefault(); const data = Object.fromEntries(new FormData(event.target)); data.interval_seconds = Number(data.interval_seconds); try { await call("/api/synthetic/config", {method: "POST", body: JSON.stringify(data)}); event.target.password.value = ""; await loadSynthetic(); message("Synthetic test account and interval saved.", "success"); } catch (error) { message(error.message); } };

async function collectMetrics() {
  const id = $("router-select").value;
  if (!id) return message("Retrieve inventory from NetBox and select a router first.");
  if (collecting) return;
  collecting = true; $("collect").disabled = true; $("collect").textContent = "Collecting…";
  $("connection-status").textContent = "Connecting"; $("connection-status").classList.add("working");
  try {
    const web = await call("/instance");
    const data = await call(`/api/routers/${id}/metrics`); samples.push(data); samples = samples.slice(-30);
    $("web-instance").textContent = `Web Pod: ${web.instance}`;
    $("app-instance").textContent = `App Pod: ${data.app_instance}`;
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
$("logout").onclick = async () => { stopAutoRefresh(); if (syntheticRefreshTimer) clearInterval(syntheticRefreshTimer); await call("/api/session", {method: "DELETE"}); location.reload(); };

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
function drawSyntheticChart() {
  const canvas = $("synthetic-chart");
  if (!canvas || !syntheticResults.length || canvas.parentElement.clientWidth === 0) return;
  const ratio = devicePixelRatio || 1, width = canvas.parentElement.clientWidth, height = 280;
  canvas.width = width * ratio; canvas.height = height * ratio; canvas.style.width = `${width}px`; canvas.style.height = `${height}px`;
  const context = canvas.getContext("2d"); context.scale(ratio, ratio);
  const pad = {left: 62, right: 18, top: 18, bottom: 34}, plotW = width - pad.left - pad.right, plotH = height - pad.top - pad.bottom;
  const maximum = Math.max(100, ...syntheticResults.map(result => Number(result.response_time_ms) || 0));
  context.font = "12px system-ui"; context.fillStyle = "#718096"; context.strokeStyle = "#e4eaf1"; context.lineWidth = 1;
  for (let step = 0; step <= 4; step += 1) { const value = maximum * step / 4, y = pad.top + plotH - step * plotH / 4; context.beginPath(); context.moveTo(pad.left, y); context.lineTo(width - pad.right, y); context.stroke(); context.fillText(`${Math.round(value)} ms`, 3, y + 4); }
  const points = syntheticResults.map((result, index) => ({x: pad.left + (syntheticResults.length < 2 ? plotW / 2 : index * plotW / (syntheticResults.length - 1)), y: pad.top + plotH - (Number(result.response_time_ms) || 0) * plotH / maximum, outcome: result.outcome}));
  context.strokeStyle = "#2563eb"; context.lineWidth = 3; context.beginPath(); points.forEach((point, index) => index ? context.lineTo(point.x, point.y) : context.moveTo(point.x, point.y)); context.stroke();
  points.forEach(point => { context.fillStyle = point.outcome === "success" ? "#10b981" : "#dc2626"; context.beginPath(); context.arc(point.x, point.y, 5, 0, Math.PI * 2); context.fill(); });
}
window.addEventListener("resize", () => { drawCharts(); drawSyntheticChart(); });
boot();
