import asyncio

from sqlalchemy import text

# Ensure all models are imported
from app.core.database import Base, db_manager


async def force_fix() -> None:
    print("MetaData tables:", list(Base.metadata.tables.keys()))
    try:
        engine = db_manager.management_engine
        async with engine.begin() as conn:
            # Drop tables that we know are outdated
            await conn.execute(text("DROP TABLE IF EXISTS candidate_applications CASCADE;"))
            await conn.execute(text("DROP TABLE IF EXISTS candidates CASCADE;"))
            print("Dropped candidate related tables.")

            # Recreate all
            await conn.run_sync(Base.metadata.create_all)
            print("Base.metadata.create_all called.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(force_fix())
