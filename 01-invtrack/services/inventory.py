"""
services/inventory.py — Stock Management & Low-Stock Alerts

Handles business logic around stock levels that sits above
the raw CRUD layer in models/.
"""

from db import products_col


def get_low_stock_products(threshold: int = None) -> list[dict]:
    """Return products whose stock is at or below their reorder_level.

    If threshold is given, use it instead of each product's own
    reorder_level (i.e. stock <= threshold).

    Uses an aggregation pipeline with $match and $project.

    Returns:
        List of dicts with product_id, name, stock, reorder_level.
    """
    if threshold is not None:
        match_stage = {"$match": {"stock": {"$lte": threshold}}}
    else:
        match_stage = {"$match": {"$expr": {"$lte": ["$stock", "$reorder_level"]}}}

    pipeline = [
        match_stage,
        {"$project": {"_id": 0, "product_id": 1, "name": 1, "stock": 1, "reorder_level": 1}},
        {"$sort": {"stock": 1}}
    ]
    return list(products_col.aggregate(pipeline))


def update_stock(product_id: str, quantity_change: int):
    """Increment (or decrement) a product's stock by quantity_change.

    Args:
        product_id:      e.g. "PRD-001"
        quantity_change:  positive to add stock, negative to deduct.
    Returns:
        modified_count.
    """
    res = products_col.update_one({"product_id": product_id}, {"$inc": {"stock": quantity_change}})
    return res.modified_count


def get_stock_summary() -> list[dict]:
    """Aggregate total stock and valuation grouped by category.

    Pipeline:
        $group by category → sum stock, sum (price * stock)
        $sort by category

    Returns:
        List of {category, total_items, total_value}.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "total_items": {"$sum": "$stock"},
                "total_value": {"$sum": {"$multiply": ["$price", "$stock"]}},
                "unique_products": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "category": "$_id",
                "total_items": 1,
                "total_value": {"$round": ["$total_value", 2]},
                "unique_products": 1
            }
        },
        {"$sort": {"category": 1}}
    ]
    return list(products_col.aggregate(pipeline))

