import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from datetime import datetime

def create_pdf(text_content, filename="Research_Report.pdf"):
    # Ensure outputs directory exists
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"Report_{timestamp}.pdf")

    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom Styles
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['BodyText']
    
    # 1. Add Title
    story.append(Paragraph("AI Research Report", title_style))
    story.append(Spacer(1, 12))
    
    # 2. Add Timestamp
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style))
    story.append(Spacer(1, 24))

    # 3. Process the Text Content
    lines = text_content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Headers (Lines starting with # or 'Research Report')
        if line.startswith("#") or "Research Report" in line or "Peer Review" in line:
            story.append(Paragraph(line.replace("#", "").strip(), heading_style))
            story.append(Spacer(1, 12))
        # Bullet points
        elif line.startswith("*") or line.startswith("-"):
            story.append(Paragraph(f"• {line[1:].strip()}", normal_style))
            story.append(Spacer(1, 6))
        # Normal Text
        else:
            story.append(Paragraph(line, normal_style))
            story.append(Spacer(1, 12))

    # Build PDF
    doc.build(story)
    return filepath