import os
import sys

sys.path.append(os.getcwd())

import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate, CandidateApplication


async def check_scores():
    async with db_manager.sessionmaker() as session:
        stmt = select(CandidateApplication.id, CandidateApplication.ai_match_score, Candidate.full_name).join(
            Candidate
        )
        result = await session.execute(stmt)
        apps = result.all()
        for app in apps:
            print(f"AppID:{app.id} | Score:{app.ai_match_score} | Name:{app.full_name}")


if __name__ == "__main__":
    asyncio.run(check_scores())
