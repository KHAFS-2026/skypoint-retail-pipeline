# DAX Measures

All measures live on the **`fct_sales`** table (create a new measure with
**Home → New measure** while the fact is selected). Group them under a
single display folder called `Measures` so they're easy to find.

Format strings are noted next to each — set via **Measure tools → Format**.

Each measure is mapped to the business question it answers at the bottom.

---

## Revenue

```DAX
Net Revenue =
SUM ( 'fct_sales'[net_revenue] )
```
Format: **Currency, 0 dp**

```DAX
Gross Revenue =
SUM ( 'fct_sales'[gross_revenue] )
```
Format: Currency, 0 dp

```DAX
Discount Amount =
SUM ( 'fct_sales'[discount_amount] )
```
Format: Currency, 0 dp

---

## Profitability

```DAX
Total Cost =
SUM ( 'fct_sales'[total_cost] )
```
Format: Currency, 0 dp

```DAX
Gross Profit =
SUM ( 'fct_sales'[gross_profit] )
```
Format: Currency, 0 dp

```DAX
Margin % =
DIVIDE ( [Gross Profit], [Net Revenue], 0 )
```
Format: **Percentage, 1 dp**

---

## Volume

```DAX
Total Quantity =
SUM ( 'fct_sales'[quantity] )
```
Format: Whole number, with separator

```DAX
Order Count =
DISTINCTCOUNT ( 'fct_sales'[order_id] )
```
Format: Whole number, with separator

```DAX
Customer Count =
DISTINCTCOUNT ( 'fct_sales'[customer_id] )
```
Format: Whole number, with separator

```DAX
Avg Order Value =
DIVIDE ( [Net Revenue], [Order Count], 0 )
```
Format: Currency, 2 dp

---

## Filtered (completed business only)

The fact contains every order line including `cancelled` and `returned`.
For the headline revenue/profit numbers, most BI conventions exclude those.

```DAX
Net Revenue (Completed) =
CALCULATE (
    [Net Revenue],
    'fct_sales'[status] IN { "completed", "shipped" }
)
```
Format: Currency, 0 dp

```DAX
Gross Profit (Completed) =
CALCULATE (
    [Gross Profit],
    'fct_sales'[status] IN { "completed", "shipped" }
)
```
Format: Currency, 0 dp

> Decide which set of measures (raw vs. completed-only) drives the headline
> KPI cards on the report. Mixing them is the most common source of
> "why don't the totals match the database?" confusion.

---

## Time intelligence

These all rely on `dim_date` being **marked as the date table** — see
[semantic_model.md](semantic_model.md).

```DAX
Net Revenue PY =
CALCULATE (
    [Net Revenue],
    SAMEPERIODLASTYEAR ( 'dim_date'[date] )
)
```
Format: Currency, 0 dp

```DAX
Revenue YoY =
[Net Revenue] - [Net Revenue PY]
```
Format: Currency, 0 dp

```DAX
Revenue YoY % =
DIVIDE ( [Revenue YoY], [Net Revenue PY], 0 )
```
Format: Percentage, 1 dp

```DAX
Net Revenue YTD =
TOTALYTD ( [Net Revenue], 'dim_date'[date] )
```
Format: Currency, 0 dp

```DAX
Net Revenue MTD =
TOTALMTD ( [Net Revenue], 'dim_date'[date] )
```
Format: Currency, 0 dp

---

## Mapping back to the business questions

The challenge asks four specific questions. Here's which measure(s) and
visual to use for each.

### Q1. Total sales by store, category, and month

- **Measure**: `[Net Revenue]` (or `[Net Revenue (Completed)]`)
- **Visuals**:
  - Matrix: rows = `dim_store[store_name]`, columns = `dim_date[year_month]`,
    values = `[Net Revenue]`
  - Stacked bar: axis = `dim_date[year_month]`, legend =
    `dim_product[category]`, values = `[Net Revenue]`

### Q2. Top 10 customers by revenue

- **Measure**: `[Net Revenue]`
- **Visual**: Table or bar chart with `dim_customer[customer_name]` as the
  axis, sorted desc by `[Net Revenue]`. Apply a **Top N filter** on the
  visual: Top N = 10 by `[Net Revenue]`.

### Q3. Products with highest / lowest margins

- **Source**: this is a **dimension attribute**, not a measure — it lives
  on `dim_product[margin_pct]` (computed in dbt).
- **Visuals**:
  - Two tables side by side: `dim_product[product_name]` +
    `dim_product[margin_pct]`, one sorted desc (top 5 by margin), one
    sorted asc (bottom 5 by margin). Apply Top N filter = 5.
- **Optional measure** to surface margin issues:
  ```DAX
  Margin Issue Count =
  CALCULATE (
      COUNTROWS ( 'dim_product' ),
      'dim_product'[has_margin_issue] = TRUE
  )
  ```

### Q4. Sales performance over time

- **Measure**: `[Net Revenue]`, `[Revenue YoY %]`
- **Visuals**:
  - Line chart: x = `dim_date[date]` (drill: year → quarter → month → day),
    y = `[Net Revenue]`
  - Card: `[Revenue YoY %]` with the trend arrow

---

## Total count

Measures defined here: **15**

(6 revenue/profit, 4 volume, 2 completed-only, 5 time-intelligence — plus
the optional Margin Issue Count = 15 total. Drop the optional one if you
prefer 14.)
