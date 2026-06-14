import csv
import io
from typing import List
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def generate_csv_report(candidates: List, jd_title: str = "") -> bytes:
    """Generate CSV report for candidates."""
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ResumeIQ — Candidate Report"])
    if jd_title:
        writer.writerow([f"Job: {jd_title}"])
    writer.writerow([])
    writer.writerow([
        "Rank", "Name", "Email", "Phone",
        "Match Score (%)", "Matched Skills", "Missing Skills",
        "Experience (Years)", "Education", "Recommendations"
    ])

    for c in candidates:
        writer.writerow([
            c.rank or "",
            c.name,
            c.email or "",
            c.phone or "",
            c.match_score or "",
            ", ".join(c.matched_skills or []),
            ", ".join(c.missing_skills or []),
            c.experience_years or "",
            ", ".join([e.get("degree", "") for e in (c.education or [])]),
            " | ".join(c.recommendations or [])
        ])

    return output.getvalue().encode("utf-8")


def generate_pdf_report(candidates: List, jd_title: str = "", jd_company: str = "") -> bytes:
    """Generate styled PDF report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#6366f1'),
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'Sub', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#6b7280'), spaceAfter=12
    )

    story.append(Paragraph("ResumeIQ — Candidate Report", title_style))
    if jd_title:
        label = f"Job: {jd_title}" + (f" @ {jd_company}" if jd_company else "")
        story.append(Paragraph(label, sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e5e7eb')))
    story.append(Spacer(1, 12))

    # Summary table
    ranked = sorted([c for c in candidates if c.match_score is not None], key=lambda x: -x.match_score)

    table_data = [["#", "Candidate", "Score", "Matched", "Missing", "Experience"]]
    for i, c in enumerate(ranked):
        table_data.append([
            str(i + 1),
            c.name,
            f"{c.match_score}%",
            str(len(c.matched_skills or [])),
            str(len(c.missing_skills or [])),
            f"{c.experience_years}y" if c.experience_years else "—"
        ])

    t = Table(table_data, colWidths=[0.4*inch, 2.2*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.0*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366f1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    # Detail per candidate
    for i, c in enumerate(ranked[:10]):  # Top 10 detailed
        story.append(Paragraph(f"#{i+1} — {c.name}", ParagraphStyle(
            'CandName', parent=styles['Heading2'],
            fontSize=13, textColor=colors.HexColor('#1f2937'), spaceBefore=10
        )))
        details = [
            ["Match Score", f"{c.match_score}%"],
            ["Email", c.email or "—"],
            ["Experience", f"{c.experience_years} years" if c.experience_years else "—"],
            ["Matched Skills", ", ".join(c.matched_skills[:8] or []) or "—"],
            ["Missing Skills", ", ".join(c.missing_skills[:8] or []) or "—"],
        ]
        dt = Table(details, colWidths=[1.5*inch, 4.5*inch])
        dt.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6366f1')),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(dt)

        if c.recommendations:
            story.append(Spacer(1, 4))
            for rec in c.recommendations:
                story.append(Paragraph(f"• {rec}", ParagraphStyle(
                    'Rec', parent=styles['Normal'],
                    fontSize=8, textColor=colors.HexColor('#6b7280'), leftIndent=10
                )))

        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb')))

    doc.build(story)
    return buffer.getvalue()
