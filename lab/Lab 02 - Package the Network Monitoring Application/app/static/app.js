const history = { cpu: [], memory: [] };

function draw(id, points, color) {
  const canvas = document.getElementById(id);
  const ctx = canvas.getContext("2d");
  const width = canvas.width = canvas.clientWidth * devicePixelRatio;
  const height = canvas.height = 180 * devicePixelRatio;
  ctx.clearRect(0, 0, width, height);
  ctx.strokeStyle = "#d7e0ea";
  for (let n = 0; n <= 4; n++) {
    const y = height * n / 4;
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke();
  }
  if (points.length < 2) return;
  ctx.strokeStyle = color; ctx.lineWidth = 3 * devicePixelRatio; ctx.beginPath();
  points.forEach((point, index) => {
    const x = index * width / (points.length - 1);
    const y = height - Math.max(0, Math.min(100, point)) * height / 100;
    index ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  });
  ctx.stroke();
}

async function refresh() {
  const status = document.getElementById("status");
  try {
    const response = await fetch("/api/metrics", { cache: "no-store" });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
    history.cpu.push(data.cpu_percent); history.memory.push(data.memory_percent);
    history.cpu = history.cpu.slice(-30); history.memory = history.memory.slice(-30);
    document.getElementById("cpu-value").textContent = `${data.cpu_percent}%`;
    document.getElementById("memory-value").textContent = `${data.memory_percent}%`;
    draw("cpu", history.cpu, "#1177bb"); draw("memory", history.memory, "#15a37d");
    status.textContent = `Last sample: ${new Date(data.timestamp).toLocaleString()}`;
  } catch (error) { status.textContent = `Collection error: ${error.message}`; }
}
refresh(); setInterval(refresh, 5000); addEventListener("resize", refresh);
