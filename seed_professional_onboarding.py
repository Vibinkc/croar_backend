import asyncio

from app.core.database import db_manager
from app.models.enterprise.onboarding import OnboardingTemplate


async def seed_professional_template():
    template_data = {
        "name": "Professional Corporate Onboarding",
        "description": "A comprehensive onboarding flow for corporate employees covering personal, contact, identity, education, professional, and bank details.",
        "sections": [
            "personal_info",
            "contact_info",
            "identity_legal",
            "education_details",
            "professional_experience",
            "bank_details",
            "document_uploads",
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
                        {
                            "name": "personal_email",
                            "label": "Personal Email",
                            "type": "email",
                            "required": True,
                        },
                        {
                            "name": "mobile_number",
                            "label": "Mobile Number",
                            "type": "phone",
                            "required": True,
                        },
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
                            "type": "text",
                            "required": True,
                        },
                        {
                            "name": "permanent_address",
                            "label": "Permanent Address",
                            "type": "text",
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
                        {
                            "name": "percentage_cgpa",
                            "label": "Percentage/CGPA",
                            "type": "number",
                            "required": True,
                        },
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
                        {
                            "name": "account_number",
                            "label": "Account Number",
                            "type": "text",
                            "required": True,
                        },
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
        "required_documents": [
            {"name": "Profile Photo", "description": "Recent passport size photo"},
            {"name": "PAN Card", "description": "Copy of Permanent Account Number card"},
            {"name": "Aadhar Card", "description": "Copy of Aadhar card (Front & Back)"},
            {"name": "Qualification Proof", "description": "Marksheet or Degree of highest qualification"},
            {"name": "Experience Letter", "description": "Relieving or Experience letter from last employer"},
            {"name": "Bank Proof", "description": "Cancelled cheque or passbook first page"},
        ],
    }

    async with db_manager.session() as session:
        from sqlalchemy import select

        stmt = select(OnboardingTemplate).where(OnboardingTemplate.name == template_data["name"])
        existing = await session.execute(stmt)
        if not existing.scalar_one_or_none():
            template = OnboardingTemplate(**template_data)
            session.add(template)
            await session.commit()
            print(f"Template '{template_data['name']}' seeded successfully.")
        else:
            print(f"Template '{template_data['name']}' already exists.")


if __name__ == "__main__":
    asyncio.run(seed_professional_template())
