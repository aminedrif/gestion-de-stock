"""
Script pour créer un fichier .exe de l'application Gestion de Stock
Utilise PyInstaller pour créer un exécutable standalone
"""

import os
import subprocess
import sys

def build_exe():
    """Construire l'exécutable avec PyInstaller"""
    
    print("=" * 60)
    print("Construction de l'exécutable GestionDeStock.exe")
    print("=" * 60)
    
    # Commande PyInstaller
    cmd = [
        'pyinstaller',
        '--name=DamDevPOS',
        '--onefile',  # Un seul fichier .exe
        '--windowed',  # Pas de console
        '--add-data=database/schema.sql;database',  # Inclure le schéma SQL
        '--add-data=config.py;.',  # Inclure config.py
        '--collect-all=escpos',    # Collecter tout escpos (capabilities.json, etc.)
        '--collect-all=reportlab', # Collecter tout reportlab (fonts, etc.)
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=bcrypt',
        '--hidden-import=openpyxl',
        '--hidden-import=xlsxwriter',
        '--hidden-import=reportlab',
        '--hidden-import=reportlab.pdfgen.canvas',
        '--hidden-import=reportlab.platypus', 
        '--hidden-import=reportlab.lib.pagesizes',
        '--hidden-import=reportlab.lib.styles',
        '--hidden-import=reportlab.lib.units',
        '--hidden-import=reportlab.lib.colors',
        '--hidden-import=reportlab.lib.enums',
        '--hidden-import=matplotlib',
        '--hidden-import=PIL',
        '--hidden-import=escpos.printer',
        '--hidden-import=escpos.escpos',
        '--clean',  # Nettoyer avant de construire
        '--add-data=resources;resources',  # Include resources folder
        'main.py'
    ]
    
    # Check for icon
    icon_path = os.path.join('resources', 'images', 'logo.ico')
    # If .ico doesn't exist, we can't force it for Windows exe easily without conversion
    # But we can try to find valid icon
    if os.path.exists(icon_path):
        cmd.insert(2, f'--icon={icon_path}')
        print(f"Icône ajoutée: {icon_path}")
    else:
        print("ℹ️  Aucun fichier .ico trouvé dans resources/images/logo.ico - L'icône par défaut sera utilisée.")
    
    print("\nCommande PyInstaller:")
    print(' '.join(cmd))
    print("\n" + "=" * 60)
    print("Construction en cours... (cela peut prendre quelques minutes)")
    print("=" * 60 + "\n")
    
    try:
        # Exécuter PyInstaller
        result = subprocess.run(cmd, check=True)
        
        print("\n" + "=" * 60)
        print("✓ Construction réussie!")
        print("=" * 60)
        print("\nL'exécutable se trouve dans:")
        print("  dist/DamDevPOS.exe")
        print("\nVous pouvez maintenant:")
        print("  1. Tester l'exécutable: dist\\DamDevPOS.exe")
        print("  2. Distribuer ce fichier à d'autres utilisateurs")
        print("  3. Créer un installateur si nécessaire")
        print("=" * 60)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print("✗ Erreur lors de la construction")
        print("=" * 60)
        print(f"Erreur: {e}")
        return False
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ Erreur inattendue")
        print("=" * 60)
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
