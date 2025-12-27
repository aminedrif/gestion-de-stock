import subprocess
import sys

def build_keygen():
    print("Building KeyGen.exe...")
    cmd = [
        'pyinstaller',
        '--name=KeyGen',
        '--onefile',
        '--console',
        '--clean',
        'generate_license.py'
    ]
    subprocess.run(cmd, check=True)
    print("Done! KeyGen.exe is in dist/")

if __name__ == "__main__":
    build_keygen()
