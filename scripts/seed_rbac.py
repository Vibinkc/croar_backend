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
from app.models.shared.auth import Permission, Role, role_permissions, super_admin_roles
from app.models.shared.constants import ModuleScope, PermissionAction, PermissionScope
from app.models.shared.super_admin import SuperAdmin


async def seed_rbac():
    print("=== SEEDING RBAC DATA ===")

    async with db_manager.session() as session:
        # 1. Create Permissions for each Module and Action
        actions = list(PermissionAction)
        modules = list(ModuleScope)

        print(f"Initializing {len(actions) * len(modules)} system permissions...")

        for module in modules:
            for action in actions:
                stmt = select(Permission).where(
                    Permission.module == module, Permission.action == action, Permission.tenant_id.is_(None)
                )
                result = await session.execute(stmt)
                perm = result.scalar_one_or_none()

                if not perm:
                    perm = Permission(
                        resource=module.value,
                        action=action,
                        module=module,
                        scope=PermissionScope.system
                        if module == ModuleScope.platform
                        else PermissionScope.tenant,
                        is_system=True,
                    )
                    session.add(perm)

        await session.commit()  # Commit permissions first
        print("Permissions initialized.")

        # Re-open session or just continue
        # 2. Create Super Admin Role
        stmt = select(Role).where(Role.name == "SUPER_ADMIN", Role.tenant_id.is_(None))
        result = await session.execute(stmt)
        super_admin_role = result.scalar_one_or_none()

        if not super_admin_role:
            super_admin_role = Role(
                name="SUPER_ADMIN",
                description="Platform-wide administrator with full access.",
                is_system=True,
                role_rank=0,
            )
            session.add(super_admin_role)
            await session.commit()
            print("SUPER_ADMIN role created.")

        # 3. Assign all system permissions to the Super Admin role via direct insert to avoid lazy load issues
        # Fetch all permission IDs
        stmt = select(Permission.id).where(Permission.tenant_id.is_(None))
        result = await session.execute(stmt)
        all_perm_ids = result.scalars().all()

        # Fetch existing assigned permission IDs for this role
        stmt = select(role_permissions.c.permission_id).where(
            role_permissions.c.role_id == super_admin_role.id
        )
        result = await session.execute(stmt)
        existing_perm_ids = set(result.scalars().all())

        new_perm_ids = [pid for pid in all_perm_ids if pid not in existing_perm_ids]

        if new_perm_ids:
            print(f"Assigning {len(new_perm_ids)} new permissions to SUPER_ADMIN role...")
            for pid in new_perm_ids:
                await session.execute(
                    insert(role_permissions).values(role_id=super_admin_role.id, permission_id=pid)
                )
            await session.commit()
            print("Permissions assigned.")

        # 4. Create Default Super Admin User
        admin_email = "admin@croar.co"
        stmt = select(SuperAdmin).where(
            (SuperAdmin.email == admin_email) | (SuperAdmin.username == "superadmin")
        )
        result = await session.execute(stmt)
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            admin_user = SuperAdmin(
                username="superadmin",
                email=admin_email,
                password_hash=get_password_hash("Admin@123"),
                first_name="Super",
                last_name="Admin",
                is_active=True,
            )
            session.add(admin_user)
            await session.commit()
            print(f"Default Super Admin created: {admin_email}")

        # 5. Link user to the Super Admin role via direct insert
        stmt = select(super_admin_roles.c.super_admin_id).where(
            super_admin_roles.c.super_admin_id == admin_user.id,
            super_admin_roles.c.role_id == super_admin_role.id,
        )
        result = await session.execute(stmt)
        if not result.scalar_one_or_none():
            await session.execute(
                insert(super_admin_roles).values(super_admin_id=admin_user.id, role_id=super_admin_role.id)
            )
            await session.commit()
            print("Linked Super Admin user to SUPER_ADMIN role.")

        print("\n=== RBAC SEEDING COMPLETE ===")
        print(f"Super Admin Login: {admin_email} / Admin@123")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_rbac())
