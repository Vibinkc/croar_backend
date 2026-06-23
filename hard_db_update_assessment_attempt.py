import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def update_db() -> None:
    async with db_manager.session() as session:
        # Add company_id to assessment_attempts
        try:
            await session.execute(
                text(
                    "ALTER TABLE assessment_attempts ADD COLUMN company_id UUID REFERENCES companies(id) ON DELETE SET NULL;"
                )
            )
            print("Added company_id to assessment_attempts")
        except Exception as e:
            print(f"Error adding to assessment_attempts: {e}")

        # Backfill
        try:
            await session.execute(
                text(
                    "UPDATE assessment_attempts SET company_id = (SELECT id FROM companies WHERE slug = 'appxcess-corp' LIMIT 1) WHERE company_id IS NULL;"
                )
            )
            print("Backfilled company_id")
        except Exception as e:
            print(f"Error backfilling: {e}")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(update_db())
