import os
import sys

sys.path.append(os.getcwd())

import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.job import JobRequirement


async def list_jobs():
    async with db_manager.sessionmaker() as session:
        stmt = select(JobRequirement.id, JobRequirement.title, JobRequirement.workflow_stages)
        result = await session.execute(stmt)
        jobs = result.all()
        print(f"FOUND {len(jobs)} JOBS")
        for job in jobs:
            print(f"ID:{job.id} | Title:{job.title} | Stages:{job.workflow_stages}")


if __name__ == "__main__":
    asyncio.run(list_jobs())
