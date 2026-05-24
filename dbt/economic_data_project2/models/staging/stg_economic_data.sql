{{ config(materialized='view') }}

select
    cast(indicator_id as text)          as indicator_id,
    cast(indicator_name as text)        as indicator_name,
    cast(country_id as text)            as country_id,
    cast(country_name as text)          as country_name,
    cast(countryiso3code as text)       as countryiso3code,
    
    cast(date as integer)               as year,
    
    cast(value as numeric)              as value,
    cast(unit as text)                  as unit,
    cast(obs_status as text)            as obs_status,
    cast(decimal as integer)            as decimal,
    
    cast(ingestion_time as timestamp)   as ingestion_time

from {{ source('raw', 'economic_raw_data') }}