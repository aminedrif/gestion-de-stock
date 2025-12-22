# -*- coding: utf-8 -*-
"""
Gestionnaire de rapports de ventes
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from database.db_manager import db
from core.logger import logger


class SalesReportManager:
    """Gestionnaire de rapports de ventes"""
    
    def get_sales_by_period(self, start_date: str, end_date: str,
                           cashier_id: int = None, 
                           customer_id: int = None) -> List[Dict]:
        """
        Obtenir les ventes par période
        
        Args:
            start_date: Date de début (YYYY-MM-DD)
            end_date: Date de fin (YYYY-MM-DD)
            cashier_id: Filtrer par caissier
            customer_id: Filtrer par client
            
        Returns:
            Liste des ventes
        """
        query = """
            SELECT s.*, u.full_name as cashier_name, c.full_name as customer_name
            FROM sales s
            LEFT JOIN users u ON s.cashier_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE date(s.sale_date) BETWEEN ? AND ?
              AND s.status = 'completed'
        """
        
        params = [start_date, end_date]
        
        if cashier_id:
            query += " AND s.cashier_id = ?"
            params.append(cashier_id)
        
        if customer_id:
            query += " AND s.customer_id = ?"
            params.append(customer_id)
        
        query += " ORDER BY s.sale_date DESC"
        
        results = db.execute_query(query, tuple(params))
        return [dict(row) for row in results]
    
    def get_daily_sales(self, date: str = None) -> Dict[str, Any]:
        """
        Obtenir les ventes du jour
        
        Args:
            date: Date (YYYY-MM-DD), None = aujourd'hui
            
        Returns:
            Dictionnaire avec les statistiques
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                COUNT(*) as sale_count,
                SUM(total_amount) as total_revenue,
                SUM(discount_amount) as total_discount,
                AVG(total_amount) as average_sale
            FROM sales
            WHERE date(sale_date) = ? AND status = 'completed'
        """
        
        result = db.fetch_one(query, (date,))
        
        stats = {
            'date': date,
            'sale_count': result['sale_count'] if result else 0,
            'total_revenue': round(result['total_revenue'], 2) if result and result['total_revenue'] else 0.0,
            'total_discount': round(result['total_discount'], 2) if result and result['total_discount'] else 0.0,
            'average_sale': round(result['average_sale'], 2) if result and result['average_sale'] else 0.0,
        }
        
        return stats
    
    def get_monthly_sales(self, year: int, month: int) -> Dict[str, Any]:
        """
        Obtenir les ventes du mois
        
        Args:
            year: Année
            month: Mois (1-12)
            
        Returns:
            Dictionnaire avec les statistiques
        """
        start_date = f"{year}-{month:02d}-01"
        
        # Calculer le dernier jour du mois
        if month == 12:
            end_date = f"{year}-12-31"
        else:
            next_month = datetime(year, month + 1, 1)
            last_day = next_month - timedelta(days=1)
            end_date = last_day.strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                COUNT(*) as sale_count,
                SUM(total_amount) as total_revenue,
                SUM(discount_amount) as total_discount,
                AVG(total_amount) as average_sale
            FROM sales
            WHERE date(sale_date) BETWEEN ? AND ?
              AND status = 'completed'
        """
        
        result = db.fetch_one(query, (start_date, end_date))
        
        stats = {
            'year': year,
            'month': month,
            'sale_count': result['sale_count'] if result else 0,
            'total_revenue': round(result['total_revenue'], 2) if result and result['total_revenue'] else 0.0,
            'total_discount': round(result['total_discount'], 2) if result and result['total_discount'] else 0.0,
            'average_sale': round(result['average_sale'], 2) if result and result['average_sale'] else 0.0,
        }
        
        return stats
    
    def get_sales_by_cashier(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Obtenir les ventes par caissier
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des statistiques par caissier
        """
        query = """
            SELECT 
                u.id,
                u.full_name as cashier_name,
                COUNT(s.id) as sale_count,
                SUM(s.total_amount) as total_revenue,
                AVG(s.total_amount) as average_sale
            FROM sales s
            JOIN users u ON s.cashier_id = u.id
            WHERE date(s.sale_date) BETWEEN ? AND ?
              AND s.status = 'completed'
            GROUP BY u.id, u.full_name
            ORDER BY total_revenue DESC
        """
        
        results = db.execute_query(query, (start_date, end_date))
        return [dict(row) for row in results]
    
    def get_sales_by_payment_method(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Obtenir les ventes par méthode de paiement
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des statistiques par méthode
        """
        query = """
            SELECT 
                payment_method,
                COUNT(*) as sale_count,
                SUM(total_amount) as total_amount
            FROM sales
            WHERE date(sale_date) BETWEEN ? AND ?
              AND status = 'completed'
            GROUP BY payment_method
            ORDER BY total_amount DESC
        """
        
        results = db.execute_query(query, (start_date, end_date))
        return [dict(row) for row in results]
    
    def get_top_selling_products(self, start_date: str, end_date: str, 
                                 limit: int = 10) -> List[Dict]:
        """
        Obtenir les produits les plus vendus
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            limit: Nombre de produits à retourner
            
        Returns:
            Liste des produits
        """
        query = """
            SELECT 
                p.id,
                p.name,
                p.name_ar,
                SUM(si.quantity) as total_quantity,
                SUM(si.subtotal) as total_revenue,
                COUNT(DISTINCT si.sale_id) as sale_count
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            JOIN sales s ON si.sale_id = s.id
            WHERE date(s.sale_date) BETWEEN ? AND ?
              AND s.status = 'completed'
            GROUP BY p.id, p.name, p.name_ar
            ORDER BY total_quantity DESC
            LIMIT ?
        """
        
        results = db.execute_query(query, (start_date, end_date, limit))
        return [dict(row) for row in results]
    
    def get_sales_by_category(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Obtenir les ventes par catégorie
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Liste des statistiques par catégorie
        """
        query = """
            SELECT 
                c.id,
                c.name as category_name,
                c.name_ar as category_name_ar,
                SUM(si.quantity) as total_quantity,
                SUM(si.subtotal) as total_revenue,
                COUNT(DISTINCT si.sale_id) as sale_count
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            JOIN sales s ON si.sale_id = s.id
            WHERE date(s.sale_date) BETWEEN ? AND ?
              AND s.status = 'completed'
            GROUP BY c.id, c.name, c.name_ar
            ORDER BY total_revenue DESC
        """
        
        results = db.execute_query(query, (start_date, end_date))
        return [dict(row) for row in results]
    
    def get_hourly_sales(self, date: str = None) -> List[Dict]:
        """
        Obtenir les ventes par heure
        
        Args:
            date: Date (YYYY-MM-DD), None = aujourd'hui
            
        Returns:
            Liste des ventes par heure
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        query = """
            SELECT 
                strftime('%H', sale_date) as hour,
                COUNT(*) as sale_count,
                SUM(total_amount) as total_revenue
            FROM sales
            WHERE date(sale_date) = ? AND status = 'completed'
            GROUP BY hour
            ORDER BY hour
        """
        
        results = db.execute_query(query, (date,))
        return [dict(row) for row in results]
    
    def export_to_dict(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Exporter un rapport complet en dictionnaire
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dictionnaire avec toutes les statistiques
        """
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
            },
            'sales': self.get_sales_by_period(start_date, end_date),
            'by_cashier': self.get_sales_by_cashier(start_date, end_date),
            'by_payment_method': self.get_sales_by_payment_method(start_date, end_date),
            'top_products': self.get_top_selling_products(start_date, end_date),
            'by_category': self.get_sales_by_category(start_date, end_date),
        }


# Instance globale
sales_report_manager = SalesReportManager()
