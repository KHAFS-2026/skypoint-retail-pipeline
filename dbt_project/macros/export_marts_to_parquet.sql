{# Exports each marts table to a single .parquet file so Power BI can
   connect to flat files as a fallback if the DuckDB ODBC driver isn't
   available. Output dir is controlled by the PARQUET_DIR env var
   (defaults to /data/warehouse/parquet) and must exist when this runs. #}
{% macro export_marts_to_parquet() %}
    {% set output_dir = env_var('PARQUET_DIR', '/data/warehouse/parquet') %}
    {% set tables = ['dim_customer', 'dim_product', 'dim_store', 'dim_date', 'fct_sales'] %}
    {% for t in tables %}
        {% set path = output_dir ~ '/' ~ t ~ '.parquet' %}
        {% set sql %}
            COPY (SELECT * FROM marts.{{ t }}) TO '{{ path }}' (FORMAT 'parquet')
        {% endset %}
        {% do run_query(sql) %}
        {{ log("Exported marts." ~ t ~ " -> " ~ path, info=true) }}
    {% endfor %}
{% endmacro %}
