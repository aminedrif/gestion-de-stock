# -*- coding: utf-8 -*-
"""
Système de sauvegarde automatique et manuelle
"""
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import config
from database.db_manager import db
from .logger import logger


class BackupManager:
    """Gestionnaire de sauvegardes"""
    
    def __init__(self):
        self.backup_dir = config.BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, destination: Optional[Path] = None, 
                     compress: bool = True) -> tuple[bool, str, Optional[Path]]:
        """
        Créer une sauvegarde de la base de données
        
        Args:
            destination: Dossier de destination (None = dossier par défaut)
            compress: Compresser en ZIP
            
        Returns:
            (success, message, backup_path)
        """
        try:
            # Générer le nom du fichier de sauvegarde
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"minimarket_backup_{timestamp}"
            
            # Déterminer le dossier de destination
            if destination is None:
                destination = self.backup_dir
            else:
                destination = Path(destination)
                destination.mkdir(parents=True, exist_ok=True)
            
            # Copier la base de données
            db_backup_path = destination / f"{backup_name}.db"
            
            # Utiliser la méthode de backup de SQLite pour éviter les corruptions
            success = db.backup_database(db_backup_path)
            
            if not success:
                return False, "Erreur lors de la copie de la base de données", None
            
            # Compresser si demandé
            if compress:
                zip_path = destination / f"{backup_name}.zip"
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(db_backup_path, db_backup_path.name)
                
                # Supprimer le fichier .db non compressé
                db_backup_path.unlink()
                
                final_path = zip_path
                logger.log_backup(str(zip_path), True)
            else:
                final_path = db_backup_path
                logger.log_backup(str(db_backup_path), True)
            
            return True, f"Sauvegarde créée: {final_path.name}", final_path
            
        except Exception as e:
            error_msg = f"Erreur lors de la sauvegarde: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def restore_backup(self, backup_path: Path) -> tuple[bool, str]:
        """
        Restaurer une sauvegarde
        
        Args:
            backup_path: Chemin de la sauvegarde
            
        Returns:
            (success, message)
        """
        try:
            if not backup_path.exists():
                return False, "Fichier de sauvegarde introuvable"
            
            # Si c'est un fichier ZIP, décompresser d'abord
            if backup_path.suffix == '.zip':
                temp_dir = config.DATA_DIR / "temp_restore"
                temp_dir.mkdir(exist_ok=True)
                
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Trouver le fichier .db
                db_files = list(temp_dir.glob("*.db"))
                if not db_files:
                    shutil.rmtree(temp_dir)
                    return False, "Aucune base de données trouvée dans l'archive"
                
                db_file = db_files[0]
            else:
                db_file = backup_path
            
            # Créer une sauvegarde de la base actuelle avant restauration
            current_backup = config.DATA_DIR / f"before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            if config.DATABASE_PATH.exists():
                shutil.copy2(config.DATABASE_PATH, current_backup)
            
            # Restaurer
            success = db.restore_database(db_file)
            
            # Nettoyer le dossier temporaire si créé
            if backup_path.suffix == '.zip':
                shutil.rmtree(temp_dir)
            
            if success:
                logger.info(f"Base de données restaurée depuis: {backup_path}")
                return True, "Restauration réussie"
            else:
                return False, "Erreur lors de la restauration"
                
        except Exception as e:
            error_msg = f"Erreur lors de la restauration: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def auto_backup(self) -> tuple[bool, str]:
        """
        Effectuer une sauvegarde automatique
        
        Returns:
            (success, message)
        """
        if not config.BACKUP_CONFIG['auto_backup']:
            return False, "Sauvegarde automatique désactivée"
        
        compress = config.BACKUP_CONFIG['compress_backups']
        success, message, _ = self.create_backup(compress=compress)
        
        if success:
            # Nettoyer les anciennes sauvegardes
            self.cleanup_old_backups()
        
        return success, message
    
    def cleanup_old_backups(self):
        """Supprimer les sauvegardes anciennes"""
        try:
            keep_days = config.BACKUP_CONFIG['keep_backups_days']
            cutoff_date = datetime.now() - timedelta(days=keep_days)
            
            # Lister tous les fichiers de sauvegarde
            backup_files = list(self.backup_dir.glob("minimarket_backup_*"))
            
            deleted_count = 0
            for backup_file in backup_files:
                # Obtenir la date de modification
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                
                if mtime < cutoff_date:
                    backup_file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"{deleted_count} ancienne(s) sauvegarde(s) supprimée(s)")
                
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des sauvegardes: {e}")
    
    def list_backups(self) -> List[Dict]:
        """
        Lister toutes les sauvegardes disponibles
        
        Returns:
            Liste de dictionnaires avec infos sur les sauvegardes
        """
        backups = []
        
        for backup_file in sorted(self.backup_dir.glob("minimarket_backup_*"), reverse=True):
            stat = backup_file.stat()
            
            backups.append({
                'path': backup_file,
                'name': backup_file.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_mtime),
                'created_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return backups
    
    def export_to_usb(self, usb_path: Path) -> tuple[bool, str]:
        """
        Exporter une sauvegarde vers une clé USB
        
        Args:
            usb_path: Chemin de la clé USB
            
        Returns:
            (success, message)
        """
        if not usb_path.exists():
            return False, "Clé USB introuvable"
        
        # Créer un dossier pour les sauvegardes sur la clé
        usb_backup_dir = usb_path / "MiniMarket_Backups"
        usb_backup_dir.mkdir(exist_ok=True)
        
        # Créer la sauvegarde
        success, message, backup_path = self.create_backup(
            destination=usb_backup_dir,
            compress=True
        )
        
        if success:
            return True, f"Sauvegarde exportée vers: {backup_path}"
        else:
            return False, message


# Instance globale
backup_manager = BackupManager()
