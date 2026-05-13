with src as (
    select * from {{ source('raw', 'customers') }}
),

cleaned as (
    select
        cast(customer_id as integer)                       as customer_id,
        trim(name)                                         as customer_name,
        case
            when nullif(trim(email), '') is null            then null
            when position('@' in email) = 0                 then null
            else lower(trim(email))
        end                                                as email,
        trim(city)                                         as city,
        case
            when lower(trim(country)) in ('usa', 'u.s.a.', 'us', 'united states')   then 'USA'
            when lower(trim(country)) in ('uk', 'u.k.', 'united kingdom')           then 'UK'
            when lower(trim(country)) in ('ca', 'canada')                            then 'Canada'
            when lower(trim(country)) in ('de', 'germany', 'deutschland')            then 'Germany'
            when lower(trim(country)) in ('au', 'australia')                         then 'Australia'
            else trim(country)
        end                                                as country,
        coalesce(
            try_strptime(signup_date, '%Y-%m-%d')::date,
            try_strptime(signup_date, '%m/%d/%Y')::date
        )                                                  as signup_date
    from src
),

dedup as (
    select *,
        row_number() over (partition by customer_id order by customer_name) as rn
    from cleaned
)

select
    customer_id,
    customer_name,
    email,
    city,
    country,
    signup_date
from dedup
where rn = 1
