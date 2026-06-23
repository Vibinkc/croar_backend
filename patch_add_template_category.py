import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def patch_database() -> None:
    print("Patching database to add 'category' to 'email_templates' table...")
    async with db_manager.session() as session:
        try:
            # Check if column exists
            check_sql = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='email_templates' AND column_name='category';
            """)
            result = await session.execute(check_sql)
            exists = result.scalar()

            if not exists:
                print("Adding 'category' column...")
                await session.execute(
                    text("ALTER TABLE email_templates ADD COLUMN category VARCHAR(50) DEFAULT 'GENERAL';")
                )
                await session.commit()
                print("Column 'category' added successfully.")
            else:
                print("Column 'category' already exists.")

        except Exception as e:
            print(f"Error patching database: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(patch_database())
