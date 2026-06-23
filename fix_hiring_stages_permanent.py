import asyncio

from sqlalchemy import select

from app.core.database import db_manager
from app.models.enterprise.candidate import CandidateApplication
from app.models.enterprise.job import JobRequirement


async def fix_jobs_and_apps():
    async with db_manager.session() as session:
        # 1. Fetch all jobs with workflow_stages
        stmt = select(JobRequirement).where(JobRequirement.workflow_stages is not None)
        result = await session.execute(stmt)
        jobs = result.scalars().all()

        print(f"Checking {len(jobs)} jobs for stage ID mismatches...")

        for job in jobs:
            print(f"Processing Job: {job.title} ({job.id})")
            stages = job.workflow_stages
            if not stages:
                continue

            # Create a mapping of old_id -> new_id
            mapping = {}
            needs_fix = False

            new_stages = []
            for i, stage in enumerate(stages):
                old_id = str(stage.get("id"))
                new_id = str(i + 1)

                if old_id != new_id:
                    needs_fix = True

                mapping[old_id] = new_id

                # Update stage in place or create new list
                new_stage = dict(stage)
                new_stage["id"] = new_id
                new_stages.append(new_stage)

            if needs_fix:
                print(f"Fixing Job: {job.title} (ID: {job.id})")
                print(f"  Old IDs: {[s.get('id') for s in stages]}")
                print(f"  New IDs: {[s.get('id') for s in new_stages]}")
                # Update Job
                job.workflow_stages = new_stages

            # ALWAYS Update Applications for this job (to cap stages)
            app_stmt = select(CandidateApplication).where(CandidateApplication.job_requirement_id == job.id)
            app_res = await session.execute(app_stmt)
            apps = app_res.scalars().all()

            max_stage_idx = len(new_stages)

            for app in apps:
                old_curr = str(app.current_stage)
                new_curr = app.current_stage

                # Apply mapping if exists
                if old_curr in mapping:
                    new_curr = int(mapping[old_curr])

                # CAP existing stages to the max defined for this job
                if new_curr > max_stage_idx:
                    print(f"    Capping App {app.id}: {new_curr} -> {max_stage_idx}")
                    new_curr = max_stage_idx

                if app.current_stage != new_curr:
                    print(f"    Updating App {app.id}: {app.current_stage} -> {new_curr}")
                    app.current_stage = new_curr

            await session.flush()

        await session.commit()
        print("Done fixing jobs and applications.")


if __name__ == "__main__":
    asyncio.run(fix_jobs_and_apps())
