from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
PROJECT = "Group Travel Expense Simplification Engine"
SRN = "PES1UG24CS606"
NAVY = "#17365D"
BLUE = "#DCE6F1"
PALE_BLUE = "#F2F6FB"
TEAL = "#DDEBF7"
INK = "#263746"
MUTED = "#536575"
LINE = "#52677D"

JUSTIFICATION = [
    (
        "Architecture Selection: We chose Layered Architecture (modular monolith) "
        "for the Group Travel Expense Simplification Engine."
    ),
    (
        "Reason 1 - A single trip-and-expense domain service maintains one ledger "
        "for payers, participants, currency conversion, and traveler balances. "
        "The settlement engine works from those normalized balances so each "
        "settlement can be checked against the net-zero invariant."
    ),
    (
        "Reason 2 - Clear layers separate the traveler/admin interface, access "
        "control, expense workflows, settlement logic, persistence, and exchange-rate "
        "integration. This fits a focused product that does not need independently "
        "deployed microservices."
    ),
    (
        "Security advantage - The API authenticates each request and checks trip "
        "membership and the Trip Admin role before allowing expense or participant "
        "changes. Clients cannot access the ledger repository directly; access passes "
        "through the authorized service layer."
    ),
    (
        "Performance benefit - The settlement engine runs in the same application "
        "deployment and consumes bounded trip data, avoiding an extra network hop "
        "for the under-100-ms target (50 travelers and 500 expenses). Indexing and "
        "the stated workload still need benchmark validation; this design does not "
        "claim measured performance."
    ),
    (
        "Conclusion - The layered design keeps balance and settlement rules testable, "
        "supports the required workflows, and leaves a clear integration seam for "
        "daily exchange rates."
    ),
]

STYLE_ROWS = [
    (
        "Layered",
        "Best fit for the internal application. Separates presentation, access "
        "control, trip/expense rules, settlement, integrations, and persistence. "
        "A modular monolith keeps the balance ledger and settlement call local.",
        "Clear responsibility boundaries and straightforward testing. A change to "
        "one layer can be made without creating a distributed deployment. The "
        "trade-off is that all layers scale together and careless cross-layer "
        "coupling can erode the separation.",
    ),
    (
        "Microservices",
        "Not justified at the stated scope. Independent settlement, trip, and FX "
        "services could scale separately, but 50 travelers and 500 expenses per "
        "benchmark case do not establish a need for that operational split.",
        "Independent deployment and fault isolation are useful at larger scale. "
        "However, network hops, distributed data consistency, service discovery, "
        "and duplicated authorization add complexity and can consume the "
        "under-100-ms settlement budget.",
    ),
    (
        "Client-server",
        "Useful as the deployment boundary: traveler and admin clients call a "
        "central API and ledger. By itself, this style does not define how expense, "
        "FX, and settlement responsibilities are separated inside the server.",
        "Centralized access control and a single source of trip data are helpful. "
        "The central server can become a bottleneck or single point of failure, "
        "so availability and capacity still need attention.",
    ),
]

COMPONENTS = [
    (
        "Traveler / Trip Admin Client",
        "Trip screens, expense entry, balances, and settlement view",
    ),
    (
        "API & Access Control",
        "Authentication, trip membership, and role checks",
    ),
    (
        "Trip & Expense Service",
        "Expense capture, participant management, conversion orchestration, balances",
    ),
    (
        "Settlement Engine",
        "Net balances and simplified payment-transfer plan",
    ),
    (
        "Trip Ledger Repository",
        "Trips, participants, expenses, rates, and settlement records",
    ),
    (
        "FX Rate Adapter",
        "Daily dated exchange-rate lookup and normalization",
    ),
]

INTERFACES = [
    (
        "Client -> API & Access Control",
        "HTTPS/JSON trip, expense, balance, and settlement requests",
    ),
    (
        "API & Access Control -> Trip & Expense Service",
        "Authorized trip and expense commands/queries",
    ),
    (
        "Trip & Expense Service -> Settlement Engine",
        "Net-balance input; simplified transfer result",
    ),
    (
        "Trip & Expense Service -> Trip Ledger Repository",
        "Transactional reads/writes for trip and expense data",
    ),
    (
        "Trip & Expense Service -> FX Rate Adapter",
        "Dated source/base currency rate lookup",
    ),
    (
        "FX Rate Adapter -> Daily FX Provider",
        "HTTPS daily exchange-rate request",
    ),
]


def svg_text(x, y, value, size=17, fill=INK, weight="normal", anchor="middle", rotate=None):
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}"{transform} '
        f'font-family="Arial, Helvetica, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}">{escape(value)}</text>'
    )


def svg_rect(x, y, width, height, fill, stroke, radius=12, stroke_width=2):
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
    )


def svg_component(x, y, width, height, title, detail_lines, fill=BLUE):
    result = [
        svg_rect(x, y, width, height, fill, NAVY, radius=12, stroke_width=2.5),
        f'<path d="M{x} {y + 40} H{x + width}" stroke="{NAVY}" stroke-width="1.5"/>',
        svg_text(x + width / 2, y + 25, "<<component>>", size=14, fill=MUTED),
    ]
    icon_x = x + width - 34
    result.extend(
        [
            f'<rect x="{icon_x}" y="{y + 9}" width="19" height="15" fill="white" '
            f'stroke="{NAVY}" stroke-width="1.5"/>',
            f'<path d="M{icon_x + 5} {y + 9} V{y + 24} M{icon_x + 11} {y + 9} '
            f'V{y + 24}" stroke="{NAVY}" stroke-width="1"/>',
            svg_text(x + width / 2, y + 74, title, size=19, fill=NAVY, weight="bold"),
        ]
    )
    line_y = y + 101
    for line in detail_lines:
        result.append(svg_text(x + width / 2, line_y, line, size=14, fill=MUTED))
        line_y += 21
    return "".join(result)


def svg_socket(x, y, side):
    if side == "right":
        path = f"M{x} {y - 13} A13 13 0 0 1 {x} {y + 13}"
    elif side == "left":
        path = f"M{x} {y - 13} A13 13 0 0 0 {x} {y + 13}"
    elif side == "top":
        path = f"M{x - 13} {y} A13 13 0 0 0 {x + 13} {y}"
    else:
        path = f"M{x - 13} {y} A13 13 0 0 1 {x + 13} {y}"
    return f'<path d="{path}" fill="none" stroke="{NAVY}" stroke-width="4"/>'


def svg_ball(x, y):
    return f'<circle cx="{x}" cy="{y}" r="11" fill="{NAVY}" stroke="white" stroke-width="2"/>'


def svg_label(x, y, value, rotate=None):
    transform = f' transform="rotate({rotate} {x} {y})"' if rotate is not None else ""
    width = max(90, len(value) * 7.4)
    return (
        f'<g{transform}><rect x="{x - width / 2}" y="{y - 16}" width="{width}" '
        f'height="23" rx="5" fill="white" opacity="0.94"/>'
        f'{svg_text(x, y, value, size=13, fill=INK)}</g>'
    )


def load_font(size, bold=False):
    filename = "arialbd.ttf" if bold else "arial.ttf"
    candidates = [
        Path("C:/Windows/Fonts") / filename,
        Path("C:/Windows/Fonts") / "calibri.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(str(candidate), size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_diagram_png(path):
    image = Image.new("RGB", (1800, 1080), "white")
    draw = ImageDraw.Draw(image)

    def text(x, y, value, size=17, fill=INK, bold=False, anchor="mm"):
        draw.text((x, y), value, font=load_font(size, bold), fill=fill, anchor=anchor)

    def box(x, y, width, height, fill, stroke, radius=12, stroke_width=2):
        draw.rounded_rectangle(
            (x, y, x + width, y + height),
            radius=radius,
            fill=fill,
            outline=stroke,
            width=stroke_width,
        )

    def component(x, y, width, height, title, detail_lines, fill):
        box(x, y, width, height, fill, NAVY, radius=12, stroke_width=3)
        draw.line((x, y + 40, x + width, y + 40), fill=NAVY, width=2)
        text(x + width / 2, y + 25, "<<component>>", size=14, fill=MUTED)
        icon_x = x + width - 34
        draw.rectangle((icon_x, y + 9, icon_x + 19, y + 24), fill="white", outline=NAVY, width=2)
        draw.line((icon_x + 5, y + 9, icon_x + 5, y + 24), fill=NAVY, width=1)
        draw.line((icon_x + 11, y + 9, icon_x + 11, y + 24), fill=NAVY, width=1)
        text(x + width / 2, y + 74, title, size=19, fill=NAVY, bold=True)
        for index, line in enumerate(detail_lines):
            text(x + width / 2, y + 102 + index * 21, line, size=14, fill=MUTED)

    def connector(points, arrow=True):
        draw.line(points, fill=LINE, width=3, joint="curve")
        if arrow:
            x1, y1 = points[-2]
            x2, y2 = points[-1]
            if x2 > x1:
                tip = (x2 - 2, y2)
                wings = [(x2 - 13, y2 - 7), (x2 - 13, y2 + 7)]
            elif x2 < x1:
                tip = (x2 + 2, y2)
                wings = [(x2 + 13, y2 - 7), (x2 + 13, y2 + 7)]
            elif y2 > y1:
                tip = (x2, y2 - 2)
                wings = [(x2 - 7, y2 - 13), (x2 + 7, y2 - 13)]
            else:
                tip = (x2, y2 + 2)
                wings = [(x2 - 7, y2 + 13), (x2 + 7, y2 + 13)]
            draw.polygon([tip, *wings], fill=LINE)

    def socket(x, y, side):
        radius = 13
        if side == "right":
            bounds, start, end = (x - radius, y - radius, x + radius, y + radius), -90, 90
        elif side == "left":
            bounds, start, end = (x - radius, y - radius, x + radius, y + radius), 90, 270
        elif side == "top":
            bounds, start, end = (x - radius, y - radius, x + radius, y + radius), 180, 360
        else:
            bounds, start, end = (x - radius, y - radius, x + radius, y + radius), 0, 180
        draw.arc(bounds, start=start, end=end, fill=NAVY, width=4)

    def ball(x, y):
        draw.ellipse((x - 11, y - 11, x + 11, y + 11), fill=NAVY, outline="white", width=2)

    def label(x, y, value, rotate=None):
        font = load_font(13)
        bounds = draw.textbbox((0, 0), value, font=font)
        width = max(90, bounds[2] - bounds[0] + 14)
        height = 24
        if rotate is None:
            draw.rounded_rectangle(
                (x - width / 2, y - height + 5, x + width / 2, y + 5),
                radius=5,
                fill="white",
            )
            text(x, y - 7, value, size=13, fill=INK)
            return
        layer = Image.new("RGBA", (width, height), (255, 255, 255, 0))
        layer_draw = ImageDraw.Draw(layer)
        layer_draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=5, fill="white")
        layer_draw.text((width / 2, height / 2), value, font=font, fill=INK, anchor="mm")
        layer = layer.rotate(rotate, expand=True)
        image.paste(layer, (int(x - layer.width / 2), int(y - layer.height / 2)), layer)

    text(900, 48, PROJECT, size=31, fill=NAVY, bold=True)
    text(900, 80, "Layered modular monolith | UML component view | PES1UG24CS606", size=17, fill=MUTED)
    box(40, 115, 1330, 865, "#FFFFFF", "#7890A8", radius=18, stroke_width=2)
    text(68, 145, "<<system>>", size=15, fill=MUTED, anchor="lm")
    text(206, 145, PROJECT, size=17, fill=NAVY, bold=True, anchor="lm")
    box(70, 180, 320, 285, PALE_BLUE, "#9CB4CB")
    text(230, 211, "Presentation", size=16, fill=NAVY, bold=True)
    box(415, 165, 880, 480, "#F8FAFD", "#9CB4CB")
    text(855, 195, "Application & Domain", size=16, fill=NAVY, bold=True)
    box(415, 685, 880, 255, "#F8FAFD", "#9CB4CB")
    text(855, 715, "Persistence & Integration", size=16, fill=NAVY, bold=True)

    component(95, 245, 270, 170, "Traveler / Trip Admin Client",
              ["Trip, expense, balance views", "Role-specific actions"], "#E8F1FA")
    component(455, 235, 300, 170, "API & Access Control",
              ["Authentication + trip roles", "Validates each request"], BLUE)
    component(855, 225, 370, 170, "Trip & Expense Service",
              ["Records expenses and members", "Converts amounts; serves balances"], BLUE)
    component(855, 475, 370, 150, "Settlement Engine",
              ["Net-zero balance settlement", "Minimizes payment transactions"], "#E4EDF7")
    component(455, 755, 330, 150, "Trip Ledger Repository",
              ["Trips, members, expenses", "Rate snapshots, settlements"], "#E6F2F1")
    component(855, 755, 370, 150, "FX Rate Adapter",
              ["Daily, date-specific rates", "Normalizes provider responses"], "#E6F2F1")
    box(1430, 755, 300, 150, "#FFF3DF", "#A57630", radius=12, stroke_width=3)
    text(1580, 785, "<<external system>>", size=14, fill=MUTED)
    text(1580, 830, "Daily FX Provider", size=19, fill="#74521E", bold=True)
    text(1580, 860, "Published exchange rates", size=14, fill=MUTED)
    text(1580, 882, "for the expense date", size=14, fill=MUTED)

    connector([(373, 330), (442, 330)])
    connector([(768, 320), (842, 320)])
    connector([(1040, 408), (1040, 462)])
    connector([(842, 370), (820, 370), (820, 830), (798, 830)])
    connector([(1238, 370), (1280, 370), (1280, 830), (867, 830)])
    connector([(1238, 830), (1417, 830)])
    socket(365, 330, "right")
    ball(455, 330)
    socket(755, 320, "right")
    ball(855, 320)
    socket(1040, 400, "bottom")
    ball(1040, 475)
    socket(850, 370, "left")
    ball(785, 830)
    socket(1230, 370, "right")
    ball(855, 830)
    socket(1230, 830, "right")
    ball(1430, 830)

    label(410, 305, "HTTPS / JSON")
    label(805, 298, "authorized trip API")
    label(1118, 438, "net balances / transfers")
    label(820, 605, "transactional ledger access", rotate=90)
    label(1280, 610, "dated rate lookup", rotate=90)
    label(1335, 800, "HTTPS rate request")

    text(70, 965, "UML key:", size=14, fill=NAVY, bold=True, anchor="lm")
    ball(160, 960)
    text(183, 965, "provided interface", size=14, fill=MUTED, anchor="lm")
    socket(350, 960, "right")
    text(373, 965, "required interface", size=14, fill=MUTED, anchor="lm")
    connector([(555, 960), (625, 960)])
    text(640, 965, "assembly connector / request flow", size=14, fill=MUTED, anchor="lm")
    text(
        70,
        1008,
        "The Trip & Expense Service persists converted amounts and invokes settlement from one normalized trip ledger.",
        size=14,
        fill=MUTED,
        anchor="lm",
    )
    image.save(path, format="PNG", dpi=(150, 150))


def create_component_diagram():
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1080" '
        'viewBox="0 0 1800 1080">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" '
        'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,5 L0,10 z" '
        f'fill="{LINE}"/></marker>',
        "</defs>",
        '<rect width="1800" height="1080" fill="#FFFFFF"/>',
        svg_text(900, 48, PROJECT, size=31, fill=NAVY, weight="bold"),
        svg_text(
            900,
            80,
            "Layered modular monolith | UML component view | PES1UG24CS606",
            size=17,
            fill=MUTED,
        ),
        svg_rect(40, 115, 1330, 865, "#FFFFFF", "#7890A8", radius=18, stroke_width=2),
        svg_text(68, 145, "<<system>>", size=15, fill=MUTED, anchor="start"),
        svg_text(206, 145, PROJECT, size=17, fill=NAVY, weight="bold", anchor="start"),
        svg_rect(70, 180, 320, 285, PALE_BLUE, "#9CB4CB"),
        svg_text(230, 211, "Presentation", size=16, fill=NAVY, weight="bold"),
        svg_rect(415, 165, 880, 480, "#F8FAFD", "#9CB4CB"),
        svg_text(855, 195, "Application & Domain", size=16, fill=NAVY, weight="bold"),
        svg_rect(415, 685, 880, 255, "#F8FAFD", "#9CB4CB"),
        svg_text(855, 715, "Persistence & Integration", size=16, fill=NAVY, weight="bold"),
        svg_component(
            95,
            245,
            270,
            170,
            "Traveler / Trip Admin Client",
            ["Trip, expense, balance views", "Role-specific actions"],
            fill="#E8F1FA",
        ),
        svg_component(
            455,
            235,
            300,
            170,
            "API & Access Control",
            ["Authentication + trip roles", "Validates each request"],
        ),
        svg_component(
            855,
            225,
            370,
            170,
            "Trip & Expense Service",
            ["Records expenses and members", "Converts amounts; serves balances"],
        ),
        svg_component(
            855,
            475,
            370,
            150,
            "Settlement Engine",
            ["Net-zero balance settlement", "Minimizes payment transactions"],
            fill="#E4EDF7",
        ),
        svg_component(
            455,
            755,
            330,
            150,
            "Trip Ledger Repository",
            ["Trips, members, expenses", "Rate snapshots, settlements"],
            fill="#E6F2F1",
        ),
        svg_component(
            855,
            755,
            370,
            150,
            "FX Rate Adapter",
            ["Daily, date-specific rates", "Normalizes provider responses"],
            fill="#E6F2F1",
        ),
        svg_rect(1430, 755, 300, 150, "#FFF3DF", "#A57630", radius=12, stroke_width=2.5),
        svg_text(1580, 785, "«external system»", size=14, fill=MUTED),
        svg_text(1580, 830, "Daily FX Provider", size=19, fill="#74521E", weight="bold"),
        svg_text(1580, 860, "Published exchange rates", size=14, fill=MUTED),
        svg_text(1580, 882, "for the expense date", size=14, fill=MUTED),
    ]

    connectors = [
        '<path d="M373 330 H442" fill="none" stroke="'
        + LINE
        + '" stroke-width="2.5" marker-end="url(#arrow)"/>',
        '<path d="M768 320 H842" fill="none" stroke="'
        + LINE
        + '" stroke-width="2.5" marker-end="url(#arrow)"/>',
        '<path d="M1040 408 V462" fill="none" stroke="'
        + LINE
        + '" stroke-width="2.5" marker-end="url(#arrow)"/>',
        '<path d="M842 370 H820 V830 H798" fill="none" stroke="'
        + LINE
        + '" stroke-width="2.5" marker-end="url(#arrow)"/>',
        '<path d="M1238 370 H1280 V830 H867" fill="none" stroke="'
        + LINE
        + '" stroke-width="2.5" marker-end="url(#arrow)"/>',
        '<path d="M1238 830 H1417" fill="none" stroke="'
        + LINE
        + '" stroke-width="2.5" marker-end="url(#arrow)"/>',
    ]
    parts.extend(connectors)

    interfaces = [
        svg_socket(365, 330, "right") + svg_ball(455, 330),
        svg_socket(755, 320, "right") + svg_ball(855, 320),
        svg_socket(1040, 400, "bottom") + svg_ball(1040, 475),
        svg_socket(850, 370, "left") + svg_ball(785, 830),
        svg_socket(1230, 370, "right") + svg_ball(855, 830),
        svg_socket(1230, 830, "right") + svg_ball(1430, 830),
    ]
    parts.extend(interfaces)

    parts.extend(
        [
            svg_label(410, 305, "HTTPS / JSON"),
            svg_label(805, 298, "authorized trip API"),
            svg_label(1118, 438, "net balances / transfers"),
            svg_label(820, 605, "transactional ledger access", rotate=-90),
            svg_label(1280, 610, "dated rate lookup", rotate=-90),
            svg_label(1335, 800, "HTTPS rate request"),
            svg_text(70, 965, "UML key:", size=14, fill=NAVY, weight="bold", anchor="start"),
            svg_ball(160, 960),
            svg_text(183, 965, "provided interface", size=14, fill=MUTED, anchor="start"),
            svg_socket(350, 960, "right"),
            svg_text(373, 965, "required interface", size=14, fill=MUTED, anchor="start"),
            '<path d="M555 960 H625" fill="none" stroke="'
            + LINE
            + '" stroke-width="2.5" marker-end="url(#arrow)"/>',
            svg_text(640, 965, "assembly connector / request flow", size=14, fill=MUTED, anchor="start"),
            svg_text(
                70,
                1008,
                "The Trip & Expense Service persists converted amounts and invokes settlement from one normalized trip ledger.",
                size=14,
                fill=MUTED,
                anchor="start",
            ),
        ]
    )
    parts.append("</svg>")

    svg_path = ROOT / "Group_Travel_Expense_Component_Diagram.svg"
    png_path = ROOT / "Group_Travel_Expense_Component_Diagram.png"
    pdf_path = ROOT / "Group_Travel_Expense_Component_Diagram.pdf"
    svg_path.write_text("".join(parts), encoding="utf-8")
    draw_diagram_png(png_path)
    page_width, page_height = landscape(A4)
    pdf_canvas = canvas.Canvas(str(pdf_path), pagesize=landscape(A4))
    image_width = page_width - 44
    image_height = image_width * 1080 / 1800
    image_x = 22
    image_y = (page_height - image_height) / 2
    pdf_canvas.drawImage(
        ImageReader(str(png_path)),
        image_x,
        image_y,
        width=image_width,
        height=image_height,
        preserveAspectRatio=True,
    )
    pdf_canvas.showPage()
    pdf_canvas.save()
    return svg_path, png_path, pdf_path


def set_docx_font(run, name="Arial", size=10, color=INK, bold=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color.lstrip("#"))
    if bold is not None:
        run.bold = bold


def add_docx_title(document, title, subtitle):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(4)
    run = paragraph.add_run(title)
    set_docx_font(run, size=16, color=NAVY, bold=True)
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_after = Pt(12)
    run = paragraph.add_run(subtitle)
    set_docx_font(run, size=9, color=MUTED)


def add_pdf_title(story, title, subtitle, styles):
    story.append(Paragraph(escape(title), styles["TitleLab"]))
    story.append(Paragraph(escape(subtitle), styles["MetaLab"]))
    story.append(Spacer(1, 8))


def create_justification():
    document = Document()
    section = document.sections[0]
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.72)
    section.right_margin = Inches(0.72)
    add_docx_title(
        document,
        "Architecture Selection",
        f"Lab 3 | {PROJECT} | {SRN}",
    )
    for index, text in enumerate(JUSTIFICATION):
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(7 if index < len(JUSTIFICATION) - 1 else 0)
        paragraph.paragraph_format.line_spacing = 1.02
        run = paragraph.add_run(text)
        set_docx_font(run, size=10)
        if index == 0:
            run.bold = True
            run.font.color.rgb = RGBColor.from_string(NAVY.lstrip("#"))
    docx_path = ROOT / "Architecture_Justification.docx"
    document.save(docx_path)

    pdf_path = ROOT / "Architecture_Justification.pdf"
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "TitleLab",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            textColor=colors.HexColor(NAVY),
            alignment=TA_CENTER,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            "MetaLab",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor(MUTED),
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            "BodyLab",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor(INK),
            alignment=TA_LEFT,
            spaceAfter=9,
        )
    )
    story = []
    add_pdf_title(story, "Architecture Selection", f"Lab 3 | {PROJECT} | {SRN}", styles)
    for index, text in enumerate(JUSTIFICATION):
        style = styles["BodyLab"]
        if index == 0:
            style = ParagraphStyle(
                "OpeningLab",
                parent=styles["BodyLab"],
                fontName="Helvetica-Bold",
                textColor=colors.HexColor(NAVY),
            )
        story.append(Paragraph(escape(text), style))
    SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=48,
        rightMargin=48,
        topMargin=42,
        bottomMargin=42,
        title="Architecture Selection - Group Travel Expense Simplification Engine",
        author=SRN,
    ).build(story)
    if len(PdfReader(str(pdf_path)).pages) != 1:
        raise RuntimeError("The architecture justification PDF must fit on one page.")
    return docx_path, pdf_path


def add_docx_table(document, headers, rows, widths):
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.width = Inches(widths[index])
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        paragraph = cell.paragraphs[0]
        run = paragraph.add_run(header)
        set_docx_font(run, size=9, color="#FFFFFF", bold=True)
        for row in table.rows:
            row.cells[index].width = Inches(widths[index])
    for row_values in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row_values):
            cells[index].width = Inches(widths[index])
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            paragraph = cells[index].paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(2)
            run = paragraph.add_run(value)
            set_docx_font(run, size=8.5, color=INK)
    for cell in table.rows[0].cells:
        shading = cell._tc.get_or_add_tcPr()
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        element = OxmlElement("w:shd")
        element.set(qn("w:fill"), NAVY.lstrip("#"))
        shading.append(element)
    return table


def create_style_analysis():
    document = Document()
    section = document.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Inches(11.69)
    section.page_height = Inches(8.27)
    section.top_margin = Inches(0.48)
    section.bottom_margin = Inches(0.48)
    section.left_margin = Inches(0.55)
    section.right_margin = Inches(0.55)
    add_docx_title(
        document,
        "Architectural Style Analysis",
        f"Lab 3 | {PROJECT} | {SRN}",
    )
    paragraph = document.add_paragraph(
        "Scenario drivers: net-zero expense settlement, daily foreign-currency conversion, "
        "trip-member administration, authorized access, and a settlement target below "
        "100 ms for 50 travelers and 500 expenses."
    )
    paragraph.paragraph_format.space_after = Pt(8)
    for run in paragraph.runs:
        set_docx_font(run, size=9, color=INK)

    add_docx_table(
        document,
        ["Style", "Fit for this scenario", "Advantages and trade-offs"],
        STYLE_ROWS,
        [1.35, 4.45, 4.55],
    )
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(9)
    run = paragraph.add_run(
        "Selection: Layered architecture as a modular monolith. Client-server describes "
        "the outer client-to-API deployment boundary and can coexist with these internal "
        "layers; it is not being used as a substitute for internal component separation."
    )
    set_docx_font(run, size=9, color=NAVY, bold=True)

    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(4)
    run = paragraph.add_run(
        "Components: Traveler/Trip Admin Client; API & Access Control; Trip & Expense "
        "Service; Settlement Engine; Trip Ledger Repository; FX Rate Adapter. "
        "External dependency: Daily FX Provider."
    )
    set_docx_font(run, size=8.5, color=MUTED)

    paragraph = document.add_paragraph()
    run = paragraph.add_run(
        "Key interfaces: HTTPS/JSON client requests; authorized trip API; settlement "
        "balances/transfers; transactional ledger reads/writes; dated rate lookup; "
        "HTTPS exchange-rate request."
    )
    set_docx_font(run, size=8.5, color=MUTED)
    docx_path = ROOT / "Architecture_Style_Analysis.docx"
    document.save(docx_path)

    pdf_path = ROOT / "Architecture_Style_Analysis.pdf"
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "AnalysisTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=21,
            textColor=colors.HexColor(NAVY),
            alignment=TA_CENTER,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "AnalysisMeta",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor(MUTED),
            alignment=TA_CENTER,
            spaceAfter=9,
        )
    )
    styles.add(
        ParagraphStyle(
            "AnalysisBody",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8.3,
            leading=11,
            textColor=colors.HexColor(INK),
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            "AnalysisCell",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10.4,
            textColor=colors.HexColor(INK),
        )
    )
    styles.add(
        ParagraphStyle(
            "AnalysisHeaderCell",
            parent=styles["AnalysisCell"],
            fontName="Helvetica-Bold",
            textColor=colors.white,
        )
    )
    story = [
        Paragraph("Architectural Style Analysis", styles["AnalysisTitle"]),
        Paragraph(escape(f"Lab 3 | {PROJECT} | {SRN}"), styles["AnalysisMeta"]),
        Paragraph(
            "<b>Scenario drivers:</b> net-zero expense settlement, daily foreign-currency "
            "conversion, trip-member administration, authorized access, and a settlement "
            "target below 100 ms for 50 travelers and 500 expenses.",
            styles["AnalysisBody"],
        ),
        Spacer(1, 3),
    ]
    table_data = [
        [
            Paragraph("Style", styles["AnalysisHeaderCell"]),
            Paragraph("Fit for this scenario", styles["AnalysisHeaderCell"]),
            Paragraph("Advantages and trade-offs", styles["AnalysisHeaderCell"]),
        ]
    ]
    for name, fit, tradeoffs in STYLE_ROWS:
        table_data.append(
            [
                Paragraph(f"<b>{escape(name)}</b>", styles["AnalysisCell"]),
                Paragraph(escape(fit), styles["AnalysisCell"]),
                Paragraph(escape(tradeoffs), styles["AnalysisCell"]),
            ]
        )
    table = Table(table_data, colWidths=[105, 320, 320], repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F6F8FB")),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#AAB8C6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend(
        [
            table,
            Spacer(1, 9),
            Paragraph(
                "<b>Selection:</b> Layered architecture as a modular monolith. Client-server "
                "describes the outer client-to-API deployment boundary and can coexist "
                "with these internal layers; it does not replace internal component separation.",
                styles["AnalysisBody"],
            ),
            Paragraph(
                "<b>Components:</b> Traveler/Trip Admin Client; API &amp; Access Control; "
                "Trip &amp; Expense Service; Settlement Engine; Trip Ledger Repository; "
                "FX Rate Adapter. External dependency: Daily FX Provider.",
                styles["AnalysisBody"],
            ),
            Paragraph(
                "<b>Key interfaces:</b> HTTPS/JSON client requests; authorized trip API; "
                "settlement balances/transfers; transactional ledger reads/writes; dated "
                "rate lookup; HTTPS exchange-rate request.",
                styles["AnalysisBody"],
            ),
        ]
    )
    SimpleDocTemplate(
        str(pdf_path),
        pagesize=landscape(A4),
        leftMargin=34,
        rightMargin=34,
        topMargin=28,
        bottomMargin=28,
        title="Architectural Style Analysis - Group Travel Expense Simplification Engine",
        author=SRN,
    ).build(story)
    return docx_path, pdf_path


def main():
    diagram = create_component_diagram()
    justification = create_justification()
    analysis = create_style_analysis()
    for path in (*diagram, *justification, *analysis):
        print(f"Created {path}")


if __name__ == "__main__":
    main()
