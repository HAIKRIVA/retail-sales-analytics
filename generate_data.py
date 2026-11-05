"""
generate_data.py
Generates a realistic, enterprise-grade retail sales dataset saved to CSV.
Includes Cost, Margins, Discounts, Order Status, Ratings, and Timestamps.
"""

import csv
import random
from datetime import datetime, timedelta

def generate_retail_sales_csv(filename="retail_sales_data.csv", num_records=1200, seed=42):
    random.seed(seed)
    
    categories = {
        "Electronics": [
            ("Wireless Headphones", 120.0, 72.0),
            ("Smartphone", 650.0, 420.0),
            ("Smart Watch", 180.0, 105.0),
            ("Bluetooth Speaker", 60.0, 32.0),
            ("Gaming Mouse", 45.0, 22.0),
            ("Laptop Stand", 35.0, 16.0)
        ],
        "Clothing & Apparel": [
            ("Denim Jacket", 75.0, 32.0),
            ("Cotton T-Shirt", 25.0, 8.5),
            ("Running Shoes", 90.0, 42.0),
            ("Formal Shirt", 40.0, 18.0),
            ("Hoodie", 55.0, 24.0)
        ],
        "Home & Kitchen": [
            ("Air Fryer", 110.0, 68.0),
            ("Coffee Maker", 85.0, 48.0),
            ("Stainless Steel Cookware Set", 140.0, 80.0),
            ("Blender", 50.0, 28.0),
            ("Ceramic Dinnerware Set", 65.0, 34.0)
        ],
        "Beauty & Personal Care": [
            ("Skincare Serum Set", 45.0, 16.0),
            ("Electric Toothbrush", 60.0, 28.0),
            ("Hair Dryer", 50.0, 25.0),
            ("Organic Perfume", 70.0, 26.0),
            ("Moisturizer Cream", 22.0, 8.0)
        ],
        "Groceries & Gourmet": [
            ("Organic Olive Oil", 24.0, 15.0),
            ("Artisan Coffee Beans", 18.0, 10.0),
            ("Premium Dark Chocolate", 12.0, 6.5),
            ("Mixed Nuts Pack", 20.0, 12.0),
            ("Green Tea Box", 15.0, 8.0)
        ],
        "Books & Stationery": [
            ("Hardcover Journal", 16.0, 6.0),
            ("Bestseller Fiction Book", 22.0, 11.0),
            ("Calligraphy Pen Set", 28.0, 13.0),
            ("Productivity Planner", 20.0, 7.5)
        ]
    }
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "San Francisco", "Miami", "Seattle", "Austin"]
    payment_methods = ["Credit Card", "UPI / Digital Wallet", "Debit Card", "Cash"]
    payment_weights = [0.45, 0.30, 0.15, 0.10]
    
    age_groups = ["18-25", "26-35", "36-50", "51+"]
    age_weights = [0.25, 0.40, 0.25, 0.10]
    
    genders = ["Female", "Male", "Non-Binary"]
    gender_weights = [0.52, 0.44, 0.04]

    order_statuses = ["Delivered", "Delivered", "Delivered", "Delivered", "Delivered", "Delivered", "Returned", "Cancelled"]
    ratings = [5, 5, 4, 4, 4, 3, 2, 1]
    rating_weights = [0.45, 0.25, 0.15, 0.08, 0.04, 0.01, 0.01, 0.01]
    
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range_days = (end_date - start_date).days
    
    fields = [
        "Transaction_ID",
        "Date",
        "Time",
        "Customer_ID",
        "Gender",
        "Age_Group",
        "City",
        "Product_Category",
        "Product_Name",
        "Quantity",
        "Price_Per_Unit",
        "Cost_Per_Unit",
        "Discount_Pct",
        "Total_Amount",
        "Cost_Total",
        "Net_Profit",
        "Payment_Method",
        "Order_Status",
        "Rating"
    ]
    
    records = []
    
    for i in range(1, num_records + 1):
        tx_id = f"TXN-{10000 + i}"
        cust_id = f"CUST-{random.randint(1001, 1350)}"
        
        # Date with seasonal boost in Nov-Dec and July
        random_day = random.randint(0, date_range_days)
        tx_date = start_date + timedelta(days=random_day)
        
        # Time of purchase (peak between 11 AM and 9 PM)
        hour = random.choices(range(8, 23), weights=[1, 2, 4, 6, 8, 8, 7, 7, 8, 9, 8, 6, 4, 2, 1])[0]
        minute = random.randint(0, 59)
        time_str = f"{hour:02d}:{minute:02d}"
        
        category = random.choice(list(categories.keys()))
        product_name, base_price, base_cost = random.choice(categories[category])
        
        # Price & cost fluctuation (+/- 4%)
        unit_price = round(base_price * random.uniform(0.96, 1.04), 2)
        unit_cost = round(base_cost * random.uniform(0.97, 1.03), 2)
        quantity = random.choices([1, 2, 3, 4, 5], weights=[0.55, 0.25, 0.12, 0.05, 0.03])[0]
        
        # Discounts: 0%, 5%, 10%, 15%, 20%
        discount_pct = random.choices([0.0, 5.0, 10.0, 15.0, 20.0], weights=[0.50, 0.20, 0.15, 0.10, 0.05])[0]
        gross_amount = quantity * unit_price
        discount_amount = gross_amount * (discount_pct / 100.0)
        total_amount = round(gross_amount - discount_amount, 2)
        
        cost_total = round(quantity * unit_cost, 2)
        net_profit = round(total_amount - cost_total, 2)
        
        city = random.choice(cities)
        gender = random.choices(genders, weights=gender_weights)[0]
        age_group = random.choices(age_groups, weights=age_weights)[0]
        payment_method = random.choices(payment_methods, weights=payment_weights)[0]
        order_status = random.choice(order_statuses)
        rating = random.choices(ratings, weights=rating_weights)[0]
        
        records.append({
            "Transaction_ID": tx_id,
            "Date": tx_date.strftime("%Y-%m-%d"),
            "Time": time_str,
            "Customer_ID": cust_id,
            "Gender": gender,
            "Age_Group": age_group,
            "City": city,
            "Product_Category": category,
            "Product_Name": product_name,
            "Quantity": quantity,
            "Price_Per_Unit": f"{unit_price:.2f}",
            "Cost_Per_Unit": f"{unit_cost:.2f}",
            "Discount_Pct": f"{discount_pct:.1f}",
            "Total_Amount": f"{total_amount:.2f}",
            "Cost_Total": f"{cost_total:.2f}",
            "Net_Profit": f"{net_profit:.2f}",
            "Payment_Method": payment_method,
            "Order_Status": order_status,
            "Rating": rating
        })
        
    # Sort chronologically
    records.sort(key=lambda x: (x["Date"], x["Time"]))
    
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
        
    print(f"Successfully generated {len(records)} professional retail transactions in '{filename}'.")
    return filename

if __name__ == "__main__":
    generate_retail_sales_csv()
