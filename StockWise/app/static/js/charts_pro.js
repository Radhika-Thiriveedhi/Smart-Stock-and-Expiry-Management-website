// StockWise Pro Interactive Offline SVG Chart Engine
// High-precision financial data visualizations without external CDNs

function renderAreaChart(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container || !data || data.length === 0) return;

  const width = container.clientWidth || 550;
  const height = 240;
  const padding = { top: 30, right: 30, bottom: 45, left: 60 };

  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const maxSales = Math.max(...data.map(d => d.sales), 100);
  const maxProfit = Math.max(...data.map(d => d.profit), 50);
  const maxY = Math.max(maxSales, maxProfit) * 1.2;

  const pointsSales = data.map((d, i) => {
    const x = padding.left + (chartWidth / (data.length - 1 || 1)) * i;
    const y = padding.top + chartHeight - (d.sales / maxY) * chartHeight;
    return { x, y, sales: d.sales, date: d.date };
  });

  const pointsProfit = data.map((d, i) => {
    const x = padding.left + (chartWidth / (data.length - 1 || 1)) * i;
    const y = padding.top + chartHeight - (d.profit / maxY) * chartHeight;
    return { x, y, profit: d.profit, date: d.date };
  });

  let pathSales = `M ${pointsSales[0].x} ${pointsSales[0].y}`;
  pointsSales.slice(1).forEach(pt => {
    pathSales += ` L ${pt.x} ${pt.y}`;
  });

  let areaSales = `${pathSales} L ${pointsSales[pointsSales.length - 1].x} ${padding.top + chartHeight} L ${pointsSales[0].x} ${padding.top + chartHeight} Z`;

  let pathProfit = `M ${pointsProfit[0].x} ${pointsProfit[0].y}`;
  pointsProfit.slice(1).forEach(pt => {
    pathProfit += ` L ${pt.x} ${pt.y}`;
  });

  let svg = `
    <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow: visible; font-family: inherit;">
      <defs>
        <linearGradient id="salesGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#0284c7" stop-opacity="0.35" />
          <stop offset="100%" stop-color="#0284c7" stop-opacity="0.0" />
        </linearGradient>
        <linearGradient id="profitGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#10b981" stop-opacity="0.2" />
          <stop offset="100%" stop-color="#10b981" stop-opacity="0.0" />
        </linearGradient>
      </defs>
  `;

  // Grid Lines
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartHeight / 4) * i;
    const val = Math.round(maxY - (maxY / 4) * i);
    svg += `<line x1="${padding.left}" y1="${y}" x2="${width - padding.right}" y2="${y}" stroke="var(--border-subtle)" stroke-width="1" stroke-dasharray="3,3" />`;
    svg += `<text x="${padding.left - 10}" y="${y + 4}" font-size="10.5" fill="var(--text-light)" font-family="var(--font-mono)" text-anchor="end">$${val}</text>`;
  }

  // Shaded Area & Line for Sales
  svg += `<path d="${areaSales}" fill="url(#salesGrad)" />`;
  svg += `<path d="${pathSales}" fill="none" stroke="#0284c7" stroke-width="2.5" stroke-linecap="round" />`;

  // Shaded Area & Line for Profit
  svg += `<path d="${pathProfit}" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-dasharray="4,4" />`;

  // Interactive Data Points
  pointsSales.forEach((pt, idx) => {
    svg += `<circle cx="${pt.x}" cy="${pt.y}" r="4" fill="#ffffff" stroke="#0284c7" stroke-width="2.5" style="cursor: pointer;" />`;
    if (pt.sales > 0) {
      svg += `<text x="${pt.x}" y="${pt.y - 8}" font-size="10" font-weight="600" fill="var(--text-main)" font-family="var(--font-mono)" text-anchor="middle">$${Math.round(pt.sales)}</text>`;
    }
    const dateLabel = pt.date.substring(5);
    svg += `<text x="${pt.x}" y="${height - 18}" font-size="10.5" fill="var(--text-muted)" text-anchor="middle">${dateLabel}</text>`;
  });

  // Base Axis Line
  svg += `<line x1="${padding.left}" y1="${padding.top + chartHeight}" x2="${width - padding.right}" y2="${padding.top + chartHeight}" stroke="var(--border-color)" stroke-width="1" />`;

  // Legend
  svg += `
    <g transform="translate(${width - 200}, 14)">
      <circle cx="5" cy="5" r="4" fill="#0284c7" />
      <text x="14" y="8" font-size="11" fill="var(--text-muted)">Revenue</text>
      <line x1="85" y1="5" x2="105" y2="5" stroke="#10b981" stroke-width="2" stroke-dasharray="3,3" />
      <text x="112" y="8" font-size="11" fill="var(--text-muted)">Gross Profit</text>
    </g>
  `;

  svg += `</svg>`;
  container.innerHTML = svg;
}

function renderCategoryDonutChart(containerId, categoriesData) {
  const container = document.getElementById(containerId);
  if (!container || !categoriesData || categoriesData.length === 0) return;

  const total = categoriesData.reduce((acc, c) => acc + c.value, 0) || 1;
  const colors = ["#0284c7", "#0d9488", "#f59e0b", "#8b5cf6", "#ec4899", "#10b981"];

  let cumulativeAngle = 0;
  const radius = 60;
  const cx = 80;
  const cy = 80;
  let paths = "";

  categoriesData.forEach((cat, idx) => {
    const sliceAngle = (cat.value / total) * 360;
    const startAngle = cumulativeAngle;
    const endAngle = cumulativeAngle + sliceAngle;
    cumulativeAngle += sliceAngle;

    const x1 = cx + radius * Math.cos((Math.PI * startAngle) / 180);
    const y1 = cy + radius * Math.sin((Math.PI * startAngle) / 180);
    const x2 = cx + radius * Math.cos((Math.PI * endAngle) / 180);
    const y2 = cy + radius * Math.sin((Math.PI * endAngle) / 180);

    const largeArcFlag = sliceAngle > 180 ? 1 : 0;
    const color = colors[idx % colors.length];

    paths += `<path d="M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2} Z" fill="${color}" stroke="var(--bg-surface)" stroke-width="2" />`;
  });

  // Inner cutout to make it a donut
  paths += `<circle cx="${cx}" cy="${cy}" r="38" fill="var(--bg-surface)" />`;
  paths += `<text x="${cx}" y="${cy + 4}" font-size="11" font-weight="700" fill="var(--text-main)" text-anchor="middle">Stock</text>`;

  let legendHtml = '<div style="display: flex; flex-direction: column; gap: 6px; font-size: 11.5px; margin-left: 16px;">';
  categoriesData.forEach((cat, idx) => {
    const color = colors[idx % colors.length];
    const pct = ((cat.value / total) * 100).toFixed(0);
    legendHtml += `
      <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px;">
        <span style="display: flex; align-items: center; gap: 6px;">
          <span style="width: 8px; height: 8px; border-radius: 50%; background: ${color};"></span>
          <span style="color: var(--text-muted);">${cat.name}</span>
        </span>
        <strong class="font-mono">${pct}%</strong>
      </div>
    `;
  });
  legendHtml += '</div>';

  container.innerHTML = `
    <div style="display: flex; align-items: center;">
      <svg width="160" height="160" viewBox="0 0 160 160">
        ${paths}
      </svg>
      ${legendHtml}
    </div>
  `;
}
