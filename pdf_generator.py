from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
import os
from datetime import datetime
from models import Client, Company
from io import BytesIO

class PDFGenerator:
    """Génère des factures PDF à partir des données client"""
    
    def __init__(self, company: Company):
        self.company = company
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configure les styles personnalisés"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1f4e79'),
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='ClientInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            leftIndent=0,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='CompanyInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_RIGHT
        ))
    
    def generate_pdf(self, client: Client) -> BytesIO:
        """Génère le PDF pour un client"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        
        # En-tête avec logo et informations de l'entreprise
        self.add_header(story)
        
        # Titre
        title = Paragraph("FACTURE GLOBALE", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Informations client
        self.add_client_info(story, client)
        
        # Tableau des factures
        self.add_invoice_table(story, client)
        
        # Totaux
        self.add_totals(story, client)
        
        # Pied de page
        self.add_footer(story) 
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def add_header(self, story):
        """Ajoute l'en-tête avec logo et infos entreprise"""
        # Créer un tableau pour l'en-tête
        header_data = []
        
        # Logo (si disponible) et informations de l'entreprise
        company_info = f"""
        <b>{self.company.name}</b><br/>
        {self.company.address.replace(chr(10), '<br/>')}<br/>
        Tél: {self.company.phone}<br/>
        Email: {self.company.email}
        """
        
        if os.path.exists(self.company.logo_path):
            try:
                logo = Image(self.company.logo_path, width=40*mm, height=40*mm)
                header_data.append([logo, Paragraph(company_info, self.styles['CompanyInfo'])])
            except:
                header_data.append(['', Paragraph(company_info, self.styles['CompanyInfo'])])
        else:
            header_data.append(['', Paragraph(company_info, self.styles['CompanyInfo'])])
        
        header_table = Table(header_data, colWidths=[60*mm, None])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ]))
        
        story.append(header_table)
        story.append(Spacer(1, 20))
    
    def add_client_info(self, story, client: Client):
        """Ajoute les informations du client"""
        client_info = f"""
        <b>FACTURÉ À:</b><br/>
        <b>{client.number}</b><br/>
        {client.address.replace(chr(10), '<br/>')}
        """
        
        story.append(Paragraph(client_info, self.styles['ClientInfo']))
        story.append(Spacer(1, 20))
        
        # Date et numéro de facture globale
        date_info = f"""
        <b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        <b>Facture globale pour:</b> {len(client.invoices)} facture(s)
        """
        story.append(Paragraph(date_info, self.styles['Normal']))
        story.append(Spacer(1, 20))
    
    def add_invoice_table(self, story, client: Client):
        """Ajoute le tableau des factures"""
        # En-têtes du tableau
        headers = ['N° client','N° Facture','N° contrat', 'Montant HT', 'TVA ', 'TTC ']
        
        # Données du tableau
        table_data = [headers]
        
        for invoice in client.invoices:
            row = [
                client.number,                      
                invoice.invoice_number,             
                invoice.contrat_number,
                f"{invoice.amount_ht:.2f}",
                f"{invoice.amount_tva:.2f}",
                f"{invoice.amount_ttc:.2f}"
            ]
            table_data.append(row)
        
        # Créer le tableau
        table = Table(table_data, colWidths=[30*mm,30*mm,30*mm, 30*mm, 25*mm, 30*mm])
        
        # Style du tableau
        table.setStyle(TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            
            # Corps du tableau
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Montants alignés à droite
            
            # Bordures
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
            
            # Alternance de couleurs
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
    
    def add_totals(self, story, client: Client):
        """Ajoute les totaux"""
        totals_data = [
            ['', '', 'TOTAL HT:', f"{client.total_ht:.2f} "],
            ['', '', 'TOTAL TVA:', f"{client.total_tva:.2f} "],
            ['', '', 'TOTAL TTC:', f"{client.total_ttc:.2f} "]
        ]
        
        totals_table = Table(totals_data, colWidths=[30*mm,30*mm,30*mm, 30*mm, 30*mm, 35*mm])
        
        totals_table.setStyle(TableStyle([
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (2, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, 0), (-1, -1), 12),
            ('TEXTCOLOR', (2, -1), (-1, -1), colors.HexColor('#1f4e79')),
            ('FONTSIZE', (2, -1), (-1, -1), 14),
            ('LINEABOVE', (2, -1), (-1, -1), 2, colors.HexColor('#1f4e79')),
        ]))
        
        story.append(totals_table)
        story.append(Spacer(1, 30))
    
    def add_footer(self, story):
        """Ajoute le pied de page"""
        footer_text = """
        <i>Cette facture globale regroupe toutes les factures émises pour ce client.<br/>
        </i>
        """
        
        footer = Paragraph(footer_text, self.styles['Normal'])
        story.append(footer)