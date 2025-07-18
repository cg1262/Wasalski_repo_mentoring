from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

DATABASE = 'finance_tracker.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            date TEXT NOT NULL,
            is_recurring BOOLEAN DEFAULT 0,
            recurring_months INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            hours REAL,
            hourly_rate REAL,
            vat_rate REAL DEFAULT 23.0,
            tax_rate REAL DEFAULT 12.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS recurring_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_id INTEGER,
            transaction_type TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT,
            date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    
    # Pobierz wszystkie wydatki
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    
    # Pobierz wszystkie przychody
    income = conn.execute('SELECT * FROM income ORDER BY date DESC').fetchall()
    
    # Pobierz powtarzalne transakcje
    recurring = conn.execute('SELECT * FROM recurring_transactions ORDER BY date DESC').fetchall()
    
    conn.close()
    
    return render_template('index.html', expenses=expenses, income=income, recurring=recurring)

@app.route('/add_expense', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        is_recurring = 'is_recurring' in request.form
        recurring_months = int(request.form.get('recurring_months', 1))
        
        conn = get_db_connection()
        
        # Dodaj główny wydatek
        cursor = conn.execute('''
            INSERT INTO expenses (description, amount, category, date, is_recurring, recurring_months)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (description, amount, category, date, is_recurring, recurring_months))
        
        parent_id = cursor.lastrowid
        
        # Jeśli wydatek jest powtarzalny, stwórz kolejne wpisy
        if is_recurring and recurring_months > 1:
            base_date = datetime.strptime(date, '%Y-%m-%d')
            for i in range(1, recurring_months):
                next_date = base_date + timedelta(days=30 * i)  # Przybliżony miesiąc
                next_date_str = next_date.strftime('%Y-%m-%d')
                
                conn.execute('''
                    INSERT INTO recurring_transactions (parent_id, transaction_type, description, amount, category, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (parent_id, 'expense', description, amount, category, next_date_str))
        
        conn.commit()
        conn.close()
        
        flash('Wydatek został dodany pomyślnie!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_expense.html')

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if request.method == 'POST':
        description = request.form['description']
        date = request.form['date']
        
        # Sprawdź czy to przychód z godzin
        if 'hours' in request.form and request.form['hours']:
            hours = float(request.form['hours'])
            hourly_rate = float(request.form['hourly_rate'])
            vat_rate = float(request.form.get('vat_rate', 23.0))
            tax_rate = float(request.form.get('tax_rate', 12.0))
            
            # Oblicz kwotę brutto
            gross_amount = hours * hourly_rate
            vat_amount = gross_amount * (vat_rate / 100)
            total_with_vat = gross_amount + vat_amount
            
            # Oblicz podatek
            tax_amount = gross_amount * (tax_rate / 100)
            net_amount = gross_amount - tax_amount
            
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO income (description, amount, date, hours, hourly_rate, vat_rate, tax_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (description, total_with_vat, date, hours, hourly_rate, vat_rate, tax_rate))
            
        else:
            amount = float(request.form['amount'])
            tax_rate = float(request.form.get('tax_rate', 12.0))
            
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO income (description, amount, date, tax_rate)
                VALUES (?, ?, ?, ?)
            ''', (description, amount, date, tax_rate))
        
        conn.commit()
        conn.close()
        
        flash('Przychód został dodany pomyślnie!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_income.html')

@app.route('/calculate_tax', methods=['POST'])
def calculate_tax():
    data = request.get_json()
    gross_amount = float(data['amount'])
    tax_rate = float(data.get('tax_rate', 12.0))
    
    tax_amount = gross_amount * (tax_rate / 100)
    net_amount = gross_amount - tax_amount
    
    return jsonify({
        'gross_amount': gross_amount,
        'tax_amount': tax_amount,
        'net_amount': net_amount,
        'tax_rate': tax_rate
    })

@app.route('/summary')
def summary():
    conn = get_db_connection()
    
    # Suma wydatków
    total_expenses = conn.execute('SELECT SUM(amount) as total FROM expenses').fetchone()['total'] or 0
    recurring_expenses = conn.execute('SELECT SUM(amount) as total FROM recurring_transactions WHERE transaction_type = "expense"').fetchone()['total'] or 0
    
    # Suma przychodów
    total_income = conn.execute('SELECT SUM(amount) as total FROM income').fetchone()['total'] or 0
    
    # Suma podatków
    total_tax = conn.execute('SELECT SUM(amount * tax_rate / 100) as total FROM income').fetchone()['total'] or 0
    
    conn.close()
    
    total_expenses_all = total_expenses + recurring_expenses
    net_income = total_income - total_tax
    balance = net_income - total_expenses_all
    
    return render_template('summary.html', 
                         total_expenses=total_expenses_all,
                         total_income=total_income,
                         total_tax=total_tax,
                         net_income=net_income,
                         balance=balance)

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.execute('DELETE FROM recurring_transactions WHERE parent_id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Wydatek został usunięty!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_income/<int:id>')
def delete_income(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM income WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Przychód został usunięty!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)