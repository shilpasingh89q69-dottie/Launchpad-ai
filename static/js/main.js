/**
 * main.js
 * -------
 * Handles form submission via Fetch API, client-side validation,
 * processing state UI, and dynamic rendering of AI analysis results
 * into the Startup Analytics / SWOT / Recommendations cards.
 */

const MAX_LENGTH = window.LP_MAX_LENGTH || 2000;

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("startup-form");
  const textFields = form.querySelectorAll("textarea, input[type='text']");

  textFields.forEach((field) => attachCharCounter(field));

  form.addEventListener("submit", handleSubmit);

  loadHistory();
});

/* -------------------------------------------------------------------- */
/* Character counting / validation                                      */
/* -------------------------------------------------------------------- */

function attachCharCounter(field) {
  const counterId = `${field.id}-counter`;
  const counter = document.getElementById(counterId);
  if (!counter) return;

  const update = () => {
    const len = field.value.length;
    counter.textContent = `${len} / ${MAX_LENGTH}`;
    counter.classList.toggle("over-limit", len > MAX_LENGTH);
  };

  field.addEventListener("input", update);
  update();
}

function validateForm(data) {
  for (const [key, value] of Object.entries(data)) {
    if (!value || !value.trim()) {
      return `Please fill in the "${labelFor(key)}" field.`;
    }
    if (value.length > MAX_LENGTH) {
      return `"${labelFor(key)}" exceeds the ${MAX_LENGTH} character limit.`;
    }
  }
  return null;
}

function labelFor(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

/* -------------------------------------------------------------------- */
/* Form submission                                                      */
/* -------------------------------------------------------------------- */

async function handleSubmit(e) {
  e.preventDefault();

  const formData = {
    startup_name: document.getElementById("startup_name").value.trim(),
    description: document.getElementById("description").value.trim(),
    target_audience: document.getElementById("target_audience").value.trim(),
    business_model: document.getElementById("business_model").value.trim(),
  };

  const validationError = validateForm(formData);
  if (validationError) {
    showAlert(validationError, "danger");
    return;
  }

  setProcessing(true);
  hideAlert();
  hideResults();

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    const payload = await response.json();

    if (!response.ok || !payload.success) {
      throw new Error(payload.error || "Something went wrong while analyzing your startup.");
    }

    renderResults(payload.data);

    if (payload.warning) {
      showAlert(payload.warning, "warning");
    }

    loadHistory();
  } catch (err) {
    console.error(err);
    showAlert(err.message || "Network error. Please try again.", "danger");
  } finally {
    setProcessing(false);
  }
}

function setProcessing(isProcessing) {
  const processingEl = document.getElementById("processing-state");
  const submitBtn = document.getElementById("submit-btn");

  processingEl.style.display = isProcessing ? "flex" : "none";
  submitBtn.disabled = isProcessing;
  submitBtn.textContent = isProcessing ? "Analyzing..." : "Launch Analysis";
}

/* -------------------------------------------------------------------- */
/* Alerts                                                                */
/* -------------------------------------------------------------------- */

function showAlert(message, type = "danger") {
  const box = document.getElementById("alert-box");
  box.className = `alert alert-${type}`;
  box.textContent = message;
  box.style.display = "block";
  box.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hideAlert() {
  const box = document.getElementById("alert-box");
  box.style.display = "none";
}

/* -------------------------------------------------------------------- */
/* Rendering results                                                     */
/* -------------------------------------------------------------------- */

function hideResults() {
  document.getElementById("results-section").style.display = "none";
}

function renderResults(data) {
  renderAnalytics(data);
  renderSwot(data.swot);
  renderRecommendations(data);

  const section = document.getElementById("results-section");
  section.style.display = "block";
  section.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderAnalytics(data) {
  document.getElementById("viability-score").textContent = data.viability_score;
  document.getElementById("innovation-score").textContent = data.innovation_score;
  document.getElementById("analytics-startup-name").textContent = data.startup_name || "";
}

function renderSwot(swot) {
  const map = {
    strengths: "swot-strengths-list",
    weaknesses: "swot-weaknesses-list",
    opportunities: "swot-opportunities-list",
    threats: "swot-threats-list",
  };

  Object.entries(map).forEach(([key, elementId]) => {
    const list = document.getElementById(elementId);
    list.innerHTML = "";
    (swot[key] || []).forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      list.appendChild(li);
    });
  });
}

function renderRecommendations(data) {
  document.getElementById("market-insights-text").textContent = data.market_insights;
  document.getElementById("growth-strategy-text").textContent = data.growth_strategy;
}

/* -------------------------------------------------------------------- */
/* History                                                               */
/* -------------------------------------------------------------------- */

async function loadHistory() {
  const historyList = document.getElementById("history-list");
  if (!historyList) return;

  try {
    const res = await fetch("/api/history");
    const payload = await res.json();

    if (!payload.success) return;

    historyList.innerHTML = "";

    if (payload.data.length === 0) {
      historyList.innerHTML = `<p class="text-muted small mb-0">No reports yet. Run your first analysis above.</p>`;
      return;
    }

    payload.data.forEach((report) => {
      const item = document.createElement("div");
      item.className = "d-flex justify-content-between align-items-center border-bottom py-2";
      item.innerHTML = `
        <div>
          <strong>${escapeHtml(report.startup_name)}</strong>
          <div class="text-muted small">Viability: ${report.viability_score} · Innovation: ${report.innovation_score}</div>
        </div>
        <button class="btn btn-sm btn-outline-secondary view-report-btn">View</button>
      `;
      item.querySelector(".view-report-btn").addEventListener("click", () => renderResults(report));
      historyList.appendChild(item);
    });
  } catch (err) {
    console.error("Failed to load history:", err);
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
