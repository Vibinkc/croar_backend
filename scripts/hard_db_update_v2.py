import asyncio
import os
import sys

from sqlalchemy import text

# Ensure the app code is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager


async def update_db():
    print("=== STARTING DATABASE SCHEMA UPDATE V2 ===")
    async with db_manager.session() as session:
        # 1. Update companies table
        try:
            await session.execute(
                text("ALTER TABLE companies ADD COLUMN IF NOT EXISTS is_consultancy BOOLEAN DEFAULT FALSE;")
            )
            await session.execute(
                text("UPDATE companies SET is_consultancy = FALSE WHERE is_consultancy IS NULL;")
            )
            print("Verified companies.is_consultancy")
        except Exception as e:
            print(f"Notice (companies): {e}")

        # 2. Update onboarding_templates table
        try:
            await session.execute(
                text(
                    "ALTER TABLE onboarding_templates ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE SET NULL;"
                )
            )
            print("Verified onboarding_templates.company_id")
        except Exception as e:
            print(f"Notice (onboarding_templates): {e}")

        # 3. Update survey_types table
        try:
            await session.execute(
                text(
                    "ALTER TABLE survey_types ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE CASCADE;"
                )
            )
            print("Verified survey_types.company_id")
        except Exception as e:
            print(f"Notice (survey_types): {e}")

        # 4. Update survey_questions table
        try:
            await session.execute(
                text(
                    "ALTER TABLE survey_questions ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE CASCADE;"
                )
            )
            print("Verified survey_questions.company_id")
        except Exception as e:
            print(f"Notice (survey_questions): {e}")

        # 5. Update survey_invites table
        try:
            await session.execute(
                text(
                    "ALTER TABLE survey_invites ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE CASCADE;"
                )
            )
            print("Verified survey_invites.company_id")
        except Exception as e:
            print(f"Notice (survey_invites): {e}")

        # 6. Update survey_responses table
        try:
            await session.execute(
                text(
                    "ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id) ON DELETE CASCADE;"
                )
            )
            print("Verified survey_responses.company_id")
        except Exception as e:
            print(f"Notice (survey_responses): {e}")

        await session.commit()
    print("=== DATABASE SCHEMA UPDATE COMPLETE ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(update_db())
