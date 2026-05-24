from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
import requests

DB_URI = "postgresql+psycopg2://airflow_user:airflow_pass@postgres:5432/airflow_db"

def fetch_economic_data():
    import requests
    import pandas as pd
    from sqlalchemy import create_engine
    from datetime import datetime

    indicators = [
        "NY.GDP.MKTP.CD",     # GDP
        "NY.GDP.MKTP.KD.ZG",  # GDP growth
        "FP.CPI.TOTL.ZG",     # Inflation
        "SL.UEM.TOTL.ZS",     # Unemployment
        "SP.POP.TOTL",        # Population
        "NE.EXP.GNFS.ZS",     # Exports
        "GC.DOD.TOTL.GD.ZS"   # Debt
    ]

    all_data = []

    for code in indicators:
        url = f"https://api.worldbank.org/v2/country/IND/indicator/{code}?format=json&per_page=1000"
        
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"API request failed for {code} with status {response.status_code}")

        data_json = response.json()

        if not isinstance(data_json, list) or len(data_json) < 2:
            continue

        data = data_json[1]

        df = pd.DataFrame(data)

        # Extract BOTH id and value (important!)
        df['country_id'] = df['country'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
        df['country_name'] = df['country'].apply(lambda x: x.get('value') if isinstance(x, dict) else None)

        df['indicator_id'] = df['indicator'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
        df['indicator_name'] = df['indicator'].apply(lambda x: x.get('value') if isinstance(x, dict) else None)

        #  Keep full raw structure
        df = df[[
            'indicator_id',
            'indicator_name',
            'country_id',
            'country_name',
            'countryiso3code',
            'date',
            'value',
            'unit',
            'obs_status',
            'decimal'
        ]]

        df['ingestion_time'] = datetime.utcnow()

        all_data.append(df)

    # Combine all data
    final_df = pd.concat(all_data, ignore_index=True)

    print(final_df.head())

    engine = create_engine(DB_URI)

    final_df.to_sql(
        'economic_raw_data',
        engine,
        if_exists='append',
        index=False
    )



def validate_data():
    engine = create_engine(DB_URI)
    df = pd.read_sql("SELECT * FROM economic_raw_data LIMIT 100", engine)

    assert not df.empty, "Data validation failed!"

with DAG(
    dag_id='economic_ingestion',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    ingest = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_economic_data
    )

    validate = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data
    )

    ingest >> validate