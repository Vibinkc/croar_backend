import asyncio
import os
import sys

sys.path.append(os.getcwd())

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import db_manager
from app.models.enterprise.project import Project


async def verify():
    async with db_manager.session() as session:
        stmt = select(Project).options(selectinload(Project.members))
        result = await session.execute(stmt)
        projects = result.scalars().all()
        for p in projects:
            member_names = [f"{m.first_name} {m.last_name}" for m in p.members]
            print(f"Project: {p.name} | Members: {', '.join(member_names)}")


if __name__ == "__main__":
    asyncio.run(verify())
