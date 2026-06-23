import asyncio

from sqlalchemy import update

from app.core.database import db_manager
from app.models.enterprise.job import JobRequirement


async def update_job():
    async with db_manager.session() as session:
        await session.execute(
            update(JobRequirement).where(JobRequirement.title.like("%React Developer%")).values(status_id=2)
        )
        await session.commit()
        print("SUCCESS: All React Developer jobs are now ACTIVE (Status ID 2).")


if __name__ == "__main__":
    asyncio.run(update_job())
