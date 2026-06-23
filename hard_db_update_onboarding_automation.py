import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def update_db() -> None:
    async with db_manager.session() as session:
        # Add company_id to onboarding_automations
        try:
            await session.execute(
                text(
                    "ALTER TABLE onboarding_automations ADD COLUMN company_id UUID REFERENCES companies(id) ON DELETE SET NULL;"
                )
            )
            print("Added company_id to onboarding_automations")
        except Exception as e:
            print(f"Error adding to onboarding_automations: {e}")

        # Backfill
        try:
            await session.execute(
                text(
                    "UPDATE onboarding_automations SET company_id = (SELECT id FROM companies WHERE slug = 'appxcess-corp' LIMIT 1) WHERE company_id IS NULL;"
                )
            )
            print("Backfilled company_id")
        except Exception as e:
            print(f"Error backfilling: {e}")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(update_db())
