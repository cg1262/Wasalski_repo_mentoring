from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Add current date context to templates
@app.context_processor
def inject_current_date():
    now = datetime.now()
    return dict(current_year=now.year, current_month=now.month)

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
    
    # Lease installments table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS leases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            total_installments INTEGER NOT NULL,
            installments_paid INTEGER DEFAULT 0,
            installment_amount REAL NOT NULL,
            start_date TEXT NOT NULL,
            next_payment_date TEXT NOT NULL,
            last_payment_date TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Yearly planned expenses
    conn.execute('''
        CREATE TABLE IF NOT EXISTS yearly_planned (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            planned_date TEXT NOT NULL,
            category TEXT,
            is_paid BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Monthly projections with carryover
    conn.execute('''
        CREATE TABLE IF NOT EXISTS monthly_projections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            planned_income REAL DEFAULT 0,
            planned_expenses REAL DEFAULT 0,
            actual_income REAL DEFAULT 0,
            actual_expenses REAL DEFAULT 0,
            carryover_from_previous REAL DEFAULT 0,
            savings_transfer REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, month)
        )
    ''')
    
    # Savings account tracking
    conn.execute('''
        CREATE TABLE IF NOT EXISTS savings_account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            transaction_type TEXT NOT NULL, -- 'deposit' or 'withdrawal'
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
        
        # If category is 'Savings', treat as savings transfer
        if category == 'Savings':
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO savings_account (date, amount, description, transaction_type)
                VALUES (?, ?, ?, ?)
            ''', (date, amount, description, 'deposit'))
            conn.commit()
            conn.close()
            flash('Kwota została przelana na konto oszczędnościowe!', 'success')
            return redirect(url_for('index'))
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

@app.route('/calculate_hourly', methods=['POST'])
def calculate_hourly():
    """API endpoint for real-time hourly calculations"""
    data = request.get_json()
    hours = float(data.get('hours', 0))
    hourly_rate = float(data.get('hourly_rate', 0))
    vat_rate = float(data.get('vat_rate', 23.0))
    tax_rate = float(data.get('tax_rate', 12.0))
    
    gross_amount = hours * hourly_rate
    vat_amount = gross_amount * (vat_rate / 100)
    total_with_vat = gross_amount + vat_amount
    tax_amount = gross_amount * (tax_rate / 100)
    net_amount = gross_amount - tax_amount
    
    return jsonify({
        'gross_amount': gross_amount,
        'vat_amount': vat_amount,
        'total_with_vat': total_with_vat,
        'tax_amount': tax_amount,
        'net_amount': net_amount,
        'hours': hours,
        'hourly_rate': hourly_rate,
        'vat_rate': vat_rate,
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

# Lease management routes
@app.route('/leases')
def leases():
    conn = get_db_connection()
    leases = conn.execute('''
        SELECT *, 
               (total_installments - installments_paid) as remaining_installments,
               ((total_installments - installments_paid) * installment_amount) as remaining_amount
        FROM leases 
        ORDER BY next_payment_date
    ''').fetchall()
    
    # Calculate total monthly lease payments
    total_monthly = conn.execute('''
        SELECT SUM(installment_amount) as total 
        FROM leases 
        WHERE installments_paid < total_installments
    ''').fetchone()['total'] or 0
    
    conn.close()
    return render_template('leases.html', leases=leases, total_monthly=total_monthly)

@app.route('/add_lease', methods=['GET', 'POST'])
def add_lease():
    if request.method == 'POST':
        description = request.form['description']
        total_installments = int(request.form['total_installments'])
        installment_amount = float(request.form['installment_amount'])
        start_date = request.form['start_date']
        
        # Calculate last payment date
        start = datetime.strptime(start_date, '%Y-%m-%d')
        last_payment = start + timedelta(days=30 * (total_installments-1))
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO leases (description, total_installments, installment_amount, 
                              start_date, next_payment_date, last_payment_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (description, total_installments, installment_amount, 
              start_date, start_date, last_payment.strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        
        flash('Rata została dodana pomyślnie!', 'success')
        return redirect(url_for('leases'))
    
    return render_template('add_lease.html')

@app.route('/pay_lease/<int:id>')
def pay_lease(id):
    conn = get_db_connection()
    lease = conn.execute('SELECT * FROM leases WHERE id = ?', (id,)).fetchone()
    
    if lease and lease['installments_paid'] < lease['total_installments']:
        new_installments_paid = lease['installments_paid'] + 1
        
        # Calculate next payment date
        current_date = datetime.strptime(lease['next_payment_date'], '%Y-%m-%d')
        next_date = current_date + timedelta(days=30)
        
        conn.execute('''
            UPDATE leases 
            SET installments_paid = ?, next_payment_date = ? 
            WHERE id = ?
        ''', (new_installments_paid, next_date.strftime('%Y-%m-%d'), id))
        
        # Add to expenses
        conn.execute('''
            INSERT INTO expenses (description, amount, category, date)
            VALUES (?, ?, ?, ?)
        ''', (f"Rata: {lease['description']}", lease['installment_amount'], 'Raty', 
              lease['next_payment_date']))
        
        conn.commit()
        flash('Rata została opłacona!', 'success')
    
    conn.close()
    return redirect(url_for('leases'))

# Yearly planned expenses
@app.route('/yearly_planned')
def yearly_planned():
    conn = get_db_connection()
    planned = conn.execute('''
        SELECT * FROM yearly_planned 
        ORDER BY planned_date
    ''').fetchall()
    conn.close()
    return render_template('yearly_planned.html', planned=planned)

@app.route('/add_yearly_planned', methods=['GET', 'POST'])
def add_yearly_planned():
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        planned_date = request.form['planned_date']
        category = request.form.get('category', '')
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO yearly_planned (description, amount, planned_date, category)
            VALUES (?, ?, ?, ?)
        ''', (description, amount, planned_date, category))
        conn.commit()
        conn.close()
        
        flash('Planowany wydatek został dodany!', 'success')
        return redirect(url_for('yearly_planned'))
    
    return render_template('add_yearly_planned.html')

@app.route('/mark_yearly_paid/<int:id>')
def mark_yearly_paid(id):
    conn = get_db_connection()
    planned = conn.execute('SELECT * FROM yearly_planned WHERE id = ?', (id,)).fetchone()
    
    if planned:
        # Add to expenses
        conn.execute('''
            INSERT INTO expenses (description, amount, category, date)
            VALUES (?, ?, ?, ?)
        ''', (planned['description'], planned['amount'], 
              planned['category'] or 'Planowane', planned['planned_date']))
        
        # Mark as paid
        conn.execute('UPDATE yearly_planned SET is_paid = 1 WHERE id = ?', (id,))
        conn.commit()
        flash('Wydatek został oznaczony jako opłacony!', 'success')
    
    conn.close()
    return redirect(url_for('yearly_planned'))

# Monthly projections and savings
@app.route('/projections')
def projections():
    conn = get_db_connection()
    
    # Get or create projections for next 12 months
    current_date = datetime.now()
    projections = []
    
    for i in range(12):
        month_date = current_date.replace(day=1) + timedelta(days=32*i)
        month_date = month_date.replace(day=1)
        year = month_date.year
        month = month_date.month
        
        projection = conn.execute('''
            SELECT * FROM monthly_projections WHERE year = ? AND month = ?
        ''', (year, month)).fetchone()
        
        # Calculate automatic expenses for this month
        month_start = f"{year}-{month:02d}-01"
        if month == 12:
            next_month_start = f"{year+1}-01-01"
        else:
            next_month_start = f"{year}-{month+1:02d}-01"
        
        # Get lease installments for this month
        # Calculate which leases will still be active in this month
        lease_expenses = 0
        leases = conn.execute('''
            SELECT * FROM leases 
            WHERE installments_paid < total_installments
        ''').fetchall()
        
        for lease in leases:
            # Calculate how many months from start_date to the projection month
            start_date = datetime.strptime(lease['start_date'], '%Y-%m-%d')
            projection_date = datetime(year, month, 1)
            
            months_diff = (projection_date.year - start_date.year) * 12 + (projection_date.month - start_date.month)
            
            # If this lease should still have payments in this month
            if months_diff >= lease['installments_paid'] and months_diff < lease['total_installments']:
                lease_expenses += lease['installment_amount']
        
        # Get yearly planned expenses for this month
        yearly_expenses = conn.execute('''
            SELECT SUM(amount) as total
            FROM yearly_planned 
            WHERE is_paid = 0
            AND planned_date >= ? AND planned_date < ?
        ''', (month_start, next_month_start)).fetchone()['total'] or 0
        
        # Total automatic expenses
        automatic_expenses = lease_expenses + yearly_expenses
        
        if not projection:
            # Create default projection with automatic expenses
            conn.execute('''
                INSERT INTO monthly_projections (year, month, planned_income, planned_expenses)
                VALUES (?, ?, ?, ?)
            ''', (year, month, 0, automatic_expenses))
            conn.commit()
            projection = conn.execute('''
                SELECT * FROM monthly_projections WHERE year = ? AND month = ?
            ''', (year, month)).fetchone()
        else:
            # Update existing projection to include automatic expenses if not manually set
            if projection['planned_expenses'] == 0:
                conn.execute('''
                    UPDATE monthly_projections 
                    SET planned_expenses = ?
                    WHERE year = ? AND month = ?
                ''', (automatic_expenses, year, month))
                conn.commit()
                projection = conn.execute('''
                    SELECT * FROM monthly_projections WHERE year = ? AND month = ?
                ''', (year, month)).fetchone()
        
        # Calculate carryover and available balance
        if i == 0:
            carryover = 0
        else:
            prev_projection = projections[-1] if projections else None
            if prev_projection:
                carryover = (prev_projection['planned_income'] + prev_projection['carryover_from_previous'] - 
                           prev_projection['planned_expenses'] - prev_projection['savings_transfer'])
            else:
                carryover = 0
        
        projection_dict = dict(projection)
        projection_dict['carryover_from_previous'] = carryover
        projection_dict['lease_expenses'] = lease_expenses
        projection_dict['yearly_expenses'] = yearly_expenses
        projection_dict['automatic_expenses'] = automatic_expenses
        month_names = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 
                       'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
        projection_dict['month_name'] = month_names[month]
        projection_dict['available_balance'] = (projection['planned_income'] + carryover - 
                                              projection['planned_expenses'] - (projection['savings_transfer'] or 0))
        
        projections.append(projection_dict)
    
    # Get savings account balance
    savings_balance = conn.execute('''
        SELECT COALESCE(SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE -amount END), 0) as balance
        FROM savings_account
    ''').fetchone()['balance']
    
    conn.close()
    return render_template('projections.html', projections=projections, savings_balance=savings_balance)

@app.route('/refresh_automatic_expenses', methods=['POST'])
def refresh_automatic_expenses():
    """Recalculate automatic expenses for all months"""
    conn = get_db_connection()
    
    # Delete all existing projections to force recalculation
    conn.execute('DELETE FROM monthly_projections')
    conn.commit()
    conn.close()
    
    flash('Automatyczne wydatki zostały przeliczone ponownie!', 'success')
    return redirect(url_for('projections'))

@app.route('/update_projection/<int:year>/<int:month>', methods=['POST'])
def update_projection(year, month):
    planned_income = float(request.form.get('planned_income', 0))
    planned_expenses = float(request.form.get('planned_expenses', 0))
    savings_transfer = float(request.form.get('savings_transfer', 0))
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE monthly_projections 
        SET planned_income = ?, planned_expenses = ?, savings_transfer = ?
        WHERE year = ? AND month = ?
    ''', (planned_income, planned_expenses, savings_transfer, year, month))
    
    # If savings transfer, add to savings account
    if savings_transfer > 0:
        date_str = f"{year}-{month:02d}-01"
        month_names = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 
                       'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
        conn.execute('''
            INSERT INTO savings_account (date, amount, description, transaction_type)
            VALUES (?, ?, ?, ?)
        ''', (date_str, savings_transfer, f"Transfer from {month_names[month]} {year}", 'deposit'))
    
    conn.commit()
    conn.close()
    
    flash('Projekcja została zaktualizowana!', 'success')
    return redirect(url_for('projections'))

@app.route('/savings')
def savings():
    conn = get_db_connection()
    
    transactions = conn.execute('''
        SELECT * FROM savings_account ORDER BY date DESC
    ''').fetchall()
    
    balance = conn.execute('''
        SELECT COALESCE(SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE -amount END), 0) as balance
        FROM savings_account
    ''').fetchone()['balance']
    
    conn.close()
    return render_template('savings.html', transactions=transactions, balance=balance)

# Monthly detailed views
@app.route('/month/<int:year>/<int:month>')
def month_detail(year, month):
    conn = get_db_connection()
    
    # Date range for the month
    month_start = f"{year}-{month:02d}-01"
    if month == 12:
        next_month_start = f"{year+1}-01-01"
    else:
        next_month_start = f"{year}-{month+1:02d}-01"
    
    # Get actual income and expenses for this month
    actual_income = conn.execute('''
        SELECT *, 'actual' as source FROM income 
        WHERE date >= ? AND date < ?
        ORDER BY date
    ''', (month_start, next_month_start)).fetchall()
    
    actual_expenses = conn.execute('''
        SELECT *, 'actual' as source FROM expenses 
        WHERE date >= ? AND date < ?
        ORDER BY date
    ''', (month_start, next_month_start)).fetchall()
    
    # Get planned expenses from leases for this month
    planned_lease_expenses = []
    leases = conn.execute('''
        SELECT * FROM leases 
        WHERE installments_paid < total_installments
    ''').fetchall()
    
    for lease in leases:
        start_date = datetime.strptime(lease['start_date'], '%Y-%m-%d')
        projection_date = datetime(year, month, 1)
        months_diff = (projection_date.year - start_date.year) * 12 + (projection_date.month - start_date.month)
        
        if months_diff >= lease['installments_paid'] and months_diff < lease['total_installments']:
            planned_lease_expenses.append({
                'id': lease['id'],
                'description': f"Rata: {lease['description']}",
                'amount': lease['installment_amount'],
                'category': 'Raty',
                'date': f"{year}-{month:02d}-15",  # Mid-month for display
                'source': 'lease',
                'lease_id': lease['id']
            })
    
    # Get planned yearly expenses for this month
    planned_yearly_expenses = conn.execute('''
        SELECT *, 'yearly_planned' as source FROM yearly_planned 
        WHERE is_paid = 0
        AND planned_date >= ? AND planned_date < ?
        ORDER BY planned_date
    ''', (month_start, next_month_start)).fetchall()
    
    # Get month projection data
    projection = conn.execute('''
        SELECT * FROM monthly_projections WHERE year = ? AND month = ?
    ''', (year, month)).fetchone()
    
    # Calculate previous month carryover
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    
    prev_projection = conn.execute('''
        SELECT * FROM monthly_projections WHERE year = ? AND month = ?
    ''', (prev_year, prev_month)).fetchone()
    
    carryover = 0
    if prev_projection:
        carryover = (prev_projection['planned_income'] - prev_projection['planned_expenses'] - 
                    (prev_projection['savings_transfer'] or 0))
    
    # Calculate totals
    total_actual_income = sum(float(item['amount']) for item in actual_income)
    total_actual_expenses = sum(float(item['amount']) for item in actual_expenses)
    total_planned_lease = sum(float(item['amount']) for item in planned_lease_expenses)
    total_planned_yearly = sum(float(item['amount']) for item in planned_yearly_expenses)
    
    month_names = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 
                   'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
    
    conn.close()
    
    return render_template('month_detail.html', 
                         year=year, 
                         month=month,
                         month_name=month_names[month],
                         actual_income=actual_income,
                         actual_expenses=actual_expenses,
                         planned_lease_expenses=planned_lease_expenses,
                         planned_yearly_expenses=planned_yearly_expenses,
                         projection=projection,
                         carryover=carryover,
                         total_actual_income=total_actual_income,
                         total_actual_expenses=total_actual_expenses,
                         total_planned_lease=total_planned_lease,
                         total_planned_yearly=total_planned_yearly)

@app.route('/month/<int:year>/<int:month>/add_income', methods=['GET', 'POST'])
def add_month_income(year, month):
    if request.method == 'POST':
        description = request.form['description']
        date = request.form['date']
        
        conn = get_db_connection()
        
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
            
            conn.execute('''
                INSERT INTO income (description, amount, date, hours, hourly_rate, vat_rate, tax_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (description, total_with_vat, date, hours, hourly_rate, vat_rate, tax_rate))
            
        else:
            amount = float(request.form['amount'])
            tax_rate = float(request.form.get('tax_rate', 12.0))
            
            conn.execute('''
                INSERT INTO income (description, amount, date, tax_rate)
                VALUES (?, ?, ?, ?)
            ''', (description, amount, date, tax_rate))
        
        conn.commit()
        conn.close()
        
        flash('Przychód został dodany!', 'success')
        return redirect(url_for('month_detail', year=year, month=month))
    
    # Pre-fill date with current month
    default_date = f"{year}-{month:02d}-01"
    month_names = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 
                   'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
    
    return render_template('add_month_income.html', 
                         year=year, 
                         month=month, 
                         month_name=month_names[month],
                         default_date=default_date)

@app.route('/month/<int:year>/<int:month>/add_expense', methods=['GET', 'POST'])
def add_month_expense(year, month):
    if request.method == 'POST':
        description = request.form['description']
        amount = float(request.form['amount'])
        category = request.form['category']
        date = request.form['date']
        
        conn = get_db_connection()
        
        # If category is 'Savings', treat as savings transfer
        if category == 'Savings':
            conn.execute('''
                INSERT INTO savings_account (date, amount, description, transaction_type)
                VALUES (?, ?, ?, ?)
            ''', (date, amount, description, 'deposit'))
        else:
            conn.execute('''
                INSERT INTO expenses (description, amount, category, date)
                VALUES (?, ?, ?, ?)
            ''', (description, amount, category, date))
        
        conn.commit()
        conn.close()
        
        if category == 'Savings':
            flash('Kwota została przelana na konto oszczędnościowe!', 'success')
        else:
            flash('Wydatek został dodany!', 'success')
            
        return redirect(url_for('month_detail', year=year, month=month))
    
    # Pre-fill date with current month
    default_date = f"{year}-{month:02d}-01"
    month_names = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec', 
                   'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
    
    return render_template('add_month_expense.html', 
                         year=year, 
                         month=month, 
                         month_name=month_names[month],
                         default_date=default_date)

@app.route('/pay_lease_from_month/<int:lease_id>/<int:year>/<int:month>')
def pay_lease_from_month(lease_id, year, month):
    conn = get_db_connection()
    lease = conn.execute('SELECT * FROM leases WHERE id = ?', (lease_id,)).fetchone()
    
    if lease and lease['installments_paid'] < lease['total_installments']:
        new_installments_paid = lease['installments_paid'] + 1
        
        # Calculate next payment date
        current_date = datetime.strptime(lease['next_payment_date'], '%Y-%m-%d')
        next_date = current_date + timedelta(days=30)
        
        conn.execute('''
            UPDATE leases 
            SET installments_paid = ?, next_payment_date = ? 
            WHERE id = ?
        ''', (new_installments_paid, next_date.strftime('%Y-%m-%d'), lease_id))
        
        # Add to expenses for this month
        payment_date = f"{year}-{month:02d}-15"  # Mid-month
        conn.execute('''
            INSERT INTO expenses (description, amount, category, date)
            VALUES (?, ?, ?, ?)
        ''', (f"Rata: {lease['description']}", lease['installment_amount'], 'Raty', payment_date))
        
        conn.commit()
        flash('Rata została opłacona!', 'success')
    
    conn.close()
    return redirect(url_for('month_detail', year=year, month=month))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=9876)