with locations as (
    select distinct
        location_name,
        location_gps
    from {{ref('stg_police_events')}}
)

select
    {{ dbt_utils.generate_surrogate_key(['location_name', 'location_gps']) }} as location_key,
    location_name,
    split_part(location_gps, ',', 1)::numeric as latitude,
    split_part(location_gps, ',', 2)::numeric as longitude
from locations
