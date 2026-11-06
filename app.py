"""
app.py
Enterprise-Grade Flask Web Application for Retail Sales Intelligence & Dashboard.
Includes Real-Time Category Configuration, Scenario Simulation, and Analytics.
"""

import os
import io
import csv
import random
import shutil
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
from sales_analyzer import RetailSalesAnalyzer
from dashboard import create_dashboard

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.abspath(__file__))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

DEFAULT_DATASET = "retail_sales_5000.csv" if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], "retail_sales_5000.csv")) else "retail_sales_data.csv"
CURRENT_DATASET = DEFAULT_DATASET
DATA_FILE = os.path.join(app.config['UPLOAD_FOLDER'], CURRENT_DATASET)
STATIC_DIR = os.path.join(app.config['UPLOAD_FOLDER'], "static")
STATIC_IMG = os.path.join(STATIC_DIR, "retail_sales_dashboard.png")

os.makedirs(STATIC_DIR, exist_ok=True)

# Global analyzer instance
analyzer = RetailSalesAnalyzer(DATA_FILE)

# Ensure static dashboard image exists
try:
    create_dashboard(csv_path=DATA_FILE, output_image=STATIC_IMG, show_plot=False)
    if os.path.exists(STATIC_IMG):
        shutil.copy(STATIC_IMG, "retail_sales_dashboard.png")
except Exception as e:
    print(f"Initial dashboard render note: {e}")

def refresh_dashboard_image():
    """Regenerates the 300 DPI Matplotlib image reflecting current category config."""
    try:
        create_dashboard(csv_path=DATA_FILE, output_image=STATIC_IMG, show_plot=False)
        if os.path.exists(STATIC_IMG):
            shutil.copy(STATIC_IMG, "retail_sales_dashboard.png")
    except Exception as e:
        print(f"Error refreshing dashboard image: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/datasets", methods=["GET"])
def get_datasets():
    datasets = []
    f5000 = os.path.join(app.config['UPLOAD_FOLDER'], "retail_sales_5000.csv")
    fdata = os.path.join(app.config['UPLOAD_FOLDER'], "retail_sales_data.csv")
    if os.path.exists(f5000):
        datasets.append({
            "id": "retail_sales_5000.csv",
            "name": "retail_sales_5000.csv (5,000 Rows - Excel Repo Dataset)",
            "active": CURRENT_DATASET == "retail_sales_5000.csv"
        })
    if os.path.exists(fdata):
        datasets.append({
            "id": "retail_sales_data.csv",
            "name": "retail_sales_data.csv (1,201 Rows - Sample Dataset)",
            "active": CURRENT_DATASET == "retail_sales_data.csv"
        })
    return jsonify({"current": CURRENT_DATASET, "datasets": datasets})

@app.route("/api/dataset/switch", methods=["POST"])
def switch_dataset():
    global CURRENT_DATASET, DATA_FILE, analyzer
    data = request.get_json(silent=True) or {}
    target = data.get("dataset", "retail_sales_5000.csv")
    target_path = os.path.join(app.config['UPLOAD_FOLDER'], target)
    if os.path.exists(target_path):
        CURRENT_DATASET = target
        DATA_FILE = target_path
        analyzer = RetailSalesAnalyzer(DATA_FILE)
        refresh_dashboard_image()
        return jsonify({"success": True, "dataset": CURRENT_DATASET, "records": len(analyzer.records)})
    return jsonify({"success": False, "error": f"Dataset file '{target}' not found"}), 404

@app.route("/api/metrics")
def get_metrics():
    category = request.args.get("category", "All")
    city = request.args.get("city", "All")
    period = request.args.get("period", "All")

    filtered = analyzer.filter_records(category=category, city=city, period=period)
    kpis = analyzer.get_kpis(filtered)
    monthly = analyzer.get_monthly_sales(filtered)
    cats = analyzer.get_category_sales(filtered)
    cities = analyzer.get_city_sales(filtered)
    payments = analyzer.get_payment_method_distribution(filtered)
    rfm = analyzer.get_rfm_segments(filtered)
    dow = analyzer.get_day_of_week_sales(filtered)
    status_dist = analyzer.get_order_status_distribution(filtered)
    age_groups = analyzer.get_age_group_sales(filtered)
    top_products = analyzer.get_top_products(5, filtered)

    # Convert latest 25 transactions
    recent = []
    for r in list(reversed(filtered))[:25]:
        recent.append({
            "Transaction_ID": r["Transaction_ID"],
            "Date_Str": r["Date_Str"],
            "Time": r.get("Time", "12:00"),
            "Customer_ID": r["Customer_ID"],
            "Gender": r["Gender"],
            "City": r["City"],
            "Product_Category": r["Product_Category"],
            "Product_Name": r["Product_Name"],
            "Quantity": r["Quantity"],
            "Price_Per_Unit": r["Price_Per_Unit"],
            "Discount_Pct": r["Discount_Pct"],
            "Total_Amount": r["Total_Amount"],
            "Net_Profit": r["Net_Profit"],
            "Payment_Method": r["Payment_Method"],
            "Order_Status": r["Order_Status"],
            "Rating": r["Rating"]
        })

    return jsonify({
        "kpis": kpis,
        "monthly": monthly,
        "categories": cats,
        "cities": cities,
        "payments": payments,
        "rfm": rfm,
        "dow": dow,
        "status_dist": status_dist,
        "age_groups": age_groups,
        "top_products": top_products,
        "recent_transactions": recent,
        "category_config": analyzer.category_config
    })

# --- CATEGORY EDITING & SCENARIO PLANNING ENDPOINTS ---

@app.route("/api/categories/config", methods=["GET"])
def get_category_config():
    """Returns current category configuration with baseline metrics."""
    stats = {}
    for cat in analyzer.category_config.keys():
        cat_records = [r for r in analyzer.records if r.get("Base_Category") == cat or r.get("Product_Category") == cat]
        rev = sum(r["Total_Amount"] for r in cat_records)
        profit = sum(r["Net_Profit"] for r in cat_records)
        units = sum(r["Quantity"] for r in cat_records)
        txns = len(cat_records)
        stats[cat] = {
            "revenue": round(rev, 2),
            "profit": round(profit, 2),
            "units": units,
            "transactions": txns,
            "margin_pct": round((profit / rev * 100.0), 1) if rev > 0 else 0.0
        }
    return jsonify({
        "config": analyzer.category_config,
        "stats": stats
    })

@app.route("/api/categories/config", methods=["POST"])
def update_category_config():
    """Updates editable options for categories and applies them across the entire dashboard."""
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid configuration payload"}), 400

    # Merge / update
    for cat, opts in data.items():
        if cat in analyzer.category_config:
            analyzer.category_config[cat].update(opts)
        else:
            analyzer.category_config[cat] = opts

    analyzer.save_category_config(analyzer.category_config)
    analyzer.apply_category_config()
    
    # Refresh Matplotlib image in background
    refresh_dashboard_image()

    return jsonify({
        "success": True,
        "message": "Category options updated and reflected on dashboard!",
        "kpis": analyzer.get_kpis()
    })

@app.route("/api/categories/reset", methods=["POST"])
def reset_category_config():
    """Resets all category parameters back to default baseline."""
    analyzer.reset_category_config()
    refresh_dashboard_image()
    return jsonify({
        "success": True,
        "message": "Category options reset to default baseline.",
        "config": analyzer.category_config,
        "kpis": analyzer.get_kpis()
    })

# --- SIMULATION & EXPORT ENDPOINTS ---

@app.route("/api/simulate-sale", methods=["POST"])
def simulate_sale():
    """Simulates an incoming live transaction and recalculates."""
    sample_items = [
        ("Electronics", "Smartphone", 650.0, 420.0),
        ("Electronics", "Wireless Headphones", 120.0, 72.0),
        ("Home & Kitchen", "Air Fryer", 110.0, 68.0),
        ("Clothing & Apparel", "Denim Jacket", 75.0, 32.0),
        ("Beauty & Personal Care", "Organic Perfume", 70.0, 26.0),
        ("Books & Stationery", "Bestseller Fiction Book", 22.0, 11.0)
    ]
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "San Francisco", "Miami", "Seattle", "Austin"]
    payments = ["Credit Card", "UPI / Digital Wallet", "Debit Card", "Cash"]
    
    cat, prod, price, cost = random.choice(sample_items)
    qty = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
    discount = random.choice([0.0, 5.0, 10.0])
    gross = qty * price
    disc_amt = gross * (discount / 100.0)
    total = round(gross - disc_amt, 2)
    profit = round(total - (qty * cost), 2)
    
    now = datetime.now()
    tx_id = f"TXN-{10000 + len(analyzer.raw_records) + 1}"
    cust_id = f"CUST-{random.randint(1001, 1350)}"
    
    new_txn = {
        "Transaction_ID": tx_id,
        "Date": now.strftime("%Y-%m-%d"),
        "Time": now.strftime("%H:%M"),
        "Customer_ID": cust_id,
        "Gender": random.choice(["Female", "Male"]),
        "Age_Group": random.choice(["18-25", "26-35", "36-50"]),
        "City": random.choice(cities),
        "Product_Category": cat,
        "Product_Name": prod,
        "Quantity": qty,
        "Price_Per_Unit": price,
        "Cost_Per_Unit": cost,
        "Discount_Pct": discount,
        "Total_Amount": total,
        "Cost_Total": round(qty * cost, 2),
        "Net_Profit": profit,
        "Payment_Method": random.choice(payments),
        "Order_Status": "Delivered",
        "Rating": 5
    }

    enriched = analyzer.append_transaction(new_txn)

    # Append to CSV
    try:
        with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                tx_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M"), cust_id,
                new_txn["Gender"], new_txn["Age_Group"], new_txn["City"],
                cat, prod, qty, f"{price:.2f}", f"{cost:.2f}", f"{discount:.1f}",
                f"{total:.2f}", f"{qty*cost:.2f}", f"{profit:.2f}",
                new_txn["Payment_Method"], "Delivered", 5
            ])
    except Exception as e:
        print(f"Error persisting simulated sale to CSV: {e}")

    return jsonify({"success": True, "transaction": enriched})

@app.route("/api/export-report")
def export_report():
    report_text = analyzer.generate_text_summary()
    mem = io.BytesIO()
    mem.write(report_text.encode('utf-8'))
    mem.seek(0)
    return send_file(
        mem,
        mimetype="text/plain",
        as_attachment=True,
        download_name="retail_sales_executive_report.txt"
    )

@app.route("/api/export-csv")
def export_csv():
    category = request.args.get("category", "All")
    city = request.args.get("city", "All")
    filtered = analyzer.filter_records(category=category, city=city)

    mem = io.StringIO()
    writer = csv.writer(mem)
    writer.writerow([
        "Transaction_ID", "Date", "Time", "Customer_ID", "Gender", "Age_Group",
        "City", "Product_Category", "Product_Name", "Quantity", "Price_Per_Unit",
        "Discount_Pct", "Total_Amount", "Net_Profit", "Payment_Method", "Order_Status", "Rating"
    ])
    for r in filtered:
        writer.writerow([
            r["Transaction_ID"], r["Date_Str"], r.get("Time", ""), r["Customer_ID"],
            r["Gender"], r["Age_Group"], r["City"], r["Product_Category"],
            r["Product_Name"], r["Quantity"], r["Price_Per_Unit"], r["Discount_Pct"],
            r["Total_Amount"], r["Net_Profit"], r["Payment_Method"], r["Order_Status"], r["Rating"]
        ])
    mem.seek(0)
    return send_file(
        io.BytesIO(mem.getvalue().encode('utf-8')),
        mimetype="text/csv",
        as_attachment=True,
        download_name="retail_transactions_filtered.csv"
    )

@app.route("/api/upload", methods=["POST"])
def upload_csv():
    global analyzer
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"success": False, "error": "File must be a CSV (.csv)"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "retail_sales_data.csv")
    file.save(file_path)

    # Reload analyzer
    analyzer = RetailSalesAnalyzer(file_path)
    refresh_dashboard_image()

    return jsonify({"success": True, "records_count": len(analyzer.records)})

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  [*] Starting Enterprise Retail Flask Web Dashboard")
    print("  [*] Access in your browser at: http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    app.run(debug=False, host="127.0.0.1", port=5000)
