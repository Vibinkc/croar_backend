import asyncio
import os
import sys

sys.path.append(os.getcwd())


from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.employee import Employee
from app.models.enterprise.project import Project


async def seed_project():
    print("Starting seeding script...")
    async with db_manager.session() as session:
        try:
            # 1. Find all employees to debug
            stmt = select(Employee)
            result = await session.execute(stmt)
            all_emps = result.scalars().all()
            print(f"Total employees found: {len(all_emps)}")
            for e in all_emps:
                print(f" - {e.employee_id}: {e.first_name} {e.last_name}")

            # 2. Find the specific employee
            emp = next((e for e in all_emps if "1002" in e.employee_id), None)

            if not emp:
                print("Employee with '1002' in ID not found!")
                return

            print(f"Target employee: {emp.first_name} {emp.last_name} (ID: {emp.id})")

            # 3. Create project
            proj_name = "AI Research & Development"
            project = Project(
                name=proj_name,
                description="Cutting-edge AI research project for enterprise automation.",
                status="Active",
                company_id=emp.company_id,
                # start_date, end_date will be null
            )
            session.add(project)
            await session.flush()
            print(f"Created project: {proj_name}")

            # 4. Map employee to project
            print(f"Mapping {emp.first_name} to project...")
            project.members.append(emp)

            await session.commit()
            print("Successfully seeded and mapped!")
        except Exception as e:
            print(f"ERROR: {e!s}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(seed_project())
