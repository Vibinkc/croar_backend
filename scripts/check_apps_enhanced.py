import os
import sys

sys.path.append(os.getcwd())

import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate, CandidateApplication
from app.models.enterprise.job import JobRequirement


async def check_all_apps_enhanced():
    async with db_manager.sessionmaker() as session:
        stmt = (
            select(
                CandidateApplication.id,
                CandidateApplication.current_stage,
                JobRequirement.title,
                Candidate.full_name,
            )
            .join(Candidate)
            .join(JobRequirement)
        )
        result = await session.execute(stmt)
        apps = result.all()
        print(f"FOUND {len(apps)} APPLICATIONS")
        for app in apps:
            print(f"AppID:{app.id} | Stage:{app.current_stage} | Job:{app.title} | Name:{app.full_name}")


if __name__ == "__main__":
    asyncio.run(check_all_apps_enhanced())
