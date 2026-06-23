import asyncio
import os
import sys

from sqlalchemy import select

# Ensure the app code is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.communication import EmailTemplate

TEMPLATES = [
    {
        "name": "Default Invite Email",
        "subject": "Invitation for next round: {{job_title}}",
        "body": "Hi {{candidate_name}},\n\nCongratulations! You have been shortlisted for the next round of the {{job_title}} position.\n\nPlease stay tuned for further instructions.\n\nBest regards,\nHiring Team",
        "variables": ["candidate_name", "job_title"],
    },
    {
        "name": "Assessment Invite Email",
        "subject": "Test Invitation: {{job_title}}",
        "body": "Hi {{candidate_name}},\n\nAs part of our selection process for {{job_title}}, we would like you to complete a brief assessment.\n\nPlease use the button below to begin your test:\n\n<a href='{{assessment_link}}' style='display:inline-block;padding:10px 18px;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px;font-weight:600;'>Start Assessment</a>\n\nIf the button does not work, copy and paste this link into your browser:\n{{assessment_link}}\n\nBest regards,\nRecruitment Team",
        "variables": ["candidate_name", "job_title", "assessment_link"],
    },
    {
        "name": "Interview Invitation",
        "subject": "Interview Scheduled: {{job_title}}",
        "body": "Hi {{candidate_name}},\n\nWe are excited to move forward with your application for {{job_title}}! We have scheduled an interview for you.\n\nPlease use the button below to join your interview:\n\n<a href='{{interview_link}}' style='display:inline-block;padding:10px 18px;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px;font-weight:600;'>Join Interview</a>\n\nIf the button does not work, copy and paste this link into your browser:\n{{interview_link}}\n\nBest regards,\nScheduling team",
        "variables": ["candidate_name", "job_title", "interview_link"],
    },
    {
        "name": "Onboarding Welcome",
        "subject": "Welcome to the team! - {{job_title}}",
        "body": "Hi {{candidate_name}},\n\nWelcome aboard! We are thrilled to have you join us as a {{job_title}}.\n\nPlease follow the link below to complete your onboarding formalities:\n{{onboarding_link}}\n\nCheers,\nHR Team",
        "variables": ["candidate_name", "job_title", "onboarding_link"],
    },
]


async def seed_templates():
    async with db_manager.session() as session:
        for t_data in TEMPLATES:
            # Check if template already exists by name
            stmt = select(EmailTemplate).where(EmailTemplate.name == t_data["name"])
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()

            if not existing:
                print(f"Seeding template: {t_data['name']}")
                new_t = EmailTemplate(
                    name=t_data["name"],
                    subject=t_data["subject"],
                    body=t_data["body"],
                    variables=t_data["variables"],
                )
                session.add(new_t)
            else:
                print(f"Template already exists: {t_data['name']}")
                # Update existing template
                existing.subject = t_data["subject"]
                existing.body = t_data["body"]
                existing.variables = t_data["variables"]

        await session.commit()
    print("Seeding complete.")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_templates())
