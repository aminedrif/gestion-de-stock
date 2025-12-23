# 📦 Guide de Distribution - Gestion de Stock

## ✅ Exécutable Créé avec Succès!

Votre application a été compilée en un fichier exécutable standalone.

### 📍 Emplacement de l'Exécutable

```
dist/GestionDeStock.exe
```

**Taille**: ~76 MB (contient Python + toutes les dépendances)

---

## 🚀 Comment Utiliser l'Exécutable

### Option 1: Exécution Simple
1. Double-cliquez sur `dist/GestionDeStock.exe`
2. L'application se lancera directement
3. Connectez-vous avec: `admin` / `admin123`

### Option 2: Distribution à d'Autres Utilisateurs

**Ce dont vous avez besoin:**
- Le fichier `GestionDeStock.exe` (dans le dossier `dist/`)
- C'est tout! Aucune installation de Python requise

**Pour distribuer:**
1. Copiez `GestionDeStock.exe` sur une clé USB ou envoyez-le par email
2. L'utilisateur peut simplement double-cliquer pour lancer l'application
3. La base de données sera créée automatiquement au premier lancement

---

## 📂 Structure des Données

Lors de la première exécution, l'application créera automatiquement:

```
C:\Users\[Utilisateur]\AppData\Local\MiniMarket\
├── data\
│   ├── minimarket.db          # Base de données SQLite
│   ├── backups\                # Sauvegardes automatiques
│   └── receipts\               # Tickets de caisse
└── logs\
    └── minimarket.log          # Fichiers de logs
```

---

## 🔧 Reconstruire l'Exécutable

Si vous modifiez le code et voulez recréer l'exécutable:

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate

# Reconstruire
python build_executable.py
```

---

## 📋 Options de Build Avancées

### Créer un Exécutable avec Console (pour Debug)

Modifiez `build_executable.py` et changez:
```python
'--windowed',  # Remplacer par '--console'
```

### Ajouter une Icône

1. Créez ou obtenez un fichier `.ico`
2. Dans `build_executable.py`, ajoutez:
```python
'--icon=chemin/vers/icone.ico',
```

### Créer un Dossier au lieu d'un Seul Fichier

Remplacez `--onefile` par `--onedir` dans `build_executable.py`:
- **Avantage**: Démarrage plus rapide
- **Inconvénient**: Plusieurs fichiers à distribuer

---

## 🎯 Créer un Installateur (Optionnel)

Pour une distribution professionnelle, vous pouvez créer un installateur:

### Option 1: Inno Setup (Recommandé pour Windows)

1. Téléchargez [Inno Setup](https://jrsoftware.org/isdl.php)
2. Créez un script `.iss` qui:
   - Copie `GestionDeStock.exe`
   - Crée un raccourci sur le bureau
   - Ajoute au menu Démarrer
   - Permet la désinstallation

### Option 2: NSIS

Alternative à Inno Setup, également gratuit et open-source.

---

## ⚠️ Notes Importantes

### Antivirus
- Certains antivirus peuvent signaler l'exécutable comme suspect (faux positif)
- C'est normal pour les exécutables PyInstaller
- Solution: Signez numériquement votre exécutable ou ajoutez une exception

### Première Exécution
- Le premier lancement peut être plus lent (décompression)
- Les lancements suivants seront plus rapides

### Mise à Jour
- Pour mettre à jour, remplacez simplement l'ancien `.exe` par le nouveau
- La base de données sera préservée

---

## 🔍 Dépannage

### L'exécutable ne démarre pas
1. Vérifiez les logs dans `%LOCALAPPDATA%\MiniMarket\logs\`
2. Essayez de reconstruire avec `--console` pour voir les erreurs
3. Vérifiez que l'antivirus ne bloque pas l'exécutable

### Erreur "Base de données introuvable"
- L'application créera automatiquement la base de données
- Vérifiez les permissions d'écriture dans `%LOCALAPPDATA%`

### L'application est trop lente
- Utilisez `--onedir` au lieu de `--onefile`
- Optimisez en excluant les modules inutilisés

---

## 📊 Informations Techniques

**Construit avec:**
- PyInstaller 6.17+
- Python 3.x
- PyQt5
- SQLite

**Contenu de l'exécutable:**
- Interpréteur Python embarqué
- Toutes les bibliothèques Python (PyQt5, bcrypt, openpyxl, etc.)
- Schéma de base de données
- Fichiers de configuration

---

## 📞 Support

Pour toute question ou problème:
- Consultez les logs: `%LOCALAPPDATA%\MiniMarket\logs\minimarket.log`
- Vérifiez le README principal du projet
- Contactez le développeur

---

## 📝 Licence

Version 1.0.0 - Gestion de Stock Mini-Market
© 2025 - Tous droits réservés
