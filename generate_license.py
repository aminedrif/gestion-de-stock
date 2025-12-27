# -*- coding: utf-8 -*-
"""
Utilitaire de génération de clés de licence PERMANENTES
À utiliser par le développeur uniquement
"""
import hashlib


def generate_license_key(client_name: str, machine_id: str) -> str:
    """
    Générer une clé de licence PERMANENTE
    """
    secret = "AKHRIB_SUPERETTE_2024_SECRET"
    
    # Hash de validation basé UNIQUEMENT sur l'ID machine pour lock
    data_to_hash = f"{machine_id}_{secret}"
    validation_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()[:12].upper()
    
    return f"PRO-{validation_hash}"


def main():
    print("=" * 60)
    print("🔑 GÉNÉRATEUR DE CLÉS DE LICENCE PRO (MACHINE LOCK)")
    print("DamDev POS")
    print("=" * 60)
    print()
    
    # Demander les informations
    client_name = input("Nom du client (pour référence): ").strip()
    
    print("\n⚠️  IMPORTANT: Vous devez obtenir l'ID Machine du client.")
    print("   L'ID s'affiche quand il lance le logiciel sans licence.")
    machine_id = input("ID Machine du client (ex: 1234-ABCD-5678-EF90): ").strip()
    
    if not machine_id:
        print("❌ L'ID Machine est obligatoire pour la sécurité !")
        return
    
    # Générer la clé
    license_key = generate_license_key(client_name, machine_id)
    
    print()
    print("=" * 60)
    print("✅ CLÉ SÉCURISÉE GÉNÉRÉE")
    print("=" * 60)
    print()
    print(f"Client: {client_name}")
    print(f"Machine ID: {machine_id}")
    print(f"Type: LICENCE À VIE (Verrouillée sur cette machine)")
    print()
    print(f"🔐 CLÉ: {license_key}")
    print()
    print("=" * 60)
    print()
    print("Instructions:")
    print("1. Envoyez cette clé à votre client.")
    print("2. Elle ne fonctionnera QUE sur sa machine.")
    print("3. S'il change de PC, il faudra une nouvelle clé.")
    print()
    print("📧 Contact: DamDev Solutions")
    print()
    input("Appuyez sur Entrée pour fermer...")


if __name__ == "__main__":
    main()
