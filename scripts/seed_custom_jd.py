import asyncio
import os
import sys
from datetime import datetime
from uuid import uuid4

# Ensure the app code is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate, CandidateApplication
from app.models.enterprise.job import JobRequirement, JobStatus
from app.models.enterprise.onboarding import OnboardingAutomation, OnboardingTemplate


async def seed_custom_workflow():
    print("=== SEEDING CUSTOM WORKFLOW DATA ===")

    async with db_manager.session() as session:
        # 1. Get/Create Active Job Status
        from sqlalchemy import select

        from app.models.enterprise.candidate import ApplicationStatus

        stmt = select(JobStatus).where(JobStatus.name == "ACTIVE")
        result = await session.execute(stmt)
        status = result.scalar_one_or_none()
        if not status:
            stmt = select(JobStatus).limit(1)
            result = await session.execute(stmt)
            status = result.scalar_one_or_none()

            if not status:
                status = JobStatus(name="ACTIVE", is_system=True)
                session.add(status)
                try:
                    await session.flush()
                except:
                    await session.rollback()
                    stmt = select(JobStatus).limit(1)
                    result = await session.execute(stmt)
                    status = result.scalar_one()

        # Get/Create Application Status
        stmt = select(ApplicationStatus).where(ApplicationStatus.name == "APPLIED")
        result = await session.execute(stmt)
        app_status = result.scalar_one_or_none()
        if not app_status:
            stmt = select(ApplicationStatus).limit(1)
            result = await session.execute(stmt)
            app_status = result.scalar_one_or_none()
            if not app_status:
                app_status = ApplicationStatus(name="APPLIED", is_system=True)
                session.add(app_status)
                await session.flush()

        # 2. Create Custom Job
        # Use a fixed ID or check for existence to allow re-runs
        job_title = "Senior AI Engineer (Custom Pipeline)"
        stmt = select(JobRequirement).where(JobRequirement.title == job_title)
        result = await session.execute(stmt)
        job = result.scalar_one_or_none()

        if job:
            print(f"Job '{job_title}' already exists, reusing it.")
            job_id = job.id
        else:
            job_id = uuid4()
            custom_stages = [
                {"id": "1", "name": "Resume Screening", "type": "Screening"},
                {"id": "2", "name": "Technical Assessment", "type": "Assessment"},
                {"id": "3", "name": "HR Interview", "type": "Interview"},
                {"id": "4", "name": "Final Leadership Round", "type": "Interview"},
                {"id": "5", "name": "Documentation & Offer", "type": "Onboarding"},
            ]

            company_id = "626ce885-1b7d-424d-a891-f015cf725874"

            job = JobRequirement(
                id=job_id,
                title=job_title,
                description="A role with custom stages to test the dynamic Kanban board.",
                status_id=status.id,
                company_id=company_id,
                workflow_stages=custom_stages,
                location="Remote",
                job_type="Full-time",
            )
            session.add(job)
            print(f"Created Job: {job.title} with {len(custom_stages)} stages")

        # 3. Create Candidates and Applications
        candidate_names = ["Alice Smith", "Bob Johnson", "Charlie Davis"]
        for i, name in enumerate(candidate_names):
            email = f"{name.lower().replace(' ', '.')}@example.com"
            stmt = select(Candidate).where(Candidate.email == email)
            result = await session.execute(stmt)
            candidate = result.scalar_one_or_none()

            if not candidate:
                candidate = Candidate(
                    id=uuid4(), full_name=name, email=email, skills=["Python", "AI", "React"]
                )
                session.add(candidate)
                await session.flush()
                print(f"Created Candidate: {name}")
            else:
                print(f"Candidate '{name}' already exists.")

            # Check for existing application
            stmt = select(CandidateApplication).where(
                CandidateApplication.candidate_id == candidate.id,
                CandidateApplication.job_requirement_id == job_id,
            )
            result = await session.execute(stmt)
            app = result.scalar_one_or_none()

            if not app:
                # Place them in different stages
                app = CandidateApplication(
                    id=uuid4(),
                    candidate_id=candidate.id,
                    job_requirement_id=job_id,
                    status_id=app_status.id,
                    current_stage=i + 1,  # Alice in 1, Bob in 2, Charlie in 3
                    applied_at=datetime.now(),
                )
                session.add(app)
                print(f"Added Application: {name} at Stage {i + 1}")
            else:
                print(f"Application for {name} already exists.")

        # 4. Set up Onboarding Automation for Stage 5
        # First, ensure a template exists
        stmt = select(OnboardingTemplate).limit(1)
        result = await session.execute(stmt)
        template = result.scalar_one_or_none()

        if template:
            # Check for existing automation
            stmt = select(OnboardingAutomation).where(
                OnboardingAutomation.job_requirement_id == job_id, OnboardingAutomation.workflow_stage_id == 5
            )
            result = await session.execute(stmt)
            automation = result.scalar_one_or_none()

            if not automation:
                automation = OnboardingAutomation(
                    id=uuid4(),
                    job_requirement_id=job_id,
                    workflow_stage_id=5,  # Stage 5: Documentation & Offer
                    template_id=template.id,
                    is_active=True,
                    auto_move=True,
                )
                session.add(automation)
                print(f"Set up Onboarding Automation for Stage 5 using template: {template.name}")
            else:
                print("Onboarding Automation for Stage 5 already exists.")
        else:
            print("No onboarding templates found, skipping automation seed.")

        await session.commit()
        print("\n=== CUSTOM SEEDING COMPLETE ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_custom_workflow())
