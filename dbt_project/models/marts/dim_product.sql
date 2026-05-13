select
    product_id,
    product_name,
    category,
    sub_category,
    unit_cost,
    unit_price,
    case
        when unit_price is null or unit_price = 0 then null
        else round((unit_price - unit_cost) / unit_price, 4)
    end as margin_pct,
    has_margin_issue
from {{ ref('stg_products') }}
