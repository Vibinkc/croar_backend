import asyncio

from sqlalchemy import func, select

from app.core.database import db_manager
from app.models.enterprise.survey import SurveyType


async def count_survey_types() -> None:
    async with db_manager.session() as db:
        count = await db.scalar(select(func.count(SurveyType.id)))
        print(f"DEBUG: TOTAL_SURVEY_TYPES={count}")

        types = await db.execute(select(SurveyType.name))
        print(f"DEBUG: NAMES={[t[0] for t in types.all()]}")


if __name__ == "__main__":
    asyncio.run(count_survey_types())
