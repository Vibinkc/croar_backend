import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.job import JobRequirement


async def verify_job():
    async with db_manager.session() as session:
        res = await session.execute(
            select(JobRequirement)
            .where(JobRequirement.title == "Senior React Developer")
            .order_by(JobRequirement.created_at.desc())
            .limit(1)
        )
        j = res.scalar()
        if j:
            print(f"VERIFIED: Job '{j.title}' exists with ID {j.id}")
            print(f"Location: {j.location}, Experience: {j.experience_min}-{j.experience_max}")
        else:
            print("JOB_NOT_FOUND")


if __name__ == "__main__":
    asyncio.run(verify_job())
