import os
from werkzeug.utils import secure_filename
from flask import current_app, flash
import pandas as pd

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_uploaded_file(file):
    """Save uploaded file to the upload folder"""
    if not file or file.filename == '':
        flash('No file selected')
        return None
    
    if not allowed_file(file.filename):
        flash('File type not allowed')
        return None
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    except Exception as e:
        flash(f'Error saving file: {str(e)}')
        return None

def validate_expense_file(filepath):
    """Validate the structure of expense CSV file"""
    try:
        df = pd.read_csv(filepath)
        required_columns = {'nama', 'jumlah', 'kategori', 'tanggal'}
        
        if not required_columns.issubset(df.columns):
            return False, "CSV file must contain columns: nama, jumlah, kategori, tanggal"
            
        # Check for empty values in required columns
        if df[['jumlah', 'kategori', 'tanggal']].isnull().any().any():
            return False, "Required columns cannot contain empty values"
            
        return True, df
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def append_to_expense_file(df):
    """Append new expenses to the main expense file"""
    try:
        # Read existing data if file exists
        if os.path.exists(current_app.config['EXPENSE_FILE']):
            existing_df = pd.read_csv(current_app.config['EXPENSE_FILE'])
            combined_df = pd.concat([existing_df, df], ignore_index=True)
        else:
            combined_df = df
            
        # Save to CSV
        combined_df.to_csv(current_app.config['EXPENSE_FILE'], index=False)
        return True
    except Exception as e:
        current_app.logger.error(f"Error appending to expense file: {str(e)}")
        return False

def cleanup_temp_file(filepath):
    """Remove temporary file"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        current_app.logger.error(f"Error removing temp file: {str(e)}")