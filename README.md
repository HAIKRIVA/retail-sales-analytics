# 📊 Enterprise Retail Intelligence & Sales Dashboard

An industry-grade Python Mini Project combining **CSV Data Processing**, **Matplotlib Visualizations**, and an **Interactive Flask Web Application** with commercial KPIs, Profit Margins, and Customer RFM Segmentation.

---

## 🌟 Professional Features

### 1. Financial & Commercial Metrics
- **Gross Revenue vs. Net Profit**: Unit cost modeling, total profit (\$58k+), and gross margin percentage (41.8%).
- **Discount & Promotion Impact**: Average discount applied per category and net sales impact.
- **Order Fulfillment & Return Rate**: Tracks order status (`Delivered`, `Returned`, `Cancelled`) and return percentage (12.8%).
- **Customer CSAT Score**: Average customer rating out of 5.0 stars with rating distributions.

### 2. Editable Category Options & Pricing Strategy Simulation
- **Editable Category Controls**:
  - **Price Markup / Markdown %** (-30% to +50% range or number input)
  - **Supplier Cost / Inflation %** (-30% to +50% range or number input)
  - **Promotional Discount % Override** (0% to 30%)
  - **Annual Revenue Target Goal ($)**
  - **Active / Inactive Toggle Switch** (disable/enable categories to evaluate partial-portfolio performance)
  - **Custom Display Name / Rename Category**
- **Instant Global Recalculation**: Any edit instantly updates all 5 KPI cards, all 12 Chart.js visualizations, the live transactions table, and re-renders the 300 DPI Matplotlib image.
- **Presets & Reset**: One-click *"Apply +10% Inflation"*, *"10% Holiday Discount"*, or *"Reset to Baseline"*.

### 2. Customer RFM Intelligence
- **RFM Segmentation (Recency, Frequency, Monetary)**:
  - 🏆 **Champions**: High spenders with repeat orders and recent purchases.
  - ⭐ **Loyal Customers**: Consistent buyers across categories.
  - 🚀 **Potential Loyalists**: Recent buyers with growing basket sizes.
  - ⚠️ **At Risk**: High historical spenders who haven't ordered recently.
  - 💤 **Lost / Dormant**: Inactive accounts.

### 3. Shopping Patterns & Time Intelligence
- **Month-over-Month (MoM) Growth**: Percentage month-over-month revenue velocity.
- **Target Attainment Benchmark**: Compares monthly revenue against monthly quota targets.
- **Day-of-Week Shopping Heat**: Peak transaction days (Monday through Sunday).

### 4. Interactive Web Application (Flask + Chart.js)
- **Multi-Tab Dashboard**:
  - 📊 **Executive Overview**: High-level KPIs, Revenue vs Target, City breakdowns, Top products.
  - 💰 **Profit & Margins**: Category Profitability comparison, Margin percentages, Fulfillment donut.
  - 👥 **RFM Customers**: Customer segment distribution and spend contribution.
  - 🕒 **Shopping Patterns**: Day-of-week patterns and MoM growth trajectories.
  - 📑 **Data Explorer**: Searchable, real-time transaction ledger with live filters.
- **Live Sale Simulator**: Click *"Simulate Live Sale"* to push instant real-time transactions into the dataset and watch charts update live!
- **Dark & Light Mode**: Seamless theme toggle with persistent styling.
- **Exporting Suite**: Download individual charts as PNGs, download filtered transactions as CSV, or download executive summary text reports.

### 5. Publication-Quality Matplotlib Dashboard (300 DPI)
- Generated via `dashboard.py` using `GridSpec` layout with custom KPI metric cards.

### 6. Excel Dashboard & Presentation Suite
- Included in [`excel_dashboard_analysis/`](file:///c:/Users/HAIKRIVA%20RB/Downloads/python%20mini%20project/excel_dashboard_analysis):
  - **Dynamic Excel Workbook (`Retail Sales Dashboard.xlsx`)**: Built with Power Query, Slicers, and Pivot Tables.
  - **5,000-Row Production Dataset (`retail_sales_5000.csv`)**: Full multi-year sales transaction records across multiple categories and states.
  - **Presentation Deck (`Retail Sales Dashboard.pptx`) & PDF (`Retail Sales Dashboard.pdf`)**: Complete executive presentation and deck.
  - **Walkthrough Video (`Retail Sales Dashboard.mp4`)**: Demonstration walkthrough of dashboard capabilities.

---

## 🚀 How to Run

### Method 1: Web Dashboard (Browser)
- **Windows double-click**: Double-click [`run_web.bat`](file:///c:/Users/HAIKRIVA%20RB/Downloads/python%20mini%20project/run_web.bat)
- **Terminal**:
  ```powershell
  py -3 app.py
  ```
  Then open **http://localhost:5000** in your browser.

### Method 2: Command-Line Interface (Terminal Menu)
- **Windows double-click**: Double-click [`run.bat`](file:///c:/Users/HAIKRIVA%20RB/Downloads/python%20mini%20project/run.bat)
- **Terminal**:
  ```powershell
  py -3 main.py
  ```

### Method 3: Direct Matplotlib Image Generation
```powershell
py -3 dashboard.py
```

---

## 🎓 Academic / Viva Presentation Highlights

If presenting this project for an evaluation or interview, be prepared to discuss:

1. **Why `csv.DictReader` over basic string splitting?**
   - Automatically maps headers to row dictionaries, preventing column index mismatch bugs.
2. **Why `matplotlib.gridspec` instead of simple `plt.subplots`?**
   - Enables non-uniform grids, allowing the top KPI metrics banner to span the full width while arranging 6 subplots cleanly in a $2 \times 3$ matrix beneath.
3. **Dual-Axis Visualization**:
   - Used `ax.twinx()` on the Customer Demographics chart to simultaneously plot monetary revenue (bars on primary Y-axis) and transaction count (bars on secondary Y-axis).
4. **Data Aggregation Logic**:
   - Uses `collections.defaultdict` for $O(N)$ single-pass aggregation across 1,000+ records.
