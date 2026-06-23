import asyncio

from sqlalchemy import func, select

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate, CandidateApplication
from app.models.enterprise.interview import InterviewSchedule
from app.models.enterprise.job import JobRequirement


async def check_counts():
    async with db_manager.get_session() as session:
        # Active Jobs
        stmt = select(func.count(JobRequirement.id)).where(JobRequirement.deleted_at is None)
        jobs_count = (await session.execute(stmt)).scalar() or 0

        # Total Candidates
        stmt = select(func.count(Candidate.id))
        candidates_count = (await session.execute(stmt)).scalar() or 0

        # Total Applications
        stmt = select(func.count(CandidateApplication.id))
        apps_count = (await session.execute(stmt)).scalar() or 0

        # Interviews
        stmt = select(func.count(InterviewSchedule.id))
        interviews_count = (await session.execute(stmt)).scalar() or 0

        # High value matches
        stmt = select(func.count(CandidateApplication.id)).where(CandidateApplication.ai_match_score >= 80)
        high_value = (await session.execute(stmt)).scalar() or 0

        print(f"Jobs: {jobs_count}")
        print(f"Candidates: {candidates_count}")
        print(f"Applications: {apps_count}")
        print(f"Interviews: {interviews_count}")
        print(f"High Value: {high_value}")


if __name__ == "__main__":
    asyncio.run(check_counts())
