import asyncio
import uuid

from sqlalchemy import select

from app.core.database import get_db
from app.models.enterprise.ai_simulation import AISimulation
from app.models.enterprise.company import Company


async def seed() -> None:
    session_gen = get_db()
    session = await anext(session_gen)

    # Get first company
    stmt = select(Company).limit(1)
    company = (await session.execute(stmt)).scalar_one_or_none()

    if not company:
        print("No company found to seed simulations for.")
        await session.close()
        return

    simulations = [
        {
            "id": uuid.uuid4(),
            "company_id": company.id,
            "title": "Executive Exit Interview",
            "scenario_type": "Role-Play",
            "description": "Practice a high-stakes exit interview with a departing executive to gather constructive feedback.",
            "agent_config": {
                "character_name": "Sarah (Departing VP)",
                "personality": "Professional but blunt. Frustrated with recent leadership changes.",
                "objective": "Understand the root cause of her departure and identify cultural red flags.",
                "scenario_type": "Exit Interview",
            },
        },
        {
            "id": uuid.uuid4(),
            "company_id": company.id,
            "title": "Conflict Mitigation",
            "scenario_type": "Communication",
            "description": "Handle a heated dispute between two team leads regarding resource allocation.",
            "agent_config": {
                "character_name": "Mark (Angry Lead)",
                "personality": "Defensive, feels overworked, blames others for delays.",
                "objective": "De-escalate the situation and reach a compromise.",
                "scenario_type": "Conflict Management",
            },
        },
        {
            "id": uuid.uuid4(),
            "company_id": company.id,
            "title": "Direct Report Coaching",
            "scenario_type": "Management",
            "description": "Coach a high-performer who has recently seen a dip in productivity.",
            "agent_config": {
                "character_name": "Alex (Employee)",
                "personality": "Talented but feeling burnt out and uninspired.",
                "objective": "Identify the burnout early and create a re-engagement plan.",
                "scenario_type": "Performance Coaching",
            },
        },
    ]

    for sim_data in simulations:
        # Check if already exists by title
        exists_stmt = select(AISimulation).where(
            AISimulation.title == sim_data["title"], AISimulation.company_id == company.id
        )
        exists = (await session.execute(exists_stmt)).scalar_one_or_none()
        if not exists:
            new_sim = AISimulation(**sim_data)
            session.add(new_sim)
            print(f"Added simulation: {sim_data['title']}")

    await session.commit()
    await session.close()
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())
