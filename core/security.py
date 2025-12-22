# -*- coding: utf-8 -*-
"""
Module de sécurité - Hachage des mots de passe
"""
import bcrypt


def hash_password(password: str) -> str:
    """
    Hacher un mot de passe avec bcrypt
    
    Args:
        password: Mot de passe en clair
        
    Returns:
        Hash du mot de passe (string)
    """
    # Convertir le mot de passe en bytes
    password_bytes = password.encode('utf-8')
    
    # Générer un salt et hacher
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Retourner le hash en string
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Vérifier un mot de passe contre son hash
    
    Args:
        password: Mot de passe en clair
        password_hash: Hash stocké
        
    Returns:
        True si le mot de passe correspond
    """
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Erreur lors de la vérification du mot de passe: {e}")
        return False


def is_strong_password(password: str) -> tuple[bool, str]:
    """
    Vérifier la force d'un mot de passe
    
    Args:
        password: Mot de passe à vérifier
        
    Returns:
        (is_strong, message)
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Le mot de passe doit contenir des majuscules, minuscules et chiffres"
    
    return True, "Mot de passe fort"
