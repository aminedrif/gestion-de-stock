# -*- coding: utf-8 -*-
"""
Application de Gestion de Mini-Market
Point d'entrée principal
"""
import sys
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

import config
from core.logger import logger
from database.db_manager import db


def initialize_application():
    """Initialiser l'application"""
    try:
        logger.info("=" * 60)
        logger.info(f"Démarrage de {config.APP_NAME} v{config.APP_VERSION}")
        logger.info("=" * 60)
        
        # Vérifier la base de données
        logger.info("Vérification de la base de données...")
        db_info = db.get_database_info()
        logger.info(f"Base de données: {db_info['path']}")
        logger.info(f"Taille: {db_info['size_bytes'] / 1024:.2f} KB")
        logger.info(f"Tables: {len(db_info['tables'])}")
        
        # Afficher les compteurs de tables
        for table, count in db_info['table_counts'].items():
            logger.info(f"  - {table}: {count} enregistrement(s)")
        
        logger.info("Application initialisée avec succès")
        return True
        
    except Exception as e:
        logger.critical(f"Erreur lors de l'initialisation: {e}")
        logger.exception("Détails de l'erreur:")
        return False


def main():
    """Fonction principale"""
    # Initialiser l'application
    if not initialize_application():
        print("Erreur lors de l'initialisation de l'application")
        sys.exit(1)
    
    # TODO: Lancer l'interface graphique PyQt5
    # Pour l'instant, on affiche juste un message
    print("\n" + "=" * 60)
    print(f"  {config.APP_NAME} v{config.APP_VERSION}")
    print("=" * 60)
    print("\n✓ Application initialisée avec succès!")
    print(f"✓ Base de données: {config.DATABASE_PATH}")
    print(f"✓ Logs: {config.LOG_CONFIG['log_file']}")
    print("\n" + "=" * 60)
    print("\nINFO: Interface graphique PyQt5 à implémenter")
    print("Pour tester les modules, utilisez test_modules.py")
    print("=" * 60)
    
    # Garder la fenêtre ouverte
    input("\nAppuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()
