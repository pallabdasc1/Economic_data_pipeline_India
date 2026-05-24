from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id='dbt_run_dag',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False
) as dag:

    dbt_run = BashOperator(
        task_id='dbt_run',
        #bash_command='cd /opt/airflow/dbt && dbt run'
        bash_command='dbt run --project-dir /opt/airflow/dbt/economic_data_project2 --profiles-dir /opt/airflow/dbt'
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        #bash_command='cd /opt/airflow/dbt && dbt test'
        bash_command='dbt test --project-dir /opt/airflow/dbt/economic_data_project2 --profiles-dir /opt/airflow/dbt'
    )

    dbt_run >> dbt_test