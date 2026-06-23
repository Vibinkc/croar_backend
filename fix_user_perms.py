import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import db_manager
from app.models.enterprise.user_role import EnterpriseUser
from app.models.shared.auth import Permission
from app.models.shared.constants import ModuleScope


async def fix_permissions(email):
    async with db_manager.session() as session:
        stmt = (
            select(EnterpriseUser)
            .options(selectinload(EnterpriseUser.roles))
            .where(EnterpriseUser.email == email)
        )
        user = (await session.execute(stmt)).scalar_one_or_none()

        if user and user.roles:
            role = user.roles[0]
            print(f"Fixing permissions for role: {role.name} (ID: {role.id})")

            # Re-fetch the role with permissions loaded
            from app.models.shared.auth import Role

            stmt_role = select(Role).options(selectinload(Role.permissions)).where(Role.id == role.id)
            role_obj = (await session.execute(stmt_role)).scalar_one()

            perm_stmt = select(Permission).where(Permission.module != ModuleScope.platform)
            perms = (await session.execute(perm_stmt)).scalars().all()

            role_obj.permissions = list(perms)
            await session.commit()
            print(f"✅ Successfully updated {len(perms)} permissions for {email}")
        else:
            print(f"❌ User or role not found for {email}")


if __name__ == "__main__":
    asyncio.run(fix_permissions("vibinvibi2003@gmail.com"))
