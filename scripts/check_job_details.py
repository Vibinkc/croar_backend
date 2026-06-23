import os
import sys

sys.path.append(os.getcwd())

import asyncio
from uuid import UUID

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.job import JobRequirement


async def check_job():
    job_id = UUID("f81d4fae-7dec-11d0-a765-00a0c91e6bf6")
    async with db_manager.sessionmaker() as session:
        stmt = select(JobRequirement).where(JobRequirement.id == job_id)
        result = await session.execute(stmt)
        job = result.scalar_one_or_none()
        if job:
            print(f"JOB: {job.title}")
            print(f"STAGES: {job.workflow_stages}")
        else:
            print("JOB NOT FOUND")


if __name__ == "__main__":
    asyncio.run(check_job())
