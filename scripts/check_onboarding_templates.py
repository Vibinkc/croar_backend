import asyncio
import os
import sys

from sqlalchemy import select

# Ensure the app code is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.onboarding import OnboardingTemplate


async def check_templates():
    async with db_manager.session() as session:
        stmt = select(OnboardingTemplate)
        res = await session.execute(stmt)
        templates = res.scalars().all()
        for t in templates:
            print(f"Name: {t.name}")
            print(f"Sections: {t.sections}")
            print(f"Section Type: {type(t.sections)}")
            print(f"Section Length: {len(t.sections)}")
            print("-" * 20)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_templates())
