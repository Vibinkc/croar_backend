"""Seed payroll RBAC permissions and grant them to existing ADMIN roles.

Run once after applying the payroll migration:

    python seed_payroll_permissions.py

Idempotent:
  * Creates the 12 ``payroll`` module permissions (one per PermissionAction),
    global (tenant_id NULL) + is_system, mirroring every other Croar module.
  * Grants all payroll permissions to every existing role named ADMIN so current
    admins can use payroll immediately. New signups already receive them (signup
    assigns all non-platform permissions).
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

import app.models.enterprise  # noqa: F401  (register all mappers)
import app.models.payroll  # noqa: F401
import app.models.shared  # noqa: F401
from app.core.database import db_manager
from app.models.shared.auth import Permission, Role
from app.models.shared.constants import ModuleScope, PermissionAction, PermissionScope


async def main() -> None:
    async with db_manager.session() as session:
        # 1. Ensure a payroll permission exists for every action.
        existing = (
            (await session.execute(select(Permission).where(Permission.module == ModuleScope.payroll)))
            .scalars()
            .all()
        )
        by_action = {p.action: p for p in existing}

        created = 0
        for action in PermissionAction:
            if action in by_action:
                continue
            perm = Permission(
                resource="payroll",
                action=action,
                module=ModuleScope.payroll,
                scope=PermissionScope.tenant,
                tenant_id=None,
                is_system=True,
            )
            session.add(perm)
            by_action[action] = perm
            created += 1
        await session.flush()
        payroll_perms = list(by_action.values())
        print(f"payroll permissions: {len(payroll_perms)} total ({created} created)")

        # 2. Grant them to every existing ADMIN role.
        admin_roles = (
            (
                await session.execute(
                    select(Role).options(selectinload(Role.permissions)).where(Role.name == "ADMIN")
                )
            )
            .scalars()
            .all()
        )

        granted = 0
        for role in admin_roles:
            have = {p.id for p in role.permissions}
            for perm in payroll_perms:
                if perm.id not in have:
                    role.permissions.append(perm)
                    granted += 1
        await session.commit()
        print(f"granted payroll perms to {len(admin_roles)} ADMIN role(s); {granted} new grants")


if __name__ == "__main__":
    asyncio.run(main())
