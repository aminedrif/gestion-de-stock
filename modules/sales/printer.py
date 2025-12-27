# -*- coding: utf-8 -*-
"""
Système d'impression de tickets
"""
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
import config
from core.logger import logger
from .receipt import receipt_generator

try:
    from escpos.printer import Serial, Usb, Network, File
    ESCPOS_AVAILABLE = True
except ImportError:
    ESCPOS_AVAILABLE = False
    logger.warning("Module python-escpos non disponible. Impression thermique désactivée.")


class PrinterManager:
    """Gestionnaire d'impression"""
    
    def __init__(self):
        self.printer_config = config.PRINTER_CONFIG
        self.thermal_printer = None
    
    def setup_thermal_printer(self, port: str = None) -> bool:
        """
        Configurer l'imprimante thermique
        
        Args:
            port: Port série (ex: 'COM1', '/dev/ttyUSB0')
            
        Returns:
            True si succès
        """
        if not ESCPOS_AVAILABLE:
            logger.error("Module python-escpos non installé")
            return False
        
        try:
            port = port or self.printer_config.get('thermal_printer_port', 'COM1')
            
            # Essayer de se connecter à l'imprimante série
            self.thermal_printer = Serial(port)
            logger.info(f"Imprimante thermique configurée sur {port}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la configuration de l'imprimante thermique: {e}")
            return False
    
    def print_receipt(self, sale_data: Dict, method: str = None) -> tuple[bool, str]:
        """
        Imprimer un ticket
        
        Args:
            sale_data: Données de la vente
            method: Méthode d'impression ('thermal', 'pdf', 'standard', 'direct')
            
        Returns:
            (success, message)
        """
        method = method or self.printer_config.get('default_printer', 'DIRECT')
        method = method.upper()
        
        if method == 'THERMAL':
            return self._print_thermal(sale_data)
        elif method == 'PDF':
            return self._print_pdf(sale_data)
        elif method == 'STANDARD':
            return self._print_standard(sale_data)
        elif method == 'DIRECT':
            return self._print_direct(sale_data)
        else:
            return False, f"Méthode d'impression inconnue: {method}"
    
    def _print_thermal(self, sale_data: Dict) -> tuple[bool, str]:
        """
        Imprimer sur imprimante thermique ESC/POS
        
        Args:
            sale_data: Données de la vente
            
        Returns:
            (success, message)
        """
        if not ESCPOS_AVAILABLE:
            return False, "Module python-escpos non installé"
        
        if not self.thermal_printer:
            # Essayer de configurer l'imprimante
            if not self.setup_thermal_printer():
                return False, "Imprimante thermique non configurée"
        
        try:
            # Générer le ticket en texte
            receipt_text = receipt_generator.generate_text_receipt(sale_data)
            
            # Imprimer
            self.thermal_printer.text(receipt_text)
            self.thermal_printer.cut()
            
            logger.info(f"Ticket imprimé (thermique): {sale_data['sale_number']}")
            return True, "Ticket imprimé avec succès"
            
        except Exception as e:
            error_msg = f"Erreur lors de l'impression thermique: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _print_pdf(self, sale_data: Dict) -> tuple[bool, str]:
        """
        Générer et ouvrir un PDF
        
        Args:
            sale_data: Données de la vente
            
        Returns:
            (success, message)
        """
        try:
            # Créer le dossier de tickets s'il n'existe pas
            receipts_dir = config.DATA_DIR / "receipts"
            receipts_dir.mkdir(exist_ok=True)
            
            # Générer le nom du fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ticket_{sale_data['sale_number']}_{timestamp}.pdf"
            output_path = receipts_dir / filename
            
            # Générer le PDF
            success = receipt_generator.generate_pdf_receipt(sale_data, output_path)
            
            if success:
                logger.info(f"Ticket PDF généré: {output_path}")
                
                # Ouvrir le PDF automatiquement
                import os
                os.startfile(str(output_path))
                
                return True, f"Ticket PDF généré: {filename}"
            else:
                return False, "Erreur lors de la génération du PDF"
                
        except Exception as e:
            error_msg = f"Erreur lors de la génération du PDF: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _print_standard(self, sale_data: Dict) -> tuple[bool, str]:
        """
        Imprimer sur imprimante standard (via PyQt5)
        
        Args:
            sale_data: Données de la vente
            
        Returns:
            (success, message)
        """
        try:
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
            from PyQt5.QtGui import QTextDocument
            from PyQt5.QtWidgets import QApplication
            
            # Générer le HTML
            html = receipt_generator.generate_html_receipt(sale_data)
            
            # Créer un document
            document = QTextDocument()
            document.setHtml(html)
            
            # Configurer l'imprimante
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)
            
            # Afficher le dialogue d'impression
            app = QApplication.instance()
            parent = app.activeWindow() if app else None
            dialog = QPrintDialog(printer, parent)
            if dialog.exec_() == QPrintDialog.Accepted:
                document.print_(printer)
                logger.info(f"Ticket imprimé (standard): {sale_data['sale_number']}")
                return True, "Ticket imprimé avec succès"
            else:
                return False, "Impression annulée"
                
        except Exception as e:
            error_msg = f"Erreur lors de l'impression standard: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _print_direct(self, sale_data: Dict) -> tuple[bool, str]:
        """
        Imprimer DIRECTEMENT sur l'imprimante par défaut (sans dialogue)
        
        Args:
            sale_data: Données de la vente
            
        Returns:
            (success, message)
        """
        try:
            from PyQt5.QtPrintSupport import QPrinter, QPrinterInfo
            from PyQt5.QtGui import QTextDocument
            from PyQt5.QtWidgets import QApplication
            
            # Générer le HTML
            html = receipt_generator.generate_html_receipt(sale_data)
            
            # Créer un document
            document = QTextDocument()
            document.setHtml(html)
            
            # Obtenir l'imprimante par défaut
            default_printer = QPrinterInfo.defaultPrinter()
            if default_printer.isNull():
                return False, "Aucune imprimante par défaut configurée"
            
            # Configurer l'imprimante
            printer = QPrinter(default_printer, QPrinter.HighResolution)
            
            # Imprimer directement
            document.print_(printer)
            
            logger.info(f"Ticket imprimé directement: {sale_data['sale_number']}")
            return True, "Ticket imprimé avec succès"
                
        except Exception as e:
            error_msg = f"Erreur lors de l'impression directe: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def preview_receipt(self, sale_data: Dict) -> str:
        """
        Générer un aperçu HTML du ticket
        
        Args:
            sale_data: Données de la vente
            
        Returns:
            HTML du ticket
        """
        return receipt_generator.generate_html_receipt(sale_data)
    
    def save_receipt_copy(self, sale_data: Dict, format: str = 'pdf') -> tuple[bool, str, Optional[Path]]:
        """
        Sauvegarder une copie du ticket
        
        Args:
            sale_data: Données de la vente
            format: Format ('pdf', 'txt', 'html')
            
        Returns:
            (success, message, file_path)
        """
        try:
            # Créer le dossier de tickets
            receipts_dir = config.DATA_DIR / "receipts"
            receipts_dir.mkdir(exist_ok=True)
            
            # Générer le nom du fichier
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ticket_{sale_data['sale_number']}_{timestamp}.{format}"
            output_path = receipts_dir / filename
            
            if format == 'pdf':
                success = receipt_generator.generate_pdf_receipt(sale_data, output_path)
            elif format == 'txt':
                text = receipt_generator.generate_text_receipt(sale_data)
                output_path.write_text(text, encoding='utf-8')
                success = True
            elif format == 'html':
                html = receipt_generator.generate_html_receipt(sale_data)
                output_path.write_text(html, encoding='utf-8')
                success = True
            else:
                return False, f"Format non supporté: {format}", None
            
            if success:
                logger.info(f"Copie du ticket sauvegardée: {output_path}")
                return True, f"Ticket sauvegardé: {filename}", output_path
            else:
                return False, "Erreur lors de la sauvegarde", None
                
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None


# Instance globale
printer_manager = PrinterManager()
