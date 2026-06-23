import asyncio
import os
import sys
from uuid import uuid4

from sqlalchemy import select

# Ensure the app code is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.company import Company
from app.models.enterprise.x360 import (
    QuestionCategory,
    QuestionType,
    X360AssessmentTemplate,
    X360Question,
    X360TemplateQuestion,
)


async def seed_x360():
    print("=== SEEDING X360 DATA ===")

    async with db_manager.session() as session:
        # 1. Get Company (default to Test Corp or first one)
        stmt = select(Company).limit(1)
        result = await session.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            print("Error: No company found. Please run seed_employee.py first.")
            return

        print(f"Using Company: {company.name} ({company.id})")

        # 2. Define standard questions
        questions_to_add = [
            # Performance
            {
                "text": "How effectively does this employee meet their project deadlines?",
                "category": QuestionCategory.PERFORMANCE,
                "type": QuestionType.RATING,
            },
            {
                "text": "How would you rate the quality of this employee's technical output?",
                "category": QuestionCategory.PERFORMANCE,
                "type": QuestionType.RATING,
            },
            {
                "text": "What are this employee's top 3 strengths?",
                "category": QuestionCategory.PERFORMANCE,
                "type": QuestionType.TEXT,
            },
            # Leadership
            {
                "text": "How well does this employee mentor or support colleagues?",
                "category": QuestionCategory.LEADERSHIP,
                "type": QuestionType.RATING,
            },
            {
                "text": "Rate this employee's ability to take ownership of complex tasks.",
                "category": QuestionCategory.LEADERSHIP,
                "type": QuestionType.RATING,
            },
            # Core Values
            {
                "text": "How consistently does this employee demonstrate our core value of 'Integrity'?",
                "category": QuestionCategory.CORE_VALUES,
                "type": QuestionType.RATING,
            },
            {
                "text": "How effectively does this employee collaborate across different teams?",
                "category": QuestionCategory.CORE_VALUES,
                "type": QuestionType.RATING,
            },
            # Engagement
            {
                "text": "How much does this employee contribute to a positive team culture?",
                "category": QuestionCategory.ENGAGEMENT,
                "type": QuestionType.RATING,
            },
            {
                "text": "What is one thing this employee could do to improve their impact on the team?",
                "category": QuestionCategory.ENGAGEMENT,
                "type": QuestionType.TEXT,
            },
        ]

        created_questions = []
        for q_data in questions_to_add:
            # Check if exists
            stmt = select(X360Question).where(
                X360Question.text == q_data["text"], X360Question.company_id == company.id
            )
            res = await session.execute(stmt)
            exists = res.scalar_one_or_none()

            if not exists:
                new_q = X360Question(id=uuid4(), company_id=company.id, **q_data)
                session.add(new_q)
                created_questions.append(new_q)
                print(f"Added Question: {q_data['text'][:50]}...")
            else:
                created_questions.append(exists)
                print(f"Question already exists: {q_data['text'][:50]}...")

        await session.flush()

        # 3. Create a default template
        template_name = "Annual Performance Review (Standard)"
        stmt = select(X360AssessmentTemplate).where(
            X360AssessmentTemplate.name == template_name, X360AssessmentTemplate.company_id == company.id
        )
        res = await session.execute(stmt)
        template = res.scalar_one_or_none()

        if not template:
            template = X360AssessmentTemplate(
                id=uuid4(),
                name=template_name,
                description="A comprehensive 360-degree feedback template covering performance, leadership, and core values.",
                company_id=company.id,
            )
            session.add(template)
            await session.flush()
            print(f"Created Template: {template.name}")

            # Add questions to template
            for idx, q in enumerate(created_questions):
                tpl_q = X360TemplateQuestion(template_id=template.id, question_id=q.id, order=idx)
                session.add(tpl_q)
            print(f"Linked {len(created_questions)} questions to template.")
        else:
            print(f"Template already exists: {template.name}")

        await session.commit()
        print("\n=== X360 SEEDING COMPLETE ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_x360())
