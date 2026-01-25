import subprocess
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("Building twit_mover.exe...")
result = subprocess.run([sys.executable, "-m", "PyInstaller", "twit_mover.spec", "--clean"])

if result.returncode == 0:
    print("\nBuild successful!")
    print(f"Executable: {os.path.join(script_dir, 'dist', 'twit_mover.exe')}")
else:
    print("\nBuild failed!")
    sys.exit(1)
