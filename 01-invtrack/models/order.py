"""
models/order.py — Purchase Order Operations

Collections used: orders, products
Demonstrates: insert_one, find, update_one, transactions (stock update on receive)
"""

from db import orders_col, products_col


from datetime import datetime
from db import CLIENT, orders_col, products_col


def create_order(order_doc: dict):
    """Insert a new purchase order.

    Args:
        order_doc: dict with order_id, supplier_id, items (list),
                   total_cost, status, order_date.
    Returns:
        inserted_id.
    """
    res = orders_col.insert_one(order_doc)
    return res.inserted_id


def get_order(order_id: str) -> dict | None:
    """Fetch a single order by order_id."""
    return orders_col.find_one({"order_id": order_id})


def get_all_orders() -> list[dict]:
    """Return all orders, sorted by order_date descending."""
    return list(orders_col.find().sort("order_date", -1))


def receive_order(order_id: str):
    """Mark an order as received and add quantities to product stock.

    This should use a MongoDB TRANSACTION to ensure atomicity:
      1. Update order status to 'received' and set received_date.
      2. For each item in the order, increment the product's stock.

    If any step fails, the entire operation rolls back.
    If MongoDB is standalone (no replica set), we fall back gracefully to a non-transactional execute.
    """
    order = get_order(order_id)
    if not order:
        raise ValueError(f"Order {order_id} not found.")
    
    if order.get("status") == "received":
        raise ValueError(f"Order {order_id} has already been received.")

    def perform_receive(session=None):
        # 1. Update order status
        orders_col.update_one(
            {"order_id": order_id},
            {"$set": {"status": "received", "received_date": datetime.now()}},
            session=session
        )
        # 2. Increment stock for each item
        for item in order.get("items", []):
            products_col.update_one(
                {"product_id": item["product_id"]},
                {"$inc": {"stock": item["quantity"]}},
                session=session
            )

    try:
        with CLIENT.start_session() as session:
            with session.start_transaction():
                perform_receive(session)
    except Exception as e:
        # Fallback for standalone MongoDB which doesn't support transactions
        if "transaction" in str(e).lower() or "replica set" in str(e).lower():
            # Run without transaction
            perform_receive(session=None)
        else:
            raise e


def update_order_status(order_id: str, new_status: str):
    """Update just the status field of an order."""
    res = orders_col.update_one({"order_id": order_id}, {"$set": {"status": new_status}})
    return res.modified_count

