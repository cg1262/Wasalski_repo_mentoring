from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime, timedelta
import os
import calendar

app = Flask(__name__)
app.secret_key = 'excel-finance-tracker-secret-key'

# Add current date context to templates
@app.context_processor
def inject_current_date():
    now = datetime.now()
    return dict(current_year=now.year, current_month=now.month)

DATABASE = 'finance_tracker_excel.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Main control panel settings
    conn.execute('''
        CREATE TABLE IF NOT EXISTS control_panel (
            id INTEGER PRIMARY KEY,
            monthly_income_net REAL DEFAULT 0,
            monthly_hours REAL DEFAULT 180,
            hourly_rate REAL DEFAULT 140,
            vat_rate REAL DEFAULT 23.0,
            rent_cost REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Monthly financial data - each month as separate record
    conn.execute('''
        CREATE TABLE IF NOT EXISTS monthly_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            przeniesienie_z_poprzedniego REAL DEFAULT 0,
            przychod_netto REAL DEFAULT 0,
            wydatki_razem REAL DEFAULT 0,
            zostaje_na_nastepny REAL DEFAULT 0,
            konto_oszczednosciowe REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(year, month)
        )
    ''')
    
    # Expense categories with colors like Excel
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expense_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color_code TEXT DEFAULT 'default',
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Monthly expenses - detailed breakdown
    conn.execute('''
        CREATE TABLE IF NOT EXISTS monthly_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL,
            month INTEGER NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            is_planned BOOLEAN DEFAULT 0,
            is_recurring BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Lease tracking (like Excel leasing section)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS leasing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            monthly_amount REAL NOT NULL,
            total_months INTEGER NOT NULL,
            months_paid INTEGER DEFAULT 0,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Yearly planned expenses (Planowane rocznie wydatki)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS yearly_planned_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            planned_month INTEGER NOT NULL,
            planned_year INTEGER NOT NULL,
            is_paid BOOLEAN DEFAULT 0,
            actual_payment_date TEXT,
            category TEXT DEFAULT 'Planowane',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Savings account transactions
    conn.execute('''
        CREATE TABLE IF NOT EXISTS savings_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL, -- 'deposit' or 'withdrawal'
            description TEXT NOT NULL,
            month_source TEXT, -- which month this transfer came from
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert default control panel if not exists
    existing = conn.execute('SELECT COUNT(*) as count FROM control_panel').fetchone()
    if existing['count'] == 0:
        conn.execute('''
            INSERT INTO control_panel (monthly_income_net, monthly_hours, hourly_rate, vat_rate, rent_cost)
            VALUES (43673.21, 180, 140, 23.0, 0)
        ''')
    
    # Insert default expense categories with Excel-like colors
    categories = [
        ('Leasing', 'red', 1),
        ('Żywność', 'orange', 2),
        ('Transport', 'orange', 3),
        ('Rozrywka', 'orange', 4),
        ('Leki', 'orange', 5),
        ('Dom', 'orange', 6),
        ('VAT', 'yellow', 7),
        ('Inne', 'gray', 8)
    ]
    
    for name, color, order in categories:
        conn.execute('''
            INSERT OR IGNORE INTO expense_categories (name, color_code, sort_order)
            VALUES (?, ?, ?)
        ''', (name, color, order))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """Main dashboard - Excel-like overview"""
    conn = get_db_connection()
    
    # Get control panel data
    control_panel = conn.execute('SELECT * FROM control_panel ORDER BY id DESC LIMIT 1').fetchone()
    
    # Get current month data
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    current_month_data = conn.execute('''
        SELECT * FROM monthly_data WHERE year = ? AND month = ?
    ''', (current_year, current_month)).fetchone()
    
    # Get monthly expenses for current month by category
    monthly_expenses = conn.execute('''
        SELECT category, SUM(amount) as total_amount, COUNT(*) as count
        FROM monthly_expenses 
        WHERE year = ? AND month = ?
        GROUP BY category
        ORDER BY category
    ''', (current_year, current_month)).fetchall()
    
    # Get active leasing
    active_leasing = conn.execute('''
        SELECT * FROM leasing WHERE is_active = 1 ORDER BY description
    ''').fetchall()
    
    # Get upcoming yearly planned expenses
    upcoming_planned = conn.execute('''
        SELECT * FROM yearly_planned_expenses 
        WHERE is_paid = 0 AND planned_year >= ? 
        ORDER BY planned_year, planned_month
        LIMIT 10
    ''', (current_year,)).fetchall()
    
    # Calculate totals
    total_leasing = sum(lease['monthly_amount'] for lease in active_leasing)
    total_monthly_expenses = sum(exp['total_amount'] for exp in monthly_expenses)
    
    # Calculate Excel-like values
    if control_panel:
        przychod_brutto = control_panel['monthly_hours'] * control_panel['hourly_rate']
        vat_amount = przychod_brutto * (control_panel['vat_rate'] / 100)
        przychod_z_vat = przychod_brutto + vat_amount
        
        # Calculate pozostaje (what's left)
        wydatek_na_reke = total_monthly_expenses + total_leasing
        zostaje = control_panel['monthly_income_net'] - wydatek_na_reke
    else:
        przychod_brutto = przychod_z_vat = vat_amount = 0
        wydatek_na_reke = zostaje = 0
    
    conn.close()
    
    return render_template('index.html',
                         control_panel=control_panel,
                         current_month_data=current_month_data,
                         monthly_expenses=monthly_expenses,
                         active_leasing=active_leasing,
                         upcoming_planned=upcoming_planned,
                         przychod_brutto=przychod_brutto,
                         przychod_z_vat=przychod_z_vat,
                         vat_amount=vat_amount,
                         total_leasing=total_leasing,
                         total_monthly_expenses=total_monthly_expenses,
                         wydatek_na_reke=wydatek_na_reke,
                         zostaje=zostaje,
                         current_year=current_year,
                         current_month=current_month)

@app.route('/control_panel', methods=['GET', 'POST'])
def control_panel():
    """Excel-like control panel for main settings"""
    if request.method == 'POST':
        monthly_income_net = float(request.form['monthly_income_net'])
        monthly_hours = float(request.form['monthly_hours'])
        hourly_rate = float(request.form['hourly_rate'])
        vat_rate = float(request.form['vat_rate'])
        rent_cost = float(request.form['rent_cost'])
        
        conn = get_db_connection()
        
        # Update or insert control panel data
        existing = conn.execute('SELECT id FROM control_panel LIMIT 1').fetchone()
        if existing:
            conn.execute('''
                UPDATE control_panel 
                SET monthly_income_net = ?, monthly_hours = ?, hourly_rate = ?, 
                    vat_rate = ?, rent_cost = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (monthly_income_net, monthly_hours, hourly_rate, vat_rate, rent_cost, existing['id']))
        else:
            conn.execute('''
                INSERT INTO control_panel (monthly_income_net, monthly_hours, hourly_rate, vat_rate, rent_cost)
                VALUES (?, ?, ?, ?, ?)
            ''', (monthly_income_net, monthly_hours, hourly_rate, vat_rate, rent_cost))
        
        conn.commit()
        conn.close()
        
        flash('Panel kontrolny został zaktualizowany!', 'success')
        return redirect(url_for('index'))
    
    # GET request
    conn = get_db_connection()
    control_data = conn.execute('SELECT * FROM control_panel ORDER BY id DESC LIMIT 1').fetchone()
    conn.close()
    
    return render_template('control_panel.html', control_data=control_data)

@app.route('/month/<int:year>/<int:month>')
def month_detail(year, month):
    """Excel-like monthly sheet view"""
    conn = get_db_connection()
    
    # Get or create monthly data
    month_data = conn.execute('''
        SELECT * FROM monthly_data WHERE year = ? AND month = ?
    ''', (year, month)).fetchone()
    
    if not month_data:
        # Create new month record with carryover from previous month
        if month == 1:
            prev_year, prev_month = year - 1, 12
        else:
            prev_year, prev_month = year, month - 1
            
        prev_month_data = conn.execute('''
            SELECT zostaje_na_nastepny FROM monthly_data WHERE year = ? AND month = ?
        ''', (prev_year, prev_month)).fetchone()
        
        przeniesienie = prev_month_data['zostaje_na_nastepny'] if prev_month_data else 0
        
        conn.execute('''
            INSERT INTO monthly_data (year, month, przeniesienie_z_poprzedniego)
            VALUES (?, ?, ?)
        ''', (year, month, przeniesienie))
        conn.commit()
        
        month_data = conn.execute('''
            SELECT * FROM monthly_data WHERE year = ? AND month = ?
        ''', (year, month)).fetchone()
    
    # Get expenses by category for this month
    expenses_by_category = conn.execute('''
        SELECT 
            ec.name as category_name,
            ec.color_code,
            ec.sort_order,
            COALESCE(SUM(me.amount), 0) as total_amount,
            COUNT(me.id) as expense_count
        FROM expense_categories ec
        LEFT JOIN monthly_expenses me ON ec.name = me.category 
            AND me.year = ? AND me.month = ?
        WHERE ec.is_active = 1
        GROUP BY ec.id, ec.name, ec.color_code, ec.sort_order
        ORDER BY ec.sort_order
    ''', (year, month)).fetchall()
    
    # Get detailed expenses for this month
    detailed_expenses = conn.execute('''
        SELECT * FROM monthly_expenses 
        WHERE year = ? AND month = ?
        ORDER BY category, description
    ''', (year, month)).fetchall()
    
    # Get active leasing for this month
    active_leasing = conn.execute('''
        SELECT * FROM leasing WHERE is_active = 1
    ''').fetchall()
    
    # Get yearly planned expenses for this month
    yearly_planned = conn.execute('''
        SELECT * FROM yearly_planned_expenses 
        WHERE planned_year = ? AND planned_month = ? AND is_paid = 0
    ''', (year, month)).fetchall()
    
    # Calculate month totals
    total_expenses = sum(cat['total_amount'] for cat in expenses_by_category)
    total_leasing = sum(lease['monthly_amount'] for lease in active_leasing if lease['is_active'])
    total_yearly_planned = sum(planned['amount'] for planned in yearly_planned)
    
    month_names = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                   'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
    
    conn.close()
    
    return render_template('month_detail.html',
                         year=year,
                         month=month,
                         month_name=month_names[month],
                         month_data=month_data,
                         expenses_by_category=expenses_by_category,
                         detailed_expenses=detailed_expenses,
                         active_leasing=active_leasing,
                         yearly_planned=yearly_planned,
                         total_expenses=total_expenses,
                         total_leasing=total_leasing,
                         total_yearly_planned=total_yearly_planned)

@app.route('/month/<int:year>/<int:month>/add_expense', methods=['GET', 'POST'])
def add_month_expense(year, month):
    """Add expense to specific month"""
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        amount = float(request.form['amount'])
        is_recurring = 'is_recurring' in request.form
        
        conn = get_db_connection()
        
        # Add expense
        conn.execute('''
            INSERT INTO monthly_expenses (year, month, category, description, amount, is_recurring)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (year, month, category, description, amount, is_recurring))
        
        # If recurring, add to future months
        if is_recurring:
            for i in range(1, 12):  # Add to next 11 months
                future_month = month + i
                future_year = year
                if future_month > 12:
                    future_month -= 12
                    future_year += 1
                
                conn.execute('''
                    INSERT INTO monthly_expenses (year, month, category, description, amount, is_recurring)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (future_year, future_month, category, description, amount, True))
        
        # Update monthly totals
        update_monthly_totals(conn, year, month)
        
        conn.commit()
        conn.close()
        
        flash('Wydatek został dodany!', 'success')
        return redirect(url_for('month_detail', year=year, month=month))
    
    # GET request
    conn = get_db_connection()
    categories = conn.execute('''
        SELECT name FROM expense_categories WHERE is_active = 1 ORDER BY sort_order
    ''').fetchall()
    conn.close()
    
    month_names = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                   'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
    
    return render_template('add_month_expense.html',
                         year=year,
                         month=month,
                         month_name=month_names[month],
                         categories=categories)

def update_monthly_totals(conn, year, month):
    """Update monthly totals like Excel calculations"""
    # Calculate total expenses for this month
    total_expenses = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM monthly_expenses
        WHERE year = ? AND month = ?
    ''', (year, month)).fetchone()['total']
    
    # Get control panel data for income
    control_panel = conn.execute('SELECT * FROM control_panel ORDER BY id DESC LIMIT 1').fetchone()
    przychod_netto = control_panel['monthly_income_net'] if control_panel else 0
    
    # Get carryover
    przeniesienie = conn.execute('''
        SELECT przeniesienie_z_poprzedniego FROM monthly_data WHERE year = ? AND month = ?
    ''', (year, month)).fetchone()
    przeniesienie_amount = przeniesienie['przeniesienie_z_poprzedniego'] if przeniesienie else 0
    
    # Calculate what's left for next month (Excel logic)
    zostaje_na_nastepny = przychod_netto + przeniesienie_amount - total_expenses
    
    # Update monthly data
    conn.execute('''
        UPDATE monthly_data 
        SET wydatki_razem = ?, zostaje_na_nastepny = ?, updated_at = CURRENT_TIMESTAMP
        WHERE year = ? AND month = ?
    ''', (total_expenses, zostaje_na_nastepny, year, month))
    
    # Update next month's carryover
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1
    
    # Create or update next month record
    existing_next = conn.execute('''
        SELECT id FROM monthly_data WHERE year = ? AND month = ?
    ''', (next_year, next_month)).fetchone()
    
    if existing_next:
        conn.execute('''
            UPDATE monthly_data 
            SET przeniesienie_z_poprzedniego = ?
            WHERE year = ? AND month = ?
        ''', (zostaje_na_nastepny, next_year, next_month))
    else:
        conn.execute('''
            INSERT INTO monthly_data (year, month, przeniesienie_z_poprzedniego)
            VALUES (?, ?, ?)
        ''', (next_year, next_month, zostaje_na_nastepny))

@app.route('/leasing')
def leasing():
    """Manage leasing like Excel leasing section"""
    conn = get_db_connection()
    leasing_list = conn.execute('''
        SELECT *, 
               (total_months - months_paid) as remaining_months,
               ((total_months - months_paid) * monthly_amount) as remaining_amount
        FROM leasing 
        ORDER BY is_active DESC, description
    ''').fetchall()
    
    total_monthly = conn.execute('''
        SELECT COALESCE(SUM(monthly_amount), 0) as total
        FROM leasing WHERE is_active = 1
    ''').fetchone()['total']
    
    conn.close()
    
    return render_template('leasing.html', 
                         leasing_list=leasing_list,
                         total_monthly=total_monthly)

@app.route('/yearly_planned')
def yearly_planned():
    """Manage yearly planned expenses"""
    conn = get_db_connection()
    planned_expenses = conn.execute('''
        SELECT * FROM yearly_planned_expenses 
        ORDER BY planned_year, planned_month, description
    ''').fetchall()
    conn.close()
    
    month_names = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                   'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
    
    return render_template('yearly_planned.html', 
                         planned_expenses=planned_expenses,
                         month_names=month_names)

@app.route('/savings')
def savings():
    """Savings account management"""
    conn = get_db_connection()
    
    transactions = conn.execute('''
        SELECT * FROM savings_transactions 
        ORDER BY date DESC
    ''').fetchall()
    
    balance = conn.execute('''
        SELECT COALESCE(SUM(
            CASE WHEN transaction_type = 'deposit' THEN amount 
                 ELSE -amount END
        ), 0) as balance
        FROM savings_transactions
    ''').fetchone()['balance']
    
    # Calculate monthly summaries for 2025
    monthly_summaries = {}
    current_year = 2025
    month_names = ['', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
                   'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień']
    
    for month_num in range(1, 13):
        month_prefix = f"{current_year}-{month_num:02d}"
        
        # Filter transactions for this month
        month_transactions = [t for t in transactions if t['date'].startswith(month_prefix)]
        
        month_deposits = sum(t['amount'] for t in month_transactions if t['transaction_type'] == 'deposit')
        month_withdrawals = sum(t['amount'] for t in month_transactions if t['transaction_type'] == 'withdrawal')
        month_net = month_deposits - month_withdrawals
        
        if month_net != 0:  # Only include months with transactions
            monthly_summaries[month_num] = {
                'name': month_names[month_num],
                'net': month_net,
                'count': len(month_transactions)
            }
    
    conn.close()
    
    return render_template('savings.html',
                         transactions=transactions,
                         balance=balance,
                         monthly_summaries=monthly_summaries)

# Missing route implementations
@app.route('/add_leasing', methods=['POST'])
def add_leasing():
    """Add new leasing"""
    description = request.form['description']
    monthly_amount = float(request.form['monthly_amount'])
    total_months = int(request.form['total_months'])
    start_date = request.form['start_date']
    
    # Calculate end date
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = start + timedelta(days=30 * total_months)
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO leasing (description, monthly_amount, total_months, start_date, end_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (description, monthly_amount, total_months, start_date, end.strftime('%Y-%m-%d')))
    conn.commit()
    conn.close()
    
    flash('Leasing został dodany pomyślnie!', 'success')
    return redirect(url_for('leasing'))

@app.route('/add_yearly_planned', methods=['POST'])
def add_yearly_planned():
    """Add yearly planned expense"""
    description = request.form['description']
    amount = float(request.form['amount'])
    planned_year = int(request.form['planned_year'])
    planned_month = int(request.form['planned_month'])
    category = request.form['category']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO yearly_planned_expenses (description, amount, planned_year, planned_month, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (description, amount, planned_year, planned_month, category))
    conn.commit()
    conn.close()
    
    flash('Planowany wydatek został dodany!', 'success')
    return redirect(url_for('yearly_planned'))

@app.route('/add_savings_transaction', methods=['POST'])
def add_savings_transaction():
    """Add savings transaction"""
    description = request.form['description']
    amount = float(request.form['amount'])
    transaction_type = request.form['transaction_type']
    date = request.form['date']
    month_source = request.form.get('month_source', '')
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO savings_transactions (date, amount, transaction_type, description, month_source)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, amount, transaction_type, description, month_source))
    conn.commit()
    conn.close()
    
    flash('Transakcja została dodana!', 'success')
    return redirect(url_for('savings'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=9877)