import asyncio
import os
import sys

from sqlalchemy import select

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.user_role import EnterpriseUser
from app.models.shared.auth import Role, user_roles


async def check_user_role():
    email = "restricted@croar.co"
    print(f"=== CHECKING ROLES FOR {email} ===")

    async with db_manager.session() as session:
        stmt = select(EnterpriseUser).where(EnterpriseUser.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            print("User not found!")
            return

        print(f"User ID: {user.id}")
        print(f"Company ID: {user.company_id}")

        # Check raw role assignments
        stmt = select(Role).join(user_roles).where(user_roles.c.user_id == user.id)
        result = await session.execute(stmt)
        roles = result.scalars().all()

        if not roles:
            print("No roles assigned to this user!")
        for role in roles:
            print(f"- Role: {role.name} (ID: {role.id}, Tenant: {role.tenant_id})")


if __name__ == "__main__":
    asyncio.run(check_user_role())
