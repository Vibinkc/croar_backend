import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.survey import SurveyType


async def check_survey_types():
    async with db_manager.session() as session:
        stmt = select(SurveyType)
        result = await session.execute(stmt)
        types = result.scalars().all()
        print(f"Total Survey Types: {len(types)}")
        for t in types:
            print(f"- {t.name}: {t.description}")


if __name__ == "__main__":
    asyncio.run(check_survey_types())
