with date_range as (
    select
        min(event_datetime::date) as min_date,
        max(event_datetime::date) as max_date
    from {{ref('stg_police_events')}}
),

dates as (
    select
        generate_series(
            min_date,
            max_date,
            interval '1 day'
        ) as date_day
    from date_range
)

select
    to_char(date_day, 'YYYYMMDD')::integer as date_key,
    date_day::date as date,
    extract(year from date_day)::integer as year,
    extract(quarter from date_day)::integer as quarter,
    extract(month from date_day)::integer as month,
    trim(to_char(date_day, 'Month')) as month_name,
    extract(day from date_day)::integer as day,
    extract(isodow from date_day)::integer as day_of_week,
    trim(to_char(date_day, 'Day')) as day_name
from dates
