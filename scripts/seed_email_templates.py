import asyncio
import uuid

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.communication import EmailTemplate
from app.models.enterprise.company import Company

TEMPLATES = [
    {
        "name": "Shortlist_Next_Round",
        "subject": "Great News! You've been shortlisted for {{job_title}}",
        "body": "Hi {{candidate_name}},\n\nCongratulations! We've reviewed your application and are excited to move you forward to the next stage of our selection process for the {{job_title}} position.\n\nOur team will be in touch shortly with specific details about the next steps. In the meantime, feel free to check your application status on our portal:\n\n<a href='{{frontend_url}}' style='display:inline-block;padding:12px 24px;background:#6e8efb;color:#ffffff;text-decoration:none;border-radius:8px;font-weight:bold;'>View Status</a>\n\nBest regards,\n{{recruiter_name}}\n{{company_name}}",
        "variables": ["candidate_name", "job_title", "frontend_url", "recruiter_name", "company_name"],
    },
    {
        "name": "Assessment_Invitation",
        "subject": "Technical Assessment Invitation: {{job_title}}",
        "body": "Hi {{candidate_name}},\n\nTo better understand your skills for the {{job_title}} role, we'd like to invite you to complete a technical assessment.\n\n--------------------------------------------------\nASSESSMENT DETAILS:\nTopic:    {{test_topic}}\nDuration: {{test_duration}} minutes\n--------------------------------------------------\n\nPlease use the button below to start your assessment when you are ready:\n\n<a href='{{assessment_link}}' style='display:inline-block;padding:14px 30px;background:#4f46e5;color:#ffffff;text-decoration:none;border-radius:8px;font-weight:bold;margin:20px 0;'>Start Assessment</a>\n\nIf the button doesn't work, you can copy this link: {{assessment_link}}\n\nGood luck!\n{{company_name}} Hiring Team",
        "variables": [
            "candidate_name",
            "job_title",
            "test_topic",
            "test_duration",
            "assessment_link",
            "company_name",
        ],
    },
    {
        "name": "Interview_Invitation",
        "subject": "Interview Invitation: {{job_title}}",
        "body": "Hi {{candidate_name}},\n\nWe are impressed with your profile and would like to invite you for an interview for the {{job_title}} position.\n\nYour interview has been scheduled for:\n**{{interview_time}}**\n\nYou can join the session using the link below:\n\n<a href='{{interview_link}}' style='display:inline-block;padding:14px 30px;background:#10b981;color:#ffffff;text-decoration:none;border-radius:8px;font-weight:bold;margin:20px 0;'>Join Interview Session</a>\n\nWe look forward to speaking with you!\n\nBest regards,\n{{recruiter_name}}\n{{company_name}}",
        "variables": [
            "candidate_name",
            "job_title",
            "interview_time",
            "interview_link",
            "recruiter_name",
            "company_name",
        ],
    },
    {
        "name": "Offer_Letter",
        "subject": "Job Offer: {{job_title}} at {{company_name}}",
        "body": "Hi {{candidate_name}},\n\nWe are absolutely thrilled to offer you the position of **{{job_title}}** at {{company_name}}! \n\nWe were very impressed with your skills and experience, and we believe you will be a fantastic addition to our team.\n\nPlease review the official offer details and sign the document on our portal to accept the offer:\n\n<a href='{{frontend_url}}/dashboard' style='display:inline-block;padding:14px 30px;background:#7c3aed;color:#ffffff;text-decoration:none;border-radius:8px;font-weight:bold;margin:20px 0;'>Review & Accept Offer</a>\n\nWe can't wait to have you on board!\n\nBest regards,\n{{recruiter_name}}\n{{company_name}}",
        "variables": ["candidate_name", "job_title", "company_name", "frontend_url", "recruiter_name"],
    },
    {
        "name": "Onboarding_Invitation",
        "subject": "Welcome Aboard! Complete your Onboarding for {{company_name}}",
        "body": "Hi {{candidate_name}},\n\nWelcome to the team! We are excited to have you join {{company_name}} as a {{job_title}}.\n\nTo get started, please complete your onboarding formalities and upload the required documents through our portal:\n\n<a href='{{onboarding_link}}' style='display:inline-block;padding:14px 30px;background:#4f46e5;color:#ffffff;text-decoration:none;border-radius:8px;font-weight:bold;margin:20px 0;'>Complete Onboarding</a>\n\nIf you have any questions during the process, please don't hesitate to reach out.\n\nWelcome aboard!\n{{company_name}} HR Team",
        "variables": ["candidate_name", "job_title", "onboarding_link", "company_name"],
    },
]


async def seed_templates():
    print("Seeding Professional Email Templates for all companies...")
    async with db_manager.session() as session:
        # Fetch all companies
        res = await session.execute(select(Company))
        companies = res.scalars().all()

        for company in companies:
            print(f"Processing for {company.name}...")
            for t_data in TEMPLATES:
                stmt = select(EmailTemplate).where(
                    EmailTemplate.name == t_data["name"], EmailTemplate.company_id == company.id
                )
                res = await session.execute(stmt)
                existing = res.scalar_one_or_none()

                if existing:
                    print(f"Updating template: {t_data['name']}")
                    existing.subject = t_data["subject"]
                    existing.body = t_data["body"]
                    existing.variables = t_data["variables"]
                else:
                    print(f"Creating template: {t_data['name']}")
                    new_tpl = EmailTemplate(
                        id=uuid.uuid4(),
                        name=t_data["name"],
                        subject=t_data["subject"],
                        body=t_data["body"],
                        variables=t_data["variables"],
                        company_id=company.id,
                    )
                    session.add(new_tpl)

        await session.commit()
    print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_templates())
