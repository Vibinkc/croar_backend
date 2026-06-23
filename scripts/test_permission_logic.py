import asyncio
import os
import sys

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import db_manager
from app.core.dependencies import PermissionChecker
from app.models.enterprise.user_role import EnterpriseUser
from app.models.shared.auth import Role
from app.models.shared.constants import ModuleScope, PermissionAction


async def test_checker():
    email = "restricted@croar.co"
    print(f"=== TESTING PERMISSION CHECKER FOR {email} ===")

    async with db_manager.session() as session:
        stmt = (
            select(EnterpriseUser)
            .options(selectinload(EnterpriseUser.roles).selectinload(Role.permissions))
            .where(EnterpriseUser.email == email)
        )
        user = (await session.execute(stmt)).scalar_one_or_none()

        if not user:
            print("User not found!")
            return

        def check(module, action):
            checker = PermissionChecker(module, action)
            try:
                checker(user)
                print(f"✅ ALLOWED: {module}:{action}")
            except Exception as e:
                print(f"❌ DENIED: {module}:{action} ({e!s})")

        # Test various permissions
        check(ModuleScope.organization, PermissionAction.read)
        check(ModuleScope.jobs, PermissionAction.create)
        check(ModuleScope.candidates, PermissionAction.read)
        check(ModuleScope.communications, PermissionAction.read)
        check(ModuleScope.assessments, PermissionAction.read)


if __name__ == "__main__":
    asyncio.run(test_checker())
