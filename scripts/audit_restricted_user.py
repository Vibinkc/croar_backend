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
from app.models.shared.auth import Permission, Role, role_permissions, user_roles


async def check_full_permissions():
    email = "restricted@croar.co"
    print(f"=== FULL PERMISSION AUDIT FOR {email} ===")

    async with db_manager.session() as session:
        stmt = select(EnterpriseUser).where(EnterpriseUser.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            print("User not found!")
            return

        print(f"User ID: {user.id}")

        # Check all roles
        stmt = select(Role).join(user_roles).where(user_roles.c.user_id == user.id)
        result = await session.execute(stmt)
        roles = result.scalars().all()

        for role in roles:
            print(f"\nRole: {role.name} (Tenant: {role.tenant_id})")

            # Check permissions for this role
            perm_stmt = select(Permission).join(role_permissions).where(role_permissions.c.role_id == role.id)
            perm_result = await session.execute(perm_stmt)
            perms = perm_result.scalars().all()

            if not perms:
                print("  No permissions assigned.")
            for perm in perms:
                print(f"  - {perm.module.value}:{perm.action.value} (Resource: {perm.resource})")


if __name__ == "__main__":
    asyncio.run(check_full_permissions())
