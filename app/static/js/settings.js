/**
 * ResumeIQ — Settings & Privacy Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  const apiKeyInput = document.getElementById("settings-api-key");
  const toggleVisibilityBtn = document.getElementById("toggle-key-visibility");
  const saveKeyBtn = document.getElementById("save-key-btn");
  const clearKeyBtn = document.getElementById("clear-key-btn");
  const keyStatusText = document.getElementById("key-status-text");
  const keyStatusBadge = document.getElementById("key-badge-status");
  const activeModelName = document.getElementById("active-model-name");
  const purgeBtn = document.getElementById("purge-data-settings-btn");

  async function refreshSettings() {
    try {
      const resp = await fetch("/api/settings/status");
      const data = await resp.json();

      if (data.success) {
        if (data.gemini_configured) {
          keyStatusText.textContent = `Configured (${data.masked_key})`;
          if (keyStatusBadge) {
            const dot = keyStatusBadge.querySelector(".status-dot");
            if (dot) {
              dot.classList.remove("demo");
              dot.style.backgroundColor = "var(--success)";
            }
          }
        } else {
          keyStatusText.textContent = "Not Configured (Demo Mode Active)";
          if (keyStatusBadge) {
            const dot = keyStatusBadge.querySelector(".status-dot");
            if (dot) {
              dot.classList.add("demo");
              dot.style.backgroundColor = "var(--warning)";
            }
          }
        }

        if (activeModelName) {
          activeModelName.textContent = data.model_name;
        }
      }
    } catch (e) {
      console.warn("Error refreshing settings:", e);
    }
  }

  refreshSettings();

  // Show/Hide Key Toggle
  if (toggleVisibilityBtn && apiKeyInput) {
    toggleVisibilityBtn.addEventListener("click", () => {
      if (apiKeyInput.type === "password") {
        apiKeyInput.type = "text";
        toggleVisibilityBtn.textContent = "Hide";
      } else {
        apiKeyInput.type = "password";
        toggleVisibilityBtn.textContent = "Show";
      }
    });
  }

  // Save API Key
  if (saveKeyBtn && apiKeyInput) {
    saveKeyBtn.addEventListener("click", async () => {
      const key = apiKeyInput.value.trim();
      if (!key) {
        showToast("Please enter an API key.", "error");
        return;
      }

      saveKeyBtn.disabled = true;
      saveKeyBtn.textContent = "Verifying...";

      try {
        const resp = await fetch("/api/settings/api-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ api_key: key })
        });
        const result = await resp.json();

        if (result.success) {
          showToast(result.message, "success");
          apiKeyInput.value = "";
          refreshSettings();
          checkSystemStatus();
        } else {
          showToast(result.error || "Failed to validate key.", "error");
        }
      } catch (err) {
        showToast("Error updating key: " + err.message, "error");
      } finally {
        saveKeyBtn.disabled = false;
        saveKeyBtn.textContent = "Save & Verify API Key";
      }
    });
  }

  // Clear API Key
  if (clearKeyBtn) {
    clearKeyBtn.addEventListener("click", async () => {
      try {
        const resp = await fetch("/api/settings/api-key", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ api_key: "" })
        });
        const result = await resp.json();
        showToast(result.message, "info");
        apiKeyInput.value = "";
        refreshSettings();
        checkSystemStatus();
      } catch (err) {
        showToast("Error clearing key: " + err.message, "error");
      }
    });
  }

  // Purge All Data
  if (purgeBtn) {
    purgeBtn.addEventListener("click", async () => {
      if (!confirm("Are you sure you want to permanently delete all stored evaluations from your local database?")) {
        return;
      }

      try {
        const resp = await fetch("/api/analyses/all", { method: "DELETE" });
        const result = await resp.json();
        if (result.success) {
          showToast(result.message, "success");
        } else {
          showToast(result.error || "Purge failed.", "error");
        }
      } catch (err) {
        showToast("Error executing purge: " + err.message, "error");
      }
    });
  }
});
