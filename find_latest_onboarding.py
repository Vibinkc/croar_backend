import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.onboarding import Onboarding


async def main() -> None:
    async with db_manager.session() as session:
        stmt = select(Onboarding).order_by(Onboarding.created_at.desc()).limit(1)
        res = await session.execute(stmt)
        onb = res.scalar_one_or_none()
        with open("onb_id.txt", "w") as f:
            if onb:
                f.write(str(onb.id))
            else:
                f.write("NO ONBOARDING FOUND")


if __name__ == "__main__":
    asyncio.run(main())
