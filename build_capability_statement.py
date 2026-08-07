from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

# ---- Palette ----
INK = colors.HexColor("#1A2233")       # near-black navy for headers
SLATE = colors.HexColor("#4A5568")     # body text
ACCENT = colors.HexColor("#2C5F5C")    # muted teal accent (professional, not flashy)
RULE = colors.HexColor("#D6DCE1")      # hairline gray

doc = SimpleDocTemplate(
    "capability-statement.pdf",
    pagesize=letter,
    topMargin=0.55 * inch,
    bottomMargin=0.5 * inch,
    leftMargin=0.6 * inch,
    rightMargin=0.6 * inch,
)

styles = {
    "company": ParagraphStyle("company", fontName="Helvetica-Bold", fontSize=22, textColor=INK, leading=24),
    "tagline": ParagraphStyle("tagline", fontName="Helvetica", fontSize=10.5, textColor=SLATE, leading=14, spaceAfter=0),
    "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=11, textColor=ACCENT, spaceBefore=12, spaceAfter=6, leading=13, tracking=0.5),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.3, textColor=SLATE, leading=13),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.3, textColor=SLATE, leading=13, leftIndent=10),
    "projName": ParagraphStyle("projName", fontName="Helvetica-Bold", fontSize=9.6, textColor=INK, leading=12),
    "projMeta": ParagraphStyle("projMeta", fontName="Helvetica-Oblique", fontSize=8.6, textColor=ACCENT, leading=11, spaceAfter=2),
    "projBody": ParagraphStyle("projBody", fontName="Helvetica", fontSize=9.1, textColor=SLATE, leading=12.5, spaceAfter=8),
    "dataLabel": ParagraphStyle("dataLabel", fontName="Helvetica-Bold", fontSize=8.3, textColor=INK, leading=11),
    "dataValue": ParagraphStyle("dataValue", fontName="Helvetica", fontSize=8.3, textColor=SLATE, leading=11),
    "footer": ParagraphStyle("footer", fontName="Helvetica", fontSize=8.3, textColor=SLATE, leading=11),
    "stackCat": ParagraphStyle("stackCat", fontName="Helvetica-Bold", fontSize=8.4, textColor=INK, leading=12),
    "stackVal": ParagraphStyle("stackVal", fontName="Helvetica", fontSize=8.4, textColor=SLATE, leading=12),
}

story = []

# ---- Header ----
header_table = Table(
    [[
        Table(
            [[Paragraph("NOPSTER, INC.", styles["company"])],
             [Paragraph("Full-stack software development and systems integration &mdash; from custom "
                        "applications to the pipelines and APIs that connect them.", styles["tagline"])]],
            colWidths=[4.6 * inch],
        ),
        Table(
            [
                [Paragraph("UEI", styles["dataLabel"]), Paragraph("LHCRNLE7ZE79", styles["dataValue"])],
                [Paragraph("CAGE Code", styles["dataLabel"]), Paragraph("Pending", styles["dataValue"])],
                [Paragraph("NAICS", styles["dataLabel"]), Paragraph("541511 &mdash; Custom Computer Programming Services", styles["dataValue"])],
                [Paragraph("PSC", styles["dataLabel"]), Paragraph("DA01 &mdash; Application Development Support Services", styles["dataValue"])],
                [Paragraph("Business Type", styles["dataLabel"]), Paragraph("Small Business", styles["dataValue"])],
            ],
            colWidths=[0.85 * inch, 2.35 * inch],
            style=TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ]),
        ),
    ]],
    colWidths=[4.6 * inch, 3.2 * inch],
)
header_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]))
story.append(header_table)
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=1.4, color=ACCENT, spaceAfter=2))
story.append(Spacer(1, 6))

# ---- Core Competencies ----
story.append(Paragraph("CORE COMPETENCIES", styles["section"]))
competencies = [
    "Custom full-stack web and mobile application development",
    "Systems integration &amp; API development &mdash; connecting existing systems, data sources, and third-party services",
    "Microservices &amp; RESTful / GraphQL API architecture",
    "Cloud infrastructure &amp; deployment automation",
    "CI/CD pipeline design and implementation",
    "Ongoing maintenance, support, and feature development for production systems",
]
for c in competencies:
    story.append(Paragraph(f"&bull;&nbsp;&nbsp;{c}", styles["bullet"]))

story.append(Spacer(1, 6))

# ---- Technical Stack ----
story.append(Paragraph("TECHNICAL STACK", styles["section"]))
stack_rows = [
    ("Languages", "JavaScript, TypeScript, Java, C#, PHP, Python"),
    ("Front-End", "React, Next.js, Ember.js, Angular 2+, HTML5, CSS3, Sass, Bootstrap"),
    ("Back-End", "Node.js, Express.js, Nest.js, Java Spring Boot, REST, GraphQL, Microservices"),
    ("Databases", "MongoDB, MySQL, PostgreSQL, SQLite, SQL Server"),
    ("Cloud", "AWS (EC2, S3, Lambda, RDS), Google Cloud Platform (GKE, Pub/Sub), DigitalOcean"),
    ("CI/CD", "GitHub Actions, GitLab CI, Terraform, Docker, Kubernetes"),
]
stack_table_data = [[Paragraph(cat, styles["stackCat"]), Paragraph(val, styles["stackVal"])] for cat, val in stack_rows]
stack_table = Table(stack_table_data, colWidths=[0.95 * inch, 6.85 * inch])
stack_table.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 2.5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
]))
story.append(stack_table)

story.append(Spacer(1, 6))

# ---- Past Performance ----
story.append(Paragraph("PAST PERFORMANCE", styles["section"]))

projects = [
    ("Wise Education Systems, Inc.", "Online Proctoring Platform",
     "Developed new front-end and back-end features for a production online proctoring application. "
     "Built and maintained systems on an ongoing basis, with continued engagement for support and issue resolution.",
     "Node.js, Koa, MongoDB, React, Google Cloud Platform"),
    ("Keepsee", "Mobile Video-Sharing Application",
     "Built new features for a mobile application enabling users to record and share video experiences with "
     "family and friends.",
     "React Native (iOS), Firebase, Google Cloud Platform"),
    ("Stakt Commissions", "Commission Automation Platform",
     "Built third-party integrations, backend services, front-end interface, and CI/CD deployment pipeline for "
     "a platform automating commission calculations and payouts.",
     "Full-stack development, CI/CD, DigitalOcean"),
]

for name, title, desc, stack in projects:
    story.append(Paragraph(f"{title}", styles["projName"]))
    story.append(Paragraph(f"{name} &nbsp;|&nbsp; {stack}", styles["projMeta"]))
    story.append(Paragraph(desc, styles["projBody"]))

story.append(HRFlowable(width="100%", thickness=0.7, color=RULE, spaceAfter=6))

# ---- Footer / Contact ----
footer_table = Table(
    [[
        Paragraph("<b>Daniel Nop</b>, President &nbsp;|&nbsp; dan@nopster.dev &nbsp;|&nbsp; nopster.dev", styles["footer"]),
        Paragraph("Atlanta, GA &nbsp;|&nbsp; State of Incorporation: Georgia", styles["footer"]),
    ]],
    colWidths=[4.6 * inch, 3.2 * inch],
)
story.append(footer_table)

doc.build(story)
print("PDF built.")
