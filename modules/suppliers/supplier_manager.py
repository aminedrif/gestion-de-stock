# -*- coding: utf-8 -*-
"""
Gestionnaire de fournisseurs
"""
from typing import List, Optional, Dict, Any
from database.db_manager import db
from core.logger import logger


class SupplierManager:
    """Gestionnaire de fournisseurs"""
    
    def create_supplier(self, company_name: str, contact_person: str = None,
                       phone: str = None, email: str = None, 
                       address: str = None) -> tuple[bool, str, Optional[int]]:
        """
        Créer un nouveau fournisseur
        
        Args:
            company_name: Nom de l'entreprise
            contact_person: Personne de contact
            phone: Téléphone
            email: Email
            address: Adresse
            
        Returns:
            (success, message, supplier_id)
        """
        try:
            # Vérifier si le fournisseur existe déjà (par nom)
            check_query = "SELECT id, is_active, code FROM suppliers WHERE company_name = ?"
            existing = db.fetch_one(check_query, (company_name,))
            
            if existing:
                supplier_id, is_active, existing_code = existing
                if is_active:
                    return False, f"Un fournisseur avec ce nom existe déjà (Code: {existing_code})", None
                else:
                    # Réactiver le fournisseur
                    update_query = """
                        UPDATE suppliers 
                        SET contact_person = ?, phone = ?, email = ?, address = ?, is_active = 1
                        WHERE id = ?
                    """
                    db.execute_update(update_query, (contact_person, phone, email, address, supplier_id))
                    logger.info(f"Fournisseur réactivé: {company_name} (Code: {existing_code})")
                    return True, f"Fournisseur réactivé avec succès (Code: {existing_code})", supplier_id

            # Générer un code fournisseur unique
            code = self._generate_supplier_code()
            
            # Insérer le fournisseur
            insert_query = """
                INSERT INTO suppliers (code, company_name, contact_person, phone, email, address)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            supplier_id = db.execute_insert(insert_query, (
                code, company_name, contact_person, phone, email, address
            ))
            
            logger.info(f"Fournisseur créé: {company_name} (Code: {code})")
            return True, f"Fournisseur créé avec succès (Code: {code})", supplier_id
            
        except Exception as e:
            error_msg = f"Erreur lors de la création du fournisseur: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def update_supplier(self, supplier_id: int, **kwargs) -> tuple[bool, str]:
        """
        Mettre à jour un fournisseur
        
        Args:
            supplier_id: ID du fournisseur
            **kwargs: Champs à mettre à jour
            
        Returns:
            (success, message)
        """
        try:
            allowed_fields = ['company_name', 'contact_person', 'phone', 'email', 'address', 'notes']
            
            updates = []
            params = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    updates.append(f"{field} = ?")
                    params.append(value)
            
            if not updates:
                return False, "Aucune modification à effectuer"
            
            params.append(supplier_id)
            
            query = f"UPDATE suppliers SET {', '.join(updates)} WHERE id = ?"
            rows_affected = db.execute_update(query, tuple(params))
            
            if rows_affected > 0:
                logger.info(f"Fournisseur mis à jour: ID {supplier_id}")
                return True, "Fournisseur mis à jour avec succès"
            else:
                return False, "Fournisseur introuvable"
                
        except Exception as e:
            error_msg = f"Erreur lors de la mise à jour: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_supplier(self, supplier_id: int) -> tuple[bool, str]:
        """
        Supprimer un fournisseur (soft delete)
        
        Args:
            supplier_id: ID du fournisseur
            
        Returns:
            (success, message)
        """
        try:
            # Vérifier s'il a des dettes
            supplier = self.get_supplier(supplier_id)
            if supplier:
                try:
                    total_debt = float(supplier.get('total_debt', 0))
                except (ValueError, TypeError):
                    total_debt = 0.0
                    
                if total_debt > 0:
                    return False, f"Impossible de supprimer: dette en cours de {total_debt:.2f} DA"
            
            # Vérifier s'il a des produits associés
            check_query = "SELECT COUNT(*) as count FROM products WHERE supplier_id = ? AND is_active = 1"
            result = db.fetch_one(check_query, (supplier_id,))
            
            if result and result['count'] > 0:
                return False, f"Impossible de supprimer: {result['count']} produit(s) associé(s)"
            
            query = "UPDATE suppliers SET is_active = 0 WHERE id = ?"
            rows_affected = db.execute_update(query, (supplier_id,))
            
            if rows_affected > 0:
                logger.info(f"Fournisseur supprimé: ID {supplier_id}")
                return True, "Fournisseur supprimé avec succès"
            else:
                return False, "Fournisseur introuvable"
                
        except Exception as e:
            error_msg = f"Erreur lors de la suppression: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_supplier(self, supplier_id: int) -> Optional[Dict]:
        """
        Obtenir un fournisseur par son ID
        
        Args:
            supplier_id: ID du fournisseur
            
        Returns:
            Dictionnaire avec les données du fournisseur ou None
        """
        query = "SELECT * FROM suppliers WHERE id = ?"
        result = db.fetch_one(query, (supplier_id,))
        return dict(result) if result else None
    
    def get_supplier_by_code(self, code: str) -> Optional[Dict]:
        """
        Obtenir un fournisseur par son code
        
        Args:
            code: Code fournisseur
            
        Returns:
            Dictionnaire avec les données du fournisseur ou None
        """
        query = "SELECT * FROM suppliers WHERE code = ? AND is_active = 1"
        result = db.fetch_one(query, (code,))
        return dict(result) if result else None
    
    def search_suppliers(self, search_term: str) -> List[Dict]:
        """
        Rechercher des fournisseurs
        
        Args:
            search_term: Terme de recherche (nom, téléphone, code)
            
        Returns:
            Liste de fournisseurs correspondants
        """
        query = """
            SELECT * FROM suppliers
            WHERE (company_name LIKE ? OR phone LIKE ? OR code LIKE ?)
              AND is_active = 1
            ORDER BY company_name
            LIMIT 50
        """
        search_pattern = f"%{search_term}%"
        results = db.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in results]
    
    def get_all_suppliers(self, include_inactive: bool = False) -> List[Dict]:
        """
        Obtenir tous les fournisseurs
        
        Args:
            include_inactive: Inclure les fournisseurs désactivés
            
        Returns:
            Liste de fournisseurs
        """
        query = "SELECT * FROM suppliers"
        
        if not include_inactive:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY company_name"
        
        results = db.execute_query(query)
        return [dict(row) for row in results]
    
    def add_purchase(self, supplier_id: int, purchase_amount: float, debt_amount: float,
                    processed_by: int, description: str = "") -> tuple[bool, str]:
        """
        Enregistrer un achat chez un fournisseur
        
        Args:
            supplier_id: ID du fournisseur
            purchase_amount: Montant total de l'achat
            debt_amount: Montant de la dette à ajouter
            processed_by: ID de l'utilisateur
            description: Description
            
        Returns:
            (success, message)
        """
        try:
            supplier = self.get_supplier(supplier_id)
            if not supplier:
                return False, "Fournisseur introuvable"
            
            db.begin_transaction()
            
            try:
                # Mettre à jour total_purchases et total_debt
                update_query = """
                    UPDATE suppliers 
                    SET total_purchases = total_purchases + ?,
                        total_debt = total_debt + ?
                    WHERE id = ?
                """
                db.execute_update(update_query, (purchase_amount, debt_amount, supplier_id))
                
                # Enregistrer la transaction d'achat
                if purchase_amount > 0:
                    transaction_query = """
                        INSERT INTO supplier_transactions (
                            supplier_id, transaction_type, amount, description, processed_by
                        ) VALUES (?, 'purchase', ?, ?, ?)
                    """
                    db.execute_insert(transaction_query, (supplier_id, purchase_amount, description, processed_by))
                
                db.commit()
                
                logger.info(f"Achat enregistré: Fournisseur {supplier_id} - Achat: {purchase_amount} DA, Dette: {debt_amount} DA")
                return True, f"Achat enregistré: {purchase_amount} DA (Dette ajoutée: {debt_amount} DA)"
                
            except Exception as e:
                db.rollback()
                raise e
                
        except Exception as e:
            error_msg = f"Erreur lors de l'enregistrement de l'achat: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def pay_debt(self, supplier_id: int, amount: float,
                processed_by: int, description: str = "") -> tuple[bool, str]:
        """
        Enregistrer un paiement (réduit la dette)
        
        Args:
            supplier_id: ID du fournisseur
            amount: Montant payé
            processed_by: ID de l'utilisateur
            description: Description
            
        Returns:
            (success, message)
        """
        try:
            supplier = self.get_supplier(supplier_id)
            if not supplier:
                return False, "Fournisseur introuvable"
            
            if amount > supplier['total_debt']:
                return False, f"Montant trop élevé. Dette actuelle: {supplier['total_debt']} DA"
            
            db.begin_transaction()
            
            try:
                # Réduire la dette
                update_query = """
                    UPDATE suppliers 
                    SET total_debt = total_debt - ?
                    WHERE id = ?
                """
                db.execute_update(update_query, (amount, supplier_id))
                
                # Enregistrer la transaction
                transaction_query = """
                    INSERT INTO supplier_transactions (
                        supplier_id, transaction_type, amount, description, processed_by
                    ) VALUES (?, 'payment', ?, ?, ?)
                """
                db.execute_insert(transaction_query, (supplier_id, amount, description, processed_by))
                
                db.commit()
                
                logger.info(f"Paiement fournisseur: Fournisseur {supplier_id} - {amount} DA")
                return True, f"Paiement enregistré: {amount} DA"
                
            except Exception as e:
                db.rollback()
                raise e
                
        except Exception as e:
            error_msg = f"Erreur lors du paiement: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_transaction_history(self, supplier_id: int) -> List[Dict]:
        """
        Obtenir l'historique des transactions d'un fournisseur
        
        Args:
            supplier_id: ID du fournisseur
            
        Returns:
            Liste des transactions
        """
        query = """
            SELECT st.*, u.full_name as processed_by_name
            FROM supplier_transactions st
            LEFT JOIN users u ON st.processed_by = u.id
            WHERE st.supplier_id = ?
            ORDER BY st.transaction_date DESC
        """
        results = db.execute_query(query, (supplier_id,))
        return [dict(row) for row in results]
    
    def get_suppliers_with_debt(self) -> List[Dict]:
        """
        Obtenir les fournisseurs ayant une dette
        
        Returns:
            Liste de fournisseurs
        """
        query = """
            SELECT * FROM suppliers
            WHERE total_debt > 0 AND is_active = 1
            ORDER BY total_debt DESC
        """
        results = db.execute_query(query)
        return [dict(row) for row in results]
    
    def get_supplier_products(self, supplier_id: int) -> List[Dict]:
        """
        Obtenir les produits d'un fournisseur
        
        Args:
            supplier_id: ID du fournisseur
            
        Returns:
            Liste de produits
        """
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.supplier_id = ? AND p.is_active = 1
            ORDER BY p.name
        """
        results = db.execute_query(query, (supplier_id,))
        return [dict(row) for row in results]
    
    def _generate_supplier_code(self) -> str:
        """Générer un code fournisseur unique"""
        # Obtenir le dernier code
        query = "SELECT code FROM suppliers ORDER BY id DESC LIMIT 1"
        result = db.fetch_one(query)
        
        if result and result['code']:
            # Extraire le numéro et incrémenter
            try:
                last_num = int(result['code'].replace('FRN-', ''))
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"FRN-{new_num:06d}"


# Instance globale
supplier_manager = SupplierManager()
