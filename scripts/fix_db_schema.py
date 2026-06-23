import asyncio
import os
import sys

from sqlalchemy import text

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager


async def fix_db_schema():
    print("=== FIXING DATABASE SCHEMA FOR MULTI-TENANCY ===")

    commands = [
        # Onboarding
        "ALTER TABLE onboardings ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE SET NULL",
        "ALTER TABLE onboarding_templates ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE SET NULL",
        # Candidates
        "ALTER TABLE candidates ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE SET NULL",
        "ALTER TABLE candidate_applications ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE SET NULL",
        "ALTER TABLE candidate_applications ADD COLUMN IF NOT EXISTS source VARCHAR(50)",
        # Assessments
        "ALTER TABLE assessment_templates ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE SET NULL",
        "ALTER TABLE assessment_automations ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE SET NULL",
        # Communication
        "ALTER TABLE email_templates ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE SET NULL",
        # X360 (already had some, but just in case)
        "ALTER TABLE x360_assessment_cycles ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE CASCADE",
    ]

    async with db_manager.session() as session:
        for cmd in commands:
            try:
                print(f"Executing: {cmd}")
                await session.execute(text(cmd))
                print("Success.")
            except Exception as e:
                print(f"Error: {e}")

        await session.commit()

    print("\n=== SCHEMA FIX COMPLETE ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_db_schema())
