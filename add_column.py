import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def add_column():
    async with db_manager.engine.begin() as conn:
        print("Adding is_self_registered column to users table...")
        await conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_self_registered BOOLEAN DEFAULT FALSE")
        )
    print("Column added successfully.")
    await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(add_column())
