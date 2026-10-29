/**
 * ResumeIQ — Upload & Form Handling Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("analysis-form");
  const dropzone = document.getElementById("resume-dropzone");
  const fileInput = document.getElementById("resume-input");
  const previewCard = document.getElementById("file-preview-card");
  const fileNameEl = document.getElementById("selected-file-name");
  const fileSizeEl = document.getElementById("selected-file-size");
  const removeFileBtn = document.getElementById("remove-file-btn");
  const jdTextarea = document.getElementById("job_description");
  const jdCounter = document.getElementById("jd-counter");
  const loadSampleBtn = document.getElementById("load-sample-btn");
  const submitBtn = document.getElementById("submit-btn");

  if (!form) return;

  // File Selection & Drag-and-Drop
  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      fileInput.click();
    }
  });

  ["dragenter", "dragover"].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
      handleFile(fileInput.files[0]);
    }
  });

  removeFileBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.value = "";
    previewCard.style.display = "none";
    dropzone.style.display = "block";
  });

  function handleFile(file) {
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (![".pdf", ".docx"].includes(ext)) {
      showToast("Unsupported format. Please upload a PDF or DOCX file.", "error");
      fileInput.value = "";
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      showToast("File size exceeds 5MB limit. Please upload a smaller document.", "error");
      fileInput.value = "";
      return;
    }

    // Update Preview
    fileNameEl.textContent = file.name;
    fileSizeEl.textContent = formatBytes(file.size);
    dropzone.style.display = "none";
    previewCard.style.display = "flex";
  }

  function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  }

  // Job Description Word Counter
  if (jdTextarea && jdCounter) {
    jdTextarea.addEventListener("input", () => {
      const text = jdTextarea.value.trim();
      const words = text ? text.split(/\s+/).length : 0;
      jdCounter.textContent = `${words} words`;
    });
  }

  // Load Sample Job Description
  if (loadSampleBtn) {
    loadSampleBtn.addEventListener("click", () => {
      document.getElementById("job_title").value = "Full Stack Software Engineer";
      document.getElementById("company_name").value = "Nexus Technologies";
      jdTextarea.value = `Position: Full Stack Software Engineer
Location: Remote / Hybrid

About the Role:
We are looking for a versatile Full Stack Software Engineer to build and scale our modern cloud applications. You will design reliable web services, collaborate with frontend designers, and implement resilient microservices.

Required Qualifications & Skills:
- 2+ years of software development experience with Python or JavaScript/TypeScript.
- Hands-on experience developing RESTful APIs using Flask, FastAPI, or Django.
- Solid frontend experience with modern React, HTML5, and CSS3.
- Proven experience with relational databases such as PostgreSQL or MySQL, including schema design and query optimization.
- Proficiency with Git version control and collaborative GitHub workflows.
- Strong foundational understanding of data structures, algorithms, and automated testing (unit and integration tests).

Preferred / Nice to Have:
- Experience containerizing services using Docker and orchestrating with Kubernetes.
- Familiarity with AWS or Google Cloud (GCP) services (EC2, S3, Cloud Run).
- Knowledge of CI/CD pipelines (GitHub Actions) and Redis caching.
- Excellent communication skills and passion for building clean, user-centric software.`;

      const words = jdTextarea.value.trim().split(/\s+/).length;
      jdCounter.textContent = `${words} words`;
      showToast("Sample Software Engineer job description loaded!", "info");
    });
  }

  // Form Submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!fileInput.files.length) {
      showToast("Please upload a resume file (.pdf or .docx).", "error");
      return;
    }

    const formData = new FormData(form);
    submitBtn.disabled = true;

    showLoading("Uploading document & parsing text with PyMuPDF...");

    // Simulated progress steps for great UX
    const stepTimer1 = setTimeout(() => updateLoadingStep("Auditing deterministic ATS compliance & contact metadata..."), 1200);
    const stepTimer2 = setTimeout(() => updateLoadingStep("Analyzing skill gap matrix & calculating transparent job match score..."), 2600);
    const stepTimer3 = setTimeout(() => updateLoadingStep("Synthesizing personalized career roadmap & XYZ bullet rewrites..."), 4000);

    try {
      const resp = await fetch("/api/analyze", {
        method: "POST",
        body: formData
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);

      const result = await resp.json();

      if (!result.success) {
        hideLoading();
        submitBtn.disabled = false;
        showToast(result.error || "Failed to analyze resume.", "error");

        if (result.can_fallback_demo) {
          // Offer one-click demo mode fallback
          setTimeout(() => {
            if (confirm("The external API request encountered an issue. Would you like to evaluate using Academic Demo Mode (offline heuristic engine)?")) {
              document.getElementById("demo_mode").checked = true;
              form.requestSubmit();
            }
          }, 500);
        }
        return;
      }

      updateLoadingStep("Analysis complete! Preparing your report dashboard...");
      setTimeout(() => {
        window.location.href = result.redirect_url;
      }, 600);

    } catch (err) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      hideLoading();
      submitBtn.disabled = false;
      showToast("Network error while connecting to server: " + err.message, "error");
    }
  });

});
