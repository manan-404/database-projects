"""
services/seed.py — Seed the Database with Hardcoded Products & Random Data

Uses numpy.random to generate realistic random stock levels,
prices, and sale quantities so the database has meaningful
data to query against from the start.
"""

import numpy as np
from datetime import datetime, timedelta

from db import drop_all, setup_indexes
from db import products_col, suppliers_col, orders_col, sales_col


# -----------------------------------------------------------------------
# Hardcoded product catalog — variable attributes per category
# -----------------------------------------------------------------------
PRODUCTS = [
    # Electronics
    {"product_id": "PRD-001", "name": "Wireless Mouse",       "category": "Electronics", "attributes": {"wireless": True,  "battery": "AA",  "warranty_months": 12}},
    {"product_id": "PRD-002", "name": "Mechanical Keyboard",  "category": "Electronics", "attributes": {"switch_type": "Cherry MX Blue", "backlit": True, "warranty_months": 24}},
    {"product_id": "PRD-003", "name": "USB-C Hub",            "category": "Electronics", "attributes": {"ports": 7, "power_delivery": True, "warranty_months": 12}},
    {"product_id": "PRD-004", "name": "27\" 4K Monitor",      "category": "Electronics", "attributes": {"resolution": "3840x2160", "panel": "IPS", "refresh_rate": 60}},
    {"product_id": "PRD-005", "name": "Noise-Cancelling Headphones", "category": "Electronics", "attributes": {"wireless": True, "anc": True, "battery_hours": 30}},

    # Clothing
    {"product_id": "PRD-006", "name": "Cotton T-Shirt",       "category": "Clothing",    "attributes": {"size": "M",  "fabric": "100% Cotton", "color": "Black"}},
    {"product_id": "PRD-007", "name": "Denim Jeans",          "category": "Clothing",    "attributes": {"size": "32", "fabric": "Denim",       "fit": "Slim"}},
    {"product_id": "PRD-008", "name": "Hoodie",               "category": "Clothing",    "attributes": {"size": "L",  "fabric": "Fleece",      "color": "Grey"}},

    # Stationery
    {"product_id": "PRD-009", "name": "Notebook A5",          "category": "Stationery",  "attributes": {"pages": 200, "ruling": "Lined",  "cover": "Hardbound"}},
    {"product_id": "PRD-010", "name": "Ballpoint Pen Pack",   "category": "Stationery",  "attributes": {"count": 10,  "ink": "Blue",      "type": "Retractable"}},

    # Grocery
    {"product_id": "PRD-011", "name": "Basmati Rice 5kg",     "category": "Grocery",     "attributes": {"weight_kg": 5, "origin": "Pakistan", "organic": False}},
    {"product_id": "PRD-012", "name": "Olive Oil 1L",         "category": "Grocery",     "attributes": {"volume_ml": 1000, "type": "Extra Virgin", "origin": "Spain"}},

    # Furniture
    {"product_id": "PRD-013", "name": "Office Chair",         "category": "Furniture",   "attributes": {"material": "Mesh", "adjustable": True, "weight_capacity_kg": 120}},
    {"product_id": "PRD-014", "name": "Standing Desk",        "category": "Furniture",   "attributes": {"width_cm": 120, "motorized": True,  "height_range": "72-120cm"}},
    {"product_id": "PRD-015", "name": "Bookshelf",            "category": "Furniture",   "attributes": {"shelves": 5, "material": "Wood", "color": "Walnut"}},
]

SUPPLIERS = [
    {"supplier_id": "SUP-001", "name": "TechParts Co.",      "contact": "info@techparts.com",   "phone": "+92-300-1234567", "address": "Islamabad, Pakistan"},
    {"supplier_id": "SUP-002", "name": "FashionHub",         "contact": "sales@fashionhub.pk",  "phone": "+92-321-9876543", "address": "Lahore, Pakistan"},
    {"supplier_id": "SUP-003", "name": "OfficeWorld",        "contact": "orders@officeworld.pk","phone": "+92-333-5551234", "address": "Karachi, Pakistan"},
    {"supplier_id": "SUP-004", "name": "GrocersMart",        "contact": "bulk@grocersmart.pk",  "phone": "+92-345-6789012", "address": "Rawalpindi, Pakistan"},
    {"supplier_id": "SUP-005", "name": "HomeComfort Ltd.",    "contact": "hello@homecomfort.pk", "phone": "+92-311-2223344", "address": "Faisalabad, Pakistan"},
]

# Map category → supplier for realistic linking
CATEGORY_SUPPLIER = {
    "Electronics": "SUP-001",
    "Clothing":    "SUP-002",
    "Stationery":  "SUP-003",
    "Grocery":     "SUP-004",
    "Furniture":   "SUP-005",
}


def seed_database():
    """Drop all collections and re-seed with fresh data.

    Steps:
      1. drop_all() — clear existing data.
      2. Insert suppliers.
      3. Insert products with random prices and stock (via np.random).
      4. Generate random purchase orders.
      5. Generate random sales history.
      6. Re-create indexes.
    """
    print("  ▸ Dropping existing collections...")
    drop_all()

    # 1. Insert suppliers
    print("  ▸ Seeding suppliers...")
    suppliers_col.insert_many(SUPPLIERS)

    # 2. Seed products with random price, stock, reorder level
    print("  ▸ Seeding products...")
    seeded_products = []
    # Seed generator for reproducibility or just use default
    np.random.seed(42)

    for prod in PRODUCTS:
        # Category specific pricing ranges
        category = prod["category"]
        if category == "Electronics":
            price = round(float(np.random.uniform(15.0, 600.0)), 2)
        elif category == "Clothing":
            price = round(float(np.random.uniform(10.0, 80.0)), 2)
        elif category == "Stationery":
            price = round(float(np.random.uniform(2.0, 25.0)), 2)
        elif category == "Grocery":
            price = round(float(np.random.uniform(3.0, 50.0)), 2)
        else: # Furniture
            price = round(float(np.random.uniform(50.0, 800.0)), 2)

        stock = int(np.random.randint(15, 120))
        reorder_level = int(np.random.randint(5, 20))
        
        prod_doc = {
            "product_id": prod["product_id"],
            "name": prod["name"],
            "category": category,
            "price": price,
            "stock": stock,
            "reorder_level": reorder_level,
            "supplier_id": CATEGORY_SUPPLIER[category],
            "attributes": prod["attributes"]
        }
        seeded_products.append(prod_doc)
    
    products_col.insert_many(seeded_products)

    # 3. Seeding Purchase Orders
    print("  ▸ Seeding purchase orders...")
    # Generate 8 orders spread over the last 60 days
    orders = []
    now = datetime.now()
    for i in range(1, 9):
        order_id = f"ORD-{i:03d}"
        # Pick a supplier
        sup = np.random.choice(SUPPLIERS)
        sup_id = sup["supplier_id"]
        # Find products of this supplier
        sup_products = [p for p in seeded_products if p["supplier_id"] == sup_id]
        if not sup_products:
            continue
        
        # Order 1 to 3 items
        num_items = np.random.randint(1, 4)
        chosen_items = np.random.choice(sup_products, size=num_items, replace=False)
        
        items_list = []
        total_cost = 0.0
        for p in chosen_items:
            qty = int(np.random.randint(10, 50))
            # Cost is typically 60-85% of retail price
            cost_factor = float(np.random.uniform(0.6, 0.85))
            unit_cost = round(p["price"] * cost_factor, 2)
            items_list.append({
                "product_id": p["product_id"],
                "quantity": qty,
                "unit_cost": unit_cost
            })
            total_cost += qty * unit_cost

        # Status: 75% received, 25% pending
        status = np.random.choice(["received", "pending"], p=[0.75, 0.25])
        order_days_ago = int(np.random.randint(5, 60))
        order_date = now - timedelta(days=order_days_ago)
        
        order_doc = {
            "order_id": order_id,
            "supplier_id": sup_id,
            "items": items_list,
            "total_cost": round(total_cost, 2),
            "status": status,
            "order_date": order_date
        }
        if status == "received":
            # received 2-4 days after order_date
            recv_days_later = int(np.random.randint(2, 5))
            order_doc["received_date"] = order_date + timedelta(days=recv_days_later)

        orders.append(order_doc)
    
    orders_col.insert_many(orders)

    # 4. Seeding Sales
    print("  ▸ Seeding sales history...")
    # Generate 50 sales over the last 30 days
    sales = []
    for i in range(1, 51):
        sale_id = f"SAL-{i:03d}"
        # Pick a random product
        p = np.random.choice(seeded_products)
        qty = int(np.random.randint(1, 6))
        unit_price = p["price"]
        total = round(qty * unit_price, 2)
        
        sale_days_ago = int(np.random.randint(0, 30))
        # Random hour/minute
        hours_ago = int(np.random.randint(0, 24))
        mins_ago = int(np.random.randint(0, 60))
        sale_date = now - timedelta(days=sale_days_ago, hours=hours_ago, minutes=mins_ago)

        sale_doc = {
            "sale_id": sale_id,
            "product_id": p["product_id"],
            "quantity": qty,
            "unit_price": unit_price,
            "total": total,
            "sale_date": sale_date
        }
        sales.append(sale_doc)

    sales_col.insert_many(sales)

    # 5. Setup indexes
    print("  ▸ Setting up database indexes...")
    setup_indexes()

    print("\n  ✔ Database seeded successfully!")

