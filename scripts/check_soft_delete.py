import os
import sys

sys.path.append(os.getcwd())

import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate, CandidateApplication


async def check_soft_delete():
    async with db_manager.sessionmaker() as session:
        stmt = select(CandidateApplication.id, CandidateApplication.deleted_at, Candidate.full_name).join(
            Candidate
        )
        result = await session.execute(stmt)
        apps = result.all()
        for app in apps:
            print(f"ID:{app.id} | DeletedAt:{app.deleted_at} | Name:{app.full_name}")


if __name__ == "__main__":
    asyncio.run(check_soft_delete())
