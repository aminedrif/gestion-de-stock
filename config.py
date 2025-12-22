# -*- coding: utf-8 -*-
"""
Configuration globale de l'application Mini-Market
"""
import os
from pathlib import Path

# Chemins de base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
RESOURCES_DIR = BASE_DIR / "resources"
BACKUP_DIR = DATA_DIR / "backups"

# Créer les dossiers s'ils n'existent pas
for directory in [DATA_DIR, LOGS_DIR, RESOURCES_DIR, BACKUP_DIR]:
    directory.mkdir(exist_ok=True)

# Base de données
DATABASE_PATH = DATA_DIR / "minimarket.db"

# Paramètres de l'application
APP_NAME = "Gestion Mini-Market"
APP_VERSION = "1.0.0"
COMPANY_NAME = "Votre Mini-Market"

# Paramètres du magasin (modifiables via interface)
STORE_CONFIG = {
    "name": "Mini-Market",
    "address": "123 Rue Principale",
    "city": "Ville",
    "phone": "+213 XX XX XX XX",
    "email": "contact@minimarket.dz",
    "tax_id": "000000000000000",  # NIF
    "currency": "DA",  # Dinar Algérien
    "currency_symbol": "DA",
    "tax_rate": 19.0,  # TVA 19%
}

# Paramètres de sécurité
SECURITY_CONFIG = {
    "max_login_attempts": 3,
    "session_timeout": 3600,  # 1 heure en secondes
    "password_min_length": 6,
    "require_strong_password": False,  # Pour admin uniquement
}

# Paramètres de stock
STOCK_CONFIG = {
    "low_stock_threshold": 10,
    "alert_expiry_days": 30,  # Alerte si expiration dans 30 jours
    "auto_decrease_stock": True,  # Décrémenter automatiquement lors de vente
}

# Paramètres d'impression
PRINTER_CONFIG = {
    "default_printer": "PDF",  # "PDF", "THERMAL", "STANDARD"
    "paper_width_mm": 80,  # Pour imprimantes thermiques
    "auto_print": False,  # Imprimer automatiquement après vente
    "print_copies": 1,
    "thermal_printer_port": "COM1",  # Port série pour imprimante thermique
}

# Paramètres de sauvegarde
BACKUP_CONFIG = {
    "auto_backup": True,
    "backup_time": "23:00",  # Heure de sauvegarde automatique
    "keep_backups_days": 30,  # Garder les sauvegardes pendant 30 jours
    "compress_backups": True,
}

# Paramètres multi-langue
LANGUAGE_CONFIG = {
    "default_language": "fr",  # "fr" ou "ar"
    "available_languages": ["fr", "ar"],
    "rtl_languages": ["ar"],  # Langues RTL
}

# Paramètres de journalisation
LOG_CONFIG = {
    "log_file": LOGS_DIR / "app.log",
    "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "max_log_size_mb": 10,
    "backup_count": 5,  # Nombre de fichiers de log à garder
}

# Paramètres de l'interface
UI_CONFIG = {
    "theme": "light",  # "light" ou "dark"
    "font_family": "Segoe UI",
    "font_size": 10,
    "show_splash_screen": True,
    "window_width": 1280,
    "window_height": 720,
}

# Rôles utilisateurs
USER_ROLES = {
    "ADMIN": "admin",
    "CASHIER": "cashier",
}

# Permissions par rôle
PERMISSIONS = {
    "admin": [
        "manage_products",
        "manage_categories",
        "manage_customers",
        "manage_suppliers",
        "manage_users",
        "view_reports",
        "manage_settings",
        "make_sales",
        "process_returns",
        "manage_backups",
        "view_audit_log",
    ],
    "cashier": [
        "make_sales",
        "view_products",
        "view_customers",
        "process_returns",
    ],
}

# Codes de statut
STATUS_CODES = {
    "ACTIVE": 1,
    "INACTIVE": 0,
    "DELETED": -1,
}

# Types de transactions
TRANSACTION_TYPES = {
    "SALE": "sale",
    "RETURN": "return",
    "ADJUSTMENT": "adjustment",
}

# Méthodes de paiement
PAYMENT_METHODS = {
    "CASH": "cash",
    "CARD": "card",
    "CREDIT": "credit",  # Crédit client
    "MIXED": "mixed",
}

# Messages par défaut
DEFAULT_MESSAGES = {
    "fr": {
        "receipt_header": "Merci pour votre visite !",
        "receipt_footer": "À bientôt !",
        "low_stock_alert": "Stock faible pour le produit : {product_name}",
        "expiry_alert": "Le produit {product_name} expire le {expiry_date}",
    },
    "ar": {
        "receipt_header": "شكرا لزيارتكم!",
        "receipt_footer": "إلى اللقاء!",
        "low_stock_alert": "مخزون منخفض للمنتج: {product_name}",
        "expiry_alert": "المنتج {product_name} ينتهي في {expiry_date}",
    },
}

def get_config(section):
    """Récupérer une section de configuration"""
    configs = {
        "store": STORE_CONFIG,
        "security": SECURITY_CONFIG,
        "stock": STOCK_CONFIG,
        "printer": PRINTER_CONFIG,
        "backup": BACKUP_CONFIG,
        "language": LANGUAGE_CONFIG,
        "log": LOG_CONFIG,
        "ui": UI_CONFIG,
    }
    return configs.get(section, {})

def update_config(section, key, value):
    """Mettre à jour une valeur de configuration"""
    configs = {
        "store": STORE_CONFIG,
        "security": SECURITY_CONFIG,
        "stock": STOCK_CONFIG,
        "printer": PRINTER_CONFIG,
        "backup": BACKUP_CONFIG,
        "language": LANGUAGE_CONFIG,
        "ui": UI_CONFIG,
    }
    if section in configs and key in configs[section]:
        configs[section][key] = value
        return True
    return False
