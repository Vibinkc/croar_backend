import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def fix_db():
    print("Checking onboarding_automations table for auto_move column...")
    async with db_manager.session() as session:
        # Check if column exists
        check_stmt = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'onboarding_automations' AND column_name = 'auto_move'
        """)
        res = await session.execute(check_stmt)
        exists = res.scalar_one_or_none()

        if not exists:
            print("Adding auto_move column to onboarding_automations...")
            add_stmt = text("ALTER TABLE onboarding_automations ADD COLUMN auto_move BOOLEAN DEFAULT FALSE")
            await session.execute(add_stmt)
            await session.commit()
            print("Successfully added auto_move column.")
        else:
            print("auto_move column already exists.")


if __name__ == "__main__":
    asyncio.run(fix_db())
