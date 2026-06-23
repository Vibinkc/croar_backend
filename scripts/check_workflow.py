import asyncio

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.enterprise.job import JobRequirement


async def check_workflow():
    async with SessionLocal() as session:
        stmt = select(JobRequirement.workflow_stages).limit(1)
        result = await session.execute(stmt)
        stages = result.scalar()
        print(f"STAGES:{stages}")


if __name__ == "__main__":
    asyncio.run(check_workflow())
