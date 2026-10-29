/**
 * ResumeIQ — History & Comparison Controller
 */

let selectedIds = new Set();

async function loadHistory() {
  const loadingEl = document.getElementById("history-loading");
  const emptyEl = document.getElementById("history-empty");
  const wrapperEl = document.getElementById("history-table-wrapper");
  const tbody = document.getElementById("history-tbody");

  try {
    const resp = await fetch("/api/analyses");
    const data = await resp.json();

    loadingEl.style.display = "none";

    if (!data.success || !data.analyses || data.analyses.length === 0) {
      emptyEl.style.display = "block";
      wrapperEl.style.display = "none";
      return;
    }

    emptyEl.style.display = "none";
    wrapperEl.style.display = "block";
    tbody.innerHTML = "";

    data.analyses.forEach(item => {
      const tr = document.createElement("tr");

      const matchBadge = item.job_match_score !== null 
        ? `<span class="skill-chip ${item.job_match_score >= 70 ? 'chip-matched' : (item.job_match_score >= 50 ? 'chip-partial' : 'chip-missing')}" style="padding:2px 8px; font-size:0.75rem;">${item.job_match_score}%</span>`
        : `<span style="font-size:0.75rem; color:var(--text-dim);">No JD</span>`;

      const engineBadge = item.is_demo_mode
        ? `<span class="brand-badge" style="background:var(--warning-bg); color:#fbbf24; border-color:var(--warning-border); font-size:0.7rem;">Demo</span>`
        : `<span class="brand-badge" style="background:var(--primary-light); color:#a5b4fc; font-size:0.7rem;">Gemini</span>`;

      tr.innerHTML = `
        <td style="text-align: center;">
          <input type="checkbox" class="compare-checkbox" value="${item.id}" style="width:16px; height:16px; accent-color:var(--primary);">
        </td>
        <td>
          <strong style="color:#fff;">${item.candidate_name}</strong>
          <span style="display:block; font-size:0.78rem; color:var(--text-dim);">${item.resume_filename}</span>
        </td>
        <td>
          <div>${item.job_title}</div>
          <span style="font-size:0.75rem; color:var(--text-muted);">${item.company_name}</span>
        </td>
        <td>${matchBadge}</td>
        <td>
          <span style="font-size:0.85rem; font-weight:600;">${item.ats_readiness_score}%</span>
        </td>
        <td>${engineBadge}</td>
        <td style="font-size:0.8rem; color:var(--text-dim);">${item.created_at}</td>
        <td style="text-align: right;">
          <div style="display:inline-flex; gap:0.4rem;">
            <a href="/report/${item.id}" class="btn btn-primary btn-sm" style="padding:3px 8px; font-size:0.75rem;">
              View
            </a>
            <button onclick="deleteAnalysis(${item.id})" class="btn btn-outline btn-sm" style="padding:3px 8px; font-size:0.75rem; color:#f87171;" title="Delete this report">
              &times;
            </button>
          </div>
        </td>
      `;

      tbody.appendChild(tr);
    });

    // Attach Checkbox Change Listeners
    document.querySelectorAll(".compare-checkbox").forEach(cb => {
      cb.addEventListener("change", (e) => {
        const id = parseInt(e.target.value);
        if (e.target.checked) {
          if (selectedIds.size >= 2) {
            e.target.checked = false;
            showToast("You can only compare 2 analyses at a time.", "warning");
            return;
          }
          selectedIds.add(id);
        } else {
          selectedIds.delete(id);
        }
        updateCompareButton();
      });
    });

  } catch (err) {
    loadingEl.innerHTML = `<span style="color:#f87171;">Failed to load history: ${err.message}</span>`;
  }
}

function updateCompareButton() {
  const btn = document.getElementById("compare-selected-btn");
  if (!btn) return;

  const count = selectedIds.size;
  btn.textContent = `Compare Selected (${count}/2)`;
  btn.disabled = count !== 2;
}

async function deleteAnalysis(id) {
  if (!confirm(`Are you sure you want to permanently delete Analysis #${id}?`)) {
    return;
  }

  try {
    const resp = await fetch(`/api/analyses/${id}`, { method: "DELETE" });
    const result = await resp.json();
    if (result.success) {
      showToast("Record deleted successfully.", "success");
      selectedIds.delete(id);
      loadHistory();
    } else {
      showToast(result.error || "Failed to delete record.", "error");
    }
  } catch (err) {
    showToast("Error deleting analysis: " + err.message, "error");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadHistory();

  // Compare Selected Trigger
  const compareBtn = document.getElementById("compare-selected-btn");
  if (compareBtn) {
    compareBtn.addEventListener("click", () => {
      if (selectedIds.size !== 2) return;
      const arr = Array.from(selectedIds);
      window.location.href = `/compare?id1=${arr[0]}&id2=${arr[1]}`;
    });
  }

  // Purge All Records Trigger
  const purgeBtn = document.getElementById("purge-all-btn");
  if (purgeBtn) {
    purgeBtn.addEventListener("click", async () => {
      const confirmText = prompt("Warning: This will permanently delete ALL saved analysis records from the local SQLite database.\n\nType 'DELETE' to confirm:");
      if (confirmText !== "DELETE") {
        showToast("Purge canceled.", "info");
        return;
      }

      try {
        const resp = await fetch("/api/analyses/all", { method: "DELETE" });
        const result = await resp.json();
        if (result.success) {
          showToast(result.message, "success");
          selectedIds.clear();
          loadHistory();
        } else {
          showToast(result.error || "Purge failed.", "error");
        }
      } catch (err) {
        showToast("Error executing purge: " + err.message, "error");
      }
    });
  }
});
