import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.communication import EmailTemplate


async def verify():
    async with db_manager.session() as session:
        stmt = select(EmailTemplate).limit(1)
        res = await session.execute(stmt)
        template = res.scalar_one_or_none()
        if template:
            print(f"Template Name: {template.name}")
            print(f"Subject: {template.subject}")
            print("\nBody Preview (First 500 chars):")
            print(template.body[:500] + "...")
        else:
            print("No templates found.")


if __name__ == "__main__":
    asyncio.run(verify())
