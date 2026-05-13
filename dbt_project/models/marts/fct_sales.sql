with items as (
    select * from {{ ref('stg_order_items') }}
),
orders as (
    select * from {{ ref('stg_orders') }}
),
products as (
    select * from {{ ref('stg_products') }}
),
customers as (
    select * from {{ ref('stg_customers') }}
),
stores as (
    select * from {{ ref('stg_stores') }}
),

joined as (
    select
        md5(cast(i.order_id as varchar) || '|' || cast(i.product_id as varchar)) as sales_key,
        i.order_id,
        o.customer_id,
        o.store_id,
        i.product_id,
        o.order_date,
        cast(strftime(o.order_date, '%Y%m%d') as integer)                 as date_key,
        o.status,
        i.quantity,
        p.unit_price,
        p.unit_cost,
        i.discount_pct,

        -- measures
        (i.quantity * p.unit_price)                                       as gross_revenue,
        (i.quantity * p.unit_price * i.discount_pct)                      as discount_amount,
        (i.quantity * p.unit_price * (1 - i.discount_pct))                as net_revenue,
        (i.quantity * p.unit_cost)                                        as total_cost,
        (i.quantity * p.unit_price * (1 - i.discount_pct))
            - (i.quantity * p.unit_cost)                                  as gross_profit
    from items     i
    inner join orders    o on o.order_id    = i.order_id     -- drops orphan order_id and bad-date orders
    inner join products  p on p.product_id  = i.product_id   -- drops orphan product_id
    inner join customers c on c.customer_id = o.customer_id  -- drops orders w/ orphan customer FK
    inner join stores    s on s.store_id    = o.store_id     -- drops orders w/ orphan store FK
)

select * from joined
