import asyncio
import os
import sys
import uuid

from sqlalchemy import select

# Ensure the app code is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.company import Company
from app.models.enterprise.onboarding import OnboardingTemplate

DEFAULT_TEMPLATE_BASE = {
    "description": "Comprehensive onboarding template for collecting personal, bank, educational, and professional data, along with mandatory document uploads.",
    "sections": [
        "personal_info",
        "contact_info",
        "identity_legal",
        "education_details",
        "professional_experience",
        "bank_details",
        "document_uploads",
    ],
    "required_documents": [
        {"name": "Profile Photo", "description": "Recent passport size photo", "required": True},
        {"name": "PAN Card", "description": "Copy of Permanent Account Number card", "required": True},
        {"name": "Aadhar Card", "description": "Copy of Aadhar card (Front & Back)", "required": True},
        {
            "name": "Qualification Proof",
            "description": "Marksheet or Degree of highest qualification",
            "required": True,
        },
        {
            "name": "Experience Letter",
            "description": "Relieving or Experience letter from last employer",
            "required": False,
        },
        {"name": "Bank Proof", "description": "Cancelled cheque or passbook first page", "required": True},
    ],
    "form_config": {
        "sections": [
            {
                "id": "personal_info",
                "title": "Personal Information",
                "fields": [
                    {"name": "full_name", "label": "Full Name", "type": "text", "required": True},
                    {"name": "dob", "label": "Date of Birth", "type": "date", "required": True},
                    {
                        "name": "gender",
                        "label": "Gender",
                        "type": "select",
                        "required": True,
                        "options": ["Male", "Female", "Other"],
                    },
                    {
                        "name": "blood_group",
                        "label": "Blood Group",
                        "type": "select",
                        "required": True,
                        "options": ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
                    },
                    {
                        "name": "marital_status",
                        "label": "Marital Status",
                        "type": "select",
                        "required": True,
                        "options": ["Single", "Married", "Divorced", "Widowed"],
                    },
                ],
            },
            {
                "id": "contact_info",
                "title": "Contact Information",
                "fields": [
                    {"name": "personal_email", "label": "Personal Email", "type": "email", "required": True},
                    {"name": "mobile_number", "label": "Mobile Number", "type": "phone", "required": True},
                    {
                        "name": "emergency_contact_name",
                        "label": "Emergency Contact Name",
                        "type": "text",
                        "required": True,
                    },
                    {
                        "name": "emergency_contact_number",
                        "label": "Emergency Contact Number",
                        "type": "phone",
                        "required": True,
                    },
                    {
                        "name": "current_address",
                        "label": "Current Address",
                        "type": "textarea",
                        "required": True,
                    },
                    {
                        "name": "permanent_address",
                        "label": "Permanent Address",
                        "type": "textarea",
                        "required": True,
                    },
                ],
            },
            {
                "id": "identity_legal",
                "title": "Identity & Legal",
                "fields": [
                    {"name": "pan_number", "label": "PAN Number", "type": "text", "required": True},
                    {"name": "aadhar_number", "label": "Aadhar Number", "type": "text", "required": True},
                    {
                        "name": "passport_number",
                        "label": "Passport Number",
                        "type": "text",
                        "required": False,
                    },
                    {"name": "uan_number", "label": "UAN Number (PF)", "type": "text", "required": False},
                ],
            },
            {
                "id": "education_details",
                "title": "Education Details",
                "fields": [
                    {
                        "name": "highest_qualification",
                        "label": "Highest Qualification",
                        "type": "select",
                        "required": True,
                        "options": ["Doctorate", "Post-Graduate", "Graduate", "Diploma", "12th", "10th"],
                    },
                    {
                        "name": "university_college",
                        "label": "University/College Name",
                        "type": "text",
                        "required": True,
                    },
                    {"name": "passing_year", "label": "Passing Year", "type": "number", "required": True},
                    {"name": "percentage_cgpa", "label": "Percentage/CGPA", "type": "text", "required": True},
                ],
            },
            {
                "id": "professional_experience",
                "title": "Professional Experience",
                "fields": [
                    {
                        "name": "previous_company",
                        "label": "Previous Company Name",
                        "type": "text",
                        "required": False,
                    },
                    {
                        "name": "total_experience",
                        "label": "Total Experience (Years)",
                        "type": "number",
                        "required": False,
                    },
                    {
                        "name": "last_drawn_salary",
                        "label": "Last Drawn Salary (Annual)",
                        "type": "number",
                        "required": False,
                    },
                ],
            },
            {
                "id": "bank_details",
                "title": "Bank Account Details",
                "fields": [
                    {
                        "name": "account_holder",
                        "label": "Account Holder Name",
                        "type": "text",
                        "required": True,
                    },
                    {"name": "bank_name", "label": "Bank Name", "type": "text", "required": True},
                    {"name": "account_number", "label": "Account Number", "type": "text", "required": True},
                    {"name": "ifsc_code", "label": "IFSC Code", "type": "text", "required": True},
                ],
            },
            {
                "id": "document_uploads",
                "title": "Document Uploads",
                "fields": [
                    {"name": "profile_photo", "label": "Profile Photo", "type": "file", "required": True},
                    {"name": "pan_card_copy", "label": "PAN Card Copy", "type": "file", "required": True},
                    {
                        "name": "aadhar_card_copy",
                        "label": "Aadhar Card Copy",
                        "type": "file",
                        "required": True,
                    },
                    {
                        "name": "qualification_marksheet",
                        "label": "Highest Qualification Marksheet",
                        "type": "file",
                        "required": True,
                    },
                    {
                        "name": "experience_letter",
                        "label": "Experience/Relieving Letter",
                        "type": "file",
                        "required": False,
                    },
                    {
                        "name": "bank_proof",
                        "label": "Cancelled Cheque/Passbook Copy",
                        "type": "file",
                        "required": True,
                    },
                ],
            },
        ]
    },
}


async def seed_onboarding_template():
    print("=== SEEDING ONBOARDING TEMPLATES FOR ALL COMPANIES ===")
    async with db_manager.session() as session:
        # Fetch all companies
        res = await session.execute(select(Company))
        companies = res.scalars().all()

        if not companies:
            print("No companies found to seed templates for.")
            return

        for company in companies:
            template_name = f"Standard Onboarding - {company.name}"
            print(f"Processing for {company.name}...")

            # Check if already exists
            stmt = select(OnboardingTemplate).where(
                OnboardingTemplate.name == template_name, OnboardingTemplate.company_id == company.id
            )
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()

            if existing:
                print(f"  Template '{template_name}' exists. Updating...")
                existing.description = DEFAULT_TEMPLATE_BASE["description"]
                existing.sections = DEFAULT_TEMPLATE_BASE["sections"]
                existing.required_documents = DEFAULT_TEMPLATE_BASE["required_documents"]
                existing.form_config = DEFAULT_TEMPLATE_BASE["form_config"]
            else:
                print(f"  Creating new template: {template_name}")
                new_tpl = OnboardingTemplate(
                    id=uuid.uuid4(),
                    name=template_name,
                    description=DEFAULT_TEMPLATE_BASE["description"],
                    sections=DEFAULT_TEMPLATE_BASE["sections"],
                    required_documents=DEFAULT_TEMPLATE_BASE["required_documents"],
                    form_config=DEFAULT_TEMPLATE_BASE["form_config"],
                    company_id=company.id,
                )
                session.add(new_tpl)

        await session.commit()
    print("Seeding complete!")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_onboarding_template())
