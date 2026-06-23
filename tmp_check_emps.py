import asyncio
import os
import sys

sys.path.append(os.getcwd())

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.employee import Employee


async def check_emps():
    async with db_manager.session() as session:
        stmt = select(Employee)
        result = await session.execute(stmt)
        emps = result.scalars().all()
        for e in emps:
            print(f"ID: {e.id} | EMP_ID: {e.employee_id} | Name: {e.first_name} {e.last_name}")


if __name__ == "__main__":
    asyncio.run(check_emps())
