import asyncio

from sqlalchemy import text

from app.core.database import Base, db_manager


async def check_db():
    print("--- DATABASE DIAGNOSTIC ---")
    try:
        async with db_manager.engine.connect() as conn:
            # Check for uuid-ossp
            res = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'uuid-ossp'"))
            ext = res.fetchone()
            print(f"UUID Extension: {'FOUND' if ext else 'MISSING'}")

            # List all tables in public schema
            res = await conn.execute(
                text("""
                SELECT tablename
                FROM pg_catalog.pg_tables
                WHERE schemaname = 'public'
            """)
            )
            tables = [row[0] for row in res.fetchall()]
            print(f"Found {len(tables)} tables in 'public' schema:")
            for t in sorted(tables):
                print(f"  - {t}")

            if "system_settings" not in tables:
                print("!!! CRITICAL: system_settings table is MISSING !!!")
                if len(tables) == 0:
                    print("🔄 Running Fail-safe Table Creation...")
                    # Re-importing models to ensure metadata is populated

                    async with db_manager.engine.begin() as force_conn:
                        await force_conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
                        await force_conn.run_sync(Base.metadata.create_all)
                    print("✅ Force-creation complete. Tables should now exist.")
            else:
                print("✅ system_settings table exists.")

    except Exception as e:
        print(f"❌ Error during diagnostic: {e}")
    finally:
        await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(check_db())
