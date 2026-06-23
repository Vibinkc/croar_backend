import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.communication import MailAutomation


async def main():
    async with db_manager.session() as session:
        stmt = select(MailAutomation).where(MailAutomation.auto_move)
        res = await session.execute(stmt)
        automations = res.scalars().all()

        print(f"Found {len(automations)} automations with auto_move=True")
        for auto in automations:
            print(f"ID: {auto.id}, Job: {auto.job_requirement_id}, Stage: {auto.stage_index}")


if __name__ == "__main__":
    asyncio.run(main())
