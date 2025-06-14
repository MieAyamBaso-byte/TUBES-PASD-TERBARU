from flask import Blueprint, render_template, jsonify
from datetime import datetime, timedelta
import json
from collections import defaultdict
import numpy as np

analytics_bp = Blueprint('analytics', __name__)

# Sample data - in a real app, this would come from a database
def load_sample_data():
    """Load sample expense data for demonstration"""
    try:
        with open('sample_expenses.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Generate sample data if file doesn't exist
        sample_data = generate_sample_data()
        with open('sample_expenses.json', 'w') as f:
            json.dump(sample_data, f)
        return sample_data

def generate_sample_data():
    """Generate realistic sample expense data for students"""
    categories = ['makanan', 'transportasi', 'kuliah', 'hiburan', 'tagihan', 'lainnya']
    current_date = datetime.now()
    
    expenses = []
    for i in range(90):  # 3 months of data
        date = (current_date - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Generate 1-3 expenses per day
        for _ in range(np.random.randint(1, 4)):
            category = np.random.choice(categories)
            
            # Base amount based on category
            base_amounts = {
                'makanan': 15000,
                'transportasi': 10000,
                'kuliah': 50000,
                'hiburan': 30000,
                'tagihan': 100000,
                'lainnya': 25000
            }
            
            # Random variation
            amount = base_amounts[category] * np.random.uniform(0.8, 1.5)
            amount = round(amount / 1000) * 1000  # Round to nearest 1000
            
            expenses.append({
                'nama': f"Pengeluaran {category} {i}",
                'kategori': category,
                'jumlah': int(amount),
                'tanggal': date
            })
    
    return expenses

@analytics_bp.route('/analytics')
def analytics():
    """Render the analytics dashboard"""
    return render_template('analytics.html')

@analytics_bp.route('/api/analytics/summary')
def get_analytics_summary():
    """API endpoint for analytics summary data"""
    expenses = load_sample_data()
    
    # Calculate total spending
    total_spent = sum(exp['jumlah'] for exp in expenses)
    
    # Calculate spending by category
    category_spending = defaultdict(int)
    for exp in expenses:
        category_spending[exp['kategori']] += exp['jumlah']
    
    # Calculate weekly spending
    weekly_spending = defaultdict(int)
    for exp in expenses:
        date = datetime.strptime(exp['tanggal'], '%Y-%m-%d')
        week_num = date.isocalendar()[1]
        weekly_spending[f"Week {week_num}"] += exp['jumlah']
    
    # Calculate monthly spending
    monthly_spending = defaultdict(int)
    for exp in expenses:
        month = datetime.strptime(exp['tanggal'], '%Y-%m-%d').strftime('%B')
        monthly_spending[month] += exp['jumlah']
    
    # Calculate daily average
    unique_days = len(set(exp['tanggal'] for exp in expenses))
    daily_avg = total_spent / unique_days if unique_days > 0 else 0
    
    # Prepare response
    return jsonify({
        'status': 'success',
        'data': {
            'total_spent': total_spent,
            'daily_avg': daily_avg,
            'category_spending': dict(category_spending),
            'weekly_spending': dict(weekly_spending),
            'monthly_spending': dict(monthly_spending),
            'expense_count': len(expenses)
        }
    })

@analytics_bp.route('/api/analytics/expense-trend')
def get_expense_trend():
    """API endpoint for expense trend data"""
    expenses = load_sample_data()
    
    # Group expenses by date
    daily_expenses = defaultdict(list)
    for exp in expenses:
        daily_expenses[exp['tanggal']].append(exp['jumlah'])
    
    # Calculate daily totals
    trend_data = []
    for date, amounts in sorted(daily_expenses.items(), key=lambda x: x[0]):
        trend_data.append({
            'date': date,
            'total': sum(amounts),
            'count': len(amounts)
        })
    
    return jsonify({
        'status': 'success',
        'data': trend_data
    })

@analytics_bp.route('/api/analytics/category-trend')
def get_category_trend():
    """API endpoint for category trend data"""
    expenses = load_sample_data()
    
    # Group by week and category
    weekly_category = defaultdict(lambda: defaultdict(int))
    for exp in expenses:
        date = datetime.strptime(exp['tanggal'], '%Y-%m-%d')
        week_num = date.isocalendar()[1]
        weekly_category[f"Week {week_num}"][exp['kategori']] += exp['jumlah']
    
    # Prepare data for chart
    categories = sorted(set(exp['kategori'] for exp in expenses))
    weeks = sorted(weekly_category.keys())
    
    series_data = []
    for category in categories:
        series_data.append({
            'name': category,
            'data': [weekly_category[week].get(category, 0) for week in weeks]
        })
    
    return jsonify({
        'status': 'success',
        'data': {
            'weeks': weeks,
            'series': series_data
        }
    })

