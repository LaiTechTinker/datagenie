from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf_report(profile, cleaning, ml_result, filename="report.pdf"):
    doc = SimpleDocTemplate(f"exports/{filename}")
    styles = getSampleStyleSheet()

    content = []

    # Title
    content.append(Paragraph("Data Science Report", styles["Title"]))
    content.append(Spacer(1, 12))

    # Profiling Section
    content.append(Paragraph("Data Profiling Summary", styles["Heading2"]))
    content.append(Paragraph(str(profile), styles["Normal"]))
    content.append(Spacer(1, 12))

    # Cleaning Section
    content.append(Paragraph("Data Cleaning Suggestions", styles["Heading2"]))
    content.append(Paragraph(str(cleaning), styles["Normal"]))
    content.append(Spacer(1, 12))

    # ML Section
    content.append(Paragraph("Machine Learning Results", styles["Heading2"]))
    content.append(Paragraph(str(ml_result), styles["Normal"]))
    content.append(Spacer(1, 12))

    doc.build(content)

    return f"exports/{filename}"