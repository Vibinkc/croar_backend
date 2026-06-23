import asyncio
import os
import sys
from uuid import uuid4

from sqlalchemy import select

# Ensure the app code is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.core.security import get_password_hash
from app.models.enterprise.user_role import EnterpriseUser as User
from app.models.shared.auth import Role


async def seed_enterprise():
    print("=== SEEDING ENTERPRISE DATA ===")

    async with db_manager.session() as session:
        # 1. Create Role
        role_name = "RECRUITER"
        stmt = select(Role).where(Role.name == role_name)
        result = await session.execute(stmt)
        role = result.scalars().first()

        if not role:
            role = Role(id=uuid4(), name=role_name, description="Hiring Manager/Recruiter", is_system=True)
            session.add(role)
            await session.flush()
            print(f"Created Role: {role.name}")
        else:
            print(f"Role already exists: {role.name}")

        # 2. Get Company
        from app.models.enterprise.company import Company

        stmt = select(Company).limit(1)
        result = await session.execute(stmt)
        company = result.scalar_one_or_none()
        if not company:
            company = Company(id=uuid4(), name="AppXcess", slug="appxcess", industry="Technology")
            session.add(company)
            await session.flush()
            print(f"Created Company: {company.name}")
        else:
            print(f"Using Company: {company.name}")

        # 3. Create User
        email = "recruiter@test.com"
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        password_hash = get_password_hash("Password123")

        if not user:
            user = User(
                id=uuid4(),
                email=email,
                password_hash=password_hash,
                first_name="Test",
                last_name="Recruiter",
                role_id=role.id,
                company_id=company.id,
                is_active=True,
            )
            session.add(user)
            print(f"Created User: {email}")
        else:
            user.password_hash = password_hash
            user.role_id = role.id
            user.company_id = company.id
            print(f"Updated User: {email}")

        await session.commit()
        print("\n=== SEEDING COMPLETE ===")
        print("Login details:")
        print(f"Email: {email}")
        print("Password: Password123")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_enterprise())
