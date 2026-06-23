import asyncio
import json

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate, CandidateApplication
from app.models.enterprise.job import JobRequirement
from app.models.enterprise.onboarding import Onboarding


async def main():
    results = []
    async with db_manager.session() as session:
        # Check ALL jobs now
        stmt = select(JobRequirement).where(JobRequirement.workflow_stages is not None)
        result = await session.execute(stmt)
        jobs = result.scalars().all()

        for job in jobs:
            job_info = {
                "job_title": job.title,
                "job_id": str(job.id),
                "workflow_stages": job.workflow_stages,
                "applications": [],
            }

            stmt = (
                select(CandidateApplication, Candidate)
                .join(Candidate)
                .where(CandidateApplication.job_requirement_id == job.id)
            )
            res = await session.execute(stmt)
            for app, cand in res.all():
                app_info = {
                    "candidate_name": cand.full_name,
                    "application_id": str(app.id),
                    "current_stage": app.current_stage,
                    "onboarding_record": None,
                }

                stmt_onb = select(Onboarding).where(Onboarding.application_id == app.id)
                res_onb = await session.execute(stmt_onb)
                onb = res_onb.scalars().first()
                if onb:
                    app_info["onboarding_record"] = str(onb.id)

                job_info["applications"].append(app_info)

            results.append(job_info)

    with open("all_jobs_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Results written to all_jobs_results.json")


if __name__ == "__main__":
    asyncio.run(main())
