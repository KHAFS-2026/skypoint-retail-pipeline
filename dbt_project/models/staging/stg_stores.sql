select
    cast(store_id as integer)                                                  as store_id,
    trim(name)                                                                 as store_name,
    trim(region)                                                               as region,
    case
        when lower(trim(country)) in ('usa', 'u.s.a.', 'us', 'united states') then 'USA'
        when lower(trim(country)) in ('uk', 'u.k.', 'united kingdom')         then 'UK'
        when lower(trim(country)) in ('ca', 'canada')                          then 'Canada'
        when lower(trim(country)) in ('de', 'germany', 'deutschland')          then 'Germany'
        when lower(trim(country)) in ('au', 'australia')                       then 'Australia'
        else trim(country)
    end                                                                        as country,
    try_strptime(opened_date, '%Y-%m-%d')::date                                as opened_date
from {{ source('raw', 'stores') }}
