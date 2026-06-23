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


async def add_vibin_employee():
    print("=== ADDING EMPLOYEE: VIBIN KC ===")

    async with db_manager.session() as session:
        # 1. Get Company
        stmt = select(Company).limit(1)
        result = await session.execute(stmt)
        company = result.scalar_one_or_none()

        if not company:
            # Create default company if none exists
            company = Company(id=uuid4(), name="AppXcess", slug="appxcess", industry="Technology")
            session.add(company)
            await session.flush()
            print(f"Created Company: {company.name}")

        # 2. Get Department
        stmt = select(Department).where(Department.company_id == company.id).limit(1)
        result = await session.execute(stmt)
        dept = result.scalar_one_or_none()

        if not dept:
            dept = Department(id=uuid4(), name="Engineering", company_id=company.id)
            session.add(dept)
            await session.flush()
            print(f"Created Department: {dept.name}")

        # 3. Add Employee
        email = "vibi@appxcess.com"
        stmt = select(Employee).where(Employee.email == email)
        result = await session.execute(stmt)
        employee = result.scalar_one_or_none()

        if not employee:
            employee = Employee(
                id=uuid4(),
                employee_id="EXP-VIBIN-001",
                first_name="Vibin",
                last_name="KC",
                email=email,
                designation="CTO & Founder",
                status="Active",
                company_id=company.id,
                department_id=dept.id,
                hire_date=date.today(),
                country="India",
            )
            session.add(employee)
            print(f"Successfully added Employee: {employee.first_name} {employee.last_name}")
        else:
            print(f"Employee with email {email} already exists.")

        await session.commit()
        print("\n=== COMPLETE ===")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(add_vibin_employee())
