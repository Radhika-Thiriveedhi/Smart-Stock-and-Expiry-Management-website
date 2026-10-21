// StockWise Spotlight Global Search (Ctrl + K / Cmd + K)

document.addEventListener("DOMContentLoaded", function () {
  const modalBackdrop = document.getElementById("cmd-modal-backdrop");
  const searchInput = document.getElementById("cmd-search-input");
  const resultsContainer = document.getElementById("cmd-results");
  const triggerBtn = document.getElementById("cmd-search-trigger");

  if (!modalBackdrop || !searchInput) return;

  function openSearch() {
    modalBackdrop.classList.add("open");
    searchInput.value = "";
    resultsContainer.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 13px;">Type a product name, SKU, or Batch ID...</div>';
    setTimeout(() => searchInput.focus(), 50);
  }

  function closeSearch() {
    modalBackdrop.classList.remove("open");
  }

  // Keyboard shortcut listener
  document.addEventListener("keydown", function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      if (modalBackdrop.classList.contains("open")) {
        closeSearch();
      } else {
        openSearch();
      }
    }
    if (e.key === "Escape" && modalBackdrop.classList.contains("open")) {
      closeSearch();
    }
  });

  if (triggerBtn) {
    triggerBtn.addEventListener("click", openSearch);
  }

  modalBackdrop.addEventListener("click", function (e) {
    if (e.target === modalBackdrop) {
      closeSearch();
    }
  });

  // Debounced search query
  let timeoutId = null;
  searchInput.addEventListener("input", function () {
    clearTimeout(timeoutId);
    const query = searchInput.value.trim();
    if (!query) {
      resultsContainer.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 13px;">Type a product name, SKU, or Batch ID...</div>';
      return;
    }

    resultsContainer.innerHTML = '<div style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 12px;">Searching catalog & batches...</div>';

    timeoutId = setTimeout(() => {
      fetch(`/api/quick-search?q=${encodeURIComponent(query)}`)
        .then(res => res.json())
        .then(data => {
          renderResults(data.results || []);
        })
        .catch(() => {
          resultsContainer.innerHTML = '<div style="padding: 16px; text-align: center; color: var(--color-danger); font-size: 12px;">Search failed. Please try again.</div>';
        });
    }, 200);
  });

  function renderResults(items) {
    if (items.length === 0) {
      resultsContainer.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-muted); font-size: 13px;">No matching products, batches, or orders found.</div>';
      return;
    }

    let html = "";
    items.forEach((item, index) => {
      let badgeClass = "badge-info";
      if (item.badge === "EXPIRED" || item.badge === "CRITICAL") badgeClass = "badge-danger";
      if (item.badge === "WARNING") badgeClass = "badge-warning";
      if (item.badge === "COMPLETED") badgeClass = "badge-success";

      html += `
        <a href="${item.url}" class="cmd-item" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; text-decoration: none; border-bottom: 1px solid var(--border-subtle);">
          <div>
            <div style="font-weight: 600; font-size: 13.5px; color: var(--text-main);">${escapeHtml(item.title)}</div>
            <div style="font-size: 11.5px; color: var(--text-muted); margin-top: 2px;">${escapeHtml(item.subtitle)}</div>
          </div>
          <span class="badge ${badgeClass}" style="font-size: 10px;">${escapeHtml(item.badge)}</span>
        </a>
      `;
    });

    resultsContainer.innerHTML = html;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
});
