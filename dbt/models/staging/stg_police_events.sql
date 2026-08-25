select 
    event_id,
    payload ->> 'datetime' as event_datetime,
    payload ->> 'name' as event_name,
    payload ->> 'summary' as event_summary,
    payload ->> 'url' as event_url,
    payload ->> 'type' as event_type,
    payload -> 'location' ->> 'name' as location_name,
    payload -> 'location' ->> 'gps' as location_gps,
    ingested_at
from {{source('police', 'police_events')}}