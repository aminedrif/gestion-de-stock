# -*- coding: utf-8 -*-
"""
Module de génération de rapport de commande fournisseur
"""
import os
import subprocess
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from database.db_manager import db
from core.logger import logger
import config

def generate_reorder_report():
    """Générer un PDF de liste de commande basé sur le stock faible"""
    try:
        # 1. Récupérer les produits en stock faible avec infos fournisseur
        query = """
            SELECT p.name, p.stock_quantity, p.min_stock_level, 
                   s.company_name as supplier_name
            FROM products p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.stock_quantity <= p.min_stock_level 
              AND p.is_active = 1
            ORDER BY s.company_name, p.name
        """
        results = db.execute_query(query)
        
        if not results:
            return False, "Aucun produit en stock faible."
            
        # 2. Préparer le PDF
        config.DATA_DIR.mkdir(exist_ok=True)
        report_dir = config.DATA_DIR / "reports"
        report_dir.mkdir(exist_ok=True)
        
        filename = report_dir / f"commande_fournisseur_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(str(filename), pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        )
        elements.append(Paragraph("Liste de Commande Fournisseur", title_style))
        
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#7f8c8d')
        )
        elements.append(Paragraph(f"Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_style))
        elements.append(Spacer(1, 30))
        
        # 3. Organiser les données par fournisseur
        data_by_supplier = {}
        for row in results:
            supplier = row['supplier_name'] if row['supplier_name'] else "Fournisseur Inconnu"
            if supplier not in data_by_supplier:
                data_by_supplier[supplier] = []
            
            # Calculer quantité suggérée (par exemple: pour atteindre 2x min_stock)
            suggested = (row['min_stock_level'] * 2) - row['stock_quantity']
            if suggested < 0: suggested = 0
            
            data_by_supplier[supplier].append([
                row['name'],
                str(row['stock_quantity']),
                str(row['min_stock_level']),
                "" # Espace pour noter la quantité commandée
            ])

        # 4. Créer les tableaux
        for supplier, items in data_by_supplier.items():
            # Titre Fournisseur
            supplier_style = ParagraphStyle(
                'SupplierTitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=15,
                spaceAfter=10,
                textColor=colors.HexColor('#3498db')
            )
            elements.append(Paragraph(f"🏢 {supplier}", supplier_style))
            
            # En-têtes du tableau
            table_data = [['Produit', 'Stock Actuel', 'Stock Min', 'Qté à Commander']]
            table_data.extend(items)
            
            # Style du tableau
            t = Table(table_data, colWidths=[250, 80, 80, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0')),
                ('ALIGN', (3, 1), (3, -1), 'LEFT'), # Colonne à écrire vide ou avec guides
            ]))
            elements.append(t)
            elements.append(Spacer(1, 15))
            
        # Générer
        doc.build(elements)
        
        # Ouvrir le fichier
        if os.name == 'nt':
            os.startfile(str(filename))
        else:
            subprocess.run(['xdg-open', str(filename)])
            
        return True, f"Rapport généré: {filename}"
        
    except ImportError:
        return False, "Le module 'reportlab' est requis."
    except Exception as e:
        logger.error(f"Erreur génération rapport commande: {e}")
        return False, str(e)
