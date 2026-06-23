import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.communication import EmailTemplate


async def check():
    async with db_manager.session() as s:
        res = await s.execute(select(EmailTemplate.name))
        print(res.scalars().all())


if __name__ == "__main__":
    asyncio.run(check())
