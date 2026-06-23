import asyncio
import os
import sys

import asyncpg

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from app.core.settings import get_settings


async def check_db() -> None:
    s = get_settings()
    try:
        conn = await asyncpg.connect(
            user=s.db_user, password=s.db_password, database="postgres", host=s.db_host, port=s.db_port
        )
        res = await conn.fetchval(f"SELECT 1 FROM pg_database WHERE datname='{s.db_name}'")
        print(f"Database {s.db_name} exists: {bool(res)}")

        if not res:
            print(f"Creating database {s.db_name}...")
            await conn.execute(f'CREATE DATABASE "{s.db_name}"')
            print("Database created.")

        await conn.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(check_db())
