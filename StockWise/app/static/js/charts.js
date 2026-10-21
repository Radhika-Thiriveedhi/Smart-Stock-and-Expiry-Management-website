// StockWise Offline Native SVG Chart Generator
// Renders clean, restrained, crisp charts without external internet dependencies.

function renderSalesTrendChart(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container || !data || data.length === 0) return;

  const width = container.clientWidth || 500;
  const height = 220;
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const maxVal = Math.max(...data.map(d => d.sales), 100) * 1.15;
  const barWidth = Math.max(16, (chartWidth / data.length) * 0.55);

  let svg = `<svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow:visible; font-family:inherit;">`;

  // Horizontal Grid Lines
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartHeight / 4) * i;
    const val = Math.round(maxVal - (maxVal / 4) * i);
    svg += `<line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="2,2"/>`;
    svg += `<text x="${padding.left - 8}" y="${y + 4}" font-size="10" fill="#64748b" text-anchor="end">$${val}</text>`;
  }

  // Bars and Labels
  data.forEach((d, idx) => {
    const x = padding.left + (chartWidth / data.length) * idx + (chartWidth / data.length - barWidth) / 2;
    const h = (d.sales / maxVal) * chartHeight;
    const y = padding.top + (chartHeight - h);
    const dateLabel = d.date.substring(5); // MM-DD

    // Bar
    svg += `<rect x="${x}" y="${y}" width="${barWidth}" height="${h}" rx="3" fill="#0f766e" />`;
    // Value tooltip/label on bar top if space
    if (d.sales > 0) {
      svg += `<text x="${x + barWidth / 2}" y="${y - 4}" font-size="9" font-weight="600" fill="#0f172a" text-anchor="middle">$${Math.round(d.sales)}</text>`;
    }
    // X-axis date
    svg += `<text x="${x + barWidth / 2}" y="${height - 15}" font-size="10" fill="#64748b" text-anchor="middle">${dateLabel}</text>`;
  });

  // Base line
  svg += `<line x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}" stroke="#cbd5e1" stroke-width="1"/>`;
  svg += `</svg>`;

  container.innerHTML = svg;
}

function renderExpiryRiskBar(containerId, healthy, warning, critical, expired) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const total = (healthy + warning + critical + expired) || 1;
  const pHealthy = ((healthy / total) * 100).toFixed(1);
  const pWarning = ((warning / total) * 100).toFixed(1);
  const pCritical = ((critical / total) * 100).toFixed(1);
  const pExpired = ((expired / total) * 100).toFixed(1);

  container.innerHTML = `
    <div style="height: 18px; border-radius: 4px; overflow: hidden; display: flex; width: 100%; margin-bottom: 12px; background: #e2e8f0;">
      <div style="width: ${pHealthy}%; background: #15803d;" title="Healthy: $${healthy.toFixed(2)} (${pHealthy}%)"></div>
      <div style="width: ${pWarning}%; background: #d97706;" title="Near Expiry (7d): $${warning.toFixed(2)} (${pWarning}%)"></div>
      <div style="width: ${pCritical}%; background: #dc2626;" title="Critical (3d): $${critical.toFixed(2)} (${pCritical}%)"></div>
      <div style="width: ${pExpired}%; background: #7f1d1d;" title="Expired: $${expired.toFixed(2)} (${pExpired}%)"></div>
    </div>
    <div style="display: flex; gap: 16px; font-size: 11px; flex-wrap: wrap;">
      <span style="display: flex; align-items: center; gap: 4px;"><span style="width: 10px; height: 10px; background: #15803d; border-radius: 2px;"></span> Healthy ($${healthy.toFixed(0)})</span>
      <span style="display: flex; align-items: center; gap: 4px;"><span style="width: 10px; height: 10px; background: #d97706; border-radius: 2px;"></span> Near Expiry ($${warning.toFixed(0)})</span>
      <span style="display: flex; align-items: center; gap: 4px;"><span style="width: 10px; height: 10px; background: #dc2626; border-radius: 2px;"></span> Critical ($${critical.toFixed(0)})</span>
      <span style="display: flex; align-items: center; gap: 4px;"><span style="width: 10px; height: 10px; background: #7f1d1d; border-radius: 2px;"></span> Expired ($${expired.toFixed(0)})</span>
    </div>
  `;
}
