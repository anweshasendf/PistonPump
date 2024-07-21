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
import logging


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

    def add_summary_table(self, summary_data):
        table_elements = []
        table_elements.append(Paragraph("Summary", self.styles['Heading1']))
        table_elements.append(Spacer(1, 12))
        
        data = [["Metric", "Value"]]
        for key, value in summary_data.items():
            data.append([key, str(value)])
        
        t = Table(data, colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        table_elements.append(t)
        self.elements.append(KeepTogether(table_elements))
        self.elements.append(PageBreak())
    
    def add_table(self, df, title):
        
        table_elements = []
        table_elements.append(Paragraph(title, self.styles['Heading1']))
        table_elements.append(Spacer(1, 12))
        
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
        available_width = self.doc.width - 0.8*inch  # Leave some margin
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
        
        table_elements.append(t)
        self.elements.append(KeepTogether(table_elements))
        self.elements.append(PageBreak())

    def add_image(self, image_path, title):
        self.elements.append(Paragraph(title, self.styles['Heading1']))
        self.elements.append(Spacer(1, 12))
        img = ImageReader(image_path)
        aspect = img.getSize()[1] / float(img.getSize()[0])
        self.elements.append(Image(image_path, width=500, height=500*aspect))
        #self.elements.append(PageBreak())
        
    def add_single_file_plots(self, single_file_plots, single_file_name, efficiency_comparison):
        self.elements.append(PageBreak())
        self.elements.append(Paragraph(f"Single TDMS File Analysis for {single_file_name}", self.styles['Heading1']))
        self.elements.append(Spacer(1, 12))

        # Add efficiency comparison table
        if efficiency_comparison:
            self.add_efficiency_comparison(efficiency_comparison)
            self.elements.append(Spacer(1, 12))
        else:
            logging.debug("No efficiency comparison data available for single file analysis")

        logging.debug(f"Type of single_file_plots: {type(single_file_plots)}")
        logging.debug(f"Content of single_file_plots: {single_file_plots}")

        # Create a 2x4 grid for the plots
        plot_data = []
        row = []

        if isinstance(single_file_plots, dict):
            items = single_file_plots.items()
        elif isinstance(single_file_plots, (list, tuple)):
            items = enumerate(single_file_plots)
        else:
            logging.error(f"Unexpected type for single_file_plots: {type(single_file_plots)}")
            return

        for i, plot_item in items:
            logging.debug(f"Processing plot item {i}: {type(plot_item)}")
            if isinstance(plot_item, tuple):
                column, img_buffer = plot_item
            else:
                img_buffer = plot_item
            img = Image(img_buffer, width=250, height=150)
            row.append(img)
            if len(row) == 2 or i == len(single_file_plots) - 1:
                plot_data.append(row)
                row = []

        plot_table = Table(plot_data, colWidths=[250, 250])
        plot_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        self.elements.append(plot_table)
        logging.debug(f"Single file plots added to PDF: {len(single_file_plots)} plots")

        
    def add_efficiency_comparison(self, efficiency_data):
        if not efficiency_data:
            logging.warning("Efficiency comparison data is None or empty")
            return
        
        
        self.elements.append(Paragraph("Efficiency Comparison", self.styles['Heading2']))
        self.elements.append(Spacer(1, 12))

        data = [["Metric", "Value"]]
        for key, value in efficiency_data.items():
            data.append([key, str(value)])

        t = Table(data, colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        self.elements.append(t)
        logging.debug("Efficiency comparison table added to PDF")
    def generate_pdf(self):
        self.doc.build(self.elements)

def create_pdf_report(data, images, output_path, logo_path, single_file_plots=None, single_file_name=None, efficiency_comparison=None):

    pdf_gen = PDFGenerator(output_path)
    pdf_gen.add_cover_page(logo_path)
    
    if "Summary" in data:
        pdf_gen.add_summary_table(data["Summary"])
    
    for title, df in data.items():
        if title != "Summary":
            pdf_gen.add_table(df, title)
    
    for title, image_path in images.items():
        pdf_gen.add_image(image_path, title)
        
    if single_file_plots: #Removed and
        pdf_gen.add_single_file_plots(single_file_plots, single_file_name, efficiency_comparison)
        
    if "Efficiency Comparison" in data:
        logging.debug("Efficiency Comparison found in data, adding to PDF")
        pdf_gen.add_efficiency_comparison(data["Efficiency Comparison"])
    elif efficiency_comparison:
        logging.debug("Efficiency Comparison found in parameters, adding to PDF")
        pdf_gen.add_efficiency_comparison(efficiency_comparison)
    else:
        logging.debug("No Efficiency Comparison found, skipping this section")
        
    pdf_gen.generate_pdf()