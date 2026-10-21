// StockWise Multi-Palette Theme Engine (Light Brown, Emerald, Sapphire, Obsidian Dark)

(function () {
  const THEME_KEY = "stockwise-theme-v4";
  
  function getPreferredTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved) return saved;
    return "brown"; // Default: Warm Light Brown Retail
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
    
    // Update theme pill states in navbar
    document.querySelectorAll(".theme-selector-pill").forEach(pill => {
      if (pill.getAttribute("data-set-theme") === theme) {
        pill.classList.add("active");
      } else {
        pill.classList.remove("active");
      }
    });
  }

  // Apply immediately before DOM render
  applyTheme(getPreferredTheme());

  document.addEventListener("DOMContentLoaded", function () {
    // Re-apply to update any dynamic buttons
    applyTheme(getPreferredTheme());

    document.querySelectorAll(".theme-selector-pill").forEach(pill => {
      pill.addEventListener("click", function (e) {
        e.preventDefault();
        const selected = this.getAttribute("data-set-theme");
        applyTheme(selected);
      });
    });
  });
})();
