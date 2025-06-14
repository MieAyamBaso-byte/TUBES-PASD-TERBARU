import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rahasia-sangat-kuat-12345'
    DATA_FOLDER = BASE_DIR / 'data'
    MODEL_FOLDER = BASE_DIR / 'data' / 'models'
    EXPENSE_FILE = DATA_FOLDER / 'pengeluaran.csv'
    
    @staticmethod
    def init_app(app):
        os.makedirs(Config.DATA_FOLDER, exist_ok=True)
        os.makedirs(Config.MODEL_FOLDER, exist_ok=True)
        
        # Initialize default files if not exist
        if not Config.EXPENSE_FILE.exists():
            with open(Config.EXPENSE_FILE, 'w') as f:
                f.write("nama,jumlah,kategori,tanggal\n")