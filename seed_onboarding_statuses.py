import asyncio

from app.core.database import db_manager
from app.models.enterprise.onboarding import OnboardingStatus


async def seed_statuses():
    statuses = [
        {"name": "In Progress", "description": "Onboarding has been initiated and is currently in progress."},
        {
            "name": "Awaiting Confirmation",
            "description": "Candidate has submitted all details and is awaiting HR review.",
        },
        {"name": "Completed", "description": "Candidate has successfully completed the onboarding process."},
        {"name": "Discontinued", "description": "Onboarding process has been stopped for this candidate."},
        {"name": "Washed Away", "description": "Candidate is not proceeding with onboarding."},
        {"name": "Pending Approvals", "description": "Onboarding is waiting for higher-level approvals."},
    ]

    async with db_manager.session() as session:
        for status_data in statuses:
            from sqlalchemy import select

            stmt = select(OnboardingStatus).where(OnboardingStatus.name == status_data["name"])
            existing = await session.execute(stmt)
            if not existing.scalar_one_or_none():
                status = OnboardingStatus(**status_data)
                session.add(status)
        await session.commit()
    print("Onboarding statuses seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_statuses())
