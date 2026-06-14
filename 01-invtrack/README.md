# InvTrack — Inventory Management System

> **Course Project — Advanced Database Management Systems (ADBMS)**

## Authors

| Name             | CMS-ID        |
|------------------|---------------|
| Muhammad Tayyab  | 023-24-0118   |
| Abdul Manan      | 023-24-0149   |
| Uzair Ali        | 023-24-0147   |

---

## Overview

**InvTrack** is a command-line inventory management system built with **Python** and **MongoDB**. It tracks products, stock levels, suppliers, purchase orders, and sales — all from a simple terminal interface.

MongoDB is chosen because product catalogs naturally have **variable attributes** (e.g., electronics have `wattage` and `warranty_months` while clothing has `size` and `fabric`). A document-oriented database handles this schema flexibility without awkward NULLable columns.

### Key ADBMS Concepts Demonstrated

| Concept                | Where Used                                          |
|------------------------|-----------------------------------------------------|
| **CRUD Operations**    | Products, Suppliers, Purchase Orders, Sales         |
| **Aggregation Pipeline** | Revenue reports, category-wise stock, top sellers |
| **Indexing**           | Product ID, category, supplier fields               |
| **Transactions**       | Stock deduction on sale (atomic read-update)         |

---

## Project Structure

```
InvTrack/
├── README.md                # This file
├── requirements.txt         # Python dependencies (pymongo, numpy, pandas, etc.)
│
├── main.py                  # Entry point — CLI menu loop
├── db.py                    # MongoDB connection, database setup, index creation
│
├── models/                  # Data-access layer (one file per collection)
│   ├── __init__.py
│   ├── product.py           # Product CRUD operations
│   ├── supplier.py          # Supplier CRUD operations
│   ├── order.py             # Purchase order operations
│   └── sale.py              # Sales recording & retrieval
│
├── services/                # Business logic & reporting
│   ├── __init__.py
│   ├── inventory.py         # Stock management, low-stock alerts
│   ├── reports.py           # Aggregation-pipeline-based reports & charts
│   └── seed.py              # Seed database with hardcoded products + random data
│
└── utils/                   # Shared helpers
    ├── __init__.py
    └── helpers.py            # CLI formatting, input validation, table printing
```

---

## Tech Stack

| Layer        | Technology                                 |
|--------------|--------------------------------------------|
| Language     | Python 3.10+                               |
| Database     | MongoDB 6+ (local instance)                |
| Driver       | `pymongo`                                  |
| Data/Math    | `numpy`, `pandas`                          |
| Visualization| `matplotlib`, `seaborn`                    |

---

## Prerequisites

1. **MongoDB** installed and running locally on the default port (`27017`).
   - Ubuntu/Debian: `sudo systemctl start mongod`
   - macOS (Homebrew): `brew services start mongodb-community`
   - Windows: Start the MongoDB service from Services panel.

2. **Python 3.10+** installed.

---

## Installation

```bash
# Clone / navigate to the project
cd InvTrack

# Install dependencies (no virtual environment needed)
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py
```

This launches the interactive CLI menu:

```
╔══════════════════════════════════════╗
║        InvTrack — Main Menu         ║
╠══════════════════════════════════════╣
║  1. Product Management              ║
║  2. Supplier Management             ║
║  3. Purchase Orders                 ║
║  4. Record a Sale                   ║
║  5. Low-Stock Alerts                ║
║  6. Reports & Analytics             ║
║  7. Seed / Reset Database           ║
║  0. Exit                            ║
╚══════════════════════════════════════╝
```

---

## MongoDB Collections

### `products`
```json
{
  "_id": ObjectId,
  "product_id": "PRD-001",
  "name": "Wireless Mouse",
  "category": "Electronics",
  "price": 29.99,
  "stock": 150,
  "reorder_level": 20,
  "supplier_id": "SUP-001",
  "attributes": { "wireless": true, "battery": "AA", "warranty_months": 12 }
}
```

### `suppliers`
```json
{
  "_id": ObjectId,
  "supplier_id": "SUP-001",
  "name": "TechParts Co.",
  "contact": "info@techparts.com",
  "phone": "+92-300-1234567",
  "address": "Islamabad, Pakistan"
}
```

### `orders` (Purchase Orders)
```json
{
  "_id": ObjectId,
  "order_id": "ORD-001",
  "supplier_id": "SUP-001",
  "items": [
    { "product_id": "PRD-001", "quantity": 100, "unit_cost": 18.50 }
  ],
  "total_cost": 1850.00,
  "status": "received",
  "order_date": ISODate,
  "received_date": ISODate
}
```

### `sales`
```json
{
  "_id": ObjectId,
  "sale_id": "SAL-001",
  "product_id": "PRD-001",
  "quantity": 2,
  "unit_price": 29.99,
  "total": 59.98,
  "sale_date": ISODate
}
```

---

## Aggregation Pipelines Used

| Report                        | Pipeline Stages                                      |
|-------------------------------|------------------------------------------------------|
| Revenue by Category           | `$lookup` → `$group` → `$sort`                      |
| Top 5 Selling Products        | `$group` → `$sort` → `$limit`                       |
| Stock Valuation per Category  | `$group` (sum of `price × stock`) → `$sort`          |
| Monthly Sales Trend           | `$project` (extract month) → `$group` → `$sort`     |
| Supplier Order Summary        | `$unwind` → `$group` → `$lookup` → `$project`       |

---

## Indexes Created

```python
products.create_index("product_id", unique=True)
products.create_index("category")
suppliers.create_index("supplier_id", unique=True)
sales.create_index("product_id")
sales.create_index("sale_date")
orders.create_index("order_id", unique=True)
```

---

## License

This project is developed for academic purposes as part of the ADBMS course.
