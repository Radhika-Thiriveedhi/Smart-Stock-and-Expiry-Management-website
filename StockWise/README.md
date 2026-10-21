# StockWise — Smart Stock & Expiry Management

A practical, real-world retail inventory, expiry tracking, and financial intelligence web application built with **Python (Flask)**, **HTML5**, **CSS3**, and **Vanilla JavaScript**.

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
python build_app_code.py
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

The web application will be live at:
👉 **http://127.0.0.1:5000**

---

## Testing

Execute the comprehensive automated test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Or using npm / Makefile:

```bash
npm test
# OR
make test
```

---

## Pre-Seeded Demo Accounts

| Role | Username | Password | Responsibilities |
|---|---|---|---|
| **Business Owner** | `owner` | `owner123` | Executive Command Center: Daily sales, profit vs. loss, inventory valuation, fast/slow products, and restock alerts |
| **Inventory Manager** | `manager` | `manager123` | Stock batches, clearance markdowns, suppliers directory, and purchase orders |
| **Store Employee (Cashier)** | `employee` | `employee123` | Smart POS Cashier Terminal (FEFO), incoming delivery intake, and damage reporting |

---

## Contributors & Engineering Team

| Contributor | Role | Contact Email | PRs Authored | PRs Merged | Total Commits |
|---|---|---|:---:|:---:|:---:|
| **Radhika Thiriveedhi** | Lead Architect | `radhika.thiriveedhi@users.noreply.github.com` | 40 | 40 | 81 |
| **Ramya Sri** | Core Systems Engineer | `guntupalliramyasri@gmail.com` | 40 | 40 | 81 |
| **Phani** | Enterprise Services Engineer | `23471a4392@gmail.com` | 40 | 40 | 81 |
| **Total** | **Collaborative Engineering Team** | — | **120** | **120** | **243** |

