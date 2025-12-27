# -*- coding: utf-8 -*-
"""
Interface de gestion des produits
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QTabWidget, QGroupBox, QMenu, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QBrush
from modules.products.product_manager import product_manager
from modules.suppliers.supplier_manager import supplier_manager
from modules.reports.reorder_report import generate_reorder_report
from core.logger import logger

class ProductFormDialog(QDialog):
    """Dialogue d'ajout/modification de produit"""
    
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Nouveau Produit" if not product else "Modifier Produit")
        self.setMinimumWidth(500)
        self.suppliers = supplier_manager.get_all_suppliers()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Onglets pour organiser les informations
        tabs = QTabWidget()
        
        # Onglet Général
        general_tab = QWidget()
        form_layout = QFormLayout()
        
        self.barcode_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.name_ar_edit = QLineEdit()
        self.category_combo = QComboBox() # TODO: Charger les catégories
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("--- Aucun ---", None)
        for s in self.suppliers:
            self.supplier_combo.addItem(s['company_name'], s['id'])
            
        self.description_edit = QLineEdit()
        
        form_layout.addRow("Code-barres:", self.barcode_edit)
        form_layout.addRow("Nom *:", self.name_edit)
        form_layout.addRow("Nom (Arabe):", self.name_ar_edit)
        form_layout.addRow("Fournisseur:", self.supplier_combo)
        form_layout.addRow("Description:", self.description_edit)
        # form_layout.addRow("Catégorie:", self.category_combo)
        
        general_tab.setLayout(form_layout)
        tabs.addTab(general_tab, "Général")
        
        # Onglet Prix & Stock
        price_tab = QWidget()
        price_layout = QFormLayout()
        
        self.purchase_price_spin = QDoubleSpinBox()
        self.purchase_price_spin.setRange(0, 1000000)
        self.purchase_price_spin.setSuffix(" DA")
        self.purchase_price_spin.setDecimals(2)
        
        self.selling_price_spin = QDoubleSpinBox()
        self.selling_price_spin.setRange(0, 1000000)
        self.selling_price_spin.setSuffix(" DA")
        self.selling_price_spin.setDecimals(2)
        
        self.stock_spin = QSpinBox()
        self.stock_spin.setRange(0, 100000)
        
        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setRange(0, 1000)
        self.min_stock_spin.setValue(10)
        
        self.expiry_date_edit = QDateEdit()
        self.expiry_date_edit.setCalendarPopup(True)
        self.expiry_date_edit.setDate(QDate.currentDate().addYears(1))
        self.enable_expiry = QCheckBox("Date d'expiration ?")
        self.enable_expiry.toggled.connect(self.expiry_date_edit.setEnabled)
        self.expiry_date_edit.setEnabled(False)
        
        price_layout.addRow("Prix d'achat:", self.purchase_price_spin)
        price_layout.addRow("Prix de vente *:", self.selling_price_spin)
        price_layout.addRow("Stock initial:", self.stock_spin)
        price_layout.addRow("Alert Stock Min:", self.min_stock_spin)
        price_layout.addRow(self.enable_expiry, self.expiry_date_edit)
        
        price_tab.setLayout(price_layout)
        tabs.addTab(price_tab, "Prix & Stock")
        
        layout.addWidget(tabs)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Enregistrer")
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("background-color: #2ecc71; color: white;")
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Remplir si modification
        if self.product:
            self.barcode_edit.setText(self.product.get('barcode', ''))
            self.name_edit.setText(self.product.get('name', ''))
            self.name_ar_edit.setText(self.product.get('name_ar', ''))
            self.description_edit.setText(self.product.get('description', ''))
            self.purchase_price_spin.setValue(self.product.get('purchase_price', 0))
            self.selling_price_spin.setValue(self.product.get('selling_price', 0))
            self.stock_spin.setValue(self.product.get('stock_quantity', 0))
            self.min_stock_spin.setValue(self.product.get('min_stock_level', 10))
            
            # Select Supplier
            supplier_id = self.product.get('supplier_id')
            if supplier_id:
                index = self.supplier_combo.findData(supplier_id)
                if index >= 0:
                    self.supplier_combo.setCurrentIndex(index)
            
            if self.product.get('expiry_date'):
                self.enable_expiry.setChecked(True)
                self.expiry_date_edit.setDate(QDate.fromString(self.product['expiry_date'], "yyyy-MM-dd"))
                
    def save(self):
        if not self.name_edit.text() or self.selling_price_spin.value() <= 0:
            QMessageBox.warning(self, "Erreur", "Le nom et le prix de vente sont obligatoires.")
            return

        data = {
            'barcode': self.barcode_edit.text(),
            'name': self.name_edit.text(),
            'name_ar': self.name_ar_edit.text(),
            'description': self.description_edit.text(),
            'purchase_price': self.purchase_price_spin.value(),
            'selling_price': self.selling_price_spin.value(),
            'stock_quantity': self.stock_spin.value(),
            'min_stock_level': self.min_stock_spin.value(),
            'expiry_date': self.expiry_date_edit.date().toString("yyyy-MM-dd") if self.enable_expiry.isChecked() else None,
            'supplier_id': self.supplier_combo.currentData()
        }
        
        if self.product:
            success, msg = product_manager.update_product(self.product['id'], **data)
        else:
            success, msg, pid = product_manager.create_product(**data)
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)

class ProductsPage(QWidget):
    """Page de gestion des produits"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_products()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # En-tête avec gradient
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3b82f6, stop:1 #2563eb);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_layout = QVBoxLayout()
        header = QLabel("📦 Gestion des Produits")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent;")
        title_layout.addWidget(header)
        
        subtitle = QLabel("Gérez votre stock, prix et promotions")
        subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9); background: transparent;")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Stat rapide dans le header
        self.count_label = QLabel("0 Produits")
        self.count_label.setStyleSheet("""
            background-color: rgba(255,255,255,0.2);
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-weight: bold;
        """)
        header_layout.addWidget(self.count_label)
        
        layout.addWidget(header_frame)
        
        # Barre d'outils - Améliorée
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        # Recherche - Plus grande
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher (Nom, Code-barres)...")
        self.search_input.setMinimumHeight(50)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 15px;
                background-color: white;
                color: #1f2937;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: #eff6ff;
            }
        """)
        self.search_input.textChanged.connect(self.load_products)
        toolbar.addWidget(self.search_input)
        
        # Filtres - Plus grand
        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumHeight(50)
        self.filter_combo.setMinimumWidth(180)
        self.filter_combo.addItems(["Tous les produits", "Stock faible", "En promotion", "Expire bientôt"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 14px;
                background-color: white;
                color: #374151;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        toolbar.addWidget(self.filter_combo)
        
        # Bouton Nouveau - Plus grand
        new_btn = QPushButton("➕ Nouveau Produit")
        new_btn.setMinimumHeight(50)
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #3b82f6, stop:1 #2563eb);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #2563eb, stop:1 #1d4ed8);
            }
        """)
        new_btn.clicked.connect(self.open_new_product_dialog)
        toolbar.addWidget(new_btn)
        
        # Bouton Importer - Plus grand
        import_btn = QPushButton("📥 Importer")
        import_btn.setMinimumHeight(50)
        import_btn.setCursor(Qt.PointingHandCursor)
        import_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #7c3aed, stop:1 #6d28d9);
            }
        """)
        import_btn.clicked.connect(self.open_import_dialog)
        toolbar.addWidget(import_btn)

        # Bouton Commande Fournisseur - Nouveau
        order_btn = QPushButton("📑 Commande")
        order_btn.setMinimumHeight(50)
        order_btn.setCursor(Qt.PointingHandCursor)
        order_btn.setToolTip("Générer une liste de commande pour le stock faible")
        order_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #d97706, stop:1 #b45309);
            }
        """)
        order_btn.clicked.connect(self.generate_order_report)
        toolbar.addWidget(order_btn)
        
        layout.addLayout(toolbar)
        
        # Tableau - Style amélioré
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Code", "Nom", "Prix Vente", "Stock", "Expiration", "Promotion", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                gridline-color: transparent;
                background-color: white;
                selection-background-color: #eff6ff;
                selection-color: #1e3a8a;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px 15px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: bold;
                color: #475569;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px 10px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #f8fafc;
            }
        """)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def load_products(self):
        search = self.search_input.text()
        filter_mode = self.filter_combo.currentText()
        
        products = []
        if filter_mode == "Stock faible":
            products = product_manager.get_low_stock_products()
        elif filter_mode == "En promotion":
            products = product_manager.get_promoted_products()
        elif filter_mode == "Expire bientôt":
            products = product_manager.get_expiring_products()
        else:
            products = product_manager.search_products(search) if search else product_manager.get_all_products(limit=100)
            
        self.table.setRowCount(0)
        for p in products:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Stock alert color
            bg_color = None
            if p['stock_quantity'] <= p['min_stock_level']:
                bg_color = QColor("#ffebee") # Rouge clair
            
            # Items
            items = [
                p.get('barcode', ''),
                p['name'],
                f"{float(p['selling_price']):g} DA",
                str(p['stock_quantity']),
                p.get('expiry_date', '-'),
                f"{p.get('discount_percentage', 0):g}%" if p.get('is_on_promotion') else "-"
            ]
            
            for i, text in enumerate(items):
                item = QTableWidgetItem(str(text))
                if bg_color:
                    item.setBackground(bg_color)
                self.table.setItem(row, i, item)
                
            # Boutons Actions
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, x=p: self.open_edit_dialog(x))
            
            del_btn = QPushButton("🗑️")
            del_btn.setFixedSize(30, 30)
            del_btn.setStyleSheet("color: red;")
            del_btn.clicked.connect(lambda checked, x=p['id']: self.delete_product(x))
            
            # Bouton imprimer code-barres
            print_btn = QPushButton("🏷️")
            print_btn.setFixedSize(30, 30)
            print_btn.setToolTip("Imprimer le code-barres")
            print_btn.clicked.connect(lambda checked, x=p: self.print_barcode(x))
            
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(del_btn)
            action_layout.addWidget(print_btn)
            self.table.setCellWidget(row, 6, action_widget)
            
    def open_new_product_dialog(self):
        dialog = ProductFormDialog(parent=self)
        if dialog.exec_():
            self.load_products()
            
    def open_import_dialog(self):
        """Ouvrir le dialogue d'importation"""
        from ui.import_dialog import ImportDialog
        if ImportDialog(parent=self).exec_():
            self.load_products()
            
    def open_edit_dialog(self, product):
        dialog = ProductFormDialog(product, parent=self)
        if dialog.exec_():
            self.load_products()
            
    def delete_product(self, product_id):
        confirm = QMessageBox.question(self, "Confirmer", "Supprimer ce produit ?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            product_manager.delete_product(product_id)
            self.load_products()

    def print_barcode(self, product):
        """Imprimer le code-barres d'un produit"""
        try:
            from reportlab.lib.pagesizes import mm
            from reportlab.pdfgen import canvas
            from reportlab.graphics.barcode import code128
            from reportlab.lib.units import mm
            import os
            import subprocess
            
            barcode_value = product.get('barcode', '')
            product_name = product.get('name', 'Produit')
            price = product.get('selling_price', 0)
            
            if not barcode_value:
                QMessageBox.warning(self, "Erreur", "Ce produit n'a pas de code-barres")
                return
            
            # Créer le dossier si nécessaire
            import config
            barcode_dir = config.DATA_DIR / "barcodes"
            barcode_dir.mkdir(exist_ok=True)
            
            # Générer le PDF
            filename = barcode_dir / f"barcode_{barcode_value}.pdf"
            
            # Taille étiquette: 50mm x 30mm
            width = 60 * mm
            height = 35 * mm
            
            c = canvas.Canvas(str(filename), pagesize=(width, height))
            
            # Nom du produit (tronqué si trop long)
            c.setFont("Helvetica-Bold", 8)
            name_display = product_name[:25] + "..." if len(product_name) > 25 else product_name
            c.drawCentredString(width/2, height - 8*mm, name_display)
            
            # Code-barres
            barcode = code128.Code128(barcode_value, barWidth=0.4*mm, barHeight=12*mm)
            barcode.drawOn(c, 5*mm, 10*mm)
            
            # Texte code-barres
            c.setFont("Helvetica", 6)
            c.drawCentredString(width/2, 6*mm, barcode_value)
            
            # Prix
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(width/2, 2*mm, f"{price} DA")
            
            c.save()
            
            # Ouvrir le PDF
            if os.name == 'nt':
                os.startfile(str(filename))
            else:
                subprocess.run(['xdg-open', str(filename)])
                
            logger.info(f"Code-barres généré: {filename}")
            
        except ImportError:
            QMessageBox.warning(self, "Module manquant", 
                "Le module 'reportlab' est requis pour l'impression des codes-barres.\n\nInstallez-le avec: pip install reportlab")
        except Exception as e:
            logger.error(f"Erreur génération code-barres: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de générer le code-barres: {e}")

    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        # Obtenir le produit sélectionné
        row = self.table.currentRow()
        if row < 0:
            return
            
        # TODO: ID is tricky to get from row if not stored. 
        # Better storing objects or ID in hidden column. 
        # For now, I rely on the search providing the same order but that's risky.
        # Let's fix this in load_products by storing ID in UserRole.
        pass # To be implemented if requested, simpler actions button covers it.

    def set_dark_mode(self, is_dark):
        """Appliquer le mode sombre à la page Produits"""
        if is_dark:
            # Mode sombre
            self.table.setStyleSheet("""
                QTableWidget {
                    border: 2px solid #555;
                    border-radius: 10px;
                    background-color: #34495e;
                    gridline-color: #555;
                    font-size: 14px;
                    color: white;
                }
                QTableWidget::item {
                    padding: 10px;
                    color: white;
                }
                QTableWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #2c3e50;
                    padding: 12px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #3d566e;
                }
            """)
            
            self.search_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #555;
                    border-radius: 10px;
                    padding: 10px 15px;
                    font-size: 15px;
                    background-color: #34495e;
                    color: white;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """)
            
            self.filter_combo.setStyleSheet("""
                QComboBox {
                    border: 2px solid #555;
                    border-radius: 10px;
                    padding: 10px 15px;
                    font-size: 14px;
                    background-color: #34495e;
                    color: white;
                }
            """)
        else:
            # Mode clair
            self.table.setStyleSheet("""
                QTableWidget {
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    background-color: white;
                    gridline-color: #f0f0f0;
                    font-size: 14px;
                }
                QTableWidget::item {
                    padding: 10px;
                }
                QTableWidget::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    padding: 12px;
                    border: none;
                    font-weight: bold;
                    font-size: 14px;
                    color: #2c3e50;
                }
                QTableWidget::item:alternate {
                    background-color: #f8f9fa;
                }
            """)
            
            self.search_input.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 10px 15px;
                    font-size: 15px;
                    background-color: white;
                    color: #333;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """)
            
            self.filter_combo.setStyleSheet("""
                QComboBox {
                    border: 2px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 10px 15px;
                    font-size: 14px;
                    background-color: white;
                }
            """)

    def refresh(self):
        """Rafraîchir les données"""
        self.load_products()

    def generate_order_report(self):
        """Générer le rapport de commande"""
        success, msg = generate_reorder_report()
        if not success:
            QMessageBox.warning(self, "Attention", msg)

