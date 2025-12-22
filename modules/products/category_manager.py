# -*- coding: utf-8 -*-
"""
Gestionnaire de catégories de produits
"""
from typing import List, Optional, Dict, Any
from database.db_manager import db
from core.logger import logger


class CategoryManager:
    """Gestionnaire de catégories"""
    
    def create_category(self, name: str, name_ar: str = None, 
                       description: str = None, parent_id: int = None) -> tuple[bool, str, Optional[int]]:
        """
        Créer une nouvelle catégorie
        
        Args:
            name: Nom de la catégorie
            name_ar: Nom en arabe
            description: Description
            parent_id: ID de la catégorie parente (pour sous-catégories)
            
        Returns:
            (success, message, category_id)
        """
        try:
            # Vérifier si la catégorie existe déjà
            check_query = "SELECT id FROM categories WHERE name = ?"
            existing = db.fetch_one(check_query, (name,))
            
            if existing:
                return False, "Cette catégorie existe déjà", None
            
            # Insérer la catégorie
            insert_query = """
                INSERT INTO categories (name, name_ar, description, parent_id)
                VALUES (?, ?, ?, ?)
            """
            category_id = db.execute_insert(insert_query, (name, name_ar, description, parent_id))
            
            logger.info(f"Catégorie créée: {name} (ID: {category_id})")
            return True, "Catégorie créée avec succès", category_id
            
        except Exception as e:
            error_msg = f"Erreur lors de la création de la catégorie: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def update_category(self, category_id: int, name: str = None, 
                       name_ar: str = None, description: str = None) -> tuple[bool, str]:
        """
        Mettre à jour une catégorie
        
        Args:
            category_id: ID de la catégorie
            name: Nouveau nom
            name_ar: Nouveau nom en arabe
            description: Nouvelle description
            
        Returns:
            (success, message)
        """
        try:
            # Construire la requête dynamiquement
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            
            if name_ar is not None:
                updates.append("name_ar = ?")
                params.append(name_ar)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if not updates:
                return False, "Aucune modification à effectuer"
            
            params.append(category_id)
            
            query = f"UPDATE categories SET {', '.join(updates)} WHERE id = ?"
            rows_affected = db.execute_update(query, tuple(params))
            
            if rows_affected > 0:
                logger.info(f"Catégorie mise à jour: ID {category_id}")
                return True, "Catégorie mise à jour avec succès"
            else:
                return False, "Catégorie introuvable"
                
        except Exception as e:
            error_msg = f"Erreur lors de la mise à jour: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def delete_category(self, category_id: int) -> tuple[bool, str]:
        """
        Supprimer une catégorie (soft delete)
        
        Args:
            category_id: ID de la catégorie
            
        Returns:
            (success, message)
        """
        try:
            # Vérifier si des produits utilisent cette catégorie
            check_query = "SELECT COUNT(*) as count FROM products WHERE category_id = ? AND is_active = 1"
            result = db.fetch_one(check_query, (category_id,))
            
            if result and result['count'] > 0:
                return False, f"Impossible de supprimer: {result['count']} produit(s) utilisent cette catégorie"
            
            # Désactiver la catégorie
            query = "UPDATE categories SET is_active = 0 WHERE id = ?"
            rows_affected = db.execute_update(query, (category_id,))
            
            if rows_affected > 0:
                logger.info(f"Catégorie supprimée: ID {category_id}")
                return True, "Catégorie supprimée avec succès"
            else:
                return False, "Catégorie introuvable"
                
        except Exception as e:
            error_msg = f"Erreur lors de la suppression: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_category(self, category_id: int) -> Optional[Dict]:
        """
        Obtenir une catégorie par son ID
        
        Args:
            category_id: ID de la catégorie
            
        Returns:
            Dictionnaire avec les données de la catégorie ou None
        """
        query = """
            SELECT id, name, name_ar, description, parent_id, is_active,
                   created_at, updated_at
            FROM categories
            WHERE id = ?
        """
        result = db.fetch_one(query, (category_id,))
        return dict(result) if result else None
    
    def get_all_categories(self, include_inactive: bool = False) -> List[Dict]:
        """
        Obtenir toutes les catégories
        
        Args:
            include_inactive: Inclure les catégories désactivées
            
        Returns:
            Liste de dictionnaires
        """
        query = """
            SELECT id, name, name_ar, description, parent_id, is_active,
                   created_at, updated_at
            FROM categories
        """
        
        if not include_inactive:
            query += " WHERE is_active = 1"
        
        query += " ORDER BY name"
        
        results = db.execute_query(query)
        return [dict(row) for row in results]
    
    def search_categories(self, search_term: str) -> List[Dict]:
        """
        Rechercher des catégories
        
        Args:
            search_term: Terme de recherche
            
        Returns:
            Liste de catégories correspondantes
        """
        query = """
            SELECT id, name, name_ar, description, parent_id, is_active
            FROM categories
            WHERE (name LIKE ? OR name_ar LIKE ? OR description LIKE ?)
              AND is_active = 1
            ORDER BY name
        """
        search_pattern = f"%{search_term}%"
        results = db.execute_query(query, (search_pattern, search_pattern, search_pattern))
        return [dict(row) for row in results]
    
    def get_category_product_count(self, category_id: int) -> int:
        """
        Obtenir le nombre de produits dans une catégorie
        
        Args:
            category_id: ID de la catégorie
            
        Returns:
            Nombre de produits
        """
        query = "SELECT COUNT(*) as count FROM products WHERE category_id = ? AND is_active = 1"
        result = db.fetch_one(query, (category_id,))
        return result['count'] if result else 0


# Instance globale
category_manager = CategoryManager()
