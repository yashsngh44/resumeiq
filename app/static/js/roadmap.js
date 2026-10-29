/**
 * ResumeIQ — Career Roadmap Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  const filterBtns = document.querySelectorAll(".roadmap-filter");
  const cards = document.querySelectorAll(".roadmap-card");

  filterBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      filterBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const priority = btn.getAttribute("data-priority");

      cards.forEach(card => {
        if (priority === "all") {
          card.style.display = "flex";
        } else {
          const cardPriority = card.getAttribute("data-priority");
          card.style.display = (cardPriority === priority) ? "flex" : "none";
        }
      });
    });
  });
});
