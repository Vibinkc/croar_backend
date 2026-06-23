import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def update_db() -> None:
    async with db_manager.session() as session:
        # Add company_id to email_logs
        try:
            await session.execute(
                text(
                    "ALTER TABLE email_logs ADD COLUMN company_id UUID REFERENCES companies(id) ON DELETE SET NULL;"
                )
            )
            print("Added company_id to email_logs")
        except Exception as e:
            print(f"Error adding to email_logs: {e}")

        # Add company_id to mail_automations
        try:
            await session.execute(
                text(
                    "ALTER TABLE mail_automations ADD COLUMN company_id UUID REFERENCES companies(id) ON DELETE SET NULL;"
                )
            )
            print("Added company_id to mail_automations")
        except Exception as e:
            print(f"Error adding to mail_automations: {e}")

        # Backfill
        try:
            await session.execute(
                text(
                    "UPDATE email_logs SET company_id = (SELECT id FROM companies WHERE slug = 'appxcess-corp' LIMIT 1) WHERE company_id IS NULL;"
                )
            )
            await session.execute(
                text(
                    "UPDATE mail_automations SET company_id = (SELECT id FROM companies WHERE slug = 'appxcess-corp' LIMIT 1) WHERE company_id IS NULL;"
                )
            )
            print("Backfilled company_id")
        except Exception as e:
            print(f"Error backfilling: {e}")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(update_db())
