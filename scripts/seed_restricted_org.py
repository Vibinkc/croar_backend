import asyncio
import os
import sys

from sqlalchemy import insert, select

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.core.security import get_password_hash
from app.models.enterprise.company import Company
from app.models.enterprise.user_role import EnterpriseUser
from app.models.shared.auth import Role, user_roles


async def seed_restricted_org():
    print("=== SEEDING RESTRICTED ORGANIZATION (ZERO PERMISSIONS) ===")

    async with db_manager.session() as session:
        # 1. Create Restricted Company
        org_name = "Restricted Org"
        org_slug = "restricted-org"

        stmt = select(Company).where(Company.slug == org_slug)
        result = await session.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            company = Company(name=org_name, slug=org_slug)
            session.add(company)
            await session.flush()
            print(f"Created Company: {org_name}")
        else:
            print(f"Company {org_name} already exists.")

        # 2. Create Role with NO permissions
        role_name = "RESTRICTED_ACCESS"
        stmt = select(Role).where(Role.name == role_name, Role.tenant_id == company.id)
        result = await session.execute(stmt)
        restricted_role = result.scalar_one_or_none()

        if not restricted_role:
            restricted_role = Role(
                name=role_name,
                description="A role with absolutely no functional permissions for security testing.",
                tenant_id=company.id,
                is_system=False,
                role_rank=99,
            )
            session.add(restricted_role)
            await session.flush()
            print(f"Created Zero-Permission Role: {role_name}")
        else:
            print(f"Role {role_name} already exists.")

        # 3. Create Restricted User
        user_email = "restricted@croar.co"
        stmt = select(EnterpriseUser).where(EnterpriseUser.email == user_email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            user = EnterpriseUser(
                email=user_email,
                password_hash=get_password_hash("Restricted@123"),
                first_name="Restricted",
                last_name="User",
                company_id=company.id,
                is_active=True,
            )
            session.add(user)
            await session.flush()

            # Link to the restricted role via direct insert
            await session.execute(insert(user_roles).values(user_id=user.id, role_id=restricted_role.id))
            print(f"Created Restricted User: {user_email}")
        else:
            print(f"User {user_email} already exists.")
            # Check if link exists
            link_stmt = select(user_roles).where(
                user_roles.c.user_id == user.id, user_roles.c.role_id == restricted_role.id
            )
            if not (await session.execute(link_stmt)).first():
                await session.execute(insert(user_roles).values(user_id=user.id, role_id=restricted_role.id))
                print("Linked restricted role to existing user.")

        await session.commit()
        print("\n=== SEEDING COMPLETE ===")
        print(f"Login: {user_email} / Restricted@123")
        print(f"Tenant Slug: {org_slug}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_restricted_org())
