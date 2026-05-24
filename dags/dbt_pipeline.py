from airflow import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

with DAG(
    dag_id='economic_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    ingest = TriggerDagRunOperator(
        task_id="trigger_ingest",
        trigger_dag_id="ingest_economic_data"
    )

    transform = TriggerDagRunOperator(
        task_id="trigger_dbt",
        trigger_dag_id="dbt_run_dag"
    )

    ingest >> transform