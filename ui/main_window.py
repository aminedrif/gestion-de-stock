# -*- coding: utf-8 -*-
"""
Fenêtre principale de l'application
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QStackedWidget, QMessageBox,
                             QStatusBar, QToolBar, QComboBox, QFrame, QApplication, QShortcut)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QKeySequence
from core.auth import auth_manager
from core.logger import logger
from ui.home_page import HomePage
from ui.pos_page import POSPage
from ui.products_page import ProductsPage
from ui.customers_page import CustomersPage
from ui.suppliers_page import SuppliersPage
from ui.reports_page import ReportsPage
from ui.settings_page import SettingsPage
import config


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.current_widget = None
        self.is_dark_mode = False
        self.page_map = {} # Pour stocker les références des pages
        
        # Configuration de la fenêtre
        self.setWindowTitle(f"{config.APP_NAME} - {user_data['full_name']}")
        self.setGeometry(100, 100, 1280, 720)
        
        # Initialiser l'UI
        self.init_ui()
        
        # Créer raccourcis
        self.create_shortcuts()
        
        # Créer la barre d'outils
        self.create_toolbar()
        
        # Démarrer le timer pour l'horloge
        self.start_clock()
        
        # Appliquer le style initial
        self.apply_theme()
        
        logger.info(f"Fenêtre principale ouverte pour {user_data['username']}")
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Menu latéral
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Zone de contenu
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area)
        
        # Ajouter les pages
        self.add_pages()
        
        central_widget.setLayout(main_layout)
        
        # Barre de statut
        self.create_status_bar()
    
    def create_sidebar(self):
        """Créer le menu latéral avec design moderne"""
        sidebar = QWidget()
        sidebar.setFixedWidth(250)
        
        # Style du dégradé (sera mis à jour par le thème)
        self.sidebar_style = """
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50,
                    stop:1 #34495e
                );
            }
        """
        sidebar.setStyleSheet(self.sidebar_style)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(0, 30, 0, 30)
        
        # Logo/Titre - Plus grand
        logo_label = QLabel("🏪")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("font-size: 64px; background: transparent; border: none;")
        layout.addWidget(logo_label)
        
        title_label = QLabel("AKHRIB Supérette")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 22px; font-weight: bold; padding: 8px; background: transparent; border: none;")
        layout.addWidget(title_label)
        
        # Bouton Thème (Mode Sombre/Clair) - Plus visible
        self.theme_btn = QPushButton("🌙  Mode Sombre")
        self.theme_btn.setCheckable(True)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setMinimumHeight(40)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 20px;
                padding: 8px 20px;
                margin: 5px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.25);
                border-color: rgba(255, 255, 255, 0.5);
            }
            QPushButton:checked {
                background-color: #f1c40f;
                color: #2c3e50;
                border: none;
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme_sidebar)
        layout.addWidget(self.theme_btn)
        
        layout.addSpacing(25)
        
        # Boutons de menu
        self.menu_buttons = {}
        
        btn_home = self.create_menu_button("🏠  Accueil (F1)", "home")
        layout.addWidget(btn_home)
        self.menu_buttons['home'] = btn_home
        
        btn_pos = self.create_menu_button("🛒  Caisse (F2)", "pos")
        layout.addWidget(btn_pos)
        self.menu_buttons['pos'] = btn_pos
        
        if auth_manager.has_permission('manage_products'):
            btn_products = self.create_menu_button("📦  Produits (F3)", "products")
            layout.addWidget(btn_products)
            self.menu_buttons['products'] = btn_products
        
        if auth_manager.has_permission('view_customers'):
            btn_customers = self.create_menu_button("👥  Clients (F4)", "customers")
            layout.addWidget(btn_customers)
            self.menu_buttons['customers'] = btn_customers
        
        if auth_manager.has_permission('manage_suppliers'):
            btn_suppliers = self.create_menu_button("🏭  Fournisseurs (F5)", "suppliers")
            layout.addWidget(btn_suppliers)
            self.menu_buttons['suppliers'] = btn_suppliers
        
        if auth_manager.has_permission('view_reports'):
            btn_reports = self.create_menu_button("📊  Rapports (F6)", "reports")
            layout.addWidget(btn_reports)
            self.menu_buttons['reports'] = btn_reports
        
        # Accessible à tous (le contenu sera filtré dans la page)
        btn_settings = self.create_menu_button("⚙️  Paramètres (F10)", "settings")
        layout.addWidget(btn_settings)
        self.menu_buttons['settings'] = btn_settings
        
        layout.addStretch()
        
        # Bouton déconnexion
        btn_logout = QPushButton("🚪  Déconnexion")
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                padding: 10px;
                border-radius: 5px;
                margin: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_logout.clicked.connect(self.logout)
        layout.addWidget(btn_logout)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def create_menu_button(self, text, page_name):
        """Créer un bouton de menu avec design moderne"""
        button = QPushButton(text)
        button.setCheckable(True)
        button.setMinimumHeight(55)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-left: 5px solid transparent;
                padding-left: 25px;
                text-align: left;
                font-size: 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
                border-left: 5px solid rgba(255, 255, 255, 0.5);
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.25);
                border-left: 5px solid #3498db;
                font-weight: bold;
            }
        """)
        button.clicked.connect(lambda: self.switch_page(page_name))
        return button
    
    def create_shortcuts(self):
        """Créer les raccourcis clavier"""
        shortcuts = [
            ("F1", "home"),
            ("F2", "pos"),
            ("F3", "products"),
            ("F4", "customers"),
            ("F5", "suppliers"),
            ("F6", "reports"),
            ("F10", "settings"),
        ]
        
        for key, page in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self)
            # Utilisation de lambda avec un argument par défaut pour capturer la valeur
            shortcut.activated.connect(lambda p=page: self.switch_page(p))
            
    def add_pages(self):
        """Ajouter les pages au contenu"""
        self.page_map = {}
        
        # Page d'accueil
        self.home_page = HomePage()
        self.home_page.navigate_to.connect(self.switch_page)
        self.home_page.quick_scan.connect(self.handle_quick_scan)
        self.content_area.addWidget(self.home_page)
        self.page_map['home'] = self.home_page
        
        # Caisse (toujours disponible)
        self.pos_page = POSPage()
        self.content_area.addWidget(self.pos_page)
        self.page_map['pos'] = self.pos_page
        
        # Produits
        if auth_manager.has_permission('manage_products'):
            products_page = ProductsPage()
            self.content_area.addWidget(products_page)
            self.page_map['products'] = products_page
        
        # Clients
        if auth_manager.has_permission('view_customers'):
            customers_page = CustomersPage()
            self.content_area.addWidget(customers_page)
            self.page_map['customers'] = customers_page
        
        # Fournisseurs
        if auth_manager.has_permission('manage_suppliers'):
            suppliers_page = SuppliersPage()
            self.content_area.addWidget(suppliers_page)
            self.page_map['suppliers'] = suppliers_page
        
        # Rapports
        if auth_manager.has_permission('view_reports'):
            reports_page = ReportsPage()
            self.content_area.addWidget(reports_page)
            self.page_map['reports'] = reports_page
        
        # Paramètres
        if auth_manager.is_admin():
            self.settings_page = SettingsPage()
            self.settings_page.theme_changed.connect(self.set_theme)
            self.content_area.addWidget(self.settings_page)
            self.page_map['settings'] = self.settings_page
    
    def handle_quick_scan(self, barcode):
        """Gérer le scan rapide depuis l'accueil"""
        # Basculer vers Caisse
        self.switch_page('pos')
        # Ajouter le produit
        self.pos_page.barcode_input.setText(barcode)
        self.pos_page.scan_product()
    
    def switch_page(self, page_name):
        """Changer de page"""
        if page_name in self.page_map:
            target_widget = self.page_map[page_name]
            self.content_area.setCurrentWidget(target_widget)
            
            # Rafraîchir les données si la page le supporte
            if hasattr(target_widget, 'refresh'):
                target_widget.refresh()
            
            # Mettre à jour les boutons
            for name, button in self.menu_buttons.items():
                button.setChecked(name == page_name)
                
            logger.info(f"Navigation vers: {page_name}")
        else:
            logger.warning(f"Page non disponible ou droits insuffisants: {page_name}")
    
    def create_toolbar(self):
        """Créer la barre d'outils"""
        pass
        
    def create_status_bar(self):
        """Créer la barre de statut"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.clock_label = QLabel()
        self.statusBar.addPermanentWidget(self.clock_label)
    
    def start_clock(self):
        """Démarrer l'horloge"""
        self.update_clock()
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
    
    def update_clock(self):
        current_time = QDateTime.currentDateTime()
        self.clock_label.setText(current_time.toString("dddd dd MMMM yyyy - HH:mm:ss"))
    
    def apply_theme(self):
        """Appliquer le thème actuel à TOUTES les pages via QPalette"""
        app = QApplication.instance()
        
        if self.is_dark_mode:
            # Thème sombre - via QPalette (affecte TOUS les widgets)
            app.setStyle("Fusion")
            palette = QPalette()
            
            # Couleurs de base sombres
            dark_bg = QColor(44, 62, 80)  # #2c3e50
            dark_alt = QColor(52, 73, 94)  # #34495e
            dark_text = QColor(236, 240, 241)  # #ecf0f1
            accent = QColor(52, 152, 219)  # #3498db
            
            palette.setColor(QPalette.Window, dark_bg)
            palette.setColor(QPalette.WindowText, dark_text)
            palette.setColor(QPalette.Base, dark_alt)
            palette.setColor(QPalette.AlternateBase, dark_bg)
            palette.setColor(QPalette.ToolTipBase, dark_text)
            palette.setColor(QPalette.ToolTipText, dark_bg)
            palette.setColor(QPalette.Text, dark_text)
            palette.setColor(QPalette.Button, dark_alt)
            palette.setColor(QPalette.ButtonText, dark_text)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, accent)
            palette.setColor(QPalette.Highlight, accent)
            palette.setColor(QPalette.HighlightedText, Qt.white)
            
            # Couleurs désactivées
            palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
            palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
            
            app.setPalette(palette)
            
            # Style minimal pour content_area - laisser QPalette faire le travail
            self.content_area.setStyleSheet("")
            
            # Sidebar en mode sombre
            self.sidebar.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1a252f, stop:1 #2c3e50);
                }
            """)
                
        else:
            # Thème clair (défaut)
            app.setStyle("Fusion")
            palette = QPalette()
            
            # Couleurs de base claires
            light_bg = QColor(245, 245, 245)  # #f5f5f5
            light_base = QColor(255, 255, 255)  # white
            light_alt = QColor(248, 249, 250)  # #f8f9fa
            dark_text = QColor(44, 62, 80)  # #2c3e50
            accent = QColor(52, 152, 219)  # #3498db
            
            palette.setColor(QPalette.Window, light_bg)
            palette.setColor(QPalette.WindowText, dark_text)
            palette.setColor(QPalette.Base, light_base)
            palette.setColor(QPalette.AlternateBase, light_alt)
            palette.setColor(QPalette.ToolTipBase, dark_text)
            palette.setColor(QPalette.ToolTipText, light_base)
            palette.setColor(QPalette.Text, dark_text)
            palette.setColor(QPalette.Button, light_bg)
            palette.setColor(QPalette.ButtonText, dark_text)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, accent)
            palette.setColor(QPalette.Highlight, accent)
            palette.setColor(QPalette.HighlightedText, Qt.white)
            
            app.setPalette(palette)
            
            # Réinitialiser le style
            self.content_area.setStyleSheet("")
            
            # Sidebar en mode clair
            self.sidebar.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2c3e50, stop:1 #34495e);
                }
            """)

        # Mettre à jour le bouton
        if hasattr(self, 'theme_btn'):
            if self.is_dark_mode:
                self.theme_btn.setText("☀️  Mode Clair")
                self.theme_btn.setChecked(True)
            else:
                self.theme_btn.setText("🌙  Mode Sombre")
                self.theme_btn.setChecked(False)
        
        # Forcer la mise à jour de tous les widgets enfants
        self.update_all_widgets(self.content_area)
        
        # Appeler set_dark_mode sur les pages qui l'implémentent
        for page_name in ['pos_page', 'products_page', 'customers_page', 'suppliers_page', 'reports_page', 'home_page', 'settings_page']:
            page = getattr(self, page_name, None)
            if page and hasattr(page, 'set_dark_mode'):
                page.set_dark_mode(self.is_dark_mode)
    
    def update_all_widgets(self, parent_widget):
        """Mettre à jour récursivement tous les widgets pour appliquer le thème"""
        import re
        for child in parent_widget.findChildren(QWidget):
            current_style = child.styleSheet()
            if current_style:
                # Pattern pour détecter les backgrounds blancs (tous les formats)
                white_bg_pattern = re.compile(
                    r'background(?:-color)?\s*:\s*(white|#fff(?:fff)?|#ffffff)\s*;',
                    re.IGNORECASE
                )
                
                if white_bg_pattern.search(current_style):
                    if self.is_dark_mode:
                        # Remplacer par couleur sombre
                        new_style = white_bg_pattern.sub('background-color: #34495e;', current_style)
                    else:
                        # Garder blanc en mode clair
                        new_style = current_style
                    child.setStyleSheet(new_style)
            
            # Forcer la mise à jour visuelle
            child.update()
            child.repaint()
            
    def set_theme(self, is_dark):
        """Slot pour changer le thème"""
        self.is_dark_mode = is_dark
        self.apply_theme()
        
    def toggle_theme_sidebar(self):
        """Basculer le thème depuis la sidebar"""
        self.set_theme(self.theme_btn.isChecked())
        
    def logout(self):
        reply = QMessageBox.question(self, "Déconnexion", "Se déconnecter ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            auth_manager.logout()
            self.close()
