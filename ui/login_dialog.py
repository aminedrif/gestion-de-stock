# -*- coding: utf-8 -*-
"""
Dialogue de connexion - Design Premium Modern (Split Layout)
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect,
                             QWidget, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QFont, QColor, QIcon, QLinearGradient, QPalette, QBrush, QPixmap
from core.auth import auth_manager
from core.logger import logger
import config
import os

class LoginDialog(QDialog):
    """Dialogue de connexion moderne avec layout séparé (Split View)"""
    
    login_successful = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setStyleSheet("background: transparent;") # Fix for white corners
        self.setFixedSize(900, 550)
        
        self.init_ui()
        self.center_on_screen()
        
        # Variables pour le déplacement de la fenêtre
        self.old_pos = self.pos()
        
    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        self.move(
            (screen.width() - window.width()) // 2,
            (screen.height() - window.height()) // 2
        )
        
    def init_ui(self):
        # Container principal (arrondi)
        self.main_container = QFrame(self)
        self.main_container.setGeometry(10, 10, 880, 530) # Leaving space for shadow
        self.main_container.setStyleSheet("""
            QFrame#mainContainer {
                background-color: white;
                border-radius: 20px;
            }
        """)
        self.main_container.setObjectName("mainContainer")
        
        # Ombre portée
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        self.main_container.setGraphicsEffect(shadow)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- PARTIE GAUCHE (BRANDING) ---
        self.left_panel = QFrame()
        self.left_panel.setObjectName("leftPanel")
        self.left_panel.setStyleSheet("""
            QFrame#leftPanel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #4f46e5, stop:1 #7c3aed);
                border-top-left-radius: 20px;
                border-bottom-left-radius: 20px;
                border: none;
            }
        """)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(40, 60, 40, 60)
        
        # Logo/Icon
        logo_icon = QLabel()
        logo_icon.setAlignment(Qt.AlignCenter)
        
        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background-color: transparent; border: none;")
        
        logo_path = str(config.LOGO_PATH)
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_icon.setPixmap(scaled_pixmap)
        else:
            logo_icon.setText("📊")
            logo_icon.setStyleSheet("font-size: 80px; background: transparent; border: none;")
            
        left_layout.addWidget(logo_icon)
        
        left_layout.addSpacing(20)
        
        # Titre App
        app_title = QLabel("DamDev POS")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setFont(QFont("Segoe UI", 26, QFont.Bold))
        app_title.setStyleSheet("color: white; background: transparent; border: none;")
        left_layout.addWidget(app_title)
        
        # Slogan
        slogan = QLabel("La gestion de stock\nsimple et intelligente.")
        slogan.setAlignment(Qt.AlignCenter)
        slogan.setStyleSheet("color: rgba(255,255,255,0.8); font-size: 16px; background: transparent; border: none;")
        left_layout.addWidget(slogan)
        
        left_layout.addStretch()
        
        # Version
        version = QLabel(f"v{config.APP_VERSION}")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 12px; background: transparent; border: none;")
        left_layout.addWidget(version)
        
        main_layout.addWidget(self.left_panel, 40) # 40% largeur
        
        # --- PARTIE DROITE (FORMULAIRE) ---
        self.right_panel = QFrame()
        self.right_panel.setObjectName("rightPanel")
        self.right_panel.setStyleSheet("""
            QFrame#rightPanel {
                background-color: white;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
                border: none;
            }
        """)
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(50, 40, 50, 40)
        right_layout.setSpacing(20)
        
        # Bouton fermer (Custom)
        close_btn_layout = QHBoxLayout()
        close_btn_layout.addStretch()
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #9ca3af;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #fee2e2;
                color: #ef4444;
            }
        """)
        self.close_btn.clicked.connect(self.reject)
        close_btn_layout.addWidget(self.close_btn)
        right_layout.addLayout(close_btn_layout)
        
        # Titre Formulaire
        login_title = QLabel("Bon retour ! 👋")
        login_title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        login_title.setStyleSheet("color: #1f2937;")
        right_layout.addWidget(login_title)
        
        login_subtitle = QLabel("Veuillez entrer vos identifiants.")
        login_subtitle.setStyleSheet("color: #6b7280; font-size: 14px;")
        right_layout.addWidget(login_subtitle)
        
        right_layout.addSpacing(10)
        
        # Champ Username
        user_container = QFrame()
        user_container.setStyleSheet("""
            QFrame {
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #d1d5db;
            }
        """)
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(15, 5, 15, 5)
        
        user_icon = QLabel("👤")
        user_icon.setStyleSheet("background: transparent; font-size: 16px;")
        user_layout.addWidget(user_icon)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nom d'utilisateur")
        self.username_input.setMinimumHeight(45)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 15px;
                color: #374151;
            }
        """)
        self.username_input.returnPressed.connect(self.on_login)
        user_layout.addWidget(self.username_input)
        
        right_layout.addWidget(user_container)
        
        # Champ Password
        pass_container = QFrame()
        pass_container.setStyleSheet("""
            QFrame {
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #d1d5db;
            }
        """)
        pass_layout = QHBoxLayout(pass_container)
        pass_layout.setContentsMargins(15, 5, 15, 5)
        
        pass_icon = QLabel("🔒")
        pass_icon.setStyleSheet("background: transparent; font-size: 16px;")
        pass_layout.addWidget(pass_icon)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Mot de passe")
        self.password_input.setMinimumHeight(45)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                font-size: 15px;
                color: #374151;
            }
        """)
        self.password_input.returnPressed.connect(self.on_login)
        pass_layout.addWidget(self.password_input)
        
        right_layout.addWidget(pass_container)
        
        right_layout.addSpacing(10)

        # Error Message Label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 13px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        right_layout.addWidget(self.error_label)
        
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setMinimumHeight(50)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setDefault(True)  # Répondre à Enter
        self.login_btn.setAutoDefault(True)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4f46e5, stop:1 #6366f1);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4338ca, stop:1 #4f46e5);
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f3f4f6;
            }
        """)
        self.login_btn.clicked.connect(self.on_login)
        right_layout.addWidget(self.login_btn)
        
        # Default Creds Hint (Subtle)
        creds_label = QLabel("Admin par défaut: admin / admin123")
        creds_label.setAlignment(Qt.AlignCenter)
        creds_label.setStyleSheet("color: #9ca3af; font-size: 12px; margin-top: 10px;")
        right_layout.addWidget(creds_label)
        
        right_layout.addStretch()
        
        main_layout.addWidget(self.right_panel, 60) # 60% largeur
        
    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()
        
    def keyPressEvent(self, event):
        """Hide error when typing"""
        if self.error_label.isVisible():
            self.error_label.hide()
        super().keyPressEvent(event)
        
    def on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            self.shake_window()
            return

        self.login_btn.setText("Connexion...")
        self.login_btn.setEnabled(False)
        
        try:
            # Simulate slight delay for effect (optional, or just process)
            # Here we call auth directly
            success, message, user_data = auth_manager.login(username, password)
            
            if success:
                logger.info(f"Connexion réussie: {username}")
                self.login_successful.emit(user_data)
                self.accept()
            else:
                self.login_btn.setText("Se connecter")
                self.login_btn.setEnabled(True)
                self.shake_window()
                
                # Show error message
                self.error_label.setText(message)
                self.error_label.show()
                
                # Let's clean password
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            self.login_btn.setText("Se connecter")
            self.login_btn.setEnabled(True)
            self.error_label.setText(f"Erreur système: {e}")
            self.error_label.show()
            
    def shake_window(self):
        anim = QPropertyAnimation(self.main_container, b"pos")
        anim.setDuration(300)
        anim.setLoopCount(3)
        current_pos = self.main_container.pos()
        anim.setKeyValueAt(0, current_pos)
        anim.setKeyValueAt(0.2, QPoint(current_pos.x() - 10, current_pos.y()))
        anim.setKeyValueAt(0.5, QPoint(current_pos.x() + 10, current_pos.y()))
        anim.setKeyValueAt(0.8, QPoint(current_pos.x() - 10, current_pos.y()))
        anim.setKeyValueAt(1, current_pos)
        anim.start()
        self.anim = anim # keep ref
