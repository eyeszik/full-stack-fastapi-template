# Automation Examples

This directory contains ready-to-use examples for integrating the FastAPI template into various automation frameworks.

## Quick Start Examples

### 1. Python Script Automation (`quickstart_python.py`)

Simple Python script demonstrating core automation patterns.

**Features:**
- User provisioning automation
- Bulk data export to CSV
- Scheduled cleanup tasks
- Complete integration workflow

**Usage:**
```bash
# Install dependencies
pip install requests pandas python-dotenv

# Set environment variables
export ADMIN_EMAIL="admin@example.com"
export ADMIN_PASSWORD="changethis"

# Run automation
python quickstart_python.py
```

**Example Output:**
```
🚀 Starting automation workflow...

Step 1: User Provisioning
----------------------------------------
✅ Created user: user1@example.com
✅ Created user: user2@example.com
✅ Created user: user3@example.com

📊 Summary: 3/3 users created

Step 2: Data Export
----------------------------------------
✅ Exported 15 users to users_export.csv

Step 3: Cleanup Check
----------------------------------------
Found inactive user: old_user@example.com
📊 Cleanup Summary: 1 inactive users found

✅ Workflow complete!
```

---

### 2. Apache Airflow DAG (`airflow_dag.py`)

Production-ready Airflow DAG for ETL workflows.

**Features:**
- Authentication with token caching
- Extract-Transform-Load (ETL) pipeline
- Data warehouse integration
- Automated reporting
- Retry logic and error handling

**Setup:**
```bash
# Install Airflow
pip install apache-airflow requests pandas

# Initialize Airflow
airflow db init

# Set variables
airflow variables set fastapi_base_url "http://localhost:8000"
airflow variables set fastapi_admin_email "admin@example.com"
airflow variables set fastapi_admin_password "changethis"

# Copy DAG to Airflow folder
cp airflow_dag.py ~/airflow/dags/

# Start Airflow
airflow scheduler &
airflow webserver
```

**DAG Structure:**
```
authenticate → extract_users → transform_users → load_to_warehouse
                                               → generate_report
```

---

### 3. n8n Workflow (`n8n_workflow.json`)

No-code automation workflow for n8n.

**Features:**
- Visual workflow builder
- HTTP request nodes for API calls
- Data transformation
- Google Sheets integration
- Slack notifications

**Setup:**
1. Import `n8n_workflow.json` into n8n
2. Configure credentials
3. Activate workflow

---

### 4. GitHub Actions (`github_actions_example.yml`)

CI/CD automation example.

**Features:**
- Automated testing on PR
- Database migrations
- Deployment automation
- Rollback on failure

---

## Integration Patterns

### Pattern 1: Scheduled Data Sync

Sync data from external source to FastAPI backend daily.

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from quickstart_python import FastAPIClient

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=2)
def daily_sync():
    client = FastAPIClient(base_url="http://localhost:8000")
    client.authenticate("admin@example.com", "changethis")

    # Your sync logic here
    external_data = fetch_from_external_source()
    for item in external_data:
        client.create_item(title=item['name'], description=item['desc'])

scheduler.start()
```

### Pattern 2: Event-Driven Automation

React to webhook events.

```python
from flask import Flask, request
from quickstart_python import FastAPIClient

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json

    client = FastAPIClient(base_url="http://localhost:8000")
    client.authenticate("admin@example.com", "changethis")

    if data['event'] == 'user.created':
        # Send welcome email
        send_welcome_email(data['user']['email'])

    return {'status': 'ok'}

app.run(port=5000)
```

### Pattern 3: Multi-Tenant Automation

Automate tenant provisioning.

```python
def provision_tenant(tenant_name: str, admin_email: str):
    client = FastAPIClient(base_url="http://localhost:8000")
    client.authenticate("superadmin@example.com", "changethis")

    # Create tenant admin
    admin = client.create_user(
        email=admin_email,
        password=generate_random_password(),
        full_name=f"{tenant_name} Admin",
        is_superuser=False
    )

    # Create default resources
    for i in range(5):
        client.create_item(
            title=f"Default Item {i}",
            description=f"Default resource for {tenant_name}"
        )

    # Send credentials
    send_tenant_welcome_email(admin_email, admin['password'])

    return admin
```

---

## Advanced Use Cases

### Use Case 1: Data Warehouse Sync

Sync FastAPI data to Snowflake/BigQuery daily.

**Tools:** Airflow, dbt, FastAPI
**Frequency:** Daily at 2 AM
**Pattern:** Extract → Transform → Load

### Use Case 2: User Lifecycle Management

Automate user onboarding, access reviews, and offboarding.

**Tools:** Celery, FastAPI, Email service
**Triggers:** User events, scheduled tasks
**Pattern:** Event-driven + scheduled

### Use Case 3: Multi-Region Deployment

Deploy FastAPI instances across multiple regions.

**Tools:** Terraform, Docker, FastAPI
**Pattern:** Blue-green deployment
**Monitoring:** Health checks, metrics

### Use Case 4: API Gateway

Use FastAPI as authentication gateway for microservices.

**Tools:** FastAPI, Traefik, Kong
**Pattern:** Proxy with auth
**Features:** Rate limiting, JWT validation

---

## Testing Automation

Run automated tests before deployment:

```python
from quickstart_python import FastAPIClient

def test_automation():
    client = FastAPIClient(base_url="http://localhost:8000")

    # Test authentication
    token = client.authenticate("admin@example.com", "changethis")
    assert token is not None

    # Test user creation
    user = client.create_user("test@example.com", "TestPass123")
    assert user['email'] == "test@example.com"

    # Test item creation
    item = client.create_item("Test Item", "Description")
    assert item['title'] == "Test Item"

    print("✅ All automation tests passed!")

if __name__ == "__main__":
    test_automation()
```

---

## Troubleshooting

### Common Issues

**Issue:** Authentication fails
**Solution:** Check credentials and ensure backend is running

**Issue:** Rate limiting errors
**Solution:** Add delays between requests or increase rate limits

**Issue:** Database connection timeout
**Solution:** Check database health and connection pool settings

---

## Resources

- [Main Automation Guide](../MODULAR_AUTOMATION_GUIDE.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Airflow Documentation](https://airflow.apache.org)
- [n8n Documentation](https://docs.n8n.io)

---

**Need Help?** Open an issue on GitHub or check the main documentation.
