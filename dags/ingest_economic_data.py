from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

def load_csv_to_postgres():
    df = pd.read_csv('/opt/airflow/data/economic_data.csv')

    engine = create_engine("postgresql+psycopg2://airflow:airflow@postgres:5432/airflow")

    df.to_sql('economic_data', engine, if_exists='replace', index=False)

with DAG(
    dag_id='ingest_economic_data',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    load_task = PythonOperator(
        task_id='load_csv',
        python_callable=load_csv_to_postgres
    )

    load_task