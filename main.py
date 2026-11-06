"""
main.py
Interactive CLI controller for the Retail Sales Dashboard Mini Project.
"""

import sys
import os
from datetime import datetime
from sales_analyzer import RetailSalesAnalyzer
from dashboard import create_dashboard
from generate_data import generate_retail_sales_csv

DEFAULT_CSV = "retail_sales_data.csv"

def print_header():
    print("\n" + "=" * 65)
    print("      RETAIL SALES ANALYTICS & DASHBOARD SYSTEM")
    print("      Mini Project: CSV Data Processing + Matplotlib")
    print("=" * 65)

def print_menu():
    print("\n[MENU OPTIONS]")
    print("  1. View Executive Summary & Key KPIs (Terminal)")
    print("  2. Generate & View Matplotlib Visual Dashboard")
    print("  3. Filter Analysis by Category or City")
    print("  4. Export Summary Report to File")
    print("  5. Regenerate Retail Dataset (Custom Record Count)")
    print("  6. Switch Active Dataset (retail_sales_data.csv / retail_sales_5000.csv)")
    print("  7. Launch Interactive Web Dashboard (Flask on http://127.0.0.1:5000)")
    print("  0. Exit")
    print("-" * 65)

def export_report_to_file(analyzer, output_file="sales_summary_report.txt"):
    report = analyzer.generate_text_summary()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)
        f.write(f"\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"\n[SUCCESS] Report exported to '{output_file}'.")

def filter_menu(analyzer):
    print("\n--- Filter Analysis ---")
    print("Available Categories:")
    cats = analyzer.get_category_sales()["categories"]
    for i, c in enumerate(cats, 1):
        print(f"  {i}. {c}")
    print("  0. All Categories")

    cat_choice = input("Select Category (0-6): ").strip()
    selected_cat = None
    if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(cats):
        selected_cat = cats[int(cat_choice) - 1]

    print("\nAvailable Cities:")
    cities = analyzer.get_city_sales()["cities"]
    for i, city in enumerate(cities, 1):
        print(f"  {i}. {city}")
    print("  0. All Cities")

    city_choice = input("Select City (0-8): ").strip()
    selected_city = None
    if city_choice.isdigit() and 1 <= int(city_choice) <= len(cities):
        selected_city = cities[int(city_choice) - 1]

    filtered_records = analyzer.filter_records(category=selected_cat, city=selected_city)
    kpis = analyzer.get_kpis(filtered_records)

    print("\n" + "=" * 55)
    print(f" FILTERED RESULTS: Category='{selected_cat or 'All'}', City='{selected_city or 'All'}'")
    print("=" * 55)
    print(f"  Matching Transactions: {kpis['total_transactions']:,}")
    print(f"  Filtered Revenue:      ${kpis['total_revenue']:,.2f}")
    print(f"  Total Units Sold:      {kpis['total_units']:,}")
    print(f"  Avg Order Value:       ${kpis['avg_order_value']:,.2f}")
    print(f"  Unique Customers:      {kpis['unique_customers']:,}")
    print("=" * 55)

def main():
    csv_file = DEFAULT_CSV
    if not os.path.exists(csv_file):
        print(f"[INFO] '{csv_file}' not found. Generating default dataset...")
        generate_retail_sales_csv(csv_file, num_records=1000)

    analyzer = RetailSalesAnalyzer(csv_file)

    while True:
        print_header()
        print(f"  Dataset: {csv_file} ({len(analyzer.records):,} loaded records)")
        print_menu()
        choice = input("Enter your choice (0-6): ").strip()

        if choice == "1":
            print("\n" + analyzer.generate_text_summary())
            input("\nPress Enter to continue...")

        elif choice == "2":
            print("\n[INFO] Generating Matplotlib Dashboard...")
            create_dashboard(csv_path=csv_file, output_image="retail_sales_dashboard.png", show_plot=True)
            input("\nPress Enter to continue...")

        elif choice == "3":
            filter_menu(analyzer)
            input("\nPress Enter to continue...")

        elif choice == "4":
            export_report_to_file(analyzer)
            input("\nPress Enter to continue...")

        elif choice == "5":
            count_str = input("\nEnter number of records to generate (e.g. 500, 2000): ").strip()
            count = int(count_str) if count_str.isdigit() and int(count_str) > 0 else 1000
            generate_retail_sales_csv(csv_file, num_records=count)
            analyzer = RetailSalesAnalyzer(csv_file)
            print(f"[SUCCESS] Reloaded dataset with {len(analyzer.records):,} records.")
            input("\nPress Enter to continue...")

        elif choice == "6":
            print("\nAvailable datasets in directory:")
            csvs = [f for f in os.listdir(".") if f.endswith(".csv")]
            for idx, f in enumerate(csvs, 1):
                print(f"  {idx}. {f} {'(CURRENT)' if f == csv_file else ''}")
            sel = input(f"Select dataset number (1-{len(csvs)}) or enter filename: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(csvs):
                csv_file = csvs[int(sel) - 1]
                analyzer = RetailSalesAnalyzer(csv_file)
                print(f"[SUCCESS] Switched active dataset to: {csv_file} ({len(analyzer.records):,} records)")
            elif os.path.exists(sel):
                csv_file = sel
                analyzer = RetailSalesAnalyzer(csv_file)
                print(f"[SUCCESS] Switched active dataset to: {csv_file} ({len(analyzer.records):,} records)")
            else:
                print("[WARNING] Invalid selection. Keeping current dataset.")
            input("\nPress Enter to continue...")

        elif choice == "7":
            import subprocess
            import webbrowser
            print("\n[INFO] Launching Flask Web Dashboard...")
            print("Opening browser at http://127.0.0.1:5000 (Press Ctrl+C in server window to stop)...")
            try:
                webbrowser.open("http://127.0.0.1:5000")
                from app import app
                app.run(debug=False, host="127.0.0.1", port=5000)
            except KeyboardInterrupt:
                print("\n[INFO] Web dashboard stopped.")
            input("\nPress Enter to continue...")

        elif choice == "0":
            print("\nExiting Retail Sales Dashboard. Thank you!\n")
            sys.exit(0)

        else:
            print("\n[ERROR] Invalid choice. Please choose 0 to 6.")

if __name__ == "__main__":
    main()
