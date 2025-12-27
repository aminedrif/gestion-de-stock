# -*- coding: utf-8 -*-
"""
Page d'accueil - Design Moderne avec Stats et Animations
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGridLayout, QLineEdit, QFrame, 
                             QGraphicsDropShadowEffect, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor
from datetime import datetime


class StatCard(QFrame):
    """Carte de statistique moderne"""
    
    clicked = pyqtSignal()
    
    def __init__(self, icon, title, value, subtitle, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setup_ui(icon, title, value, subtitle)
        
    def setup_ui(self, icon, title, value, subtitle):
        self.setMinimumSize(200, 140)
        self.setMaximumHeight(160)
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {self.color}, stop:1 {self.color}dd);
                border-radius: 18px;
                border: none;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 {self.color}ee, stop:1 {self.color}cc);
            }}
        """)
        
        # Ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(self.color))
        shadow.setOffset(0, 8)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Ligne 1: Icon + Title
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px; background: transparent;")
        top_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: rgba(255,255,255,0.9);
            font-size: 13px;
            background: transparent;
        """)
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        
        layout.addLayout(top_layout)
        
        # Valeur principale
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("""
            color: white;
            font-size: 32px;
            font-weight: bold;
            background: transparent;
        """)
        layout.addWidget(self.value_label)
        
        # Sous-titre
        sub_label = QLabel(subtitle)
        sub_label.setStyleSheet("""
            color: rgba(255,255,255,0.8);
            font-size: 12px;
            background: transparent;
        """)
        layout.addWidget(sub_label)
        
        self.setLayout(layout)
    
    def update_value(self, new_value):
        self.value_label.setText(new_value)

    def mousePressEvent(self, event):
        """Handle click event"""
        self.clicked.emit()
        super().mousePressEvent(event)


class QuickAccessButton(QPushButton):
    """Bouton d'accès rapide moderne"""
    
    def __init__(self, icon, title, subtitle, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setup_ui(icon, title, subtitle)
        
    def setup_ui(self, icon, title, subtitle):
        self.setMinimumSize(180, 130)
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 2px solid #f0f0f0;
                border-radius: 16px;
                padding: 20px;
            }}
            QPushButton:hover {{
                border-color: {self.color};
                background-color: #fafafa;
            }}
            QPushButton:pressed {{
                background-color: #f5f5f5;
            }}
        """)
        
        # Ombre légère
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        
        # Icône dans un cercle coloré
        icon_container = QLabel(icon)
        icon_container.setFixedSize(50, 50)
        icon_container.setAlignment(Qt.AlignCenter)
        icon_container.setStyleSheet(f"""
            background-color: {self.color}22;
            border-radius: 25px;
            font-size: 26px;
        """)
        layout.addWidget(icon_container, 0, Qt.AlignCenter)
        
        # Titre
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            color: #1f2937;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Sous-titre
        sub_label = QLabel(subtitle)
        sub_label.setStyleSheet("""
            color: #6b7280;
            font-size: 11px;
            background: transparent;
        """)
        sub_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(sub_label)
        
        self.setLayout(layout)


class HomePage(QWidget):
    """Page d'accueil avec design moderne"""
    
    navigate_to = pyqtSignal(str)
    quick_scan = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_stats()
    
    def init_ui(self):
        """Initialiser l'interface"""
        # Style de fond
        self.setStyleSheet("background-color: #f8fafc;")
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(25)
        main_layout.setContentsMargins(30, 25, 30, 25)
        
        # En-tête
        header = self.create_header()
        main_layout.addLayout(header)
        
        # Cartes de stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.stat_sales = StatCard("💰", "Ventes Aujourd'hui", "0 DA", "Chiffre d'affaires", "#8b5cf6")
        stats_layout.addWidget(self.stat_sales)
        
        self.stat_products = StatCard("📦", "Produits", "0", "En stock", "#3b82f6")
        stats_layout.addWidget(self.stat_products)
        
        self.stat_expiring = StatCard("📅", "Expiration", "0", "Expire bientôt", "#ef4444")
        self.stat_expiring.clicked.connect(lambda: self.navigate_to.emit("products"))
        stats_layout.addWidget(self.stat_expiring)
        
        self.stat_alerts = StatCard("⚠️", "Alertes", "0", "Stock faible", "#f59e0b")
        self.stat_alerts.clicked.connect(self.go_to_low_stock)
        stats_layout.addWidget(self.stat_alerts)
        
        main_layout.addLayout(stats_layout)
        
        # Zone de scan rapide
        scan_section = self.create_scan_section()
        main_layout.addWidget(scan_section)
        
        # Accès rapide
        access_title = QLabel("🚀 Accès Rapide")
        access_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1f2937;
            margin-top: 10px;
        """)
        main_layout.addWidget(access_title)
        
        access_layout = QHBoxLayout()
        access_layout.setSpacing(20)
        
        btn_pos = QuickAccessButton("🛒", "Caisse", "Vente rapide", "#8b5cf6")
        btn_pos.clicked.connect(lambda: self.navigate_to.emit("pos"))
        access_layout.addWidget(btn_pos)
        
        btn_products = QuickAccessButton("📦", "Produits", "Gérer stock", "#3b82f6")
        btn_products.clicked.connect(lambda: self.navigate_to.emit("products"))
        access_layout.addWidget(btn_products)
        
        btn_customers = QuickAccessButton("👥", "Clients", "Fidélité", "#10b981")
        btn_customers.clicked.connect(lambda: self.navigate_to.emit("customers"))
        access_layout.addWidget(btn_customers)
        
        btn_suppliers = QuickAccessButton("🏭", "Fournisseurs", "Dettes", "#f59e0b")
        btn_suppliers.clicked.connect(lambda: self.navigate_to.emit("suppliers"))
        access_layout.addWidget(btn_suppliers)
        
        btn_reports = QuickAccessButton("📊", "Rapports", "Statistiques", "#ef4444")
        btn_reports.clicked.connect(lambda: self.navigate_to.emit("reports"))
        access_layout.addWidget(btn_reports)
        
        main_layout.addLayout(access_layout)
        
        main_layout.addStretch()
        self.setLayout(main_layout)
    
    def create_header(self):
        """Créer l'en-tête"""
        layout = QHBoxLayout()
        
        # Titre avec salutation
        left_layout = QVBoxLayout()
        
        greeting = self.get_greeting()
        greeting_label = QLabel(f"{greeting} 👋")
        greeting_label.setStyleSheet("""
            font-size: 16px;
            color: #6b7280;
        """)
        left_layout.addWidget(greeting_label)
        
        title = QLabel("Tableau de Bord")
        title.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title.setStyleSheet("color: #1f2937;")
        left_layout.addWidget(title)
        
        layout.addLayout(left_layout)
        layout.addStretch()
        
        # Date
        now = datetime.now()
        date_frame = QFrame()
        date_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                padding: 10px 20px;
                border: 1px solid #e5e7eb;
            }
        """)
        date_layout = QVBoxLayout(date_frame)
        date_layout.setContentsMargins(15, 10, 15, 10)
        
        day_label = QLabel(now.strftime("%A"))
        day_label.setStyleSheet("color: #8b5cf6; font-weight: bold; font-size: 14px;")
        day_label.setAlignment(Qt.AlignCenter)
        date_layout.addWidget(day_label)
        
        date_label = QLabel(now.strftime("%d %B %Y"))
        date_label.setStyleSheet("color: #374151; font-size: 13px;")
        date_label.setAlignment(Qt.AlignCenter)
        date_layout.addWidget(date_label)
        
        layout.addWidget(date_frame)
        
        return layout
    
    def get_greeting(self):
        """Obtenir le message de salutation selon l'heure"""
        hour = datetime.now().hour
        if hour < 12:
            return "Bonjour"
        elif hour < 18:
            return "Bon après-midi"
        else:
            return "Bonsoir"
    
    def create_scan_section(self):
        """Créer la section de scan rapide"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 18px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(102, 126, 234, 100))
        shadow.setOffset(0, 10)
        frame.setGraphicsEffect(shadow)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        # Icône
        icon = QLabel("⚡")
        icon.setStyleSheet("font-size: 40px; background: transparent;")
        layout.addWidget(icon)
        
        # Texte
        text_layout = QVBoxLayout()
        
        title = QLabel("Scan Rapide")
        title.setStyleSheet("""
            color: white;
            font-size: 20px;
            font-weight: bold;
            background: transparent;
        """)
        text_layout.addWidget(title)
        
        subtitle = QLabel("Scannez un produit pour l'ajouter au panier")
        subtitle.setStyleSheet("""
            color: rgba(255,255,255,0.8);
            font-size: 13px;
            background: transparent;
        """)
        text_layout.addWidget(subtitle)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        # Input de scan
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Code-barres...")
        self.scan_input.setMinimumWidth(250)
        self.scan_input.setMinimumHeight(50)
        self.scan_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.95);
                border: none;
                border-radius: 12px;
                padding: 12px 20px;
                font-size: 15px;
                color: #1f2937;
            }
            QLineEdit:focus {
                background-color: white;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)
        self.scan_input.returnPressed.connect(self.handle_scan)
        layout.addWidget(self.scan_input)
        
        # Bouton
        scan_btn = QPushButton("🛒 Ajouter")
        scan_btn.setCursor(Qt.PointingHandCursor)
        scan_btn.setMinimumHeight(50)
        scan_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #667eea;
                border: none;
                border-radius: 12px;
                padding: 12px 25px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f8fafc;
            }
        """)
        scan_btn.clicked.connect(self.handle_scan)
        layout.addWidget(scan_btn)
        
        return frame
    
    def handle_scan(self):
        """Gérer le scan"""
        code = self.scan_input.text().strip()
        if code:
            self.quick_scan.emit(code)
            self.scan_input.clear()
    
    def load_stats(self):
        """Charger les statistiques"""
        try:
            from database.db_manager import db
            
            # Produits en stock
            products = db.fetch_one("SELECT COUNT(*) as count FROM products WHERE is_active = 1")
            if products:
                self.stat_products.update_value(str(products['count']))
            
            # Produits expirant bientôt (30 jours)
            from datetime import timedelta
            future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            expiring = db.fetch_one(f"""
                SELECT COUNT(*) as count FROM products 
                WHERE is_active = 1 AND expiry_date IS NOT NULL 
                AND expiry_date <= '{future_date}' AND expiry_date >= date('now')
            """)
            if expiring:
                self.stat_expiring.update_value(str(expiring['count']))
            
            # Ventes du jour
            today = datetime.now().strftime("%Y-%m-%d")
            sales = db.fetch_one(f"""
                SELECT COALESCE(SUM(total_amount), 0) as total 
                FROM sales 
                WHERE DATE(sale_date) = '{today}'
            """)
            if sales:
                self.stat_sales.update_value(f"{float(sales['total']):,.0f} DA")
            
            # Alertes stock faible (seuil = 10 par défaut)
            alerts = db.fetch_one("""
                SELECT COUNT(*) as count FROM products 
                WHERE is_active = 1 AND stock_quantity <= 10
            """)
            if alerts:
                self.stat_alerts.update_value(str(alerts['count']))
                
        except Exception as e:
            print(f"Erreur chargement stats: {e}")
    
    def refresh_stats(self):
        """Rafraîchir les statistiques"""
        self.load_stats()

    def go_to_low_stock(self):
        """Naviguer vers la page produits filtrée par stock faible"""
        self.navigate_to.emit("products_low_stock")
