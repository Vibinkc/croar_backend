import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def check():
    async with db_manager.get_session() as session:
        # Check columns in onboardings table
        result = await session.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'onboardings'")
        )
        columns = [row[0] for row in result.fetchall()]
        print(f"Columns in onboardings: {columns}")

        if "form_data" in columns and "template_id" in columns:
            print("SUCCESS: Columns 'form_data' and 'template_id' exist.")
        else:
            print("FAILURE: Missing columns.")


if __name__ == "__main__":
    asyncio.run(check())
