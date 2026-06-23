import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.shared.system_settings import SystemSettings


async def seed_settings():
    async with db_manager.session() as session:
        # Check if settings already exist
        settings_to_seed = [
            {
                "key": "signup_enabled",
                "value_bool": True,
                "description": "Enable/Disable self-service organization registration",
            },
            {
                "key": "login_enabled",
                "value_bool": True,
                "description": "Enable/Disable global application login",
            },
            {
                "key": "google_sso_enabled",
                "value_bool": True,
                "description": "Enable/Disable Google Single Sign-On",
            },
            {
                "key": "microsoft_sso_enabled",
                "value_bool": True,
                "description": "Enable/Disable Office 365 (Microsoft) Single Sign-On",
            },
        ]

        for s_data in settings_to_seed:
            stmt = select(SystemSettings).where(SystemSettings.key == s_data["key"])
            existing = (await session.execute(stmt)).scalar_one_or_none()

            if not existing:
                print(f"Seeding setting: {s_data['key']}")
                setting = SystemSettings(**s_data)
                session.add(setting)
            else:
                print(f"Setting {s_data['key']} already exists.")

        await session.commit()
    print("Seeding completed.")


if __name__ == "__main__":
    asyncio.run(seed_settings())
