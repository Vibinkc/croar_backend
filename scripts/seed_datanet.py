import asyncio
import os
import sys
import uuid

from sqlalchemy import insert, select

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.core.security import get_password_hash
from app.models.enterprise.company import Company
from app.models.enterprise.user_role import EnterpriseUser as User
from app.models.shared.auth import Permission, Role, role_permissions, user_roles


async def seed_datanet():
    print("=== SEEDING DATANET ORGANIZATION ===")

    async with db_manager.session() as session:
        # 1. Create Company
        org_name = "Datanet"
        org_slug = "datanet"
        stmt = select(Company).where(Company.slug == org_slug)
        result = await session.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            company = Company(
                id=uuid.uuid4(),
                name=org_name,
                slug=org_slug,
                industry="Information Technology",
                location="Global",
            )
            session.add(company)
            await session.flush()
            print(f"Created Company: {company.name}")
        else:
            print(f"Company already exists: {company.name}")

        # 2. Create Admin Role for Datanet
        role_name = "ADMIN"
        stmt = select(Role).where(Role.name == role_name, Role.tenant_id == company.id)
        result = await session.execute(stmt)
        admin_role = result.scalar_one_or_none()

        if not admin_role:
            admin_role = Role(
                id=uuid.uuid4(),
                name=role_name,
                description="Full access administrator for Datanet",
                tenant_id=company.id,
                is_system=True,
                role_rank=0,
            )
            session.add(admin_role)
            await session.flush()
            print(f"Created ADMIN role for {company.name}")
        else:
            print(f"ADMIN role already exists for {company.name}")

        # 3. Assign all system permissions to the Datanet ADMIN role
        # Fetch all system permission IDs
        stmt = select(Permission.id).where(Permission.tenant_id is None)
        result = await session.execute(stmt)
        all_perm_ids = result.scalars().all()

        # Fetch existing assigned permission IDs for this role
        stmt = select(role_permissions.c.permission_id).where(role_permissions.c.role_id == admin_role.id)
        result = await session.execute(stmt)
        existing_perm_ids = set(result.scalars().all())

        new_perm_ids = [pid for pid in all_perm_ids if pid not in existing_perm_ids]

        if new_perm_ids:
            print(f"Assigning {len(new_perm_ids)} permissions to {company.name} AUTO_ADMIN role...")
            for pid in new_perm_ids:
                await session.execute(
                    insert(role_permissions).values(role_id=admin_role.id, permission_id=pid)
                )
            print("Permissions assigned.")
        else:
            print("All permissions already assigned.")

        # 4. Create Admin User
        admin_email = "admin@datanet.co"
        password = "Admin@123"
        stmt = select(User).where(User.email == admin_email)
        result = await session.execute(stmt)
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            admin_user = User(
                id=uuid.uuid4(),
                email=admin_email,
                password_hash=get_password_hash(password),
                first_name="Datanet",
                last_name="Admin",
                company_id=company.id,
                is_active=True,
            )
            session.add(admin_user)
            await session.flush()
            print(f"Created Admin User: {admin_email}")
        else:
            admin_user.company_id = company.id
            print(f"User {admin_email} already exists, updated company_id.")

        # 5. Link User to the Role
        stmt = select(user_roles.c.user_id).where(
            user_roles.c.user_id == admin_user.id, user_roles.c.role_id == admin_role.id
        )
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            await session.execute(insert(user_roles).values(user_id=admin_user.id, role_id=admin_role.id))
            print("Linked user to ADMIN role.")
        else:
            print("User already linked to ADMIN role.")

        await session.commit()
        print("\n=== SEEDING COMPLETE ===")
        print(f"Org Name: {org_name}")
        print(f"Admin Email: {admin_email}")
        print(f"Admin Password: {password}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_datanet())
