import asyncio
import os
import sys
from datetime import date
from uuid import uuid4

from sqlalchemy import select

# Ensure the app code is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from app.core.database import db_manager
from app.models.enterprise.company import Company
from app.models.enterprise.employee import Department, Employee


async def seed_employee():
    print("=== SEEDING EMPLOYEE DATA ===")

    async with db_manager.session() as session:
        # 1. Create or Get Company
        company_name = "Test Corp"
        company_slug = "test-corp"
        stmt = select(Company).where(Company.slug == company_slug)
        result = await session.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            company = Company(
                id=uuid4(),
                name=company_name,
                slug=company_slug,
                industry="Technology",
                location="San Francisco, CA",
            )
            session.add(company)
            await session.flush()
            print(f"Created Company: {company.name}")
        else:
            print(f"Company already exists: {company.name}")

        # 2. Create or Get Department
        dept_name = "Engineering"
        stmt = select(Department).where(Department.name == dept_name, Department.company_id == company.id)
        result = await session.execute(stmt)
        dept = result.scalar_one_or_none()

        if not dept:
            dept = Department(
                id=uuid4(), name=dept_name, company_id=company.id, description="Core engineering team"
            )
            session.add(dept)
            await session.flush()
            print(f"Created Department: {dept.name}")
        else:
            print(f"Department already exists: {dept.name}")

        # 3. Create or Get Employee
        email = "john.doe@testcorp.com"
        stmt = select(Employee).where(Employee.email == email)
        result = await session.execute(stmt)
        employee = result.scalar_one_or_none()

        if not employee:
            employee = Employee(
                id=uuid4(),
                employee_id="EMP-001",
                first_name="John",
                last_name="Doe",
                email=email,
                designation="Software Engineer",
                status="Active",
                employment_type="Full-time",
                company_id=company.id,
                department_id=dept.id,
                hire_date=date.today(),
                country="USA",
            )
            session.add(employee)
            print(f"Created Employee: {employee.first_name} {employee.last_name}")
        else:
            print(f"Employee already exists: {employee.email}")

        await session.commit()
        print("\n=== SEEDING COMPLETE ===")
        print(f"Employee Email: {email}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_employee())
