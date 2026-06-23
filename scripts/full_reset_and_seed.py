import asyncio
import os
import sys
import uuid

from sqlalchemy import insert, select, text

# Add the app directory to the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.core.security import get_password_hash
from app.models.enterprise.assessment import AssessmentTemplate
from app.models.enterprise.candidate import ApplicationStatus, Candidate, CandidateApplication
from app.models.enterprise.company import Company
from app.models.enterprise.job import JobRequirement, JobStatus
from app.models.enterprise.onboarding import OnboardingStatus, OnboardingTemplate
from app.models.enterprise.project import Project
from app.models.enterprise.simulation import SimulationScenario
from app.models.enterprise.survey import SurveyTemplate, SurveyType
from app.models.enterprise.user_role import EnterpriseUser, user_roles
from app.models.enterprise.x360 import X360AssessmentTemplate
from app.models.shared.auth import Permission, Role, role_permissions, super_admin_roles
from app.models.shared.constants import ModuleScope, PermissionAction, PermissionScope
from app.models.shared.super_admin import SuperAdmin


async def ensure_enums(session):
    print("=== ENSURING ENUMS ===")
    # Modules
    modules = [
        "platform",
        "organization",
        "jobs",
        "candidates",
        "assessments",
        "interviews",
        "onboarding",
        "ai_training",
        "surveys",
        "communications",
        "employees",
        "projects",
        "tasks",
        "automation",
        "billing",
        "analytics",
    ]
    for module in modules:
        try:
            # PostgreSQL doesn't support IF NOT EXISTS for ADD VALUE easily in all versions
            # We check if it exists first
            res = await session.execute(
                text(
                    f"SELECT 1 FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'modulescope' AND pg_enum.enumlabel = '{module}'"
                )
            )
            if not res.scalar():
                await session.execute(text(f"ALTER TYPE modulescope ADD VALUE '{module}'"))
                print(f"Added '{module}' to modulescope enum")
        except Exception as e:
            print(f"Error adding enum value {module}: {e}")

    # Permission Actions
    actions = [
        "create",
        "read",
        "update",
        "delete",
        "moderate",
        "assign",
        "publish",
        "submit",
        "review",
        "attempt",
        "generate",
        "finalize",
    ]
    for action in actions:
        try:
            res = await session.execute(
                text(
                    f"SELECT 1 FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'permissionaction' AND pg_enum.enumlabel = '{action}'"
                )
            )
            if not res.scalar():
                await session.execute(text(f"ALTER TYPE permissionaction ADD VALUE '{action}'"))
                print(f"Added '{action}' to permissionaction enum")
        except Exception as e:
            print(f"Error adding enum value {action}: {e}")

    await session.commit()


async def reset_database(session):
    print("=== RESETTING DATABASE ===")

    # Tables to truncate in order (respecting foreign keys)
    # We use TRUNCATE ... CASCADE for Postgres
    tables_to_truncate = [
        "audit_logs",
        "backup",
        "email_logs",
        "simulation_sessions",
        "simulation_assignments",
        "simulation_scenarios",
        "survey_responses",
        "survey_invites",
        "survey_instances",
        "survey_questions",
        "survey_templates",
        "survey_types",
        "x360_assessment_responses",
        "x360_assessment_assignments",
        "x360_employee_rater_maps",
        "x360_assessment_cycles",
        "x360_template_questions",
        "x360_assessment_templates",
        "x360_questions",
        "project_tasks",
        "project_members",
        "projects",
        "employees",
        "departments",
        "onboarding_notes",
        "onboarding_tasks",
        "onboarding_activities",
        "onboarding_documents",
        "onboardings",
        "onboarding_automations",
        "onboarding_templates",
        "onboarding_statuses",
        "assessment_attempts",
        "assessment_automations",
        "assessment_templates",
        "interview_attempts",
        "interview_schedules",
        "interview_automations",
        "interviews",
        "mail_automations",
        "candidate_applications",
        "candidates",
        "job_postings",
        "job_requirements",
        "job_statuses",
        "application_statuses",
        "email_templates",
        "enterprise_students",
        "hiring_agents",
        "user_roles",
        "role_permissions",
        "users",
        "companies",
        "super_admin_roles",
        "super_admins",
        "roles",
        "permissions",
    ]

    for table in tables_to_truncate:
        try:
            await session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
            print(f"Truncated {table}")
        except Exception as e:
            print(f"Skipping {table}: {e}")

    await session.commit()
    print("Database reset complete.")


async def seed_system_data(session):
    print("\n=== SEEDING SYSTEM DATA ===")

    # 1. Permissions
    actions = list(PermissionAction)
    modules = list(ModuleScope)
    for module in modules:
        for action in actions:
            perm = Permission(
                resource=module.value,
                action=action,
                module=module,
                scope=PermissionScope.system if module == ModuleScope.platform else PermissionScope.tenant,
                is_system=True,
            )
            session.add(perm)
    await session.flush()
    print("Permissions seeded.")

    # 2. SUPER_ADMIN Role
    sa_role = Role(
        name="SUPER_ADMIN",
        description="Platform-wide administrator with full access.",
        is_system=True,
        role_rank=0,
    )
    session.add(sa_role)
    await session.flush()

    # Link all permissions to SUPER_ADMIN
    stmt = select(Permission.id)
    res = await session.execute(stmt)
    all_perm_ids = res.scalars().all()
    for pid in all_perm_ids:
        await session.execute(insert(role_permissions).values(role_id=sa_role.id, permission_id=pid))

    # 2.1 Seed Default SuperAdmin User
    super_admin_user = SuperAdmin(
        username="superadmin",
        email="admin@croar.ai",
        password_hash=get_password_hash("SuperAdmin@123"),
        first_name="Platform",
        last_name="Owner",
        is_active=True,
    )
    session.add(super_admin_user)
    await session.flush()

    # Link SuperAdmin User to Role
    await session.execute(
        insert(super_admin_roles).values(super_admin_id=super_admin_user.id, role_id=sa_role.id)
    )
    print("SUPER_ADMIN role, permissions, and default user seeded.")

    # 3. Statuses
    # Job Statuses
    job_statuses_data = [
        {"id": 1, "name": "Draft", "description": "Job posting is in draft mode.", "is_system": True},
        {
            "id": 2,
            "name": "Active",
            "description": "Job is open and accepting applications.",
            "is_system": True,
        },
        {
            "id": 3,
            "name": "On Hold",
            "description": "Hiring for this job is temporarily paused.",
            "is_system": True,
        },
        {
            "id": 4,
            "name": "Closed",
            "description": "Job is no longer accepting applications.",
            "is_system": True,
        },
    ]
    for js in job_statuses_data:
        session.add(JobStatus(name=js["name"], description=js["description"], is_system=js["is_system"]))

    # Application Statuses
    app_statuses_data = [
        {"id": 1, "name": "Applied", "description": "Candidate has applied for the job.", "is_system": True},
        {"id": 2, "name": "Screening", "description": "Candidate is being screened.", "is_system": True},
        {
            "id": 3,
            "name": "Interviewing",
            "description": "Candidate is in the interview process.",
            "is_system": True,
        },
        {
            "id": 4,
            "name": "Offered",
            "description": "Candidate has been offered the position.",
            "is_system": True,
        },
        {"id": 5, "name": "Hired", "description": "Candidate has been hired.", "is_system": True},
        {
            "id": 6,
            "name": "Rejected",
            "description": "Candidate application was rejected.",
            "is_system": True,
        },
        {
            "id": 7,
            "name": "Withdrawn",
            "description": "Candidate withdrew their application.",
            "is_system": True,
        },
    ]
    for aps in app_statuses_data:
        session.add(
            ApplicationStatus(name=aps["name"], description=aps["description"], is_system=aps["is_system"])
        )

    # Onboarding Statuses
    onb_statuses_data = ["New", "Awaiting Confirmation", "In Progress", "Completed", "On Hold"]
    for os_name in onb_statuses_data:
        session.add(OnboardingStatus(name=os_name, is_system=True))

    await session.commit()
    print("System statuses seeded.")


async def seed_tenant(session, name, slug, admin_email, company_id=None):
    print(f"\n=== SEEDING TENANT: {name} ===")

    # 1. Company
    company = Company(
        id=company_id or uuid.uuid4(), name=name, slug=slug, industry="Technology", location="Global"
    )
    session.add(company)
    await session.flush()

    # 2. Admin Role
    admin_role = Role(
        name="ADMIN",
        description=f"Full access administrator for {name}",
        tenant_id=company.id,
        is_system=True,
        role_rank=0,
    )
    session.add(admin_role)
    await session.flush()

    # Link all non-platform permissions to Admin
    stmt = select(Permission.id).where(Permission.module != ModuleScope.platform)
    res = await session.execute(stmt)
    perm_ids = res.scalars().all()
    for pid in perm_ids:
        await session.execute(insert(role_permissions).values(role_id=admin_role.id, permission_id=pid))

    # 3. Admin User
    admin_user = EnterpriseUser(
        email=admin_email,
        password_hash=get_password_hash("Admin@123"),
        first_name=name.split()[0],
        last_name="Admin",
        company_id=company.id,
        is_active=True,
    )
    session.add(admin_user)
    await session.flush()

    # Link User to Role
    await session.execute(insert(user_roles).values(user_id=admin_user.id, role_id=admin_role.id))

    return company, admin_user


async def seed_feature_data(session, company, suffix):
    print(f"Seeding feature data for {company.name}...")

    # 1. Jobs
    job = JobRequirement(
        company_id=company.id,
        title=f"Software Engineer ({suffix})",
        description=f"Exciting opportunity at {company.name} for a Software Engineer.",
        status_id=2,  # Active
        location="Remote",
        required_skills=["Python", "FastAPI", "React"],
        salary_min=100000,
        salary_max=150000,
    )
    session.add(job)
    await session.flush()

    # 2. Candidates & Applications
    candidate = Candidate(
        company_id=company.id,
        full_name=f"Candidate {suffix}",
        email=f"candidate_{suffix.lower()}@{company.slug}.com",
        phone="1234567890",
        skills=["Python", "JavaScript"],
    )
    session.add(candidate)
    await session.flush()

    application = CandidateApplication(
        company_id=company.id,
        candidate_id=candidate.id,
        job_requirement_id=job.id,
        status_id=1,  # Applied
        current_stage=1,
    )
    session.add(application)
    await session.flush()

    # 3. Assessment Template
    # Importing AssessmentTemplate locally or from models is already done via *
    template = AssessmentTemplate(
        company_id=company.id,
        name=f"Technical Quiz - {suffix}",
        topic="General Engineering",
        question_count=5,
        test_duration=30,
    )
    session.add(template)
    await session.flush()

    # 4. Onboarding Template
    onb_template = OnboardingTemplate(
        company_id=company.id,
        name=f"Standard Onboarding ({suffix})",
        description=f"Welcome to {company.name}!",
    )
    session.add(onb_template)
    await session.flush()

    # 5. Survey Type
    survey_type = SurveyType(name=f"General Feedback ({suffix})", company_id=company.id)
    session.add(survey_type)
    await session.flush()

    # 6. Survey Template
    survey_template = SurveyTemplate(
        company_id=company.id,
        survey_type_id=survey_type.id,
        title=f"Employee Satisfaction ({suffix})",
        description="We value your feedback.",
    )
    session.add(survey_template)
    await session.flush()

    # 7. X360 Template
    x360_template = X360AssessmentTemplate(
        company_id=company.id, name=f"Annual Review ({suffix})", description="360 degree feedback."
    )
    session.add(x360_template)
    await session.flush()

    # 8. Simulation Scenario
    simulation = SimulationScenario(
        company_id=company.id,
        title=f"Customer Interaction ({suffix})",
        description="Handling a difficult customer query.",
        character_name="John Doe",
        character_role="Dissatisfied Customer",
        system_prompt="You are a customer who is unhappy with a recent purchase.",
        initial_message="I'd like to speak with a manager about my order.",
    )
    session.add(simulation)
    await session.flush()

    # 8. Project
    project = Project(
        company_id=company.id,
        name=f"Internal Dashboard ({suffix})",
        description="Internal tool for employees.",
    )
    session.add(project)
    await session.flush()

    print(f"Feature data seeded for {company.name}.")


async def main():
    async with db_manager.session() as session:
        # 0. Ensure enums
        await ensure_enums(session)

        # 1. Reset everything
        await reset_database(session)

        # System seed
        await seed_system_data(session)

        # Seed AppXcess
        appxcess_id = uuid.UUID("900125e1-1ab6-47e5-a410-2515ab2e89c0")
        appxcess, _ = await seed_tenant(session, "AppXcess", "appxcess", "admin@appxcess.com", appxcess_id)
        await seed_feature_data(session, appxcess, "AXC")

        # Seed Datanet
        datanet_id = uuid.UUID("da7a9eb5-5a5f-4d69-8e2b-f8f8b8b8b8b8")
        datanet, _ = await seed_tenant(session, "Datanet", "datanet", "admin@datanet.co", datanet_id)
        await seed_feature_data(session, datanet, "DN")

        await session.commit()

    print("\n\nAll tasks completed successfully!")
    print("Super Admin: admin@croar.ai / SuperAdmin@123")
    print("AppXcess Admin: admin@appxcess.com / Admin@123")
    print("Datanet Admin: admin@datanet.co / Admin@123")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
