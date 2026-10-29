/**
 * ResumeIQ — Report View Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // Skill Matrix Filter Pills
  const filterPills = document.querySelectorAll(".filter-pill");
  const skillRows = document.querySelectorAll(".skill-row");

  filterPills.forEach(pill => {
    pill.addEventListener("click", () => {
      filterPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");

      const filterType = pill.getAttribute("data-filter");

      skillRows.forEach(row => {
        if (filterType === "all") {
          row.style.display = "block";
        } else {
          const rowType = row.getAttribute("data-type");
          row.style.display = (rowType === filterType) ? "block" : "none";
        }
      });
    });
  });

  // Toggle Scoring Formula Drawer
  const formulaBtn = document.getElementById("toggle-formula-btn");
  const formulaCard = document.getElementById("formula-breakdown-card");
  if (formulaBtn && formulaCard) {
    formulaBtn.addEventListener("click", () => {
      const isVisible = formulaCard.style.display === "block";
      formulaCard.style.display = isVisible ? "none" : "block";
      if (!isVisible) {
        formulaCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    });
  }

  // Export Dropdown Menu
  const exportBtn = document.getElementById("export-btn");
  const exportMenu = document.getElementById("export-menu");
  if (exportBtn && exportMenu) {
    exportBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isVisible = exportMenu.style.display === "block";
      exportMenu.style.display = isVisible ? "none" : "block";
    });

    document.addEventListener("click", () => {
      exportMenu.style.display = "none";
    });
  }
});
