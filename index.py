import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import create_app

app = create_app()
