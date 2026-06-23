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
from app.models.enterprise.company import Company
from app.models.enterprise.user_role import EnterpriseUser


async def fix_user_company():
    print("=== FIXING USER COMPANY ASSOCIATION ===")

    async with db_manager.session() as session:
        # 1. Get the first company
        stmt = select(Company).limit(1)
        result = await session.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            print("Error: No company found. Please run seed_employee.py first.")
            return

        print(f"Linking to Company: {company.name} ({company.id})")

        # 2. Get all users and update them
        stmt = select(EnterpriseUser)
        result = await session.execute(stmt)
        users = result.scalars().all()

        updated_count = 0
        for user in users:
            if not user.company_id:
                user.company_id = company.id
                updated_count += 1
                print(f"Updated User: {user.email}")

        await session.commit()
        print(f"\n=== UPDATED {updated_count} USERS ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_user_company())
