import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def patch_db() -> None:
    async with db_manager.session() as session:
        try:
            # Check if column exists
            check_sql = text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'onboardings' AND column_name = 'rejected_fields';"
            )
            result = await session.execute(check_sql)
            if not result.scalar():
                print("Adding 'rejected_fields' column to 'onboardings' table...")
                add_sql = text(
                    "ALTER TABLE onboardings ADD COLUMN rejected_fields JSONB NOT NULL DEFAULT '[]';"
                )
                await session.execute(add_sql)
                await session.commit()
                print("Column added successfully.")
            else:
                print("'rejected_fields' column already exists.")
        except Exception as e:
            print(f"Error patching database: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(patch_db())
