# -*- coding: utf-8 -*-
"""
Interface de gestion des clients
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QMessageBox, QHeaderView, QDialog,
                             QFormLayout, QSpinBox, QDoubleSpinBox, QDateEdit,
                             QCheckBox, QTabWidget, QGroupBox, QTextEdit, QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from modules.customers.customer_manager import customer_manager
from core.auth import auth_manager
from core.logger import logger

class CustomerFormDialog(QDialog):
    """Dialogue d'ajout/modification de client"""
    
    def __init__(self, customer=None, parent=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Nouveau Client" if not customer else "Modifier Client")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.credit_limit_spin = QDoubleSpinBox()
        self.credit_limit_spin.setRange(0, 1000000)
        self.credit_limit_spin.setValue(0)
        self.credit_limit_spin.setSuffix(" DA")
        
        layout.addRow("Nom Complet *:", self.name_edit)
        layout.addRow("Téléphone:", self.phone_edit)
        layout.addRow("Email:", self.email_edit)
        layout.addRow("Adresse:", self.address_edit)
        layout.addRow("Limite de Crédit:", self.credit_limit_spin)
        
        # Boutons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Enregistrer")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addRow(btn_layout)
        
        self.setLayout(layout)
        
        if self.customer:
            self.name_edit.setText(self.customer.get('full_name', ''))
            self.phone_edit.setText(self.customer.get('phone', ''))
            self.email_edit.setText(self.customer.get('email', ''))
            self.address_edit.setText(self.customer.get('address', ''))
            self.credit_limit_spin.setValue(self.customer.get('credit_limit', 0))
            
    def save(self):
        if not self.name_edit.text():
            QMessageBox.warning(self, "Erreur", "Le nom est obligatoire.")
            return
            
        data = {
            'full_name': self.name_edit.text(),
            'phone': self.phone_edit.text(),
            'email': self.email_edit.text(),
            'address': self.address_edit.text(),
            'credit_limit': self.credit_limit_spin.value()
        }
        
        if self.customer:
            success, msg = customer_manager.update_customer(self.customer['id'], **data)
        else:
            success, msg, _ = customer_manager.create_customer(**data)
            
        if success:
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)

class PaymentDialog(QDialog):
    """Dialogue de paiement de crédit"""
    def __init__(self, customer, parent=None):
        super().__init__(parent)
        self.customer = customer
        # Conversion sûre en float
        try:
            self.customer['current_credit'] = float(self.customer.get('current_credit', 0))
        except (ValueError, TypeError):
             self.customer['current_credit'] = 0.0
             
        self.setWindowTitle(f"Règlement Crédit: {self.customer['full_name']}")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        info = QLabel(f"Crédit actuel: {self.customer['current_credit']:.2f} DA")
        info.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        layout.addWidget(info)
        
        form = QFormLayout()
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, self.customer['current_credit'])
        self.amount_spin.setSuffix(" DA")
        self.amount_spin.setValue(min(1000, self.customer['current_credit']))
        self.amount_spin.valueChanged.connect(self.update_remaining)
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Note optionnelle...")
        
        form.addRow("Montant à régler:", self.amount_spin)
        form.addRow("Note:", self.notes_edit)
        layout.addLayout(form)
        
        # Nouveau solde
        self.remaining_label = QLabel(f"Nouveau solde: {(self.customer['current_credit'] - self.amount_spin.value()):.2f} DA")
        self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.remaining_label)
        
        btn = QPushButton("Valider Paiement")
        btn.clicked.connect(self.save)
        btn.setStyleSheet("background-color: #2ecc71; color: white; padding: 10px;")
        layout.addWidget(btn)
        
        self.setLayout(layout)
        
    def update_remaining(self):
        """Mettre à jour le solde restant"""
        remaining = self.customer['current_credit'] - self.amount_spin.value()
        self.remaining_label.setText(f"Nouveau solde: {remaining:.2f} DA")
        if remaining < 0:
             self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")
        else:
             self.remaining_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        
    def save(self):
        amount = self.amount_spin.value()
        if amount <= 0:
            return
            
        user = auth_manager.get_current_user()
        user_id = user['id'] if user else 1
        
        success, msg = customer_manager.pay_credit(
            self.customer['id'], amount, user_id, self.notes_edit.text()
        )
        
        if success:
            QMessageBox.information(self, "Succès", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)

class CustomersPage(QWidget):
    """Page de gestion des clients"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_customers()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel("👥 Gestion des Clients")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Toolbar - Améliorée
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Rechercher client...")
        self.search_input.setMinimumHeight(50)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 15px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2ecc71;
            }
        """)
        self.search_input.textChanged.connect(self.load_customers)
        toolbar.addWidget(self.search_input)
        
        self.filter_combo = QComboBox()
        self.filter_combo.setMinimumHeight(50)
        self.filter_combo.setMinimumWidth(200)
        self.filter_combo.addItems(["Tous les clients", "Avec dettes (Crédit > 0)", "Meilleurs clients"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 10px 15px;
                font-size: 14px;
                background-color: white;
            }
        """)
        self.filter_combo.currentIndexChanged.connect(self.load_customers)
        toolbar.addWidget(self.filter_combo)
        
        new_btn = QPushButton("➕ Nouveau Client")
        new_btn.setMinimumHeight(50)
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        new_btn.clicked.connect(self.open_new_dialog)
        toolbar.addWidget(new_btn)
        
        layout.addLayout(toolbar)
        
        # Table - Style amélioré
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Code", "Nom", "Téléphone", "Dette (Crédit)", "Total Achats", "Actions"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(45)
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
                background-color: #2ecc71;
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
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        
    def load_customers(self):
        search = self.search_input.text()
        filter_mode = self.filter_combo.currentText()
        
        if filter_mode == "Avec dettes (Crédit > 0)":
            customers = customer_manager.get_customers_with_credit()
        else:
            customers = customer_manager.search_customers(search) if search else customer_manager.get_all_customers()
            
        # Tri pour "Meilleurs clients"
        if filter_mode == "Meilleurs clients":
            customers.sort(key=lambda x: x['total_purchases'], reverse=True)
            
        self.table.setRowCount(0)
        for c in customers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(c['code']))
            self.table.setItem(row, 1, QTableWidgetItem(c['full_name']))
            self.table.setItem(row, 2, QTableWidgetItem(c.get('phone', '')))
            
            try:
                current_credit = float(c.get('current_credit', 0))
            except (ValueError, TypeError):
                current_credit = 0.0
                
            try:
                total_purchases = float(c.get('total_purchases', 0))
            except (ValueError, TypeError):
                total_purchases = 0.0

            credit_item = QTableWidgetItem(f"{current_credit:.2f} DA")
            if current_credit > 0:
                credit_item.setForeground(QColor("red"))
            self.table.setItem(row, 3, credit_item)
            
            self.table.setItem(row, 4, QTableWidgetItem(f"{total_purchases:.2f} DA"))
            
            # Actions
            widget = QWidget()
            hbox = QHBoxLayout(widget)
            hbox.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Modifier")
            edit_btn.clicked.connect(lambda checked, x=c: self.open_edit_dialog(x))
            hbox.addWidget(edit_btn)
            
            if current_credit > 0:
                pay_btn = QPushButton("💰")
                pay_btn.setToolTip("Régler Dette")
                pay_btn.setStyleSheet("color: green;")
                pay_btn.clicked.connect(lambda checked, x=c: self.open_payment_dialog(x))
                hbox.addWidget(pay_btn)
            
            # Delete button
            del_btn = QPushButton("🗑️")
            del_btn.setToolTip("Supprimer")
            del_btn.setStyleSheet("color: red;")
            del_btn.clicked.connect(lambda checked, x=c['id']: self.delete_customer(x))
            hbox.addWidget(del_btn)
                
            self.table.setCellWidget(row, 5, widget)
            
    def open_new_dialog(self):
        if CustomerFormDialog(parent=self).exec_():
            self.load_customers()
            
    def open_edit_dialog(self, customer):
        if CustomerFormDialog(customer, parent=self).exec_():
            self.load_customers()
            
    def open_payment_dialog(self, customer):
        if PaymentDialog(customer, parent=self).exec_():
            self.load_customers()

    def delete_customer(self, customer_id):
        """Supprimer un client"""
        confirm = QMessageBox.question(self, "Confirmer", 
                                     "Voulez-vous vraiment supprimer ce client ?", 
                                     QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = customer_manager.delete_customer(customer_id)
            if success:
                self.load_customers()
            else:
                QMessageBox.warning(self, "Impossible de supprimer", msg)

    def refresh(self):
        """Rafraîchir les données"""
        self.load_customers()
    
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
                    background-color: #27ae60;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #2c3e50;
                }
                QHeaderView::section {
                    background-color: #27ae60;
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
                    border-color: #27ae60;
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
                    background-color: #27ae60;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #27ae60;
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
                    border-color: #27ae60;
                }
            """
        
        self.table.setStyleSheet(table_style)
        if hasattr(self, 'search_input'):
            self.search_input.setStyleSheet(input_style)

