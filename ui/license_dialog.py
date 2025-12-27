# -*- coding: utf-8 -*-
"""
Dialogue d'activation de licence - Design Premium & Moderne
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QApplication, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QPalette, QBrush
from core.license import license_manager


class LicenseDialog(QDialog):
    """Dialogue d'activation de licence - Premium UI"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(600, 500) # Allow resizing
        self.machine_id = license_manager.get_machine_id()
        self.init_ui()
        self.resize(700, 550) # Initial size Increased
        self.center_on_screen()
        self.old_pos = self.pos()
        
    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        self.move(
            (screen.width() - window.width()) // 2,
            (screen.height() - window.height()) // 2
        )
        
    def init_ui(self):
        # Main Container with Gradient Border Effect
        self.main_container = QFrame(self)
        self.main_container.setGeometry(10, 10, 680, 530) # Adjusted for new width
        self.main_container.setStyleSheet("""
            QFrame#mainContainer {
                background-color: white;
                border-radius: 20px;
                border: 1px solid #e5e7eb;
            }
        """)
        self.main_container.setObjectName("mainContainer")
        
        # Soft Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 10)
        self.main_container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self.main_container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        # --- HEADER ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        # Icon/Emoji
        icon_label = QLabel("🔐")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 42px; background: transparent;")
        header_layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Activation de Licence")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold)) # Reduced font size again
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #111827; letter-spacing: 0.5px;")
        header_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Pour utiliser ce logiciel, vous devez l'activer.\nEnvoyez votre ID Machine au développeur.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6b7280; font-size: 12px; line-height: 1.4;") # Reduced font size
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # --- MACHINE ID SECTION ---
        id_frame = QFrame()
        id_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 2px dashed #cbd5e1;
                border-radius: 12px;
            }
        """)
        id_layout = QVBoxLayout(id_frame)
        id_layout.setContentsMargins(20, 15, 20, 15)
        id_layout.setSpacing(10)
        
        id_label = QLabel("VOTRE ID MACHINE")
        id_label.setAlignment(Qt.AlignCenter)
        id_label.setStyleSheet("color: #64748b; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        id_layout.addWidget(id_label)
        
        # ID Display
        id_val_layout = QHBoxLayout()
        id_val_layout.setSpacing(10)
        
        self.id_value = QLabel(self.machine_id)
        self.id_value.setFont(QFont("Consolas", 16, QFont.Bold)) # Reduced font size
        self.id_value.setAlignment(Qt.AlignCenter)
        self.id_value.setStyleSheet("color: #0f172a; background: transparent;")
        self.id_value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        id_val_layout.addWidget(self.id_value)
        
        # Copy Button (Icon only style)
        self.copy_btn = QPushButton("📋 Copier")
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setFixedSize(90, 32)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #e2e8f0;
                color: #334155;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #cbd5e1;
                color: #0f172a;
            }
            QPushButton:pressed {
                background-color: #94a3b8;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_machine_id)
        id_val_layout.addWidget(self.copy_btn)
        
        id_layout.addLayout(id_val_layout)
        layout.addWidget(id_frame)
        
        # --- INPUT SECTION ---
        input_layout = QVBoxLayout()
        input_layout.setSpacing(8)
        
        lbl_key = QLabel("Clé de licence")
        lbl_key.setStyleSheet("color: #374151; font-weight: 600; font-size: 13px;")
        input_layout.addWidget(lbl_key)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Ex: PRO-XXXX-XXXX-XXXX")
        self.key_input.setMinimumHeight(50)
        self.key_input.setFont(QFont("Consolas", 14))
        self.key_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #e5e7eb;
                border-radius: 10px;
                padding: 0 15px;
                color: #111827;
                selection-background-color: #4f46e5;
            }
            QLineEdit:focus {
                border-color: #4f46e5;
            }
        """)
        self.key_input.returnPressed.connect(self.activate)
        input_layout.addWidget(self.key_input)
        
        layout.addLayout(input_layout)
        
        # --- ACTIONS ---
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        self.quit_btn = QPushButton("Quitter")
        self.quit_btn.setMinimumHeight(50)
        self.quit_btn.setCursor(Qt.PointingHandCursor)
        self.quit_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #ef4444;
                border: 2px solid #fee2e2;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #fef2f2;
                border-color: #fecaca;
            }
        """)
        self.quit_btn.clicked.connect(self.reject)
        actions_layout.addWidget(self.quit_btn, 1)
        
        self.activate_btn = QPushButton("Activer")
        self.activate_btn.setMinimumHeight(50)
        self.activate_btn.setCursor(Qt.PointingHandCursor)
        self.activate_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f46e5, stop:1 #4338ca);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4338ca, stop:1 #3730a3);
            }
        """)
        self.activate_btn.clicked.connect(self.activate)
        actions_layout.addWidget(self.activate_btn, 2)
        
        layout.addLayout(actions_layout)
        
        # Footer
        contact = QLabel("Contact: amine.drif2002@gmail.com | 0561491987")
        contact.setAlignment(Qt.AlignCenter)
        contact.setStyleSheet("color: #9ca3af; font-size: 11px;")
        contact.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(contact)

    def copy_machine_id(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.machine_id)
        
        # Visual feedback on button
        original_text = self.copy_btn.text()
        self.copy_btn.setText("✓ Copié")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #dcfce7;
                color: #166534;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        # Reset after 2 seconds (using QTimer would be ideal but keep it simple)
        QApplication.processEvents()
        
    def activate(self):
        key = self.key_input.text().strip()
        if not key:
            self.shake_window()
            return
        
        success, message = license_manager.activate_license(key)
        
        if success:
            QMessageBox.information(self, "Activation Réussie", "Licence activée avec succès !\nBienvenue dans DamDev POS.")
            self.accept()
        else:
            QMessageBox.critical(self, "Erreur d'Activation", message)
            self.shake_window()
            self.key_input.selectAll()
            self.key_input.setFocus()
            
    def shake_window(self):
        anim = QPropertyAnimation(self.main_container, b"pos")
        anim.setDuration(100)
        anim.setLoopCount(3)
        current = self.main_container.pos()
        anim.setKeyValueAt(0, current)
        anim.setKeyValueAt(0.25, QPoint(current.x() - 5, current.y()))
        anim.setKeyValueAt(0.75, QPoint(current.x() + 5, current.y()))
        anim.setKeyValueAt(1, current)
        anim.start()
        self.anim = anim # keep ref

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()
