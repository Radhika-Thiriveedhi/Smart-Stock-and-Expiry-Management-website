// StockWise Main Client-Side Utilities

document.addEventListener("DOMContentLoaded", function () {
  // 1. Client-side quick filter on data-tables
  const tableSearchInputs = document.querySelectorAll("[data-table-search]");
  tableSearchInputs.forEach(input => {
    input.addEventListener("input", function () {
      const targetTableId = this.getAttribute("data-table-search");
      const filter = this.value.toLowerCase().trim();
      const table = document.getElementById(targetTableId);
      if (!table) return;

      const rows = table.querySelectorAll("tbody tr");
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? "" : "none";
      });
    });
  });

  // 2. Add Item Row for Purchase Order
  const addPoItemBtn = document.getElementById("add-po-item-btn");
  if (addPoItemBtn) {
    addPoItemBtn.addEventListener("click", function () {
      const tableBody = document.querySelector("#po-items-table tbody");
      const firstRow = tableBody.querySelector("tr");
      if (!firstRow) return;

      const newRow = firstRow.cloneNode(true);
      // Reset inputs
      newRow.querySelectorAll("input").forEach(i => i.value = "");
      newRow.querySelectorAll("select").forEach(s => s.selectedIndex = 0);
      const subtotalEl = newRow.querySelector(".row-subtotal");
      if (subtotalEl) subtotalEl.textContent = "$0.00";

      tableBody.appendChild(newRow);
      attachPoRowListeners(newRow);
    });

    document.querySelectorAll("#po-items-table tbody tr").forEach(row => {
      attachPoRowListeners(row);
    });
  }

  function attachPoRowListeners(row) {
    const qtyInput = row.querySelector("input[name='quantity[]']");
    const costInput = row.querySelector("input[name='unit_cost[]']");
    const selectEl = row.querySelector("select[name='product_id[]']");
    const removeBtn = row.querySelector(".remove-row-btn");
    const subtotalEl = row.querySelector(".row-subtotal");

    function updateSubtotal() {
      const q = parseFloat(qtyInput ? qtyInput.value : 0) || 0;
      const c = parseFloat(costInput ? costInput.value : 0) || 0;
      const sub = q * c;
      if (subtotalEl) subtotalEl.textContent = "$" + sub.toFixed(2);
      recalcPoTotal();
    }

    if (qtyInput) qtyInput.addEventListener("input", updateSubtotal);
    if (costInput) costInput.addEventListener("input", updateSubtotal);

    if (removeBtn) {
      removeBtn.addEventListener("click", function () {
        const tbody = row.parentElement;
        if (tbody.children.length > 1) {
          row.remove();
          recalcPoTotal();
        } else {
          alert("A purchase order must have at least one product line.");
        }
      });
    }
  }

  function recalcPoTotal() {
    let grandTotal = 0;
    document.querySelectorAll("#po-items-table tbody tr").forEach(r => {
      const q = parseFloat(r.querySelector("input[name='quantity[]']").value) || 0;
      const c = parseFloat(r.querySelector("input[name='unit_cost[]']").value) || 0;
      grandTotal += (q * c);
    });
    const totalEl = document.getElementById("po-grand-total");
    if (totalEl) totalEl.textContent = "$" + grandTotal.toFixed(2);
  }

  // 3. Add Item Row for Sale / POS Screen
  const addSaleItemBtn = document.getElementById("add-sale-item-btn");
  if (addSaleItemBtn) {
    addSaleItemBtn.addEventListener("click", function () {
      const tableBody = document.querySelector("#sale-items-table tbody");
      const firstRow = tableBody.querySelector("tr");
      if (!firstRow) return;

      const newRow = firstRow.cloneNode(true);
      newRow.querySelectorAll("input").forEach(i => i.value = "1");
      newRow.querySelectorAll("select").forEach(s => s.selectedIndex = 0);
      const subtotalEl = newRow.querySelector(".sale-row-subtotal");
      if (subtotalEl) subtotalEl.textContent = "$0.00";
      const stockBadge = newRow.querySelector(".row-stock-info");
      if (stockBadge) stockBadge.textContent = "";

      tableBody.appendChild(newRow);
      attachSaleRowListeners(newRow);
    });

    document.querySelectorAll("#sale-items-table tbody tr").forEach(row => {
      attachSaleRowListeners(row);
    });
  }

  function attachSaleRowListeners(row) {
    const selectEl = row.querySelector("select[name='product_id[]']");
    const qtyInput = row.querySelector("input[name='quantity[]']");
    const priceDisplay = row.querySelector(".row-unit-price");
    const subtotalEl = row.querySelector(".sale-row-subtotal");
    const stockBadge = row.querySelector(".row-stock-info");
    const removeBtn = row.querySelector(".remove-sale-row-btn");

    function updateRow() {
      const opt = selectEl.options[selectEl.selectedIndex];
      if (!opt || !opt.value) {
        if (priceDisplay) priceDisplay.textContent = "$0.00";
        if (subtotalEl) subtotalEl.textContent = "$0.00";
        if (stockBadge) stockBadge.textContent = "";
        recalcSaleTotal();
        return;
      }

      const price = parseFloat(opt.getAttribute("data-price")) || 0;
      const stock = parseInt(opt.getAttribute("data-stock")) || 0;
      const qty = parseInt(qtyInput.value) || 0;

      if (priceDisplay) priceDisplay.textContent = "$" + price.toFixed(2);
      if (stockBadge) {
        stockBadge.textContent = stock + " available";
        stockBadge.className = "row-stock-info badge " + (stock <= 5 ? "badge-danger" : "badge-info");
      }
      if (subtotalEl) subtotalEl.textContent = "$" + (qty * price).toFixed(2);
      recalcSaleTotal();
    }

    if (selectEl) selectEl.addEventListener("change", updateRow);
    if (qtyInput) qtyInput.addEventListener("input", updateRow);

    if (removeBtn) {
      removeBtn.addEventListener("click", function () {
        const tbody = row.parentElement;
        if (tbody.children.length > 1) {
          row.remove();
          recalcSaleTotal();
        } else {
          alert("Sale must contain at least one item.");
        }
      });
    }

    updateRow();
  }

  function recalcSaleTotal() {
    let grandTotal = 0;
    document.querySelectorAll("#sale-items-table tbody tr").forEach(r => {
      const sel = r.querySelector("select[name='product_id[]']");
      const opt = sel ? sel.options[sel.selectedIndex] : null;
      if (opt && opt.value) {
        const price = parseFloat(opt.getAttribute("data-price")) || 0;
        const qty = parseInt(r.querySelector("input[name='quantity[]']").value) || 0;
        grandTotal += (price * qty);
      }
    });
    const grandEl = document.getElementById("sale-grand-total");
    if (grandEl) grandEl.textContent = "$" + grandTotal.toFixed(2);
  }
});
