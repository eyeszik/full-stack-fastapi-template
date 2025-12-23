# Full-Stack FastAPI Template - Modular Automation Guide

**Version:** 2.0
**Last Updated:** 2025-12-23
**Purpose:** Transform this repository into modular, reusable components for automation frameworks

---

## Table of Contents

1. [Executive Overview](#executive-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Modular Components Catalog](#modular-components-catalog)
4. [Automation Workflow Patterns](#automation-workflow-patterns)
5. [Integration Strategies](#integration-strategies)
6. [Copy-Paste Module Templates](#copy-paste-module-templates)
7. [API Reference](#api-reference)
8. [Deployment Automation](#deployment-automation)
9. [Testing Automation](#testing-automation)
10. [Advanced Workflows](#advanced-workflows)

---

## Executive Overview

### What This Repository Provides

This full-stack FastAPI template is a **production-ready, modular application framework** that provides:

- **Authentication System** - JWT-based auth with password recovery
- **User Management** - CRUD operations with role-based access control
- **Database Layer** - PostgreSQL + SQLModel ORM with migrations
- **API Layer** - FastAPI REST endpoints with auto-generated OpenAPI docs
- **Frontend Layer** - React + TypeScript SPA with auto-generated client
- **Email System** - Template-based email delivery
- **Testing Framework** - Backend (Pytest) + E2E (Playwright)
- **CI/CD Pipeline** - GitHub Actions workflows
- **Deployment Stack** - Docker Compose + Traefik reverse proxy

### Key Differentiators

✅ **Production-Ready:** Security best practices, proper password hashing, JWT tokens
✅ **Type-Safe:** Full TypeScript frontend, Pydantic/SQLModel backend
✅ **Auto-Generated Client:** OpenAPI schema → TypeScript SDK automatically
✅ **Modular Design:** Each component can be extracted and reused independently
✅ **Docker-First:** Development and production use identical containerized stack
✅ **Tested:** 90%+ code coverage, E2E tests with Playwright

### Use Cases for Automation

This template can be used as a **modular base** for:

1. **SaaS Application Scaffolding** - Start new projects in minutes
2. **Microservices Template** - Extract auth, user management as standalone services
3. **API Gateway Pattern** - Use backend as authentication proxy
4. **Multi-Tenant Systems** - Extend user model for tenant isolation
5. **Automation Workflows** - Integrate as REST API backend for workflow engines
6. **Internal Tools** - Admin dashboards, CRUD interfaces for operations teams

---

## Architecture & Technology Stack

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT TIER                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React 18 + TypeScript + Vite                        │  │
│  │  - TanStack Router (routing)                         │  │
│  │  - TanStack Query (state + cache)                    │  │
│  │  - Chakra UI (components)                            │  │
│  │  - Auto-generated Axios client                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      REVERSE PROXY TIER                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Traefik 3.0                                         │  │
│  │  - Automatic HTTPS (Let's Encrypt)                   │  │
│  │  - Subdomain routing                                 │  │
│  │  - Load balancing                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                ┌─────────────┴──────────────┐
                │                            │
                ▼                            ▼
┌───────────────────────────┐  ┌───────────────────────────┐
│    API TIER (Backend)     │  │   FRONTEND TIER (Nginx)   │
│  ┌─────────────────────┐  │  │  ┌─────────────────────┐  │
│  │  FastAPI 0.114+     │  │  │  │  Nginx serving      │  │
│  │  - REST endpoints   │  │  │  │  React build        │  │
│  │  - JWT auth         │  │  │  │  - SPA routing      │  │
│  │  - SQLModel ORM     │  │  │  └─────────────────────┘  │
│  │  - Pydantic v2      │  │  │                           │
│  └─────────────────────┘  │  └───────────────────────────┘
└───────────────────────────┘
                │
                │ PostgreSQL Driver (psycopg)
                ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE TIER                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PostgreSQL 17                                       │  │
│  │  - Alembic migrations                                │  │
│  │  - UUID primary keys                                 │  │
│  │  - Cascade delete relationships                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack Matrix

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Backend Framework** | FastAPI | 0.114.2+ | High-performance async API |
| **Backend Language** | Python | 3.10+ | Modern Python with type hints |
| **ORM** | SQLModel | 0.0.21+ | Type-safe database operations |
| **Validation** | Pydantic | 2.0+ | Data validation and serialization |
| **Database** | PostgreSQL | 17 | Production SQL database |
| **Migrations** | Alembic | 1.12.1+ | Schema versioning |
| **Authentication** | JWT + OAuth2 | PyJWT | Token-based authentication |
| **Password Hashing** | Passlib (bcrypt) | Latest | Secure password storage |
| **Frontend Framework** | React | 18.2 | Modern UI library |
| **Frontend Language** | TypeScript | 5.2 | Type-safe JavaScript |
| **Build Tool** | Vite | 6.3.4 | Fast development builds |
| **Router** | TanStack Router | 1.19.1 | Type-safe routing |
| **State Management** | TanStack Query | 5.28.14 | Server state + caching |
| **UI Library** | Chakra UI | 3.8.0 | Component library |
| **HTTP Client** | Axios | 1.9.0 | Auto-generated from OpenAPI |
| **E2E Testing** | Playwright | 1.52.0 | Browser automation |
| **Backend Testing** | Pytest | 7.4.3+ | Python test framework |
| **Reverse Proxy** | Traefik | 3.0 | HTTPS + routing |
| **Containerization** | Docker | Latest | Consistent environments |
| **Orchestration** | Docker Compose | Latest | Multi-container apps |
| **Package Manager (Backend)** | uv | Latest | Fast Python deps |
| **Package Manager (Frontend)** | npm | Latest | JavaScript deps |

---

## Modular Components Catalog

Each component below can be extracted and reused independently in automation workflows.

### Component 1: Authentication Module

**Location:** `/backend/app/core/security.py` + `/backend/app/api/routes/login.py`

**Purpose:** Provides JWT-based authentication with OAuth2 password flow

**Features:**
- Password hashing with bcrypt
- JWT token generation (HS256 algorithm)
- Token validation and user extraction
- Password recovery via email tokens
- 8-day token expiration (configurable)

**Key Functions:**

```python
# Password Operations
get_password_hash(password: str) -> str
verify_password(plain_password: str, hashed_password: str) -> bool

# JWT Operations
create_access_token(subject: str | Any, expires_delta: timedelta) -> str

# Password Reset
generate_password_reset_token(email: str) -> str
verify_password_reset_token(token: str) -> str | None
```

**API Endpoints:**

```
POST /api/v1/login/access-token
  Input: {"username": "email", "password": "string"}
  Output: {"access_token": "jwt_token", "token_type": "bearer"}

POST /api/v1/login/test-token
  Input: Authorization header with JWT
  Output: {"email": "user@example.com"}

POST /api/v1/password-recovery/{email}
  Input: Email in URL
  Output: Sends password reset email

POST /api/v1/reset-password/
  Input: {"token": "reset_token", "new_password": "string"}
  Output: {"message": "Password updated successfully"}
```

**Automation Integration:**

```python
# Example: Automated user authentication
import requests

def authenticate_user(api_base_url: str, email: str, password: str) -> str:
    """
    Authenticate and return JWT token for automation workflows.

    Returns:
        JWT access token for subsequent API calls
    """
    response = requests.post(
        f"{api_base_url}/api/v1/login/access-token",
        data={"username": email, "password": password}
    )
    response.raise_for_status()
    return response.json()["access_token"]

# Usage in automation workflow
token = authenticate_user("http://localhost:8000", "admin@example.com", "changethis")
headers = {"Authorization": f"Bearer {token}"}
```

**Reusability Score:** ⭐⭐⭐⭐⭐ (Highly reusable - can be extracted as standalone auth service)

---

### Component 2: User Management Module

**Location:** `/backend/app/api/routes/users.py` + `/backend/app/crud.py`

**Purpose:** Complete CRUD operations for user management with RBAC

**Features:**
- User creation (admin + self-registration)
- User update (admin + self-update)
- User deletion (admin + self-delete)
- Role-based access control (superuser vs regular user)
- Email uniqueness validation
- Password strength validation (8-40 characters)

**Database Schema:**

```sql
CREATE TABLE user (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_user_email ON user(email);
```

**Data Models:**

```python
# Core Models
class User(SQLModel, table=True):
    id: uuid.UUID
    email: EmailStr (max 255 chars, unique, indexed)
    hashed_password: str
    full_name: str | None
    is_active: bool = True
    is_superuser: bool = False
    items: list[Item] (relationship with cascade delete)

# API Schemas
UserCreate - For admin user creation
UserRegister - For public signup
UserUpdate - For admin updates (includes password)
UserUpdateMe - For self-updates (no role changes)
UpdatePassword - For password changes (requires current password)
UserPublic - Public response (no password fields)
```

**API Endpoints:**

```
# Admin Endpoints (require superuser)
GET    /api/v1/users/?skip=0&limit=100
POST   /api/v1/users/
GET    /api/v1/users/{user_id}
PATCH  /api/v1/users/{user_id}
DELETE /api/v1/users/{user_id}

# User Self-Management
GET    /api/v1/users/me
PATCH  /api/v1/users/me
PATCH  /api/v1/users/me/password
DELETE /api/v1/users/me

# Public Endpoint
POST   /api/v1/users/signup
```

**CRUD Functions:**

```python
create_user(session: Session, user_create: UserCreate) -> User
update_user(session: Session, db_user: User, user_in: UserUpdate) -> User
get_user_by_email(session: Session, email: str) -> User | None
authenticate(session: Session, email: str, password: str) -> User | None
```

**Automation Integration:**

```python
# Example: Automated user provisioning
class UserAutomation:
    def __init__(self, api_base_url: str, admin_token: str):
        self.base_url = api_base_url
        self.headers = {"Authorization": f"Bearer {admin_token}"}

    def create_users_bulk(self, users: list[dict]) -> list[dict]:
        """
        Bulk user creation for automation workflows.

        Args:
            users: List of {"email": str, "password": str, "full_name": str, "is_superuser": bool}

        Returns:
            List of created user objects with IDs
        """
        created_users = []
        for user_data in users:
            response = requests.post(
                f"{self.base_url}/api/v1/users/",
                json=user_data,
                headers=self.headers
            )
            response.raise_for_status()
            created_users.append(response.json())
        return created_users

    def deactivate_inactive_users(self, inactive_days: int = 90) -> list[str]:
        """
        Automated user lifecycle management.
        Deactivate users who haven't logged in for N days.
        """
        # Implementation would check last_login and deactivate
        pass

# Usage
automation = UserAutomation("http://localhost:8000", admin_token)
new_users = automation.create_users_bulk([
    {"email": "user1@example.com", "password": "SecurePass123", "full_name": "User One"},
    {"email": "user2@example.com", "password": "SecurePass456", "full_name": "User Two"}
])
```

**Reusability Score:** ⭐⭐⭐⭐⭐ (Perfect for multi-tenant SaaS, admin panels, internal tools)

---

### Component 3: Database Layer Module

**Location:** `/backend/app/core/db.py` + `/backend/app/alembic/`

**Purpose:** PostgreSQL database management with SQLModel ORM and Alembic migrations

**Features:**
- Database engine initialization
- Session management with dependency injection
- Automatic migrations via Alembic
- UUID primary keys
- Cascade delete relationships
- Connection pooling
- Transaction management

**Configuration:**

```python
# Database URI Construction
SQLALCHEMY_DATABASE_URI = postgresql+psycopg://user:pass@host:port/dbname

# Engine Creation
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,  # Set to True for SQL logging
    pool_pre_ping=True  # Verify connections before using
)
```

**Session Management:**

```python
# Dependency Injection Pattern
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]

# Usage in API endpoints
@router.get("/items/")
def get_items(session: SessionDep, current_user: CurrentUser):
    statement = select(Item).where(Item.owner_id == current_user.id)
    items = session.exec(statement).all()
    return items
```

**Migration Workflow:**

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Add new field to user table"

# Review generated migration in app/alembic/versions/

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

**Alembic Configuration:**

```python
# app/alembic/env.py
from app.models import SQLModel

target_metadata = SQLModel.metadata

# Automatically detects model changes and generates migrations
```

**Automation Integration:**

```python
# Example: Database seeding automation
from sqlmodel import Session, create_engine
from app.models import User, Item
from app.crud import create_user
from app.core.config import settings

def seed_database_for_testing(num_users: int = 100, items_per_user: int = 10):
    """
    Automated database seeding for load testing or development.
    """
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    with Session(engine) as session:
        users = []
        for i in range(num_users):
            user = create_user(
                session=session,
                user_create=UserCreate(
                    email=f"test_user_{i}@example.com",
                    password="TestPassword123",
                    full_name=f"Test User {i}"
                )
            )
            users.append(user)

            # Create items for each user
            for j in range(items_per_user):
                item = Item(
                    title=f"Item {j} for User {i}",
                    description=f"Auto-generated item {j}",
                    owner_id=user.id
                )
                session.add(item)

        session.commit()

    print(f"Seeded {num_users} users with {num_users * items_per_user} total items")

# Database backup automation
def backup_database_to_s3(s3_bucket: str, backup_name: str):
    """
    Automated database backup to S3.
    """
    import subprocess
    import boto3

    # Dump database
    dump_file = f"/tmp/{backup_name}.sql"
    subprocess.run([
        "pg_dump",
        "-h", settings.POSTGRES_SERVER,
        "-U", settings.POSTGRES_USER,
        "-d", settings.POSTGRES_DB,
        "-f", dump_file
    ], env={"PGPASSWORD": settings.POSTGRES_PASSWORD})

    # Upload to S3
    s3 = boto3.client('s3')
    s3.upload_file(dump_file, s3_bucket, f"backups/{backup_name}.sql")
```

**Reusability Score:** ⭐⭐⭐⭐⭐ (Database layer can be reused across any SQLModel project)

---

### Component 4: Email System Module

**Location:** `/backend/app/utils.py` + `/backend/app/email-templates/`

**Purpose:** Template-based email delivery with SMTP support

**Features:**
- MJML email templates (responsive HTML emails)
- Jinja2 template rendering
- SMTP with TLS/SSL support
- Password reset emails
- Welcome emails
- Test email functionality
- MailCatcher for local development

**Email Templates:**

```
email-templates/
├── src/              # MJML source files (edit these)
│   ├── reset_password.mjml
│   ├── new_account.mjml
│   └── test_email.mjml
└── build/            # Compiled HTML (auto-generated)
    ├── reset_password.html
    ├── new_account.html
    └── test_email.html
```

**Configuration:**

```python
# .env settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=True
SMTP_SSL=False
EMAILS_FROM_EMAIL=noreply@yourapp.com
EMAILS_FROM_NAME=Your App Name
```

**Email Functions:**

```python
def render_email_template(template_name: str, context: dict[str, Any]) -> str:
    """Render Jinja2 email template with context variables."""

def send_email(
    email_to: str,
    subject: str,
    html_content: str
) -> None:
    """Send email via SMTP."""

def generate_test_email(email_to: str) -> Message:
    """Generate test email."""

def generate_reset_password_email(email_to: str, token: str) -> Message:
    """Generate password reset email with token."""

def generate_new_account_email(email_to: str, username: str) -> Message:
    """Generate welcome email for new users."""
```

**Automation Integration:**

```python
# Example: Automated email campaigns
class EmailAutomation:
    def __init__(self):
        self.smtp_config = {
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "user": settings.SMTP_USER,
            "password": settings.SMTP_PASSWORD,
        }

    def send_bulk_emails(self, recipients: list[dict], template: str):
        """
        Send bulk emails with personalization.

        Args:
            recipients: [{"email": str, "name": str, "custom_data": dict}, ...]
            template: Name of email template
        """
        for recipient in recipients:
            context = {
                "name": recipient["name"],
                "email": recipient["email"],
                **recipient.get("custom_data", {})
            }
            html_content = render_email_template(template, context)
            send_email(
                email_to=recipient["email"],
                subject=f"Hello {recipient['name']}",
                html_content=html_content
            )

    def schedule_password_reset_reminders(self):
        """
        Automated workflow: Send password reset reminders to users
        who haven't changed password in 90 days.
        """
        # Query users with old passwords
        # Generate reset tokens
        # Send reminder emails
        pass

# Monitoring automation
def monitor_email_delivery_rates():
    """
    Track email delivery, bounces, and opens.
    Integrate with SendGrid/Mailgun webhooks.
    """
    pass
```

**Reusability Score:** ⭐⭐⭐⭐ (Email module can be extracted for any application needing transactional emails)

---

### Component 5: Frontend Client Module

**Location:** `/frontend/src/client/` (auto-generated)

**Purpose:** Type-safe TypeScript API client auto-generated from OpenAPI schema

**Features:**
- Axios-based HTTP client
- Full TypeScript types for all endpoints
- Automatic request/response typing
- Error handling with type safety
- Auto-regeneration on backend changes

**Generation Command:**

```bash
cd frontend
npm run generate-client
# Runs: openapi-ts --client axios --output ./src/client
```

**Generated Structure:**

```
client/
├── index.ts           # Main exports
├── types.gen.ts       # TypeScript interfaces for all models
├── schemas.gen.ts     # JSON schemas
└── services.gen.ts    # API service methods
```

**Usage Examples:**

```typescript
// Type-safe API calls
import { LoginService, UsersService, ItemsService } from "@/client"

// Login
const loginData = await LoginService.loginAccessToken({
  body: {
    username: "user@example.com",
    password: "password123"
  }
})
const token = loginData.access_token

// Get current user (with automatic typing)
const currentUser = await UsersService.readUserMe()
// currentUser is typed as UserPublic

// Create item (TypeScript enforces required fields)
const newItem = await ItemsService.createItem({
  body: {
    title: "My Item",        // Required
    description: "Details"   // Optional
  }
})
// newItem is typed as ItemPublic

// Update user (partial updates supported)
const updatedUser = await UsersService.updateUserMe({
  body: {
    full_name: "New Name"  // Only updating name
  }
})
```

**TanStack Query Integration:**

```typescript
// Automatic caching, refetching, and optimistic updates
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { ItemsService } from "@/client"

function useItems() {
  return useQuery({
    queryKey: ["items"],
    queryFn: () => ItemsService.readItems({ skip: 0, limit: 100 })
  })
}

function useCreateItem() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: ItemCreate) => ItemsService.createItem({ body: data }),
    onSuccess: () => {
      // Invalidate and refetch items
      queryClient.invalidateQueries({ queryKey: ["items"] })
    }
  })
}

// Component usage
function ItemsList() {
  const { data: items, isLoading } = useItems()
  const createItem = useCreateItem()

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      {items?.data.map(item => <div key={item.id}>{item.title}</div>)}
      <button onClick={() => createItem.mutate({ title: "New Item" })}>
        Add Item
      </button>
    </div>
  )
}
```

**Automation Integration:**

```typescript
// Example: Automated API testing with generated client
import { LoginService, UsersService, ItemsService } from "@/client"

class AutomatedAPITester {
  private token: string = ""

  async authenticate() {
    const response = await LoginService.loginAccessToken({
      body: { username: "admin@example.com", password: "changethis" }
    })
    this.token = response.access_token
    // Set token for subsequent requests
    OpenAPI.TOKEN = this.token
  }

  async testUserWorkflow() {
    // Create user
    const newUser = await UsersService.createUser({
      body: {
        email: "test@example.com",
        password: "TestPass123",
        full_name: "Test User"
      }
    })

    // Verify user created
    const fetchedUser = await UsersService.readUserById({ userId: newUser.id })
    assert(fetchedUser.email === "test@example.com")

    // Update user
    const updatedUser = await UsersService.updateUser({
      userId: newUser.id,
      body: { full_name: "Updated Name" }
    })
    assert(updatedUser.full_name === "Updated Name")

    // Delete user
    await UsersService.deleteUser({ userId: newUser.id })
  }

  async testItemWorkflow() {
    // Similar automated testing for items
  }
}

// CI/CD integration
const tester = new AutomatedAPITester()
await tester.authenticate()
await tester.testUserWorkflow()
await tester.testItemWorkflow()
```

**Reusability Score:** ⭐⭐⭐⭐⭐ (Any frontend can consume the API with this auto-generated client)

---

### Component 6: Testing Framework Module

**Location:** `/backend/app/tests/` + `/frontend/tests/`

**Purpose:** Comprehensive testing infrastructure for backend and E2E testing

**Backend Testing (Pytest):**

```
backend/app/tests/
├── conftest.py              # Shared fixtures
├── utils/
│   ├── user.py              # User factory functions
│   └── item.py              # Item factory functions
├── api/routes/
│   ├── test_login.py        # Auth endpoint tests
│   ├── test_users.py        # User CRUD tests
│   └── test_items.py        # Item CRUD tests
└── crud/
    └── test_user.py         # CRUD function tests
```

**Key Testing Patterns:**

```python
# conftest.py - Test Database Setup
@pytest.fixture(scope="session")
def engine():
    # Create test database
    yield test_engine
    # Teardown

@pytest.fixture
def session(engine):
    with Session(engine) as session:
        yield session
        session.rollback()

@pytest.fixture
def client(session):
    # Override database dependency
    app.dependency_overrides[get_db] = lambda: session
    with TestClient(app) as test_client:
        yield test_client

# Test example
def test_create_user(client: TestClient, session: Session):
    data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = client.post("/api/v1/users/", json=data)
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["email"] == data["email"]
```

**Frontend E2E Testing (Playwright):**

```
frontend/tests/
├── auth.setup.ts            # Authentication setup
├── config.ts                # Test configuration
├── login.spec.ts            # Login flow tests
├── sign-up.spec.ts          # Registration tests
├── reset-password.spec.ts   # Password recovery tests
└── user-settings.spec.ts    # Settings management tests
```

**Playwright Test Example:**

```typescript
// login.spec.ts
import { test, expect } from "@playwright/test"

test("successful login", async ({ page }) => {
  await page.goto("/login")

  await page.fill('input[name="username"]', "admin@example.com")
  await page.fill('input[name="password"]', "changethis")
  await page.click('button[type="submit"]')

  // Should redirect to dashboard
  await expect(page).toHaveURL(/.*dashboard/)

  // Should see user menu
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible()
})

test("failed login with wrong password", async ({ page }) => {
  await page.goto("/login")

  await page.fill('input[name="username"]', "admin@example.com")
  await page.fill('input[name="password"]', "wrongpassword")
  await page.click('button[type="submit"]')

  // Should show error message
  await expect(page.locator("text=Incorrect email or password")).toBeVisible()
})
```

**Automation Integration:**

```python
# Example: Automated regression testing
class AutomatedTestRunner:
    def __init__(self):
        self.backend_passed = 0
        self.backend_failed = 0
        self.e2e_passed = 0
        self.e2e_failed = 0

    def run_backend_tests(self) -> dict:
        """Run pytest with coverage reporting."""
        result = subprocess.run(
            ["pytest", "backend/app/tests", "--cov=app", "--cov-report=json"],
            capture_output=True
        )

        # Parse coverage report
        with open("coverage.json") as f:
            coverage_data = json.load(f)

        return {
            "passed": result.returncode == 0,
            "coverage": coverage_data["totals"]["percent_covered"],
            "output": result.stdout.decode()
        }

    def run_e2e_tests(self, shard: int = 1, total_shards: int = 4) -> dict:
        """Run Playwright tests with sharding for parallel execution."""
        result = subprocess.run(
            [
                "npx", "playwright", "test",
                f"--shard={shard}/{total_shards}"
            ],
            cwd="frontend",
            capture_output=True
        )

        return {
            "passed": result.returncode == 0,
            "shard": shard,
            "output": result.stdout.decode()
        }

    def run_full_test_suite(self) -> dict:
        """
        Automated workflow: Run all tests in parallel.
        """
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Run backend tests
            backend_future = executor.submit(self.run_backend_tests)

            # Run E2E tests in 4 parallel shards
            e2e_futures = [
                executor.submit(self.run_e2e_tests, shard=i, total_shards=4)
                for i in range(1, 5)
            ]

            # Collect results
            backend_result = backend_future.result()
            e2e_results = [f.result() for f in e2e_futures]

        return {
            "backend": backend_result,
            "e2e": e2e_results,
            "all_passed": backend_result["passed"] and all(r["passed"] for r in e2e_results)
        }

# CI/CD integration
runner = AutomatedTestRunner()
results = runner.run_full_test_suite()

if not results["all_passed"]:
    print("Tests failed!")
    sys.exit(1)
else:
    print(f"All tests passed! Coverage: {results['backend']['coverage']}%")
```

**Reusability Score:** ⭐⭐⭐⭐⭐ (Testing patterns can be reused across any FastAPI + React project)

---

### Component 7: CI/CD Pipeline Module

**Location:** `.github/workflows/`

**Purpose:** Automated testing, deployment, and release management

**Available Workflows:**

| Workflow | Trigger | Purpose | Key Features |
|----------|---------|---------|--------------|
| `test-backend.yml` | Push, PR | Backend tests | Pytest + coverage |
| `playwright.yml` | Push, PR, manual | E2E tests | 4-shard parallel execution |
| `lint-backend.yml` | Push, PR | Code quality | Ruff linting |
| `generate-client.yml` | Backend changes | Auto-gen client | Creates PR with updated client |
| `deploy-staging.yml` | Push to master | Staging deploy | Self-hosted runner |
| `deploy-production.yml` | Release published | Production deploy | Self-hosted runner |
| `latest-changes.yml` | PR merge | Release notes | Auto-updates changelog |

**Backend Test Workflow:**

```yaml
# .github/workflows/test-backend.yml
name: Backend Tests

on:
  push:
    branches: [master]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: changethis
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

      mailcatcher:
        image: schickling/mailcatcher

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: cd backend && uv sync

      - name: Run migrations
        run: cd backend && source .venv/bin/activate && alembic upgrade head

      - name: Run tests
        run: cd backend && source .venv/bin/activate && pytest --cov=app --cov-report=html

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: backend/htmlcov/
```

**Playwright E2E Workflow:**

```yaml
# .github/workflows/playwright.yml
name: Playwright E2E Tests

on:
  push:
  pull_request:
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false
      matrix:
        shardIndex: [1, 2, 3, 4]
        shardTotal: [4]

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker images
        run: docker compose build

      - name: Start services
        run: docker compose up -d

      - name: Wait for backend
        run: docker compose exec backend bash /app/scripts/prestart.sh

      - name: Run Playwright tests
        run: |
          docker compose exec playwright \
            npx playwright test --shard=${{ matrix.shardIndex }}/${{ matrix.shardTotal }}

      - name: Upload blob report
        uses: actions/upload-artifact@v4
        with:
          name: blob-report-${{ matrix.shardIndex }}
          path: frontend/blob-report/

  merge-reports:
    needs: test
    runs-on: ubuntu-latest

    steps:
      - uses: actions/download-artifact@v4
        with:
          pattern: blob-report-*
          path: all-blob-reports

      - name: Merge reports
        run: npx playwright merge-reports --reporter html ./all-blob-reports

      - name: Upload HTML report
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
```

**Automated Client Generation:**

```yaml
# .github/workflows/generate-client.yml
name: Generate Frontend Client

on:
  push:
    paths:
      - 'backend/app/**/*.py'

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Start backend
        run: docker compose up -d backend

      - name: Generate client
        run: |
          cd frontend
          npm install
          npm run generate-client

      - name: Create PR
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "Auto-generate frontend client"
          title: "chore: Update frontend client from OpenAPI schema"
          body: "Auto-generated TypeScript client from backend API changes"
          branch: auto-generate-client
```

**Deployment Workflow:**

```yaml
# .github/workflows/deploy-production.yml
name: Deploy Production

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: [self-hosted, production]

    steps:
      - uses: actions/checkout@v4

      - name: Create .env file
        run: |
          cat > .env << EOF
          DOMAIN=${{ secrets.DOMAIN_PRODUCTION }}
          ENVIRONMENT=production
          PROJECT_NAME=${{ secrets.PROJECT_NAME }}
          SECRET_KEY=${{ secrets.SECRET_KEY }}
          FIRST_SUPERUSER=${{ secrets.FIRST_SUPERUSER }}
          FIRST_SUPERUSER_PASSWORD=${{ secrets.FIRST_SUPERUSER_PASSWORD }}
          POSTGRES_PASSWORD=${{ secrets.POSTGRES_PASSWORD }}
          SMTP_HOST=${{ secrets.SMTP_HOST }}
          SMTP_USER=${{ secrets.SMTP_USER }}
          SMTP_PASSWORD=${{ secrets.SMTP_PASSWORD }}
          EMAILS_FROM_EMAIL=${{ secrets.EMAILS_FROM_EMAIL }}
          EOF

      - name: Build and deploy
        run: |
          docker compose -f docker-compose.yml build
          docker compose -f docker-compose.yml up -d

      - name: Run migrations
        run: docker compose exec -T backend alembic upgrade head

      - name: Health check
        run: |
          sleep 10
          curl -f http://localhost/api/v1/utils/health-check || exit 1
```

**Automation Integration:**

```python
# Example: Custom deployment automation
class DeploymentAutomation:
    def __init__(self, environment: str):
        self.env = environment
        self.gh_token = os.getenv("GITHUB_TOKEN")

    def trigger_deployment(self, version: str):
        """
        Trigger GitHub Actions deployment workflow.
        """
        import requests

        response = requests.post(
            "https://api.github.com/repos/owner/repo/actions/workflows/deploy-production.yml/dispatches",
            headers={
                "Authorization": f"Bearer {self.gh_token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={"ref": "main", "inputs": {"version": version}}
        )
        response.raise_for_status()

    def monitor_deployment_status(self, run_id: str) -> dict:
        """
        Monitor deployment workflow status.
        """
        # Poll GitHub Actions API for workflow status
        pass

    def rollback_deployment(self, previous_version: str):
        """
        Automated rollback to previous version.
        """
        # Trigger deployment with previous version
        pass

# Blue-green deployment automation
def blue_green_deployment(new_version: str):
    """
    Automated blue-green deployment strategy.
    """
    # Deploy to green environment
    # Run health checks
    # Switch traffic from blue to green
    # Keep blue as rollback target
    pass
```

**Reusability Score:** ⭐⭐⭐⭐⭐ (CI/CD workflows can be adapted for any Docker-based project)

---

### Component 8: Docker Deployment Module

**Location:** `docker-compose.yml` + `docker-compose.override.yml` + `docker-compose.traefik.yml`

**Purpose:** Complete containerized deployment stack for development and production

**Production Stack (`docker-compose.yml`):**

```yaml
services:
  db:
    image: postgres:17
    volumes:
      - app-db-data:/var/lib/postgresql/data
    env_file:
      - .env
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_DB=${POSTGRES_DB:-app}
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: ${DOCKER_IMAGE_BACKEND:-backend}
    build:
      context: ./backend
      dockerfile: Dockerfile
    depends_on:
      db:
        condition: service_healthy
    env_file:
      - .env
    environment:
      - POSTGRES_SERVER=db
    ports:
      - "8000:8000"
    command: fastapi run app/main.py --workers 4

  frontend:
    image: ${DOCKER_IMAGE_FRONTEND:-frontend}
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:80"

  adminer:
    image: adminer
    ports:
      - "8080:8080"
    environment:
      - ADMINER_DESIGN=pepa-linha-dark

volumes:
  app-db-data:
```

**Development Overrides (`docker-compose.override.yml`):**

```yaml
services:
  backend:
    build:
      context: ./backend
      target: development
    volumes:
      - ./backend:/app
    command: fastapi dev app/main.py --host 0.0.0.0 --reload
    ports:
      - "8000:8000"

  frontend:
    build:
      context: ./frontend
      target: development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0
    ports:
      - "5173:5173"

  mailcatcher:
    image: schickling/mailcatcher
    ports:
      - "1080:1080"  # Web interface
      - "1025:1025"  # SMTP

  proxy:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "8090:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    command:
      - --api.insecure=true
      - --providers.docker=true
      - --entrypoints.web.address=:80
    labels:
      - traefik.enable=true
```

**Production Traefik (`docker-compose.traefik.yml`):**

```yaml
services:
  proxy:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-public-certificates:/certificates
    command:
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.le.acme.email=${EMAIL}
      - --certificatesresolvers.le.acme.storage=/certificates/acme.json
      - --certificatesresolvers.le.acme.httpchallenge=true
      - --certificatesresolvers.le.acme.httpchallenge.entrypoint=web
      - --entrypoints.web.http.redirections.entrypoint.to=websecure
    labels:
      - traefik.enable=true

  backend:
    labels:
      - traefik.enable=true
      - traefik.http.routers.backend.rule=Host(`api.${DOMAIN}`)
      - traefik.http.routers.backend.entrypoints=websecure
      - traefik.http.routers.backend.tls.certresolver=le

  frontend:
    labels:
      - traefik.enable=true
      - traefik.http.routers.frontend.rule=Host(`${DOMAIN}`)
      - traefik.http.routers.frontend.entrypoints=websecure
      - traefik.http.routers.frontend.tls.certresolver=le

volumes:
  traefik-public-certificates:
```

**Backend Dockerfile (Multi-Stage):**

```dockerfile
# Stage 1: Base
FROM python:3.10 as base
WORKDIR /app
RUN pip install uv

# Stage 2: Dependencies
FROM base as dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Stage 3: Development
FROM dependencies as development
RUN uv sync --frozen
CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0"]

# Stage 4: Production
FROM dependencies as production
COPY ./app /app/app
RUN python -m compileall app/
CMD ["fastapi", "run", "app/main.py", "--workers", "4"]
```

**Frontend Dockerfile (Multi-Stage):**

```dockerfile
# Stage 1: Build
FROM node:20 as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM nginx:1 as production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Automation Integration:**

```python
# Example: Automated deployment orchestration
class DockerDeploymentAutomation:
    def __init__(self, environment: str):
        self.env = environment
        self.compose_files = self._get_compose_files()

    def _get_compose_files(self) -> list[str]:
        if self.env == "production":
            return ["docker-compose.yml", "docker-compose.traefik.yml"]
        else:
            return ["docker-compose.yml", "docker-compose.override.yml"]

    def deploy(self, rebuild: bool = False):
        """
        Automated deployment with health checks.
        """
        compose_cmd = ["docker", "compose"]
        for f in self.compose_files:
            compose_cmd.extend(["-f", f])

        # Build images
        if rebuild:
            subprocess.run(compose_cmd + ["build"])

        # Start services
        subprocess.run(compose_cmd + ["up", "-d"])

        # Wait for health checks
        self._wait_for_healthy()

        # Run migrations
        subprocess.run(compose_cmd + ["exec", "-T", "backend", "alembic", "upgrade", "head"])

    def _wait_for_healthy(self, timeout: int = 120):
        """Wait for all services to be healthy."""
        import time
        import docker

        client = docker.from_env()
        start = time.time()

        while time.time() - start < timeout:
            containers = client.containers.list(filters={"label": f"com.docker.compose.project={self.env}"})
            all_healthy = all(c.health == "healthy" for c in containers if c.health is not None)

            if all_healthy:
                print("All services healthy!")
                return

            time.sleep(5)

        raise TimeoutError("Services did not become healthy in time")

    def scale_service(self, service: str, replicas: int):
        """
        Scale a service to N replicas.
        """
        compose_cmd = ["docker", "compose"]
        for f in self.compose_files:
            compose_cmd.extend(["-f", f])

        subprocess.run(compose_cmd + ["up", "-d", "--scale", f"{service}={replicas}"])

    def backup_database(self, output_path: str):
        """
        Automated database backup.
        """
        subprocess.run([
            "docker", "compose", "exec", "-T", "db",
            "pg_dump", "-U", "postgres", "app"
        ], stdout=open(output_path, "w"))

    def restore_database(self, backup_path: str):
        """
        Automated database restore.
        """
        with open(backup_path) as f:
            subprocess.run([
                "docker", "compose", "exec", "-T", "db",
                "psql", "-U", "postgres", "app"
            ], stdin=f)

# Infrastructure as Code automation
def provision_infrastructure():
    """
    Automated infrastructure provisioning.
    """
    # Create VPS/EC2 instance
    # Install Docker and Docker Compose
    # Clone repository
    # Set up environment variables
    # Deploy with Traefik
    pass

# Monitoring automation
def setup_monitoring():
    """
    Deploy monitoring stack (Prometheus + Grafana).
    """
    # Add monitoring services to docker-compose.yml
    # Configure Prometheus to scrape FastAPI metrics
    # Set up Grafana dashboards
    pass
```

**Reusability Score:** ⭐⭐⭐⭐⭐ (Docker setup can be reused for any multi-tier application)

---

## Automation Workflow Patterns

### Pattern 1: User Lifecycle Automation

**Objective:** Automate user onboarding, management, and offboarding

```python
class UserLifecycleAutomation:
    """
    Complete user lifecycle automation workflow.
    """

    def __init__(self, api_base_url: str, admin_token: str):
        self.api = UserAutomation(api_base_url, admin_token)
        self.email = EmailAutomation()

    def onboard_user(self, user_data: dict) -> dict:
        """
        Automated user onboarding workflow.

        Steps:
        1. Create user account
        2. Send welcome email
        3. Create default items/resources
        4. Add to relevant groups
        5. Trigger notifications
        """
        # Create user
        user = self.api.create_user(user_data)

        # Send welcome email
        self.email.send_welcome_email(
            email=user["email"],
            name=user["full_name"],
            temporary_password=user_data["password"]
        )

        # Create default resources
        default_items = self._create_default_items(user["id"])

        # Log onboarding event
        self._log_event("user_onboarded", user["id"])

        return {
            "user": user,
            "default_items": default_items,
            "status": "onboarded"
        }

    def offboard_user(self, user_id: str, transfer_to: str = None) -> dict:
        """
        Automated user offboarding workflow.

        Steps:
        1. Transfer ownership of items to another user
        2. Deactivate user account
        3. Archive user data
        4. Send offboarding notification
        5. Remove from active directory
        """
        # Get user items
        items = self.api.get_user_items(user_id)

        # Transfer ownership if specified
        if transfer_to:
            for item in items:
                self.api.transfer_item_ownership(item["id"], transfer_to)

        # Deactivate user
        self.api.deactivate_user(user_id)

        # Archive data
        archive_path = self._archive_user_data(user_id)

        # Send notification
        user = self.api.get_user(user_id)
        self.email.send_offboarding_email(user["email"])

        return {
            "user_id": user_id,
            "items_transferred": len(items),
            "archive_path": archive_path,
            "status": "offboarded"
        }

    def periodic_access_review(self):
        """
        Automated periodic access review workflow.

        Runs daily/weekly to:
        1. Identify inactive users (no login in 90 days)
        2. Send access review notifications to managers
        3. Auto-deactivate users pending approval
        """
        inactive_users = self.api.get_inactive_users(days=90)

        for user in inactive_users:
            # Send review notification
            self.email.send_access_review_notification(
                user_email=user["email"],
                manager_email=user["manager_email"],
                inactive_days=user["inactive_days"]
            )

        # Schedule auto-deactivation in 7 days if no response
        self._schedule_auto_deactivation(inactive_users)
```

**Integration Example:**

```python
# Scheduled job (runs daily via cron or Airflow)
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=2)  # 2 AM daily
def daily_user_lifecycle_automation():
    automation = UserLifecycleAutomation(
        api_base_url="https://api.example.com",
        admin_token=os.getenv("ADMIN_TOKEN")
    )
    automation.periodic_access_review()

scheduler.start()
```

---

### Pattern 2: Data Pipeline Automation

**Objective:** Automate data ingestion, processing, and API integration

```python
class DataPipelineAutomation:
    """
    Automated data pipeline for syncing external data into FastAPI backend.
    """

    def __init__(self, api_base_url: str, admin_token: str):
        self.api_base = api_base_url
        self.token = admin_token
        self.headers = {"Authorization": f"Bearer {admin_token}"}

    def sync_users_from_csv(self, csv_path: str):
        """
        Automated workflow: Import users from CSV file.

        Steps:
        1. Read CSV file
        2. Validate data
        3. Check for duplicates
        4. Create/update users
        5. Generate report
        """
        import pandas as pd

        # Read CSV
        df = pd.read_csv(csv_path)

        # Validate schema
        required_columns = ["email", "full_name"]
        assert all(col in df.columns for col in required_columns)

        results = {
            "created": [],
            "updated": [],
            "failed": []
        }

        for _, row in df.iterrows():
            try:
                # Check if user exists
                existing_user = self._get_user_by_email(row["email"])

                if existing_user:
                    # Update user
                    updated_user = self._update_user(existing_user["id"], row.to_dict())
                    results["updated"].append(updated_user)
                else:
                    # Create user
                    new_user = self._create_user({
                        "email": row["email"],
                        "full_name": row["full_name"],
                        "password": self._generate_random_password()
                    })
                    results["created"].append(new_user)

            except Exception as e:
                results["failed"].append({
                    "email": row["email"],
                    "error": str(e)
                })

        # Generate report
        self._generate_sync_report(results)

        return results

    def sync_items_from_external_api(self, external_api_url: str):
        """
        Automated workflow: Sync items from external API.

        Steps:
        1. Fetch data from external API
        2. Transform data to match internal schema
        3. Deduplicate
        4. Bulk create/update items
        5. Log sync metrics
        """
        import requests

        # Fetch external data
        response = requests.get(external_api_url)
        external_items = response.json()

        # Transform data
        transformed_items = [
            self._transform_external_item(item)
            for item in external_items
        ]

        # Bulk upsert
        results = self._bulk_upsert_items(transformed_items)

        # Log metrics
        self._log_sync_metrics({
            "source": external_api_url,
            "total_fetched": len(external_items),
            "created": results["created"],
            "updated": results["updated"],
            "failed": results["failed"]
        })

        return results

    def scheduled_database_cleanup(self):
        """
        Automated workflow: Clean up old/orphaned data.

        Steps:
        1. Delete soft-deleted items older than 30 days
        2. Archive inactive users
        3. Vacuum database
        """
        # Implementation
        pass

# Airflow DAG integration
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'fastapi_data_sync',
    default_args=default_args,
    description='Sync external data to FastAPI backend',
    schedule_interval='0 */6 * * *',  # Every 6 hours
    catchup=False
)

def sync_users_task():
    automation = DataPipelineAutomation(
        api_base_url=os.getenv("API_BASE_URL"),
        admin_token=os.getenv("ADMIN_TOKEN")
    )
    automation.sync_users_from_csv("/data/users.csv")

def sync_items_task():
    automation = DataPipelineAutomation(
        api_base_url=os.getenv("API_BASE_URL"),
        admin_token=os.getenv("ADMIN_TOKEN")
    )
    automation.sync_items_from_external_api("https://external-api.com/items")

t1 = PythonOperator(
    task_id='sync_users',
    python_callable=sync_users_task,
    dag=dag
)

t2 = PythonOperator(
    task_id='sync_items',
    python_callable=sync_items_task,
    dag=dag
)

t1 >> t2  # Run sequentially
```

---

### Pattern 3: Multi-Tenant Automation

**Objective:** Automate tenant provisioning and isolation

```python
class MultiTenantAutomation:
    """
    Automated multi-tenant management workflow.

    Extends the base template to support multiple isolated tenants.
    """

    def __init__(self, api_base_url: str, admin_token: str):
        self.api_base = api_base_url
        self.token = admin_token

    def provision_tenant(self, tenant_data: dict) -> dict:
        """
        Automated tenant provisioning workflow.

        Steps:
        1. Create tenant record in database
        2. Create tenant admin user
        3. Set up tenant-specific resources
        4. Configure tenant subdomain/routing
        5. Send provisioning notification

        Args:
            tenant_data: {
                "name": "Acme Corp",
                "subdomain": "acme",
                "admin_email": "admin@acme.com",
                "plan": "enterprise"
            }
        """
        # Create tenant database schema (if using schema-based isolation)
        tenant_id = self._create_tenant_schema(tenant_data["subdomain"])

        # Create tenant admin user
        admin_user = self._create_tenant_admin(
            tenant_id=tenant_id,
            email=tenant_data["admin_email"],
            full_name=tenant_data["name"]
        )

        # Set up default resources
        default_resources = self._create_tenant_defaults(tenant_id)

        # Configure routing (if using subdomain routing)
        self._configure_tenant_routing(tenant_data["subdomain"], tenant_id)

        # Send provisioning email
        self._send_tenant_provisioning_email(tenant_data, admin_user)

        return {
            "tenant_id": tenant_id,
            "subdomain": tenant_data["subdomain"],
            "admin_user": admin_user,
            "status": "provisioned"
        }

    def deprovision_tenant(self, tenant_id: str) -> dict:
        """
        Automated tenant deprovisioning workflow.

        Steps:
        1. Export tenant data
        2. Deactivate all tenant users
        3. Archive tenant database
        4. Remove tenant routing
        5. Send deprovisioning notification
        """
        # Export data
        export_path = self._export_tenant_data(tenant_id)

        # Deactivate users
        users = self._get_tenant_users(tenant_id)
        for user in users:
            self._deactivate_user(user["id"])

        # Archive database
        self._archive_tenant_schema(tenant_id)

        # Remove routing
        self._remove_tenant_routing(tenant_id)

        return {
            "tenant_id": tenant_id,
            "export_path": export_path,
            "status": "deprovisioned"
        }

    def tenant_usage_reporting(self):
        """
        Automated tenant usage reporting workflow.

        Generates daily usage reports for billing/monitoring.
        """
        tenants = self._get_all_tenants()

        reports = []
        for tenant in tenants:
            usage = {
                "tenant_id": tenant["id"],
                "users_count": self._count_tenant_users(tenant["id"]),
                "items_count": self._count_tenant_items(tenant["id"]),
                "api_calls": self._get_api_call_count(tenant["id"]),
                "storage_used": self._get_storage_usage(tenant["id"])
            }
            reports.append(usage)

        # Store reports
        self._store_usage_reports(reports)

        # Send to billing system
        self._send_to_billing_system(reports)

        return reports

# Terraform integration for infrastructure
terraform_template = """
resource "aws_db_instance" "tenant_{{tenant_id}}" {
  identifier           = "fastapi-tenant-{{tenant_id}}"
  engine               = "postgres"
  engine_version       = "17"
  instance_class       = "db.t3.micro"
  allocated_storage    = 20
  username             = "{{db_user}}"
  password             = "{{db_password}}"

  tags = {
    Tenant = "{{tenant_name}}"
  }
}

resource "aws_ecs_service" "tenant_{{tenant_id}}_backend" {
  name            = "fastapi-backend-{{tenant_id}}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 2

  load_balancer {
    target_group_arn = aws_lb_target_group.tenant_{{tenant_id}}.arn
    container_name   = "backend"
    container_port   = 8000
  }
}
"""

def provision_tenant_infrastructure(tenant_id: str, tenant_data: dict):
    """
    Use Terraform to provision isolated infrastructure for tenant.
    """
    import subprocess
    from jinja2 import Template

    # Render Terraform template
    template = Template(terraform_template)
    tf_config = template.render(
        tenant_id=tenant_id,
        tenant_name=tenant_data["name"],
        db_user=f"tenant_{tenant_id}",
        db_password=secrets.token_urlsafe(32)
    )

    # Write to file
    with open(f"terraform/tenant_{tenant_id}.tf", "w") as f:
        f.write(tf_config)

    # Apply Terraform
    subprocess.run(["terraform", "init"], cwd="terraform")
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd="terraform")
```

---

### Pattern 4: API Gateway Integration

**Objective:** Use FastAPI backend as authentication/authorization gateway

```python
class APIGatewayAutomation:
    """
    Use FastAPI template as API gateway for microservices.

    Provides centralized authentication and routing.
    """

    def __init__(self, api_base_url: str):
        self.api_base = api_base_url

    def proxy_authenticated_request(
        self,
        token: str,
        service_name: str,
        endpoint: str,
        method: str = "GET",
        **kwargs
    ):
        """
        Automated workflow: Proxy request to microservice after auth.

        Steps:
        1. Validate JWT token
        2. Extract user information
        3. Check user permissions for service
        4. Proxy request to downstream service
        5. Log request for audit
        """
        # Validate token
        user = self._validate_token(token)

        # Check permissions
        if not self._user_has_access(user, service_name):
            raise PermissionError(f"User {user['email']} cannot access {service_name}")

        # Get service URL
        service_url = self._get_service_url(service_name)

        # Proxy request
        response = requests.request(
            method=method,
            url=f"{service_url}{endpoint}",
            headers={
                "X-User-ID": user["id"],
                "X-User-Email": user["email"],
                **kwargs.get("headers", {})
            },
            **{k: v for k, v in kwargs.items() if k != "headers"}
        )

        # Log request
        self._log_gateway_request(user, service_name, endpoint, response.status_code)

        return response

    def configure_service_routing(self, config: dict):
        """
        Configure API gateway routing rules.

        config = {
            "analytics": {
                "url": "http://analytics-service:8001",
                "required_role": "analyst",
                "rate_limit": "100/minute"
            },
            "billing": {
                "url": "http://billing-service:8002",
                "required_role": "admin",
                "rate_limit": "50/minute"
            }
        }
        """
        # Store routing configuration
        self._store_routing_config(config)

        # Update Traefik/Nginx configuration
        self._update_proxy_config(config)

# FastAPI Gateway Route Implementation
from fastapi import APIRouter, Depends, Request
from app.api.deps import CurrentUser

gateway_router = APIRouter(prefix="/gateway", tags=["gateway"])

@gateway_router.api_route(
    "/{service}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def gateway_proxy(
    service: str,
    path: str,
    request: Request,
    current_user: CurrentUser
):
    """
    API Gateway endpoint - proxies requests to downstream services.
    """
    gateway = APIGatewayAutomation("http://localhost:8000")

    # Get request body
    body = await request.body()

    # Proxy request
    response = gateway.proxy_authenticated_request(
        token=request.headers.get("Authorization").split()[1],
        service_name=service,
        endpoint=f"/{path}",
        method=request.method,
        data=body,
        headers=dict(request.headers)
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
```

---

### Pattern 5: Event-Driven Automation

**Objective:** React to application events with automated workflows

```python
class EventDrivenAutomation:
    """
    Event-driven automation workflows using webhooks/message queues.
    """

    def __init__(self):
        self.handlers = {}

    def register_handler(self, event_type: str, handler: callable):
        """Register event handler."""
        self.handlers[event_type] = handler

    def handle_event(self, event: dict):
        """
        Route event to appropriate handler.

        event = {
            "type": "user.created",
            "data": {"user_id": "123", "email": "user@example.com"},
            "timestamp": "2025-01-15T10:00:00Z"
        }
        """
        event_type = event["type"]

        if event_type in self.handlers:
            self.handlers[event_type](event["data"])

    def on_user_created(self, data: dict):
        """
        Automated workflow triggered when user is created.

        Actions:
        1. Send welcome email
        2. Create onboarding tasks
        3. Notify team in Slack
        4. Add to email marketing list
        """
        # Send welcome email
        send_email(
            email_to=data["email"],
            subject="Welcome!",
            template="welcome"
        )

        # Create onboarding tasks
        self._create_onboarding_tasks(data["user_id"])

        # Notify Slack
        self._send_slack_notification(
            channel="#new-users",
            message=f"New user registered: {data['email']}"
        )

        # Add to marketing list
        self._add_to_mailchimp(data["email"])

    def on_item_created(self, data: dict):
        """
        Automated workflow triggered when item is created.
        """
        # Validate item data
        # Generate thumbnail if item has image
        # Index in search engine
        # Notify interested parties
        pass

    def on_password_reset_requested(self, data: dict):
        """
        Automated security workflow.
        """
        # Log security event
        # Check for suspicious activity
        # Send reset email
        # Notify security team if unusual
        pass

# FastAPI webhook endpoint
from fastapi import APIRouter, BackgroundTasks

webhook_router = APIRouter(prefix="/webhooks", tags=["webhooks"])
automation = EventDrivenAutomation()

# Register handlers
automation.register_handler("user.created", automation.on_user_created)
automation.register_handler("item.created", automation.on_item_created)
automation.register_handler("password.reset", automation.on_password_reset_requested)

@webhook_router.post("/events")
async def handle_webhook(event: dict, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for receiving events.
    """
    # Process event asynchronously
    background_tasks.add_task(automation.handle_event, event)

    return {"status": "accepted"}

# RabbitMQ/Celery integration
from celery import Celery

celery_app = Celery('tasks', broker='amqp://localhost')

@celery_app.task
def process_user_created_event(user_data: dict):
    """
    Celery task for processing user creation events.
    """
    automation = EventDrivenAutomation()
    automation.on_user_created(user_data)

# Emit event from FastAPI endpoint
@router.post("/users/")
def create_user(user_create: UserCreate, session: SessionDep):
    # Create user
    user = crud.create_user(session=session, user_create=user_create)

    # Emit event asynchronously
    process_user_created_event.delay({
        "user_id": str(user.id),
        "email": user.email,
        "full_name": user.full_name
    })

    return user
```

---

## Integration Strategies

### Strategy 1: Python-Based Automation Framework

**Use Case:** Integrate FastAPI template into Python automation scripts (Luigi, Prefect, Dagster)

```python
# Prefect workflow integration
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=1))
def authenticate_api():
    """Get API token with caching."""
    token = authenticate_user(
        "https://api.example.com",
        "admin@example.com",
        "changethis"
    )
    return token

@task
def fetch_users(token: str):
    """Fetch all users from API."""
    response = requests.get(
        "https://api.example.com/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

@task
def process_users(users: list[dict]):
    """Process user data."""
    # Analytics, transformations, etc.
    processed = []
    for user in users["data"]:
        processed.append({
            "email": user["email"],
            "active": user["is_active"],
            "items_count": len(user.get("items", []))
        })
    return processed

@task
def export_to_warehouse(data: list[dict]):
    """Export to data warehouse."""
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_parquet("s3://warehouse/users/latest.parquet")

@flow(name="daily-user-sync")
def daily_user_sync_workflow():
    """
    Daily workflow to sync users to data warehouse.
    """
    token = authenticate_api()
    users = fetch_users(token)
    processed = process_users(users)
    export_to_warehouse(processed)

# Schedule workflow
if __name__ == "__main__":
    daily_user_sync_workflow.serve(
        name="daily-user-sync-deployment",
        cron="0 2 * * *"  # 2 AM daily
    )
```

---

### Strategy 2: No-Code/Low-Code Platform Integration

**Use Case:** Integrate with n8n, Zapier, Make.com for visual automation

```json
{
  "name": "FastAPI Template - n8n Integration",
  "nodes": [
    {
      "name": "HTTP Request - Login",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.example.com/api/v1/login/access-token",
        "method": "POST",
        "bodyParametersJson": "={{ {\"username\": \"admin@example.com\", \"password\": \"changethis\"} }}",
        "responseFormat": "json"
      }
    },
    {
      "name": "Set Token",
      "type": "n8n-nodes-base.set",
      "parameters": {
        "values": {
          "string": [
            {
              "name": "token",
              "value": "={{ $json.access_token }}"
            }
          ]
        }
      }
    },
    {
      "name": "HTTP Request - Get Users",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.example.com/api/v1/users/",
        "method": "GET",
        "headerParametersJson": "={{ {\"Authorization\": \"Bearer \" + $node[\"Set Token\"].json.token} }}"
      }
    },
    {
      "name": "Google Sheets",
      "type": "n8n-nodes-base.googleSheets",
      "parameters": {
        "operation": "append",
        "sheetId": "your-sheet-id",
        "range": "A:D"
      }
    }
  ],
  "connections": {
    "HTTP Request - Login": {
      "main": [[{"node": "Set Token"}]]
    },
    "Set Token": {
      "main": [[{"node": "HTTP Request - Get Users"}]]
    },
    "HTTP Request - Get Users": {
      "main": [[{"node": "Google Sheets"}]]
    }
  }
}
```

**Zapier Integration:**

```javascript
// Zapier Custom App Definition
const authentication = {
  type: 'custom',
  fields: [
    { key: 'api_base_url', label: 'API Base URL', required: true },
    { key: 'email', label: 'Email', required: true },
    { key: 'password', label: 'Password', required: true, type: 'password' }
  ],
  test: async (z, bundle) => {
    const response = await z.request({
      url: `${bundle.authData.api_base_url}/api/v1/login/access-token`,
      method: 'POST',
      body: {
        username: bundle.authData.email,
        password: bundle.authData.password
      }
    })

    return { token: response.json.access_token }
  },
  connectionLabel: '{{email}}'
}

const listUsers = {
  key: 'list_users',
  noun: 'User',
  display: {
    label: 'List Users',
    description: 'Fetches all users from FastAPI backend'
  },
  operation: {
    perform: async (z, bundle) => {
      const response = await z.request({
        url: `${bundle.authData.api_base_url}/api/v1/users/`,
        headers: {
          'Authorization': `Bearer ${bundle.authData.token}`
        }
      })

      return response.json.data
    }
  }
}

const createUser = {
  key: 'create_user',
  noun: 'User',
  display: {
    label: 'Create User',
    description: 'Creates a new user'
  },
  operation: {
    inputFields: [
      { key: 'email', required: true },
      { key: 'password', required: true, type: 'password' },
      { key: 'full_name', required: false }
    ],
    perform: async (z, bundle) => {
      const response = await z.request({
        url: `${bundle.authData.api_base_url}/api/v1/users/`,
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${bundle.authData.token}`
        },
        body: bundle.inputData
      })

      return response.json
    }
  }
}
```

---

### Strategy 3: Kubernetes/Cloud-Native Integration

**Use Case:** Deploy as microservice in Kubernetes cluster

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-backend
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-backend
  template:
    metadata:
      labels:
        app: fastapi-backend
    spec:
      containers:
      - name: backend
        image: your-registry/fastapi-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_SERVER
          value: postgres-service
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: secret-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/v1/utils/health-check
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/utils/health-check
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-backend-service
spec:
  selector:
    app: fastapi-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.example.com
    secretName: api-tls
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-backend-service
            port:
              number: 80

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapi-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Helm Chart Integration:**

```yaml
# helm/fastapi-template/values.yaml
replicaCount: 3

image:
  repository: your-registry/fastapi-backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls
      hosts:
        - api.example.com

postgresql:
  enabled: true
  auth:
    username: postgres
    password: changethis
    database: app
  primary:
    persistence:
      enabled: true
      size: 10Gi

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

env:
  - name: ENVIRONMENT
    value: production
  - name: PROJECT_NAME
    value: "My FastAPI App"
```

---

## Copy-Paste Module Templates

### Template 1: Standalone Auth Microservice

**Extract authentication module as standalone service**

```python
# auth_microservice/main.py
"""
Standalone authentication microservice extracted from FastAPI template.
Can be deployed independently and consumed by other services.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
import uvicorn

# Import core modules from template
from app.core.security import create_access_token, verify_password
from app.core.db import engine, init_db
from app.models import User, Token
from app.core.config import settings

app = FastAPI(title="Auth Microservice")

def get_db():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)

@app.get("/verify")
def verify_token(token: str, session: Session = Depends(get_db)):
    """Verify JWT token and return user information."""
    # Token verification logic
    pass

@app.post("/register")
def register(email: str, password: str, session: Session = Depends(get_db)):
    """Public user registration endpoint."""
    # Registration logic
    pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Docker Compose for standalone auth service:**

```yaml
# auth_microservice/docker-compose.yml
version: '3.8'

services:
  auth-db:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD: changethis
      POSTGRES_DB: auth
    volumes:
      - auth-db-data:/var/lib/postgresql/data

  auth-service:
    build: .
    ports:
      - "8001:8001"
    depends_on:
      - auth-db
    environment:
      POSTGRES_SERVER: auth-db
      POSTGRES_PASSWORD: changethis
      SECRET_KEY: your-secret-key

volumes:
  auth-db-data:
```

---

### Template 2: CRUD API Generator

**Generate CRUD endpoints for any SQLModel model**

```python
# crud_generator.py
"""
Automated CRUD API generator using FastAPI template patterns.
"""

from typing import TypeVar, Generic, Type
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, SQLModel
from uuid import UUID

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchema = TypeVar("CreateSchema", bound=SQLModel)
UpdateSchema = TypeVar("UpdateSchema", bound=SQLModel)

class CRUDGenerator(Generic[ModelType, CreateSchema, UpdateSchema]):
    """
    Generic CRUD API generator.

    Usage:
        crud = CRUDGenerator(
            model=Item,
            create_schema=ItemCreate,
            update_schema=ItemUpdate
        )
        router = crud.get_router()
    """

    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchema],
        update_schema: Type[UpdateSchema],
        prefix: str = None
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.prefix = prefix or f"/{model.__tablename__}"
        self.router = APIRouter(prefix=self.prefix, tags=[model.__tablename__])

        self._register_routes()

    def _register_routes(self):
        """Register all CRUD routes."""

        @self.router.get("/")
        def list_items(
            session: Session = Depends(get_db),
            skip: int = 0,
            limit: int = 100
        ):
            statement = select(self.model).offset(skip).limit(limit)
            items = session.exec(statement).all()
            count = len(items)
            return {"data": items, "count": count}

        @self.router.post("/")
        def create_item(
            item_in: self.create_schema,
            session: Session = Depends(get_db)
        ):
            db_item = self.model.model_validate(item_in)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return db_item

        @self.router.get("/{item_id}")
        def get_item(
            item_id: UUID,
            session: Session = Depends(get_db)
        ):
            item = session.get(self.model, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item

        @self.router.put("/{item_id}")
        def update_item(
            item_id: UUID,
            item_in: self.update_schema,
            session: Session = Depends(get_db)
        ):
            db_item = session.get(self.model, item_id)
            if not db_item:
                raise HTTPException(status_code=404, detail="Item not found")

            item_data = item_in.model_dump(exclude_unset=True)
            db_item.sqlmodel_update(item_data)
            session.add(db_item)
            session.commit()
            session.refresh(db_item)
            return db_item

        @self.router.delete("/{item_id}")
        def delete_item(
            item_id: UUID,
            session: Session = Depends(get_db)
        ):
            item = session.get(self.model, item_id)
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")

            session.delete(item)
            session.commit()
            return {"message": "Item deleted"}

    def get_router(self) -> APIRouter:
        """Get the configured router."""
        return self.router

# Usage example
from app.models import Item, ItemCreate, ItemUpdate

item_crud = CRUDGenerator(
    model=Item,
    create_schema=ItemCreate,
    update_schema=ItemUpdate
)

app.include_router(item_crud.get_router())
```

---

### Template 3: Background Job Processor

**Add async background jobs to the template**

```python
# background_jobs.py
"""
Background job processing system for FastAPI template.
Uses Celery + Redis for distributed task queue.
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from app.core.db import engine
from sqlmodel import Session
import logging

# Initialize Celery
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Background Tasks

@celery_app.task
def send_email_async(email_to: str, subject: str, html_content: str):
    """
    Send email asynchronously.
    """
    from app.utils import send_email
    send_email(email_to=email_to, subject=subject, html_content=html_content)

@celery_app.task
def process_csv_import(file_path: str, user_id: str):
    """
    Process CSV import in background.
    """
    import pandas as pd
    from app.crud import create_item

    df = pd.read_csv(file_path)

    with Session(engine) as session:
        for _, row in df.iterrows():
            create_item(
                session=session,
                item_in=ItemCreate(**row.to_dict()),
                owner_id=user_id
            )
        session.commit()

@celery_app.task
def generate_report(report_type: str, user_id: str):
    """
    Generate report asynchronously.
    """
    # Report generation logic
    pass

@celery_app.task
def cleanup_old_data():
    """
    Cleanup old data (scheduled task).
    """
    with Session(engine) as session:
        # Delete old items
        pass

# Periodic Tasks
celery_app.conf.beat_schedule = {
    'cleanup-daily': {
        'task': 'background_jobs.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'send-weekly-report': {
        'task': 'background_jobs.send_weekly_report',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Monday 9 AM
    },
}

# FastAPI Integration
from fastapi import BackgroundTasks

@router.post("/items/import")
async def import_items_csv(
    file: UploadFile,
    current_user: CurrentUser,
    background_tasks: BackgroundTasks
):
    """
    Import items from CSV (background processing).
    """
    # Save file
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Queue background task
    process_csv_import.delay(file_path, str(current_user.id))

    return {"message": "Import started, you will be notified when complete"}

# Docker Compose addition
"""
  redis:
    image: redis:7
    ports:
      - "6379:6379"

  celery-worker:
    build: ./backend
    command: celery -A background_jobs worker --loglevel=info
    depends_on:
      - redis
      - db

  celery-beat:
    build: ./backend
    command: celery -A background_jobs beat --loglevel=info
    depends_on:
      - redis
"""
```

---

### Template 4: Real-Time WebSocket Module

**Add WebSocket support for real-time features**

```python
# websocket_module.py
"""
WebSocket support for real-time features.
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import List
import json

class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)

        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        self.user_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: str):
        self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            self.user_connections[user_id].remove(websocket)

    async def send_personal_message(self, message: str, user_id: str):
        """Send message to specific user."""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_text(message)

    async def broadcast(self, message: str):
        """Broadcast message to all connected clients."""
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str
):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()

            # Handle different message types
            message = json.loads(data)

            if message["type"] == "broadcast":
                await manager.broadcast(json.dumps({
                    "user_id": user_id,
                    "message": message["content"]
                }))

            elif message["type"] == "personal":
                await manager.send_personal_message(
                    json.dumps(message["content"]),
                    message["to_user_id"]
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# Notification system
async def notify_user(user_id: str, notification: dict):
    """
    Send real-time notification to user.
    """
    await manager.send_personal_message(
        json.dumps({
            "type": "notification",
            "data": notification
        }),
        user_id
    )

# Usage in API endpoints
@router.post("/items/")
async def create_item(
    item_in: ItemCreate,
    session: SessionDep,
    current_user: CurrentUser
):
    item = crud.create_item(session=session, item_in=item_in, owner_id=current_user.id)

    # Send real-time notification
    await notify_user(str(current_user.id), {
        "message": f"Item '{item.title}' created successfully",
        "item_id": str(item.id)
    })

    return item

# Frontend WebSocket client
"""
// React WebSocket hook
import { useEffect, useState } from 'react'

export function useWebSocket(userId: string) {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [messages, setMessages] = useState<any[]>([])

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`)

    ws.onopen = () => {
      console.log('WebSocket connected')
      setSocket(ws)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setMessages(prev => [...prev, data])
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
    }

    return () => {
      ws.close()
    }
  }, [userId])

  const sendMessage = (message: any) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message))
    }
  }

  return { socket, messages, sendMessage }
}
"""
```

---

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required | Request Body | Response |
|--------|----------|-------------|---------------|--------------|----------|
| POST | `/api/v1/login/access-token` | Login and get JWT token | No | `{"username": "email", "password": "string"}` | `{"access_token": "jwt", "token_type": "bearer"}` |
| POST | `/api/v1/login/test-token` | Verify token validity | Yes | - | `{"email": "user@example.com"}` |
| POST | `/api/v1/password-recovery/{email}` | Request password reset | No | - | `{"message": "Email sent"}` |
| POST | `/api/v1/reset-password/` | Reset password with token | No | `{"token": "string", "new_password": "string"}` | `{"message": "Password updated"}` |

### User Management Endpoints

| Method | Endpoint | Description | Auth Required | Request Body | Response |
|--------|----------|-------------|---------------|--------------|----------|
| GET | `/api/v1/users/` | List all users (admin) | Yes (superuser) | - | `{"data": [User], "count": int}` |
| POST | `/api/v1/users/` | Create user (admin) | Yes (superuser) | `UserCreate` | `UserPublic` |
| GET | `/api/v1/users/me` | Get current user | Yes | - | `UserPublic` |
| PATCH | `/api/v1/users/me` | Update current user | Yes | `UserUpdateMe` | `UserPublic` |
| PATCH | `/api/v1/users/me/password` | Change password | Yes | `UpdatePassword` | `{"message": "Password updated"}` |
| DELETE | `/api/v1/users/me` | Delete own account | Yes | - | `{"message": "User deleted"}` |
| POST | `/api/v1/users/signup` | Public registration | No | `UserRegister` | `UserPublic` |
| GET | `/api/v1/users/{user_id}` | Get user by ID (admin) | Yes (superuser) | - | `UserPublic` |
| PATCH | `/api/v1/users/{user_id}` | Update user (admin) | Yes (superuser) | `UserUpdate` | `UserPublic` |
| DELETE | `/api/v1/users/{user_id}` | Delete user (admin) | Yes (superuser) | - | `{"message": "User deleted"}` |

### Item Management Endpoints

| Method | Endpoint | Description | Auth Required | Request Body | Response |
|--------|----------|-------------|---------------|--------------|----------|
| GET | `/api/v1/items/?skip=0&limit=100` | List user's items | Yes | - | `{"data": [Item], "count": int}` |
| POST | `/api/v1/items/` | Create item | Yes | `ItemCreate` | `ItemPublic` |
| GET | `/api/v1/items/{item_id}` | Get item by ID | Yes | - | `ItemPublic` |
| PUT | `/api/v1/items/{item_id}` | Update item | Yes | `ItemUpdate` | `ItemPublic` |
| DELETE | `/api/v1/items/{item_id}` | Delete item | Yes | - | `{"message": "Item deleted"}` |

### Data Models

**UserCreate:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false
}
```

**UserPublic:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false
}
```

**ItemCreate:**
```json
{
  "title": "My Item",
  "description": "Item description"
}
```

**ItemPublic:**
```json
{
  "id": "uuid",
  "title": "My Item",
  "description": "Item description",
  "owner_id": "uuid"
}
```

---

## Deployment Automation

### Automated Deployment Script

```bash
#!/bin/bash
# deploy.sh - Automated deployment script

set -e

ENVIRONMENT=${1:-production}
VERSION=${2:-latest}

echo "Deploying version $VERSION to $ENVIRONMENT..."

# 1. Backup current database
echo "Creating database backup..."
./scripts/backup-database.sh $ENVIRONMENT

# 2. Pull latest code
echo "Pulling latest code..."
git fetch origin
git checkout $VERSION

# 3. Build Docker images
echo "Building Docker images..."
docker compose -f docker-compose.yml build

# 4. Run database migrations
echo "Running migrations..."
docker compose run --rm backend alembic upgrade head

# 5. Run tests
echo "Running tests..."
docker compose run --rm backend pytest

# 6. Deploy with zero-downtime
echo "Deploying..."
docker compose up -d --scale backend=2

# Wait for health checks
sleep 10

# 7. Remove old containers
echo "Cleaning up old containers..."
docker compose up -d --scale backend=4 --remove-orphans

# 8. Verify deployment
echo "Verifying deployment..."
curl -f http://localhost/api/v1/utils/health-check || {
    echo "Health check failed! Rolling back..."
    git checkout -
    docker compose up -d
    exit 1
}

echo "Deployment successful!"
```

### Infrastructure as Code (Terraform)

```hcl
# terraform/main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true

  tags = {
    Name = "fastapi-vpc"
  }
}

# Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "fastapi-public-${count.index}"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier        = "fastapi-db"
  engine            = "postgres"
  engine_version    = "17"
  instance_class    = var.db_instance_class
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  skip_final_snapshot = false
  final_snapshot_identifier = "fastapi-db-final-snapshot"

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  tags = {
    Name = "fastapi-postgres"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "fastapi-cluster"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "fastapi-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"

  container_definitions = jsonencode([
    {
      name  = "backend"
      image = "${var.docker_registry}/fastapi-backend:${var.app_version}"

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "POSTGRES_SERVER"
          value = aws_db_instance.postgres.address
        },
        {
          name  = "POSTGRES_DB"
          value = var.db_name
        }
      ]

      secrets = [
        {
          name      = "POSTGRES_PASSWORD"
          valueFrom = aws_secretsmanager_secret.db_password.arn
        },
        {
          name      = "SECRET_KEY"
          valueFrom = aws_secretsmanager_secret.app_secret.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/fastapi-backend"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "backend" {
  name            = "fastapi-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.backend_replicas
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "fastapi-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "backend" {
  name        = "fastapi-backend-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/api/v1/utils/health-check"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = var.ssl_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

# Outputs
output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}
```

---

## Testing Automation

### Automated Test Suite Runner

```python
# test_automation.py
"""
Comprehensive automated testing framework.
"""

import subprocess
import json
import sys
from pathlib import Path

class TestAutomation:
    """
    Automated test suite runner with reporting.
    """

    def __init__(self):
        self.results = {
            "backend": {},
            "frontend": {},
            "e2e": {},
            "integration": {}
        }

    def run_backend_tests(self) -> bool:
        """Run backend tests with coverage."""
        print("🧪 Running backend tests...")

        result = subprocess.run(
            ["pytest", "backend/app/tests", "--cov=app", "--cov-report=json", "--cov-report=html"],
            capture_output=True,
            text=True
        )

        # Parse coverage
        coverage_file = Path("backend/coverage.json")
        if coverage_file.exists():
            with open(coverage_file) as f:
                coverage_data = json.load(f)

            self.results["backend"] = {
                "passed": result.returncode == 0,
                "coverage": coverage_data["totals"]["percent_covered"],
                "output": result.stdout
            }

        return result.returncode == 0

    def run_frontend_unit_tests(self) -> bool:
        """Run frontend unit tests (if configured)."""
        print("⚛️  Running frontend unit tests...")

        result = subprocess.run(
            ["npm", "run", "test"],
            cwd="frontend",
            capture_output=True,
            text=True
        )

        self.results["frontend"] = {
            "passed": result.returncode == 0,
            "output": result.stdout
        }

        return result.returncode == 0

    def run_e2e_tests(self) -> bool:
        """Run Playwright E2E tests."""
        print("🎭 Running E2E tests...")

        # Start Docker Compose stack
        subprocess.run(["docker", "compose", "up", "-d"])

        # Wait for services
        import time
        time.sleep(10)

        # Run Playwright tests
        result = subprocess.run(
            ["npx", "playwright", "test", "--reporter=json"],
            cwd="frontend",
            capture_output=True,
            text=True
        )

        self.results["e2e"] = {
            "passed": result.returncode == 0,
            "output": result.stdout
        }

        # Cleanup
        subprocess.run(["docker", "compose", "down"])

        return result.returncode == 0

    def run_integration_tests(self) -> bool:
        """Run integration tests."""
        print("🔗 Running integration tests...")

        # Custom integration test logic
        # Test database migrations, API contracts, etc.

        return True

    def run_security_tests(self) -> bool:
        """Run security tests."""
        print("🔒 Running security tests...")

        # Run bandit for Python security issues
        result = subprocess.run(
            ["bandit", "-r", "backend/app", "-f", "json", "-o", "bandit-report.json"],
            capture_output=True
        )

        # Run npm audit for frontend vulnerabilities
        npm_result = subprocess.run(
            ["npm", "audit", "--json"],
            cwd="frontend",
            capture_output=True,
            text=True
        )

        return result.returncode == 0

    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "="*60)
        print("📊 TEST AUTOMATION REPORT")
        print("="*60)

        for suite, results in self.results.items():
            if results:
                status = "✅ PASSED" if results.get("passed") else "❌ FAILED"
                print(f"\n{suite.upper()}: {status}")

                if "coverage" in results:
                    print(f"  Coverage: {results['coverage']:.2f}%")

        print("\n" + "="*60)

        # Write JSON report
        with open("test-report.json", "w") as f:
            json.dump(self.results, f, indent=2)

        print("📄 Detailed report saved to: test-report.json")

    def run_all(self) -> bool:
        """Run all test suites."""
        all_passed = True

        all_passed &= self.run_backend_tests()
        all_passed &= self.run_frontend_unit_tests()
        all_passed &= self.run_e2e_tests()
        all_passed &= self.run_integration_tests()
        all_passed &= self.run_security_tests()

        self.generate_report()

        return all_passed

if __name__ == "__main__":
    automation = TestAutomation()
    success = automation.run_all()

    sys.exit(0 if success else 1)
```

---

## Advanced Workflows

### Workflow 1: Blue-Green Deployment

```python
# blue_green_deployment.py
"""
Automated blue-green deployment workflow.
"""

class BlueGreenDeployment:
    """
    Implements blue-green deployment pattern.
    """

    def __init__(self, load_balancer_url: str):
        self.lb_url = load_balancer_url
        self.current_env = self._get_current_environment()

    def _get_current_environment(self) -> str:
        """Determine which environment is currently active."""
        # Query load balancer to see which target group is active
        # Return "blue" or "green"
        pass

    def deploy_new_version(self, version: str):
        """
        Deploy new version to inactive environment.

        Steps:
        1. Identify inactive environment (blue or green)
        2. Deploy new version to inactive environment
        3. Run health checks on new deployment
        4. Run smoke tests
        5. Switch traffic to new environment
        6. Monitor for issues
        7. Keep old environment as rollback target
        """
        # Determine target environment
        target_env = "green" if self.current_env == "blue" else "blue"

        print(f"Deploying version {version} to {target_env} environment...")

        # Deploy to target environment
        self._deploy_to_environment(target_env, version)

        # Wait for healthy
        if not self._wait_for_healthy(target_env):
            raise Exception(f"Deployment to {target_env} failed health checks")

        # Run smoke tests
        if not self._run_smoke_tests(target_env):
            raise Exception(f"Smoke tests failed on {target_env}")

        # Switch traffic
        print(f"Switching traffic from {self.current_env} to {target_env}...")
        self._switch_traffic(target_env)

        # Monitor for 5 minutes
        if not self._monitor_deployment(target_env, duration=300):
            print("Issues detected! Rolling back...")
            self._switch_traffic(self.current_env)
            raise Exception("Deployment monitoring detected issues")

        print(f"Deployment successful! {target_env} is now active.")

        # Keep old environment for 24h as rollback target
        print(f"Keeping {self.current_env} environment for 24h as rollback target")

    def rollback(self):
        """Instant rollback to previous environment."""
        previous_env = "green" if self.current_env == "blue" else "blue"
        print(f"Rolling back from {self.current_env} to {previous_env}...")
        self._switch_traffic(previous_env)
        print("Rollback complete!")
```

---

### Workflow 2: Canary Deployment

```python
# canary_deployment.py
"""
Automated canary deployment with gradual traffic shift.
"""

class CanaryDeployment:
    """
    Implements canary deployment pattern.
    """

    def deploy_canary(self, version: str):
        """
        Deploy canary with gradual traffic shift.

        Traffic progression: 5% → 25% → 50% → 100%
        At each stage, monitor metrics and auto-rollback if issues detected.
        """
        stages = [5, 25, 50, 100]

        # Deploy canary
        print(f"Deploying canary version {version}...")
        self._deploy_canary_instance(version)

        for traffic_percent in stages:
            print(f"Shifting {traffic_percent}% traffic to canary...")
            self._set_traffic_split(canary_percent=traffic_percent)

            # Monitor for 10 minutes
            if not self._monitor_canary(duration=600):
                print("Issues detected! Rolling back...")
                self._set_traffic_split(canary_percent=0)
                self._remove_canary()
                raise Exception("Canary deployment failed")

            print(f"{traffic_percent}% traffic shift successful")

        # Promote canary to stable
        print("Promoting canary to stable...")
        self._promote_canary()

    def _monitor_canary(self, duration: int) -> bool:
        """
        Monitor canary metrics vs stable.

        Check:
        - Error rate (should be < 2x stable)
        - Latency (should be < 1.5x stable)
        - CPU/Memory usage
        """
        import time

        start = time.time()
        while time.time() - start < duration:
            canary_metrics = self._get_metrics("canary")
            stable_metrics = self._get_metrics("stable")

            # Check error rate
            if canary_metrics["error_rate"] > stable_metrics["error_rate"] * 2:
                return False

            # Check latency
            if canary_metrics["p99_latency"] > stable_metrics["p99_latency"] * 1.5:
                return False

            time.sleep(30)

        return True
```

---

## Conclusion

This modular automation guide transforms the full-stack-fastapi-template into a **comprehensive automation resource** that can be:

1. **Integrated** into any automation framework (Airflow, Prefect, n8n, Zapier)
2. **Extracted** as standalone microservices (auth, user management, CRUD APIs)
3. **Deployed** with automated CI/CD pipelines
4. **Scaled** with Kubernetes, Docker Swarm, or cloud platforms
5. **Extended** with custom workflows and integrations

### Key Takeaways

✅ **Modular Design** - Every component can be used independently
✅ **Production-Ready** - Security, testing, and monitoring built-in
✅ **Automation-First** - Designed for CI/CD and workflow orchestration
✅ **Type-Safe** - Full type safety from database to frontend
✅ **Extensible** - Easy to add new features and integrations

### Next Steps

1. Choose the components you need for your automation workflow
2. Copy the relevant module templates
3. Integrate with your automation framework
4. Customize and extend as needed
5. Deploy with confidence

---

**Version:** 2.0
**Last Updated:** 2025-12-23
**Maintained By:** FastAPI Community
**License:** MIT
