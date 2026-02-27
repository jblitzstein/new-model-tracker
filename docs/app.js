/* AI Model Tracker — Dashboard Logic */

const PROVIDER_COLORS = {
  "OpenAI": "#10a37f",
  "Anthropic": "#d97706",
  "Google": "#4285f4",
  "Meta": "#0668E1",
  "Mistral": "#ff7000",
  "DeepSeek": "#4f46e5",
  "Cohere": "#39594d",
  "xAI": "#1d1d1f",
  "NVIDIA": "#76b900",
  "Microsoft": "#00a4ef",
  "Amazon": "#ff9900",
  "Qwen": "#615fff",
  "Stability AI": "#a855f7",
  "Black Forest Labs": "#1e293b",
  "ByteDance": "#00f5d4",
  "Apple": "#555555",
  "Nous Research": "#ef4444",
  "Allen AI": "#2563eb",
  "EleutherAI": "#7c3aed",
  "Perplexity": "#20b2aa",
};

const MODALITY_ICONS = {
  text: "💬",
  image: "🖼️",
  video: "🎬",
  audio: "🎵",
  code: "💻",
};

let allModels = [];
let filteredModels = [];

// --- Data Loading ---

async function loadModels() {
  try {
    const resp = await fetch("latest.json");
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    allModels = await resp.json();
    populateProviderFilter();
    applyFilters();
  } catch (err) {
    document.getElementById("models-grid").innerHTML =
      `<div class="loading">Failed to load model data: ${err.message}</div>`;
  }
}

// --- Filtering ---

function populateProviderFilter() {
  const providers = [...new Set(allModels.map(m => m.provider))].sort();
  const select = document.getElementById("provider-filter");
  providers.forEach(p => {
    const opt = document.createElement("option");
    opt.value = p;
    opt.textContent = p;
    select.appendChild(opt);
  });
}

function applyFilters() {
  const search = document.getElementById("search").value.toLowerCase();
  const provider = document.getElementById("provider-filter").value;
  const source = document.getElementById("source-filter").value;
  const activeModBtn = document.querySelector(".mod-btn.active");
  const modality = activeModBtn ? activeModBtn.dataset.mod : "";
  const sort = document.getElementById("sort-select").value;

  filteredModels = allModels.filter(m => {
    if (search && !m.name.toLowerCase().includes(search) &&
        !m.provider.toLowerCase().includes(search) &&
        !(m.description || "").toLowerCase().includes(search)) return false;
    if (provider && m.provider !== provider) return false;
    if (source && m.source !== source) return false;
    if (modality && !(m.modality || []).includes(modality)) return false;
    return true;
  });

  // Sort
  filteredModels.sort((a, b) => {
    switch (sort) {
      case "date-desc":
        return (b.release_date || b.first_seen || "").localeCompare(a.release_date || a.first_seen || "");
      case "date-asc":
        return (a.release_date || a.first_seen || "").localeCompare(b.release_date || b.first_seen || "");
      case "name-asc":
        return a.name.localeCompare(b.name);
      case "provider-asc":
        return a.provider.localeCompare(b.provider) || a.name.localeCompare(b.name);
      default:
        return 0;
    }
  });

  render();
}

// --- Rendering ---

function formatDate(iso) {
  if (!iso) return "Unknown";
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
  } catch { return iso; }
}

function formatPricing(pricing) {
  if (!pricing) return null;
  const prompt = pricing.prompt_per_million;
  const completion = pricing.completion_per_million;
  if (prompt == null && completion == null) return null;
  if (prompt === 0 && completion === 0) return "Free";
  return `$${prompt?.toFixed(2) ?? "?"} / $${completion?.toFixed(2) ?? "?"} per M tokens`;
}

function providerColor(provider) {
  return PROVIDER_COLORS[provider] || "#6e7681";
}

function renderCard(model) {
  const card = document.createElement("div");
  card.className = "model-card";

  const color = providerColor(model.provider);
  const mods = (model.modality || ["text"]).map(m =>
    `<span class="modality-tag">${MODALITY_ICONS[m] || ""} ${m}</span>`
  ).join("");

  const pricing = formatPricing(model.pricing);
  const pricingHtml = pricing ? `<span class="pricing">${pricing}</span>` : "";

  const desc = model.description
    ? `<div class="card-desc">${escapeHtml(model.description)}</div>`
    : "";

  const ctx = model.context_length
    ? `<span>📏 ${(model.context_length / 1000).toFixed(0)}K ctx</span>`
    : "";

  const url = model.url || "#";

  card.innerHTML = `
    <div class="card-header">
      <div class="model-name"><a href="${escapeHtml(url)}" target="_blank" rel="noopener">${escapeHtml(model.name)}</a></div>
      <span class="provider-badge" style="background:${color}22;color:${color};border:1px solid ${color}44">${escapeHtml(model.provider)}</span>
    </div>
    <div class="card-meta">
      <span>📅 ${formatDate(model.release_date)}</span>
      ${ctx}
      ${mods}
    </div>
    ${desc}
    <div class="card-footer">
      ${pricingHtml}
      <span class="source-tag">${model.source}</span>
    </div>
  `;
  return card;
}

function render() {
  const grid = document.getElementById("models-grid");
  const stats = document.getElementById("stats");

  stats.textContent = `Showing ${filteredModels.length} of ${allModels.length} models`;

  grid.innerHTML = "";
  if (filteredModels.length === 0) {
    grid.innerHTML = '<div class="no-results">No models match your filters.</div>';
    return;
  }

  const fragment = document.createDocumentFragment();
  filteredModels.forEach(m => fragment.appendChild(renderCard(m)));
  grid.appendChild(fragment);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// --- Event Listeners ---

document.getElementById("search").addEventListener("input", applyFilters);
document.getElementById("provider-filter").addEventListener("change", applyFilters);
document.getElementById("source-filter").addEventListener("change", applyFilters);
document.getElementById("sort-select").addEventListener("change", applyFilters);

document.getElementById("modality-filters").addEventListener("click", (e) => {
  const btn = e.target.closest(".mod-btn");
  if (!btn) return;
  document.querySelectorAll(".mod-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  applyFilters();
});

document.getElementById("theme-toggle").addEventListener("click", () => {
  const html = document.documentElement;
  const current = html.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  html.setAttribute("data-theme", next);
  document.getElementById("theme-toggle").textContent = next === "dark" ? "🌙" : "☀️";
  localStorage.setItem("theme", next);
});

// Restore theme
const saved = localStorage.getItem("theme");
if (saved) {
  document.documentElement.setAttribute("data-theme", saved);
  document.getElementById("theme-toggle").textContent = saved === "dark" ? "🌙" : "☀️";
}

// --- Init ---
loadModels();
