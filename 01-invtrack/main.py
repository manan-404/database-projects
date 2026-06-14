import sys
from datetime import datetime

from db import setup_indexes
from models.product import (
    add_product, get_product, get_all_products, get_products_by_category,
    update_product, delete_product, search_products
)
from models.supplier import (
    add_supplier, get_supplier, get_all_suppliers, update_supplier, delete_supplier
)
from models.order import (
    create_order, get_order, get_all_orders, receive_order
)
from models.sale import (
    record_sale, get_all_sales
)
from services.inventory import (
    get_low_stock_products, get_stock_summary
)
from services.reports import (
    revenue_by_category, top_selling_products, monthly_sales_trend,
    stock_valuation_report, supplier_order_summary
)
from services.seed import seed_database
from utils.helpers import (
    print_header, print_table, input_int, input_float, confirm
)

BANNER = r"""
╔══════════════════════════════════════╗
║   InvTrack — Inventory Management   ║
║          ADBMS Course Project        ║
╠══════════════════════════════════════╣
║  Muhammad Tayyab    023-24-0118     ║
║  Abdul Manan        023-24-0149     ║
║  Uzair Ali          023-24-0147     ║
╚══════════════════════════════════════╝
"""

MAIN_MENU = """
  1. Product Management
  2. Supplier Management
  3. Purchase Orders
  4. Record a Sale
  5. Low-Stock Alerts
  6. Reports & Analytics
  7. Seed / Reset Database
  0. Exit
"""


def product_menu():
    while True:
        print_header("Product Management")
        print("  1. List All Products")
        print("  2. Search / View Product")
        print("  3. Add New Product")
        print("  4. Update Product")
        print("  5. Delete Product")
        print("  0. Back to Main Menu")
        
        choice = input("\n  ▸ Enter choice: ").strip()
        
        if choice == "1":
            products = get_all_products()
            print_table(products, ["product_id", "name", "category", "price", "stock", "reorder_level"])
        
        elif choice == "2":
            q = input("  ▸ Enter product ID or name to search: ").strip()
            if not q:
                continue
            prods = search_products(q)
            single = get_product(q)
            if single and single not in prods:
                prods.append(single)
            
            if not prods:
                print("  ✗ No products found matching that query.")
            elif len(prods) == 1:
                p = prods[0]
                print(f"\n  Product Details for: {p['product_id']}")
                print(f"  Name:          {p['name']}")
                print(f"  Category:      {p['category']}")
                print(f"  Price:         ${p['price']:.2f}")
                print(f"  Stock Level:   {p['stock']}")
                print(f"  Reorder Level: {p['reorder_level']}")
                print(f"  Supplier ID:   {p['supplier_id']}")
                print("  Attributes:")
                for k, v in p.get("attributes", {}).items():
                    print(f"    - {k}: {v}")
                print()
            else:
                print_table(prods, ["product_id", "name", "category", "price", "stock"])
        
        elif choice == "3":
            print("\n  [Add New Product]")
            pid = input("  ▸ Product ID (e.g. PRD-100): ").strip()
            if not pid:
                print("  ✗ Product ID is required.")
                continue
            if get_product(pid):
                print(f"  ✗ Product ID {pid} already exists.")
                continue
            
            name = input("  ▸ Name: ").strip()
            category = input("  ▸ Category: ").strip()
            price = input_float("  ▸ Price ($)", 0.0)
            stock = input_int("  ▸ Initial Stock", 0)
            reorder_level = input_int("  ▸ Reorder Level", 10)
            
            # List suppliers
            sups = get_all_suppliers()
            if not sups:
                print("  ✗ No suppliers found. Please add a supplier first.")
                continue
            print("\n  Available Suppliers:")
            print_table(sups, ["supplier_id", "name"])
            sid = input("  ▸ Supplier ID: ").strip()
            if not get_supplier(sid):
                print(f"  ✗ Supplier {sid} does not exist.")
                continue
            
            # Dynamic attributes
            attrs = {}
            print("  ▸ Enter variable attributes (key: value). Leave key empty to finish:")
            while True:
                key = input("    Key: ").strip()
                if not key:
                    break
                val_raw = input("    Value: ").strip()
                # Try parsing as bool, int, float, or fallback to string
                if val_raw.lower() in ('true', 'yes'):
                    val = True
                elif val_raw.lower() in ('false', 'no'):
                    val = False
                elif val_raw.isdigit():
                    val = int(val_raw)
                else:
                    try:
                        val = float(val_raw)
                    except ValueError:
                        val = val_raw
                attrs[key] = val
            
            doc = {
                "product_id": pid,
                "name": name,
                "category": category,
                "price": price,
                "stock": stock,
                "reorder_level": reorder_level,
                "supplier_id": sid,
                "attributes": attrs
            }
            add_product(doc)
            print(f"\n  ✔ Product {pid} successfully added!")
            
        elif choice == "4":
            pid = input("  ▸ Enter Product ID to update: ").strip()
            prod = get_product(pid)
            if not prod:
                print(f"  ✗ Product {pid} not found.")
                continue
            
            print(f"  Updating product {pid} ({prod['name']}). Press Enter to keep current values:")
            name = input(f"  ▸ Name [{prod['name']}]: ").strip() or prod['name']
            price = input_float(f"  ▸ Price [{prod['price']}]", prod['price'])
            stock = input_int(f"  ▸ Stock [{prod['stock']}]", prod['stock'])
            reorder = input_int(f"  ▸ Reorder Level [{prod['reorder_level']}]", prod['reorder_level'])
            
            updates = {
                "name": name,
                "price": price,
                "stock": stock,
                "reorder_level": reorder
            }
            
            if confirm("  ▸ Update attributes?"):
                attrs = prod.get("attributes", {})
                print("  ▸ Enter key:value to add/update, or key with empty value to delete. Empty key to finish:")
                while True:
                    key = input("    Key: ").strip()
                    if not key:
                        break
                    val_raw = input("    Value: ").strip()
                    if not val_raw:
                        attrs.pop(key, None)
                    else:
                        if val_raw.lower() in ('true', 'yes'):
                            val = True
                        elif val_raw.lower() in ('false', 'no'):
                            val = False
                        elif val_raw.isdigit():
                            val = int(val_raw)
                        else:
                            try:
                                val = float(val_raw)
                            except ValueError:
                                val = val_raw
                        attrs[key] = val
                updates["attributes"] = attrs
                
            update_product(pid, updates)
            print(f"\n  ✔ Product {pid} successfully updated!")
            
        elif choice == "5":
            pid = input("  ▸ Enter Product ID to delete: ").strip()
            if not get_product(pid):
                print(f"  ✗ Product {pid} not found.")
                continue
            if confirm(f"  ⚠ Are you sure you want to delete product {pid}?"):
                delete_product(pid)
                print(f"  ✔ Product {pid} deleted.")
                
        elif choice == "0":
            break


def supplier_menu():
    while True:
        print_header("Supplier Management")
        print("  1. List All Suppliers")
        print("  2. Add New Supplier")
        print("  3. Update Supplier")
        print("  4. Delete Supplier")
        print("  0. Back to Main Menu")
        
        choice = input("\n  ▸ Enter choice: ").strip()
        
        if choice == "1":
            sups = get_all_suppliers()
            print_table(sups, ["supplier_id", "name", "contact", "phone", "address"])
            
        elif choice == "2":
            print("\n  [Add New Supplier]")
            sid = input("  ▸ Supplier ID (e.g. SUP-100): ").strip()
            if not sid:
                print("  ✗ Supplier ID required.")
                continue
            if get_supplier(sid):
                print(f"  ✗ Supplier {sid} already exists.")
                continue
            name = input("  ▸ Name: ").strip()
            contact = input("  ▸ Contact Email: ").strip()
            phone = input("  ▸ Phone: ").strip()
            address = input("  ▸ Address: ").strip()
            
            doc = {
                "supplier_id": sid,
                "name": name,
                "contact": contact,
                "phone": phone,
                "address": address
            }
            add_supplier(doc)
            print(f"\n  ✔ Supplier {sid} added successfully!")
            
        elif choice == "3":
            sid = input("  ▸ Enter Supplier ID to update: ").strip()
            sup = get_supplier(sid)
            if not sup:
                print(f"  ✗ Supplier {sid} not found.")
                continue
            
            print(f"  Updating Supplier {sid}. Press Enter to keep current values:")
            name = input(f"  ▸ Name [{sup['name']}]: ").strip() or sup['name']
            contact = input(f"  ▸ Contact [{sup['contact']}]: ").strip() or sup['contact']
            phone = input(f"  ▸ Phone [{sup['phone']}]: ").strip() or sup['phone']
            address = input(f"  ▸ Address [{sup['address']}]: ").strip() or sup['address']
            
            updates = {
                "name": name,
                "contact": contact,
                "phone": phone,
                "address": address
            }
            update_supplier(sid, updates)
            print(f"\n  ✔ Supplier {sid} updated successfully!")
            
        elif choice == "4":
            sid = input("  ▸ Enter Supplier ID to delete: ").strip()
            if not get_supplier(sid):
                print(f"  ✗ Supplier {sid} not found.")
                continue
            if confirm(f"  ⚠ Are you sure you want to delete supplier {sid}?"):
                delete_supplier(sid)
                print(f"  ✔ Supplier {sid} deleted.")
                
        elif choice == "0":
            break


def order_menu():
    while True:
        print_header("Purchase Orders")
        print("  1. List All Orders")
        print("  2. Place Purchase Order")
        print("  3. Receive Purchase Order")
        print("  0. Back to Main Menu")
        
        choice = input("\n  ▸ Enter choice: ").strip()
        
        if choice == "1":
            orders = get_all_orders()
            # Flatten or format display
            display_rows = []
            for o in orders:
                display_rows.append({
                    "order_id": o["order_id"],
                    "supplier_id": o["supplier_id"],
                    "total_cost": f"${o['total_cost']:.2f}",
                    "status": o["status"],
                    "order_date": o["order_date"].strftime("%Y-%m-%d %H:%M") if "order_date" in o else ""
                })
            print_table(display_rows, ["order_id", "supplier_id", "total_cost", "status", "order_date"])
            
        elif choice == "2":
            print("\n  [Place Purchase Order]")
            # Generate next order ID
            existing = get_all_orders()
            if existing:
                try:
                    nums = [int(o["order_id"].split("-")[1]) for o in existing if "-" in o["order_id"]]
                    next_num = max(nums) + 1
                except:
                    next_num = len(existing) + 1
            else:
                next_num = 1
            oid = f"ORD-{next_num:03d}"
            
            sups = get_all_suppliers()
            if not sups:
                print("  ✗ No suppliers available.")
                continue
            print("\n  Select Supplier:")
            print_table(sups, ["supplier_id", "name"])
            sid = input("  ▸ Supplier ID: ").strip()
            if not get_supplier(sid):
                print(f"  ✗ Supplier {sid} not found.")
                continue
                
            items = []
            total_cost = 0.0
            print("  ▸ Add items to purchase order:")
            while True:
                pid = input("    Product ID: ").strip()
                prod = get_product(pid)
                if not prod:
                    print("    ✗ Product not found.")
                    continue
                if prod["supplier_id"] != sid:
                    print(f"    ⚠ Warning: This product's primary supplier is {prod['supplier_id']}, not {sid}.")
                
                qty = input_int("    Quantity")
                cost = input_float("    Unit Cost ($)")
                
                items.append({
                    "product_id": pid,
                    "quantity": qty,
                    "unit_cost": cost
                })
                total_cost += qty * cost
                
                if not confirm("    Add another item?"):
                    break
            
            doc = {
                "order_id": oid,
                "supplier_id": sid,
                "items": items,
                "total_cost": round(total_cost, 2),
                "status": "pending",
                "order_date": datetime.now()
            }
            create_order(doc)
            print(f"\n  ✔ Purchase Order {oid} placed successfully (Pending receipt)!")
            
        elif choice == "3":
            oid = input("  ▸ Enter Purchase Order ID to receive: ").strip()
            order = get_order(oid)
            if not order:
                print(f"  ✗ Order {oid} not found.")
                continue
            
            if order.get("status") == "received":
                print(f"  ✗ Order {oid} is already marked as received.")
                continue
                
            print(f"\n  Order Details for {oid}:")
            print(f"  Supplier:   {order['supplier_id']}")
            print(f"  Total Cost: ${order['total_cost']:.2f}")
            print("  Items:")
            for item in order.get("items", []):
                print(f"    - {item['product_id']}: Quantity {item['quantity']} @ ${item['unit_cost']:.2f}")
            print()
            
            if confirm("  Confirm receiving this order? (Stock will be incremented)"):
                try:
                    receive_order(oid)
                    print(f"  ✔ Order {oid} marked received. Stock updated successfully!")
                except Exception as e:
                    print(f"  ✗ Transaction failed: {e}")
                    
        elif choice == "0":
            break


def record_sale_flow():
    print_header("Record a Sale")
    # Generate sale ID
    existing = get_all_sales()
    if existing:
        try:
            nums = [int(s["sale_id"].split("-")[1]) for s in existing if "-" in s["sale_id"]]
            next_num = max(nums) + 1
        except:
            next_num = len(existing) + 1
    else:
        next_num = 1
    sid = f"SAL-{next_num:03d}"

    pid = input("  ▸ Product ID: ").strip()
    prod = get_product(pid)
    if not prod:
        print(f"  ✗ Product {pid} not found.")
        return
    
    print(f"  Product: {prod['name']} | Stock Available: {prod['stock']} | Unit Price: ${prod['price']:.2f}")
    qty = input_int("  ▸ Quantity to sell")
    if qty <= 0:
        print("  ✗ Quantity must be greater than zero.")
        return
        
    if prod['stock'] < qty:
        print(f"  ✗ Insufficient stock. Only {prod['stock']} available.")
        return
        
    total = round(qty * prod['price'], 2)
    print(f"  Total Sale Value: ${total:.2f}")
    if confirm("  Confirm transaction?"):
        sale_doc = {
            "sale_id": sid,
            "product_id": pid,
            "quantity": qty,
            "unit_price": prod['price'],
            "total": total,
            "sale_date": datetime.now()
        }
        try:
            record_sale(sale_doc)
            print(f"  ✔ Sale {sid} recorded. Stock decremented successfully!")
        except Exception as e:
            print(f"  ✗ Transaction failed: {e}")


def low_stock_alerts_flow():
    print_header("Low-Stock Alerts")
    print("  1. Use product reorder levels (default)")
    print("  2. Specify custom threshold level")
    
    choice = input("\n  ▸ Enter choice: ").strip()
    threshold = None
    if choice == "2":
        threshold = input_int("  ▸ Custom threshold quantity")
        
    alerts = get_low_stock_products(threshold)
    if not alerts:
        print("  ✔ No low stock alerts. All inventory levels healthy!")
    else:
        print_table(alerts, ["product_id", "name", "stock", "reorder_level"], ["Product ID", "Product Name", "Current Stock", "Reorder Level"])


def reports_menu():
    while True:
        print_header("Reports & Analytics (Aggregation pipelines)")
        print("  1. Revenue by Product Category")
        print("  2. Top 5 Selling Products")
        print("  3. Stock Valuation per Category")
        print("  4. Monthly Sales Revenue Trend")
        print("  5. Supplier Orders & Spending Summary")
        print("  0. Back to Main Menu")
        
        choice = input("\n  ▸ Enter choice: ").strip()
        
        if choice == "1":
            print("\n  [Running Revenue by Category Aggregation...]")
            df = revenue_by_category()
            if df.empty:
                print("  (No sales data to generate report)")
            else:
                rows = df.to_dict('records')
                print_table(rows, ["category", "total_revenue"], ["Category", "Total Revenue ($)"])
                
        elif choice == "2":
            n = input_int("  ▸ Number of top products to fetch", 5)
            print(f"\n  [Running Top Selling Products Aggregation...]")
            df = top_selling_products(n)
            if df.empty:
                print("  (No sales data to generate report)")
            else:
                rows = df.to_dict('records')
                print_table(rows, ["product_id", "name", "total_sold"], ["Product ID", "Name", "Total Units Sold"])
                
        elif choice == "3":
            print("\n  [Running Stock Valuation Aggregation...]")
            df = stock_valuation_report()
            if df.empty:
                print("  (No product/stock data to generate report)")
            else:
                rows = df.to_dict('records')
                print_table(rows, ["category", "total_value"], ["Category", "Total Valuation ($)"])
                
        elif choice == "4":
            print("\n  [Running Monthly Sales Trend Aggregation...]")
            df = monthly_sales_trend()
            if df.empty:
                print("  (No sales data to generate report)")
            else:
                rows = df.to_dict('records')
                print_table(rows, ["month", "total_revenue"], ["Month (YYYY-MM)", "Total Revenue ($)"])
                
        elif choice == "5":
            print("\n  [Running Supplier Order Summary Aggregation...]")
            df = supplier_order_summary()
            if df.empty:
                print("  (No purchase order data to generate report)")
            else:
                rows = df.to_dict('records')
                print_table(rows, ["supplier_id", "supplier_name", "total_orders", "total_spent"], ["Supplier ID", "Supplier Name", "Total Orders", "Total Spent ($)"])
                
        elif choice == "0":
            break


def main():
    """Main loop — display menu, read choice, dispatch."""
    try:
        setup_indexes()
    except Exception as e:
        print(f"  ⚠ Warning connecting/indexing database: {e}")
        print("  Make sure MongoDB is running locally on port 27017.")
        
    print(BANNER)

    while True:
        print(MAIN_MENU)
        choice = input("  ▸ Enter choice: ").strip()

        if choice == "1":
            product_menu()
        elif choice == "2":
            supplier_menu()
        elif choice == "3":
            order_menu()
        elif choice == "4":
            record_sale_flow()
        elif choice == "5":
            low_stock_alerts_flow()
        elif choice == "6":
            reports_menu()
        elif choice == "7":
            if confirm("  ⚠ This will delete all collections and generate random fresh data. Proceed?"):
                seed_database()
        elif choice == "0":
            print("\n  Goodbye!\n")
            sys.exit(0)
        else:
            print("  ✗ Invalid choice. Try again.")


if __name__ == "__main__":
    main()

