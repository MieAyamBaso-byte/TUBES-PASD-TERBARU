import pandas as pd #ambil pandas
from datetime import datetime
from typing import Dict, List
from flask import current_app  # Menambahkan impor current_app

class StatistikPengeluaran:
    def __init__(self, file_path: str = None):
        # Menggunakan current_app untuk mengambil file dari konfigurasi
        self.file_path = file_path or current_app.config['EXPENSE_FILE']
        try:
            self.df = pd.read_csv(self.file_path)
            self._preprocess_data()
        except (FileNotFoundError, pd.errors.EmptyDataError):
            self.df = pd.DataFrame(columns=['nama', 'jumlah', 'kategori', 'tanggal'])

    def _preprocess_data(self):
        """Prepare data for analysis"""
        self.df['tanggal'] = pd.to_datetime(self.df['tanggal'])
        self.df['hari'] = self.df['tanggal'].dt.day_name()
        self.df['bulan'] = self.df['tanggal'].dt.month_name()
        self.df['minggu'] = self.df['tanggal'].dt.isocalendar().week

    def pengeluaran_per_kategori(self, limit: int = 5) -> Dict:
        """Get spending by category (top N)"""
        return self.df.groupby('kategori')['jumlah'].sum().nlargest(limit).to_dict()

    def rata_pengeluaran_harian(self) -> float:
        """Calculate daily average spending"""
        if self.df.empty:
            return 0.0
        return self.df.groupby(self.df['tanggal'].dt.date)['jumlah'].sum().mean()

    def estimasi_hari_bertahan(self, saldo: float) -> float:
        """Estimate days until money runs out"""
        rata_harian = self.rata_pengeluaran_harian()
        return round(saldo / rata_harian, 2) if rata_harian > 0 else 0.0

    def pola_pengeluaran_harian(self) -> Dict:
        """Weekly spending pattern"""
        if self.df.empty:
            return {}
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return self.df.groupby('hari')['jumlah'].sum().reindex(days_order).fillna(0).to_dict()

    def tren_bulanan(self) -> Dict:
        """Monthly spending trend"""
        if self.df.empty:
            return {}
        return self.df.groupby('bulan')['jumlah'].sum().to_dict()
    
    def tren_bulanan(self) -> Dict:
        """Monthly spending trend"""
        if self.df.empty:
            return {}
        return self.df.groupby(['tahun', 'bulan'])['jumlah'].sum().to_dict()

    def tren_harian(self) -> List[Dict]:
        """Daily spending trend"""
        if self.df.empty:
            return []
        daily = self.df.groupby('tanggal')['jumlah'].sum().reset_index()
        return daily.to_dict('records')

    def tren_per_kategori(self) -> Dict:
        """Spending trend by category"""
        if self.df.empty:
            return {}
        return self.df.groupby(['kategori', self.df['tanggal'].dt.to_period('M')])['jumlah'].sum().unstack().to_dict()
