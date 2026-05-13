# Connecting Power BI Desktop to the Pipeline

The Docker stack produces two artifacts that Power BI can read, both under
`warehouse/` on the host:

| Artifact | Path | How Power BI connects |
| --- | --- | --- |
| DuckDB database | `warehouse/retail_data.db` | DuckDB ODBC driver (primary) |
| Parquet exports | `warehouse/parquet/*.parquet` | Native "Parquet" connector (fallback) |

Both paths see the **same data** (the parquet files are written by a dbt
post-step from the same marts tables), so pick whichever is less painful on
your Windows machine.

---

## Option A — DuckDB via ODBC (primary, matches the challenge wording)

### 1. Install the DuckDB ODBC driver on the Windows machine

1. Go to <https://github.com/duckdb/duckdb/releases> and find the latest
   stable release.
2. Under "Assets", download `duckdb_odbc-windows-amd64.zip` (or the arm64
   variant on Surface ARM).
3. Unzip somewhere stable (e.g. `C:\Program Files\duckdb_odbc`).
4. Right-click `odbc_install.exe` → **Run as administrator**. This registers
   the driver with Windows ODBC.

### 2. Create a DSN

1. Open **ODBC Data Sources (64-bit)** from the Start menu.
2. **User DSN** tab → **Add...** → select **DuckDB Driver** → **Finish**.
3. Fill in:
   - **Data Source Name**: `retail_data`
   - **Database**: full Windows path to the `.db` file, e.g.
     `C:\Users\<you>\repos\skypointtest\warehouse\retail_data.db`
   - Leave other fields default.
4. **OK** to save.

> If the repo lives on a network share or a path with spaces, prefer copying
> the `.db` file to a local path with no spaces — the ODBC driver is picky.

### 3. Connect from Power BI Desktop

1. **Home → Get Data → More...** → search **ODBC** → **Connect**.
2. **Data source name (DSN)** → pick `retail_data` → **OK**.
3. In Navigator, expand `retail_data` → `marts` and check:
   - `dim_customer`
   - `dim_product`
   - `dim_store`
   - `dim_date`
   - `fct_sales`
4. **Transform Data** (lets you set types and clean column names before
   loading), then **Close & Apply**.

> Do **not** load the `raw` or `staging` schemas — those are internal to the
> pipeline and will clutter the semantic model.

### 4. Refresh behavior

The DuckDB file is **read at refresh time**, so re-running
`docker compose up --build` produces a new `.db` and the next Power BI
refresh picks up the new data automatically — no path changes needed.

---

## Option B — Parquet files (fallback)

If the ODBC driver is uncooperative on your Windows machine, the same data
is available as Parquet under `warehouse/parquet/`. This is just a fallback
path — the canonical answer to the challenge is Option A.

1. Power BI Desktop → **Home → Get Data → More... → File → Parquet**.
2. For each mart file you want, paste the Windows path:
   `C:\path\to\repo\warehouse\parquet\dim_customer.parquet` (and so on for
   the four other tables).
3. Click **OK** → **Load**.
4. Rename each loaded query so it matches the table name (`dim_customer`,
   `dim_product`, etc.).

Parquet preserves types, so the cleaned/cast types from dbt (DATE, DECIMAL,
INTEGER) come through directly — no Power Query type conversions needed.

### Folder-based load (faster than five individual files)

Alternative: **Get Data → Folder** → point at `warehouse/parquet/`. This
loads a table of file metadata; then in Power Query, expand the `Content`
column with the Parquet connector. Slightly fiddlier but the whole folder
re-imports if you add tables later.

---

## Sanity check the connection

Once tables are loaded, in Power BI's **Data view**:

| Table | Expected row count |
| --- | --- |
| dim_customer | 497 |
| dim_product | 100 |
| dim_store | 20 |
| dim_date | 4,018 |
| fct_sales | 14,052 |

If your row counts match these, the connection and data flow are sound and
you're ready to build relationships → see [semantic_model.md](semantic_model.md).
