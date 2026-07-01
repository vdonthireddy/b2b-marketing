import json
import csv
import io
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from app.services.journey_service import JourneyService
from fastapi import HTTPException


class ExportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.journey_service = JourneyService(db)

    async def export_json(self, journey_id: str, team_id: str) -> dict:
        """Export a journey as a JSON-serializable dict."""
        journey = await self.journey_service.get_journey(journey_id, team_id)

        return {
            "name": journey.name,
            "description": journey.description,
            "status": journey.status.value,
            "exported_at": datetime.utcnow().isoformat(),
            "stages": [
                {
                    "name": s.name,
                    "description": s.description,
                    "icon": s.icon,
                    "color": s.color,
                    "position": s.position,
                    "goals": [{"text": g.text} for g in s.goals],
                    "touchpoints": [{"text": t.text} for t in s.touchpoints],
                    "content": [{"text": c.text, "content_type": c.content_type} for c in s.content],
                }
                for s in sorted(journey.stages, key=lambda x: x.position)
            ],
            "personas": [
                {
                    "name": jp.persona.name,
                    "role_title": jp.persona.role_title,
                    "company_size": jp.persona.company_size,
                    "goals": jp.persona.goals,
                    "pain_points": jp.persona.pain_points,
                }
                for jp in journey.personas
            ],
        }

    async def export_csv(self, journey_id: str, team_id: str) -> str:
        """Export journey stages as CSV."""
        journey = await self.journey_service.get_journey(journey_id, team_id)

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Stage", "Position", "Description",
            "Goals", "Touchpoints", "Content"
        ])

        for stage in sorted(journey.stages, key=lambda s: s.position):
            goals = "; ".join(g.text for g in stage.goals)
            touchpoints = "; ".join(t.text for t in stage.touchpoints)
            content = "; ".join(c.text for c in stage.content)
            writer.writerow([
                stage.name, stage.position, stage.description or "",
                goals, touchpoints, content
            ])

        return output.getvalue()

    async def export_pdf(self, journey_id: str, team_id: str) -> bytes:
        """Export journey as a styled PDF report."""
        journey = await self.journey_service.get_journey(journey_id, team_id)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=40, bottomMargin=40)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("CustomTitle", parent=styles["Title"], fontSize=24, spaceAfter=20)
        heading_style = ParagraphStyle("CustomH2", parent=styles["Heading2"], fontSize=14, spaceAfter=10)
        body_style = styles["Normal"]

        elements = []

        # Title
        elements.append(Paragraph(f"Customer Journey Map: {journey.name}", title_style))
        if journey.description:
            elements.append(Paragraph(journey.description, body_style))
        elements.append(Spacer(1, 20))

        # Stage table
        table_data = [["Stage", "Goals", "Touchpoints", "Content"]]

        for stage in sorted(journey.stages, key=lambda s: s.position):
            goals = "\n".join(f"• {g.text}" for g in stage.goals) or "—"
            touchpoints = "\n".join(f"• {t.text}" for t in stage.touchpoints) or "—"
            content = "\n".join(f"• {c.text}" for c in stage.content) or "—"
            table_data.append([
                Paragraph(f"<b>{stage.icon} {stage.name}</b><br/><font size=8>{stage.description or ''}</font>", body_style),
                Paragraph(goals, body_style),
                Paragraph(touchpoints, body_style),
                Paragraph(content, body_style),
            ])

        col_widths = [2 * inch, 2.5 * inch, 2.5 * inch, 2.5 * inch]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#112240")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#334155")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ]))
        elements.append(table)

        doc.build(elements)
        return buffer.getvalue()

    async def import_json(self, team_id: str, user_id: str, data: dict) -> str:
        """Import a journey from JSON data. Returns the new journey ID."""
        name = data.get("name", "Imported Journey")
        description = data.get("description")

        journey = await self.journey_service.create_journey(
            team_id=team_id, user_id=user_id,
            name=name, description=description,
            include_default_stages=False,
        )

        # Add stages
        for stage_data in data.get("stages", []):
            stage = await self.journey_service.add_stage(
                journey_id=journey.id, team_id=team_id, user_id=user_id,
                name=stage_data.get("name", "Untitled"),
                description=stage_data.get("description"),
                icon=stage_data.get("icon", "📌"),
                color=stage_data.get("color", "#6366f1"),
                position=stage_data.get("position"),
            )

            for goal in stage_data.get("goals", []):
                await self.journey_service.add_stage_item(
                    stage.id, team_id, "goal", goal.get("text", "")
                )
            for tp in stage_data.get("touchpoints", []):
                await self.journey_service.add_stage_item(
                    stage.id, team_id, "touchpoint", tp.get("text", "")
                )
            for ct in stage_data.get("content", []):
                await self.journey_service.add_stage_item(
                    stage.id, team_id, "content", ct.get("text", ""), ct.get("content_type")
                )

        return journey.id
