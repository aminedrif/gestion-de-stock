# -*- coding: utf-8 -*-
"""
Interface des rapports
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDateEdit, QTableWidget, QTableWidgetItem,
                             QComboBox, QFrame, QHeaderView, QTabWidget, QGridLayout, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QFont
from modules.reports.profit_report import profit_report_manager
from core.logger import logger
import datetime

class KPICard(QFrame):
    def __init__(self, title, value, color="#3498db", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
                border-left: 5px solid {color};
            }}
        """)
        self.setMinimumSize(200, 100)
        
        layout = QVBoxLayout()
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #7f8c8d; font-size: 14px; border: none;")
        layout.addWidget(title_lbl)
        
        self.value_lbl = QLabel(value)
        self.value_lbl.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold; border: none;")
        self.value_lbl.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.value_lbl)
        
        self.setLayout(layout)
        
    def set_value(self, value):
        self.value_lbl.setText(str(value))

class ReportsPage(QWidget):
    """Page des rapports et statistiques"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.refresh_data()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # En-tête
        header = QLabel("📊 Rapports & Statistiques")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Toolbar (Période) - Améliorée
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        period_label = QLabel("📅 Période:")
        period_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        toolbar.addWidget(period_label)
        
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setMinimumHeight(50)
        self.start_date.setStyleSheet("""
            QDateEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
        """)
        toolbar.addWidget(self.start_date)
        
        toolbar.addWidget(QLabel(" à "))
        
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumHeight(50)
        self.end_date.setStyleSheet("""
            QDateEdit {
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                background-color: white;
            }
        """)
        toolbar.addWidget(self.end_date)
        
        refresh_btn = QPushButton("🔄 Actualiser")
        refresh_btn.setMinimumHeight(50)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        toolbar.addWidget(refresh_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # KPI Cards (Cartes indicateurs) - Plus grandes
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(15)
        self.card_sales = KPICard("Chiffre d'Affaires", "0 DA", "#3498db")
        self.card_profit = KPICard("Bénéfice Net", "0 DA", "#2ecc71")
        self.card_margin = KPICard("Marge", "0%", "#f1c40f")
        self.card_count = KPICard("Nombre de Ventes", "0", "#9b59b6")
        
        kpi_layout.addWidget(self.card_sales)
        kpi_layout.addWidget(self.card_profit)
        kpi_layout.addWidget(self.card_margin)
        kpi_layout.addWidget(self.card_count)
        layout.addLayout(kpi_layout)
        
        # Style pour les tables
        table_style = """
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
                background-color: #f39c12;
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
        """
        
        # Onglets Détails
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::pane { border: none; } QTabBar::tab { padding: 10px 20px; font-size: 14px; }")
        
        # Onglet 1: Ventes par jour
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(4)
        self.daily_table.setHorizontalHeaderLabels(["Date", "Ventes", "Coût", "Bénéfice"])
        self.daily_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.daily_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.daily_table.setAlternatingRowColors(True)
        self.daily_table.verticalHeader().setDefaultSectionSize(45)
        self.daily_table.setStyleSheet(table_style)
        tabs.addTab(self.daily_table, "📅 Ventes par Jour")
        
        # Onglet 2: Top Produits
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels(["Produit", "Qté Vendue", "CA", "Bénéfice", "Marge"])
        self.product_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.product_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.product_table.setAlternatingRowColors(True)
        self.product_table.verticalHeader().setDefaultSectionSize(45)
        self.product_table.setStyleSheet(table_style)
        tabs.addTab(self.product_table, "📦 Top Produits")
        
        # Onglet 3: Ventes par Utilisateur
        self.user_sales_table = QTableWidget()
        self.user_sales_table.setColumnCount(5)
        self.user_sales_table.setHorizontalHeaderLabels(["Utilisateur", "Rôle", "Nb Ventes", "CA Total", "Bénéfice"])
        self.user_sales_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.user_sales_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.user_sales_table.setAlternatingRowColors(True)
        self.user_sales_table.verticalHeader().setDefaultSectionSize(45)
        self.user_sales_table.setStyleSheet(table_style)
        tabs.addTab(self.user_sales_table, "👤 Ventes par Utilisateur")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
    def refresh_data(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        
        # 1. Global KPIs
        stats = profit_report_manager.get_profit_by_period(start, end)
        
        self.card_sales.set_value(f"{stats['total_revenue']:,.2f} DA")
        self.card_profit.set_value(f"{stats['net_profit']:,.2f} DA")
        self.card_margin.set_value(f"{stats['profit_margin']}%")
        self.card_count.set_value(str(stats['sale_count']))
        
        # 2. Daily Trend
        trend = profit_report_manager.get_daily_profit_trend(start, end)
        self.daily_table.setRowCount(0)
        for day in trend:
            row = self.daily_table.rowCount()
            self.daily_table.insertRow(row)
            self.daily_table.setItem(row, 0, QTableWidgetItem(day['date']))
            self.daily_table.setItem(row, 1, QTableWidgetItem(f"{day['revenue']:.2f}"))
            self.daily_table.setItem(row, 2, QTableWidgetItem(f"{day['cost']:.2f}"))
            
            profit_item = QTableWidgetItem(f"{day['profit']:.2f}")
            if day['profit'] > 0:
                profit_item.setForeground(QColor("green"))
            else:
                profit_item.setForeground(QColor("red"))
            self.daily_table.setItem(row, 3, profit_item)
            
        # 3. Top Products
        products = profit_report_manager.get_profit_by_product(start, end)
        self.product_table.setRowCount(0)
        for p in products:
            row = self.product_table.rowCount()
            self.product_table.insertRow(row)
            self.product_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.product_table.setItem(row, 1, QTableWidgetItem(str(p['quantity_sold'])))
            self.product_table.setItem(row, 2, QTableWidgetItem(f"{p['revenue']:.2f}"))
            self.product_table.setItem(row, 3, QTableWidgetItem(f"{p['profit']:.2f}"))
            self.product_table.setItem(row, 4, QTableWidgetItem(f"{p['profit_margin']}%"))
        
        # 4. Sales by User
        self.load_sales_by_user(start, end)

    def load_sales_by_user(self, start_date: str, end_date: str):
        """Charger les ventes par utilisateur"""
        from database.db_manager import db
        
        query = """
            SELECT 
                u.id,
                u.full_name,
                u.role,
                COUNT(s.id) as sale_count,
                COALESCE(SUM(s.total_amount), 0) as total_revenue,
                COALESCE(SUM(
                    (SELECT SUM((si.unit_price - si.purchase_price) * si.quantity)
                     FROM sale_items si
                     WHERE si.sale_id = s.id)
                ), 0) as total_profit
            FROM users u
            LEFT JOIN sales s ON u.id = s.cashier_id 
                AND s.status = 'completed'
                AND DATE(s.sale_date) BETWEEN ? AND ?
            WHERE u.is_active = 1
            GROUP BY u.id, u.full_name, u.role
            ORDER BY total_revenue DESC
        """
        
        results = db.execute_query(query, (start_date, end_date))
        
        self.user_sales_table.setRowCount(0)
        for user in results:
            row = self.user_sales_table.rowCount()
            self.user_sales_table.insertRow(row)
            
            self.user_sales_table.setItem(row, 0, QTableWidgetItem(user['full_name']))
            self.user_sales_table.setItem(row, 1, QTableWidgetItem(user['role']))
            self.user_sales_table.setItem(row, 2, QTableWidgetItem(str(user['sale_count'])))
            
            revenue_item = QTableWidgetItem(f"{user['total_revenue']:.2f} DA")
            revenue_item.setForeground(QColor("#3498db"))
            self.user_sales_table.setItem(row, 3, revenue_item)
            
            profit_item = QTableWidgetItem(f"{user['total_profit']:.2f} DA")
            if user['total_profit'] > 0:
                profit_item.setForeground(QColor("green"))
            else:
                profit_item.setForeground(QColor("red"))
            self.user_sales_table.setItem(row, 4, profit_item)

    def refresh(self):
        """Rafraîchir les données"""
        self.refresh_data()
    
    def set_dark_mode(self, is_dark):
        """Appliquer le mode sombre/clair"""
        if is_dark:
            # Mode sombre pour les KPI cards
            kpi_style = """
                QFrame {
                    background-color: #34495e;
                    border-radius: 10px;
                    padding: 15px;
                }
                QLabel {
                    color: #ecf0f1;
                }
            """
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
                    background-color: #3498db;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #2c3e50;
                }
                QHeaderView::section {
                    background-color: #3498db;
                    color: white;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                }
            """
            input_style = """
                QDateEdit {
                    background-color: #34495e;
                    color: #ecf0f1;
                    border: 2px solid #4a6785;
                    border-radius: 8px;
                    padding: 8px;
                }
            """
        else:
            # Mode clair
            kpi_style = """
                QFrame {
                    background-color: white;
                    border-radius: 10px;
                    padding: 15px;
                }
                QLabel {
                    color: #2c3e50;
                }
            """
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
                    background-color: #3498db;
                    color: white;
                }
                QTableWidget::item:alternate {
                    background-color: #f8f9fa;
                }
                QHeaderView::section {
                    background-color: #3498db;
                    color: white;
                    padding: 10px;
                    border: none;
                    font-weight: bold;
                }
            """
            input_style = """
                QDateEdit {
                    background-color: white;
                    color: #2c3e50;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 8px;
                }
            """
        
        # Appliquer aux KPI
        for kpi in [self.total_sales_kpi, self.profit_kpi, self.profit_margin_kpi, self.avg_basket_kpi]:
            kpi.setStyleSheet(kpi_style)
        
        # Appliquer aux tables
        for table in [self.sales_table, self.profits_table, self.user_sales_table]:
            table.setStyleSheet(table_style)
        
        # Appliquer aux inputs
        if hasattr(self, 'start_date'):
            self.start_date.setStyleSheet(input_style)
        if hasattr(self, 'end_date'):
            self.end_date.setStyleSheet(input_style)

