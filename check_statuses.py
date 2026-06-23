import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.job import JobStatus


async def check_statuses():
    async with db_manager.session() as session:
        res = await session.execute(select(JobStatus))
        statuses = res.scalars().all()
        print("JOB STATUSES IN DATABASE:")
        for s in statuses:
            print(f"ID: {s.id}, Name: {s.name}")


if __name__ == "__main__":
    asyncio.run(check_statuses())
