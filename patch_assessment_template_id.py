import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Hardcoded DB URL for the patch
DATABASE_URL = "postgresql+asyncpg://postgres:vibin2003@localhost:5432/HR"


async def patch_db() -> None:
    engine = create_async_engine(DATABASE_URL)
    print("Patching database: Adding template_id to assessment_automations...")
    async with engine.begin() as conn:
        try:
            # Check if column exists first
            res = await conn.execute(
                text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name='assessment_automations' AND column_name='template_id';
            """)
            )
            if not res.fetchone():
                print("Adding column template_id...")
                await conn.execute(
                    text("""
                    ALTER TABLE assessment_automations
                    ADD COLUMN template_id UUID REFERENCES assessment_templates(id) ON DELETE SET NULL;
                """)
                )
                print("Column added successfully.")
            else:
                print("Column template_id already exists.")
        except Exception as e:
            print(f"Error patching database: {e}")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(patch_db())
