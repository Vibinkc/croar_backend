import asyncio

from app.db.session import async_session
from sqlalchemy import select

from app.models.enterprise.candidate import CandidateApplication
from app.services.enterprise.automation_service import trigger_automations


async def main():
    async with async_session() as session:
        stmt = select(CandidateApplication).order_by(CandidateApplication.applied_at.desc()).limit(1)
        res = await session.execute(stmt)
        app = res.scalar_one_or_none()
        if not app:
            print("No app found")
            return
        print(f"Triggering for app {app.id}")
        await trigger_automations(app.id, 1, session)


asyncio.run(main())
