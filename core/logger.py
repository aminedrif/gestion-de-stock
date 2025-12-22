# -*- coding: utf-8 -*-
"""
Système de journalisation (logging)
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
import config


class Logger:
    """Gestionnaire de logs avec rotation"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = logging.getLogger('MiniMarket')
        
        # Créer le dossier de logs s'il n'existe pas
        config.LOGS_DIR.mkdir(exist_ok=True)
        
        # Configuration du logger
        self._setup_logger()
    
    def _setup_logger(self):
        """Configurer le logger avec handlers"""
        # Niveau de log
        log_level = getattr(logging, config.LOG_CONFIG['log_level'], logging.INFO)
        self.logger.setLevel(log_level)
        
        # Éviter les doublons
        if self.logger.handlers:
            return
        
        # Format des logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler fichier avec rotation
        max_bytes = config.LOG_CONFIG['max_log_size_mb'] * 1024 * 1024
        file_handler = RotatingFileHandler(
            config.LOG_CONFIG['log_file'],
            maxBytes=max_bytes,
            backupCount=config.LOG_CONFIG['backup_count'],
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # Handler console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        
        # Ajouter les handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log niveau DEBUG"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log niveau INFO"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log niveau WARNING"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log niveau ERROR"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log niveau CRITICAL"""
        self.logger.critical(message)
    
    def exception(self, message: str):
        """Log une exception avec traceback"""
        self.logger.exception(message)
    
    def log_user_action(self, user_id: int, action: str, details: str = ""):
        """
        Logger une action utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            action: Action effectuée
            details: Détails supplémentaires
        """
        message = f"User {user_id} - {action}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_sale(self, sale_id: int, total: float, cashier_id: int):
        """Logger une vente"""
        self.info(f"Vente #{sale_id} - Total: {total} DA - Caissier: {cashier_id}")
    
    def log_stock_alert(self, product_name: str, quantity: int):
        """Logger une alerte de stock"""
        self.warning(f"ALERTE STOCK - {product_name} - Quantité: {quantity}")
    
    def log_expiry_alert(self, product_name: str, expiry_date: str):
        """Logger une alerte d'expiration"""
        self.warning(f"ALERTE EXPIRATION - {product_name} - Date: {expiry_date}")
    
    def log_database_error(self, operation: str, error: str):
        """Logger une erreur de base de données"""
        self.error(f"Erreur DB - {operation}: {error}")
    
    def log_backup(self, backup_path: str, success: bool):
        """Logger une sauvegarde"""
        if success:
            self.info(f"Sauvegarde réussie: {backup_path}")
        else:
            self.error(f"Échec de la sauvegarde: {backup_path}")


# Instance globale
logger = Logger()
