"""
Apache Airflow DAG Example: FastAPI Template Integration
========================================================

This DAG demonstrates how to integrate the FastAPI template into
Apache Airflow for orchestrated data workflows.

Installation:
    pip install apache-airflow requests pandas

Setup:
    1. Copy this file to your Airflow DAGs folder
    2. Set Airflow variables:
       - fastapi_base_url
       - fastapi_admin_email
       - fastapi_admin_password
    3. Restart Airflow scheduler
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import requests
import pandas as pd
import logging

# Default arguments
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Initialize DAG
dag = DAG(
    'fastapi_data_pipeline',
    default_args=default_args,
    description='FastAPI template data pipeline',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    tags=['fastapi', 'data-pipeline'],
)


def authenticate(**context):
    """Authenticate and store token in XCom."""
    base_url = Variable.get("fastapi_base_url")
    email = Variable.get("fastapi_admin_email")
    password = Variable.get("fastapi_admin_password")

    response = requests.post(
        f"{base_url}/api/v1/login/access-token",
        data={"username": email, "password": password}
    )
    response.raise_for_status()

    token = response.json()["access_token"]
    logging.info("✅ Authentication successful")

    # Push token to XCom
    context['task_instance'].xcom_push(key='auth_token', value=token)


def extract_users(**context):
    """Extract users from FastAPI backend."""
    base_url = Variable.get("fastapi_base_url")
    token = context['task_instance'].xcom_pull(key='auth_token', task_ids='authenticate')

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{base_url}/api/v1/users/",
        headers=headers,
        params={"limit": 10000}
    )
    response.raise_for_status()

    users = response.json()["data"]
    logging.info(f"✅ Extracted {len(users)} users")

    # Push to XCom
    context['task_instance'].xcom_push(key='users', value=users)


def transform_users(**context):
    """Transform user data."""
    users = context['task_instance'].xcom_pull(key='users', task_ids='extract_users')

    # Convert to DataFrame
    df = pd.DataFrame(users)

    # Add derived columns
    df['is_admin'] = df['is_superuser']
    df['status'] = df['is_active'].map({True: 'active', False: 'inactive'})

    # Select relevant columns
    df_transformed = df[['id', 'email', 'full_name', 'is_admin', 'status']]

    logging.info(f"✅ Transformed {len(df_transformed)} records")

    # Push to XCom
    context['task_instance'].xcom_push(
        key='transformed_users',
        value=df_transformed.to_dict('records')
    )


def load_to_warehouse(**context):
    """Load data to data warehouse (example: write to CSV)."""
    users = context['task_instance'].xcom_pull(
        key='transformed_users',
        task_ids='transform_users'
    )

    df = pd.DataFrame(users)

    # In production, this would load to actual warehouse (Snowflake, BigQuery, etc.)
    output_file = f"/tmp/fastapi_users_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(output_file, index=False)

    logging.info(f"✅ Loaded {len(df)} records to {output_file}")


def generate_report(**context):
    """Generate daily report."""
    users = context['task_instance'].xcom_pull(
        key='transformed_users',
        task_ids='transform_users'
    )

    df = pd.DataFrame(users)

    # Calculate metrics
    total_users = len(df)
    active_users = len(df[df['status'] == 'active'])
    admin_users = len(df[df['is_admin'] == True])

    report = f"""
    📊 Daily User Report - {datetime.now().strftime('%Y-%m-%d')}
    ={'=' * 50}

    Total Users:   {total_users}
    Active Users:  {active_users} ({active_users/total_users*100:.1f}%)
    Admin Users:   {admin_users}

    ✅ Report generated successfully
    """

    logging.info(report)
    print(report)


# Define tasks
t1_auth = PythonOperator(
    task_id='authenticate',
    python_callable=authenticate,
    dag=dag,
)

t2_extract = PythonOperator(
    task_id='extract_users',
    python_callable=extract_users,
    dag=dag,
)

t3_transform = PythonOperator(
    task_id='transform_users',
    python_callable=transform_users,
    dag=dag,
)

t4_load = PythonOperator(
    task_id='load_to_warehouse',
    python_callable=load_to_warehouse,
    dag=dag,
)

t5_report = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    dag=dag,
)

# Define task dependencies
t1_auth >> t2_extract >> t3_transform >> [t4_load, t5_report]
