"""
Load CSVs from a landing directory into a DuckDB file under the `raw` schema.

All columns are loaded as VARCHAR so that the raw layer faithfully preserves
the source data (including the deliberately seeded data-quality issues).
Downstream dbt staging models are responsible for casting and cleaning.

Environment variables (with defaults for the Docker container):
    LANDING_DIR   directory containing the input CSVs       (/data/landing)
    DB_PATH       path to the DuckDB database file          (/data/warehouse/retail_data.db)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import duckdb

LANDING_DIR = Path(os.environ.get("LANDING_DIR", "/data/landing"))
DB_PATH = Path(os.environ.get("DB_PATH", "/data/warehouse/retail_data.db"))
RAW_SCHEMA = "raw"

# filename -> table name (created as raw.<table>)
TABLES = {
    "customers.csv": "customers",
    "products.csv": "products",
    "stores.csv": "stores",
    "orders.csv": "orders",
    "order_items.csv": "order_items",
}


def main() -> int:
    if not LANDING_DIR.exists():
        print(f"ERROR: landing dir {LANDING_DIR} does not exist",
              file=sys.stderr)
        return 1

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to DuckDB at {DB_PATH}")
    con = duckdb.connect(str(DB_PATH))

    con.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")
    print(f"Schema `{RAW_SCHEMA}` ready.")

    missing = []
    for filename, table in TABLES.items():
        csv_path = LANDING_DIR / filename
        if not csv_path.exists():
            print(f"  SKIP {filename}: not found in {LANDING_DIR}",
                  file=sys.stderr)
            missing.append(filename)
            continue

        fq_table = f"{RAW_SCHEMA}.{table}"
        # all_varchar=true preserves source values verbatim for the raw layer.
        # Path is from a controlled allow-list above, not user input.
        con.execute(f"""
            CREATE OR REPLACE TABLE {fq_table} AS
            SELECT * FROM read_csv_auto(
                '{csv_path.as_posix()}',
                header=true,
                all_varchar=true
            )
        """)
        n = con.execute(f"SELECT COUNT(*) FROM {fq_table}").fetchone()[0]
        print(f"  loaded {n:>6} rows -> {fq_table}")

    con.close()

    if missing:
        print(f"WARNING: {len(missing)} expected file(s) were missing: "
              f"{missing}", file=sys.stderr)
        return 2

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
