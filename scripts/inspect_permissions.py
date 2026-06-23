import asyncio
import os
import sys

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from sqlalchemy import select

from app.core.database import db_manager
from app.models.shared.auth import Permission


async def check_permissions():
    async with db_manager.session() as session:
        res = await session.execute(select(Permission))
        perms = res.scalars().all()
        print("=== SYSTEM PERMISSIONS ===")
        for p in perms:
            print(
                f"ID={p.id} | Mod={p.module} ({type(p.module)}) | Act={p.action} ({type(p.action)}) | Res={p.resource}"
            )


if __name__ == "__main__":
    asyncio.run(check_permissions())
