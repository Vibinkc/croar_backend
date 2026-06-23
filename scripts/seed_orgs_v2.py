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


async def seed_organization(session, org_name, org_slug, industry, admins, recruiters):
    print(f"--- Seeding Organization: {org_name} ---")

    # 1. Ensure Company exists
    stmt = select(Company).where(Company.slug == org_slug)
    result = await session.execute(stmt)
    company = result.scalar_one_or_none()

    if not company:
        company = Company(id=uuid.uuid4(), name=org_name, slug=org_slug, industry=industry, location="Remote")
        session.add(company)
        await session.flush()
        print(f"Created Company: {company.name}")
    else:
        print(f"Company exists: {company.name}")

    # 2. Ensure Roles exist for this tenant
    # Admin Role
    stmt = select(Role).where(Role.name == "ADMIN", Role.tenant_id == company.id)
    admin_role = (await session.execute(stmt)).scalar_one_or_none()
    if not admin_role:
        admin_role = Role(
            id=uuid.uuid4(),
            name="ADMIN",
            description=f"Admin for {org_name}",
            tenant_id=company.id,
            is_system=False,
            role_rank=10,
        )
        session.add(admin_role)
        await session.flush()
        print(f"Created ADMIN role for {org_name}")

        # Assign all system permissions to this tenant admin
        stmt = select(Permission.id).where(Permission.tenant_id is None)
        all_perm_ids = (await session.execute(stmt)).scalars().all()
        for pid in all_perm_ids:
            await session.execute(insert(role_permissions).values(role_id=admin_role.id, permission_id=pid))

    # Recruiter Role
    stmt = select(Role).where(Role.name == "RECRUITER", Role.tenant_id == company.id)
    recruiter_role = (await session.execute(stmt)).scalar_one_or_none()
    if not recruiter_role:
        recruiter_role = Role(
            id=uuid.uuid4(),
            name="RECRUITER",
            description=f"Recruiter for {org_name}",
            tenant_id=company.id,
            is_system=False,
            role_rank=50,
        )
        session.add(recruiter_role)
        await session.flush()
        print(f"Created RECRUITER role for {org_name}")

        # Assign some basic permissions to recruiter (Jobs and Candidates read/moderate)
        from app.models.shared.constants import ModuleScope

        stmt = select(Permission.id).where(Permission.module.in_([ModuleScope.jobs, ModuleScope.candidates]))
        hiring_perm_ids = (await session.execute(stmt)).scalars().all()
        for pid in hiring_perm_ids:
            await session.execute(
                insert(role_permissions).values(role_id=recruiter_role.id, permission_id=pid)
            )

    # 3. Create Users
    password_hash = get_password_hash("Admin@123")

    # Admins
    for email, first, last in admins:
        stmt = select(User).where(User.email == email)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=password_hash,
                first_name=first,
                last_name=last,
                company_id=company.id,
                is_active=True,
            )
            session.add(user)
            await session.flush()
            # Link to ADMIN role
            await session.execute(insert(user_roles).values(user_id=user.id, role_id=admin_role.id))
            print(f"Created Admin User: {email}")
        else:
            user.company_id = company.id
            print(f"Admin User exists: {email}")

    # Recruiters
    for email, first, last in recruiters:
        stmt = select(User).where(User.email == email)
        user = (await session.execute(stmt)).scalar_one_or_none()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=password_hash,
                first_name=first,
                last_name=last,
                company_id=company.id,
                is_active=True,
            )
            session.add(user)
            await session.flush()
            # Link to RECRUITER role
            await session.execute(insert(user_roles).values(user_id=user.id, role_id=recruiter_role.id))
            print(f"Created Recruiter User: {email}")
        else:
            user.company_id = company.id
            print(f"Recruiter User exists: {email}")


async def run_seed():
    print("=== MULTI-ORG CONSOLIDATED SEEDING ===")
    async with db_manager.session() as session:
        # AppXcess Corp
        await seed_organization(
            session,
            "AppXcess",
            "appxcess",
            "Technology",
            admins=[("admin@appxcess.co", "AppXcess", "Admin")],
            recruiters=[("recruiter@appxcess.co", "AppXcess", "Recruiter")],
        )

        # Datanet
        await seed_organization(
            session,
            "Datanet",
            "datanet",
            "Information Technology",
            admins=[("admin@datanet.co", "Datanet", "Admin")],
            recruiters=[("staff@datanet.co", "Datanet", "Staff")],
        )

        await session.commit()
    print("=== SEEDING COMPLETED ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_seed())
