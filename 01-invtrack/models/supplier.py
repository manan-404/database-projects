"""
models/supplier.py — Supplier CRUD Operations

Collections used: suppliers
Demonstrates: insert_one, find, find_one, update_one, delete_one
"""

from db import suppliers_col


def add_supplier(supplier_doc: dict):
    """Insert a new supplier document.

    Args:
        supplier_doc: dict with supplier_id, name, contact, phone, address.
    Returns:
        inserted_id.
    """
    res = suppliers_col.insert_one(supplier_doc)
    return res.inserted_id


def get_supplier(supplier_id: str) -> dict | None:
    """Fetch a single supplier by supplier_id."""
    return suppliers_col.find_one({"supplier_id": supplier_id})


def get_all_suppliers() -> list[dict]:
    """Return all suppliers, sorted by supplier_id."""
    return list(suppliers_col.find().sort("supplier_id", 1))


def update_supplier(supplier_id: str, updates: dict):
    """Update fields of an existing supplier.

    Returns:
        modified_count.
    """
    res = suppliers_col.update_one({"supplier_id": supplier_id}, {"$set": updates})
    return res.modified_count


def delete_supplier(supplier_id: str):
    """Delete a supplier by supplier_id.

    Returns:
        deleted_count.
    """
    res = suppliers_col.delete_one({"supplier_id": supplier_id})
    return res.deleted_count

