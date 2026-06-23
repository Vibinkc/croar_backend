import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.communication import EmailTemplate


async def check_templates():
    async with db_manager.session() as session:
        stmt = select(EmailTemplate)
        result = await session.execute(stmt)
        templates = result.scalars().all()
        for t in templates:
            print(f"--- Template: {t.name} ---")
            print(f"Subject: {t.subject}")
            print(f"Body snippet: {t.body[:200]}...")
            if "localhost:3000" in t.body:
                print("!!! WARNING: Hardcoded localhost:3000 found in body !!!")
            print("------------------------------")


if __name__ == "__main__":
    asyncio.run(check_templates())
