# -*- coding: utf-8 -*-
"""
Gestionnaire de clients
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from database.db_manager import db
from core.logger import logger


class CustomerManager:
    """Gestionnaire de clients"""
    
    def create_customer(self, full_name: str, phone: str = None,
                       email: str = None, address: str = None,
                       credit_limit: float = 0.0) -> tuple[bool, str, Optional[int]]:
        """
        Créer un nouveau client
        
        Args:
            full_name: Nom complet
            phone: Téléphone
            email: Email
            address: Adresse
            credit_limit: Limite de crédit autorisée
            
        Returns:
            (success, message, customer_id)
        """
        try:
            # Générer un code client unique
            code = self._generate_customer_code()
            
            # Insérer le client
            insert_query = """
                INSERT INTO customers (code, full_name, phone, email, address, credit_limit)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            customer_id = db.execute_insert(insert_query, (
                code, full_name, phone, email, address, credit_limit
            ))
            
            logger.info(f"Client créé: {full_name} (Code: {code})")
            return True, f"Client créé avec succès (Code: {code})", customer_id
            
        except Exception as e:
            error_msg = f"Erreur lors de la création du client: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def update_customer(self, customer_id: int, **kwargs) -> tuple[bool, str]:
        """
        Mettre à jour un client
        
        Args:
            customer_id: ID du client
            **kwargs: Champs à mettre à jour
            
        Returns:
            (success, message)
        """
        try:
            allowed_fields = ['full_name', 'phone', 'email', 'address', 'credit_limit', 'notes']
            
            updates = []
            params = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    params.append(value)
            
            if not updates:
                return False, "Aucune modification à effectuer"
            
            params.append(customer_id)
            
            query = f"UPDATE customers SET {', '.join(updates)} WHERE id = ?"
            rows_affected = db.execute_update(query, tuple(params))
            
            if rows_affected > 0:
                logger.info(f"Client mis à jour: ID {customer_id}")
                return True, "Client mis à jour avec succès"
            else:
                return False, "Client introuvable"
                
        except Exception as e:
            error_msg = f"Erreur lors de la mise à jour: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_customer(self, customer_id: int) -> tuple[bool, str]:
        """
        Supprimer un client (soft delete)
        
        Args:
            customer_id: ID du client
            
        Returns:
            (success, message)
        """
        try:
            # Vérifier s'il a des crédits en cours
            customer = self.get_customer(customer_id)
            if customer and customer['current_credit'] > 0:
                return False, f"Impossible de supprimer: crédit en cours de {customer['current_credit']} DA"
            
            query = "UPDATE customers SET is_active = 0 WHERE id = ?"
            rows_affected = db.execute_update(query, (customer_id,))
            
            if rows_affected > 0:
                logger.info(f"Client supprimé: ID {customer_id}")
                return True, "Client supprimé avec succès"
            else:
                return False, "Client introuvable"
                
        except Exception as e:
            error_msg = f"Erreur lors de la suppression: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_customer(self, customer_id: int) -> Optional[Dict]:
        """
        Obtenir un client par son ID
        
        Args:
            customer_id: ID du client
            
        Returns:
            Dictionnaire avec les données du client ou None
        """
        query = "SELECT * FROM customers WHERE id = ?"
        result = db.fetch_one(query, (customer_id,))
        return dict(result) if result else None
    
    def get_customer_by_code(self, code: str) -> Optional[Dict]:
        """
        Obtenir un client par son code
        
        Args:
            code: Code client
            
        Returns:
            Dictionnaire avec les données du client ou None
        """
        query = "SELECT * FROM customers WHERE code = ? AND is_active = 1"
        result = db.fetch_one(query, (code,))
        return dict(result) if result else None
    
    def search_customers(self, search_term: str) -> List[Dict]:
        """
        Rechercher des clients
        
        Args:
            search_term: Terme de recherche (nom, téléphone, code)
            
        Returns:
            Liste de clients correspondants
        """
        query = """
            SELECT * FROM customers
            WHERE (full_name LIKE ? OR phone LIKE ? OR code LIKE ?)
              AND is_active = 1
            ORDER BY full_name
            LIMIT 50
        """
        search_pattern = f"%{search_term}%"
        results = db.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in results]
    
    def get_all_customers(self, include_inactive: bool = False) -> List[Dict]:
        """
        Obtenir tous les clients
        
        Args:
            include_inactive: Inclure les clients désactivés
            
        Returns:
            Liste de clients
        """
        query = "SELECT * FROM customers"
        
        if not include_inactive:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY full_name"
        
        results = db.execute_query(query)
        return [dict(row) for row in results]
    
    def add_credit(self, customer_id: int, amount: float, 
                  processed_by: int, notes: str = "") -> tuple[bool, str]:
        """
        Ajouter du crédit à un client
        
        Args:
            customer_id: ID du client
            amount: Montant du crédit
            processed_by: ID de l'utilisateur
            notes: Notes
            
        Returns:
            (success, message)
        """
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return False, "Client introuvable"
            
            # Vérifier la limite de crédit
            new_credit = customer['current_credit'] + amount
            if new_credit > customer['credit_limit']:
                return False, f"Limite de crédit dépassée. Limite: {customer['credit_limit']} DA"
            
            db.begin_transaction()
            
            try:
                # Mettre à jour le crédit
                update_query = """
                    UPDATE customers 
                    SET current_credit = current_credit + ?
                    WHERE id = ?
                """
                db.execute_update(update_query, (amount, customer_id))
                
                # Enregistrer la transaction
                transaction_query = """
                    INSERT INTO customer_credit_transactions (
                        customer_id, transaction_type, amount, processed_by, notes
                    ) VALUES (?, 'credit_sale', ?, ?, ?)
                """
                db.execute_insert(transaction_query, (customer_id, amount, processed_by, notes))
                
                db.commit()
                
                logger.info(f"Crédit ajouté: Client {customer_id} - {amount} DA")
                return True, f"Crédit ajouté: {amount} DA"
                
            except Exception as e:
                db.rollback()
                raise e
                
        except Exception as e:
            error_msg = f"Erreur lors de l'ajout du crédit: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def pay_credit(self, customer_id: int, amount: float,
                  processed_by: int, notes: str = "") -> tuple[bool, str]:
        """
        Enregistrer un paiement de crédit
        
        Args:
            customer_id: ID du client
            amount: Montant payé
            processed_by: ID de l'utilisateur
            notes: Notes
            
        Returns:
            (success, message)
        """
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return False, "Client introuvable"
            
            if amount > customer['current_credit']:
                return False, f"Montant trop élevé. Crédit actuel: {customer['current_credit']} DA"
            
            db.begin_transaction()
            
            try:
                # Réduire le crédit
                update_query = """
                    UPDATE customers 
                    SET current_credit = current_credit - ?
                    WHERE id = ?
                """
                db.execute_update(update_query, (amount, customer_id))
                
                # Enregistrer la transaction
                transaction_query = """
                    INSERT INTO customer_credit_transactions (
                        customer_id, transaction_type, amount, processed_by, notes
                    ) VALUES (?, 'payment', ?, ?, ?)
                """
                db.execute_insert(transaction_query, (customer_id, amount, processed_by, notes))
                
                db.commit()
                
                logger.info(f"Paiement crédit: Client {customer_id} - {amount} DA")
                return True, f"Paiement enregistré: {amount} DA"
                
            except Exception as e:
                db.rollback()
                raise e
                
        except Exception as e:
            error_msg = f"Erreur lors du paiement: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_credit_history(self, customer_id: int) -> List[Dict]:
        """
        Obtenir l'historique de crédit d'un client
        
        Args:
            customer_id: ID du client
            
        Returns:
            Liste des transactions
        """
        query = """
            SELECT ct.*, u.full_name as processed_by_name
            FROM customer_credit_transactions ct
            LEFT JOIN users u ON ct.processed_by = u.id
            WHERE ct.customer_id = ?
            ORDER BY ct.transaction_date DESC
        """
        results = db.execute_query(query, (customer_id,))
        return [dict(row) for row in results]
    
    def get_purchase_history(self, customer_id: int, limit: int = 50) -> List[Dict]:
        """
        Obtenir l'historique des achats d'un client
        
        Args:
            customer_id: ID du client
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des ventes
        """
        query = """
            SELECT s.*, u.full_name as cashier_name
            FROM sales s
            LEFT JOIN users u ON s.cashier_id = u.id
            WHERE s.customer_id = ?
            ORDER BY s.sale_date DESC
            LIMIT ?
        """
        results = db.execute_query(query, (customer_id, limit))
        return [dict(row) for row in results]
    
    def get_customers_with_credit(self) -> List[Dict]:
        """
        Obtenir les clients ayant un crédit en cours
        
        Returns:
            Liste de clients
        """
        query = """
            SELECT * FROM customers
            WHERE current_credit > 0 AND is_active = 1
            ORDER BY current_credit DESC
        """
        results = db.execute_query(query)
        return [dict(row) for row in results]
    
    def get_customer_stats(self, customer_id: int) -> Dict[str, Any]:
        """
        Obtenir les statistiques d'un client
        
        Args:
            customer_id: ID du client
            
        Returns:
            Dictionnaire avec les statistiques
        """
        customer = self.get_customer(customer_id)
        if not customer:
            return {}
        
        stats = {
            'total_purchases': customer['total_purchases'],
            'purchase_count': customer['purchase_count'],
            'current_credit': customer['current_credit'],
            'credit_limit': customer['credit_limit'],
            'available_credit': customer['credit_limit'] - customer['current_credit'],
            'last_purchase_date': customer['last_purchase_date'],
        }
        
        # Moyenne par achat
        if customer['purchase_count'] > 0:
            stats['average_purchase'] = round(customer['total_purchases'] / customer['purchase_count'], 2)
        else:
            stats['average_purchase'] = 0.0
        
        return stats
    
    def _generate_customer_code(self) -> str:
        """Générer un code client unique"""
        # Obtenir le dernier code
        query = "SELECT code FROM customers ORDER BY id DESC LIMIT 1"
        result = db.fetch_one(query)
        
        if result and result['code']:
            # Extraire le numéro et incrémenter
            try:
                last_num = int(result['code'].replace('CLT-', ''))
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"CLT-{new_num:06d}"


# Instance globale
customer_manager = CustomerManager()
