/**
 * ResumeIQ — Resume Improvement Lab Controller
 */

async function handleBulletAction(bulletId, status) {
  const container = document.getElementById("bullets-container");
  const analysisId = container ? container.getAttribute("data-analysis-id") : null;
  const textarea = document.getElementById(`textarea-${bulletId}`);
  const badge = document.getElementById(`badge-${bulletId}`);

  if (!analysisId || !textarea) return;

  const userEditedText = textarea.value.trim();

  try {
    const resp = await fetch("/api/bullet/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        analysis_id: parseInt(analysisId),
        bullet_id: bulletId,
        status: status,
        user_edited_text: userEditedText
      })
    });

    const result = await resp.json();
    if (result.success) {
      if (badge) {
        badge.textContent = status.toUpperCase();
        badge.className = "brand-badge status-indicator-badge " + 
          (status === "accepted" ? "chip-matched" : (status === "rejected" ? "chip-missing" : "chip-partial"));
      }
      showToast(`Bullet marked as ${status}!`, "success");
    } else {
      showToast(result.error || "Failed to update bullet state.", "error");
    }
  } catch (err) {
    showToast("Error updating bullet: " + err.message, "error");
  }
}

function copyBulletText(bulletId) {
  const textarea = document.getElementById(`textarea-${bulletId}`);
  if (!textarea) return;

  navigator.clipboard.writeText(textarea.value.trim()).then(() => {
    showToast("Bullet point copied to clipboard!", "success");
  }).catch(() => {
    showToast("Unable to copy to clipboard.", "error");
  });
}

document.addEventListener("DOMContentLoaded", () => {
  // Copy All Accepted Bullets
  const copyAllBtn = document.getElementById("copy-all-accepted-btn");
  if (copyAllBtn) {
    copyAllBtn.addEventListener("click", () => {
      const cards = document.querySelectorAll(".bullet-card");
      const acceptedTexts = [];

      cards.forEach(card => {
        const badge = card.querySelector(".status-indicator-badge");
        if (badge && (badge.textContent.includes("ACCEPTED") || badge.textContent.includes("EDITED"))) {
          const textarea = card.querySelector("textarea");
          if (textarea && textarea.value.trim()) {
            acceptedTexts.push("• " + textarea.value.trim());
          }
        }
      });

      if (acceptedTexts.length === 0) {
        showToast("No bullets marked as Accepted yet. Click 'Accept Suggestion' first.", "info");
        return;
      }

      navigator.clipboard.writeText(acceptedTexts.join("\n\n")).then(() => {
        showToast(`Copied ${acceptedTexts.length} accepted bullet(s) to clipboard!`, "success");
      });
    });
  }

  // Custom Bullet Point Improver
  const customBtn = document.getElementById("custom-improve-btn");
  const customInput = document.getElementById("custom-bullet-input");
  const customResultBox = document.getElementById("custom-result-box");
  const customRevisedText = document.getElementById("custom-revised-text");
  const customPrompt = document.getElementById("custom-metric-prompt");
  const customNotes = document.getElementById("custom-notes");

  if (customBtn && customInput) {
    customBtn.addEventListener("click", async () => {
      const text = customInput.value.trim();
      if (!text) {
        showToast("Please enter a bullet point to improve.", "error");
        return;
      }

      customBtn.disabled = true;
      customBtn.textContent = "Enhancing...";

      try {
        const resp = await fetch("/api/bullet/custom-improve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ bullet_text: text })
        });
        const result = await resp.json();

        if (result.success && result.suggestion) {
          const s = result.suggestion;
          customRevisedText.textContent = s.revised;

          if (s.needs_user_metric && s.user_metric_prompt) {
            customPrompt.style.display = "block";
            customPrompt.innerHTML = `<strong>Factual Metric Prompt:</strong> ${s.user_metric_prompt}`;
          } else {
            customPrompt.style.display = "none";
          }

          customNotes.textContent = `What changed: ${s.what_changed} Diagnostic: ${s.weakness_identified}`;
          customResultBox.style.display = "block";
          showToast("Bullet improved using XYZ formula!", "success");
        } else {
          showToast(result.error || "Failed to improve bullet.", "error");
        }
      } catch (err) {
        showToast("Error processing custom bullet: " + err.message, "error");
      } finally {
        customBtn.disabled = false;
        customBtn.textContent = "Enhance with XYZ Formula";
      }
    });
  }
});
