FROM python:3.9-slim

WORKDIR /dbt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake the project into the image so it can run without a bind mount.
# In docker-compose this directory is also bind-mounted for live iteration.
COPY . .

ENV DBT_PROFILES_DIR=/dbt
ENV DBT_DUCKDB_PATH=/data/warehouse/retail_data.db
ENV PARQUET_DIR=/data/warehouse/parquet

# 1. dbt build = run models in dependency order + execute tests
# 2. ensure the parquet output dir exists (DuckDB COPY won't create it)
# 3. dump every marts.* table to a single .parquet file for Power BI fallback
CMD ["sh", "-c", "dbt build --target dev && mkdir -p \"$PARQUET_DIR\" && dbt run-operation export_marts_to_parquet --target dev"]
