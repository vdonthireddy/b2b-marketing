import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.journey import Journey


async def deduplicate():
    async with AsyncSessionLocal() as session:
        # Fetch all journeys ordered by creation time
        result = await session.execute(select(Journey).order_by(Journey.created_at))
        journeys = result.scalars().all()
        
        seen = {}
        for j in journeys:
            if j.name in seen:
                seen[j.name] += 1
                new_name = f"{j.name} {seen[j.name]}"
                print(f"Renaming duplicate journey ID {j.id}: '{j.name}' -> '{new_name}'")
                j.name = new_name
            else:
                seen[j.name] = 1
                
        await session.commit()
        print("Deduplication completed successfully!")


if __name__ == "__main__":
    asyncio.run(deduplicate())
