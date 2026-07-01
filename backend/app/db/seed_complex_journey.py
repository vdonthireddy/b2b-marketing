import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.journey import Journey, JourneyStatus
from app.models.stage import Stage, StageGoal, StageTouchpoint, StageContent
from app.models.user import User, Team


async def seed_complex_journey():
    async with AsyncSessionLocal() as session:
        # Get admin user & team
        user_result = await session.execute(select(User).limit(1))
        user = user_result.scalar_one_or_none()
        
        if not user:
            print("Error: No admin user found. Please run seed_leads first.")
            return

        team_result = await session.execute(select(Team).where(Team.id == user.team_id))
        team = team_result.scalar_one()

        # Create complex journey
        journey = Journey(
            team_id=team.id,
            name="Enterprise Lead Nurturing Flow",
            description="Advanced customer journey map featuring automated sales qualification, decision split nodes, and retargeting wait paths.",
            status=JourneyStatus.ACTIVE,
            created_by=user.id
        )
        session.add(journey)
        await session.flush()

        # Define 9 stages representing the complex path
        stages_data = [
            {
                "name": "Awareness",
                "icon": "👁️",
                "color": "#6366f1",
                "position": 0,
                "description": "Prospect visits website or reads blog content",
                "goals": ["Increase organic traffic", "Brand recognition"],
                "touchpoints": ["Google Search", "LinkedIn Ads"],
                "content": ["Blog Post: B2B Growth", "Infographics"]
            },
            {
                "name": "Engagement",
                "icon": "💬",
                "color": "#8b5cf6",
                "position": 1,
                "description": "Prospect registers for a webinar or downloads whitepaper",
                "goals": ["Collect contact details", "Warm lead nurturing"],
                "touchpoints": ["Webinar Landing Page", "Email newsletter"],
                "content": ["Whitepaper: State of Marketing", "Webinar: Enterprise Scaling"]
            },
            {
                "name": "Split: Demo Requested?",
                "icon": "🔶",
                "color": "#f59e0b",
                "position": 2,
                "description": "System check: Did the prospect request a live product demo?",
                "goals": ["Segment lead paths"],
                "touchpoints": ["CRM Automation"],
                "content": ["Form submission webhook"]
            },
            {
                "name": "[Branch A] Discovery Call",
                "icon": "📞",
                "color": "#10b981",
                "position": 3,
                "description": "Sales representative schedules a discovery and qualification call",
                "goals": ["Qualify B2B prospect size", "Identify core pain points"],
                "touchpoints": ["Calendly link", "Phone Call"],
                "content": ["Sales Playbook", "Qualification Script"]
            },
            {
                "name": "[Branch A] Proposal Presentation",
                "icon": "📄",
                "color": "#06b6d4",
                "position": 4,
                "description": "Present customized enterprise platform proposal and pricing",
                "goals": ["Obtain technical buy-in", "Approve contract draft"],
                "touchpoints": ["Zoom Presentation", "PDF proposal document"],
                "content": ["Pricing Deck", "Case Studies"]
            },
            {
                "name": "[Branch B] Wait 7 Days",
                "icon": "⏳",
                "color": "#64748b",
                "position": 5,
                "description": "Cool down period before sending follow-up resource",
                "goals": ["Prevent email fatigue"],
                "touchpoints": ["Delay timer"],
                "content": ["Wait state config"]
            },
            {
                "name": "[Branch B] Nurturing Email",
                "icon": "📧",
                "color": "#a855f7",
                "position": 6,
                "description": "Send automated case study and client testimonial email",
                "goals": ["Re-engage cold lead", "Build social proof"],
                "touchpoints": ["HubSpot campaign"],
                "content": ["Customer Testimonial email", "Product Video demo"]
            },
            {
                "name": "Conversion",
                "icon": "💰",
                "color": "#00d4aa",
                "position": 7,
                "description": "Prospect signs the enterprise contract and finishes onboarding",
                "goals": ["Signed contract", "Successful kick-off call"],
                "touchpoints": ["DocuSign contract email", "Onboarding Portal"],
                "content": ["Service Level Agreement", "Welcome Kit"]
            },
            {
                "name": "Customer Advocacy",
                "icon": "❤️",
                "color": "#ec4899",
                "position": 8,
                "description": "Customer participates in case study or refers another lead",
                "goals": ["Obtain testimonial", "Receive referral"],
                "touchpoints": ["NPS survey email", "Referral program page"],
                "content": ["Case Study draft", "Loyalty program discount"]
            }
        ]

        # Insert stages and nested items
        for s_data in stages_data:
            stage = Stage(
                journey_id=journey.id,
                name=s_data["name"],
                description=s_data["description"],
                icon=s_data["icon"],
                color=s_data["color"],
                position=s_data["position"],
            )
            session.add(stage)
            await session.flush()

            # Insert goals
            for idx, goal_text in enumerate(s_data["goals"]):
                goal = StageGoal(stage_id=stage.id, text=goal_text, position=idx)
                session.add(goal)

            # Insert touchpoints
            for idx, tp_text in enumerate(s_data["touchpoints"]):
                tp = StageTouchpoint(stage_id=stage.id, text=tp_text, position=idx)
                session.add(tp)

            # Insert content
            for idx, c_text in enumerate(s_data["content"]):
                content = StageContent(stage_id=stage.id, text=c_text, content_type="general", position=idx)
                session.add(content)

        await session.commit()
        print(f"Successfully seeded complex journey: '{journey.name}'!")


if __name__ == "__main__":
    asyncio.run(seed_complex_journey())
