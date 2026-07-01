import asyncio
import random
import uuid
from sqlalchemy import select
from app.database import AsyncSessionLocal, engine
from app.models.lead import Lead
from app.models.journey import Journey, JourneyStatus
from app.models.stage import Stage
from app.models.persona import Persona, JourneyPersona
from app.models.user import User, Team
from app.services.journey_service import DEFAULT_STAGES

FIRST_NAMES = [
    "John", "Jane", "Robert", "Michael", "Sarah", "David", "Emily", "James", "Maria", "William",
    "Oliver", "Sophia", "Daniel", "Isabella", "Lucas", "Mia", "Alexander", "Charlotte", "Ethan", "Amelia"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Wilson",
    "Martinez", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White"
]

COMPANIES = [
    "Acme Corp", "Globex Corporation", "Initech LLC", "Umbrella Corp", "Stark Industries", 
    "Wayne Enterprises", "Hooli", "Pied Piper", "Soylent Corp", "Tyrell Corp",
    "Vehement Capital", "Massive Dynamic", "Cyberdyne Systems", "Aperture Science", "Wonka Industries"
]

JOB_TITLES = [
    "VP of Marketing", "CTO", "Product Manager", "Director of Sales", "Head of Growth", 
    "Chief Executive Officer", "Software Engineer", "Operations Lead", "VP of Engineering", "Marketing Specialist"
]

STATUSES = ["new", "contacted", "qualified", "nurturing", "converted", "closed_lost"]


async def seed_leads():
    async with AsyncSessionLocal() as session:
        # Check if we have an admin user & team
        user_result = await session.execute(select(User).limit(1))
        user = user_result.scalar_one_or_none()
        
        if not user:
            # Create a default team
            team = Team(name="Acme Marketing Team", slug="acme-marketing")
            session.add(team)
            await session.flush()
            
            # Create default admin user
            user = User(
                email="admin",
                password_hash="$2b$12$qJpDWdiMeeyGR2q1EN4IC.HG/SyzZ2eJgV5p4JpeaLnrj6q3Ujpva", # hashed "admin"
                name="Admin User",
                role="admin",
                team_id=team.id
            )
            session.add(user)
            await session.flush()
        else:
            team_result = await session.execute(select(Team).where(Team.id == user.team_id))
            team = team_result.scalar_one()

        # Check if we have any journeys
        journey_result = await session.execute(select(Journey).where(Journey.team_id == team.id))
        journeys = journey_result.scalars().all()

        if not journeys:
            # Create a default B2B SaaS journey
            journey = Journey(
                team_id=team.id,
                name="B2B SaaS Growth Journey",
                description="Standard marketing/sales pipeline stages for B2B SaaS expansion.",
                status=JourneyStatus.ACTIVE,
                created_by=user.id
            )
            session.add(journey)
            await session.flush()

            # Create default stages
            stages = []
            for i, stage_data in enumerate(DEFAULT_STAGES):
                stage = Stage(
                    journey_id=journey.id,
                    name=stage_data["name"],
                    description=stage_data["description"],
                    icon=stage_data["icon"],
                    color=stage_data["color"],
                    position=i,
                )
                session.add(stage)
                stages.append(stage)
            await session.flush()
            
            # Create a default persona
            persona = Persona(
                team_id=team.id,
                name="Enterprise Tech Buyer",
                role_title="CIO / VP of IT",
                company_size="Enterprise",
                goals="Streamline operations, reduce vendor risk, improve scale.",
                pain_points="Fragmented software stack, high cost of integration.",
                motivations="Efficiency, reliability, security.",
                created_by=user.id
            )
            session.add(persona)
            await session.flush()
            
            # Link persona to journey
            jp = JourneyPersona(journey_id=journey.id, persona_id=persona.id)
            session.add(jp)
            await session.flush()
            
            journeys = [journey]
        else:
            journey = journeys[0]
            # Fetch stages
            stages_result = await session.execute(
                select(Stage).where(Stage.journey_id == journey.id).order_by(Stage.position)
            )
            stages = stages_result.scalars().all()
            
            # Fetch personas
            persona_result = await session.execute(select(Persona).where(Persona.team_id == team.id))
            personas = persona_result.scalars().all()
            if not personas:
                persona = Persona(
                    team_id=team.id,
                    name="Default Persona",
                    created_by=user.id
                )
                session.add(persona)
                await session.flush()
                personas = [persona]
            else:
                persona = personas[0]

        # Generate 100+ leads
        leads_count = 110
        print(f"Generating {leads_count} leads for journey: '{journey.name}'")
        
        for i in range(leads_count):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            company = random.choice(COMPANIES)
            job_title = random.choice(JOB_TITLES)
            status_val = random.choice(STATUSES)
            value = round(random.uniform(5000.0, 150000.0), 2)
            
            # Email address based on name and company
            email_domain = company.lower().replace(" ", "").replace(",", "") + ".com"
            email = f"{first_name.lower()}.{last_name.lower()}@{email_domain}"
            
            # Select random stage (if stages exist)
            stage = random.choice(stages) if stages else None
            stage_id = stage.id if stage else None
            
            lead = Lead(
                first_name=first_name,
                last_name=last_name,
                email=email,
                company=company,
                job_title=job_title,
                status=status_val,
                value=value,
                journey_id=journey.id,
                stage_id=stage_id,
                persona_id=persona.id if persona else None
            )
            session.add(lead)
        
        await session.commit()
        print(f"Successfully seeded {leads_count} leads!")


if __name__ == "__main__":
    asyncio.run(seed_leads())
