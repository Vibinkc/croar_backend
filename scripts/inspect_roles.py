import asyncio
import os
import sys

from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.shared.auth import Role


async def inspect_roles():
    async with db_manager.session() as session:
        stmt = select(Role).options(selectinload(Role.permissions))
        result = await session.execute(stmt)
        roles = result.scalars().all()

        print(f"{'Name':<20} | {'Tenant ID':<40} | {'Is System':<10} | {'Perm Count':<10}")
        print("-" * 90)
        for role in roles:
            print(
                f"{role.name:<20} | {role.tenant_id!s:<40} | {role.is_system!s:<10} | {len(role.permissions):<10}"
            )


if __name__ == "__main__":
    asyncio.run(inspect_roles())
