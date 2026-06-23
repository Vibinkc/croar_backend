import asyncio
import os

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.communication import EmailTemplate


async def fix_urls():
    # Detect the correct frontend URL from environment or use default
    frontend_url = os.getenv("FRONTEND_URL", "https://app.croar.co")

    print(f"Target Frontend URL: {frontend_url}")
    print("Scanning database for hardcoded 'localhost:3000'...")

    async with db_manager.session() as session:
        stmt = select(EmailTemplate)
        result = await session.execute(stmt)
        templates = result.scalars().all()

        fixed_count = 0
        for t in templates:
            if "localhost:3000" in t.body or "localhost:3000" in t.subject:
                print(f"Fixing template: {t.name}")
                t.body = t.body.replace("http://localhost:3000", frontend_url)
                t.body = t.body.replace("localhost:3000", frontend_url)
                if t.subject:
                    t.subject = t.subject.replace("http://localhost:3000", frontend_url)
                    t.subject = t.subject.replace("localhost:3000", frontend_url)
                fixed_count += 1

        if fixed_count > 0:
            await session.commit()
            print(f"Successfully fixed {fixed_count} templates.")
        else:
            print("No hardcoded localhost URLs found in templates.")


if __name__ == "__main__":
    asyncio.run(fix_urls())
