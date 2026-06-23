import asyncio

import sqlalchemy as sa

from app.core.database import db_manager


async def main() -> None:
    print("Enabling uuid-ossp extension...")
    async with db_manager.engine.begin() as conn:
        await conn.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
    print("Extension enabled successfully.")
    await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())
