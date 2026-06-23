import os
import sys

sys.path.append(os.getcwd())

import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate, CandidateApplication


async def check_apps():
    async with db_manager.sessionmaker() as session:
        stmt = select(
            CandidateApplication.id,
            CandidateApplication.current_stage,
            CandidateApplication.job_requirement_id,
            Candidate.full_name,
        ).join(Candidate)
        result = await session.execute(stmt)
        apps = result.all()
        print(f"FOUND {len(apps)} APPLICATIONS")
        for app in apps:
            print(
                f"ID:{app.id} | Stage:{app.current_stage} | JobIdx:{app.job_requirement_id} | Name:{app.full_name}"
            )


if __name__ == "__main__":
    asyncio.run(check_apps())
