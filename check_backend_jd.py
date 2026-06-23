import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.assessment import AssessmentAutomation
from app.models.enterprise.communication import MailAutomation
from app.models.enterprise.interview import InterviewAutomation
from app.models.enterprise.job import JobRequirement


async def main():
    output = []
    async with db_manager.session() as session:
        stmt = select(JobRequirement).where(JobRequirement.title.ilike("%Backend Developer%"))
        result = await session.execute(stmt)
        jobs = result.scalars().all()

        if not jobs:
            output.append("Backend Developer job not found.")
        else:
            for job in jobs:
                output.append(f"\nFound Job: {job.title} (ID: {job.id})")
                output.append(f"Workflow Stages: {job.workflow_stages}")

                # Check Mail Automations
                output.append("\n--- Mail Automations ---")
                stmt = select(MailAutomation).where(MailAutomation.job_requirement_id == job.id)
                res = await session.execute(stmt)
                for auto in res.scalars().all():
                    output.append(f"Stage {auto.stage_index}: {auto.id} (Enabled: {auto.is_enabled})")

                # Check Assessment Automations
                output.append("\n--- Assessment Automations ---")
                stmt = select(AssessmentAutomation).where(AssessmentAutomation.job_requirement_id == job.id)
                res = await session.execute(stmt)
                for auto in res.scalars().all():
                    output.append(
                        f"Stage {auto.stage_index}: {auto.topic} (Type: {auto.type}, Enabled: {auto.is_enabled})"
                    )

                # Check Interview Automations
                output.append("\n--- Interview Automations ---")
                stmt = select(InterviewAutomation).where(InterviewAutomation.job_requirement_id == job.id)
                res = await session.execute(stmt)
                for auto in res.scalars().all():
                    output.append(f"Stage {auto.stage_index}: {auto.id} (Enabled: {auto.is_enabled})")

    with open("jd_info_v2.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print("Done. Output written to jd_info_v2.txt")


if __name__ == "__main__":
    asyncio.run(main())
