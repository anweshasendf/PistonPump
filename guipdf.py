from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
import matplotlib.pyplot as plt
import io
from reportlab.platypus import Image, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.enums import TA_LEFT, TA_CENTER

class PDFGenerator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(output_path, pagesize=letter)
        self.elements = []
        self.styles = getSampleStyleSheet()

    def add_cover_page(self, logo_path):
        self.elements.append(Spacer(1, 100))
        img = ImageReader(logo_path)
        aspect = img.getSize()[1] / float(img.getSize()[0])
        self.elements.append(Image(logo_path, width=300, height=300*aspect))
        self.elements.append(Spacer(1, 30))
        self.elements.append(Paragraph("Danfoss Industries", self.styles['Title']))
        self.elements.append(PageBreak())

    def add_table(self, df, title):
        self.elements.append(Paragraph(title, self.styles['Heading1']))
        self.elements.append(Spacer(1, 12))
        
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=self.styles['Normal'],
            fontSize=8,
            leading=10,
            alignment=TA_LEFT,
        )
        
        # Convert DataFrame to list of lists
        data = [df.columns.tolist()] + df.values.tolist()
        
        # Calculate column widths
        data = [[Paragraph(str(col), cell_style) for col in df.columns]]
        for row in df.values:
            data.append([Paragraph(str(cell), cell_style) for cell in row])
        
        # Calculate column widths
        available_width = self.doc.width - 1*inch  # Leave some margin
        col_widths = [available_width / len(df.columns)] 
        
        t = Table(data, repeatRows=1, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.elements.append(KeepTogether(t))
        self.elements.append(PageBreak())

    def add_image(self, image_path, title):
        self.elements.append(Paragraph(title, self.styles['Heading1']))
        self.elements.append(Spacer(1, 12))
        img = ImageReader(image_path)
        aspect = img.getSize()[1] / float(img.getSize()[0])
        self.elements.append(Image(image_path, width=500, height=500*aspect))
        self.elements.append(PageBreak())

    def generate_pdf(self):
        self.doc.build(self.elements)

def create_pdf_report(data, images, output_path, logo_path):
    pdf_gen = PDFGenerator(output_path)
    pdf_gen.add_cover_page(logo_path)
    
    for title, df in data.items():
        pdf_gen.add_table(df, title)
    
    for title, image_path in images.items():
        pdf_gen.add_image(image_path, title)
    
    pdf_gen.generate_pdf()