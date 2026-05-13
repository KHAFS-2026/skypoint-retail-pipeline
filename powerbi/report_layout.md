# One-Page Report Layout

A suggested layout that answers all four business questions on a single
page (the challenge calls for one page). 16:9 page size, default margins.

```
┌────────────────────────────────────────────────────────────────────────────────┐
│  RETAIL SALES — Executive Summary                              [Date slicer]   │
├──────────┬──────────┬──────────┬──────────┬───────────────────────────────────┤
│ Revenue  │ Profit   │ Margin % │ Orders   │  Revenue trend (monthly)          │
│ $5.27M   │ $2.94M   │ 55.8%    │ 4,750    │  ╱╲    ╱╲   ╱                     │
│  ▲ 12%   │  ▲ 9%    │ ▼ 0.4pp  │  ▲ 6%    │ ╱  ╲__╱  ╲_╱                      │
├──────────┴──────────┴──────────┴──────────┤  Line chart, x=date, y=Net Rev    │
│                                            │                                   │
│  Revenue by Category (stacked bar)         │                                   │
│  ████████████████  Beauty       1.19M      │                                   │
│  ███████████████   Sports       1.18M      ├───────────────────────────────────┤
│  ██████████████    Apparel      1.08M      │  Top 10 Customers (table)         │
│  █████████████     Books        1.00M      │  Casey Robinson    $53k  Canada   │
│  ███████████       Home&Kitchen 0.82M      │  Harper Hill       $44k  UK       │
│  ▏                                         │  Mateo Sanchez     $42k  Canada   │
│                                            │  …                                │
├────────────────────────────────────────────┴───────────────────────────────────┤
│ Highest margin products  │ Lowest margin products  │ Filters / slicers         │
│ (table top 5)            │ (table bottom 5)        │  [Category]  [Country]    │
│                          │                         │  [Status]                 │
└──────────────────────────┴─────────────────────────┴───────────────────────────┘
```

(Numbers above are illustrative — your numbers will differ slightly run to run.)

---

## Visuals — exact spec

### Header row

| Visual | Type | Field / Measure |
| --- | --- | --- |
| Title | Text box | "Retail Sales — Executive Summary" |
| Date slicer | Slicer (date range) | `dim_date[date]` |

### KPI card row

Four card visuals across the top. For each card, set:
- **Fields** → the measure
- **Format → Callout value** → the format string already on the measure
- **Format → Reference label** → measure's display name

| Card | Measure |
| --- | --- |
| Revenue | `Net Revenue (Completed)` |
| Profit  | `Gross Profit (Completed)` |
| Margin % | `Margin %` |
| Orders | `Order Count` |

Optional: add `Revenue YoY %` as a callout subtitle on the Revenue card to
show the trend arrow.

### Middle row — categorical breakdowns

| Visual | Type | Axis / Legend | Values |
| --- | --- | --- | --- |
| Revenue by Category | Stacked bar (horizontal) | `dim_product[category]` | `Net Revenue` |
| Revenue Trend | Line chart | `dim_date[date]` (date hierarchy) | `Net Revenue` |
| Top 10 Customers | Table | `dim_customer[customer_name]`, `dim_customer[country]` | `Net Revenue` |

For the **Top 10 Customers** table:
- Add a **Top N visual-level filter** on `customer_name`, N = 10, by `Net Revenue`.
- Sort by `Net Revenue` descending.

### Bottom row — margin analysis & slicers

| Visual | Type | Fields | Notes |
| --- | --- | --- | --- |
| Highest margin products | Table | `dim_product[product_name]`, `dim_product[margin_pct]` | Top N filter, N=5, by `margin_pct` desc |
| Lowest margin products | Table | `dim_product[product_name]`, `dim_product[margin_pct]` | Top N filter, N=5, by `margin_pct` asc |
| Filters | Slicer × 3 | `dim_product[category]`, `dim_store[country]`, `fct_sales[status]` | Tile or dropdown style |

> Filter the margin tables to **exclude `has_margin_issue = TRUE`** if you
> want only legitimate products (i.e. positive margins from clean rows).
> Otherwise you'll see deliberately seeded negative-margin rows on the
> bottom-5 list, which is honest but distracting.

---

## Cross-filtering behavior

Default behavior is fine — all visuals filter each other through the
dimension relationships. A few tweaks worth making via
**Edit interactions** on each visual:

- KPI cards on top: leave them filtered by everything (so they reflect
  current slicer selections).
- Top 10 Customers and margin tables: consider setting cross-filter to
  "None" from the KPI cards, since clicking a card shouldn't reshuffle a
  customer list.

---

## Theme

Use the built-in **Executive** or **Default** Power BI theme; nothing fancy
required for the challenge. Match all currency formats so the numbers
don't display in inconsistent precision.

---

## Save and ship

1. **File → Save As** → `retail_sales.pbix` in `powerbi/`.
2. Take **at least two screenshots** of the report:
   - One showing the full page
   - One with a slicer applied (e.g. one country selected) — proves
     interactivity works
   Save to `powerbi/screenshots/`.
3. Reference the screenshots from the top-level README.

That's the full Power BI deliverable.
