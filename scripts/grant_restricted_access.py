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
from app.models.enterprise.company import Company
from app.models.shared.auth import Permission, Role, role_permissions
from app.models.shared.constants import ModuleScope, PermissionAction


async def grant_restricted_access():
    print("=== GRANTING SINGLE ACCESS (organization:read) ===")

    async with db_manager.session() as session:
        # 1. Get the Restricted Company
        org_slug = "restricted-org"
        stmt = select(Company).where(Company.slug == org_slug)
        company = (await session.execute(stmt)).scalar_one_or_none()

        if not company:
            print("Error: Restricted Org not found. Run seed_restricted_org.py first.")
            return

        # 2. Get the Restricted Role
        role_name = "RESTRICTED_ACCESS"
        stmt = select(Role).where(Role.name == role_name, Role.tenant_id == company.id)
        role = (await session.execute(stmt)).scalar_one_or_none()

        if not role:
            print(f"Error: Role {role_name} not found.")
            return

        # 3. Find the 'organization:read' permission
        perm_stmt = select(Permission).where(
            Permission.module == ModuleScope.organization,
            Permission.action == PermissionAction.read,
            Permission.tenant_id.is_(None),  # System-wide template
        )
        permission = (await session.execute(perm_stmt)).scalar_one_or_none()

        if not permission:
            print("Error: System permission 'assessments:read' not found.")
            return

        # 4. Link Permission to Role
        link_stmt = select(role_permissions).where(
            role_permissions.c.role_id == role.id, role_permissions.c.permission_id == permission.id
        )
        if not (await session.execute(link_stmt)).first():
            await session.execute(
                insert(role_permissions).values(role_id=role.id, permission_id=permission.id)
            )
            await session.commit()
            print(
                f"Successfully granted '{permission.module.value}:{permission.action.value}' to {role.name}"
            )
        else:
            print("Access already granted.")

        print("\n=== GRANT COMPLETE ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(grant_restricted_access())
