import asyncio
import os
import sys
import uuid

from sqlalchemy import select

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.candidate import Candidate
from app.models.enterprise.job import JobRequirement
from app.models.enterprise.user_role import EnterpriseUser


async def verify_isolation():
    print("=== VERIFYING MULTI-TENANCY ISOLATION ===")

    async with db_manager.session() as session:
        # 1. Fetch Companies
        appxcess_id = uuid.UUID("900125e1-1ab6-47e5-a410-2515ab2e89c0")
        datanet_id = uuid.UUID("da7a9eb5-5a5f-4d69-8e2b-f8f8b8b8b8b8")

        # 2. Check AppXcess Data
        appxcess_jobs = await session.execute(
            select(JobRequirement).where(JobRequirement.company_id == appxcess_id)
        )
        appxcess_jobs = appxcess_jobs.scalars().all()
        print(f"AppXcess Jobs: {len(appxcess_jobs)}")
        for job in appxcess_jobs:
            print(f" - {job.title}")

        appxcess_candidates = await session.execute(
            select(Candidate).where(Candidate.company_id == appxcess_id)
        )
        appxcess_candidates = appxcess_candidates.scalars().all()
        print(f"AppXcess Candidates: {len(appxcess_candidates)}")

        # 3. Check Datanet Data
        datanet_jobs = await session.execute(
            select(JobRequirement).where(JobRequirement.company_id == datanet_id)
        )
        datanet_jobs = datanet_jobs.scalars().all()
        print(f"Datanet Jobs: {len(datanet_jobs)}")
        for job in datanet_jobs:
            print(f" - {job.title}")

        datanet_candidates = await session.execute(
            select(Candidate).where(Candidate.company_id == datanet_id)
        )
        datanet_candidates = datanet_candidates.scalars().all()
        print(f"Datanet Candidates: {len(datanet_candidates)}")

        # 4. Cross-Verification
        print("\nCross-Verification:")
        # Check if any Datanet job has AppXcess company_id (impossible via query but good to check total counts)
        all_jobs = await session.execute(select(JobRequirement))
        all_jobs = all_jobs.scalars().all()

        app_jobs_in_all = [j for j in all_jobs if str(j.company_id) == str(appxcess_id)]
        data_jobs_in_all = [j for j in all_jobs if str(j.company_id) == str(datanet_id)]

        print(f"Total Jobs in DB: {len(all_jobs)}")
        print(f"Jobs belonging to AppXcess: {len(app_jobs_in_all)}")
        print(f"Jobs belonging to Datanet: {len(data_jobs_in_all)}")

        if len(all_jobs) == len(app_jobs_in_all) + len(data_jobs_in_all):
            print("SUCCESS: Every job belongs to either AppXcess or Datanet.")
        else:
            print("WARNING: Some jobs do not belong to either tenant!")

        # 5. Admin Verification
        admins = await session.execute(select(EnterpriseUser))
        admins = admins.scalars().all()
        print(f"\nTotal Users: {len(admins)}")
        for admin in admins:
            print(f" - {admin.email} (Company ID: {admin.company_id})")

    print("\n=== VERIFICATION COMPLETE ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(verify_isolation())
