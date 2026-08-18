with events as (
    select *
    from {{ref('stg_police_events')}}
), 

event_types as (
    select * 
    from {{ref('dim_event_type')}}
),

dates as (
    select *
    from {{ref('dim_date')}}
),

locations as (
    select *
    from {{ref('dim_location')}}
)

select
    e.event_id,
    e.event_datetime,
    e.event_name,
    e.event_summary,
    e.event_url,
    et.event_type_key,
    d.date_key,
    l.location_key,
    e.ingested_at
from events e
left join event_types et
    on e.event_type = et.event_type
left join dates d
    on e.event_datetime::date = d.date
left join locations l
    on e.location_gps = l.location_gps
    and e.location_name = l.location_name