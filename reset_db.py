import asyncio

import sqlalchemy as sa

from app.core.database import db_manager


async def main():
    print("Resetting database...")
    async with db_manager.engine.begin() as conn:
        # Enable uuid-ossp
        print("Enabling uuid-ossp extension...")
        await conn.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))

        # Drop all tables and types (clean slate)
        # Note: In PostgreSQL, dropping types can be tricky if they are in use.
        # This will drop all tables in the public schema.
        print("Clearing partial schema...")
        await conn.execute(
            sa.text("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
                FOR r IN (SELECT typname FROM pg_type t JOIN pg_namespace n ON n.oid = t.typnamespace WHERE n.nspname = 'public' AND t.typtype = 'e') LOOP
                    EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        )
    print("Database reset complete.")
    await db_manager.close_all()


if __name__ == "__main__":
    asyncio.run(main())
