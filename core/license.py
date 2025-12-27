# -*- coding: utf-8 -*-
"""
Gestionnaire de licence - Validation locale avec verrouillage machine
Compatible avec generate_license.py (keygen)
"""
import hashlib
import uuid
import platform
from pathlib import Path
from database.db_manager import db
import config


class LicenseManager:
    """Gestionnaire de licence avec verrouillage machine"""
    
    def __init__(self):
        self.secret = "AKHRIB_SUPERETTE_2024_SECRET"
        self.license_file = config.DATA_DIR / "license.dat"
    
    def get_machine_id(self) -> str:
        """Generer un ID unique pour cette machine"""
        try:
            machine_info = f"{platform.node()}-{uuid.getnode()}"
            machine_hash = hashlib.md5(machine_info.encode()).hexdigest()[:16].upper()
            return f"{machine_hash[:4]}-{machine_hash[4:8]}-{machine_hash[8:12]}-{machine_hash[12:16]}"
        except Exception:
            return "0000-0000-0000-0000"
    
    def validate_key(self, license_key: str, machine_id: str) -> bool:
        """Valider une cle de licence pour une machine donnee"""
        if not license_key or not license_key.startswith("PRO-"):
            return False
        
        data_to_hash = f"{machine_id}_{self.secret}"
        expected_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()[:12].upper()
        expected_key = f"PRO-{expected_hash}"
        
        return license_key.strip().upper() == expected_key.upper()
    
    def is_licensed(self) -> tuple:
        """Verifier si le logiciel est sous licence valide"""
        try:
            result = db.fetch_one("SELECT * FROM license LIMIT 1")
            if result:
                result = dict(result) # Convert sqlite3.Row to dict
                stored_key = result.get('license_key', '')
                stored_machine = result.get('machine_id', '')
                current_machine = self.get_machine_id()
                
                if stored_machine == current_machine:
                    if self.validate_key(stored_key, current_machine):
                        return True, "Licence permanente"
                
            if self.license_file.exists():
                stored_key = self.license_file.read_text().strip()
                if self.validate_key(stored_key, self.get_machine_id()):
                    self.activate_license(stored_key)
                    return True, "Licence permanente"
            
            return False, "Licence non trouvee"
            
        except Exception as e:
            return False, f"Erreur de verification: {e}"
    
    def activate_license(self, license_key: str) -> tuple:
        """Activer une licence"""
        machine_id = self.get_machine_id()
        
        if not self.validate_key(license_key, machine_id):
            return False, "Cle de licence invalide pour cette machine"
        
        try:
            db.execute_update("DELETE FROM license")
            db.execute_update(
                "INSERT INTO license (license_key, machine_id, activation_date) VALUES (?, ?, datetime('now'))",
                (license_key.strip().upper(), machine_id)
            )
            
            self.license_file.write_text(license_key.strip().upper())
            
            return True, "Licence activee avec succes !"
            
        except Exception as e:
            return False, f"Erreur d'activation: {e}"


license_manager = LicenseManager()
