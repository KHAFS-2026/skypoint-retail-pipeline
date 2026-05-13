with src as (
    select * from {{ source('raw', 'products') }}
),

casted as (
    select
        cast(product_id as integer)                    as product_id,
        trim(name)                                     as product_name,
        coalesce(nullif(trim(category), ''), 'Unknown') as category,
        nullif(trim(sub_category), '')                 as sub_category,
        try_cast(unit_cost as decimal(10,2))           as unit_cost,
        try_cast(unit_price as decimal(10,2))          as unit_price
    from src
)

select
    product_id,
    product_name,
    category,
    sub_category,
    unit_cost,
    unit_price,
    case
        when unit_price is null or unit_price <= 0 then true
        when unit_cost  is not null and unit_cost > unit_price then true
        else false
    end as has_margin_issue
from casted
