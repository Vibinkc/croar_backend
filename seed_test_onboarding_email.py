import asyncio

from sqlalchemy import delete, select

from app.core.database import db_manager
from app.models.enterprise.candidate import ApplicationStatus, Candidate, CandidateApplication
from app.models.enterprise.communication import EmailLog
from app.models.enterprise.onboarding import Onboarding
from app.services.enterprise.onboarding_service import initiate_onboarding_process


async def seed_test_email():
    async with db_manager.session() as session:
        # 1. Clear old email logs as requested
        print("Clearing old email logs...")
        await session.execute(delete(EmailLog))
        await session.flush()

        # 2. Get a test candidate or create one
        print("Finding test candidate...")
        stmt = select(Candidate).where(Candidate.email == "vibin@example.com")
        res = await session.execute(stmt)
        candidate = res.scalar_one_or_none()

        if not candidate:
            candidate = Candidate(full_name="vibin", email="vibin@example.com", phone="1234567890")
            session.add(candidate)
            await session.flush()

        # 3. Ensure an application exists
        stmt = select(CandidateApplication).where(CandidateApplication.candidate_id == candidate.id).limit(1)
        res = await session.execute(stmt)
        app = res.scalar_one_or_none()

        if not app:
            # We need a job to create an application
            from app.models.enterprise.job import JobRequirement

            stmt = select(JobRequirement).limit(1)
            res = await session.execute(stmt)
            job = res.scalar_one_or_none()
            if not job:
                print("No job requirements found in DB. Cannot seed.")
                return

            # Find status
            st_stmt = select(ApplicationStatus).where(ApplicationStatus.name == "Applied")
            st_res = await session.execute(st_stmt)
            status = st_res.scalar_one_or_none()
            if not status:
                status = ApplicationStatus(name="Applied", is_system=True)
                session.add(status)
                await session.flush()

            app = CandidateApplication(
                candidate_id=candidate.id, job_requirement_id=job.id, status_id=status.id
            )
            session.add(app)
            await session.flush()

        # 4. Remove any existing onboarding for this app to allow re-initiation
        await session.execute(delete(Onboarding).where(Onboarding.application_id == app.id))
        await session.commit()

        # 5. Trigger the email
        app_id = app.id
        print(f"Triggering celebratory onboarding email for app {app_id}...")

    # Re-triggering outside the first session to avoid state issues
    try:
        async with db_manager.session() as fresh_session:
            print(f"Calling initiate_onboarding_process with app_id={app_id}")
            onb = await initiate_onboarding_process(fresh_session, app_id)
            print(f"Returned from initiate: {onb}")
            if onb:
                print(f"Created onboarding ID: {onb.id}")
            await fresh_session.commit()
            print("Committed successfully.")
    except Exception as e:
        print(f"Exception during seeding: {e}")

    print("Test email triggered successfully! (Check terminal logs for SMTP output)")


if __name__ == "__main__":
    import sys
    import traceback

    with open("seed_log.txt", "w") as f:
        sys.stdout = f
        try:
            asyncio.run(seed_test_email())
        except Exception:
            traceback.print_exc(file=f)
