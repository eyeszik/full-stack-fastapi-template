#!/usr/bin/env python3
"""
Quick Start: Python Automation with FastAPI Template
=====================================================

This script demonstrates how to quickly integrate the FastAPI template
into Python-based automation workflows.

Usage:
    python quickstart_python.py

Requirements:
    pip install requests pandas python-dotenv
"""

import requests
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class FastAPIClient:
    """Simple client for FastAPI template automation."""

    base_url: str
    token: Optional[str] = None

    def authenticate(self, email: str, password: str) -> str:
        """Authenticate and store token."""
        response = requests.post(
            f"{self.base_url}/api/v1/login/access-token",
            data={"username": email, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]
        return self.token

    @property
    def headers(self) -> dict:
        """Get authentication headers."""
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        return {"Authorization": f"Bearer {self.token}"}

    def get_users(self, skip: int = 0, limit: int = 100) -> dict:
        """Get all users (requires admin)."""
        response = requests.get(
            f"{self.base_url}/api/v1/users/",
            headers=self.headers,
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def create_user(self, email: str, password: str, full_name: str = None,
                   is_superuser: bool = False) -> dict:
        """Create a new user (requires admin)."""
        response = requests.post(
            f"{self.base_url}/api/v1/users/",
            headers=self.headers,
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
                "is_superuser": is_superuser
            }
        )
        response.raise_for_status()
        return response.json()

    def get_items(self, skip: int = 0, limit: int = 100) -> dict:
        """Get user's items."""
        response = requests.get(
            f"{self.base_url}/api/v1/items/",
            headers=self.headers,
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def create_item(self, title: str, description: str = None) -> dict:
        """Create a new item."""
        response = requests.post(
            f"{self.base_url}/api/v1/items/",
            headers=self.headers,
            json={"title": title, "description": description}
        )
        response.raise_for_status()
        return response.json()


def example_user_automation():
    """Example: Automated user provisioning."""

    # Initialize client
    client = FastAPIClient(base_url="http://localhost:8000")

    # Authenticate as admin
    client.authenticate(
        email=os.getenv("ADMIN_EMAIL", "admin@example.com"),
        password=os.getenv("ADMIN_PASSWORD", "changethis")
    )

    # Bulk create users from list
    new_users = [
        {"email": "user1@example.com", "password": "SecurePass123", "full_name": "User One"},
        {"email": "user2@example.com", "password": "SecurePass456", "full_name": "User Two"},
        {"email": "user3@example.com", "password": "SecurePass789", "full_name": "User Three"},
    ]

    created = []
    for user_data in new_users:
        try:
            user = client.create_user(**user_data)
            created.append(user)
            print(f"✅ Created user: {user['email']}")
        except requests.HTTPError as e:
            print(f"❌ Failed to create {user_data['email']}: {e}")

    print(f"\n📊 Summary: {len(created)}/{len(new_users)} users created")
    return created


def example_data_export():
    """Example: Export all users to CSV."""
    import pandas as pd

    client = FastAPIClient(base_url="http://localhost:8000")
    client.authenticate(
        email=os.getenv("ADMIN_EMAIL", "admin@example.com"),
        password=os.getenv("ADMIN_PASSWORD", "changethis")
    )

    # Get all users
    users_data = client.get_users(limit=1000)
    users = users_data["data"]

    # Convert to DataFrame
    df = pd.DataFrame(users)

    # Export to CSV
    output_file = "users_export.csv"
    df.to_csv(output_file, index=False)
    print(f"✅ Exported {len(users)} users to {output_file}")

    return df


def example_scheduled_cleanup():
    """Example: Scheduled cleanup automation (run daily via cron)."""

    client = FastAPIClient(base_url="http://localhost:8000")
    client.authenticate(
        email=os.getenv("ADMIN_EMAIL", "admin@example.com"),
        password=os.getenv("ADMIN_PASSWORD", "changethis")
    )

    # Get all users
    users = client.get_users(limit=1000)["data"]

    # Find inactive users (example logic)
    inactive_count = 0
    for user in users:
        if not user["is_active"]:
            inactive_count += 1
            # Could deactivate or delete here
            print(f"Found inactive user: {user['email']}")

    print(f"\n📊 Cleanup Summary: {inactive_count} inactive users found")


def example_integration_workflow():
    """Example: Complete integration workflow."""

    print("🚀 Starting automation workflow...\n")

    # Step 1: User provisioning
    print("Step 1: User Provisioning")
    print("-" * 40)
    created_users = example_user_automation()

    # Step 2: Data export
    print("\nStep 2: Data Export")
    print("-" * 40)
    df = example_data_export()

    # Step 3: Cleanup
    print("\nStep 3: Cleanup Check")
    print("-" * 40)
    example_scheduled_cleanup()

    print("\n✅ Workflow complete!")


if __name__ == "__main__":
    # Run the complete integration workflow
    example_integration_workflow()
