# -*- coding: utf-8 -*-
"""
Page d'accueil avec calculatrice et accès rapide
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QLineEdit, QFrame, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime


class HomePage(QWidget):
    """Page d'accueil avec widgets utiles"""
    
    # Signaux pour la navigation et actions
    navigate_to = pyqtSignal(str) # page_name
    quick_scan = pyqtSignal(str) # barcode
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # En-tête de bienvenue
        header_layout = QHBoxLayout()
        
        welcome_label = QLabel("🏪 Tableau de Bord")
        welcome_font = QFont()
        welcome_font.setPointSize(28)
        welcome_font.setBold(True)
        welcome_label.setFont(welcome_font)
        welcome_label.setStyleSheet("color: #667eea;")
        header_layout.addWidget(welcome_label)
        
        header_layout.addStretch()
        
        # Date et heure
        now = datetime.now()
        date_label = QLabel(now.strftime("%A %d %B %Y"))
        date_label.setStyleSheet("color: #666; font-size: 16px;")
        header_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        
        # Mini Caisse (Scan rapide)
        scan_group = QGroupBox("⚡ Scan Rapide & Caisse")
        scan_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding-top: 20px;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: #e74c3c;
            }
        """)
        scan_layout = QHBoxLayout()
        
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Scanner un produit ici pour l'ajouter directement au panier...")
        self.scan_input.setMinimumHeight(50)
        self.scan_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e74c3c;
                border-radius: 8px;
                padding: 10px;
                font-size: 16px;
                background-color: #fff;
            }
        """)
        self.scan_input.returnPressed.connect(self.handle_scan)
        scan_layout.addWidget(self.scan_input)
        
        scan_btn = QPushButton("🛒 Ajouter")
        scan_btn.setMinimumHeight(50)
        scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-weight: bold;
                font-size: 16px;
            }
        """)
        scan_btn.clicked.connect(self.handle_scan)
        scan_layout.addWidget(scan_btn)
        
        scan_group.setLayout(scan_layout)
        layout.addWidget(scan_group)
        
        # Boutons d'accès rapide
        quick_access_label = QLabel("🚀 Accès Rapide")
        quick_access_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-top: 10px;")
        layout.addWidget(quick_access_label)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Bouton Caisse
        btn_pos = self.create_quick_button("🛒", "CAISSE", "Point de vente", "#667eea", "pos")
        buttons_layout.addWidget(btn_pos)
        
        # Bouton Produits
        btn_products = self.create_quick_button("📦", "PRODUITS", "Gestion stock", "#3498db", "products")
        buttons_layout.addWidget(btn_products)
        
        # Bouton Clients
        btn_customers = self.create_quick_button("👥", "CLIENTS", "Fidélité", "#2ecc71", "customers")
        buttons_layout.addWidget(btn_customers)
        
        # Bouton Rapports
        btn_reports = self.create_quick_button("📊", "RAPPORTS", "Statistiques", "#f39c12", "reports")
        buttons_layout.addWidget(btn_reports)
        
        layout.addLayout(buttons_layout)
        
        # Section Achat Rapide (remplace calculatrice + mini-caisse)
        quick_purchase = self.create_quick_purchase()
        layout.addWidget(quick_purchase)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def handle_scan(self):
        """Gérer le scan rapide"""
        code = self.scan_input.text().strip()
        if code:
            self.quick_scan.emit(code)
            self.scan_input.clear()
    
    def create_quick_purchase(self):
        """Créer le widget Achat Rapide"""
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                border: none;
            }
        """)
        container.setMinimumHeight(200)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # En-tête
        header_layout = QHBoxLayout()
        
        title = QLabel("⚡ Achat Rapide")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent; border: none;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Icône
        icon_label = QLabel("🛒")
        icon_label.setStyleSheet("font-size: 36px; background: transparent; border: none;")
        header_layout.addWidget(icon_label)
        
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel("Scannez un produit ou accédez directement à la caisse pour effectuer une vente rapide")
        desc.setStyleSheet("font-size: 14px; color: rgba(255,255,255,0.9); background: transparent; border: none;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Boutons côte à côte
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Bouton Ouvrir Caisse
        open_btn = QPushButton("🛒 Ouvrir la Caisse")
        open_btn.setMinimumHeight(60)
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #667eea;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 25px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        open_btn.clicked.connect(lambda: self.navigate_to.emit("pos"))
        buttons_layout.addWidget(open_btn)
        
        # Bouton Nouvelle Vente
        new_sale_btn = QPushButton("➕ Nouvelle Vente")
        new_sale_btn.setMinimumHeight(60)
        new_sale_btn.setCursor(Qt.PointingHandCursor)
        new_sale_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.2);
                color: white;
                border: 2px solid white;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 25px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.3);
            }
        """)
        new_sale_btn.clicked.connect(lambda: self.navigate_to.emit("pos"))
        buttons_layout.addWidget(new_sale_btn)
        
        layout.addLayout(buttons_layout)
        
        container.setLayout(layout)
        return container
    
    
    def create_quick_button(self, icon, title, subtitle, color, page_target):
        """Créer un bouton d'accès rapide - Design amélioré"""
        button = QPushButton()
        button.setMinimumSize(220, 120)
        button.setCursor(Qt.PointingHandCursor)
        
        # Layout du bouton
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px; background: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; background: transparent; color: white; border: none;")
        title_label.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(title_label)
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 12px; background: transparent; color: rgba(255,255,255,0.9); border: none;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(subtitle_label)
        
        button.setLayout(btn_layout)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 15px;
                padding: 15px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
                transform: scale(1.02);
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """)
        
        button.clicked.connect(lambda: self.navigate_to.emit(page_target))
        return button
    
    def set_dark_mode(self, is_dark):
        """Appliquer le mode sombre/clair"""
        if is_dark:
            # Mode sombre
            group_style = """
                QGroupBox {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 1px solid #4a6785;
                    border-radius: 10px;
                    padding: 15px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QGroupBox::title {
                    color: #ecf0f1;
                }
            """
            input_style = """
                QLineEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 2px solid #4a6785;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """
        else:
            # Mode clair
            group_style = """
                QGroupBox {
                    background-color: white;
                    color: #2c3e50;
                    border: 1px solid #e0e0e0;
                    border-radius: 10px;
                    padding: 15px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QGroupBox::title {
                    color: #2c3e50;
                }
            """
            input_style = """
                QLineEdit {
                    background-color: white;
                    color: #2c3e50;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #3498db;
                }
            """
        
        # Appliquer aux groupes
        if hasattr(self, 'scan_group'):
            self.scan_group.setStyleSheet(group_style)
        if hasattr(self, 'quick_purchase_group'):
            self.quick_purchase_group.setStyleSheet(group_style)
        
        # Appliquer aux inputs
        if hasattr(self, 'scan_input'):
            self.scan_input.setStyleSheet(input_style)

