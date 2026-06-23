import asyncio

from sqlalchemy import text

from app.core.database import db_manager

APPXCESS_ID = "900125e1-1ab6-47e5-a410-2515ab2e89c0"

TABLES_TO_UPDATE = [
    "onboarding_documents",
    "onboarding_tasks",
    "onboarding_notes",
    "interviews",
    "interview_automations",
    "interview_schedules",
    "interview_attempts",
    "project_members",
    "project_tasks",
    "simulation_assignments",
    "simulation_sessions",
    "enterprise_students",
    "survey_types",
    "survey_questions",
    "survey_invites",
    "survey_responses",
    "x360_template_questions",
    "x360_assessment_assignments",
    "x360_assessment_responses",
    "x360_employee_rater_maps",
]


async def update_db():
    print(f"Starting final multi-tenancy DB update. Backfilling to: {APPXCESS_ID}")

    async with db_manager.engine.begin() as conn:
        for table in TABLES_TO_UPDATE:
            print(f"Processing table: {table}")

            # 1. Add column if it doesn't exist
            await conn.execute(
                text(f"""
                ALTER TABLE {table}
                ADD COLUMN IF NOT EXISTS company_id UUID
                REFERENCES companies(id) ON DELETE CASCADE;
            """)
            )

            # 2. Backfill existing records
            result = await conn.execute(
                text(f"UPDATE {table} SET company_id = :cid WHERE company_id IS NULL"), {"cid": APPXCESS_ID}
            )
            print(f"  Updated {result.rowcount} rows in {table}")

    print("DB migration complete!")


if __name__ == "__main__":
    asyncio.run(update_db())
