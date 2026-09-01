from datetime import datetime, timedelta
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator

API_BASE_URL = "http://4.213.215.203"

default_args = {
    "owner": "ruchi",
    "retries": 2,
    "retry_delay": timedelta(seconds=30),
}


def find_failed_runs(**context):
    response = requests.get(f"{API_BASE_URL}/runs", timeout=10)
    response.raise_for_status()
    runs = response.json()
    failed = [run for run in runs if run.get("status") == "ERROR"]
    print(f"Found {len(failed)} failed run(s) out of {len(runs)} recent runs.")
    context["ti"].xcom_push(key="failed_runs", value=failed)


def retry_failed_runs(**context):
    failed_runs = context["ti"].xcom_pull(key="failed_runs", task_ids="find_failed_runs")
    if not failed_runs:
        print("No failed runs to retry.")
        return

    success_count = 0
    failure_count = 0
    for run in failed_runs:
        prompt = run.get("prompt")
        try:
            response = requests.post(
                f"{API_BASE_URL}/generate",
                json={"prompt": prompt},
                timeout=60,
            )
            response.raise_for_status()
            success_count += 1
        except requests.RequestException as e:
            print(f"Retry failed for run {run.get('id')}: {e}")
            failure_count += 1

    total = success_count + failure_count
    success_rate = (success_count / total * 100) if total else 0
    print(
        f"Retried {total} run(s): {success_count} succeeded, {failure_count} failed. "
        f"Success rate: {success_rate:.1f}%"
    )


with DAG(
    dag_id="health_check_and_reprocess",
    default_args=default_args,
    description="Checks for failed AI App Builder runs and retries them",
    schedule=timedelta(minutes=15),
    start_date=datetime(2026, 9, 1),
    catchup=False,
    tags=["ai-app-builder"],
) as dag:

    find_failed = PythonOperator(
        task_id="find_failed_runs",
        python_callable=find_failed_runs,
    )

    retry_failed = PythonOperator(
        task_id="retry_failed_runs",
        python_callable=retry_failed_runs,
    )

    find_failed >> retry_failed