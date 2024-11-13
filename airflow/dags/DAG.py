from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'daily_clothing_crawler',
    default_args=default_args,
    description='A DAG to run clothing shop crawler daily',
    schedule_interval='@daily',
    start_date=datetime(2023, 11, 7),
    catchup=False,
) as dag:
    
    # Task to run the crawler script
    run_crawler = BashOperator(
        task_id='run_main_py',
        bash_command="python3 /opt/airflow/app/main.py"
,
    )

    run_crawler