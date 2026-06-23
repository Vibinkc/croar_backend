import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate, CandidateApplication
from app.models.enterprise.job import JobRequirement
from app.models.enterprise.onboarding import Onboarding


async def main():
    async with db_manager.session() as session:
        # 1. JobRequirement for Backend Developer
        stmt = select(JobRequirement).where(JobRequirement.title.ilike("%Backend Developer%"))
        result = await session.execute(stmt)
        jobs = result.scalars().all()

        for job in jobs:
            print("\n==========================================")
            print(f"Found Job: {job.title} (ID: {job.id})")
            print(f"Workflow Stages: {job.workflow_stages}")

            # 2. CandidateApplications in Onboarding Stage
            stmt = (
                select(CandidateApplication, Candidate)
                .join(Candidate)
                .where(
                    CandidateApplication.job_requirement_id == job.id, CandidateApplication.current_stage >= 5
                )
            )
            res = await session.execute(stmt)
            for app, cand in res.all():
                print(f"Candidate: {cand.full_name} (Application ID: {app.id})")
                print(f"  Current Stage: {app.current_stage}")

                # Check Onboarding
                stmt_onb = select(Onboarding).where(Onboarding.application_id == app.id)
                res_onb = await session.execute(stmt_onb)
                onb = res_onb.scalars().first()
                print(f"  Onboarding Record: {'Found (ID: ' + str(onb.id) + ')' if onb else 'Not Found'}")


if __name__ == "__main__":
    asyncio.run(main())
