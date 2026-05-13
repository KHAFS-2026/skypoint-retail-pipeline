"""
Generate a static HTML executive-summary report from the marts.

Used as a time-constrained substitute for the Power BI .pbix deliverable.
Reads warehouse/retail_data.db and renders charts answering the four
business questions from CHALLENGE.md.

Outputs (paths are relative to the repo root):
    analytics/report.html                       interactive Plotly report
    powerbi/screenshots/report_overview.png     four-quadrant overview PNG
    powerbi/screenshots/report_filtered.png     country-filtered PNG

Usage:
    python -m venv .venv
    .venv/bin/pip install -r analytics/requirements.txt
    .venv/bin/python analytics/report.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "warehouse" / "retail_data.db"
REPORT_HTML = ROOT / "analytics" / "report.html"
SCREENSHOTS_DIR = ROOT / "powerbi" / "screenshots"

# Headline numbers exclude cancelled / returned orders. Matches the
# "Net Revenue (Completed)" measure documented in powerbi/dax_measures.md.
COMPLETED_FILTER = "f.status IN ('completed', 'shipped')"


def query_data(con: duckdb.DuckDBPyConnection) -> dict:
    """Run every query the report needs in one place."""
    kpis = con.execute(f"""
        SELECT
            SUM(f.net_revenue)              AS net_revenue,
            SUM(f.gross_profit)             AS gross_profit,
            COUNT(DISTINCT f.order_id)      AS order_count,
            COUNT(DISTINCT f.customer_id)   AS customer_count,
            SUM(f.quantity)                 AS units
        FROM marts.fct_sales f
        WHERE {COMPLETED_FILTER}
    """).fetchone()

    return {
        "kpis": {
            "net_revenue": kpis[0],
            "gross_profit": kpis[1],
            "margin_pct": kpis[1] / kpis[0] if kpis[0] else 0,
            "order_count": kpis[2],
            "customer_count": kpis[3],
            "units": kpis[4],
        },
        "monthly_trend": con.execute(f"""
            SELECT d.year_month, SUM(f.net_revenue) AS revenue
            FROM marts.fct_sales f
            JOIN marts.dim_date d ON d.date_key = f.date_key
            WHERE {COMPLETED_FILTER}
            GROUP BY 1 ORDER BY 1
        """).df(),
        "monthly_by_category": con.execute(f"""
            SELECT d.year_month, p.category, SUM(f.net_revenue) AS revenue
            FROM marts.fct_sales f
            JOIN marts.dim_date d    ON d.date_key   = f.date_key
            JOIN marts.dim_product p ON p.product_id = f.product_id
            WHERE {COMPLETED_FILTER}
            GROUP BY 1, 2 ORDER BY 1, 2
        """).df(),
        "rev_by_category": con.execute(f"""
            SELECT p.category, SUM(f.net_revenue) AS revenue
            FROM marts.fct_sales f
            JOIN marts.dim_product p USING (product_id)
            WHERE {COMPLETED_FILTER}
            GROUP BY 1 ORDER BY revenue DESC
        """).df(),
        "rev_by_store": con.execute(f"""
            SELECT s.store_name, s.region, SUM(f.net_revenue) AS revenue
            FROM marts.fct_sales f
            JOIN marts.dim_store s USING (store_id)
            WHERE {COMPLETED_FILTER}
            GROUP BY 1, 2 ORDER BY revenue DESC
        """).df(),
        "top_customers": con.execute(f"""
            SELECT c.customer_name, c.country,
                   SUM(f.net_revenue) AS revenue,
                   COUNT(DISTINCT f.order_id) AS orders
            FROM marts.fct_sales f
            JOIN marts.dim_customer c USING (customer_id)
            WHERE {COMPLETED_FILTER}
            GROUP BY 1, 2 ORDER BY revenue DESC
            LIMIT 10
        """).df(),
        "top_margin": con.execute("""
            SELECT product_name, category, margin_pct, unit_price, unit_cost
            FROM marts.dim_product
            WHERE NOT has_margin_issue AND margin_pct IS NOT NULL
            ORDER BY margin_pct DESC
            LIMIT 5
        """).df(),
        "bottom_margin": con.execute("""
            SELECT product_name, category, margin_pct, unit_price, unit_cost
            FROM marts.dim_product
            WHERE NOT has_margin_issue AND margin_pct IS NOT NULL
            ORDER BY margin_pct ASC
            LIMIT 5
        """).df(),
    }


def build_figures(d: dict) -> dict:
    fig_trend = px.line(
        d["monthly_trend"], x="year_month", y="revenue",
        title="Net Revenue by Month", markers=True,
        labels={"year_month": "Month", "revenue": "Net Revenue"},
    )
    fig_trend.update_layout(yaxis_tickformat="$,.0f")

    fig_category = px.bar(
        d["rev_by_category"], x="revenue", y="category",
        title="Net Revenue by Category", orientation="h",
        labels={"revenue": "Net Revenue", "category": "Category"},
    )
    fig_category.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_tickformat="$,.0f",
    )

    fig_monthly_cat = px.bar(
        d["monthly_by_category"], x="year_month", y="revenue",
        color="category", title="Monthly Revenue by Category",
        labels={"year_month": "Month", "revenue": "Net Revenue"},
    )
    fig_monthly_cat.update_layout(yaxis_tickformat="$,.0f", barmode="stack")

    fig_store = px.bar(
        d["rev_by_store"], x="revenue", y="store_name", color="region",
        title="Net Revenue by Store", orientation="h",
        labels={"revenue": "Net Revenue", "store_name": "Store"},
    )
    fig_store.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_tickformat="$,.0f", height=560,
    )

    fig_top_cust = px.bar(
        d["top_customers"], x="revenue", y="customer_name", color="country",
        title="Top 10 Customers by Net Revenue", orientation="h",
        labels={"revenue": "Net Revenue", "customer_name": "Customer"},
        hover_data=["orders"],
    )
    fig_top_cust.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_tickformat="$,.0f", height=420,
    )

    fig_top_margin = px.bar(
        d["top_margin"], x="margin_pct", y="product_name",
        title="Top 5 Products by Margin",
        orientation="h",
        labels={"margin_pct": "Margin %", "product_name": "Product"},
        color_discrete_sequence=["#2ca02c"],
        hover_data=["category", "unit_price", "unit_cost"],
    )
    fig_top_margin.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_tickformat=".1%",
    )

    fig_bottom_margin = px.bar(
        d["bottom_margin"], x="margin_pct", y="product_name",
        title="Bottom 5 Products by Margin",
        orientation="h",
        labels={"margin_pct": "Margin %", "product_name": "Product"},
        color_discrete_sequence=["#d62728"],
        hover_data=["category", "unit_price", "unit_cost"],
    )
    fig_bottom_margin.update_layout(
        yaxis={"categoryorder": "total descending"},
        xaxis_tickformat=".1%",
    )

    return {
        "trend": fig_trend,
        "category": fig_category,
        "monthly_cat": fig_monthly_cat,
        "store": fig_store,
        "top_cust": fig_top_cust,
        "top_margin": fig_top_margin,
        "bottom_margin": fig_bottom_margin,
    }


STYLES = """
<style>
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; max-width: 1200px; margin: 0 auto; padding: 1.5rem; color: #222; background: #fff; }
h1 { font-size: 1.6rem; margin: 0 0 0.2rem 0; }
.subtitle { color: #777; margin-bottom: 1.2rem; font-size: 0.9rem; }
h2 { font-size: 1.05rem; margin-top: 2.5rem; color: #444; border-bottom: 1px solid #eee; padding-bottom: 0.3rem; }
.kpi-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 0.8rem; margin: 1.2rem 0; }
.kpi { background: #f4f6f8; border-radius: 8px; padding: 0.9rem; text-align: center; }
.kpi h3 { font-size: 0.7rem; color: #666; text-transform: uppercase; margin: 0 0 0.4rem 0; letter-spacing: 0.05em; font-weight: 600; }
.kpi .v { font-size: 1.15rem; font-weight: 700; color: #222; }
.note { background: #fff8e1; border-left: 4px solid #fb8c00; padding: 0.75rem 1rem; margin: 1rem 0 1.5rem 0; font-size: 0.85rem; color: #555; line-height: 1.5; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #eee; color: #999; font-size: 0.8rem; text-align: center; }
</style>
"""


def render_html(d: dict, figs: dict) -> str:
    k = d["kpis"]

    kpi_html = f"""
    <div class="kpi-row">
      <div class="kpi"><h3>Net Revenue</h3><div class="v">${k['net_revenue']:,.0f}</div></div>
      <div class="kpi"><h3>Gross Profit</h3><div class="v">${k['gross_profit']:,.0f}</div></div>
      <div class="kpi"><h3>Margin %</h3><div class="v">{k['margin_pct']:.1%}</div></div>
      <div class="kpi"><h3>Orders</h3><div class="v">{k['order_count']:,}</div></div>
      <div class="kpi"><h3>Customers</h3><div class="v">{k['customer_count']:,}</div></div>
      <div class="kpi"><h3>Units Sold</h3><div class="v">{k['units']:,}</div></div>
    </div>
    """

    def fig_html(fig):
        return fig.to_html(full_html=False, include_plotlyjs=False)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Retail Sales — Executive Summary</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  {STYLES}
</head>
<body>
  <h1>Retail Sales — Executive Summary</h1>
  <p class="subtitle">Completed and shipped orders only · sourced from <code>marts.fct_sales</code></p>

  <div class="note">
    <strong>Substitute deliverable.</strong> This page is a time-constrained
    stand-in for the Power BI <code>.pbix</code> required by the challenge.
    The full Power BI design is specified in <code>powerbi/</code> (connection
    setup, semantic model, DAX measures, one-page layout) and would take
    ~30 min to assemble on a Windows machine.
  </div>

  {kpi_html}

  <h2>Q4 — Sales performance trend over time</h2>
  {fig_html(figs['trend'])}

  <h2>Q1 — Net revenue by category (overall)</h2>
  {fig_html(figs['category'])}

  <h2>Q1 — Net revenue by category × month</h2>
  {fig_html(figs['monthly_cat'])}

  <h2>Q1 — Net revenue by store</h2>
  {fig_html(figs['store'])}

  <h2>Q2 — Top 10 customers by net revenue</h2>
  {fig_html(figs['top_cust'])}

  <h2>Q3 — Highest &amp; lowest margin products</h2>
  <div class="grid-2">
    <div>{fig_html(figs['top_margin'])}</div>
    <div>{fig_html(figs['bottom_margin'])}</div>
  </div>

  <footer>Generated by <code>analytics/report.py</code> from <code>warehouse/retail_data.db</code></footer>
</body>
</html>"""


def write_screenshots(con: duckdb.DuckDBPyConnection, d: dict) -> None:
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    overview = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Net Revenue by Month",
            "Net Revenue by Category",
            "Top 10 Customers",
            "Top 5 Products by Margin",
        ],
        horizontal_spacing=0.22,
        vertical_spacing=0.18,
    )
    overview.add_trace(
        go.Scatter(x=d["monthly_trend"]["year_month"],
                   y=d["monthly_trend"]["revenue"],
                   mode="lines+markers", line=dict(color="#1f77b4")),
        row=1, col=1,
    )
    overview.add_trace(
        go.Bar(x=d["rev_by_category"]["revenue"],
               y=d["rev_by_category"]["category"],
               orientation="h", marker_color="#1f77b4"),
        row=1, col=2,
    )
    overview.add_trace(
        go.Bar(x=d["top_customers"]["revenue"],
               y=d["top_customers"]["customer_name"],
               orientation="h", marker_color="#1f77b4"),
        row=2, col=1,
    )
    overview.add_trace(
        go.Bar(x=d["top_margin"]["margin_pct"],
               y=d["top_margin"]["product_name"],
               orientation="h", marker_color="#2ca02c"),
        row=2, col=2,
    )
    overview.update_layout(
        height=900, width=1600, showlegend=False,
        title_text="Retail Sales — Executive Summary (completed & shipped orders)",
        title_x=0.5,
    )
    overview.update_yaxes(autorange="reversed", row=1, col=2)
    overview.update_yaxes(autorange="reversed", row=2, col=2)
    overview.update_yaxes(tickformat="$,.0f", row=1, col=1)  # revenue on Y for the line chart
    overview.update_xaxes(tickformat="$,.0f", row=1, col=2)
    overview.update_xaxes(tickformat="$,.0f", row=2, col=1)
    overview.update_xaxes(tickformat=".0%", row=2, col=2)

    png_overview = SCREENSHOTS_DIR / "report_overview.png"
    overview.write_image(str(png_overview), scale=2)
    print(f"Wrote {png_overview.relative_to(ROOT)}")

    # Filtered view: pick the strongest country, recompute the same charts.
    strongest = d["top_customers"].groupby("country")["revenue"].sum().idxmax()
    monthly_filt = con.execute(f"""
        SELECT d.year_month, SUM(f.net_revenue) AS revenue
        FROM marts.fct_sales f
        JOIN marts.dim_customer c USING (customer_id)
        JOIN marts.dim_date d     ON d.date_key = f.date_key
        WHERE c.country = '{strongest}' AND {COMPLETED_FILTER}
        GROUP BY 1 ORDER BY 1
    """).df()
    cust_filt = d["top_customers"][d["top_customers"]["country"] == strongest]

    filtered = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"Net Revenue by Month — {strongest} customers only",
            f"Top customers — {strongest}",
        ],
        column_widths=[0.55, 0.45],
        horizontal_spacing=0.2,
    )
    filtered.add_trace(
        go.Scatter(x=monthly_filt["year_month"], y=monthly_filt["revenue"],
                   mode="lines+markers", line=dict(color="#1f77b4")),
        row=1, col=1,
    )
    filtered.add_trace(
        go.Bar(x=cust_filt["revenue"], y=cust_filt["customer_name"],
               orientation="h", marker_color="#1f77b4"),
        row=1, col=2,
    )
    filtered.update_layout(
        height=520, width=1600, showlegend=False,
        title_text=f"Retail Sales — Filtered to {strongest}",
        title_x=0.5,
    )
    filtered.update_yaxes(autorange="reversed", row=1, col=2)
    filtered.update_yaxes(tickformat="$,.0f", row=1, col=1)  # revenue on Y in line chart
    filtered.update_xaxes(tickformat="$,.0f", row=1, col=2)  # revenue on X in bar chart

    png_filtered = SCREENSHOTS_DIR / "report_filtered.png"
    filtered.write_image(str(png_filtered), scale=2)
    print(f"Wrote {png_filtered.relative_to(ROOT)}")


def main() -> int:
    if not DB_PATH.exists():
        print(f"ERROR: {DB_PATH} does not exist. "
              "Run `docker compose up --build` first.", file=sys.stderr)
        return 1

    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        data = query_data(con)
        figs = build_figures(data)

        REPORT_HTML.parent.mkdir(parents=True, exist_ok=True)
        REPORT_HTML.write_text(render_html(data, figs))
        print(f"Wrote {REPORT_HTML.relative_to(ROOT)}")

        write_screenshots(con, data)
    finally:
        con.close()

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
