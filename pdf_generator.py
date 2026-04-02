from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import os
import uuid


def generate_pdf_report(report_text: str) -> str:
    """
    Converts AI-generated report text into a styled PDF
    Returns the file path
    """

    # Create folder
    output_dir = "reports"
    os.makedirs(output_dir, exist_ok=True)

    file_name = f"report_{uuid.uuid4()}.pdf"
    file_path = os.path.join(output_dir, file_name)

    # Create document
    doc = SimpleDocTemplate(file_path, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    # Split report into lines
    lines = report_text.split("\n")

    for line in lines:
        line = line.strip()

        if not line:
            elements.append(Spacer(1, 10))
            continue

        # Detect headings (simple heuristic)
        if line.isupper():
            elements.append(Paragraph(f"<b>{line}</b>", styles["Heading2"]))

        # Detect bullet points
        elif line.startswith("-"):
            elements.append(Paragraph(line, styles["Normal"]))

        # Detect simple tables (pipe format)
        elif "|" in line:
            table_data = parse_table(report_text)
            if table_data:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 10))
                break  # avoid reprocessing

        else:
            elements.append(Paragraph(line, styles["Normal"]))

        elements.append(Spacer(1, 8))

    # Build PDF
    doc.build(elements)

    return file_path


def parse_table(text: str):
    """
    Extracts simple tables from LLM output (pipe-separated)
    """
    lines = text.split("\n")
    table_lines = []

    for line in lines:
        if "|" in line:
            row = [cell.strip() for cell in line.split("|") if cell.strip()]
            if row:
                table_lines.append(row)

    return table_lines if len(table_lines) > 1 else None