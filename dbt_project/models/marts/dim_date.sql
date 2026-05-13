with date_range as (
    select range::date as date_day
    from range(date '2020-01-01', date '2031-01-01', interval 1 day)
)

select
    cast(strftime(date_day, '%Y%m%d') as integer)         as date_key,
    date_day                                              as date,
    extract(year    from date_day)                        as year,
    extract(quarter from date_day)                        as quarter,
    extract(month   from date_day)                        as month,
    strftime(date_day, '%B')                              as month_name,
    extract(day     from date_day)                        as day,
    extract(dow     from date_day)                        as day_of_week,
    strftime(date_day, '%A')                              as day_name,
    case
        when extract(dow from date_day) in (0, 6) then true
        else false
    end                                                   as is_weekend,
    strftime(date_day, '%Y-%m')                           as year_month
from date_range
