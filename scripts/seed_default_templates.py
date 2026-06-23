import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.company import Company
from app.models.enterprise.survey import SurveyQuestion, SurveyTemplate, SurveyType


async def seed_templates():
    async with db_manager.session() as session:
        # 1. Get a Company
        res = await session.execute(select(Company.id).limit(1))
        company_id = res.scalar()
        if not company_id:
            print("No company found. Please seed a company first.")
            return

        # 2. Get Survey Types
        res = await session.execute(select(SurveyType))
        types = {t.name: t.id for t in res.scalars().all()}

        if not types:
            print("No survey types found. Run seed_surveys.py first.")
            return

        templates = [
            {
                "type": "Employee Engagement",
                "title": "Annual Cultural Engagement Survey",
                "description": "A comprehensive assessment of organizational alignment, job satisfaction, and long-term commitment.",
                "questions": [
                    {"text": "I feel proud to work for this organization.", "type": "RATING"},
                    {"text": "I would recommend this company as a great place to work.", "type": "RATING"},
                    {"text": "My manager provides me with the support I need to succeed.", "type": "RATING"},
                    {"text": "I see myself working here in two years' time.", "type": "RATING"},
                    {
                        "text": "What is the one thing we could do to improve your experience here?",
                        "type": "TEXT",
                    },
                ],
            },
            {
                "type": "DEI (Diversity, Equity & Inclusion)",
                "title": "Inclusive Culture Framework",
                "description": "Measuring belonging, fairness, and the effectiveness of our diversity initiatives.",
                "questions": [
                    {"text": "I feel like I belong at this company.", "type": "RATING"},
                    {"text": "People from all backgrounds are treated fairly here.", "type": "RATING"},
                    {"text": "What does 'inclusion' mean to you in your daily work?", "type": "TEXT"},
                    {
                        "text": "How often do you hear biased comments at work?",
                        "type": "MCQ",
                        "options": ["Never", "Rarely", "Occasionally", "Frequently"],
                    },
                ],
            },
            {
                "type": "Pulse Survey",
                "title": "Monthly Sentiment Pulse",
                "description": "A quick check-in to monitor organizational health and immediate blockers.",
                "questions": [
                    {"text": "How happy are you at work this month?", "type": "RATING"},
                    {"text": "I have the tools and resources I need to do my job.", "type": "RATING"},
                    {"text": "What is your primary focus for the upcoming week?", "type": "TEXT"},
                ],
            },
        ]

        for t_data in templates:
            type_id = types.get(t_data["type"])
            if not type_id:
                continue

            # Check if exists
            exists = await session.execute(
                select(SurveyTemplate).where(
                    SurveyTemplate.title == t_data["title"], SurveyTemplate.company_id == company_id
                )
            )
            if exists.scalar():
                continue

            new_tpl = SurveyTemplate(
                survey_type_id=type_id,
                title=t_data["title"],
                description=t_data["description"],
                company_id=company_id,
                is_active=True,
            )
            session.add(new_tpl)
            await session.flush()

            for idx, q_data in enumerate(t_data["questions"]):
                import json

                new_q = SurveyQuestion(
                    template_id=new_tpl.id,
                    text=q_data["text"],
                    type=q_data["type"],
                    order=idx,
                    scale_min=1 if q_data["type"] == "RATING" else None,
                    scale_max=5 if q_data["type"] == "RATING" else None,
                    options=json.dumps(q_data.get("options", [])) if q_data["type"] == "MCQ" else None,
                )
                session.add(new_q)

        await session.commit()
        print("Default HR templates seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed_templates())
