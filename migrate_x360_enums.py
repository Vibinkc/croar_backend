import asyncio
import os
import sys

# Add current directory to path to import app modules
sys.path.append(os.getcwd())

from sqlalchemy import text

from app.core.database import db_manager


async def migrate() -> None:
    new_values = ["CULTURE", "STRATEGY", "INNOVATION", "PROBLEM_SOLVING"]
    type_name = "questioncategory"

    # Use the engine directly to avoid session overhead
    engine = db_manager.engine

    try:
        async with engine.connect() as conn:
            # Set isolation level to AUTOCOMMIT for ALTER TYPE
            await conn.execution_options(isolation_level="AUTOCOMMIT")

            for val in new_values:
                try:
                    await conn.execute(text(f"ALTER TYPE {type_name} ADD VALUE '{val}';"))
                    print(f"Successfully added {val} to {type_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"Value {val} already exists in {type_name}")
                    else:
                        print(f"Error adding {val}: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate())
