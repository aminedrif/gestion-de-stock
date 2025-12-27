# -*- coding: utf-8 -*-
"""
Dialogue de gestion des permissions
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QCheckBox, QScrollArea, QWidget,
                             QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.auth import auth_manager
import config

class PermissionDialog(QDialog):
    """Dialogue pour configurer les permissions d'un utilisateur"""
    
    def __init__(self, user_id, username, role, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.username = username
        self.role = role
        self.permissions_state = {} # Key: Checkbox
        
        self.setWindowTitle(f"Permissions: {username}")
        self.resize(500, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(f"Configuration des accès pour {self.username}")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header)
        
        info = QLabel("Cochez pour autoriser, décochez pour interdire.\nCes réglages surchargent les permissions par défaut du rôle.")
        info.setStyleSheet("color: #666; margin-bottom: 15px;")
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Scroll Area for permissions
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)
        
        # Get existing specific permissions from DB
        user_perms = auth_manager.get_user_permissions(self.user_id)
        
        # Get default permissions for this role
        default_perms = config.PERMISSIONS.get(self.role, [])
        pass_all_perms = set(config.PERMISSIONS['admin']) # Use admin set as superset of all meaningful perms
        
        # Group by category (simplified mapping)
        categories = {
            "Ventes & Caisse": ["make_sales", "process_returns"],
            "Produits & Stock": ["manage_products", "view_products", "manage_categories"],
            "Partenaires": ["manage_customers", "view_customers", "manage_suppliers", "view_suppliers"],
            "Administration": ["manage_users", "manage_settings", "view_reports", "manage_backups", "view_audit_log"]
        }
        
        for category, perms in categories.items():
            cat_label = QLabel(category)
            cat_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 10px;")
            content_layout.addWidget(cat_label)
            
            for perm in perms:
                if perm not in pass_all_perms and self.role != 'admin':
                    # Skip check if it's strictly an admin perm usually not relevant for cashier override?
                    # actually let's show all, allowing a cashier to do admin stuff might be intended
                    pass

                # Check state determination
                # 1. If in user_perms, use that value
                # 2. Else use role default
                
                is_checked = False
                is_default = True # Visual indicator
                
                if perm in user_perms:
                    is_checked = user_perms[perm]
                    is_default = False
                else:
                    is_checked = (perm in default_perms)
                
                cb = QCheckBox(self.format_perm_name(perm))
                cb.setChecked(is_checked)
                
                # Style modification if overridden
                if not is_default:
                    cb.setStyleSheet("color: #d35400; font-weight: 500;") # Orange for custom
                    cb.setToolTip("Permission personnalisée (diffère ou explicite)")
                
                self.permissions_state[perm] = cb
                content_layout.addWidget(cb)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Réinitialiser au défaut")
        reset_btn.clicked.connect(self.reset_to_default)
        reset_btn.setStyleSheet("color: #c0392b; background: transparent; border: 1px solid #c0392b;")
        
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setDefault(True)
        save_btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 15px;")
        save_btn.clicked.connect(self.save_permissions)
        
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
    def format_perm_name(self, perm):
        """Format technical name to readable"""
        mapping = {
            "make_sales": "Effectuer des ventes",
            "process_returns": "Effectuer des retours",
            "manage_products": "Gérer les produits (Ajout/Modif)",
            "view_products": "Voir les produits",
            "manage_categories": "Gérer les catégories",
            "manage_customers": "Gérer les clients",
            "view_customers": "Voir les clients",
            "manage_suppliers": "Gérer les fournisseurs",
            "view_suppliers": "Voir les fournisseurs",
            "manage_users": "Gérer les utilisateurs",
            "view_reports": "Voir les rapports",
            "manage_settings": "Modifier les paramètres",
            "manage_backups": "Gérer les sauvegardes",
            "view_audit_log": "Voir le journal d'audit"
        }
        return mapping.get(perm, perm)
        
    def reset_to_default(self):
        """Reset checkboxes to role defaults"""
        default_perms = config.PERMISSIONS.get(self.role, [])
        for perm, cb in self.permissions_state.items():
            cb.setChecked(perm in default_perms)
            cb.setStyleSheet("") # Reset style
            
    def save_permissions(self):
        """Save changes to DB"""
        perms_to_save = {}
        default_perms = config.PERMISSIONS.get(self.role, [])
        
        for perm, cb in self.permissions_state.items():
            is_checked = cb.isChecked()
            is_role_default = (perm in default_perms)
            
            # Save ONLY if different from role default OR if it was already overridden to ensure persistence
            # Actually, robust way: always save explicit state if user interacted, 
            # OR just save everything as overrides to be safe.
            # Let's save all displayed permissions as explicit overrides for this user
            perms_to_save[perm] = is_checked
            
        if auth_manager.update_user_permissions(self.user_id, perms_to_save):
            QMessageBox.information(self, "Succès", "Permissions mises à jour avec succès")
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur", "Echec de l'enregistrement")
