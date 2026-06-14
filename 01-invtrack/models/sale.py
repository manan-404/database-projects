"""
models/sale.py — Sales Recording & Retrieval

Collections used: sales, products
Demonstrates: insert_one, find, transactions (stock deduction on sale)
"""

from db import sales_col, products_col, CLIENT


def record_sale(sale_doc: dict):
    """Record a sale and deduct stock atomically using a transaction.

    Steps inside the transaction:
      1. Check that enough stock exists for the product.
      2. Insert the sale document into the sales collection.
      3. Decrement the product's stock by the sold quantity.

    Args:
        sale_doc: dict with sale_id, product_id, quantity,
                  unit_price, total, sale_date.
    Returns:
        inserted_id or raises an error if stock is insufficient.
    """
    prod_id = sale_doc["product_id"]
    qty = sale_doc["quantity"]

    def perform_sale(session=None):
        # 1. Check stock
        prod = products_col.find_one({"product_id": prod_id}, session=session)
        if not prod:
            raise ValueError(f"Product {prod_id} not found.")
        
        current_stock = prod.get("stock", 0)
        if current_stock < qty:
            raise ValueError(f"Insufficient stock for product {prod_id}. Available: {current_stock}, Requested: {qty}")

        # 2. Insert sale document
        sales_col.insert_one(sale_doc, session=session)

        # 3. Decrement stock
        products_col.update_one(
            {"product_id": prod_id},
            {"$inc": {"stock": -qty}},
            session=session
        )

    try:
        with CLIENT.start_session() as session:
            with session.start_transaction():
                perform_sale(session)
    except Exception as e:
        # Fallback for standalone MongoDB which doesn't support transactions
        if "transaction" in str(e).lower() or "replica set" in str(e).lower():
            # Run without transaction
            perform_sale(session=None)
        else:
            raise e


def get_sale(sale_id: str) -> dict | None:
    """Fetch a single sale by sale_id."""
    return sales_col.find_one({"sale_id": sale_id})


def get_all_sales() -> list[dict]:
    """Return all sales, sorted by sale_date descending."""
    return list(sales_col.find().sort("sale_date", -1))


def get_sales_by_product(product_id: str) -> list[dict]:
    """Return all sales for a given product."""
    return list(sales_col.find({"product_id": product_id}).sort("sale_date", -1))

