# -*- coding: utf-8 -*-
"""
Interface Point de Vente (POS)
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QSpinBox,
                             QDoubleSpinBox, QGroupBox, QGridLayout, QDialog,
                             QFormLayout, QInputDialog, QAbstractItemView, QShortcut, QTextBrowser,
                             QCheckBox, QCompleter)
from PyQt5.QtCore import Qt, QTimer, QStringListModel
# ... imports ...
from modules.sales.printer import printer_manager

class ReceiptPreviewDialog(QDialog):
    """Dialogue d'aperçu du ticket"""
    def __init__(self, sale_data, parent=None):
        super().__init__(parent)
        self.sale_data = sale_data
        self.setWindowTitle(f"Aperçu Ticket #{sale_data['sale_number']}")
        self.setMinimumSize(400, 600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Aperçu HTML
        self.preview = QTextBrowser()
        html = printer_manager.preview_receipt(self.sale_data)
        self.preview.setHtml(html)
        layout.addWidget(self.preview)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        print_btn = QPushButton("🖨️ Imprimer")
        print_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
        print_btn.clicked.connect(self.print_ticket)
        
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def print_ticket(self):
        success, msg = printer_manager.print_receipt(self.sale_data)
        if success:
            QMessageBox.information(self, "Succès", msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Erreur", msg)
from PyQt5.QtGui import QFont, QColor, QKeySequence
from datetime import datetime
from modules.products.product_manager import product_manager
from modules.sales.cart import Cart
from modules.sales.pos import pos_manager
from modules.customers.customer_manager import customer_manager
from modules.sales.printer import printer_manager
from core.auth import auth_manager
from core.logger import logger


class ReturnDialog(QDialog):
    """Dialogue de gestion des retours"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestion des Retours / Annulations")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.sale_data = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Recherche Vente
        search_layout = QHBoxLayout()
        self.sale_id_input = QLineEdit()
        self.sale_id_input.setPlaceholderText("ID Vente ou Numéro Ticket...")
        search_btn = QPushButton("🔍 Rechercher")
        search_btn.clicked.connect(self.search_sale)
        
        search_layout.addWidget(QLabel("Vente:"))
        search_layout.addWidget(self.sale_id_input)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        
        # Info Vente
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("font-weight: bold; color: #34495e;")
        layout.addWidget(self.info_label)
        
        # Liste articles
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels(["Produit", "Qté Achetée", "Prix Unit.", "Qté Retour", "Sélection"])
        self.items_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.items_table)
        
        # Actions
        btn_layout = QHBoxLayout()
        cancel_sale_btn = QPushButton("🗑️ Annuler TOUTE la vente")
        cancel_sale_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        cancel_sale_btn.clicked.connect(self.cancel_entire_sale)
        
        process_return_btn = QPushButton("↩️ Retourner les articles sélectionnés")
        process_return_btn.setStyleSheet("background-color: #f39c12; color: white;")
        process_return_btn.clicked.connect(self.process_partial_return)
        
        btn_layout.addWidget(cancel_sale_btn)
        
        reprint_btn = QPushButton("🖨️ Réimprimer Ticket")
        reprint_btn.setStyleSheet("background-color: #3498db; color: white;")
        reprint_btn.clicked.connect(self.reprint_ticket)
        btn_layout.addWidget(reprint_btn)
        
        btn_layout.addWidget(process_return_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def search_sale(self):
        term = self.sale_id_input.text().strip()
        if not term:
            return
            
        # Essayer de trouver par ID ou Numéro
        # Pour simplifier, on suppose que l'utilisateur entre l'ID numérique
        # Pour une vraie recherche par numéro (VNT-...), il faudrait une méthode search_sale dans pos_manager
        
        # Hack temporaire: Si c'est numérique, c'est l'ID. Sinon c'est complexe sans méthode de recherche dédiée.
        # On va utiliser pos_manager.get_sale(id) si numérique.
        
        if term.isdigit():
            sale = pos_manager.get_sale(int(term))
        else:
            # TODO: Implémenter get_sale_by_number dans pos_manager
            QMessageBox.warning(self, "Info", "Recherche par numéro non implémentée, utilisez l'ID de vente (affiché dans les logs ou base)")
            return
            
        if sale:
            self.sale_data = sale
            self.display_sale()
        else:
            QMessageBox.warning(self, "Erreur", "Vente introuvable")
            
    def display_sale(self):
        if not self.sale_data:
            return
            
        self.info_label.setText(f"Vente #{self.sale_data['sale_number']} - Total: {self.sale_data['total_amount']} DA - Date: {self.sale_data['sale_date']}")
        
        self.items_table.setRowCount(0)
        items = self.sale_data.get('items', [])
        
        for item in items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)
            
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            self.items_table.setItem(row, 1, QTableWidgetItem(str(item['quantity'])))
            self.items_table.setItem(row, 2, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            
            # SpinBox pour quantité retour
            spin = QDoubleSpinBox()
            spin.setRange(0, item['quantity'])
            spin.setValue(0)
            self.items_table.setCellWidget(row, 3, spin)
            
            # Checkbox
            chk = QTableWidgetItem()
            chk.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk.setCheckState(Qt.Unchecked)
            self.items_table.setItem(row, 4, chk)
            
    def cancel_entire_sale(self):
        if not self.sale_data:
            return
            
        confirm = QMessageBox.question(self, "Confirmer", "Annuler TOTALEMENT cette vente ? Stock sera restauré.", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            success, msg = pos_manager.cancel_sale(self.sale_data['id'], "Annulation utilisateur")
            if success:
                QMessageBox.information(self, "Succès", msg)
                self.accept()
            else:
                QMessageBox.critical(self, "Erreur", msg)
                
    def process_partial_return(self):
        if not self.sale_data:
            return
            
        items_to_return = []
        rows = self.items_table.rowCount()
        original_items = self.sale_data.get('items', [])
        
        for i in range(rows):
            if self.items_table.item(i, 4).checkState() == Qt.Checked:
                qty = self.items_table.cellWidget(i, 3).value()
                if qty > 0:
                    # Trouver l'ID produit correspondant (supposons l'ordre conservé ou on stocke l'ID)
                    # Mieux: stocker l'ID dans UserRole
                    # Pour simplifier ici, on utilise l'index
                    product_id = original_items[i]['product_id']
                    items_to_return.append({'product_id': product_id, 'quantity': qty})
        
        if not items_to_return:
            QMessageBox.warning(self, "Info", "Aucun article sélectionné ou quantité nulle")
            return
            
        user = auth_manager.get_current_user()
        user_id = user['id'] if user else 1
            
        success, msg, ret_id = pos_manager.process_return(
            self.sale_data['id'], items_to_return, user_id, "Retour partiel"
        )
        
        if success:
            QMessageBox.information(self, "Succès", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)

    def reprint_ticket(self):
        """Réimprimer le ticket de la vente affichée"""
        if not self.sale_data:
            return
            
        printer_manager.print_receipt(self.sale_data, "standard")


class POSPage(QWidget):
    """Page Point de Vente"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cart = pos_manager.get_cart()
        self.current_customer = None
        self.init_ui()
        
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Colonne gauche - Scanner et produits
        self.left_panel_container = self.create_left_panel()
        layout.addWidget(self.left_panel_container, 1) # Equal width
        
        # Colonne droite - Panier et paiement
        self.right_panel_container = self.create_right_panel()
        layout.addWidget(self.right_panel_container, 1) # Equal width
        
        self.setLayout(layout)
        
        # Focus sur le scanner
        self.barcode_input.setFocus()

        # Raccourcis Clavier POS
        QShortcut(QKeySequence("F9"), self, self.process_payment) # F9 pour payer
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.search_input.setFocus()) # Ctrl+F pour recherche
        QShortcut(QKeySequence("Ctrl+Space"), self, lambda: self.barcode_input.setFocus()) # Ctrl+Espace pour scanner
    
    def create_left_panel(self):
        """Créer le panneau gauche"""
        panel = QFrame()
        panel.setObjectName("leftPanel")
        panel.setStyleSheet("""
            QFrame#leftPanel {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e5e7eb;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # En-tête avec TOTAL et Remise (grand)
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #8b5cf6, stop:1 #6366f1);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 10px;
            }
        """)
        header_layout_inner = QVBoxLayout(header_frame)
        
        # Label TOTAL (très grand)
        self.header_total_label = QLabel("TOTAL: 0.00 DA")
        self.header_total_label.setStyleSheet("font-size: 38px; font-weight: bold; color: white; background: transparent;")
        header_layout_inner.addWidget(self.header_total_label)
        
        # Label Remise (sous le total)
        self.header_discount_label = QLabel("Remise: 0.00 DA")
        self.header_discount_label.setStyleSheet("font-size: 16px; color: #fbbf24; background: transparent;")
        header_layout_inner.addWidget(self.header_discount_label)
        
        layout.addWidget(header_frame)
        
        # Scanner code-barres
        scanner_group = QGroupBox("Scanner Code-Barres")
        scanner_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                margin-top: 10px;
                padding: 20px 15px 15px 15px;
                background-color: #fafafa;
            }
            QGroupBox::title {
                color: #8b5cf6;
                subcontrol-position: top left;
                padding: 5px 10px;
            }
        """)
        scanner_layout = QVBoxLayout()
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("Scanner ou entrer le code-barres...")
        self.barcode_input.setMinimumHeight(50)
        self.barcode_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 18px;
                border: 2px solid #8b5cf6;
                border-radius: 10px;
                font-size: 16px;
                background-color: white;
                color: #1f2937;
            }
            QLineEdit:focus {
                border-color: #6366f1;
                background-color: #faf5ff;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)
        self.barcode_input.returnPressed.connect(self.scan_product)
        # Auto-scan après un court délai (pour scanners automatiques)
        self.scan_timer = QTimer()
        self.scan_timer.setSingleShot(True)
        self.scan_timer.timeout.connect(self.auto_scan_product)
        self.barcode_input.textChanged.connect(self.on_barcode_text_changed)
        scanner_layout.addWidget(self.barcode_input)
        scanner_group.setLayout(scanner_layout)
        layout.addWidget(scanner_group)
        
        # Recherche produit
        search_group = QGroupBox("Recherche Produit")
        search_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #3498db;
            }
        """)
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher par nom...")
        self.search_input.setMinimumHeight(45)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍")
        search_btn.setMinimumSize(45, 45)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_btn.clicked.connect(self.search_products)
        search_layout.addWidget(search_btn)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Liste des produits trouvés
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["Code", "Nom", "Prix", "Stock", "Action"])
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Read-only
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                gridline-color: #f0f0f0;
                color: #333;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                font-weight: bold;
                color: #333;
            }
        """)
        layout.addWidget(self.products_table)
        
        # Calculatrice intégrée (Montant Libre) - EN BAS
        calc_group = QGroupBox("🧮 Calculatrice (Montant Libre)")
        calc_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8fff8;
            }
            QGroupBox::title {
                color: #27ae60;
            }
        """)
        calc_layout = QVBoxLayout()
        
        # Écran d'affichage
        self.calc_display = QLineEdit("0")
        self.calc_display.setReadOnly(True)
        self.calc_display.setAlignment(Qt.AlignRight)
        self.calc_display.setMinimumHeight(50)
        self.calc_display.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold;
            padding: 8px; 
            border: 2px solid #27ae60; 
            border-radius: 8px;
            background-color: #e8f5e9;
            color: #2c3e50;
        """)
        calc_layout.addWidget(self.calc_display)
        
        # Grille de boutons
        calc_grid = QGridLayout()
        calc_grid.setSpacing(4)
        
        calc_buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 0), ('00', 3, 1), ('C', 3, 2),
        ]
        
        for text, row, col in calc_buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    font-weight: bold;
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)
            if text == 'C':
                btn.setStyleSheet(btn.styleSheet() + "background-color: #ffcccc; color: #c0392b;")
                btn.clicked.connect(self.calc_clear)
            else:
                btn.clicked.connect(lambda checked, t=text: self.calc_add_digit(t))
            calc_grid.addWidget(btn, row, col)
        
        calc_layout.addLayout(calc_grid)
        
        # Bouton Ajouter au panier
        calc_add_btn = QPushButton("✅ AJOUTER AU PANIER")
        calc_add_btn.setMinimumHeight(50)
        calc_add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        calc_add_btn.clicked.connect(self.add_from_calculator)
        calc_layout.addWidget(calc_add_btn)
        
        calc_group.setLayout(calc_layout)
        layout.addWidget(calc_group)
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Créer le panneau droit"""
        panel = QFrame()
        panel.setObjectName("rightPanel")
        panel.setStyleSheet("""
            QFrame#rightPanel {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Client - avec recherche clavier
        customer_group = QGroupBox("👤 Client")
        customer_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        customer_layout = QHBoxLayout()
        
        self.customer_combo = QComboBox()
        self.customer_combo.setMinimumHeight(50)
        self.customer_combo.setEditable(True)  # Permet la recherche au clavier
        self.customer_combo.lineEdit().setPlaceholderText("🔍 Rechercher un client (optionnel)...")
        self.customer_combo.setInsertPolicy(QComboBox.NoInsert)
        self.load_customers()
        self.customer_combo.setCurrentIndex(-1)  # Aucune sélection = champ vide
        self.customer_combo.setStyleSheet("""
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 15px;
                color: #333;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                color: #333;
                font-size: 14px;
                background-color: white;
                selection-background-color: #ede9fe;
            }
            QComboBox::drop-down {
                width: 40px;
            }
        """)
        customer_layout.addWidget(self.customer_combo)
        
        # Bouton Vider sélection
        self.clear_customer_btn = QPushButton("❌")
        self.clear_customer_btn.setFixedSize(50, 50)
        self.clear_customer_btn.setToolTip("Réinitialiser (Aucun client)")
        self.clear_customer_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                color: #555;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
                color: #e74c3c;
            }
        """)
        self.clear_customer_btn.clicked.connect(self.clear_customer_selection)
        customer_layout.addWidget(self.clear_customer_btn)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Panier
        cart_label = QLabel("🛒 Panier")
        cart_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #8b5cf6; margin-top: 10px;")
        layout.addWidget(cart_label)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Produit", "Prix", "Qté", "Total", "❌"])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # Read-only
        self.cart_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                gridline-color: #f3f4f6;
                color: #1f2937;
                background-color: white;
                selection-background-color: #ede9fe;
            }
            QHeaderView::section {
                background-color: #f5f3ff;
                padding: 10px;
                font-weight: bold;
                color: #6b21a8;
                border: none;
                border-bottom: 2px solid #e5e7eb;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        layout.addWidget(self.cart_table)
        
        # Totaux
        # Totaux supprimés du panneau droit pour laisser plus de place au panier
        # (Déplacés vers le header gauche)
        
        # Paiement
        payment_group = QGroupBox("💳 Paiement")
        payment_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
        """)
        payment_layout = QVBoxLayout()
        
        self.payment_method = QComboBox()
        self.payment_method.addItem("💵 Espèces", "cash")
        # Carte supprimée à la demande
        self.payment_method.addItem("📝 Crédit", "credit")
        self.payment_method.setMinimumHeight(40)
        self.payment_method.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                color: #333;
            }
            QComboBox QAbstractItemView {
                color: #333;
            }
        """)
        payment_layout.addWidget(self.payment_method)
        
        # Checkbox pour imprimer le ticket
        self.print_receipt_cb = QCheckBox("🖨️ Imprimer le ticket")
        self.print_receipt_cb.setChecked(True)
        self.print_receipt_cb.setStyleSheet("font-size: 14px; padding: 5px;")
        payment_layout.addWidget(self.print_receipt_cb)
        
        payment_group.setLayout(payment_layout)
        layout.addWidget(payment_group)
        
        # Boutons d'action - Plus gros pour écran tactile
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(12)
        
        # Bouton Payer - TRÈS GRAND pour écran tactile
        pay_btn = QPushButton("💰 PAYER (F9)")
        pay_btn.setMinimumHeight(80)
        pay_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 14px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #059669, stop:1 #047857);
            }
            QPushButton:pressed {
                background: #047857;
            }
        """)
        pay_btn.clicked.connect(self.process_payment)
        buttons_layout.addWidget(pay_btn)
        
        # Boutons secondaires - Plus gros
        secondary_layout = QHBoxLayout()
        secondary_layout.setSpacing(10)
        
        clear_btn = QPushButton("🗑️ Vider")
        clear_btn.setMinimumHeight(55)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self.clear_cart)
        secondary_layout.addWidget(clear_btn)

        
        discount_btn = QPushButton("🏷️ Remise")
        discount_btn.setMinimumHeight(55)
        discount_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        discount_btn.clicked.connect(self.apply_discount)
        secondary_layout.addWidget(discount_btn)
        
        # Bouton Retour
        return_btn = QPushButton("↩️ Retour")
        return_btn.setMinimumHeight(55)
        return_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        return_btn.clicked.connect(self.open_returns)
        secondary_layout.addWidget(return_btn)
        
        buttons_layout.addLayout(secondary_layout)
        layout.addLayout(buttons_layout)
        
        panel.setLayout(layout)
        return panel
    
    def set_dark_mode(self, is_dark):
        """Appliquer le mode sombre"""
        if is_dark:
            # Mode sombre
            main_bg = "#2c3e50"
            panel_bg = "#34495e"
            text_color = "white"
            input_bg = "#2c3e50"
            
            self.left_panel_container.setStyleSheet(f"""
                QFrame#leftPanel {{
                    background-color: {panel_bg};
                    border-radius: 10px;
                    padding: 15px;
                    color: {text_color};
                }}
            """)
            
            self.right_panel_container.setStyleSheet(f"""
                QFrame#rightPanel {{
                    background-color: {panel_bg};
                    border-radius: 10px;
                    padding: 15px;
                    color: {text_color};
                }}
            """)
            
            # Mise à jour des tables
            table_style = f"""
                QTableWidget {{
                    border: 2px solid #555;
                    border-radius: 8px;
                    background-color: #2c3e50;
                    gridline-color: #555;
                    color: white;
                }}
                QHeaderView::section {{
                    background-color: #455a64;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                    color: white;
                }}
            """
            self.products_table.setStyleSheet(table_style)
            self.cart_table.setStyleSheet(table_style)
            
            # Mise à jour des inputs
            input_style = f"""
                QLineEdit {{
                    padding: 10px 15px;
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    font-size: 16px;
                    background-color: #2c3e50;
                    color: white;
                }}
            """
            self.barcode_input.setStyleSheet(input_style)
            self.search_input.setStyleSheet(input_style.replace("16px", "14px").replace("#667eea", "white"))
            
            # ComboBoxes
            combo_style = """
                QComboBox {
                    padding: 8px 12px;
                    border: 2px solid #555;
                    border-radius: 6px;
                    font-size: 14px;
                    color: white;
                    background-color: #2c3e50;
                }
                QComboBox QAbstractItemView {
                    background-color: #2c3e50;
                    color: white;
                    selection-background-color: #667eea;
                }
            """
            self.customer_combo.setStyleSheet(combo_style)
            self.payment_method.setStyleSheet(combo_style)
            
            if hasattr(self, 'clear_customer_btn'):
                self.clear_customer_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #34495e;
                        border: 1px solid #555;
                        border-radius: 8px;
                        font-weight: bold;
                        color: #ecf0f1;
                    }
                    QPushButton:hover {
                        background-color: #4a6785;
                        color: #e74c3c;
                    }
                """)
            
        else:
            # Mode clair (reset aux styles d'origine)
            self.left_panel_container.setStyleSheet("""
                QFrame#leftPanel {
                    background-color: white;
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            self.right_panel_container.setStyleSheet("""
                QFrame#rightPanel {
                    background-color: white;
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            
            # Tables
            table_style = """
                QTableWidget {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: white;
                    gridline-color: #f0f0f0;
                    color: #333;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                    color: #333;
                }
            """
            self.products_table.setStyleSheet(table_style)
            self.cart_table.setStyleSheet(table_style)
            
            # Inputs
            input_style = """
                QLineEdit {
                    padding: 10px 15px;
                    border: 2px solid #667eea;
                    border-radius: 8px;
                    font-size: 16px;
                    background-color: #f0f4ff;
                    color: #333;
                }
            """
            self.barcode_input.setStyleSheet(input_style)
            
            # Combo
            combo_style = """
                QComboBox {
                    padding: 8px 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    font-size: 14px;
                    color: #333;
                }
            """
            self.customer_combo.setStyleSheet(combo_style)
            self.payment_method.setStyleSheet(combo_style)
            
            if hasattr(self, 'clear_customer_btn'):
                self.clear_customer_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e0e0e0;
                        border: none;
                        border-radius: 8px;
                        font-weight: bold;
                        color: #555;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                        color: #e74c3c;
                    }
                """)

    def load_customers(self):
        """Charger la liste des clients"""
        try:
            customers = customer_manager.get_all_customers()
            for customer in customers:
                self.customer_combo.addItem(
                    f"{customer['full_name']} ({customer['code']})",
                    customer['id']
                )
        except Exception as e:
            logger.error(f"Erreur chargement clients: {e}")
    
    def scan_product(self):
        """Scanner un produit par code-barres"""
        barcode = self.barcode_input.text().strip()
        if not barcode:
            return
        
        try:
            product = product_manager.get_product_by_barcode(barcode)
            if product:
                self.add_to_cart(product)
                self.barcode_input.clear()
            else:
                QMessageBox.warning(self, "Produit introuvable", 
                                  f"Aucun produit avec le code-barres: {barcode}")
                self.barcode_input.clear()
        except Exception as e:
            logger.error(f"Erreur scan produit: {e}")
            QMessageBox.critical(self, "Erreur", f"Erreur lors du scan: {e}")
    
    def on_barcode_text_changed(self, text):
        """Démarrer le timer pour auto-scan"""
        if text.strip():
            # Redémarrer le timer à chaque frappe
            self.scan_timer.start(300)  # 300ms délai
        else:
            self.scan_timer.stop()
    
    def auto_scan_product(self):
        """Auto-scan du produit après délai"""
        barcode = self.barcode_input.text().strip()
        if barcode and len(barcode) >= 3:  # Au moins 3 caractères
            self.scan_product()
    
    def search_products(self):
        """Rechercher des produits"""
        search_term = self.search_input.text().strip()
        
        try:
            products = product_manager.search_products(search_term) if search_term else []
            self.display_products(products)
        except Exception as e:
            logger.error(f"Erreur recherche produits: {e}")
    
    def display_products(self, products):
        """Afficher les produits trouvés"""
        self.products_table.setRowCount(0)
        self.last_search_results = products  # Stocker pour double-click
        
        for i, product in enumerate(products):
            row = self.products_table.rowCount()
            self.products_table.insertRow(row)
            
            self.products_table.setItem(row, 0, QTableWidgetItem(product['barcode'] or ''))
            self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))
            self.products_table.setItem(row, 2, QTableWidgetItem(f"{product['selling_price']:.2f} DA"))
            item_stock = QTableWidgetItem(str(product['stock_quantity']))
            if product['stock_quantity'] <= product['min_stock_level']:
                 item_stock.setForeground(QColor("red"))
            self.products_table.setItem(row, 3, item_stock)
            
            # Bouton Ajouter
            add_btn = QPushButton("➕ Ajouter")
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            add_btn.clicked.connect(lambda checked, p=product: self.add_to_cart(p))
            self.products_table.setCellWidget(row, 4, add_btn)

    def on_product_double_click(self, row, column):
        """Ajouter au panier sur double click"""
        if hasattr(self, 'last_search_results') and 0 <= row < len(self.last_search_results):
            product = self.last_search_results[row]
            self.add_to_cart(product)

    def add_to_cart(self, product):
        """Ajouter un produit au panier"""
        try:
            success, message = self.cart.add_item(product, 1)
            
            if success:
                self.update_cart_display()
                logger.info(f"Produit ajouté au panier: {product['name']}")
            else:
                logger.warning(f"Échec ajout panier ({product['name']}): {message}")
                QMessageBox.warning(self, "Impossible d'ajouter", message)
                
        except Exception as e:
            logger.error(f"Erreur ajout panier: {e}")
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    
    def update_cart_display(self):
        """Mettre à jour l'affichage du panier"""
        self.cart_table.setRowCount(0)
        
        for item in self.cart.items:
            row = self.cart_table.rowCount()
            self.cart_table.insertRow(row)
            
            self.cart_table.setItem(row, 0, QTableWidgetItem(item.product_name))
            self.cart_table.setItem(row, 1, QTableWidgetItem(f"{item.unit_price:.2f}"))
            self.cart_table.setItem(row, 2, QTableWidgetItem(str(item.quantity)))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{item.get_subtotal():.2f}"))
            
            # Bouton supprimer
            remove_btn = QPushButton("❌")
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 4px;
                }
            """)
            remove_btn.clicked.connect(lambda checked, pid=item.product_id: self.remove_from_cart(pid))
            self.cart_table.setCellWidget(row, 4, remove_btn)
        
        # Mettre à jour les totaux (dans le header gauche)
        discount = self.cart.get_discount_amount()
        total = self.cart.get_total()
        
        self.header_discount_label.setText(f"Remise: {discount:.2f} DA")
        self.header_total_label.setText(f"TOTAL: {total:.2f} DA")
    
    def remove_from_cart(self, product_id):
        """Retirer un produit du panier"""
        self.cart.remove_item(product_id)
        self.update_cart_display()
    
    def clear_customer_selection(self):
        """Réinitialiser la sélection client"""
        self.customer_combo.setCurrentIndex(-1)  # Vider le champ = aucun client
    
    def clear_cart(self):
        """Vider le panier"""
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment vider le panier ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cart.clear()
            self.update_cart_display()
    
    def apply_discount(self):
        """Appliquer une remise"""
        discount, ok = QInputDialog.getDouble(
            self, "Remise",
            "Montant de la remise (DA):",
            0, 0, 100000, 2
        )
        
        if ok:
            success, message = self.cart.set_discount_amount(discount)
            if success:
                self.update_cart_display()
            else:
                QMessageBox.warning(self, "Erreur", message)
                
    def open_returns(self):
        """Ouvrir le dialogue de retours"""
        dialog = ReturnDialog(self)
        dialog.exec_()
    
    def add_custom_product(self):
        """Ajouter un produit personnalisé (non référencé dans la base)"""
        dialog = QDialog(self)
        dialog.setWindowTitle("➕ Ajouter un Produit Personnalisé")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        form = QFormLayout()
        
        # Champs
        name_input = QLineEdit()
        name_input.setPlaceholderText("Ex: Service, Réparation, Article divers...")
        name_input.setMinimumHeight(40)
        
        price_input = QDoubleSpinBox()
        price_input.setRange(0, 999999)
        price_input.setDecimals(2)
        price_input.setSuffix(" DA")
        price_input.setMinimumHeight(40)
        price_input.setStyleSheet("font-size: 16px;")
        
        qty_input = QDoubleSpinBox()
        qty_input.setRange(0.01, 1000)
        qty_input.setValue(1)
        qty_input.setMinimumHeight(40)
        
        form.addRow("Nom du produit:", name_input)
        form.addRow("Prix unitaire:", price_input)
        form.addRow("Quantité:", qty_input)
        
        layout.addLayout(form)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("✅ Ajouter au panier")
        add_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; font-weight: bold;")
        add_btn.setMinimumHeight(50)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.setMinimumHeight(50)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)
        
        dialog.setLayout(layout)
        
        def add_to_cart():
            name = name_input.text().strip()
            price = price_input.value()
            qty = qty_input.value()
            
            if not name:
                QMessageBox.warning(dialog, "Erreur", "Veuillez entrer un nom de produit")
                return
            if price <= 0:
                QMessageBox.warning(dialog, "Erreur", "Veuillez entrer un prix valide")
                return
            
            # Créer un produit temporaire (non sauvegardé en base)
            custom_product = {
                'id': -1,  # ID négatif pour indiquer produit personnalisé
                'barcode': f"CUSTOM-{datetime.now().strftime('%H%M%S')}",
                'name': name,
                'selling_price': price,
                'purchase_price': 0,
                'stock_quantity': 999  # Stock illimité pour produit personnalisé
            }
            
            success, msg = self.cart.add_item(custom_product, qty)
            if success:
                self.update_cart_display()
                dialog.accept()
                QMessageBox.information(self, "✅ Ajouté", f"{name} x{qty} ajouté au panier")
            else:
                QMessageBox.warning(dialog, "Erreur", msg)
        
        add_btn.clicked.connect(add_to_cart)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
    
    def process_payment(self):
        """Traiter le paiement"""
        # Check explicitement si items est vide
        if not self.cart.items:
            QMessageBox.warning(self, "Panier vide", "Ajoutez des produits avant de payer")
            return
        
        try:
            customer_id = self.customer_combo.currentData()
            payment_method = self.payment_method.currentData()
            
            # Vérifier si crédit est sélectionné mais pas de client
            if payment_method == 'credit' and not customer_id:
                QMessageBox.warning(self, "Client requis", 
                    "Vous devez sélectionner un client pour un paiement à crédit")
                return
            
            # Obtenir l'utilisateur actuel (caissier)
            current_user = auth_manager.get_current_user()
            cashier_id = current_user['id'] if current_user else 1
            
            success, message, sale_id = pos_manager.complete_sale(
                cashier_id,
                payment_method,
                self.cart.get_total(), 
                customer_id
            )
            
            if success:
                # Rafraîchir la référence du panier (car recréé dans POSManager)
                self.cart = pos_manager.get_cart()
                self.update_cart_display()
                
                # Réinitialiser champs
                self.customer_combo.setCurrentIndex(-1)  # Vider le champ client
                self.payment_method.setCurrentIndex(0)
                
                # Afficher l'aperçu du ticket SEULEMENT si checkbox cochée
                if self.print_receipt_cb.isChecked():
                    sale_data = pos_manager.get_sale(sale_id)
                    if sale_data:
                        preview = ReceiptPreviewDialog(sale_data, self)
                        preview.exec_()
                else:
                    # Juste un message de succès sans impression
                    QMessageBox.information(self, "✅ Vente enregistrée", 
                        f"Vente #{message.split(':')[-1].strip()} enregistrée avec succès!")
                
            else:
                QMessageBox.warning(self, "Erreur", message)
                
        except Exception as e:
            logger.error(f"Erreur paiement: {e}")
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def refresh(self):
        """Rafraîchir les données de la page"""
        self.customer_combo.clear()
        self.load_customers()
        self.customer_combo.setCurrentIndex(-1)  # Toujours vide par défaut
        self.barcode_input.setFocus()

    def calc_add_digit(self, digit):
        """Ajouter un chiffre à la calculatrice"""
        current = self.calc_display.text()
        if current == "0":
            self.calc_display.setText(digit)
        else:
            self.calc_display.setText(current + digit)
    
    def calc_clear(self):
        """Effacer la calculatrice"""
        self.calc_display.setText("0")
    
    def add_from_calculator(self):
        """Ajouter le montant de la calculatrice au panier"""
        try:
            price = int(self.calc_display.text())
        except:
            price = 0
            
        if price <= 0:
            QMessageBox.warning(self, "Attention", "Le montant doit être supérieur à 0")
            return
            
        success, msg = pos_manager.add_to_cart(
            product_id=0,
            quantity=1,
            custom_price=price,
            product_name="Produit Divers"
        )
        
        if success:
            self.calc_display.setText("0")
            self.update_cart_display()
        else:
            QMessageBox.warning(self, "Erreur", msg)
            

class CalculatorDialog(QDialog):
    """Dialogue Calculatrice Simple"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculatrice")
        self.setFixedSize(300, 400)
        self.layout = QVBoxLayout()
        
        # Écran
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMinimumHeight(50)
        self.display.setStyleSheet("font-size: 24px; padding: 5px; border: 2px solid #ccc; border-radius: 5px;")
        self.layout.addWidget(self.display)
        
        # Grille boutons
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('/', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('*', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('-', 2, 3),
            ('0', 3, 0), ('.', 3, 1), ('C', 3, 2), ('+', 3, 3),
            ('=', 4, 0, 1, 4)
        ]
        
        for btn_text, *pos in buttons:
            btn = QPushButton(btn_text)
            btn.setMinimumHeight(50)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    font-weight: bold;
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)
            
            if btn_text == 'C':
                btn.setStyleSheet(btn.styleSheet() + "background-color: #ffcccc; color: #c0392b;")
                btn.clicked.connect(self.clear)
            elif btn_text == '=':
                btn.setStyleSheet(btn.styleSheet() + "background-color: #2ecc71; color: white;")
                btn.clicked.connect(self.calculate)
            else:
                btn.clicked.connect(lambda checked, x=btn_text: self.append(x))
            
            if len(pos) == 4:
                grid_layout.addWidget(btn, *pos)
            else:
                grid_layout.addWidget(btn, *pos)
                
        self.layout.addLayout(grid_layout)
        self.setLayout(self.layout)
        
    def append(self, text):
        self.display.setText(self.display.text() + text)
        
    def clear(self):
        self.display.clear()
        
    def calculate(self):
        try:
            expression = self.display.text().replace('x', '*')
            result = eval(expression)
            self.display.setText(str(result))
        except Exception:
            self.display.setText("Erreur")


class MiniCalculatorDialog(QDialog):
    """Mini Calculatrice avec ajout direct au panier"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("💰 Montant Libre")
        self.setFixedSize(280, 380)
        self.value = 0
        layout = QVBoxLayout()
        
        # Écran d'affichage
        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMinimumHeight(60)
        self.display.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold;
            padding: 10px; 
            border: 2px solid #27ae60; 
            border-radius: 8px;
            background-color: #e8f5e9;
        """)
        layout.addWidget(self.display)
        
        # Grille de boutons numériques
        grid = QGridLayout()
        grid.setSpacing(5)
        
        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2),
            ('0', 3, 0), ('00', 3, 1), ('C', 3, 2),
        ]
        
        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(55)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    font-weight: bold;
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #e8e8e8;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)
            if text == 'C':
                btn.setStyleSheet(btn.styleSheet() + "background-color: #ffcccc; color: #c0392b;")
                btn.clicked.connect(self.clear_display)
            else:
                btn.clicked.connect(lambda checked, t=text: self.add_digit(t))
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        
        # Bouton Ajouter
        add_btn = QPushButton("✅ AJOUTER AU PANIER")
        add_btn.setMinimumHeight(60)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #219150;
            }
        """)
        add_btn.clicked.connect(self.accept)
        layout.addWidget(add_btn)
        
        self.setLayout(layout)
    
    def add_digit(self, digit):
        current = self.display.text()
        if current == "0":
            self.display.setText(digit)
        else:
            self.display.setText(current + digit)
    
    def clear_display(self):
        self.display.setText("0")
    
    def get_value(self):
        try:
            return int(self.display.text())
        except:
            return 0
