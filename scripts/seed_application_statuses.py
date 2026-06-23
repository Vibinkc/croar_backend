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
from app.models.enterprise.candidate import ApplicationStatus


async def seed_application_statuses():
    print("=== SEEDING APPLICATION STATUSES ===")

    statuses = [
        {"id": 1, "name": "Applied", "description": "Candidate has applied for the job.", "is_system": True},
        {"id": 2, "name": "Screening", "description": "Candidate is being screened.", "is_system": True},
        {
            "id": 3,
            "name": "Interviewing",
            "description": "Candidate is in the interview process.",
            "is_system": True,
        },
        {
            "id": 4,
            "name": "Offered",
            "description": "Candidate has been offered the position.",
            "is_system": True,
        },
        {"id": 5, "name": "Hired", "description": "Candidate has been hired.", "is_system": True},
        {
            "id": 6,
            "name": "Rejected",
            "description": "Candidate application was rejected.",
            "is_system": True,
        },
        {
            "id": 7,
            "name": "Withdrawn",
            "description": "Candidate withdrew their application.",
            "is_system": True,
        },
    ]

    async with db_manager.session() as session:
        for status_data in statuses:
            stmt = select(ApplicationStatus).where(ApplicationStatus.name == status_data["name"])
            result = await session.execute(stmt)
            existing_status = result.scalar_one_or_none()

            if not existing_status:
                status = ApplicationStatus(
                    # id=status_data["id"], # Let autoincrement handle it
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
    asyncio.run(seed_application_statuses())
