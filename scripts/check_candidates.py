import os
import sys

sys.path.append(os.getcwd())

import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate


async def check_candidates():
    async with db_manager.sessionmaker() as session:
        stmt = select(Candidate.id, Candidate.full_name, Candidate.email)
        result = await session.execute(stmt)
        objs = result.all()
        print(f"FOUND {len(objs)} CANDIDATES")
        for obj in objs:
            print(f"ID:{obj.id} | Email:{obj.email} | Name:{obj.full_name}")


if __name__ == "__main__":
    asyncio.run(check_candidates())
