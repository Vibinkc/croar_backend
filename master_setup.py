import asyncio
import os
import sys

# Add the current directory to sys.path to ensure imports work
sys.path.append(os.getcwd())

from sqlalchemy import text

from app.core.database import Base, db_manager

# 1. IMPORT ALL MODELS EXPLICITLY (Order matters for circular refs)
print("--- Loading Models ---")

# 2. SEEDING IMPORTS
from scripts.seed_application_statuses import seed_application_statuses
from scripts.seed_enterprise import seed_enterprise
from scripts.seed_job_statuses import seed_job_statuses
from scripts.seed_onboarding_template import seed_onboarding_template
from scripts.seed_orgs_v2 import run_seed as seed_orgs
from scripts.seed_rbac import seed_rbac
from scripts.seed_surveys import seed_survey_types as seed_surveys
from scripts.seed_x360 import seed_x360
from seed_consultancy import seed_consultancy
from seed_email_templates import seed_templates as seed_email_templates
from seed_onboarding_statuses import seed_statuses as seed_onboarding_statuses
from seed_professional_onboarding import seed_professional_template as seed_professional_onboarding
from seed_system_settings import seed_settings


async def master_init() -> None:

    print("\n=== MASTER DATABASE INITIALIZATION STARTED ===")

    # A. INITIALIZE TABLES AND RUN MIGRATIONS
    try:
        print("\nStep 1: Running Database Migrations...")
        import subprocess

        res = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"], capture_output=True, text=True
        )
        print(res.stdout)
        if res.returncode != 0:
            print(f"[ERROR] Migration failed with exit code {res.returncode}: {res.stderr}")
            print("Falling back to Base.metadata.create_all...")
            async with db_manager.engine.begin() as conn:
                print("  - Enabling 'uuid-ossp' extension...")
                await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                print(f"  - Tables found in metadata: {len(Base.metadata.tables)}")
                await conn.run_sync(Base.metadata.create_all)
        else:
            print("[SUCCESS] Database migrations completed successfully.")
    except Exception as e:
        print(f"[ERROR] Error during database migrations: {e}")
        print("Falling back to Base.metadata.create_all...")
        async with db_manager.engine.begin() as conn:
            print("  - Enabling 'uuid-ossp' extension...")
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            print(f"  - Tables found in metadata: {len(Base.metadata.tables)}")
            await conn.run_sync(Base.metadata.create_all)
        print("[SUCCESS] Fallback table creation complete.")

    # B. RUN SEEDING IN ORDER
    print("\nStep 2: Running Seeding Sequence...")

    try:
        print("  - Seeding System Settings...")
        await seed_settings()
    except Exception as e:
        print(f"[WARNING] Failed to seed system settings: {e}")

    try:
        print("  - Seeding RBAC (Roles & Permissions)...")
        await seed_rbac()
    except Exception as e:
        print(f"[WARNING] Failed to seed RBAC: {e}")

    try:
        print("  - Seeding Organizations...")
        await seed_orgs()
    except Exception as e:
        print(f"[WARNING] Failed to seed Organizations: {e}")

    try:
        print("  - Seeding Consultancy...")
        await seed_consultancy()
    except Exception as e:
        print(f"[WARNING] Failed to seed Consultancy: {e}")

    try:
        print("  - Seeding Enterprise Data...")
        await seed_enterprise()
    except Exception as e:
        print(f"[WARNING] Failed to seed Enterprise Data: {e}")

    try:
        print("  - Seeding Application Statuses...")
        await seed_application_statuses()
    except Exception as e:
        print(f"[WARNING] Failed to seed Application Statuses: {e}")

    try:
        print("  - Seeding Job Statuses...")
        await seed_job_statuses()
    except Exception as e:
        print(f"[WARNING] Failed to seed Job Statuses: {e}")

    try:
        print("  - Seeding Onboarding Statuses...")
        await seed_onboarding_statuses()
    except Exception as e:
        print(f"[WARNING] Failed to seed Onboarding Statuses: {e}")

    try:
        print("  - Seeding Email Templates...")
        await seed_email_templates()
    except Exception as e:
        print(f"[WARNING] Failed to seed Email Templates: {e}")

    try:
        print("  - Seeding Professional Onboarding...")
        await seed_professional_onboarding()
    except Exception as e:
        print(f"[WARNING] Failed to seed Professional Onboarding: {e}")

    try:
        print("  - Seeding Onboarding Template...")
        await seed_onboarding_template()
    except Exception as e:
        print(f"[WARNING] Failed to seed Onboarding Template: {e}")

    try:
        print("  - Seeding X360 Data...")
        await seed_x360()
    except Exception as e:
        print(f"[WARNING] Failed to seed X360 Data: {e}")

    try:
        print("  - Seeding Surveys...")
        await seed_surveys()
    except Exception as e:
        print(f"[WARNING] Failed to seed Surveys: {e}")

    await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(master_init())
