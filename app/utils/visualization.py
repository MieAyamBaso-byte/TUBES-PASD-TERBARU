import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime

def create_daily_spending_chart(df):
    """Create daily spending line chart"""
    if df.empty:
        return None
        
    daily_spending = df.groupby(df['tanggal'].dt.date)['jumlah'].sum().reset_index()
    daily_spending.columns = ['tanggal', 'total']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_spending['tanggal'],
        y=daily_spending['total'],
        mode='lines+markers',
        name='Pengeluaran Harian',
        line=dict(color='#3498db', width=2),
        marker=dict(size=8)
    ))
    
    # Add 7-day moving average
    daily_spending['moving_avg'] = daily_spending['total'].rolling(7, min_periods=1).mean()
    
    fig.add_trace(go.Scatter(
        x=daily_spending['tanggal'],
        y=daily_spending['moving_avg'],
        mode='lines',
        name='Rata-rata 7 Hari',
        line=dict(color='#e74c3c', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title='Tren Pengeluaran Harian',
        xaxis_title='Tanggal',
        yaxis_title='Jumlah Pengeluaran',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    return fig.to_html(full_html=False, config={'displayModeBar': False})

def create_category_pie_chart(df):
    """Create pie chart of spending by category"""
    if df.empty:
        return None
        
    category_spending = df.groupby('kategori')['jumlah'].sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=category_spending['kategori'],
        values=category_spending['jumlah'],
        hole=0.4,
        marker=dict(colors=['#3498db', '#2ecc71', '#f1c40f', '#e74c3c', '#9b59b6'])
    ))
    
    fig.update_layout(
        title='Distribusi Pengeluaran per Kategori',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig.to_html(full_html=False, config={'displayModeBar': False})

def create_weekly_pattern_chart(df):
    """Create bar chart of weekly spending pattern"""
    if df.empty:
        return None
        
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_pattern = df.groupby('hari')['jumlah'].sum().reindex(days_order).fillna(0)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=weekly_pattern.index,
        y=weekly_pattern.values,
        marker_color='#2ecc71'
    ))
    
    fig.update_layout(
        title='Pola Pengeluaran Mingguan',
        xaxis_title='Hari',
        yaxis_title='Total Pengeluaran',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig.to_html(full_html=False, config={'displayModeBar': False})

def create_monthly_trend_chart(df):
    """Create monthly trend chart"""
    if df.empty:
        return None
        
    monthly_trend = df.groupby('bulan')['jumlah'].sum()
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=monthly_trend.index,
        y=monthly_trend.values,
        marker_color='#3498db'
    ))
    
    fig.update_layout(
        title='Tren Pengeluaran Bulanan',
        xaxis_title='Bulan',
        yaxis_title='Total Pengeluaran',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig.to_html(full_html=False, config={'displayModeBar': False})

def generate_all_visualizations(df):
    """Generate all visualizations for the analytics page"""
    return {
        'daily_chart': create_daily_spending_chart(df),
        'category_chart': create_category_pie_chart(df),
        'weekly_chart': create_weekly_pattern_chart(df),
        'monthly_chart': create_monthly_trend_chart(df)
    }