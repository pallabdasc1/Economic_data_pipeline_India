{{ config(materialized='view') }}

with base as (

    select
        country_name as country,
        year,

        -- clean pivot using indicator_clean
        max(case when indicator_clean = 'gdp' then value end) as gdp,
        max(case when indicator_clean = 'inflation' then value end) as inflation,
        max(case when indicator_clean = 'unemployment' then value end) as unemployment,
        max(case when indicator_clean = 'population' then value end) as population

    from {{ ref('stg_economic_data') }}
    group by country_name, year
),

lagged as (

    -- compute lag once (cleaner + faster)
    select
        country,
        year,
        gdp,
        inflation,
        unemployment,
        population,

        lag(gdp) over (partition by country order by year) as prev_gdp,
        lag(inflation) over (partition by country order by year) as prev_inflation,
        lag(unemployment) over (partition by country order by year) as prev_unemployment,
        lag(population) over (partition by country order by year) as prev_population

    from base
),

final as (

    select
        country,
        year,

        -- core metrics
        gdp,
        inflation,
        unemployment,
        population,

        -- GDP insights
        prev_gdp,

        case 
            when prev_gdp is not null and prev_gdp != 0
            then (gdp - prev_gdp) / prev_gdp * 100
        end as gdp_growth,

        -- GDP per capita (NEW powerful metric)
        case
            when population is not null and population != 0
            then gdp / population
        end as gdp_per_capita,

        -- Inflation insights
        case
            when inflation >= 6 then 'High Inflation'
            when inflation between 2 and 6 then 'Moderate Inflation'
            when inflation < 2 then 'Low Inflation'
            else 'Unknown'
        end as inflation_category,

        inflation - prev_inflation as inflation_change,

        -- Unemployment insights
        case
            when unemployment >= 8 then 'High Unemployment'
            when unemployment between 4 and 8 then 'Moderate Unemployment'
            when unemployment < 4 then 'Low Unemployment'
            else 'Unknown'
        end as unemployment_category,

        unemployment - prev_unemployment as unemployment_change,

        -- Population insights (NEW)
        prev_population,
        population - prev_population as population_change,

        -- Combined macro signal
        case
            when inflation >= 6 and unemployment >= 8 then 'Stagflation Risk'
            when gdp < prev_gdp then 'Economic Slowdown'
            when gdp_growth > 5 and unemployment < 5 then 'Strong Growth'
            else 'Stable'
        end as economic_condition

    from lagged
)

select
    country,
    year,
    gdp,
    prev_gdp,
    gdp_growth,
    gdp_per_capita,
    inflation,
    inflation_category,
    inflation_change,
    unemployment,
    unemployment_category,
    unemployment_change,
    population,
    prev_population,
    population_change,
    economic_condition
from final
order by country, year