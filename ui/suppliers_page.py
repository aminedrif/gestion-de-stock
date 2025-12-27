# -*- coding: utf-8 -*-
"""
Interface de gestion des fournisseurs
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QTabWidget, QGroupBox, QTextEdit, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from modules.suppliers.supplier_manager import supplier_manager
from core.auth import auth_manager
from core.logger import logger
from ui.purchase_dialog import PurchaseDialog

class SupplierFormDialog(QDialog):
    """Dialogue d'ajout/modification de fournisseur"""
    
    def __init__(self, supplier=None, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        self.setWindowTitle("Nouveau Fournisseur" if not supplier else "Modifier Fournisseur")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout()
        
        self.company_name_edit = QLineEdit()
        self.contact_person_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.address_edit = QLineEdit()
        
        layout.addRow("Entreprise *:", self.company_name_edit)
        layout.addRow("Contact:", self.contact_person_edit)
        layout.addRow("Téléphone:", self.phone_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Adresse:", self.address_edit)
        
        # Boutons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Enregistrer")
        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)
        
        self.setLayout(layout)
        
        if self.supplier:
            self.company_name_edit.setText(self.supplier.get('company_name', ''))
            self.contact_person_edit.setText(self.supplier.get('contact_person', ''))
            self.phone_edit.setText(self.supplier.get('phone', ''))
            self.email_edit.setText(self.supplier.get('email', ''))
            self.address_edit.setText(self.supplier.get('address', ''))
            
    def save(self):
        if not self.company_name_edit.text():
            QMessageBox.warning(self, "Erreur", "Le nom de l'entreprise est obligatoire.")
            return
            
        data = {
            'company_name': self.company_name_edit.text(),
            'contact_person': self.contact_person_edit.text(),
            'phone': self.phone_edit.text(),
            'email': self.email_edit.text(),
            'address': self.address_edit.text()
        }
        
        if self.supplier:
            success, msg = supplier_manager.update_supplier(self.supplier['id'], **data)
        else:
            success, msg, _ = supplier_manager.create_supplier(**data)
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)

class DebtPaymentDialog(QDialog):
    """Dialogue de paiement de dette fournisseur"""
    def __init__(self, supplier, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        # Conversion sûre en float
        try:
            self.supplier['total_debt'] = float(self.supplier.get('total_debt', 0))
        except (ValueError, TypeError):
             self.supplier['total_debt'] = 0.0

        self.setWindowTitle(f"Règlement Dette: {supplier['company_name']}")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        info = QLabel(f"Dette actuelle: {self.supplier['total_debt']:g} DA")
        info.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(info)
        
        form = QFormLayout()
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, self.supplier['total_debt'])
        self.amount_spin.setSuffix(" DA")
        self.amount_spin.setValue(min(1000, self.supplier['total_debt']))
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Description du paiement...")
        
        form.addRow("Montant à régler:", self.amount_spin)
        form.addRow("Description:", self.notes_edit)
        layout.addLayout(form)
        
        btn = QPushButton("Valider Paiement")
        btn.clicked.connect(self.save)
        btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px;")
        layout.addWidget(btn)
        
        self.setLayout(layout)
        
    def save(self):
        amount = self.amount_spin.value()
        if amount <= 0:
            return
            
        user = auth_manager.get_current_user()
        user_id = user['id'] if user else 1
        
        success, msg = supplier_manager.pay_debt(
            self.supplier['id'], amount, user_id, self.notes_edit.text()
        )
        
        if success:
            QMessageBox.information(self, "Succès", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)

class SuppliersPage(QWidget):
    """Page de gestion des fournisseurs"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_suppliers()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # En-tête avec gradient
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #f59e0b, stop:1 #d97706);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        title_layout = QVBoxLayout()
        header = QLabel("🏭 Gestion des Fournisseurs")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent;")
        title_layout.addWidget(header)
        
        subtitle = QLabel("Gérez vos fournisseurs et vos dettes")
        subtitle.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9); background: transparent;")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addWidget(header_frame)
        
        # Toolbar - Améliorée
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher fournisseur...")
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
                border-color: #f59e0b;
                background-color: #fffbeb;
            }
        """)
        self.search_input.textChanged.connect(self.load_suppliers)
        toolbar.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumHeight(50)
        self.filter_combo.setMinimumWidth(180)
        self.filter_combo.addItems(["Tous les fournisseurs", "Avec dettes"])
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
        self.filter_combo.currentIndexChanged.connect(self.load_suppliers)
        toolbar.addWidget(self.filter_combo)
        
        new_btn = QPushButton("➕ Nouveau Fournisseur")
        new_btn.setMinimumHeight(50)
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet("""
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
        new_btn.clicked.connect(self.open_new_dialog)
        toolbar.addWidget(new_btn)
        
        layout.addLayout(toolbar)
        
        # Table - Style amélioré
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Code", "Entreprise", "Contact", "Téléphone", 
            "Total Achats", "Dettes à payer", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                gridline-color: transparent;
                background-color: white;
                selection-background-color: #fffbeb;
                selection-color: #92400e;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #fff7ed;
                padding: 10px 15px;
                border: none;
                border-bottom: 2px solid #fed7aa;
                font-weight: bold;
                color: #9a3412;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px 10px;
                border-bottom: 1px solid #fff7ed;
            }
            QTableWidget::item:selected {
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #fff7ed;
            }

        """)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def load_suppliers(self):
        search = self.search_input.text()
        filter_mode = self.filter_combo.currentText()
        
        if filter_mode == "Avec dettes":
            suppliers = supplier_manager.get_suppliers_with_debt()
        else:
            suppliers = supplier_manager.search_suppliers(search) if search else supplier_manager.get_all_suppliers()
            
        self.table.setRowCount(0)
        for s in suppliers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(s['code']))
            self.table.setItem(row, 1, QTableWidgetItem(s['company_name']))
            self.table.setItem(row, 2, QTableWidgetItem(s.get('contact_person', '')))
            self.table.setItem(row, 3, QTableWidgetItem(s.get('phone', '')))
            
            # Total Achats
            try:
                total_purchases = float(s.get('total_purchases', 0))
            except (ValueError, TypeError):
                total_purchases = 0.0
                
            purchases_item = QTableWidgetItem(f"{total_purchases:g} DA")
            purchases_item.setForeground(QColor("#3498db"))
            self.table.setItem(row, 4, purchases_item)
            
            # Dettes
            try:
                total_debt = float(s.get('total_debt', 0))
            except (ValueError, TypeError):
                total_debt = 0.0
                
            debt_item = QTableWidgetItem(f"{total_debt:g} DA")
            if total_debt > 0:
                debt_item.setForeground(QColor("red"))
            self.table.setItem(row, 5, debt_item)
            
            # Actions
            widget = QWidget()
            hbox = QHBoxLayout(widget)
            hbox.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(lambda checked, x=s: self.open_edit_dialog(x))
            hbox.addWidget(edit_btn)
            
            # Bouton pour ajouter dette/achat
            add_purchase_btn = QPushButton("🛒")
            add_purchase_btn.setToolTip("Ajouter Achat")
            add_purchase_btn.setStyleSheet("color: blue;")
            add_purchase_btn.clicked.connect(lambda checked, x=s: self.open_purchase_dialog(x))
            hbox.addWidget(add_purchase_btn)
            
            if total_debt > 0:
                pay_btn = QPushButton("💸")
                pay_btn.setToolTip("Régler Dette")
                pay_btn.setStyleSheet("color: green;")
                pay_btn.clicked.connect(lambda checked, x=s: self.open_payment_dialog(x))
                hbox.addWidget(pay_btn)

            # Bouton Supprimer
            del_btn = QPushButton("🗑️")
            del_btn.setToolTip("Supprimer")
            del_btn.setStyleSheet("color: red;")
            del_btn.clicked.connect(lambda checked, x=s['id']: self.delete_supplier(x))
            hbox.addWidget(del_btn)
                
            self.table.setCellWidget(row, 6, widget)
            
    def open_new_dialog(self):
        if SupplierFormDialog(parent=self).exec_():
            self.load_suppliers()
            
    def open_edit_dialog(self, supplier):
        if SupplierFormDialog(supplier, parent=self).exec_():
            self.load_suppliers()
            
    def open_payment_dialog(self, supplier):
        if DebtPaymentDialog(supplier, parent=self).exec_():
            self.load_suppliers()

    def delete_supplier(self, supplier_id):
        """Supprimer un fournisseur"""
        confirm = QMessageBox.question(self, "Confirmer", 
                                     "Voulez-vous vraiment supprimer ce fournisseur ?\n(Impossible s'il a des produits ou des dettes)", 
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = supplier_manager.delete_supplier(supplier_id)
            if success:
                # QMessageBox.information(self, "Succès", "Fournisseur supprimé avec succès")
                self.load_suppliers()
            else:
                QMessageBox.warning(self, "Impossible de supprimer", msg)
    
    def open_purchase_dialog(self, supplier):
        """Ouvrir le dialogue d'ajout d'achat"""
        if PurchaseDialog(supplier, supplier_manager, auth_manager, parent=self).exec_():
            self.load_suppliers()

    def refresh(self):
        """Rafraîchir les données"""
        self.load_suppliers()
    
    def set_dark_mode(self, is_dark):
        """Appliquer le mode sombre/clair"""
        if is_dark:
            # Mode sombre
            table_style = """
                QTableWidget {
                    background-color: #34495e;
                    color: #ecf0f1;
                    gridline-color: #4a6785;
                    border: 1px solid #4a6785;
                    border-radius: 8px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #4a6785;
                }
                QTableWidget::item:selected {
                    background-color: #9b59b6;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #2c3e50;
                }
                QHeaderView::section {
                    background-color: #9b59b6;
                    color: white;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                }
            """
            input_style = """
                QLineEdit, QComboBox {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 2px solid #4a6785;
                    border-radius: 8px;
                    padding: 8px;
                }
                QLineEdit:focus, QComboBox:focus {
                    border-color: #9b59b6;
                }
            """
        else:
            # Mode clair
            table_style = """
                QTableWidget {
                    background-color: white;
                    color: #2c3e50;
                    gridline-color: #e0e0e0;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid #e0e0e0;
                }
                QTableWidget::item:selected {
                    background-color: #9b59b6;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #9b59b6;
                    color: white;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                }
            """
            input_style = """
                QLineEdit, QComboBox {
                    background-color: white;
                    color: #2c3e50;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px;
                }
                QLineEdit:focus, QComboBox:focus {
                    border-color: #9b59b6;
                }
            """
        
        self.table.setStyleSheet(table_style)
        if hasattr(self, 'search_input'):
            self.search_input.setStyleSheet(input_style)

