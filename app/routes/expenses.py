from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for, current_app, Response
import os
import pandas as pd
from werkzeug.utils import secure_filename
from datetime import datetime

expenses_bp = Blueprint('expenses', __name__)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}

# Helper function to read expenses from CSV
def read_expenses():
    file_path = current_app.config['EXPENSE_FILE']
    if not os.path.exists(file_path):
        return []
    
    try:
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    except Exception as e:
        current_app.logger.error(f"Error reading expenses: {str(e)}")
        return []

# Helper function to save expenses to CSV
def save_expenses(expenses):
    file_path = current_app.config['EXPENSE_FILE']
    try:
        df = pd.DataFrame(expenses)
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        current_app.logger.error(f"Error saving expenses: {str(e)}")
        return False

@expenses_bp.route('/expenses')
def expenses():
    return render_template('expenses.html')

@expenses_bp.route('/api/expenses', methods=['GET'])
def get_expenses():
    try:
        expenses = read_expenses()
        return jsonify({'status': 'success', 'data': expenses})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@expenses_bp.route('/api/expenses', methods=['POST'])
def add_expense():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not all(k in data for k in ['jumlah', 'kategori', 'tanggal']):
            return jsonify({'status': 'error', 'message': 'Data tidak lengkap'}), 400
            
        # Create new expense
        new_expense = {
            'nama': data.get('nama', ''),
            'jumlah': float(data['jumlah']),
            'kategori': data['kategori'],
            'tanggal': data['tanggal']
        }
        
        # Read existing expenses
        expenses = read_expenses()
        expenses.append(new_expense)
        
        # Save back to file
        if save_expenses(expenses):
            return jsonify({'status': 'success', 'data': new_expense})
        else:
            return jsonify({'status': 'error', 'message': 'Gagal menyimpan pengeluaran'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@expenses_bp.route('/api/expenses/<int:index>', methods=['PUT'])
def update_expense(index):
    try:
        data = request.get_json()
        expenses = read_expenses()
        
        if index < 0 or index >= len(expenses):
            return jsonify({'status': 'error', 'message': 'Indeks tidak valid'}), 400
            
        # Update expense
        expenses[index] = {
            'nama': data.get('nama', expenses[index]['nama']),
            'jumlah': float(data.get('jumlah', expenses[index]['jumlah'])),
            'kategori': data.get('kategori', expenses[index]['kategori']),
            'tanggal': data.get('tanggal', expenses[index]['tanggal'])
        }
        
        # Save back to file
        if save_expenses(expenses):
            return jsonify({'status': 'success', 'data': expenses[index]})
        else:
            return jsonify({'status': 'error', 'message': 'Gagal memperbarui pengeluaran'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@expenses_bp.route('/api/expenses/<int:index>', methods=['DELETE'])
def delete_expense(index):
    try:
        expenses = read_expenses()
        
        if index < 0 or index >= len(expenses):
            return jsonify({'status': 'error', 'message': 'Indeks tidak valid'}), 400
            
        # Remove expense
        deleted_expense = expenses.pop(index)
        
        # Save back to file
        if save_expenses(expenses):
            return jsonify({'status': 'success', 'data': deleted_expense})
        else:
            return jsonify({'status': 'error', 'message': 'Gagal menghapus pengeluaran'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@expenses_bp.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        flash('Tidak ada file yang dipilih')
        return redirect(url_for('expenses.expenses'))
    
    file = request.files['file']
    if file.filename == '':
        flash('Tidak ada file yang dipilih')
        return redirect(url_for('expenses.expenses'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(temp_path)
        
        try:
            # Read uploaded CSV
            df = pd.read_csv(temp_path)
            
            # Validate required columns
            required_cols = {'nama', 'jumlah', 'kategori', 'tanggal'}
            if not required_cols.issubset(df.columns):
                flash('File CSV harus memiliki kolom: nama, jumlah, kategori, tanggal')
                return redirect(url_for('expenses.expenses'))
            
            # Convert to proper data types
            df['jumlah'] = pd.to_numeric(df['jumlah'], errors='coerce')
            df = df.dropna(subset=['jumlah', 'kategori', 'tanggal'])
            
            # Read existing expenses
            existing_expenses = read_expenses()
            
            # Combine with new expenses
            combined_expenses = existing_expenses + df.to_dict('records')
            
            # Save back to file
            if save_expenses(combined_expenses):
                flash('File CSV berhasil diupload!')
                return redirect(url_for('expenses.expenses'))
            else:
                flash('Gagal menyimpan data pengeluaran')
                return redirect(url_for('expenses.expenses'))
                
        except Exception as e:
            flash(f'Error memproses file: {str(e)}')
            return redirect(url_for('expenses.expenses'))
            
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        flash('Format file tidak didukung. Harus CSV')
        return redirect(url_for('expenses.expenses'))

@expenses_bp.route('/download-template')
def download_template():
    csv_data = "nama,jumlah,kategori,tanggal\nMakan Siang,25000,makanan," + datetime.now().strftime('%Y-%m-%d') + "\nTransportasi,10000,transportasi," + datetime.now().strftime('%Y-%m-%d')
    response = Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=template_pengeluaran.csv"}
    )
    return response