import asyncio

import asyncpg

from app.core.settings import get_settings


async def check_tables() -> None:
    s = get_settings()
    conn = await asyncpg.connect(
        user=s.db_user, password=s.db_password, database=s.db_name, host=s.db_host, port=s.db_port
    )
    tables = await conn.fetch("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
    print(f"Tables in {s.db_name}: {[r[0] for r in tables]}")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(check_tables())
