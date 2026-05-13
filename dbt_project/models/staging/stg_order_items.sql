with src as (
    select * from {{ source('raw', 'order_items') }}
),

casted as (
    select
        try_cast(order_id as integer)               as order_id,
        try_cast(product_id as integer)             as product_id,
        try_cast(quantity as integer)               as quantity,
        try_cast(discount_pct as decimal(5,2))      as discount_pct_raw
    from src
),

-- discount_pct is sometimes stored as a decimal (0.25) and sometimes as a
-- whole percent (25). Whole numbers in (1,100] are interpreted as percents;
-- anything outside [0,1] that isn't a whole percent is treated as junk.
normalized as (
    select
        order_id,
        product_id,
        quantity,
        case
            when discount_pct_raw is null then null
            when discount_pct_raw between 0 and 1 then discount_pct_raw
            when discount_pct_raw > 1
                and discount_pct_raw <= 100
                and discount_pct_raw = floor(discount_pct_raw)
                then discount_pct_raw / 100.0
            else null
        end as discount_pct
    from casted
),

dedup as (
    select *,
        row_number() over (partition by order_id, product_id order by quantity desc) as rn
    from normalized
)

select
    order_id,
    product_id,
    quantity,
    discount_pct
from dedup
where rn = 1
  and order_id is not null
  and product_id is not null
  and quantity is not null
  and quantity > 0
  and discount_pct is not null
  and discount_pct between 0 and 1
