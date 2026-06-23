import asyncio
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.survey import SurveyType

SURVEY_TYPES = [
    {"name": "Employee Engagement", "description": "Measure overall commitment and satisfaction."},
    {"name": "eNPS (Net Promoter Score)", "description": "Quick gauge of employee loyalty and advocacy."},
    {
        "name": "DEI (Diversity, Equity & Inclusion)",
        "description": "Assess workplace belonging and fairness.",
    },
    {"name": "Pulse Survey", "description": "Short, frequent check-ins on morale or specific topics."},
    {"name": "Onboarding Experience", "description": "Feedback on the first 30/60/90 days."},
    {"name": "Exit Interview", "description": "Understand reasons for departure and areas for improvement."},
    {"name": "Manager Effectiveness", "description": "Gather feedback on direct supervisor performance."},
    {"name": "Leadership Effectiveness", "description": "Evaluate executive team vision and communication."},
    {"name": "Team Climate", "description": "Assess collaboration and psychological safety within teams."},
    {
        "name": "Learning & Training Feedback",
        "description": "Evaluate the impact of professional development programs.",
    },
    {
        "name": "Performance Alignment",
        "description": "Check if individual goals match organizational strategy.",
    },
    {"name": "Workplace Well-being", "description": "Monitor stress levels and work-life balance."},
    {"name": "Change Management", "description": "Gauge sentiment during organizational transitions."},
]


async def seed_survey_types():
    async with db_manager.session() as db:
        for st_data in SURVEY_TYPES:
            # Check if exists
            stmt = select(SurveyType).where(SurveyType.name == st_data["name"])
            res = await db.execute(stmt)
            existing = res.scalar_one_or_none()

            if not existing:
                new_type = SurveyType(**st_data)
                db.add(new_type)
                print(f"Adding survey type: {st_data['name']}")

        await db.commit()
        print("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_survey_types())
