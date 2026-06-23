import asyncio

from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.enterprise.interview import InterviewAttempt


async def main():
    async with async_session_maker() as session:
        # Check attempts
        stmt = select(InterviewAttempt)
        result = await session.execute(stmt)
        attempts = result.scalars().all()

        print(f"Total Attempts: {len(attempts)}")
        for a in attempts:
            print(f"Attempt: {a.id}, Schedule: {a.schedule_id}, Score: {a.overall_score}")


asyncio.run(main())
