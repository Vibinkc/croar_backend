import asyncio
import os
import sys

from sqlalchemy import select

# Ensure the app code is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.job import JobStatus


async def seed_job_statuses():
    print("=== SEEDING JOB STATUSES ===")

    statuses = [
        {"id": 1, "name": "Draft", "description": "Job posting is in draft mode.", "is_system": True},
        {
            "id": 2,
            "name": "Active",
            "description": "Job is open and accepting applications.",
            "is_system": True,
        },
        {
            "id": 3,
            "name": "On Hold",
            "description": "Hiring for this job is temporarily paused.",
            "is_system": True,
        },
        {
            "id": 4,
            "name": "Closed",
            "description": "Job is no longer accepting applications.",
            "is_system": True,
        },
    ]

    async with db_manager.session() as session:
        for status_data in statuses:
            stmt = select(JobStatus).where(JobStatus.name == status_data["name"])
            result = await session.execute(stmt)
            existing_status = result.scalar_one_or_none()

            if not existing_status:
                # We use identity column, so we just add them in order.
                # If we need exact IDs, we might need a more complex insert,
                # but these are the first ones.
                status = JobStatus(
                    # id=status_data["id"], # Let autoincrement handle it to avoid conflicts
                    name=status_data["name"],
                    description=status_data["description"],
                    is_system=status_data["is_system"],
                )
                session.add(status)
                print(f"Adding Status: {status_data['name']}")
            else:
                print(f"Status '{status_data['name']}' already exists.")

        await session.commit()

    print("\n=== SEEDING COMPLETE ===")
    await db_manager.close_all()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_job_statuses())
