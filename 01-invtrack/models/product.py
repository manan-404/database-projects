"""
models/product.py — Product CRUD Operations

Collections used: products
Demonstrates: insert_one, find, find_one, update_one, delete_one
"""

from db import products_col


def add_product(product_doc: dict):
    """Insert a new product document into the products collection.

    Args:
        product_doc: dict with keys like product_id, name, category,
                     price, stock, reorder_level, supplier_id, attributes.
    Returns:
        The inserted_id.
    """
    res = products_col.insert_one(product_doc)
    return res.inserted_id


def get_product(product_id: str) -> dict | None:
    """Fetch a single product by its product_id.

    Args:
        product_id: e.g. "PRD-001"
    Returns:
        The product document or None.
    """
    return products_col.find_one({"product_id": product_id})


def get_all_products() -> list[dict]:
    """Return all products, sorted by product_id."""
    return list(products_col.find().sort("product_id", 1))


def get_products_by_category(category: str) -> list[dict]:
    """Return products filtered by category."""
    return list(products_col.find({"category": category}).sort("product_id", 1))


def update_product(product_id: str, updates: dict):
    """Update fields of an existing product.

    Args:
        product_id: the product to update.
        updates:    dict of fields to set, e.g. {"price": 39.99}.
    Returns:
        modified_count.
    """
    res = products_col.update_one({"product_id": product_id}, {"$set": updates})
    return res.modified_count


def delete_product(product_id: str):
    """Delete a product by product_id.

    Returns:
        deleted_count.
    """
    res = products_col.delete_one({"product_id": product_id})
    return res.deleted_count


def search_products(query: str) -> list[dict]:
    """Search products by name (case-insensitive regex match)."""
    return list(products_col.find({"name": {"$regex": query, "$options": "i"}}).sort("product_id", 1))

