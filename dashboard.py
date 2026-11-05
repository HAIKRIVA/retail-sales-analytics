"""
dashboard.py
Generates an executive, publication-quality Retail Sales & Profitability Dashboard using matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sales_analyzer import RetailSalesAnalyzer

# Theme Colors
BG_COLOR = "#0B0F19"       # Deep luxury navy
PANEL_COLOR = "#151D2F"    # Container slate
TEXT_COLOR = "#F8FAFC"     # Bright white
MUTED_TEXT = "#94A3B8"     # Soft slate
ACCENT_BLUE = "#38BDF8"    # Sky blue
ACCENT_PURPLE = "#A855F7"  # Electric purple
ACCENT_GREEN = "#34D399"   # Mint green
ACCENT_AMBER = "#FBBF24"   # Amber gold
ACCENT_ROSE = "#F43F5E"    # Crimson rose
PALETTE = ["#38BDF8", "#818CF8", "#A855F7", "#EC4899", "#34D399", "#FBBF24", "#F97316"]

def set_plot_style(ax):
    """Applies clean executive styling to an axis."""
    ax.set_facecolor(PANEL_COLOR)
    ax.tick_params(colors=MUTED_TEXT, labelsize=8.5)
    for spine in ax.spines.values():
        spine.set_color("#232F47")
        spine.set_linewidth(0.8)
    ax.grid(color="#232F47", linestyle="--", linewidth=0.5, alpha=0.6)

def create_dashboard(csv_path="retail_sales_data.csv", output_image="retail_sales_dashboard.png", show_plot=False):
    analyzer = RetailSalesAnalyzer(csv_path)
    kpis = analyzer.get_kpis()
    monthly = analyzer.get_monthly_sales()
    categories = analyzer.get_category_sales()
    cities = analyzer.get_city_sales()
    payments = analyzer.get_payment_method_distribution()
    rfm = analyzer.get_rfm_segments()
    dow = analyzer.get_day_of_week_sales()
    top_products = analyzer.get_top_products(5)

    fig = plt.figure(figsize=(19, 11.5), facecolor=BG_COLOR)
    
    # GridSpec: Row 0 = KPIs, Row 1 = 3 charts, Row 2 = 3 charts
    gs = gridspec.GridSpec(3, 3, height_ratios=[1.0, 3.2, 3.2], hspace=0.36, wspace=0.25,
                           top=0.94, bottom=0.06, left=0.05, right=0.96)

    # -------------------------------------------------------------
    # HEADER & EXECUTIVE KPI BANNER (gs[0, :])
    # -------------------------------------------------------------
    ax_kpi = fig.add_subplot(gs[0, :])
    ax_kpi.set_facecolor(BG_COLOR)
    ax_kpi.axis("off")

    # Header Title & Subtitle
    ax_kpi.text(0.0, 0.90, "ENTERPRISE RETAIL EXECUTIVE DASHBOARD",
                fontsize=19, fontweight="bold", color=TEXT_COLOR, transform=ax_kpi.transAxes)
    ax_kpi.text(0.0, 0.67, f"Multi-channel commercial performance & RFM intelligence | {kpis['total_transactions']:,} Orders | CSAT: {kpis['avg_rating']} / 5.0",
                fontsize=10.5, color=MUTED_TEXT, transform=ax_kpi.transAxes)

    # 4 Executive Cards
    cards = [
        {"label": "GROSS REVENUE", "value": f"${kpis['total_revenue']:,.0f}", "sub": f"{kpis['total_units']:,} Units | AOV: ${kpis['avg_order_value']:.1f}", "color": ACCENT_BLUE},
        {"label": "NET PROFIT", "value": f"${kpis['total_profit']:,.0f}", "sub": f"Margin: {kpis['profit_margin_pct']}% | Discount: {kpis['avg_discount_pct']}%", "color": ACCENT_GREEN},
        {"label": "CUSTOMER BASE", "value": f"{kpis['unique_customers']:,}", "sub": f"Return Rate: {kpis['return_rate_pct']}% | CSAT: {kpis['avg_rating']}/5.0", "color": ACCENT_PURPLE},
        {"label": "TOP PERFORMER", "value": kpis['top_category'], "sub": f"Top Item: {kpis['top_product']}", "color": ACCENT_AMBER}
    ]

    card_width = 0.22
    start_x = 0.0
    gap = 0.04
    card_y = 0.02
    card_height = 0.50

    for i, card in enumerate(cards):
        x = start_x + i * (card_width + gap)
        rect = plt.Rectangle((x, card_y), card_width, card_height,
                             facecolor=PANEL_COLOR, edgecolor=card["color"],
                             linewidth=1.2, transform=ax_kpi.transAxes, clip_on=False)
        ax_kpi.add_patch(rect)

        ax_kpi.text(x + 0.015, card_y + 0.34, card["label"],
                    fontsize=8.5, fontweight="bold", color=MUTED_TEXT, transform=ax_kpi.transAxes)
        val_size = 14 if len(card["value"]) > 15 else 16
        ax_kpi.text(x + 0.015, card_y + 0.17, card["value"],
                    fontsize=val_size, fontweight="bold", color=card["color"], transform=ax_kpi.transAxes)
        ax_kpi.text(x + 0.015, card_y + 0.05, card["sub"],
                    fontsize=7.8, color=MUTED_TEXT, transform=ax_kpi.transAxes)

    # -------------------------------------------------------------
    # 1. MONTHLY REVENUE & PROFIT TREND (gs[1, 0])
    # -------------------------------------------------------------
    ax1 = fig.add_subplot(gs[1, 0])
    set_plot_style(ax1)
    x_idx = range(len(monthly["months"]))
    ax1.plot(x_idx, monthly["revenues"], color=ACCENT_BLUE, marker="o", linewidth=2.2, markersize=4.5, label="Revenue ($)")
    ax1.plot(x_idx, monthly["profits"], color=ACCENT_GREEN, marker="s", linewidth=1.8, markersize=4, linestyle="--", label="Net Profit ($)")
    ax1.fill_between(x_idx, monthly["revenues"], color=ACCENT_BLUE, alpha=0.15)
    ax1.set_xticks(x_idx)
    ax1.set_xticklabels(monthly["months"], rotation=40, ha="right", fontsize=7.5)
    ax1.set_title("Monthly Revenue & Net Profit", fontsize=11, fontweight="bold", color=TEXT_COLOR, pad=10)
    ax1.yaxis.set_major_formatter('${x:,.0f}')
    ax1.legend(loc="upper left", facecolor=PANEL_COLOR, edgecolor="#232F47", fontsize=7.5, labelcolor=TEXT_COLOR)

    # -------------------------------------------------------------
    # 2. CATEGORY REVENUE & PROFIT MARGIN (gs[1, 1])
    # -------------------------------------------------------------
    ax2 = fig.add_subplot(gs[1, 1])
    set_plot_style(ax2)
    cat_names = [c.replace(" & ", "\n& ") for c in categories["categories"]]
    x = range(len(cat_names))
    width = 0.36
    b1 = ax2.bar([i - width/2 for i in x], categories["revenues"], width=width, label="Revenue ($)", color=ACCENT_BLUE, edgecolor="#232F47")
    b2 = ax2.bar([i + width/2 for i in x], categories["profits"], width=width, label="Profit ($)", color=ACCENT_GREEN, edgecolor="#232F47")
    ax2.set_xticks(x)
    ax2.set_xticklabels(cat_names, fontsize=7.5)
    ax2.set_title("Category Revenue vs. Net Profit", fontsize=11, fontweight="bold", color=TEXT_COLOR, pad=10)
    ax2.yaxis.set_major_formatter('${x:,.0f}')
    ax2.legend(loc="upper right", facecolor=PANEL_COLOR, edgecolor="#232F47", fontsize=7.5, labelcolor=TEXT_COLOR)

    # Annotate margin % above bars
    for i, mrg in enumerate(categories["margins"]):
        top_y = max(categories["revenues"][i], categories["profits"][i])
        ax2.annotate(f"{mrg}%", xy=(i, top_y), xytext=(0, 3), textcoords="offset points",
                     ha="center", fontsize=7.5, color=ACCENT_AMBER, fontweight="bold")

    # -------------------------------------------------------------
    # 3. PAYMENT METHOD DISTRIBUTION (gs[1, 2])
    # -------------------------------------------------------------
    ax3 = fig.add_subplot(gs[1, 2])
    ax3.set_facecolor(PANEL_COLOR)
    donut_colors = [ACCENT_BLUE, ACCENT_PURPLE, ACCENT_AMBER, ACCENT_GREEN]
    wedges, texts, autotexts = ax3.pie(
        payments["revenues"],
        labels=payments["methods"],
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.76,
        colors=donut_colors[:len(payments["methods"])],
        textprops=dict(color=TEXT_COLOR, fontsize=8),
        wedgeprops=dict(width=0.45, edgecolor=PANEL_COLOR, linewidth=2)
    )
    for at in autotexts:
        at.set_color("#0B0F19")
        at.set_fontsize(7.5)
        at.set_fontweight("bold")
    ax3.set_title("Payment Method Share", fontsize=11, fontweight="bold", color=TEXT_COLOR, pad=10)
    ax3.text(0, 0, f"${kpis['total_revenue']/1000:.1f}k\nTotal",
             ha="center", va="center", fontsize=9, fontweight="bold", color=TEXT_COLOR)

    # -------------------------------------------------------------
    # 4. RFM CUSTOMER SEGMENTS (gs[2, 0])
    # -------------------------------------------------------------
    ax4 = fig.add_subplot(gs[2, 0])
    set_plot_style(ax4)
    rfm_labels = list(reversed(rfm["labels"]))
    rfm_revs = list(reversed(rfm["revenues"]))
    rfm_counts = list(reversed(rfm["counts"]))
    bars4 = ax4.barh(rfm_labels, rfm_revs, color=ACCENT_PURPLE, height=0.55, edgecolor="#232F47")
    ax4.set_title("Customer RFM Segments (Revenue)", fontsize=11, fontweight="bold", color=TEXT_COLOR, pad=10)
    ax4.xaxis.set_major_formatter('${x:,.0f}')
    ax4.tick_params(axis="y", labelsize=8)

    for bar, cnt in zip(bars4, rfm_counts):
        w = bar.get_width()
        ax4.annotate(f"${w/1000:.1f}k ({cnt} users)",
                     xy=(w, bar.get_y() + bar.get_height() / 2),
                     xytext=(4, 0), textcoords="offset points",
                     ha="left", va="center", fontsize=7.2, color=MUTED_TEXT)

    # -------------------------------------------------------------
    # 5. SALES BY CITY / REGION (gs[2, 1])
    # -------------------------------------------------------------
    ax5 = fig.add_subplot(gs[2, 1])
    set_plot_style(ax5)
    sorted_cities = list(reversed(cities["cities"]))
    sorted_revs = list(reversed(cities["revenues"]))
    bars5 = ax5.barh(sorted_cities, sorted_revs, color=ACCENT_BLUE, height=0.58, edgecolor="#232F47")
    ax5.set_title("Metropolitan Sales Performance", fontsize=11, fontweight="bold", color=TEXT_COLOR, pad=10)
    ax5.xaxis.set_major_formatter('${x:,.0f}')
    ax5.tick_params(axis="y", labelsize=8)

    for bar in bars5:
        w = bar.get_width()
        ax5.annotate(f"${w/1000:.1f}k",
                     xy=(w, bar.get_y() + bar.get_height() / 2),
                     xytext=(4, 0), textcoords="offset points",
                     ha="left", va="center", fontsize=7.2, color=TEXT_COLOR)

    # -------------------------------------------------------------
    # 6. DAY-OF-WEEK SHOPPING PATTERN (gs[2, 2])
    # -------------------------------------------------------------
    ax6 = fig.add_subplot(gs[2, 2])
    set_plot_style(ax6)
    bars6 = ax6.bar(dow["days"], dow["revenues"], color=ACCENT_AMBER, width=0.55, edgecolor="#232F47")
    ax6.set_title("Sales by Day of Week", fontsize=11, fontweight="bold", color=TEXT_COLOR, pad=10)
    ax6.yaxis.set_major_formatter('${x:,.0f}')
    ax6.tick_params(axis="x", labelsize=8)

    for bar, ord_cnt in zip(bars6, dow["orders"]):
        h = bar.get_height()
        ax6.annotate(f"{ord_cnt} orders",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 2), textcoords="offset points",
                     ha="center", va="bottom", fontsize=7.0, color=MUTED_TEXT)

    # Save Dashboard to disk
    plt.savefig(output_image, dpi=300, facecolor=BG_COLOR, bbox_inches="tight")
    print(f"Executive Dashboard saved successfully as: '{output_image}' (300 DPI high resolution)")

    if show_plot:
        try:
            plt.show()
        except Exception as e:
            print(f"Interactive window could not be opened: {e}")

    plt.close(fig)
    return output_image

if __name__ == "__main__":
    create_dashboard(show_plot=False)
