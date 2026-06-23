import asyncio
import os
import sys

from sqlalchemy import select, update

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.assessment import AssessmentAutomation, AssessmentTemplate
from app.models.enterprise.candidate import Candidate, CandidateApplication
from app.models.enterprise.communication import EmailTemplate
from app.models.enterprise.company import Company
from app.models.enterprise.onboarding import Onboarding, OnboardingTemplate
from app.models.enterprise.x360 import X360AssessmentCycle


async def backfill():
    print("=== BACKFILLING MULTI-TENANCY DATA ===")

    async with db_manager.session() as session:
        # 1. Get AppXcess ID
        stmt = select(Company.id).where(Company.slug == "appxcess")
        result = await session.execute(stmt)
        appx_id = result.scalar()

        if not appx_id:
            print("Error: AppXcess not found. Using the first company found.")
            stmt = select(Company.id).limit(1)
            result = await session.execute(stmt)
            appx_id = result.scalar()

        if not appx_id:
            print("Critical Error: No companies found in DB.")
            return

        print(f"Targeting Company ID: {appx_id} (AppXcess)")

        models = [
            Onboarding,
            OnboardingTemplate,
            Candidate,
            CandidateApplication,
            AssessmentTemplate,
            AssessmentAutomation,
            EmailTemplate,
            X360AssessmentCycle,
        ]

        for model in models:
            try:
                print(f"Backfilling {model.__tablename__}...")
                stmt = update(model).where(model.company_id is None).values(company_id=appx_id)
                res = await session.execute(stmt)
                print(f"Updated {res.rowcount} rows.")
            except Exception as e:
                print(f"Error updating {model.__tablename__}: {e}")

        await session.commit()

    print("\n=== BACKFILL COMPLETE ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(backfill())
