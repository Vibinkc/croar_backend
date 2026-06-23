import asyncio

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()


async def check_jobs():
    database_url = "postgresql+asyncpg://postgres:vibin2003@localhost:5432/HR"
    engine = create_async_engine(database_url)

    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, title, company_id, deleted_at FROM job_requirements"))
        jobs = result.all()

        print("\n--- JOB REQUIREMENTS IN DB ---")
        if not jobs:
            print("No jobs found in database.")
        for job in jobs:
            print(
                f"ID: {job.id} | Title: {job.title} | Company ID: {job.company_id} | Deleted: {job.deleted_at}"
            )

        result_comp = await conn.execute(text("SELECT id, name FROM companies"))
        companies = result_comp.all()
        print("\n--- COMPANIES IN DB ---")
        for comp in companies:
            print(f"ID: {comp.id} | Name: {comp.name}")

        result_user = await conn.execute(
            text("SELECT id, email, company_id FROM users WHERE email = 'test@demo.com'")
        )
        user = result_user.first()
        print("\n--- TEST@DEMO.COM USER RECORD ---")
        if user:
            print(f"ID: {user.id} | Email: {user.email} | Company ID: {user.company_id}")
        else:
            print("User record for test@demo.com not found in users table.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_jobs())
