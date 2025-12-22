# -*- coding: utf-8 -*-
"""
Script de test des modules
Permet de tester les fonctionnalités sans interface graphique
"""
import sys
from pathlib import Path

# Ajouter le répertoire courant au path
sys.path.insert(0, str(Path(__file__).parent))

from core.auth import auth_manager
from core.logger import logger
from modules.products.product_manager import product_manager
from modules.products.category_manager import category_manager
from modules.sales.pos import pos_manager
from modules.customers.customer_manager import customer_manager
from modules.suppliers.supplier_manager import supplier_manager
from modules.reports.sales_report import sales_report_manager
from modules.reports.profit_report import profit_report_manager


def test_authentication():
    """Tester l'authentification"""
    print("\n" + "=" * 60)
    print("TEST: Authentification")
    print("=" * 60)
    
    # Connexion avec le compte admin par défaut
    success, message, user = auth_manager.login("admin", "admin123")
    
    if success:
        print(f"✓ Connexion réussie: {user['full_name']} ({user['role']})")
    else:
        print(f"✗ Échec de connexion: {message}")
    
    return success


def test_categories():
    """Tester les catégories"""
    print("\n" + "=" * 60)
    print("TEST: Catégories")
    print("=" * 60)
    
    # Lister les catégories existantes
    categories = category_manager.get_all_categories()
    print(f"✓ Catégories existantes: {len(categories)}")
    
    for cat in categories:
        print(f"  - {cat['name']} ({cat['name_ar']})")
    
    return True


def test_products():
    """Tester les produits"""
    print("\n" + "=" * 60)
    print("TEST: Produits")
    print("=" * 60)
    
    # Créer un produit de test
    success, message, product_id = product_manager.create_product(
        name="Coca Cola 1.5L",
        name_ar="كوكا كولا 1.5 لتر",
        selling_price=150.0,
        purchase_price=100.0,
        barcode="1234567890123",
        category_id=2,  # Boissons
        stock_quantity=50,
        min_stock_level=10,
        created_by=1
    )
    
    if success:
        print(f"✓ Produit créé: ID {product_id}")
        
        # Récupérer le produit
        product = product_manager.get_product(product_id)
        print(f"  Nom: {product['name']}")
        print(f"  Prix: {product['selling_price']} DA")
        print(f"  Stock: {product['stock_quantity']}")
    else:
        print(f"✗ Erreur: {message}")
    
    # Lister les produits
    products = product_manager.get_all_products(limit=5)
    print(f"\n✓ Produits dans la base: {len(products)}")
    
    # Statistiques
    stats = product_manager.get_product_stats()
    print(f"\n✓ Statistiques produits:")
    print(f"  - Total produits: {stats['total_products']}")
    print(f"  - Valeur stock: {stats['total_stock_value']} DA")
    print(f"  - Stock faible: {stats['low_stock_count']}")
    print(f"  - En promotion: {stats['promoted_count']}")
    
    return success


def test_customers():
    """Tester les clients"""
    print("\n" + "=" * 60)
    print("TEST: Clients")
    print("=" * 60)
    
    # Créer un client de test
    success, message, customer_id = customer_manager.create_customer(
        full_name="Ahmed Benali",
        phone="0555123456",
        credit_limit=5000.0
    )
    
    if success:
        print(f"✓ Client créé: {message}")
        
        # Récupérer le client
        customer = customer_manager.get_customer(customer_id)
        print(f"  Code: {customer['code']}")
        print(f"  Nom: {customer['full_name']}")
        print(f"  Limite crédit: {customer['credit_limit']} DA")
    else:
        print(f"✗ Erreur: {message}")
    
    # Lister les clients
    customers = customer_manager.get_all_customers()
    print(f"\n✓ Clients dans la base: {len(customers)}")
    
    return success


def test_pos():
    """Tester le point de vente"""
    print("\n" + "=" * 60)
    print("TEST: Point de Vente (POS)")
    print("=" * 60)
    
    # Nouvelle vente
    pos_manager.new_sale()
    
    # Ajouter des produits (si disponibles)
    products = product_manager.get_all_products(limit=2)
    
    if len(products) > 0:
        for product in products[:2]:
            success, message = pos_manager.add_product_by_id(product['id'], 2)
            if success:
                print(f"✓ Produit ajouté: {product['name']} x 2")
            else:
                print(f"✗ Erreur: {message}")
        
        # Afficher le panier
        cart = pos_manager.get_cart()
        cart_data = cart.to_dict()
        
        print(f"\n✓ Panier:")
        print(f"  - Articles: {cart_data['item_count']}")
        print(f"  - Quantité totale: {cart_data['total_quantity']}")
        print(f"  - Sous-total: {cart_data['subtotal']} DA")
        print(f"  - Total: {cart_data['total']} DA")
        print(f"  - Bénéfice: {cart_data['profit']} DA")
        
        # Appliquer une réduction
        cart.set_discount_percentage(10)
        print(f"\n✓ Réduction de 10% appliquée")
        print(f"  - Nouveau total: {cart.get_total()} DA")
        
        # Finaliser la vente (simulation)
        print(f"\n✓ Vente prête à être finalisée")
        print(f"  (Utilisez pos_manager.complete_sale() pour finaliser)")
        
        return True
    else:
        print("✗ Aucun produit disponible pour tester le POS")
        return False


def test_reports():
    """Tester les rapports"""
    print("\n" + "=" * 60)
    print("TEST: Rapports")
    print("=" * 60)
    
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Rapport du jour
    daily_sales = sales_report_manager.get_daily_sales(today)
    print(f"✓ Ventes du jour ({today}):")
    print(f"  - Nombre de ventes: {daily_sales['sale_count']}")
    print(f"  - Chiffre d'affaires: {daily_sales['total_revenue']} DA")
    print(f"  - Vente moyenne: {daily_sales['average_sale']} DA")
    
    # Bénéfice du jour
    daily_profit = profit_report_manager.get_daily_profit(today)
    print(f"\n✓ Bénéfice du jour:")
    print(f"  - Revenu: {daily_profit['total_revenue']} DA")
    print(f"  - Coût: {daily_profit['total_cost']} DA")
    print(f"  - Bénéfice net: {daily_profit['net_profit']} DA")
    print(f"  - Marge: {daily_profit['profit_margin']}%")
    
    return True


def run_all_tests():
    """Exécuter tous les tests"""
    print("\n" + "=" * 60)
    print("  TEST DES MODULES - GESTION MINI-MARKET")
    print("=" * 60)
    
    tests = [
        ("Authentification", test_authentication),
        ("Catégories", test_categories),
        ("Produits", test_products),
        ("Clients", test_customers),
        ("Point de Vente", test_pos),
        ("Rapports", test_reports),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ ERREUR dans {test_name}: {e}")
            logger.exception(f"Erreur dans le test {test_name}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "=" * 60)
    print("  RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ RÉUSSI" if result else "✗ ÉCHOUÉ"
        print(f"{status}: {test_name}")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    print("\n" + "=" * 60)
    print(f"  {success_count}/{total_count} tests réussis")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
    input("\nAppuyez sur Entrée pour quitter...")
