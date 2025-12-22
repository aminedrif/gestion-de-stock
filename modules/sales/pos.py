# -*- coding: utf-8 -*-
"""
Gestionnaire de point de vente (POS - Point Of Sale)
"""
from typing import Dict, Optional, List
from datetime import datetime
from database.db_manager import db
from core.logger import logger
from modules.products.product_manager import product_manager
from .cart import Cart
import config


class POSManager:
    """Gestionnaire de point de vente"""
    
    def __init__(self):
        self.current_cart = Cart()
        self.register_number = 1  # Numéro de caisse
    
    def set_register_number(self, register_number: int):
        """Définir le numéro de caisse"""
        self.register_number = register_number
    
    def get_cart(self) -> Cart:
        """Obtenir le panier actuel"""
        return self.current_cart
    
    def new_sale(self):
        """Démarrer une nouvelle vente (réinitialiser le panier)"""
        self.current_cart = Cart()
    
    def add_product_by_barcode(self, barcode: str, quantity: float = 1.0) -> tuple[bool, str]:
        """
        Ajouter un produit au panier par code-barres
        
        Args:
            barcode: Code-barres du produit
            quantity: Quantité
            
        Returns:
            (success, message)
        """
        product = product_manager.get_product_by_barcode(barcode)
        
        if not product:
            return False, "Produit introuvable"
        
        return self.current_cart.add_item(product, quantity)
    
    def add_product_by_id(self, product_id: int, quantity: float = 1.0) -> tuple[bool, str]:
        """
        Ajouter un produit au panier par ID
        
        Args:
            product_id: ID du produit
            quantity: Quantité
            
        Returns:
            (success, message)
        """
        product = product_manager.get_product(product_id)
        
        if not product:
            return False, "Produit introuvable"
        
        return self.current_cart.add_item(product, quantity)
    
    def complete_sale(self, cashier_id: int, payment_method: str = 'cash',
                     amount_paid: float = None, customer_id: int = None) -> tuple[bool, str, Optional[int]]:
        """
        Finaliser une vente
        
        Args:
            cashier_id: ID du caissier
            payment_method: Méthode de paiement (cash, card, credit, mixed)
            amount_paid: Montant payé
            customer_id: ID du client (optionnel)
            
        Returns:
            (success, message, sale_id)
        """
        try:
            # Vérifier que le panier n'est pas vide
            if self.current_cart.is_empty():
                return False, "Le panier est vide", None
            
            # Calculer les montants
            subtotal = self.current_cart.get_subtotal()
            discount_amount = self.current_cart.get_discount_amount()
            total_amount = self.current_cart.get_total()
            
            # Vérifier le paiement
            if amount_paid is None:
                amount_paid = total_amount
            
            if payment_method != 'credit' and amount_paid < total_amount:
                return False, f"Montant insuffisant. Total: {total_amount} DA", None
            
            change_amount = max(0, amount_paid - total_amount)
            
            # Générer le numéro de vente
            sale_number = self._generate_sale_number()
            
            # Démarrer une transaction
            db.begin_transaction()
            
            try:
                # Insérer la vente
                sale_query = """
                    INSERT INTO sales (
                        sale_number, customer_id, cashier_id, subtotal,
                        discount_amount, total_amount, payment_method,
                        amount_paid, change_amount, register_number
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                sale_id = db.execute_insert(sale_query, (
                    sale_number, customer_id, cashier_id, subtotal,
                    discount_amount, total_amount, payment_method,
                    amount_paid, change_amount, self.register_number
                ))
                
                # Insérer les articles de la vente
                item_query = """
                    INSERT INTO sale_items (
                        sale_id, product_id, product_name, barcode,
                        quantity, unit_price, discount_percentage,
                        subtotal, purchase_price
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                for item in self.current_cart.items:
                    db.execute_insert(item_query, (
                        sale_id, item.product_id, item.product_name, item.barcode,
                        item.quantity, item.unit_price, item.discount_percentage,
                        item.get_subtotal(), item.purchase_price
                    ))
                    
                    # Décrémenter le stock si configuré
                    if config.STOCK_CONFIG['auto_decrease_stock']:
                        product_manager.decrease_stock(item.product_id, item.quantity)
                
                # Si paiement à crédit, mettre à jour le crédit client
                if payment_method == 'credit' and customer_id:
                    self._update_customer_credit(customer_id, total_amount, sale_id)
                
                # Mettre à jour les statistiques client
                if customer_id:
                    self._update_customer_stats(customer_id, total_amount)
                
                # Valider la transaction
                db.commit()
                
                logger.log_sale(sale_id, total_amount, cashier_id)
                
                # Réinitialiser le panier
                self.new_sale()
                
                return True, f"Vente enregistrée: {sale_number}", sale_id
                
            except Exception as e:
                db.rollback()
                raise e
                
        except Exception as e:
            error_msg = f"Erreur lors de la finalisation de la vente: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def cancel_sale(self, sale_id: int, reason: str = "") -> tuple[bool, str]:
        """
        Annuler une vente
        
        Args:
            sale_id: ID de la vente
            reason: Raison de l'annulation
            
        Returns:
            (success, message)
        """
        try:
            # Vérifier que la vente existe
            sale_query = "SELECT * FROM sales WHERE id = ?"
            sale = db.fetch_one(sale_query, (sale_id,))
            
            if not sale:
                return False, "Vente introuvable"
            
            if sale['status'] != 'completed':
                return False, "Cette vente est déjà annulée ou retournée"
            
            db.begin_transaction()
            
            try:
                # Marquer la vente comme annulée
                update_query = "UPDATE sales SET status = 'cancelled' WHERE id = ?"
                db.execute_update(update_query, (sale_id,))
                
                # Restaurer le stock
                items_query = "SELECT product_id, quantity FROM sale_items WHERE sale_id = ?"
                items = db.execute_query(items_query, (sale_id,))
                
                for item in items:
                    product_manager.increase_stock(item['product_id'], item['quantity'])
                
                # Si c'était un paiement à crédit, ajuster le crédit client
                if sale['payment_method'] == 'credit' and sale['customer_id']:
                    credit_query = """
                        UPDATE customers 
                        SET current_credit = current_credit - ?
                        WHERE id = ?
                    """
                    db.execute_update(credit_query, (sale['total_amount'], sale['customer_id']))
                
                db.commit()
                
                logger.info(f"Vente annulée: {sale['sale_number']} - Raison: {reason}")
                return True, "Vente annulée avec succès"
                
            except Exception as e:
                db.rollback()
                raise e
                
        except Exception as e:
            error_msg = f"Erreur lors de l'annulation: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def process_return(self, sale_id: int, items_to_return: List[Dict],
                      processed_by: int, reason: str = "") -> tuple[bool, str, Optional[int]]:
        """
        Traiter un retour de produits
        
        Args:
            sale_id: ID de la vente originale
            items_to_return: Liste des articles à retourner [{product_id, quantity}]
            processed_by: ID de l'utilisateur qui traite le retour
            reason: Raison du retour
            
        Returns:
            (success, message, return_id)
        """
        try:
            # Vérifier la vente
            sale_query = "SELECT * FROM sales WHERE id = ?"
            sale = db.fetch_one(sale_query, (sale_id,))
            
            if not sale:
                return False, "Vente introuvable", None
            
            db.begin_transaction()
            
            try:
                # Calculer le montant du retour
                return_amount = 0.0
                
                # Générer le numéro de retour
                return_number = self._generate_return_number()
                
                # Créer l'enregistrement de retour
                return_query = """
                    INSERT INTO returns (
                        return_number, original_sale_id, return_amount,
                        refund_method, processed_by, reason
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """
                
                return_id = db.execute_insert(return_query, (
                    return_number, sale_id, 0.0,  # Montant mis à jour après
                    sale['payment_method'], processed_by, reason
                ))
                
                # Traiter chaque article retourné
                for item_data in items_to_return:
                    product_id = item_data['product_id']
                    quantity = item_data['quantity']
                    
                    # Obtenir l'article de vente original
                    item_query = """
                        SELECT * FROM sale_items 
                        WHERE sale_id = ? AND product_id = ?
                    """
                    sale_item = db.fetch_one(item_query, (sale_id, product_id))
                    
                    if not sale_item:
                        raise Exception(f"Article introuvable dans la vente: {product_id}")
                    
                    if quantity > sale_item['quantity']:
                        raise Exception(f"Quantité de retour invalide pour le produit {product_id}")
                    
                    # Calculer le montant du retour pour cet article
                    unit_price = sale_item['unit_price'] * (1 - sale_item['discount_percentage'] / 100.0)
                    item_return_amount = unit_price * quantity
                    return_amount += item_return_amount
                    
                    # Insérer l'article de retour
                    return_item_query = """
                        INSERT INTO return_items (
                            return_id, sale_item_id, product_id,
                            quantity_returned, unit_price, subtotal
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """
                    db.execute_insert(return_item_query, (
                        return_id, sale_item['id'], product_id,
                        quantity, unit_price, item_return_amount
                    ))
                    
                    # Restaurer le stock
                    product_manager.increase_stock(product_id, quantity)
                
                # Mettre à jour le montant du retour
                update_return_query = "UPDATE returns SET return_amount = ? WHERE id = ?"
                db.execute_update(update_return_query, (return_amount, return_id))
                
                # Ajuster le crédit client si nécessaire
                if sale['payment_method'] == 'credit' and sale['customer_id']:
                    credit_query = """
                        UPDATE customers 
                        SET current_credit = current_credit - ?
                        WHERE id = ?
                    """
                    db.execute_update(credit_query, (return_amount, sale['customer_id']))
                
                db.commit()
                
                logger.info(f"Retour traité: {return_number} - Montant: {return_amount} DA")
                return True, f"Retour enregistré: {return_number}", return_id
                
            except Exception as e:
                db.rollback()
                raise e
                
        except Exception as e:
            error_msg = f"Erreur lors du traitement du retour: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def get_sale(self, sale_id: int) -> Optional[Dict]:
        """
        Obtenir les détails d'une vente
        
        Args:
            sale_id: ID de la vente
            
        Returns:
            Dictionnaire avec les détails de la vente
        """
        sale_query = """
            SELECT s.*, u.full_name as cashier_name, c.full_name as customer_name
            FROM sales s
            LEFT JOIN users u ON s.cashier_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE s.id = ?
        """
        sale = db.fetch_one(sale_query, (sale_id,))
        
        if not sale:
            return None
        
        # Obtenir les articles
        items_query = "SELECT * FROM sale_items WHERE sale_id = ?"
        items = db.execute_query(items_query, (sale_id,))
        
        result = dict(sale)
        result['items'] = [dict(item) for item in items]
        
        return result
    
    def _generate_sale_number(self) -> str:
        """Générer un numéro de vente unique"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"VNT-{timestamp}-{self.register_number}"
    
    def _generate_return_number(self) -> str:
        """Générer un numéro de retour unique"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"RET-{timestamp}"
    
    def _update_customer_credit(self, customer_id: int, amount: float, sale_id: int):
        """Mettre à jour le crédit d'un client"""
        # Augmenter le crédit actuel
        update_query = """
            UPDATE customers 
            SET current_credit = current_credit + ?
            WHERE id = ?
        """
        db.execute_update(update_query, (amount, customer_id))
        
        # Enregistrer la transaction de crédit
        transaction_query = """
            INSERT INTO customer_credit_transactions (
                customer_id, transaction_type, amount, sale_id, processed_by
            ) VALUES (?, 'credit_sale', ?, ?, ?)
        """
        # Note: processed_by devrait être le cashier_id, mais on ne l'a pas ici
        db.execute_insert(transaction_query, (customer_id, amount, sale_id, 1))
    
    def _update_customer_stats(self, customer_id: int, amount: float):
        """Mettre à jour les statistiques d'un client"""
        update_query = """
            UPDATE customers 
            SET total_purchases = total_purchases + ?,
                purchase_count = purchase_count + 1,
                last_purchase_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        db.execute_update(update_query, (amount, customer_id))


# Instance globale
pos_manager = POSManager()
