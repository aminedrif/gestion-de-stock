# -*- coding: utf-8 -*-
"""
Système d'authentification et gestion des sessions
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import config
from database.db_manager import db
from .security import verify_password, hash_password


class AuthManager:
    """Gestionnaire d'authentification et de sessions"""
    
    def __init__(self):
        self.current_user = None
        self.session_start = None
    
    def login(self, username: str, password: str) -> tuple[bool, str, Optional[Dict]]:
        """
        Authentifier un utilisateur
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            
        Returns:
            (success, message, user_data)
        """
        # Récupérer l'utilisateur
        query = """
            SELECT id, username, password_hash, full_name, role, is_active,
                   failed_login_attempts, locked_until
            FROM users 
            WHERE username = ?
        """
        user = db.fetch_one(query, (username,))
        
        if not user:
            return False, "Nom d'utilisateur ou mot de passe incorrect", None
        
        # Vérifier si le compte est actif
        if not user['is_active']:
            return False, "Ce compte est désactivé", None
        
        # VERROUILLAGE DÉSACTIVÉ POUR LE DÉVELOPPEMENT
        # Vérifier si le compte est verrouillé
        # if user['locked_until']:
        #     locked_until = datetime.fromisoformat(user['locked_until'])
        #     if datetime.now() < locked_until:
        #         minutes_left = int((locked_until - datetime.now()).total_seconds() / 60)
        #         return False, f"Compte verrouillé. Réessayez dans {minutes_left} minutes", None
        #     else:
        #         # Déverrouiller le compte
        #         self._unlock_account(user['id'])
        
        # Vérifier le mot de passe
        if not verify_password(password, user['password_hash']):
            # VERROUILLAGE DÉSACTIVÉ
            # Incrémenter les tentatives échouées
            # self._increment_failed_attempts(user['id'])
            # 
            # # Vérifier si on doit verrouiller le compte
            # failed_attempts = user['failed_login_attempts'] + 1
            # max_attempts = config.SECURITY_CONFIG['max_login_attempts']
            # 
            # if failed_attempts >= max_attempts:
            #     self._lock_account(user['id'])
            #     return False, "Trop de tentatives échouées. Compte verrouillé pour 30 minutes", None
            # 
            # remaining = max_attempts - failed_attempts
            # return False, f"Mot de passe incorrect. {remaining} tentative(s) restante(s)", None
            
            return False, "Nom d'utilisateur ou mot de passe incorrect", None
        
        # Connexion réussie
        self._reset_failed_attempts(user['id'])
        self._update_last_login(user['id'])
        
        # Créer la session
        self.current_user = {
            'id': user['id'],
            'username': user['username'],
            'full_name': user['full_name'],
            'role': user['role'],
        }
        self.session_start = datetime.now()
        
        # Enregistrer dans le journal d'audit
        self._log_action('login', user['id'])
        
        return True, "Connexion réussie", self.current_user
    
    def logout(self):
        """Déconnecter l'utilisateur actuel"""
        if self.current_user:
            self._log_action('logout', self.current_user['id'])
            self.current_user = None
            self.session_start = None
    
    def is_authenticated(self) -> bool:
        """Vérifier si un utilisateur est connecté"""
        if not self.current_user or not self.session_start:
            return False
        
        # Vérifier le timeout de session
        timeout = config.SECURITY_CONFIG['session_timeout']
        if (datetime.now() - self.session_start).total_seconds() > timeout:
            self.logout()
            return False
        
        return True
    
    def has_permission(self, permission: str) -> bool:
        """
        Vérifier si l'utilisateur a une permission
        
        Args:
            permission: Nom de la permission
            
        Returns:
            True si l'utilisateur a la permission
        """
        if not self.is_authenticated():
            return False
        
        role = self.current_user['role']
        return permission in config.PERMISSIONS.get(role, [])
    
    def is_admin(self) -> bool:
        """Vérifier si l'utilisateur est admin"""
        return (self.is_authenticated() and 
                self.current_user['role'] == config.USER_ROLES['ADMIN'])
    
    def get_current_user(self) -> Optional[Dict]:
        """Obtenir les données de l'utilisateur actuel"""
        return self.current_user if self.is_authenticated() else None
        
    def get_all_users(self) -> list[Dict]:
        """Obtenir tous les utilisateurs actifs"""
        query = """
            SELECT id, username, full_name, role, is_active, last_login 
            FROM users 
            WHERE is_active = 1 
            ORDER BY username
        """
        results = db.execute_query(query)
        return [dict(row) for row in results]
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> tuple[bool, str]:
        """
        Changer le mot de passe d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            old_password: Ancien mot de passe
            new_password: Nouveau mot de passe
            
        Returns:
            (success, message)
        """
        # Vérifier l'ancien mot de passe
        query = "SELECT password_hash FROM users WHERE id = ?"
        user = db.fetch_one(query, (user_id,))
        
        if not user:
            return False, "Utilisateur introuvable"
        
        if not verify_password(old_password, user['password_hash']):
            return False, "Ancien mot de passe incorrect"
        
        # Vérifier la longueur du nouveau mot de passe
        min_length = config.SECURITY_CONFIG['password_min_length']
        if len(new_password) < min_length:
            return False, f"Le mot de passe doit contenir au moins {min_length} caractères"
        
        # Hacher et enregistrer le nouveau mot de passe
        new_hash = hash_password(new_password)
        update_query = "UPDATE users SET password_hash = ? WHERE id = ?"
        db.execute_update(update_query, (new_hash, user_id))
        
        # Enregistrer dans le journal
        self._log_action('change_password', user_id)
        
        return True, "Mot de passe modifié avec succès"
    
    def create_user(self, username: str, password: str, full_name: str, 
                   role: str, email: str = None, phone: str = None) -> tuple[bool, str, Optional[int]]:
        """
        Créer un nouvel utilisateur
        
        Args:
            username: Nom d'utilisateur
            password: Mot de passe
            full_name: Nom complet
            role: Rôle (admin/cashier)
            email: Email (optionnel)
            phone: Téléphone (optionnel)
            
        Returns:
            (success, message, user_id)
        """
        # Vérifier si l'utilisateur existe déjà
        check_query = "SELECT id, is_active FROM users WHERE username = ?"
        existing = db.fetch_one(check_query, (username,))
        
        # Vérifier la longueur du mot de passe
        min_length = config.SECURITY_CONFIG['password_min_length']
        if len(password) < min_length:
            return False, f"Le mot de passe doit contenir au moins {min_length} caractères", None
        
        # Hacher le mot de passe
        password_hash = hash_password(password)

        if existing:
            user_id, is_active = existing
            if is_active:
                return False, "Ce nom d'utilisateur existe déjà", None
            else:
                # Réactiver l'utilisateur
                update_query = """
                    UPDATE users 
                    SET password_hash = ?, full_name = ?, role = ?, email = ?, phone = ?, is_active = 1
                    WHERE id = ?
                """
                try:
                    db.execute_update(update_query, 
                                     (password_hash, full_name, role, email, phone, user_id))
                    
                    if self.current_user:
                        self._log_action('reactivate_user', self.current_user['id'], 
                                       entity_type='user', entity_id=user_id)
                    
                    return True, "Utilisateur réactivé avec succès", user_id
                except Exception as e:
                    return False, f"Erreur lors de la réactivation: {str(e)}", None
        
        # Vérifier le rôle
        if role not in [config.USER_ROLES['ADMIN'], config.USER_ROLES['CASHIER']]:
            return False, "Rôle invalide", None
        
        # Insérer l'utilisateur
        insert_query = """
            INSERT INTO users (username, password_hash, full_name, role, email, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            user_id = db.execute_insert(insert_query, 
                                       (username, password_hash, full_name, role, email, phone))
            
            # Enregistrer dans le journal
            if self.current_user:
                self._log_action('create_user', self.current_user['id'], 
                               entity_type='user', entity_id=user_id)
            
            return True, "Utilisateur créé avec succès", user_id
            
        except Exception as e:
            return False, f"Erreur lors de la création: {str(e)}", None
    
    def _increment_failed_attempts(self, user_id: int):
        """Incrémenter le compteur de tentatives échouées"""
        query = """
            UPDATE users 
            SET failed_login_attempts = failed_login_attempts + 1
            WHERE id = ?
        """
        db.execute_update(query, (user_id,))
    
    def _reset_failed_attempts(self, user_id: int):
        """Réinitialiser le compteur de tentatives échouées"""
        query = """
            UPDATE users 
            SET failed_login_attempts = 0, locked_until = NULL
            WHERE id = ?
        """
        db.execute_update(query, (user_id,))
    
    def _lock_account(self, user_id: int):
        """Verrouiller un compte pour 30 minutes"""
        locked_until = datetime.now() + timedelta(minutes=30)
        query = """
            UPDATE users 
            SET locked_until = ?
            WHERE id = ?
        """
        db.execute_update(query, (locked_until.isoformat(), user_id))
    
    def _unlock_account(self, user_id: int):
        """Déverrouiller un compte"""
        query = """
            UPDATE users 
            SET locked_until = NULL, failed_login_attempts = 0
            WHERE id = ?
        """
        db.execute_update(query, (user_id,))
    
    def _update_last_login(self, user_id: int):
        """Mettre à jour la date de dernière connexion"""
        query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (user_id,))
    
    def _log_action(self, action: str, user_id: int, entity_type: str = None, entity_id: int = None):
        """Enregistrer une action dans le journal d'audit"""
        query = """
            INSERT INTO audit_log (user_id, action, entity_type, entity_id)
            VALUES (?, ?, ?, ?)
        """
        try:
            db.execute_insert(query, (user_id, action, entity_type, entity_id))
        except Exception as e:
            print(f"Erreur lors de l'enregistrement dans le journal: {e}")


# Instance globale
auth_manager = AuthManager()
