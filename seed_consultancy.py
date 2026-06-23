import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import db_manager
from app.core.security import get_password_hash
from app.models.enterprise.company import Company
from app.models.enterprise.user_role import EnterpriseUser
from app.models.shared.auth import Permission, Role
from app.models.shared.constants import ModuleScope


async def seed_consultancy():
    async with db_manager.session() as session:
        # 1. Consultancy Company
        c_slug = "global-recruitment-solutions"
        c_stmt = select(Company).where(Company.slug == c_slug)
        consultancy = (await session.execute(c_stmt)).scalar_one_or_none()

        if not consultancy:
            consultancy = Company(
                name="Global Recruitment Solutions",
                slug=c_slug,
                is_consultancy=True,
                industry="Human Resources",
                location="London, UK",
            )
            session.add(consultancy)
            await session.flush()
        else:
            consultancy.is_consultancy = True

        # 2. Partner Company
        p_slug = "techflow-systems"
        p_stmt = select(Company).where(Company.slug == p_slug)
        partner = (await session.execute(p_stmt)).scalar_one_or_none()

        if not partner:
            partner = Company(
                name="TechFlow Systems",
                slug=p_slug,
                parent_id=consultancy.id,
                industry="Software Engineering",
                location="San Francisco, CA",
            )
            session.add(partner)
            await session.flush()

        # 3. Permissions
        perm_stmt = select(Permission).where(Permission.module != ModuleScope.platform)
        all_perms = (await session.execute(perm_stmt)).scalars().all()

        # 4. Role
        r_stmt = (
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.name == "ADMIN", Role.tenant_id == consultancy.id)
        )
        admin_role = (await session.execute(r_stmt)).scalar_one_or_none()

        if not admin_role:
            admin_role = Role(
                name="ADMIN",
                description="Consultancy Administrator",
                tenant_id=consultancy.id,
                is_system=True,
                role_rank=1,
            )
            # Add permissions to role BEFORE adding role to session to avoid some flush issues
            admin_role.permissions = list(all_perms)
            session.add(admin_role)
            await session.flush()

        # 5. User
        email = "consultant@example.com"
        u_stmt = (
            select(EnterpriseUser)
            .options(selectinload(EnterpriseUser.roles))
            .where(EnterpriseUser.email == email)
        )
        user = (await session.execute(u_stmt)).scalar_one_or_none()

        if not user:
            user = EnterpriseUser(
                email=email,
                password_hash=get_password_hash("Consultant@123"),
                first_name="Corey",
                last_name="Consultant",
                company_id=consultancy.id,
                is_active=True,
            )
            user.roles = [admin_role]
            session.add(user)

        await session.commit()
        print("Seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_consultancy())
