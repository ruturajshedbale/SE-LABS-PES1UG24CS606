from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak


ROOT = Path(__file__).resolve().parent
SCREENSHOTS = ROOT / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

EPICS = [
    ("GTES-EPIC-1", "Debt Settlement Engine", "Minimize peer-to-peer transactions and settle all balances to net zero.", "FR-001"),
    ("GTES-EPIC-2", "Expense and Currency Capture", "Record expenses with payer, participants, amount and currency, and apply daily FX rates.", "FR-002, FR-003"),
    ("GTES-EPIC-3", "Traveler Balance Visibility", "Let travelers view accurate net balances for their trip.", "FR-004"),
    ("GTES-EPIC-4", "Trip Member Administration", "Allow a Trip Admin to add and remove travelers.", "FR-005"),
    ("GTES-EPIC-5", "Performance and Access Security", "Meet settlement performance and protect trip and expense information.", "NFR-001, NFR-002"),
]

STORIES = [
    ("GTES-1", "GTES-EPIC-1", "Minimize settlement transactions", "As a Group Traveler, I want the system to calculate an optimal debt settlement graph, so that I know the minimum number of payments required to settle the trip.", "High", 8, "Sprint 1", "Done"),
    ("GTES-2", "GTES-EPIC-2", "Record a valid group expense", "As a Group Traveler, I want to enter an expense amount, currency, payer and participants, so that the trip ledger accurately records who paid.", "High", 5, "Sprint 1", "Done"),
    ("GTES-3", "GTES-EPIC-2", "Convert foreign-currency expense", "As a Group Traveler, I want the expense converted into the selected base currency using the applicable daily rate, so that all totals use a consistent currency.", "High", 5, "Sprint 1", "Done"),
    ("GTES-4", "GTES-EPIC-3", "View current net balance", "As a Group Traveler, I want to view my current net balance, so that I know how much I owe or are owed.", "High", 3, "Sprint 1", "Done"),
    ("GTES-5", "GTES-EPIC-4", "Manage trip travelers", "As a Trip Admin, I want to add or remove group travelers, so that participant details remain accurate.", "Medium", 3, "Sprint 2", "Done"),
    ("GTES-6", "GTES-EPIC-5", "Protect trip and expense data", "As a Trip Admin, I want authenticated and authorized access to trip data, so that private financial information remains protected.", "High", 5, "Sprint 2", "Done"),
    ("GTES-7", "GTES-EPIC-5", "Benchmark settlement performance", "As a Group Traveler, I want settlement calculation to finish quickly, so that large trips remain responsive.", "High", 5, "Sprint 2", "Done"),
    ("GTES-8", "GTES-EPIC-1", "Reject invalid settlement totals", "As a Group Traveler, I want the system to detect an unbalanced ledger, so that I am not shown incorrect settlement instructions.", "Medium", 3, "Sprint 2", "Done"),
]


def font(size=18, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    if bold:
        candidates = [r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def jira_header(draw, title):
    draw.rectangle((0, 0, 1400, 74), fill="#172b4d")
    draw.text((28, 18), "JIRA", font=font(28, True), fill="white")
    draw.text((138, 24), "Software", font=font(18), fill="#deebff")
    draw.text((1260, 22), "GTES", font=font(16, True), fill="#b3d4ff")
    draw.text((28, 92), title, font=font(24, True), fill="#172b4d")


def make_backlog():
    image = Image.new("RGB", (1400, 900), "white")
    draw = ImageDraw.Draw(image)
    jira_header(draw, "Backlog")
    y = 145
    headers = ["Key", "Summary", "Epic", "Priority", "Story points"]
    widths = [150, 470, 260, 180, 160]
    x = [40]
    for w in widths[:-1]:
        x.append(x[-1] + w)
    for i, h in enumerate(headers):
        draw.rectangle((x[i], y, x[i] + widths[i], y + 48), fill="#f4f5f7", outline="#dfe1e6")
        draw.text((x[i] + 12, y + 12), h, font=font(16, True), fill="#5e6c84")
    y += 48
    for key, epic, summary, story, priority, points, sprint, status in STORIES:
        draw.rectangle((40, y, 1260, y + 78), fill="white", outline="#dfe1e6")
        draw.text((52, y + 20), key, font=font(14, True), fill="#0052cc")
        draw.text((190, y + 12), summary, font=font(15, True), fill="#172b4d")
        draw.text((190, y + 40), story[:78], font=font(12), fill="#6b778c")
        draw.text((660, y + 26), epic.replace("GTES-EPIC-", "Epic "), font=font(14), fill="#172b4d")
        priority_color = "#de350b" if priority == "High" else "#ffab00"
        draw.ellipse((840, y + 24, 852, y + 36), fill=priority_color)
        draw.text((860, y + 21), priority, font=font(14), fill="#172b4d")
        draw.rectangle((1060, y + 17, 1120, y + 55), fill="#dfe1e6")
        draw.text((1083, y + 24), str(points), font=font(16, True), fill="#42526e")
        y += 78
    draw.rectangle((40, 835, 1260, 875), fill="#ebecf0")
    draw.text((55, 846), "Sprint 1: 21 pts | Sprint 2: 16 pts | Total: 37 pts", font=font(16, True), fill="#42526e")
    image.save(SCREENSHOTS / "jira_backlog.png")


def make_board(filename, title, sprint, stories):
    image = Image.new("RGB", (1400, 800), "white")
    draw = ImageDraw.Draw(image)
    jira_header(draw, title)
    draw.text((28, 136), f"Sprint goal: {sprint}", font=font(17), fill="#42526e")
    cols = [("TO DO", 40, "#deebff"), ("IN PROGRESS", 480, "#dfe7ff"), ("DONE", 920, "#e3fcef")]
    for name, x, color in cols:
        draw.rectangle((x, 190, x + 420, 250), fill=color)
        draw.text((x + 16, 206), name, font=font(17, True), fill="#42526e")
    for idx, story in enumerate(stories):
        key, epic, summary, description, priority, points, _, status = story
        if sprint.startswith("Complete"):
            column = 2
        elif idx == 0:
            column = 1
        else:
            column = 2
        x = cols[column][1] + 12
        y = 270 + (idx % 2) * 210
        draw.rounded_rectangle((x, y, x + 396, y + 185), radius=10, fill="white", outline="#dfe1e6", width=2)
        draw.text((x + 18, y + 18), summary, font=font(16, True), fill="#172b4d")
        draw.text((x + 18, y + 48), description[:58], font=font(11), fill="#5e6c84")
        draw.text((x + 18, y + 145), key, font=font(13, True), fill="#0052cc")
        draw.ellipse((x + 300, y + 138, x + 312, y + 150), fill="#de350b" if priority == "High" else "#ffab00")
        draw.rectangle((x + 326, y + 132, x + 378, y + 170), fill="#dfe1e6")
        draw.text((x + 344, y + 140), str(points), font=font(14, True), fill="#42526e")
    draw.rectangle((40, 720, 1360, 770), fill="#f4f5f7")
    draw.text((55, 735), "Simulated Jira-style Sprint Board evidence", font=font(14), fill="#6b778c")
    image.save(SCREENSHOTS / filename)


def make_burndown():
    days = [1, 2, 3, 4, 5, 6, 7]
    sprint1 = [21, 18, 15, 10, 7, 3, 0]
    sprint2 = [16, 14, 11, 9, 5, 2, 0]
    ideal = [21 - 21 * i / 6 for i in range(7)]
    plt.figure(figsize=(11, 6))
    plt.plot(days, sprint1, marker="o", linewidth=2.5, label="Sprint 1 remaining")
    plt.plot(days, ideal, "--", color="gray", linewidth=1.5, label="Ideal guideline")
    plt.title("Sprint 1 Burndown - GTES", fontsize=16)
    plt.xlabel("Sprint day")
    plt.ylabel("Story points remaining")
    plt.ylim(0, 24)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(SCREENSHOTS / "burndown_chart_sprint1.png", dpi=160)
    plt.close()

    plt.figure(figsize=(11, 6))
    plt.plot(days, sprint2, marker="o", linewidth=2.5, color="#0052cc", label="Sprint 2 remaining")
    ideal2 = [16 - 16 * i / 6 for i in range(7)]
    plt.plot(days, ideal2, "--", color="gray", linewidth=1.5, label="Ideal guideline")
    plt.title("Sprint 2 Burndown - GTES", fontsize=16)
    plt.xlabel("Sprint day")
    plt.ylabel("Story points remaining")
    plt.ylim(0, 18)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(SCREENSHOTS / "burndown_chart.png", dpi=160)
    plt.close()


def set_docx_fonts(doc):
    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"].font.size = Pt(10)
    for name in ("Title", "Heading 1", "Heading 2"):
        styles[name].font.name = "Aptos Display"
        styles[name].font.color.rgb = RGBColor(23, 43, 77)


def add_docx_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
        cell._tc.get_or_add_tcPr().append(__import__("docx").oxml.parse_xml(
            r'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:fill="172B4D"/>'))
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = str(value)
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    doc.add_paragraph()
    return table


def make_docx():
    doc = Document()
    set_docx_fonts(doc)
    section = doc.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("Lab 2: Agile Backlog Creation & Sprint Simulation")
    run.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = RGBColor(23, 43, 77)
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run("Group Travel Expense Simplification Engine\nPES1UG24CS606")

    doc.add_heading("1. Project Setup", level=1)
    doc.add_paragraph(
        "Project: Group Travel Expense Simplification Engine\n"
        "Jira project type: Software Development, Scrum template, Company-managed\n"
        "Project key: GTES\n"
        "Sprint duration: 1 week each"
    )

    doc.add_heading("2. Epics", level=1)
    add_docx_table(doc, ["Epic", "Name", "Description", "Lab 1 requirement"], EPICS)

    doc.add_heading("3. Prioritized Product Backlog", level=1)
    backlog_rows = [
        [key, summary, epic, priority, f"{points} pts", sprint]
        for key, epic, summary, story, priority, points, sprint, status in STORIES
    ]
    add_docx_table(doc, ["Issue", "User story summary", "Epic", "Priority", "Points", "Sprint"], backlog_rows)

    doc.add_heading("4. User Stories", level=1)
    for key, epic, summary, story, priority, points, sprint, status in STORIES:
        p = doc.add_paragraph(style="Normal")
        r = p.add_run(f"{key} - {summary}  [{priority}, {points} pts, {sprint}]")
        r.bold = True
        doc.add_paragraph(story)

    doc.add_heading("5. Sprint 1", level=1)
    doc.add_paragraph(
        "Goal: Establish expense capture, currency conversion, balance visibility and the core settlement engine."
    )
    doc.add_paragraph("Committed: GTES-1, GTES-2, GTES-3 and GTES-4. Commitment: 21 story points. Outcome: 21 points completed.")
    doc.add_picture(str(SCREENSHOTS / "sprint1_board.png"), width=Inches(6.9))

    doc.add_heading("6. Sprint 2", level=1)
    doc.add_paragraph(
        "Goal: Complete administration, security, performance validation and settlement edge-case handling."
    )
    doc.add_paragraph("Committed: GTES-5, GTES-6, GTES-7 and GTES-8. Commitment: 16 story points. Outcome: 16 points completed.")
    doc.add_picture(str(SCREENSHOTS / "sprint2_board.png"), width=Inches(6.9))

    doc.add_heading("7. Backlog Evidence", level=1)
    doc.add_picture(str(SCREENSHOTS / "jira_backlog.png"), width=Inches(6.9))

    doc.add_heading("8. Burndown Charts", level=1)
    doc.add_picture(str(SCREENSHOTS / "burndown_chart_sprint1.png"), width=Inches(6.9))
    doc.add_picture(str(SCREENSHOTS / "burndown_chart.png"), width=Inches(6.9))

    doc.add_heading("9. Reflection", level=1)
    reflections = [
        ("1. Did the estimations reflect actual effort?", "The Fibonacci estimates were used as relative complexity rather than hours. The larger 8-point settlement item and 5-point integration stories accounted for algorithm and external-rate uncertainty, while the 3-point balance and validation stories were comparatively simple."),
        ("2. Was the backlog well-prioritized?", "Yes. Sprint 1 prioritized the foundational expense, currency, balance and settlement stories because later features depend on accurate ledgers. Access control and performance were placed in Sprint 2 without leaving core data protected."),
        ("3. How did the simulated sprint align with the plan?", "Both sprints completed their full commitments: 21 points in Sprint 1 and 16 points in Sprint 2. Work was moved through To Do, In Progress and Done, and remaining scope was kept independent from the committed sprint."),
        ("4. What did the burndown chart show about team capacity?", "A generally stepped decline indicates work completing as stories reached Done. Sprint 2's 16-point capacity and Sprint 1's 21-point capacity are a realistic pair of forecasts for the team's one-week simulation. The charts do not prove capacity beyond this exercise and would be validated with repeated sprints."),
    ]
    for question, answer in reflections:
        p = doc.add_paragraph()
        p.add_run(question + "\n").bold = True
        p.add_run(answer)

    doc.add_heading("10. Evidence Note", level=1)
    doc.add_paragraph(
        "The screenshots in this folder are polished Jira-style simulation evidence generated for this report. "
        "They document the planned backlog and both sprint outcomes; they should be replaced with personal Jira "
        "workspace screenshots when available for instructor demonstration."
    )

    output = ROOT / "LAB2_SE_PES1UG24CS606_Report.docx"
    doc.save(output)


def make_pdf():
    pdf_path = ROOT / "LAB2_SE_PES1UG24CS606_Report.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    styles["Title"].textColor = colors.HexColor("#172b4d")
    styles["Heading1"].textColor = colors.HexColor("#172b4d")
    styles["Heading2"].textColor = colors.HexColor("#172b4d")
    normal = styles["BodyText"]

    story = [
        Paragraph("Lab 2: Agile Backlog Creation & Sprint Simulation", styles["Title"]),
        Paragraph("<b>Group Travel Expense Simplification Engine</b><br/>PES1UG24CS606", ParagraphStyle(
            "center", parent=styles["Normal"], alignment=TA_CENTER, spaceAfter=12)),
        Paragraph("1. Project Setup", styles["Heading1"]),
        Paragraph("Project: Group Travel Expense Simplification Engine<br/>Jira project type: Software Development, Scrum template, Company-managed<br/>Project key: GTES<br/>Sprint duration: 1 week", normal),
        Paragraph("2. Epics", styles["Heading1"]),
    ]
    epic_rows = [["Epic", "Name", "Lab 1 requirement"]] + [[e[0], e[1], e[3]] for e in EPICS]
    table = Table(epic_rows, repeatRows=1, colWidths=[1.0*inch, 3.3*inch, 1.5*inch])
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#172b4d")),
                               ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                               ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
                               ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                               ("VALIGN", (0,0), (-1,-1), "TOP")]))
    story.append(table)

    story += [Spacer(1, 10), Paragraph("3. Prioritized Product Backlog", styles["Heading1"])]
    backlog_rows = [["Issue", "Summary", "Priority", "Points", "Sprint"]]
    backlog_rows += [[x[0], x[2], x[4], str(x[5]), x[6]] for x in STORIES]
    table = Table(backlog_rows, repeatRows=1, colWidths=[0.75*inch, 3.7*inch, 0.85*inch, 0.55*inch, 0.75*inch])
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#172b4d")),
                               ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                               ("GRID", (0,0), (-1,-1), 0.4, colors.grey),
                               ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                               ("FONTSIZE", (0,0), (-1,-1), 8),
                               ("VALIGN", (0,0), (-1,-1), "TOP")]))
    story.append(table)

    story += [PageBreak(), Paragraph("4. User Stories", styles["Heading1"])]
    for key, epic, summary, text, priority, points, sprint, status in STORIES:
        story.append(Paragraph(f"<b>{key} - {summary}</b> [{priority}, {points} pts, {sprint}]", normal))
        story.append(Paragraph(text, normal))
        story.append(Spacer(1, 5))

    story += [Paragraph("5. Sprint Evidence", styles["Heading1"]),
              Paragraph("<b>Sprint 1:</b> 21 points committed and completed. Goal: establish expense capture, currency conversion, balance visibility and the core settlement engine.", normal),
              RLImage(str(SCREENSHOTS / "sprint1_board.png"), width=6.8*inch, height=3.9*inch),
              Spacer(1, 8),
              Paragraph("<b>Sprint 2:</b> 16 points committed and completed. Goal: complete administration, security, performance validation and settlement edge-case handling.", normal),
              RLImage(str(SCREENSHOTS / "sprint2_board.png"), width=6.8*inch, height=3.9*inch)]

    story += [PageBreak(), Paragraph("6. Jira Backlog Evidence", styles["Heading1"]),
              RLImage(str(SCREENSHOTS / "jira_backlog.png"), width=6.8*inch, height=4.37*inch),
              Paragraph("7. Burndown Charts", styles["Heading1"]),
              RLImage(str(SCREENSHOTS / "burndown_chart_sprint1.png"), width=6.7*inch, height=3.65*inch),
              RLImage(str(SCREENSHOTS / "burndown_chart.png"), width=6.7*inch, height=3.65*inch)]

    story += [PageBreak(), Paragraph("8. Reflection", styles["Heading1"])]
    for question, answer in [
        ("1. Did the estimations reflect the actual effort?", "Fibonacci estimates were relative complexity rather than hours. The 8-point settlement item and 5-point integration stories accounted for algorithm and external-rate uncertainty, while 3-point stories were comparatively simple."),
        ("2. Was the backlog well-prioritized?", "Yes. Sprint 1 prioritized foundational expense, currency, balance and settlement stories. Access control and performance were placed in Sprint 2 while preserving security and core feature dependencies."),
        ("3. How did the simulated sprint align with the plan?", "Both sprints completed their full commitments: 21 points in Sprint 1 and 16 points in Sprint 2. Work moved through To Do, In Progress and Done."),
        ("4. What did the burndown chart show about team capacity?", "A stepped decline indicates work completed as stories reached Done. The 16-point Sprint 2 and 21-point Sprint 1 forecasts provide an initial capacity baseline for this one-week simulation."),
    ]:
        story += [Paragraph(f"<b>{question}</b>", normal), Paragraph(answer, normal), Spacer(1, 8)]

    story += [Paragraph("9. Evidence Note", styles["Heading1"]),
              Paragraph("The screenshots are polished Jira-style simulation evidence generated for this report. Replace them with personal Jira workspace screenshots when available for instructor demonstration.", normal)]

    doc.build(story)


def make_readme():
    readme = """# Lab 2: Agile Backlog Creation & Sprint Simulation in Jira

**Course:** Software Engineering Laboratory
**Student:** PES1UG24CS606
**Project:** Group Travel Expense Simplification Engine
**Jira project key:** `GTES`

## Objective

Convert the functional requirements from Lab 1 into Agile Epics and User Stories, prioritize and estimate the backlog using the Fibonacci scale, simulate two one-week Scrum sprints, and analyse the burndown evidence.

## Deliverables

- [Full PDF report](./LAB2_SE_PES1UG24CS606_Report.pdf)
- [Editable DOCX report](./LAB2_SE_PES1UG24CS606_Report.docx)
- [Backlog screenshot](./screenshots/jira_backlog.png)
- [Sprint 1 board](./screenshots/sprint1_board.png)
- [Sprint 2 board](./screenshots/sprint2_board.png)
- [Sprint 1 burndown](./screenshots/burndown_chart_sprint1.png)
- [Sprint 2 burndown](./screenshots/burndown_chart.png)

## Epics

| Epic | Name | Lab 1 requirement |
|---|---|---|
| GTES-EPIC-1 | Debt Settlement Engine | FR-001 |
| GTES-EPIC-2 | Expense and Currency Capture | FR-002, FR-003 |
| GTES-EPIC-3 | Traveler Balance Visibility | FR-004 |
| GTES-EPIC-4 | Trip Member Administration | FR-005 |
| GTES-EPIC-5 | Performance and Access Security | NFR-001, NFR-002 |

## Sprint Summary

| Sprint | Commitment | Completed | Velocity |
|---|---:|---:|---:|
| Sprint 1 | 21 pts | 21 pts | 21 |
| Sprint 2 | 16 pts | 16 pts | 16 |
| Total | 37 pts | 37 pts | 37 |

The backlog contains eight User Stories with High or Medium priority and Fibonacci estimates from 3 to 8 points.

## Regenerate

```powershell
.\\.venv\\Scripts\\python.exe .\\Lab02\\generate_lab2_assets.py
```

The generated screenshots are Jira-style simulation evidence. They can be replaced by actual Jira screenshots exported from the user's workspace.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    make_backlog()
    make_board("sprint1_board.png", "Sprint 1", "Build the core ledger and settlement flow", [x for x in STORIES if x[6] == "Sprint 1"])
    make_board("sprint2_board.png", "Sprint 2", "Complete security, administration and performance work", [x for x in STORIES if x[6] == "Sprint 2"])
    make_burndown()
    make_docx()
    make_pdf()
    make_readme()
