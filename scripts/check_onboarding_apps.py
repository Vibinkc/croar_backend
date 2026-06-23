import os
import sys

sys.path.append(os.getcwd())

import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.onboarding import Onboarding


async def check_onboarding():
    async with db_manager.sessionmaker() as session:
        stmt = select(Onboarding.id, Onboarding.application_id)
        result = await session.execute(stmt)
        objs = result.all()
        for obj in objs:
            print(f"OnbID:{obj.id} | AppID:{obj.application_id}")


if __name__ == "__main__":
    asyncio.run(check_onboarding())
