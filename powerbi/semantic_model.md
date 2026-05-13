# Semantic Model

After loading the five marts tables (see [connection_setup.md](connection_setup.md)),
the model needs relationships, a marked date table, and a small amount of
column hygiene before the DAX measures will work cleanly.

---

## Relationships

A classic star schema — one fact, four dimensions. Build these in
**Model view → Manage relationships**.

| From (many) | To (one) | Cross-filter | Notes |
| --- | --- | --- | --- |
| `fct_sales[customer_id]` | `dim_customer[customer_id]` | Single | |
| `fct_sales[product_id]` | `dim_product[product_id]` | Single | |
| `fct_sales[store_id]` | `dim_store[store_id]` | Single | |
| `fct_sales[date_key]` | `dim_date[date_key]` | Single | active relationship |

All relationships are **many-to-one** (the fact side is the "many"). Keep
the default **single-direction** cross-filter — bi-directional filtering is
not needed for any of these business questions and tends to cause
ambiguity downstream.

---

## Mark dim_date as the date table

This unlocks time-intelligence DAX like `SAMEPERIODLASTYEAR`, `TOTALYTD`, etc.

1. Select `dim_date` in the **Fields** pane.
2. **Table tools** ribbon → **Mark as date table**.
3. Pick the column **`date`** (the actual DATE column, not `date_key`).
4. OK.

If you skip this, the time intelligence measures will still parse but won't
filter correctly across year boundaries.

---

## Hide foreign-key columns from the report view

These columns exist to make relationships work but shouldn't appear in
slicers or visuals. Right-click each → **Hide in report view**:

- `fct_sales[customer_id]`
- `fct_sales[product_id]`
- `fct_sales[store_id]`
- `fct_sales[date_key]`
- `dim_customer[customer_id]`
- `dim_product[product_id]`
- `dim_store[store_id]`
- `dim_date[date_key]`

Users should drag `dim_customer[customer_name]` (etc.) onto visuals — never
the raw IDs.

---

## Column renames (optional but polishing)

Power BI's auto-renaming from snake_case is decent. If you want fully
title-cased labels, rename in **Data view** (right-click column → Rename):

| Source column | Display name |
| --- | --- |
| `customer_name` | Customer |
| `product_name` | Product |
| `store_name` | Store |
| `unit_cost` | Unit Cost |
| `unit_price` | Unit Price |
| `margin_pct` | Margin % |
| `has_margin_issue` | Margin Issue Flag |
| `signup_date` | Signup Date |
| `opened_date` | Opened Date |
| `order_date` | Order Date |
| `year_month` | Year-Month |
| `day_of_week` | Day of Week |
| `day_name` | Day Name |
| `month_name` | Month Name |
| `is_weekend` | Is Weekend |

Renames in Power BI don't break DAX measures because they're applied on the
display side — but keep the original snake_case names handy for writing the
DAX itself.

---

## Format columns

In **Data view**, select the column and use the **Column tools** ribbon:

| Column(s) | Format |
| --- | --- |
| `dim_product[unit_cost]`, `dim_product[unit_price]` | Currency, 2 dp |
| `dim_product[margin_pct]` | Percentage, 1 dp |
| `dim_date[date]`, `dim_customer[signup_date]`, `dim_store[opened_date]` | Date, short |
| `dim_date[date_key]` | Whole number, no separator |
| `fct_sales[quantity]` | Whole number |
| `fct_sales[discount_pct]` | Percentage, 1 dp |

The fact-table measures (revenue, profit, etc.) inherit formatting from the
measure definitions in [dax_measures.md](dax_measures.md), so the underlying
columns don't need formatting.

---

## Sort by

For a tidier x-axis on month/day-of-week charts, set sort columns:

1. Select `dim_date[month_name]` → **Column tools → Sort by column** → pick
   `month`.
2. Select `dim_date[day_name]` → **Sort by column** → pick `day_of_week`.

Without these, "April" sorts alphabetically before "January".

---

## What you'll have after this

- 1 fact, 4 dimensions, all connected
- `dim_date` marked, time intelligence ready to use
- Surrogate keys hidden, friendly labels visible
- Columns formatted so visuals look clean before any DAX is written

Now you can add the DAX measures in [dax_measures.md](dax_measures.md).
