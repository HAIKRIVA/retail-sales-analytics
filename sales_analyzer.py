"""
sales_analyzer.py
Enterprise-grade data processing and aggregation engine for retail sales.
Includes Profit Margins, RFM Customer Segmentation, Time Intelligence, KPIs,
and Dynamic Editable Category Configuration & Simulation.
"""

import csv
import json
import os
from collections import defaultdict
from datetime import datetime

DEFAULT_CATEGORY_CONFIG = {
    "Electronics": {
        "display_name": "Electronics",
        "price_markup_pct": 0.0,
        "cost_markup_pct": 0.0,
        "discount_pct": 5.0,
        "target_revenue": 65000.0,
        "is_active": True
    },
    "Clothing & Apparel": {
        "display_name": "Clothing & Apparel",
        "price_markup_pct": 0.0,
        "cost_markup_pct": 0.0,
        "discount_pct": 5.0,
        "target_revenue": 20000.0,
        "is_active": True
    },
    "Home & Kitchen": {
        "display_name": "Home & Kitchen",
        "price_markup_pct": 0.0,
        "cost_markup_pct": 0.0,
        "discount_pct": 5.0,
        "target_revenue": 30000.0,
        "is_active": True
    },
    "Beauty & Personal Care": {
        "display_name": "Beauty & Personal Care",
        "price_markup_pct": 0.0,
        "cost_markup_pct": 0.0,
        "discount_pct": 5.0,
        "target_revenue": 22000.0,
        "is_active": True
    },
    "Groceries & Gourmet": {
        "display_name": "Groceries & Gourmet",
        "price_markup_pct": 0.0,
        "cost_markup_pct": 0.0,
        "discount_pct": 5.0,
        "target_revenue": 6000.0,
        "is_active": True
    },
    "Books & Stationery": {
        "display_name": "Books & Stationery",
        "price_markup_pct": 0.0,
        "cost_markup_pct": 0.0,
        "discount_pct": 5.0,
        "target_revenue": 9000.0,
        "is_active": True
    }
}

class RetailSalesAnalyzer:
    def __init__(self, csv_filepath):
        self.csv_filepath = csv_filepath
        dir_name = os.path.dirname(os.path.abspath(csv_filepath))
        self.config_filepath = os.path.join(dir_name, "category_config.json")
        self.raw_records = []
        self.records = []
        self.category_config = {}
        
        self.load_data()
        self.load_category_config()
        self.apply_category_config()

    def load_category_config(self):
        """Loads category settings from category_config.json or initializes default."""
        if os.path.exists(self.config_filepath):
            try:
                with open(self.config_filepath, "r", encoding="utf-8") as f:
                    self.category_config = json.load(f)
            except Exception as e:
                print(f"Error loading category config: {e}. Using defaults.")
                self.category_config = dict(DEFAULT_CATEGORY_CONFIG)
        else:
            self.category_config = dict(DEFAULT_CATEGORY_CONFIG)
            self.save_category_config(self.category_config)

        # Ensure all discovered categories exist in config
        discovered_cats = set(r["Base_Category"] for r in self.raw_records)
        for cat in discovered_cats:
            if cat not in self.category_config:
                self.category_config[cat] = {
                    "display_name": cat,
                    "price_markup_pct": 0.0,
                    "cost_markup_pct": 0.0,
                    "discount_pct": 5.0,
                    "target_revenue": 10000.0,
                    "is_active": True
                }

    def save_category_config(self, new_config=None):
        """Persists category configuration to file."""
        if new_config is not None:
            self.category_config = new_config
        with open(self.config_filepath, "w", encoding="utf-8") as f:
            json.dump(self.category_config, f, indent=2)

    def reset_category_config(self):
        """Resets all category parameters back to default baseline."""
        self.category_config = dict(DEFAULT_CATEGORY_CONFIG)
        self.save_category_config(self.category_config)
        self.apply_category_config()
        return self.category_config

    def apply_category_config(self):
        """
        Recalculates active records applying the category configuration multipliers:
        - Price markup / markdown %
        - Cost inflation %
        - Custom discount %
        - Active/Inactive status
        - Category display rename
        """
        self.records = []
        for r in self.raw_records:
            base_cat = r["Base_Category"]
            cfg = self.category_config.get(base_cat, {
                "display_name": base_cat,
                "price_markup_pct": 0.0,
                "cost_markup_pct": 0.0,
                "discount_pct": r["Base_Discount_Pct"],
                "target_revenue": 10000.0,
                "is_active": True
            })

            # Check if category is active
            if not cfg.get("is_active", True):
                continue  # Excluded from active analytics

            price_mult = 1.0 + (float(cfg.get("price_markup_pct", 0.0)) / 100.0)
            cost_mult = 1.0 + (float(cfg.get("cost_markup_pct", 0.0)) / 100.0)
            discount_pct = float(cfg.get("discount_pct", r["Base_Discount_Pct"]))

            adj_price = round(r["Base_Price_Per_Unit"] * price_mult, 2)
            adj_cost = round(r["Base_Cost_Per_Unit"] * cost_mult, 2)
            qty = r["Quantity"]

            gross = adj_price * qty
            disc_amt = gross * (discount_pct / 100.0)
            adj_total = round(gross - disc_amt, 2)
            adj_cost_total = round(qty * adj_cost, 2)
            adj_net_profit = round(adj_total - adj_cost_total, 2)

            display_category = cfg.get("display_name", base_cat) or base_cat

            effective = dict(r)
            effective["Product_Category"] = display_category
            effective["Price_Per_Unit"] = adj_price
            effective["Cost_Per_Unit"] = adj_cost
            effective["Discount_Pct"] = discount_pct
            effective["Total_Amount"] = adj_total
            effective["Cost_Total"] = adj_cost_total
            effective["Net_Profit"] = adj_net_profit

            self.records.append(effective)

    def load_data(self):
        """Reads CSV file and saves baseline raw records."""
        self.raw_records = []
        if not os.path.exists(self.csv_filepath):
            return 0

        with open(self.csv_filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    price = float(row.get("Price_Per_Unit", 0.0))
                    qty = int(row.get("Quantity", 1))
                    total = float(row.get("Total_Amount", price * qty))
                    cost_unit = float(row.get("Cost_Per_Unit", price * 0.62))
                    cost_total = float(row.get("Cost_Total", cost_unit * qty))
                    net_profit = float(row.get("Net_Profit", total - cost_total))
                    discount_pct = float(row.get("Discount_Pct", 0.0))
                    order_status = row.get("Order_Status", "Delivered")
                    rating = int(row.get("Rating", 5))
                    time_str = row.get("Time", "12:00")
                    date_obj = datetime.strptime(row["Date"], "%Y-%m-%d")

                    record = {
                        "Transaction_ID": row["Transaction_ID"],
                        "Date": date_obj,
                        "Date_Str": row["Date"],
                        "Time": time_str,
                        "Day_Of_Week": date_obj.strftime("%A"),
                        "Customer_ID": row["Customer_ID"],
                        "Gender": row.get("Gender", "Unknown"),
                        "Age_Group": row.get("Age_Group", "Unknown"),
                        "City": row.get("City", "Unknown"),
                        "Base_Category": row["Product_Category"],
                        "Product_Category": row["Product_Category"],
                        "Product_Name": row["Product_Name"],
                        "Quantity": qty,
                        "Base_Price_Per_Unit": price,
                        "Base_Cost_Per_Unit": cost_unit,
                        "Base_Discount_Pct": discount_pct,
                        "Base_Total_Amount": total,
                        "Base_Net_Profit": net_profit,
                        "Price_Per_Unit": price,
                        "Cost_Per_Unit": cost_unit,
                        "Discount_Pct": discount_pct,
                        "Total_Amount": total,
                        "Cost_Total": cost_total,
                        "Net_Profit": net_profit,
                        "Payment_Method": row.get("Payment_Method", "Unknown"),
                        "Order_Status": order_status,
                        "Rating": rating
                    }
                    self.raw_records.append(record)
                except (ValueError, KeyError):
                    continue

        return len(self.raw_records)

    def filter_records(self, category=None, city=None, start_date=None, end_date=None, period=None):
        """Returns a subset of active records based on filters including date periods."""
        filtered = self.records
        if category and category != "All":
            filtered = [r for r in filtered if r["Product_Category"].lower() == category.lower()]
        if city and city != "All":
            filtered = [r for r in filtered if r["City"].lower() == city.lower()]
        if start_date:
            filtered = [r for r in filtered if r["Date"] >= start_date]
        if end_date:
            filtered = [r for r in filtered if r["Date"] <= end_date]

        if period and period != "All":
            if period == "Q1":
                filtered = [r for r in filtered if 1 <= r["Date"].month <= 3]
            elif period == "Q2":
                filtered = [r for r in filtered if 4 <= r["Date"].month <= 6]
            elif period == "Q3":
                filtered = [r for r in filtered if 7 <= r["Date"].month <= 9]
            elif period == "Q4":
                filtered = [r for r in filtered if 10 <= r["Date"].month <= 12]

        return filtered

    def get_kpis(self, records=None):
        """Calculates commercial, financial, and operational Key Performance Indicators."""
        data = records if records is not None else self.records
        if not data:
            return {
                "total_revenue": 0.0,
                "total_profit": 0.0,
                "profit_margin_pct": 0.0,
                "total_units": 0,
                "total_transactions": 0,
                "avg_order_value": 0.0,
                "avg_discount_pct": 0.0,
                "return_rate_pct": 0.0,
                "avg_rating": 0.0,
                "unique_customers": 0,
                "top_category": "N/A",
                "top_product": "N/A"
            }

        total_revenue = sum(r["Total_Amount"] for r in data)
        total_profit = sum(r["Net_Profit"] for r in data)
        profit_margin_pct = (total_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0
        total_units = sum(r["Quantity"] for r in data)
        total_transactions = len(data)
        avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0.0
        avg_discount_pct = sum(r["Discount_Pct"] for r in data) / total_transactions if total_transactions > 0 else 0.0

        returned_count = sum(1 for r in data if r["Order_Status"] == "Returned")
        return_rate_pct = (returned_count / total_transactions * 100.0) if total_transactions > 0 else 0.0

        avg_rating = sum(r["Rating"] for r in data) / total_transactions if total_transactions > 0 else 5.0
        unique_customers = len(set(r["Customer_ID"] for r in data))

        # Top category
        category_revenue = defaultdict(float)
        for r in data:
            category_revenue[r["Product_Category"]] += r["Total_Amount"]
        top_category = max(category_revenue.items(), key=lambda x: x[1])[0] if category_revenue else "N/A"

        # Top product
        product_revenue = defaultdict(float)
        for r in data:
            product_revenue[r["Product_Name"]] += r["Total_Amount"]
        top_product = max(product_revenue.items(), key=lambda x: x[1])[0] if product_revenue else "N/A"

        return {
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "profit_margin_pct": round(profit_margin_pct, 1),
            "total_units": total_units,
            "total_transactions": total_transactions,
            "avg_order_value": round(avg_order_value, 2),
            "avg_discount_pct": round(avg_discount_pct, 1),
            "return_rate_pct": round(return_rate_pct, 1),
            "avg_rating": round(avg_rating, 2),
            "unique_customers": unique_customers,
            "top_category": top_category,
            "top_product": top_product
        }

    def get_monthly_sales(self, records=None):
        """Returns monthly revenue, profit, and MoM growth rate."""
        data = records if records is not None else self.records
        monthly_rev = defaultdict(float)
        monthly_profit = defaultdict(float)
        monthly_units = defaultdict(int)

        for r in data:
            month_key = r["Date"].strftime("%Y-%m")
            monthly_rev[month_key] += r["Total_Amount"]
            monthly_profit[month_key] += r["Net_Profit"]
            monthly_units[month_key] += r["Quantity"]

        sorted_months = sorted(monthly_rev.keys())
        labels = [datetime.strptime(m, "%Y-%m").strftime("%b '%y") for m in sorted_months]
        revenues = [round(monthly_rev[m], 2) for m in sorted_months]
        profits = [round(monthly_profit[m], 2) for m in sorted_months]
        units = [monthly_units[m] for m in sorted_months]

        # Month-over-Month (MoM) Growth
        mom_growth = [0.0]
        for i in range(1, len(revenues)):
            prev = revenues[i - 1]
            curr = revenues[i]
            pct = ((curr - prev) / prev * 100.0) if prev > 0 else 0.0
            mom_growth.append(round(pct, 1))

        # Sum of active category monthly targets (annual target / 12)
        total_annual_target = sum(
            float(cfg.get("target_revenue", 10000.0))
            for cfg in self.category_config.values()
            if cfg.get("is_active", True)
        )
        monthly_target = round(total_annual_target / 12.0, 2) if total_annual_target > 0 else 12500.0
        targets = [monthly_target] * len(revenues)

        return {
            "months": labels,
            "revenues": revenues,
            "profits": profits,
            "units": units,
            "mom_growth": mom_growth,
            "targets": targets
        }

    def get_category_sales(self, records=None):
        """Returns revenue, profit, and profit margin per category."""
        data = records if records is not None else self.records
        cat_rev = defaultdict(float)
        cat_profit = defaultdict(float)
        cat_units = defaultdict(int)

        for r in data:
            cat = r["Product_Category"]
            cat_rev[cat] += r["Total_Amount"]
            cat_profit[cat] += r["Net_Profit"]
            cat_units[cat] += r["Quantity"]

        sorted_cats = sorted(cat_rev.items(), key=lambda x: x[1], reverse=True)
        categories = [item[0] for item in sorted_cats]
        revenues = [round(item[1], 2) for item in sorted_cats]
        profits = [round(cat_profit[c], 2) for c in categories]
        units = [cat_units[c] for c in categories]
        margins = [round((cat_profit[c] / cat_rev[c] * 100.0), 1) if cat_rev[c] > 0 else 0.0 for c in categories]

        return {
            "categories": categories,
            "revenues": revenues,
            "profits": profits,
            "units": units,
            "margins": margins
        }

    def get_city_sales(self, records=None):
        """Returns revenue and profit per city."""
        data = records if records is not None else self.records
        city_rev = defaultdict(float)
        city_profit = defaultdict(float)
        for r in data:
            city_rev[r["City"]] += r["Total_Amount"]
            city_profit[r["City"]] += r["Net_Profit"]

        sorted_cities = sorted(city_rev.items(), key=lambda x: x[1], reverse=True)
        cities = [item[0] for item in sorted_cities]
        revenues = [round(item[1], 2) for item in sorted_cities]
        profits = [round(city_profit[c], 2) for c in cities]

        return {
            "cities": cities,
            "revenues": revenues,
            "profits": profits
        }

    def get_rfm_segments(self, records=None):
        """Computes Recency, Frequency, and Monetary (RFM) segmentation."""
        data = records if records is not None else self.records
        if not data:
            return {"labels": [], "counts": [], "revenues": []}

        max_date = max(r["Date"] for r in data)
        cust_orders = defaultdict(list)

        for r in data:
            cust_orders[r["Customer_ID"]].append(r)

        segment_counts = {
            "Champions": 0,
            "Loyal Customers": 0,
            "Potential Loyalists": 0,
            "At Risk": 0,
            "Lost / Dormant": 0
        }
        segment_revenue = {
            "Champions": 0.0,
            "Loyal Customers": 0.0,
            "Potential Loyalists": 0.0,
            "At Risk": 0.0,
            "Lost / Dormant": 0.0
        }

        for cid, txns in cust_orders.items():
            freq = len(txns)
            total_spend = sum(t["Total_Amount"] for t in txns)
            latest_date = max(t["Date"] for t in txns)
            recency_days = (max_date - latest_date).days

            if freq >= 4 and total_spend >= 400 and recency_days <= 60:
                seg = "Champions"
            elif freq >= 3 and recency_days <= 90:
                seg = "Loyal Customers"
            elif freq >= 2 and recency_days <= 60:
                seg = "Potential Loyalists"
            elif recency_days > 120 and total_spend >= 300:
                seg = "At Risk"
            else:
                seg = "Lost / Dormant"

            segment_counts[seg] += 1
            segment_revenue[seg] += total_spend

        labels = list(segment_counts.keys())
        counts = [segment_counts[k] for k in labels]
        revs = [round(segment_revenue[k], 2) for k in labels]

        return {
            "labels": labels,
            "counts": counts,
            "revenues": revs
        }

    def get_day_of_week_sales(self, records=None):
        """Returns sales distribution across days of the week."""
        data = records if records is not None else self.records
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        rev_by_day = {d: 0.0 for d in days}
        orders_by_day = {d: 0 for d in days}

        for r in data:
            d = r["Day_Of_Week"]
            if d in rev_by_day:
                rev_by_day[d] += r["Total_Amount"]
                orders_by_day[d] += 1

        return {
            "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "revenues": [round(rev_by_day[d], 2) for d in days],
            "orders": [orders_by_day[d] for d in days]
        }

    def get_order_status_distribution(self, records=None):
        """Returns counts for Delivered, Returned, Cancelled."""
        data = records if records is not None else self.records
        counts = defaultdict(int)
        for r in data:
            counts[r["Order_Status"]] += 1
        labels = list(counts.keys())
        values = [counts[k] for k in labels]
        return {"labels": labels, "counts": values}

    def get_payment_method_distribution(self, records=None):
        """Returns revenue and transaction counts per payment method."""
        data = records if records is not None else self.records
        pm_rev = defaultdict(float)
        pm_count = defaultdict(int)

        for r in data:
            pm_rev[r["Payment_Method"]] += r["Total_Amount"]
            pm_count[r["Payment_Method"]] += 1

        methods = list(pm_rev.keys())
        revenues = [round(pm_rev[m], 2) for m in methods]
        counts = [pm_count[m] for m in methods]

        return {
            "methods": methods,
            "revenues": revenues,
            "counts": counts
        }

    def get_age_group_sales(self, records=None):
        """Returns revenue and order counts grouped by customer age."""
        data = records if records is not None else self.records
        standard_groups = ["18-25", "26-35", "36-50", "51+"]
        age_rev = {g: 0.0 for g in standard_groups}
        age_counts = {g: 0 for g in standard_groups}

        for r in data:
            g = r["Age_Group"]
            if g in age_rev:
                age_rev[g] += r["Total_Amount"]
                age_counts[g] += 1

        return {
            "groups": standard_groups,
            "revenues": [round(age_rev[g], 2) for g in standard_groups],
            "counts": [age_counts[g] for g in standard_groups]
        }

    def get_top_products(self, limit=5, records=None):
        """Returns top products by revenue and profit."""
        data = records if records is not None else self.records
        prod_rev = defaultdict(float)
        prod_profit = defaultdict(float)
        prod_qty = defaultdict(int)

        for r in data:
            p = r["Product_Name"]
            prod_rev[p] += r["Total_Amount"]
            prod_profit[p] += r["Net_Profit"]
            prod_qty[p] += r["Quantity"]

        sorted_prods = sorted(prod_rev.items(), key=lambda x: x[1], reverse=True)[:limit]
        products = [item[0] for item in sorted_prods]
        revenues = [round(item[1], 2) for item in sorted_prods]
        profits = [round(prod_profit[p], 2) for p in products]
        quantities = [prod_qty[p] for p in products]

        return {
            "products": products,
            "revenues": revenues,
            "profits": profits,
            "quantities": quantities
        }

    def append_transaction(self, record_dict):
        """Appends a new live transaction to raw_records and persists to CSV."""
        date_obj = datetime.strptime(record_dict["Date"], "%Y-%m-%d")
        price = float(record_dict["Price_Per_Unit"])
        qty = int(record_dict["Quantity"])
        cost_unit = float(record_dict.get("Cost_Per_Unit", price * 0.62))
        discount_pct = float(record_dict.get("Discount_Pct", 0.0))
        gross = price * qty
        discount_amt = gross * (discount_pct / 100.0)
        total = round(gross - discount_amt, 2)
        cost_total = round(qty * cost_unit, 2)
        profit = round(total - cost_total, 2)

        raw = {
            "Transaction_ID": record_dict["Transaction_ID"],
            "Date": date_obj,
            "Date_Str": record_dict["Date"],
            "Time": record_dict.get("Time", "12:00"),
            "Day_Of_Week": date_obj.strftime("%A"),
            "Customer_ID": record_dict["Customer_ID"],
            "Gender": record_dict.get("Gender", "Unknown"),
            "Age_Group": record_dict.get("Age_Group", "26-35"),
            "City": record_dict.get("City", "New York"),
            "Base_Category": record_dict["Product_Category"],
            "Product_Category": record_dict["Product_Category"],
            "Product_Name": record_dict["Product_Name"],
            "Quantity": qty,
            "Base_Price_Per_Unit": price,
            "Base_Cost_Per_Unit": cost_unit,
            "Base_Discount_Pct": discount_pct,
            "Base_Total_Amount": total,
            "Base_Net_Profit": profit,
            "Price_Per_Unit": price,
            "Cost_Per_Unit": cost_unit,
            "Discount_Pct": discount_pct,
            "Total_Amount": total,
            "Cost_Total": cost_total,
            "Net_Profit": profit,
            "Payment_Method": record_dict.get("Payment_Method", "Credit Card"),
            "Order_Status": record_dict.get("Order_Status", "Delivered"),
            "Rating": int(record_dict.get("Rating", 5))
        }

        self.raw_records.append(raw)
        self.apply_category_config()
        return raw

    def generate_text_summary(self):
        """Generates a formatted enterprise executive summary."""
        kpis = self.get_kpis()
        cat_data = self.get_category_sales()
        pm_data = self.get_payment_method_distribution()
        rfm_data = self.get_rfm_segments()
        top_prods = self.get_top_products(5)

        lines = []
        lines.append("=" * 70)
        lines.append("           ENTERPRISE RETAIL EXECUTIVE PERFORMANCE REPORT           ")
        lines.append("=" * 70)
        lines.append(f"  Total Gross Revenue:       ${kpis['total_revenue']:,.2f}")
        lines.append(f"  Total Net Profit:          ${kpis['total_profit']:,.2f}  (Gross Margin: {kpis['profit_margin_pct']}%)")
        lines.append(f"  Total Transactions:        {kpis['total_transactions']:,}")
        lines.append(f"  Total Units Sold:          {kpis['total_units']:,}")
        lines.append(f"  Average Order Value (AOV): ${kpis['avg_order_value']:,.2f}")
        lines.append(f"  Avg Discount Applied:      {kpis['avg_discount_pct']}%")
        lines.append(f"  Order Return Rate:         {kpis['return_rate_pct']}%")
        lines.append(f"  Customer CSAT Rating:      {kpis['avg_rating']} / 5.0")
        lines.append(f"  Unique Customer Base:      {kpis['unique_customers']:,}")
        lines.append(f"  Top Category:              {kpis['top_category']}")
        lines.append(f"  Top Product:               {kpis['top_product']}")
        lines.append("-" * 70)
        lines.append("  CATEGORY PERFORMANCE & MARGINS (CONFIG APPLIED):")
        for cat, rev, prof, mrg in zip(cat_data["categories"], cat_data["revenues"], cat_data["profits"], cat_data["margins"]):
            lines.append(f"    - {cat:<24}: Rev ${rev:>10,.2f} | Profit ${prof:>9,.2f} ({mrg:>4.1f}% margin)")
        lines.append("-" * 70)
        lines.append("  RFM CUSTOMER SEGMENTS:")
        for seg, cnt, rev in zip(rfm_data["labels"], rfm_data["counts"], rfm_data["revenues"]):
            lines.append(f"    - {seg:<22}: {cnt:>4} customers (${rev:>10,.2f})")
        lines.append("-" * 70)
        lines.append("  PAYMENT CHANNEL BREAKDOWN:")
        for pm, rev, cnt in zip(pm_data["methods"], pm_data["revenues"], pm_data["counts"]):
            pct = (rev / kpis["total_revenue"] * 100) if kpis["total_revenue"] else 0
            lines.append(f"    - {pm:<22}: ${rev:>10,.2f}  ({cnt:>4} orders, {pct:>5.1f}%)")
        lines.append("-" * 70)
        lines.append("  TOP 5 BEST-SELLING PRODUCTS:")
        for idx, (prod, rev, prof, qty) in enumerate(zip(top_prods["products"], top_prods["revenues"], top_prods["profits"], top_prods["quantities"]), 1):
            lines.append(f"    {idx}. {prod:<26}: Rev ${rev:>10,.2f} | Profit ${prof:>8,.2f} ({qty} sold)")
        lines.append("=" * 70)
        return "\n".join(lines)
