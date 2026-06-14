"""
services/reports.py — Aggregation-Pipeline-Based Reports & Charts

Each function runs a MongoDB aggregation pipeline, converts the
results to a pandas DataFrame, and optionally renders a chart
with matplotlib / seaborn.
"""

import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless mode to prevent GUI block/errors
import matplotlib.pyplot as plt
import seaborn as sns

from db import sales_col, products_col, orders_col

PLOTS_DIR = "plots"


def ensure_plots_dir():
    """Ensure the plots directory exists."""
    if not os.path.exists(PLOTS_DIR):
        os.makedirs(PLOTS_DIR)


def revenue_by_category() -> pd.DataFrame:
    """Total revenue per product category.

    Pipeline:
        sales → $lookup products → $group by category → $sort

    Returns:
        DataFrame with columns [category, total_revenue].
    Also:
        Saves a seaborn barplot to plots/revenue_by_category.png.
    """
    pipeline = [
        {
            "$lookup": {
                "from": "products",
                "localField": "product_id",
                "foreignField": "product_id",
                "as": "product_info"
            }
        },
        {"$unwind": "$product_info"},
        {
            "$group": {
                "_id": "$product_info.category",
                "total_revenue": {"$sum": "$total"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "category": "$_id",
                "total_revenue": {"$round": ["$total_revenue", 2]}
            }
        },
        {"$sort": {"total_revenue": -1}}
    ]
    results = list(sales_col.aggregate(pipeline))
    df = pd.DataFrame(results)

    if not df.empty:
        ensure_plots_dir()
        plt.figure(figsize=(8, 5))
        sns.set_theme(style="whitegrid")
        ax = sns.barplot(x="category", y="total_revenue", data=df, hue="category", legend=False, palette="viridis")
        ax.set_title("Revenue by Category")
        ax.set_xlabel("Category")
        ax.set_ylabel("Total Revenue ($)")
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "revenue_by_category.png"))
        plt.close()
        print(f"\n  [Chart saved to: {PLOTS_DIR}/revenue_by_category.png]")

    return df


def top_selling_products(n: int = 5) -> pd.DataFrame:
    """Top N products by total quantity sold.

    Pipeline:
        sales → $group by product_id (sum qty) → $sort → $limit
        → $lookup products for name

    Returns:
        DataFrame with columns [product_id, name, total_sold].
    Also:
        Saves a seaborn barplot to plots/top_selling_products.png.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$product_id",
                "total_sold": {"$sum": "$quantity"}
            }
        },
        {"$sort": {"total_sold": -1}},
        {"$limit": n},
        {
            "$lookup": {
                "from": "products",
                "localField": "_id",
                "foreignField": "product_id",
                "as": "product_info"
            }
        },
        {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "product_id": "$_id",
                "name": {"$ifNull": ["$product_info.name", "Unknown Product"]},
                "total_sold": 1
            }
        }
    ]
    results = list(sales_col.aggregate(pipeline))
    df = pd.DataFrame(results)

    if not df.empty:
        ensure_plots_dir()
        plt.figure(figsize=(8, 5))
        sns.set_theme(style="whitegrid")
        ax = sns.barplot(x="total_sold", y="name", data=df, hue="name", legend=False, palette="plasma", orient="h")
        ax.set_title(f"Top {n} Selling Products")
        ax.set_xlabel("Total Quantity Sold")
        ax.set_ylabel("Product Name")
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "top_selling_products.png"))
        plt.close()
        print(f"  [Chart saved to: {PLOTS_DIR}/top_selling_products.png]")

    return df


def monthly_sales_trend() -> pd.DataFrame:
    """Total sales revenue grouped by month.

    Pipeline:
        sales → $project (extract year-month) → $group → $sort

    Returns:
        DataFrame with columns [month, total_revenue].
    Also:
        Saves a line chart to plots/monthly_sales_trend.png.
    """
    pipeline = [
        {
            "$project": {
                "month": {"$dateToString": {"format": "%Y-%m", "date": "$sale_date"}},
                "total": 1
            }
        },
        {
            "$group": {
                "_id": "$month",
                "total_revenue": {"$sum": "$total"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "month": "$_id",
                "total_revenue": {"$round": ["$total_revenue", 2]}
            }
        },
        {"$sort": {"month": 1}}
    ]
    results = list(sales_col.aggregate(pipeline))
    df = pd.DataFrame(results)

    if not df.empty:
        ensure_plots_dir()
        plt.figure(figsize=(8, 5))
        plt.plot(df["month"], df["total_revenue"], marker='o', color='b', linewidth=2)
        plt.title("Monthly Sales Trend")
        plt.xlabel("Month")
        plt.ylabel("Revenue ($)")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "monthly_sales_trend.png"))
        plt.close()
        print(f"  [Chart saved to: {PLOTS_DIR}/monthly_sales_trend.png]")

    return df


def stock_valuation_report() -> pd.DataFrame:
    """Stock value (price × stock) per category.

    Pipeline:
        products → $group by category → sum(price * stock)

    Returns:
        DataFrame with columns [category, total_value].
    Also:
        Saves a pie chart to plots/stock_valuation_report.png.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "total_value": {"$sum": {"$multiply": ["$price", "$stock"]}}
            }
        },
        {
            "$project": {
                "_id": 0,
                "category": "$_id",
                "total_value": {"$round": ["$total_value", 2]}
            }
        },
        {"$sort": {"total_value": -1}}
    ]
    results = list(products_col.aggregate(pipeline))
    df = pd.DataFrame(results)

    if not df.empty:
        ensure_plots_dir()
        plt.figure(figsize=(7, 7))
        colors = sns.color_palette("pastel")[0:len(df)]
        plt.pie(df["total_value"], labels=df["category"], autopct='%1.1f%%', startangle=140, colors=colors)
        plt.title("Stock Valuation by Category")
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "stock_valuation_report.png"))
        plt.close()
        print(f"  [Chart saved to: {PLOTS_DIR}/stock_valuation_report.png]")

    return df


def supplier_order_summary() -> pd.DataFrame:
    """Total orders and spending per supplier.

    Pipeline:
        orders → $group by supplier_id → $lookup suppliers → $project

    Returns:
        DataFrame with columns [supplier_id, supplier_name,
                                 total_orders, total_spent].
    """
    pipeline = [
        {
            "$group": {
                "_id": "$supplier_id",
                "total_orders": {"$sum": 1},
                "total_spent": {"$sum": "$total_cost"}
            }
        },
        {
            "$lookup": {
                "from": "suppliers",
                "localField": "_id",
                "foreignField": "supplier_id",
                "as": "supplier_info"
            }
        },
        {"$unwind": {"path": "$supplier_info", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "supplier_id": "$_id",
                "supplier_name": {"$ifNull": ["$supplier_info.name", "Unknown Supplier"]},
                "total_orders": 1,
                "total_spent": {"$round": ["$total_spent", 2]}
            }
        },
        {"$sort": {"total_spent": -1}}
    ]
    results = list(orders_col.aggregate(pipeline))
    df = pd.DataFrame(results)
    return df
