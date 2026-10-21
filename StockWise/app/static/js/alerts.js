// StockWise Alert Notifications & Toast Handling

document.addEventListener("DOMContentLoaded", function () {
  // Allow user to dismiss alerts
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(alert => {
    const closeBtn = document.createElement("button");
    closeBtn.innerHTML = "&times;";
    closeBtn.style.background = "transparent";
    closeBtn.style.border = "none";
    closeBtn.style.fontSize = "18px";
    closeBtn.style.cursor = "pointer";
    closeBtn.style.marginLeft = "12px";
    closeBtn.style.color = "inherit";
    closeBtn.style.opacity = "0.7";

    closeBtn.addEventListener("click", () => {
      alert.style.transition = "opacity 0.2s ease, transform 0.2s ease";
      alert.style.opacity = "0";
      setTimeout(() => alert.remove(), 200);
    });

    alert.appendChild(closeBtn);

    // Auto dismiss after 7 seconds if not danger
    if (!alert.classList.contains("alert-danger")) {
      setTimeout(() => {
        if (alert.parentElement) {
          alert.style.transition = "opacity 0.4s ease";
          alert.style.opacity = "0";
          setTimeout(() => alert.remove(), 400);
        }
      }, 7000);
    }
  });
});
