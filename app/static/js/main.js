/**
 * ResumeIQ — Core UI & Application Controller
 */

// Toast Notifications
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div style="flex:1;">${message}</div>
    <button onclick="this.parentElement.remove()" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.1rem;">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transition = "opacity 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Loading Overlay
function showLoading(stepText = "Processing Resume Analysis...") {
  const overlay = document.getElementById("loading-overlay");
  const stepEl = document.getElementById("loading-step-text");
  if (overlay) {
    overlay.style.display = "flex";
    overlay.setAttribute("aria-hidden", "false");
  }
  if (stepEl && stepText) {
    stepEl.textContent = stepText;
  }
}

function updateLoadingStep(stepText) {
  const stepEl = document.getElementById("loading-step-text");
  if (stepEl) stepEl.textContent = stepText;
}

function hideLoading() {
  const overlay = document.getElementById("loading-overlay");
  if (overlay) {
    overlay.style.display = "none";
    overlay.setAttribute("aria-hidden", "true");
  }
}

// Global System Status Check
async function checkSystemStatus() {
  try {
    const resp = await fetch("/api/settings/status");
    if (!resp.ok) return;
    const data = await resp.json();

    const statusPill = document.getElementById("system-status-pill");
    const statusText = document.getElementById("status-model-text");
    const demoAlert = document.getElementById("global-demo-alert");

    if (data.gemini_configured) {
      if (statusText) statusText.textContent = data.model_name;
      if (statusPill) {
        const dot = statusPill.querySelector(".status-dot");
        if (dot) {
          dot.classList.remove("demo");
          dot.style.backgroundColor = "var(--success)";
        }
      }
    } else {
      if (statusText) statusText.textContent = "Academic Demo Mode";
      if (demoAlert && window.location.pathname === "/dashboard") {
        demoAlert.style.display = "flex";
      }
    }
  } catch (err) {
    console.warn("Unable to check system status:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  checkSystemStatus();
});
