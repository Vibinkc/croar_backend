import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.onboarding import OnboardingTemplate


async def check_template():
    async with db_manager.session() as session:
        stmt = select(OnboardingTemplate).where(
            OnboardingTemplate.name == "Professional Corporate Onboarding"
        )
        result = await session.execute(stmt)
        template = result.scalar_one_or_none()
        if template:
            print(f"Found template: {template.name}")
            print(f"Sections: {template.sections}")
            print(f"Required Documents: {len(template.required_documents)}")
        else:
            print("Template not found.")


if __name__ == "__main__":
    asyncio.run(check_template())
