with event_type as (
    select distinct
        event_type
    from {{ref('stg_police_events')}}
)

select 
    {{ dbt_utils.generate_surrogate_key(['event_type']) }} as event_type_key,
    event_type
from event_type
