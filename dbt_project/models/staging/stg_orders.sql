with src as (
    select * from {{ source('raw', 'orders') }}
),

cleaned as (
    select
        cast(order_id as integer)                            as order_id,
        cast(customer_id as integer)                         as customer_id,
        cast(store_id as integer)                            as store_id,
        try_strptime(order_date, '%Y-%m-%d')::date           as order_date,
        case
            when lower(trim(status)) in ('completed', 'complete')         then 'completed'
            when lower(trim(status)) = 'pending'                          then 'pending'
            when lower(trim(status)) in ('cancelled', 'canceled')         then 'cancelled'
            when lower(trim(status)) = 'shipped'                          then 'shipped'
            when lower(trim(status)) = 'returned'                         then 'returned'
            when nullif(trim(status), '') is null                          then null
            else lower(trim(status))
        end                                                  as status
    from src
),

filtered as (
    -- drop impossible dates (year-2099 typos) and unparseable dates
    select *
    from cleaned
    where order_date is not null
      and order_date <= current_date
),

dedup as (
    select *,
        row_number() over (partition by order_id order by order_date) as rn
    from filtered
)

select order_id, customer_id, store_id, order_date, status
from dedup
where rn = 1
