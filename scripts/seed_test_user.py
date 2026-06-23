import asyncio
import os
import sys
import uuid
from datetime import date, timedelta

from sqlalchemy import delete, insert, select

# Ensure python path is correct
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.assessment import AssessmentTemplate, AssessmentType
from app.models.enterprise.candidate import Candidate, CandidateApplication
from app.models.enterprise.communication import EmailTemplate, MailAutomation
from app.models.enterprise.company import Company
from app.models.enterprise.employee import Department, Employee
from app.models.enterprise.interview import Interview
from app.models.enterprise.job import JobRequirement
from app.models.enterprise.onboarding import OnboardingTemplate
from app.models.enterprise.project import Project, ProjectTask, project_members
from app.models.enterprise.simulation import SimulationScenario
from app.models.enterprise.survey import SurveyTemplate, SurveyType
from app.models.enterprise.user_role import EnterpriseUser
from app.models.enterprise.x360 import (
    QuestionCategory,
    QuestionType,
    X360AssessmentTemplate,
    X360Question,
    X360TemplateQuestion,
)


async def run_seed():
    print("=== SEEDING DEMO DATA ===")
    async with db_manager.session() as session:
        # 1. Resolve Company
        company = None

        # Try finding test@appxcess.com
        res = await session.execute(select(EnterpriseUser).where(EnterpriseUser.email == "test@appxcess.com"))
        user = res.scalar_one_or_none()
        if user:
            print(f"Found test@appxcess.com user. Resolving company ID: {user.company_id}")
            res = await session.execute(select(Company).where(Company.id == user.company_id))
            company = res.scalar_one_or_none()

        # Try fallback to local admin
        if not company:
            res = await session.execute(
                select(EnterpriseUser).where(EnterpriseUser.email == "admin@appxcess.com")
            )
            user = res.scalar_one_or_none()
            if user:
                print(f"Found admin@appxcess.com user. Resolving company ID: {user.company_id}")
                res = await session.execute(select(Company).where(Company.id == user.company_id))
                company = res.scalar_one_or_none()

        # Last resort fallback: get first company or create one
        if not company:
            res = await session.execute(select(Company).limit(1))
            company = res.scalar_one_or_none()
            if company:
                print(f"Using first company found: {company.name} ({company.id})")
            else:
                company = Company(
                    id=uuid.UUID("a762b170-de8c-4ed6-be55-1616407743e0"),
                    name="Appxcess",
                    slug="appxcess-2c3d",
                    industry="Technology",
                    location="Global",
                )
                session.add(company)
                await session.flush()
                print(f"Created default company: {company.name}")

        print(f"Target Company: {company.name} ({company.id})")
        company_id = company.id

        # 2. Cleanup existing records for this company to prevent duplication
        print("\nCleaning up existing data for target company...")
        await session.execute(delete(ProjectTask).where(ProjectTask.company_id == company_id))
        await session.execute(delete(Project).where(Project.company_id == company_id))
        await session.execute(delete(Employee).where(Employee.company_id == company_id))
        await session.execute(delete(Department).where(Department.company_id == company_id))
        await session.execute(
            delete(CandidateApplication).where(CandidateApplication.company_id == company_id)
        )
        await session.execute(delete(Candidate).where(Candidate.company_id == company_id))
        await session.execute(delete(JobRequirement).where(JobRequirement.company_id == company_id))
        await session.execute(delete(AssessmentTemplate).where(AssessmentTemplate.company_id == company_id))
        await session.execute(delete(OnboardingTemplate).where(OnboardingTemplate.company_id == company_id))
        await session.execute(delete(SurveyTemplate).where(SurveyTemplate.company_id == company_id))
        await session.execute(
            delete(X360AssessmentTemplate).where(X360AssessmentTemplate.company_id == company_id)
        )
        await session.execute(delete(X360Question).where(X360Question.company_id == company_id))
        await session.execute(delete(SimulationScenario).where(SimulationScenario.company_id == company_id))
        await session.execute(delete(EmailTemplate).where(EmailTemplate.company_id == company_id))
        await session.execute(delete(Interview).where(Interview.company_id == company_id))
        await session.flush()

        # 3. Seed Departments and Employees
        print("\nSeeding Departments & Employees...")
        eng_dept = Department(
            id=uuid.uuid4(),
            name="Engineering",
            description="Core engineering and development team.",
            company_id=company_id,
        )
        prod_dept = Department(
            id=uuid.uuid4(),
            name="Product Management",
            description="Product managers and UI/UX designers.",
            company_id=company_id,
        )
        session.add_all([eng_dept, prod_dept])
        await session.flush()

        # Seed Vibin KC as CTO & Founder (reporting to None)
        vibi = Employee(
            id=uuid.uuid4(),
            employee_id="EXP-VIBIN-001",
            first_name="Vibin",
            last_name="KC",
            email="vibi@appxcess.com",
            designation="CTO & Founder",
            status="Active",
            employment_type="Full-time",
            company_id=company_id,
            department_id=eng_dept.id,
            hire_date=date.today() - timedelta(days=365),
            country="India",
            skills=["React", "Next.js", "Python", "FastAPI", "Docker"],
        )
        session.add(vibi)
        await session.flush()

        # Other Employees
        emp1 = Employee(
            id=uuid.uuid4(),
            employee_id="EMP-1002",
            first_name="John",
            last_name="Doe",
            email="john.doe@appxcess.com",
            designation="Senior Frontend Engineer",
            status="Active",
            employment_type="Full-time",
            company_id=company_id,
            department_id=eng_dept.id,
            hire_date=date.today() - timedelta(days=200),
            country="USA",
            reporting_to_id=vibi.id,
            skills=["React", "TypeScript", "Tailwind CSS", "Redux"],
        )
        emp2 = Employee(
            id=uuid.uuid4(),
            employee_id="EMP-1003",
            first_name="Sarah",
            last_name="Jenkins",
            email="sarah.j@appxcess.com",
            designation="AI Specialist",
            status="Active",
            employment_type="Full-time",
            company_id=company_id,
            department_id=eng_dept.id,
            hire_date=date.today() - timedelta(days=120),
            country="United Kingdom",
            reporting_to_id=vibi.id,
            skills=["Python", "PyTorch", "HuggingFace", "LangChain"],
        )
        emp3 = Employee(
            id=uuid.uuid4(),
            employee_id="EMP-1004",
            first_name="Mia",
            last_name="Wong",
            email="mia.wong@appxcess.com",
            designation="Lead Product Designer",
            status="Active",
            employment_type="Full-time",
            company_id=company_id,
            department_id=prod_dept.id,
            hire_date=date.today() - timedelta(days=180),
            country="Canada",
            reporting_to_id=vibi.id,
            skills=["Figma", "UI/UX Design", "Wireframing", "User Research"],
        )
        session.add_all([emp1, emp2, emp3])
        await session.flush()

        # 4. Seed Projects & Tasks
        print("\nSeeding Projects & Tasks...")
        proj = Project(
            id=uuid.uuid4(),
            name="Croar Sourcing Engine v1.0",
            description="Building AI-powered candidate scraping and matching pipeline.",
            status="Active",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=90),
            company_id=company_id,
            kanban_columns=["Planning", "Development", "Testing", "Done"],
        )
        session.add(proj)
        await session.flush()

        # Link project members using direct insert to avoid lazy-loading MissingGreenlet error
        await session.execute(
            insert(project_members).values(
                [
                    {"project_id": proj.id, "employee_id": vibi.id, "company_id": company_id},
                    {"project_id": proj.id, "employee_id": emp1.id, "company_id": company_id},
                    {"project_id": proj.id, "employee_id": emp2.id, "company_id": company_id},
                    {"project_id": proj.id, "employee_id": emp3.id, "company_id": company_id},
                ]
            )
        )
        await session.flush()

        # Seed Tasks
        task1 = ProjectTask(
            id=uuid.uuid4(),
            project_id=proj.id,
            employee_id=emp1.id,
            title="Implement AI Chat fallback inside sourcing page",
            description="If no profiles exist in MongoDB cache, fallback to live scraping synchronously.",
            column="Done",
            status="Completed",
            due_date=date.today() - timedelta(days=1),
            company_id=company_id,
        )
        task2 = ProjectTask(
            id=uuid.uuid4(),
            project_id=proj.id,
            employee_id=emp2.id,
            title="Optimize celery background web scrapers",
            description="Implement rate-limiting and pagination for LinkedIn/GitHub scraping.",
            column="Development",
            status="In Progress",
            due_date=date.today() + timedelta(days=5),
            company_id=company_id,
        )
        task3 = ProjectTask(
            id=uuid.uuid4(),
            project_id=proj.id,
            employee_id=emp3.id,
            title="Design candidate profile detail view card",
            description="Create clean dashboard layouts for showcasing matched candidate skills.",
            column="Planning",
            status="Pending",
            due_date=date.today() + timedelta(days=12),
            company_id=company_id,
        )
        session.add_all([task1, task2, task3])
        await session.flush()

        # 5. Seed Jobs & Pipeline
        print("\nSeeding Jobs & Hiring Pipeline...")
        # Active Job
        job1 = JobRequirement(
            id=uuid.uuid4(),
            title="Senior Python & FastAPI Developer",
            description="We are seeking an experienced Backend Developer with expert knowledge in Python, FastAPI, Postgres, and Docker. Experience building scalable REST APIs is required.",
            required_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
            experience_min=4,
            experience_max=8,
            location="Remote",
            job_type="Full-time",
            work_mode="Remote",
            department="Engineering",
            salary_min=120000.0,
            salary_max=160000.0,
            salary_currency="USD",
            salary_frequency="Yearly",
            status_id=2,  # Active
            company_id=company_id,
        )
        # Active Job 2
        job2 = JobRequirement(
            id=uuid.uuid4(),
            title="Frontend Engineer (React)",
            description="Join our frontend team. You will lead the development of complex dashboards in Next.js/React using TypeScript and custom design systems.",
            required_skills=["React", "Next.js", "TypeScript", "Tailwind CSS", "JavaScript"],
            experience_min=3,
            experience_max=6,
            location="San Francisco, CA",
            job_type="Full-time",
            work_mode="Hybrid",
            department="Engineering",
            salary_min=100000.0,
            salary_max=130000.0,
            salary_currency="USD",
            salary_frequency="Yearly",
            status_id=2,  # Active
            company_id=company_id,
        )
        # Draft Job
        job3 = JobRequirement(
            id=uuid.uuid4(),
            title="Product Manager (AI Solutions)",
            description="Draft posting for an AI Product Manager to overlook Croar's automation engine features.",
            required_skills=["Product Management", "Agile", "AI/ML", "Roadmapping"],
            experience_min=5,
            experience_max=10,
            location="Remote",
            job_type="Full-time",
            work_mode="Remote",
            department="Product Management",
            salary_min=130000.0,
            salary_max=180000.0,
            salary_currency="USD",
            salary_frequency="Yearly",
            status_id=1,  # Draft
            company_id=company_id,
        )
        session.add_all([job1, job2, job3])
        await session.flush()

        # Seed Pipeline Candidates
        cand1 = Candidate(
            id=uuid.uuid4(),
            full_name="Alice Johnson",
            email="alice.j@example.com",
            phone="+1-555-0199",
            total_experience=5,
            relevant_experience=4,
            skills=["Python", "FastAPI", "SQL", "Docker"],
            source_platform="GitHub",
            company_id=company_id,
        )
        cand2 = Candidate(
            id=uuid.uuid4(),
            full_name="Bob Smith",
            email="bob.smith@example.com",
            phone="+1-555-0144",
            total_experience=3,
            relevant_experience=3,
            skills=["JavaScript", "React", "CSS", "TypeScript"],
            source_platform="LinkedIn",
            company_id=company_id,
        )
        cand3 = Candidate(
            id=uuid.uuid4(),
            full_name="Charlie Brown",
            email="charlie.b@example.com",
            phone="+1-555-0177",
            total_experience=7,
            relevant_experience=5,
            skills=["Python", "Django", "FastAPI", "PostgreSQL", "AWS"],
            source_platform="GitHub",
            company_id=company_id,
        )
        cand4 = Candidate(
            id=uuid.uuid4(),
            full_name="Diana Prince",
            email="diana.prince@example.com",
            phone="+1-555-0122",
            total_experience=6,
            relevant_experience=5,
            skills=["React", "TypeScript", "Tailwind CSS", "HTML5", "Next.js"],
            source_platform="LinkedIn",
            company_id=company_id,
        )
        cand5 = Candidate(
            id=uuid.uuid4(),
            full_name="Evan Wright",
            email="evan.wright@example.com",
            phone="+1-555-0188",
            total_experience=8,
            relevant_experience=6,
            skills=["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD"],
            source_platform="LinkedIn",
            company_id=company_id,
        )
        session.add_all([cand1, cand2, cand3, cand4, cand5])
        await session.flush()

        # Map candidates to applications/pipeline stages
        app1 = CandidateApplication(
            id=uuid.uuid4(),
            candidate_id=cand1.id,
            job_requirement_id=job1.id,
            status_id=1,  # Applied
            ai_match_score=85.5,
            skill_match_percent=80.0,
            experience_fit=90.0,
            ranking_position=2,
            company_id=company_id,
            source="GitHub",
        )
        app2 = CandidateApplication(
            id=uuid.uuid4(),
            candidate_id=cand2.id,
            job_requirement_id=job2.id,
            status_id=2,  # Screening
            ai_match_score=78.2,
            skill_match_percent=75.0,
            experience_fit=80.0,
            ranking_position=4,
            company_id=company_id,
            source="LinkedIn",
        )
        app3 = CandidateApplication(
            id=uuid.uuid4(),
            candidate_id=cand3.id,
            job_requirement_id=job1.id,
            status_id=3,  # Interviewing
            ai_match_score=92.8,
            skill_match_percent=90.0,
            experience_fit=95.0,
            ranking_position=1,
            company_id=company_id,
            source="GitHub",
        )
        app4 = CandidateApplication(
            id=uuid.uuid4(),
            candidate_id=cand4.id,
            job_requirement_id=job2.id,
            status_id=4,  # Offered
            ai_match_score=94.1,
            skill_match_percent=95.0,
            experience_fit=90.0,
            ranking_position=1,
            company_id=company_id,
            source="LinkedIn",
        )
        app5 = CandidateApplication(
            id=uuid.uuid4(),
            candidate_id=cand5.id,
            job_requirement_id=job1.id,
            status_id=5,  # Hired
            ai_match_score=89.4,
            skill_match_percent=85.0,
            experience_fit=90.0,
            ranking_position=3,
            company_id=company_id,
            source="LinkedIn",
        )
        session.add_all([app1, app2, app3, app4, app5])
        await session.flush()

        # 6. Seed Email Templates
        print("\nSeeding Email Templates...")
        welcome_tpl = EmailTemplate(
            id=uuid.uuid4(),
            name="Welcome_Email",
            subject="Welcome to Appxcess! Details inside",
            body="Hi {{candidate_name}},\n\nWelcome to Appxcess! We are excited to evaluate your profile for the {{job_title}} role. Our team will keep you posted on the next steps.",
            category="GENERAL",
            variables=["candidate_name", "job_title"],
            company_id=company_id,
        )
        interview_tpl = EmailTemplate(
            id=uuid.uuid4(),
            name="Interview_Confirmation",
            subject="Interview Schedule - Appxcess Technical Round",
            body="Hi {{candidate_name}},\n\nYour interview for the {{job_title}} role has been scheduled for {{interview_time}}.\n\nJoin link: {{interview_link}}.\n\nBest of luck!",
            category="GENERAL",
            variables=["candidate_name", "job_title", "interview_time", "interview_link"],
            company_id=company_id,
        )
        offer_tpl = EmailTemplate(
            id=uuid.uuid4(),
            name="Offer_Letter",
            subject="Job Offer: {{job_title}} at Appxcess",
            body="Hi {{candidate_name}},\n\nWe are pleased to offer you the position of {{job_title}} at Appxcess! Please review the document and sign via our portal.",
            category="GENERAL",
            variables=["candidate_name", "job_title"],
            company_id=company_id,
        )
        session.add_all([welcome_tpl, interview_tpl, offer_tpl])
        await session.flush()

        # 7. Seed Assessment Templates
        print("\nSeeding Assessment Templates...")
        tech_assessment = AssessmentTemplate(
            id=uuid.uuid4(),
            name="Backend Engineering Technical Quiz",
            type=AssessmentType.BOTH,
            topic="FastAPI, PostgreSQL & Coding Fundamentals",
            question_count=10,
            test_duration=45,
            email_template_id=welcome_tpl.id,
            company_id=company_id,
            generated_questions=[
                {"question": "Explain FastAPI dependency injection.", "type": "text"},
                {"question": "How do you run database migrations in alembic?", "type": "text"},
            ],
        )
        session.add(tech_assessment)
        await session.flush()

        # 8. Seed Onboarding Templates
        print("\nSeeding Onboarding Templates...")
        onb_tpl = OnboardingTemplate(
            id=uuid.uuid4(),
            name="Standard Engineering Onboarding",
            description="Onboarding path for new engineers joining Appxcess.",
            sections=["personal_info", "contact_info", "bank_details", "document_uploads"],
            required_documents=[
                {"name": "Profile Photo", "description": "Recent passport photo", "required": True},
                {"name": "Gov ID Proof", "description": "National identity document copy", "required": True},
            ],
            form_config={
                "sections": [
                    {
                        "id": "personal_info",
                        "title": "Personal Information",
                        "fields": [
                            {"name": "full_name", "label": "Full Name", "type": "text", "required": True},
                            {"name": "dob", "label": "Date of Birth", "type": "date", "required": True},
                        ],
                    }
                ]
            },
            company_id=company_id,
        )
        session.add(onb_tpl)
        await session.flush()

        # 9. Seed Surveys
        print("\nSeeding Surveys...")
        survey_type = SurveyType(
            id=1,  # Uses integer primary key or auto-increment, let's select first if exists
            name="Pulse Survey",
            description="Short, frequent check-ins on morale.",
        )
        # Check if type exists or create
        res = await session.execute(select(SurveyType).where(SurveyType.name == "Pulse Survey"))
        existing_st = res.scalar_one_or_none()
        if not existing_st:
            session.add(survey_type)
            await session.flush()
            survey_type_id = survey_type.id
        else:
            survey_type_id = existing_st.id

        survey = SurveyTemplate(
            id=uuid.uuid4(),
            title="Employee Satisfaction Survey Q2",
            description="Anonymous feedback survey on company culture.",
            survey_type_id=survey_type_id,
            company_id=company_id,
        )
        session.add(survey)
        await session.flush()

        # 10. Seed 360 Assessments
        print("\nSeeding 360 Assessments...")
        x360_q1 = X360Question(
            id=uuid.uuid4(),
            text="How effectively does this employee collaborate with cross-functional team members?",
            category=QuestionCategory.CORE_VALUES,
            type=QuestionType.RATING,
            company_id=company_id,
        )
        x360_q2 = X360Question(
            id=uuid.uuid4(),
            text="Rate this employee's code quality and compliance with backend architectural standards.",
            category=QuestionCategory.PERFORMANCE,
            type=QuestionType.RATING,
            company_id=company_id,
        )
        session.add_all([x360_q1, x360_q2])
        await session.flush()

        x360_tpl = X360AssessmentTemplate(
            id=uuid.uuid4(),
            name="Annual Engineering Review Template",
            description="360 performance evaluation for tech team members.",
            company_id=company_id,
        )
        session.add(x360_tpl)
        await session.flush()

        # Link questions
        link1 = X360TemplateQuestion(template_id=x360_tpl.id, question_id=x360_q1.id, order=1)
        link2 = X360TemplateQuestion(template_id=x360_tpl.id, question_id=x360_q2.id, order=2)
        session.add_all([link1, link2])
        await session.flush()

        # 11. Seed Scenario Architect (Simulations)
        print("\nSeeding Simulation Scenarios...")
        sim_scenario = SimulationScenario(
            id=uuid.uuid4(),
            title="Technical Server Crash Scenario",
            description="Roleplay scenario to evaluate how a backend developer handles client communication during an outage.",
            category="Customer Success & Technical",
            character_name="Jack Miller",
            character_role="VP of Engineering at client firm",
            system_prompt="You are a frustrated client VP. Your production server has been down for 2 hours.",
            initial_message="Where is our dashboard? This outage is costing us thousands of dollars a minute!",
            difficulty="Expert",
            company_id=company_id,
        )
        session.add(sim_scenario)
        await session.flush()

        # 12. Seed Automations
        print("\nSeeding Automations...")
        mail_auto = MailAutomation(
            id=uuid.uuid4(),
            job_requirement_id=job1.id,
            stage_index=1,
            stage_name="Applied",
            criteria="AI Score >= 80",
            template_id=welcome_tpl.id,
            auto_move=True,
            is_enabled=True,
            is_immediate=True,
            company_id=company_id,
        )
        session.add(mail_auto)
        await session.flush()

        await session.commit()
        print("\n=== DATABASE SEEDING COMPLETED SUCCESSFULLY ===")
        print(f"All data has been registered under company ID: {company_id} (Slug: {company.slug})")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(run_seed())
