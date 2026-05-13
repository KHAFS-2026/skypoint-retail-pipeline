select
    store_id,
    store_name,
    region,
    country,
    opened_date
from {{ ref('stg_stores') }}
