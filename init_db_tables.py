import asyncio

from sqlalchemy import text

from app.core.database import Base, db_manager

# Explicitly import all models to ensure they are registered with Base.metadata


async def main() -> None:
    print("Connecting to database...")
    async with db_manager.engine.begin() as conn:
        print("Enabling UUID extension...")
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
        print(f"Registered tables: {list(Base.metadata.tables.keys())}")
        print("Creating all tables from models...")
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")
    await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())
