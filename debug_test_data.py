import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def get_test_ids():
    async with db_manager.session() as session:
        # Get User and Company
        res = await session.execute(text("SELECT id, company_id FROM users WHERE email = 'test@demo.com'"))
        user = res.first()
        if user:
            u_id, c_id = user
            print(f"USER_ID: {u_id}")
            print(f"COMPANY_ID: {c_id}")

            # Find an application for this company
            app_res = await session.execute(
                text(f"SELECT id FROM candidate_applications WHERE company_id = '{c_id}' LIMIT 1")
            )
            app = app_res.first()
            if app:
                print(f"APPLICATION_ID: {app[0]}")
            else:
                print("NO_APPLICATIONS_FOUND_FOR_COMPANY")
        else:
            print("USER_NOT_FOUND")


if __name__ == "__main__":
    asyncio.run(get_test_ids())
