# -*- coding: utf-8 -*-
"""
Gestionnaire de base de données SQLite
Singleton pattern pour une seule instance de connexion
"""
import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import config


class DatabaseManager:
    """Gestionnaire singleton de la base de données SQLite"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implémentation du pattern Singleton"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialiser la connexion à la base de données"""
        if self._initialized:
            return
            
        self.db_path = config.DATABASE_PATH
        self.connection = None
        self._local = threading.local()
        self._initialized = True
        
        # Initialiser la base de données
        self.initialize_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Obtenir une connexion thread-safe à la base de données
        Chaque thread a sa propre connexion
        """
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=10.0
            )
            # Activer les clés étrangères
            self._local.connection.execute("PRAGMA foreign_keys = ON")
            # Retourner les résultats comme dictionnaires
            self._local.connection.row_factory = sqlite3.Row
            
        return self._local.connection
    
    def initialize_database(self):
        """Initialiser la base de données avec le schéma"""
        # Créer le dossier data s'il n'existe pas
        config.DATA_DIR.mkdir(exist_ok=True)
        
        # Lire le schéma SQL
        schema_path = Path(__file__).parent / "schema.sql"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Fichier de schéma introuvable: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        # Exécuter le schéma
        conn = self.get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
            print("✓ Base de données initialisée avec succès")
        except sqlite3.Error as e:
            print(f"✗ Erreur lors de l'initialisation de la base de données: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """
        Exécuter une requête SELECT et retourner les résultats
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            Liste des résultats
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'exécution de la requête: {e}")
            print(f"Requête: {query}")
            print(f"Paramètres: {params}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Exécuter une requête INSERT, UPDATE ou DELETE
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            Nombre de lignes affectées
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Erreur lors de l'exécution de la mise à jour: {e}")
            print(f"Requête: {query}")
            print(f"Paramètres: {params}")
            raise
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """
        Exécuter une requête INSERT et retourner l'ID inséré
        
        Args:
            query: Requête SQL INSERT
            params: Paramètres de la requête
            
        Returns:
            ID de la ligne insérée
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Erreur lors de l'insertion: {e}")
            print(f"Requête: {query}")
            print(f"Paramètres: {params}")
            raise
    
    def execute_many(self, query: str, params_list: List[tuple]) -> int:
        """
        Exécuter plusieurs requêtes INSERT/UPDATE en une transaction
        
        Args:
            query: Requête SQL
            params_list: Liste de tuples de paramètres
            
        Returns:
            Nombre total de lignes affectées
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Erreur lors de l'exécution multiple: {e}")
            raise
    
    def begin_transaction(self):
        """Démarrer une transaction explicite"""
        conn = self.get_connection()
        conn.execute("BEGIN TRANSACTION")
    
    def commit(self):
        """Valider la transaction en cours"""
        conn = self.get_connection()
        conn.commit()
    
    def rollback(self):
        """Annuler la transaction en cours"""
        conn = self.get_connection()
        conn.rollback()
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """
        Exécuter une requête et retourner une seule ligne
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
            
        Returns:
            Une ligne ou None
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Erreur lors de la récupération: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """
        Vérifier si une table existe
        
        Args:
            table_name: Nom de la table
            
        Returns:
            True si la table existe
        """
        query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        """
        result = self.fetch_one(query, (table_name,))
        return result is not None
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Obtenir la liste des colonnes d'une table
        
        Args:
            table_name: Nom de la table
            
        Returns:
            Liste des noms de colonnes
        """
        query = f"PRAGMA table_info({table_name})"
        results = self.execute_query(query)
        return [row['name'] for row in results]
    
    def close(self):
        """Fermer la connexion à la base de données"""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
    
    def vacuum(self):
        """Optimiser la base de données (récupérer l'espace)"""
        conn = self.get_connection()
        conn.execute("VACUUM")
        conn.commit()
    
    def get_database_size(self) -> int:
        """
        Obtenir la taille de la base de données en octets
        
        Returns:
            Taille en octets
        """
        if self.db_path.exists():
            return self.db_path.stat().st_size
        return 0
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Obtenir des informations sur la base de données
        
        Returns:
            Dictionnaire avec les informations
        """
        conn = self.get_connection()
        
        # Obtenir la liste des tables
        tables_query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        tables = [row['name'] for row in self.execute_query(tables_query)]
        
        # Compter les enregistrements par table
        table_counts = {}
        for table in tables:
            count_query = f"SELECT COUNT(*) as count FROM {table}"
            result = self.fetch_one(count_query)
            table_counts[table] = result['count'] if result else 0
        
        return {
            'path': str(self.db_path),
            'size_bytes': self.get_database_size(),
            'tables': tables,
            'table_counts': table_counts,
        }
    
    def backup_database(self, backup_path: Path) -> bool:
        """
        Créer une sauvegarde de la base de données
        
        Args:
            backup_path: Chemin de la sauvegarde
            
        Returns:
            True si succès
        """
        try:
            import shutil
            
            # Créer le dossier de sauvegarde s'il n'existe pas
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copier la base de données
            shutil.copy2(self.db_path, backup_path)
            
            print(f"✓ Sauvegarde créée: {backup_path}")
            return True
            
        except Exception as e:
            print(f"✗ Erreur lors de la sauvegarde: {e}")
            return False
    
    def restore_database(self, backup_path: Path) -> bool:
        """
        Restaurer la base de données depuis une sauvegarde
        
        Args:
            backup_path: Chemin de la sauvegarde
            
        Returns:
            True si succès
        """
        try:
            import shutil
            
            if not backup_path.exists():
                print(f"✗ Fichier de sauvegarde introuvable: {backup_path}")
                return False
            
            # Fermer la connexion actuelle
            self.close()
            
            # Restaurer la base de données
            shutil.copy2(backup_path, self.db_path)
            
            # Réinitialiser la connexion
            self._local.connection = None
            
            print(f"✓ Base de données restaurée depuis: {backup_path}")
            return True
            
        except Exception as e:
            print(f"✗ Erreur lors de la restauration: {e}")
            return False


# Instance globale
db = DatabaseManager()
