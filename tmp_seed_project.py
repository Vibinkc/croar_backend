import asyncio
import os
import sys

# Add the backend directory to the sys.path
sys.path.append(os.getcwd())


from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.employee import Employee
from app.models.enterprise.project import Project


async def seed_project():
    async with db_manager.session() as session:
        # 1. Find the employee
        stmt = select(Employee).where(Employee.employee_id.ilike("%1002%"))
        result = await session.execute(stmt)
        emp = result.scalars().first()

        if not emp:
            print("Employee EMP-1002 not found!")
            return

        print(f"Found employee: {emp.first_name} {emp.last_name} (ID: {emp.id})")

        # 2. Check if project already exists
        proj_name = "Cloud Migration 2026"
        stmt = select(Project).where(Project.name == proj_name, Project.company_id == emp.company_id)
        result = await session.execute(stmt)
        project = result.scalars().first()

        if not project:
            print(f"Creating project: {proj_name}")
            project = Project(
                name=proj_name,
                description="Global cloud infrastructure migration to AWS.",
                status="Active",
                company_id=emp.company_id,
                # start_date, end_date will be null or can be added
            )
            session.add(project)
            await session.flush()
        else:
            print(f"Project '{proj_name}' already exists.")

        # 3. Map employee to project
        if emp not in project.members:
            print(f"Adding {emp.first_name} to project.")
            project.members.append(emp)
        else:
            print("Employee already in project.")

        await session.commit()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(seed_project())
