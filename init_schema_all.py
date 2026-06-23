import asyncio
import os
import sys

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from app.core.database import Base, db_manager

# Import all models to ensure they are registered with Base.metadata


async def main() -> None:
    print("Connecting to database...")
    async with db_manager.engine.begin() as conn:
        print("Enabling uuid-ossp extension...")
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))

        print("Creating all tables from models...")
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")
    await db_manager.close_all()


if __name__ == "__main__":
    from sqlalchemy import text

    asyncio.run(main())
