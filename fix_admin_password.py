# -*- coding: utf-8 -*-
"""
Script pour créer un utilisateur admin avec le bon hash
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.security import hash_password
from database.db_manager import db

# Générer le hash pour admin123
password_hash = hash_password("admin123")
print(f"Hash pour 'admin123': {password_hash}")

# Mettre à jour l'utilisateur admin
db.execute_update("""
    UPDATE users 
    SET password_hash = ?
    WHERE username = 'admin'
""", (password_hash,))

print("✓ Mot de passe admin mis à jour avec succès!")
print("Vous pouvez maintenant vous connecter avec: admin / admin123")

