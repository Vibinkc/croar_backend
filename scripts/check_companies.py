import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def get_companies():
    async with db_manager.engine.begin() as conn:
        result = await conn.execute(text("SELECT id, slug, name FROM companies"))
        companies = result.fetchall()
        for row in companies:
            print(f"ID: {row[0]}, Slug: {row[1]}, Name: {row[2]}")


if __name__ == "__main__":
    asyncio.run(get_companies())
