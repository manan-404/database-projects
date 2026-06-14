"""
db.py — MongoDB Connection & Setup

Handles:
  - Connecting to the local MongoDB instance
  - Returning database and collection handles
  - Creating indexes for performance
"""

from pymongo import MongoClient, ASCENDING

# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------
CLIENT = MongoClient("mongodb://localhost:27017/")
DB = CLIENT["invtrack"]

# ---------------------------------------------------------------------------
# Collection handles
# ---------------------------------------------------------------------------
products_col   = DB["products"]
suppliers_col  = DB["suppliers"]
orders_col     = DB["orders"]
sales_col      = DB["sales"]


def setup_indexes():
    """Create indexes on frequently queried fields.

    Called once at application startup (main.py).
    MongoDB silently skips if the index already exists.
    """
    products_col.create_index([("product_id", ASCENDING)], unique=True)
    products_col.create_index([("category", ASCENDING)])
    suppliers_col.create_index([("supplier_id", ASCENDING)], unique=True)
    orders_col.create_index([("order_id", ASCENDING)], unique=True)
    sales_col.create_index([("product_id", ASCENDING)])
    sales_col.create_index([("sale_date", ASCENDING)])


def drop_all():
    """Drop every collection — used by the seed/reset flow."""
    products_col.drop()
    suppliers_col.drop()
    orders_col.drop()
    sales_col.drop()

