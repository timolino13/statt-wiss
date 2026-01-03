from pathlib import Path

# Basisverzeichnis des Projekts (z. B. das Verzeichnis, wo main.py liegt)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
LOG_DIR = PROJECT_ROOT / "logs"
