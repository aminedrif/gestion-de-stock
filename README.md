# Gestion de Mini-Market

Système professionnel de gestion de mini-market hors ligne avec PyQt5 et SQLite.

## 📋 Fonctionnalités

### ✅ Implémentées (Backend)

- **Authentification & Sécurité**
  - Système de connexion avec rôles (admin/caissier)
  - Hachage sécurisé des mots de passe (bcrypt)
  - Verrouillage après tentatives échouées
  - Journal d'audit complet

- **Gestion des Produits**
  - CRUD complet des produits
  - Gestion des catégories
  - Code-barres
  - Alertes stock minimum
  - Dates d'expiration
  - Historique des prix
  - Promotions

- **Point de Vente (POS)**
  - Panier d'achat intelligent
  - Réductions (% ou montant fixe)
  - Multi-méthodes de paiement (espèces, carte, crédit)
  - Calcul automatique du bénéfice
  - Annulation/retour de ventes

- **Gestion des Clients**
  - Clients fidèles
  - Crédit client avec limite
  - Historique des achats
  - Statistiques client

- **Gestion des Fournisseurs**
  - CRUD fournisseurs
  - Gestion des dettes
  - Historique des transactions

- **Tickets de Caisse**
  - Génération PDF
  - Format texte (imprimantes thermiques ESC/POS)
  - Format HTML (aperçu)
  - Impression standard

- **Rapports**
  - Ventes par jour/mois
  - Bénéfice net
  - Top produits vendus
  - Ventes par catégorie
  - Performance des caissiers

- **Sauvegarde**
  - Sauvegarde automatique
  - Export vers clé USB
  - Restauration de sauvegarde

### 🚧 À Implémenter

- **Interface Graphique PyQt5**
  - Fenêtre principale
  - Écrans de gestion
  - Interface caisse
  - Dialogues

- **Multi-langue (FR/AR)**
  - Fichiers de traduction
  - Support RTL pour l'arabe

- **Import/Export Excel**

- **Compilation .exe**
  - Configuration PyInstaller

## 🏗️ Structure du Projet

```
gestion-minimarket/
├── main.py                 # Point d'entrée
├── test_modules.py         # Tests des modules
├── config.py               # Configuration
├── requirements.txt        # Dépendances
│
├── database/
│   ├── schema.sql          # Schéma SQLite
│   ├── db_manager.py       # Gestionnaire DB
│   └── __init__.py
│
├── core/
│   ├── auth.py             # Authentification
│   ├── logger.py           # Journalisation
│   ├── security.py         # Sécurité
│   ├── backup.py           # Sauvegarde
│   └── __init__.py
│
├── modules/
│   ├── products/
│   │   ├── product_manager.py
│   │   ├── category_manager.py
│   │   └── __init__.py
│   │
│   ├── sales/
│   │   ├── pos.py          # Point de vente
│   │   ├── cart.py         # Panier
│   │   ├── receipt.py      # Génération tickets
│   │   ├── printer.py      # Impression
│   │   └── __init__.py
│   │
│   ├── customers/
│   │   ├── customer_manager.py
│   │   └── __init__.py
│   │
│   ├── suppliers/
│   │   ├── supplier_manager.py
│   │   └── __init__.py
│   │
│   └── reports/
│       ├── sales_report.py
│       ├── profit_report.py
│       └── __init__.py
│
├── data/
│   ├── minimarket.db       # Base de données (généré)
│   ├── backups/            # Sauvegardes
│   └── receipts/           # Tickets PDF
│
└── logs/
    └── app.log             # Fichiers de log
```

## 🚀 Installation

### 1. Cloner ou télécharger le projet

```bash
cd "c:\Users\msi\Desktop\gestion de stock"
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
python main.py
```

### 4. Tester les modules (sans GUI)

```bash
python test_modules.py
```

## 🔑 Compte par Défaut

- **Utilisateur**: `admin`
- **Mot de passe**: `admin123`
- **Rôle**: Administrateur

## 📊 Base de Données

La base de données SQLite est créée automatiquement au premier lancement.

### Tables Principales

- `users` - Utilisateurs
- `categories` - Catégories de produits
- `products` - Produits
- `customers` - Clients
- `suppliers` - Fournisseurs
- `sales` - Ventes
- `sale_items` - Détails des ventes
- `returns` - Retours
- `audit_log` - Journal d'audit

## 🛠️ Technologies

- **Python 3.8+**
- **PyQt5** - Interface graphique (à implémenter)
- **SQLite** - Base de données
- **bcrypt** - Hachage des mots de passe
- **ReportLab** - Génération PDF
- **python-escpos** - Imprimantes thermiques
- **openpyxl** - Import/Export Excel

## 📝 Utilisation

### Créer un Produit

```python
from modules.products.product_manager import product_manager

success, message, product_id = product_manager.create_product(
    name="Coca Cola 1.5L",
    name_ar="كوكا كولا",
    selling_price=150.0,
    purchase_price=100.0,
    barcode="1234567890",
    stock_quantity=50
)
```

### Effectuer une Vente

```python
from modules.sales.pos import pos_manager

# Nouvelle vente
pos_manager.new_sale()

# Ajouter des produits
pos_manager.add_product_by_barcode("1234567890", quantity=2)

# Finaliser
success, message, sale_id = pos_manager.complete_sale(
    cashier_id=1,
    payment_method='cash',
    amount_paid=300.0
)
```

### Générer un Rapport

```python
from modules.reports.sales_report import sales_report_manager

# Ventes du jour
stats = sales_report_manager.get_daily_sales()
print(f"Chiffre d'affaires: {stats['total_revenue']} DA")
```

## 🔒 Sécurité

- Mots de passe hachés avec bcrypt
- Verrouillage après 3 tentatives échouées
- Journal d'audit de toutes les actions
- Gestion des permissions par rôle

## 💾 Sauvegarde

```python
from core.backup import backup_manager

# Sauvegarde manuelle
success, message, path = backup_manager.create_backup()

# Export vers USB
success, message = backup_manager.export_to_usb(Path("E:/"))
```

## 📈 Prochaines Étapes

1. **Interface PyQt5**
   - Créer les widgets principaux
   - Implémenter les dialogues
   - Connecter aux modules backend

2. **Multi-langue**
   - Créer les fichiers de traduction
   - Implémenter le support RTL

3. **Compilation**
   - Configurer PyInstaller
   - Créer l'exécutable .exe

4. **Tests**
   - Tests unitaires
   - Tests d'intégration

## 📄 Licence

Projet personnel - Tous droits réservés

## 👨‍💻 Auteur

Développé pour la gestion professionnelle de mini-market

---

**Version**: 1.0.0  
**Date**: Décembre 2025
