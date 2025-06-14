import csv
import os
from datetime import datetime
from typing import List, Dict
from flask import current_app

class Pengeluaran:
    def __init__(self, nama: str, jumlah: float, kategori: str, tanggal: str):
        self.nama = nama
        self.jumlah = float(jumlah)
        self.kategori = kategori
        self.tanggal = datetime.strptime(tanggal, '%Y-%m-%d')

    def to_dict(self) -> Dict:
        return {
            'nama': self.nama,
            'jumlah': self.jumlah,
            'kategori': self.kategori,
            'tanggal': self.tanggal.strftime('%Y-%m-%d')
        }

def simpan_pengeluaran(pengeluaran: Pengeluaran) -> bool:
    """Save expense to CSV with error handling"""
    try:
        file_exists = os.path.exists(current_app.config['EXPENSE_FILE'])
        with open(current_app.config['EXPENSE_FILE'], mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['nama', 'jumlah', 'kategori', 'tanggal'])
            if not file_exists:
                writer.writeheader()
            writer.writerow(pengeluaran.to_dict())
        return True
    except Exception as e:
        current_app.logger.error(f"Error saving expense: {e}")
        return False

def baca_pengeluaran() -> List[Dict]:
    """Read all expenses from CSV"""
    if not os.path.exists(current_app.config['EXPENSE_FILE']):
        return []
    
    expenses = []
    try:
        with open(current_app.config['EXPENSE_FILE'], mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    expenses.append({
                        'nama': row['nama'],
                        'jumlah': float(row['jumlah']),
                        'kategori': row['kategori'],
                        'tanggal': row['tanggal']
                    })
                except (ValueError, KeyError):
                    continue
    except Exception as e:
        current_app.logger.error(f"Error reading expenses: {e}")
    
    return expenses
