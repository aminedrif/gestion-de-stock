# -*- coding: utf-8 -*-
"""
Dialogue pour ajouter un achat chez un fournisseur
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLabel, 
                             QPushButton, QDoubleSpinBox, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt

class PurchaseDialog(QDialog):
    """Dialogue d'ajout d'achat fournisseur"""
    def __init__(self, supplier, supplier_manager, auth_manager, parent=None):
        super().__init__(parent)
        self.supplier = supplier
        self.supplier_manager = supplier_manager
        self.auth_manager = auth_manager
        self.setWindowTitle(f"Ajouter Achat: {supplier['company_name']}")
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        info = QLabel(f"Fournisseur: {self.supplier['company_name']}")
        info.setStyleSheet("font-size: 16px; font-weight: bold; color: #3498db;")
        layout.addWidget(info)
        
        form = QFormLayout()
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999999)
        self.amount_spin.setSuffix(" DA")
        self.amount_spin.setValue(1000)
        self.amount_spin.setDecimals(2)
        
        self.debt_spin = QDoubleSpinBox()
        self.debt_spin.setRange(0, 999999999)
        self.debt_spin.setSuffix(" DA")
        self.debt_spin.setValue(0)
        self.debt_spin.setDecimals(2)
        
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Description de l'achat...")
        
        form.addRow("Montant total de l'achat:", self.amount_spin)
        form.addRow("Dette à ajouter:", self.debt_spin)
        form.addRow("Description:", self.notes_edit)
        
        layout.addLayout(form)
        
        # Info
        info_label = QLabel("💡 Le montant total sera ajouté aux achats totaux.\nLa dette sera ajoutée à la dette actuelle.")
        info_label.setStyleSheet("color: gray; font-size: 12px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Boutons
        btn_layout = QVBoxLayout()
        save_btn = QPushButton("✅ Enregistrer l'Achat")
        save_btn.clicked.connect(self.save)
        save_btn.setStyleSheet("background-color: #3498db; color: white; padding: 10px; font-weight: bold;")
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def save(self):
        amount = self.amount_spin.value()
        debt = self.debt_spin.value()
        
        if amount <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à 0")
            return
            
        user = self.auth_manager.get_current_user()
        user_id = user['id'] if user else 1
        
        # Ajouter l'achat (met à jour total_purchases et total_debt)
        success, msg = self.supplier_manager.add_purchase(
            self.supplier['id'], 
            amount, 
            debt,
            user_id, 
            self.notes_edit.text()
        )
        
        if success:
            QMessageBox.information(self, "Succès", msg)
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", msg)
