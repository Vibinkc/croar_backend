import asyncio

from sqlalchemy import text

from app.core.database import db_manager


async def patch_schema() -> None:
    print("Connecting to database for schema repair...")
    async with db_manager.engine.begin() as conn:
        # Check if hiring_agent_id exists
        check_col = await conn.execute(
            text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='simulation_sessions' AND column_name='hiring_agent_id';
        """)
        )

        if not check_col.fetchone():
            print("Adding 'hiring_agent_id' to 'simulation_sessions'...")
            await conn.execute(
                text("""
                ALTER TABLE simulation_sessions
                ADD COLUMN hiring_agent_id UUID REFERENCES hiring_agents(id) ON DELETE CASCADE;
            """)
            )
            print("Column added successfully.")
        else:
            print("'hiring_agent_id' already exists.")

        # Also ensure assignment_id is present and has the correct SET NULL constraint
        # as it was a relatively recent addition
        check_assign = await conn.execute(
            text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='simulation_sessions' AND column_name='assignment_id';
        """)
        )

        if not check_assign.fetchone():
            print("Adding missing 'assignment_id' to 'simulation_sessions'...")
            await conn.execute(
                text("""
                ALTER TABLE simulation_sessions
                ADD COLUMN assignment_id UUID REFERENCES simulation_assignments(id) ON DELETE SET NULL;
            """)
            )
            print("Assignment column added.")
        else:
            print("'assignment_id' already exists.")

    print("Schema repair completed.")
    await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(patch_schema())
