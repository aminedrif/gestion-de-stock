# Cahier des Charges - Logiciel de Gestion de Stock
## Supérette AKHRIB

---

## 1. Présentation Générale

**Nom du logiciel** : Gestion Supérette AKHRIB  
**Version** : 1.0.0  
**Technologie** : Python 3 + PyQt5 (Desktop)  
**Base de données** : SQLite (locale)  
**Développeur** : Amine Drif  

---

## 2. Objectifs du Logiciel

Le logiciel a pour but de gérer l'ensemble des opérations d'une supérette :
- Gestion des stocks de produits
- Point de vente (Caisse)
- Gestion des clients et de leurs crédits
- Gestion des fournisseurs et de leurs dettes
- Rapports de ventes et de profits
- Système de sauvegarde automatique

---

## 3. Modules et Fonctionnalités

### 3.1 Module Authentification
| Fonctionnalité | Description |
|----------------|-------------|
| Connexion sécurisée | Authentification par nom d'utilisateur et mot de passe (crypté bcrypt) |
| Gestion des rôles | Administrateur (accès complet) et Caissier (accès limité) |
| Verrouillage de compte | Après 3 tentatives échouées |
| Déconnexion automatique | Après 1 heure d'inactivité |

### 3.2 Module Produits
| Fonctionnalité | Description |
|----------------|-------------|
| Ajout de produits | Nom, code-barres, prix d'achat, prix de vente, catégorie, fournisseur |
| Modification/Suppression | Édition et suppression douce (soft delete) |
| Gestion des stocks | Suivi des quantités, alertes de stock bas |
| Import Excel | Importation en masse depuis fichier Excel |
| Recherche | Recherche par nom, code-barres, catégorie |
| Historique des prix | Suivi des changements de prix |

### 3.3 Module Point de Vente (POS)
| Fonctionnalité | Description |
|----------------|-------------|
| Interface de caisse | Interface tactile optimisée pour ventes rapides |
| Scan code-barres | Saisie par code-barres ou recherche manuelle |
| Calculatrice intégrée | Calcul du rendu monnaie |
| Sélection client | Client de passage ou client enregistré |
| Modes de paiement | Espèces, Carte, Crédit client, Paiement mixte |
| Remises | Application de remises (montant ou pourcentage) |
| Impression ticket | Génération et impression de tickets de caisse |

### 3.4 Module Clients
| Fonctionnalité | Description |
|----------------|-------------|
| Fiche client | Nom, téléphone, adresse, email |
| Gestion des crédits | Suivi des crédits clients (dettes) |
| Règlement crédit | Enregistrement des paiements de crédit |
| Historique achats | Suivi des achats par client |
| Filtres | Clients avec crédit, meilleurs clients |

### 3.5 Module Fournisseurs
| Fonctionnalité | Description |
|----------------|-------------|
| Fiche fournisseur | Nom société, contact, téléphone, adresse |
| Gestion des dettes | Suivi des dettes envers les fournisseurs |
| Enregistrement achats | Saisie des achats de marchandises |
| Règlement dette | Enregistrement des paiements aux fournisseurs |
| Produits associés | Liste des produits par fournisseur |

### 3.6 Module Rapports
| Fonctionnalité | Description |
|----------------|-------------|
| Ventes journalières | CA, coût, profit par jour |
| Ventes par produit | Produits les plus vendus, revenus par produit |
| Ventes par utilisateur | Performance des caissiers |
| KPI Dashboard | Chiffre d'affaires, profit, marge moyenne |
| Filtrage par date | Sélection de période pour les rapports |

### 3.7 Module Paramètres
| Fonctionnalité | Description |
|----------------|-------------|
| Gestion utilisateurs | Ajout/modification/suppression d'utilisateurs |
| Informations magasin | Nom, adresse, téléphone, NIF |
| Sauvegarde manuelle | Export ZIP (base de données + Excel) |
| Restauration | Restauration depuis sauvegarde |
| Réinitialisation | Remise à zéro des données (avec confirmation) |
| Thème | Mode clair / Mode sombre |
| Tutoriel | Guide d'utilisation intégré |
| À propos | Informations développeur |

### 3.8 Système de Sauvegarde Automatique
| Fonctionnalité | Description |
|----------------|-------------|
| Sauvegarde horaire | Backup automatique toutes les heures |
| Format ZIP | Base de données SQLite + Export Excel |
| Rétention | Conservation des 30 dernières sauvegardes |
| Dossier | `data/backups/` |

---

## 4. Architecture Technique

### 4.1 Structure des Dossiers
```
gestion de stock/
├── main.py                 # Point d'entrée
├── config.py               # Configuration globale
├── core/                   # Modules système
│   ├── auth.py            # Authentification
│   ├── backup.py          # Sauvegarde
│   ├── logger.py          # Journalisation
│   └── security.py        # Sécurité
├── database/              # Base de données
│   ├── db_manager.py      # Gestionnaire SQLite
│   └── schema.sql         # Schéma de création
├── modules/               # Logique métier
│   ├── customers/         # Gestion clients
│   ├── products/          # Gestion produits
│   ├── sales/             # Ventes et POS
│   ├── suppliers/         # Gestion fournisseurs
│   └── reports/           # Rapports
├── ui/                    # Interfaces graphiques
│   ├── main_window.py     # Fenêtre principale
│   ├── login_dialog.py    # Connexion
│   ├── home_page.py       # Accueil
│   ├── products_page.py   # Produits
│   ├── pos_page.py        # Caisse
│   ├── customers_page.py  # Clients
│   ├── suppliers_page.py  # Fournisseurs
│   ├── reports_page.py    # Rapports
│   └── settings_page.py   # Paramètres
└── data/                  # Données (créé au runtime)
    ├── minimarket.db      # Base de données
    ├── backups/           # Sauvegardes
    └── receipts/          # Tickets PDF
```

### 4.2 Base de Données (Tables)
| Table | Description |
|-------|-------------|
| users | Utilisateurs du système |
| categories | Catégories de produits |
| products | Catalogue produits |
| customers | Clients |
| customer_credit_transactions | Mouvements crédit clients |
| suppliers | Fournisseurs |
| supplier_transactions | Mouvements fournisseurs |
| sales | Ventes |
| sale_items | Lignes de vente |
| price_history | Historique des prix |
| settings | Paramètres du magasin |
| audit_log | Journal d'audit |

---

## 5. Sécurité

- **Mots de passe** : Cryptage bcrypt (irréversible)
- **Sessions** : Timeout automatique après 1 heure
- **Verrouillage** : Compte bloqué après 3 tentatives
- **Permissions** : Rôles Admin et Caissier avec droits différents
- **Suppression** : Soft delete (données conservées mais masquées)

---

## 6. Configuration par Défaut

| Paramètre | Valeur |
|-----------|--------|
| Utilisateur par défaut | admin |
| Mot de passe par défaut | admin123 |
| Seuil stock bas | 10 unités |
| Alerte expiration | 30 jours avant |
| Devise | DA (Dinar Algérien) |
| TVA | 19% |

---

## 7. Prérequis Techniques

### Pour développement :
- Python 3.10+
- PyQt5
- bcrypt, openpyxl, reportlab, matplotlib

### Pour utilisation :
- Windows 10/11 (64-bit)
- Fichier exécutable autonome (GestionDeStock.exe)
- Pas besoin d'installation supplémentaire

---

## 8. Livrables

1. **GestionDeStock.exe** - Application exécutable autonome (~66 MB)
2. **Code source** - Projet Python complet sur GitHub
3. **Documentation** - README et guides d'utilisation
4. **Sauvegardes** - Système automatique intégré

---

## 9. Contact

**Développeur** : Amine Drif  
**Email** : amine.drif2002@gmail.com  
**Téléphone** : 0561491987
**GitHub** : https://github.com/aminedrif

---

*Document généré le 24/12/2025*
