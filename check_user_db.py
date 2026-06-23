import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.company import Company
from app.models.enterprise.user_role import EnterpriseUser


async def check_user_company():
    async with db_manager.session() as session:
        # Check users
        user_stmt = select(EnterpriseUser)
        user_res = await session.execute(user_stmt)
        users = user_res.scalars().all()

        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"User: {u.email}, Company ID: {u.company_id}")

        # Check companies
        comp_stmt = select(Company)
        comp_res = await session.execute(comp_stmt)
        companies = comp_res.scalars().all()
        print(f"\nTotal Companies: {len(companies)}")
        for c in companies:
            print(f"Company: {c.name}, ID: {c.id}")


if __name__ == "__main__":
    asyncio.run(check_user_company())
