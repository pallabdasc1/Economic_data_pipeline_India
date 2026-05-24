{{ config(materialized='table') }}

with base as (

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

    from {{ ref('int_economic_growth') }}
),

final as (

    select
        country,
        year,

        -- core metrics
        gdp,
        gdp_growth,
        gdp_per_capita,
        inflation,
        unemployment,
        population,

        -- growth classification
        case 
            when gdp_growth >= 7 then 'High Growth'
            when gdp_growth between 3 and 7 then 'Moderate Growth'
            when gdp_growth < 3 then 'Low Growth'
            else 'Unknown'
        end as growth_category,

        -- economic strength index (NEW)
        case
            when gdp_growth > 5 and unemployment < 5 then 'Strong Economy'
            when gdp_growth < 0 then 'Recession'
            else 'Average Economy'
        end as economic_strength,

        -- inflation pressure (NEW)
        case
            when inflation >= 6 then 'High Pressure'
            when inflation between 2 and 6 then 'Normal'
            else 'Low Pressure'
        end as inflation_pressure,

        -- labor market signal (NEW)
        case
            when unemployment >= 8 then 'Weak Labor Market'
            when unemployment < 4 then 'Strong Labor Market'
            else 'Moderate Labor Market'
        end as labor_market_status,

        -- population trend
        case
            when population_change > 0 then 'Growing Population'
            when population_change < 0 then 'Declining Population'
            else 'Stable Population'
        end as population_trend,

        -- carry forward key insights
        inflation_category,
        unemployment_category,
        economic_condition

    from base
)

select
    country,
    year,
    gdp,
    gdp_growth,
    gdp_per_capita,
    inflation,
    inflation_pressure,
    unemployment,
    labor_market_status,
    population,
    population_trend,
    growth_category,
    economic_strength,
    economic_condition,
    inflation_category,
    unemployment_category
from final
order by country, year