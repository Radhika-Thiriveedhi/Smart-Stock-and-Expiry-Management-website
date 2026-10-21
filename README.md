# StockWise — Smart Stock & Expiry Management

A practical, real-world retail inventory, expiry tracking, and financial intelligence web application built with **Python (Flask)**, **HTML5**, **CSS3**, and **Vanilla JavaScript**.

StockWise is designed for supermarkets, grocery stores, pharmacies, and convenience shops to solve the everyday challenges of inventory management:
1. **Stock Intake**: Enter incoming deliveries with purchase cost, batch lot numbers, supplier details, and specific expiry dates.
2. **Daily Sales & Revenue**: Real-time sales turnover, today's order counts, and cash intake.
3. **True Profit vs. Loss**: Gross Margin (`Sales Revenue − Cost of Goods Sold`) minus recorded `Wastage & Damage Losses` to calculate **Net Store Earnings**.
4. **Product Expiry Days Countdown**: Exact live shelf-life countdown for every batch (`Expires in 1 day`, `Expires in 3 days`, `Expired 3 days ago`), with 50% discount clearance markdown recommendations and 1-click disposal.
5. **Fast-Moving vs. Slow-Moving Analytics**: High turnover bestsellers driving profits vs. stagnant items tying up working capital.
6. **Restock Alerts & 1-Click Reorders**: Low-stock items below safety reorder levels with 1-click Purchase Order generation.

---

## Installation

To install all dependencies required by StockWise, run:

```bash
pip install -r requirements.txt
```

Or using Poetry:

```bash
poetry install
```

---

## Build

To compile and verify all production domain services:

```bash
python StockWise/build_app_code.py
```

Or using npm / Makefile:

```bash
npm run build
# OR
make build
```

---

## Run

To launch the application server:

```bash
python main.py
```

Or using Makefile / Docker:

```bash
make run
# OR
docker build -t stockwise:latest .
docker run -p 5000:5000 stockwise:latest
```

The web application will be live at:
👉 **http://127.0.0.1:5000**

---

## Testing

Execute the comprehensive automated test suite:

```bash
python -m unittest discover -s StockWise/tests -p "test_*.py"
```

Or using npm / Makefile:

```bash
npm test
# OR
make test
```

---

## Pre-Seeded Demo Accounts

You can log in directly using the credentials below, or click any role in the **Top Role Switcher** on the website header:

| Role | Username | Password | Responsibilities |
|---|---|---|---|
| **Business Owner** | `owner` | `owner123` | Executive Command Center: Daily sales, profit vs. loss, inventory valuation, fast/slow products, and restock alerts |
| **Inventory Manager** | `manager` | `manager123` | Stock batches, clearance markdowns, suppliers directory, and purchase orders |
| **Store Employee (Cashier)** | `employee` | `employee123` | Smart POS Cashier Terminal (FEFO), incoming delivery intake, and damage reporting |

---

## Key Features

- **FEFO (First Expired, First Out) Allocation**: Automated FIFO/FEFO sale allocation engine ensures oldest non-expired batches sell first.
- **Daily Profit & Loss Ledger**: Day-by-day financial accounting of gross sales, COGS, wastage write-offs, and net bottom-line earnings.
- **Zero Database Requirement**: High-concurrency atomic JSON flat-file storage with process-safe re-entrant file locking (`threading.RLock`).
- **Responsive Top Menubar & Warm Light Brown Theme**: Polished retail interface with instant on-the-fly theme switching.
- **CSV Data Exports**: One-click downloads for Daily P&L, customer transactions, inventory valuation, and waste audit trails.

---

## Contributors & Engineering Team

| Contributor | Role | Contact Email | PRs Authored | PRs Merged | Total Commits |
|---|---|---|:---:|:---:|:---:|
| **Radhika Thiriveedhi** | Lead Architect | `radhikathiriveedhi@gmail.com` | 40 | 40 | 81 |
| **Ramya Sri** | Core Systems Engineer | `guntupalliramyasri@gmail.com` | 40 | 40 | 81 |
| **Phani** | Enterprise Services Engineer | `23471a4392@gmail.com` | 40 | 40 | 81 |
| **Total** | **Collaborative Engineering Team** | — | **120** | **120** | **243** |

