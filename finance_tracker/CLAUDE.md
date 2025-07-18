# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Finance Tracker is a Flask web application for tracking personal expenses and income with advanced features for recurring transactions, hourly rate calculations, and tax computations. The application is designed to run from a single directory, making it suitable for deployment on NAS servers or simple hosting environments.

## Development Commands

### Running the Application
```bash
pip install -r requirements.txt
python app.py
```

The application runs on http://0.0.0.0:9876 with debug mode enabled.

### Database Management
- SQLite database (`finance_tracker.db`) is created automatically on startup
- Database initialization happens in `init_db()` function (app.py:16)
- No migration system - schema changes require manual database updates

## Architecture Overview

### Core Data Models (SQLite Tables)
- **expenses**: Basic and recurring expenses with category support
- **income**: Income records with optional hourly calculation and tax rates  
- **recurring_transactions**: Future occurrences of recurring expenses

### Key Financial Calculations

**Hourly Income Calculation** (app.py:131-138):
```
gross_amount = hours × hourly_rate
vat_amount = gross_amount × (vat_rate / 100)  # Default 23%
total_with_vat = gross_amount + vat_amount
tax_amount = gross_amount × (tax_rate / 100)  # Default 12%
net_amount = gross_amount - tax_amount
```

**Recurring Expenses** (app.py:99-108):
- Creates future transaction records in `recurring_transactions` table
- Uses 30-day approximation for monthly intervals
- Linked to parent expense via `parent_id`

### Route Structure
- `/` - Main dashboard with expense/income/recurring transaction lists
- `/add_expense` - Form for adding expenses with recurring options
- `/add_income` - Form for adding income with hourly rate calculations
- `/summary` - Financial summary with totals and balance calculations
- `/calculate_tax` - AJAX endpoint for real-time tax calculations
- `/delete_expense/<id>` and `/delete_income/<id>` - Deletion endpoints

### Frontend Architecture
- Bootstrap 5 responsive design with custom CSS gradients
- Jinja2 templates extending `base.html`
- jQuery for AJAX interactions
- Font Awesome icons throughout interface
- Flash messaging system for user feedback

## Important Implementation Details

### Database Schema
**expenses table**:
- `is_recurring`: Boolean flag for recurring expenses
- `recurring_months`: Number of months to repeat
- Deletion cascades to `recurring_transactions` table

**income table**:
- `hours`, `hourly_rate`: Optional fields for hourly calculations
- `vat_rate`, `tax_rate`: Configurable tax rates (defaults: 23%, 12%)
- Amount stored includes VAT when calculated from hours

**recurring_transactions table**:
- `parent_id`: Links to original expense
- `transaction_type`: 'expense' or 'income'
- Separate from main tables to track future occurrences

### Security Considerations
- Secret key hardcoded as 'your-secret-key-change-this' (app.py:7)
- No user authentication - single-user application
- Basic SQL injection protection via parameterized queries
- No CSRF protection on forms

### Tax System
- 12% income tax rate (Polish system)
- 23% VAT rate for hourly calculations
- Tax calculations in summary exclude VAT amount
- Real-time tax calculation via `/calculate_tax` endpoint

## File Structure

```
finance_tracker/
├── app.py                  # Main Flask application
├── requirements.txt        # Dependencies (Flask 2.3.3, sqlite3)
├── finance_tracker.db      # SQLite database (auto-created)
├── README.md              # Polish documentation
└── templates/
    ├── base.html          # Base template with Bootstrap
    ├── index.html         # Main dashboard
    ├── add_expense.html   # Expense form
    ├── add_income.html    # Income form  
    └── summary.html       # Financial summary
```

## Customization Points

- **Tax Rates**: Modify default values in income routes (app.py:129, 148)
- **Recurring Logic**: Adjust 30-day approximation in expense creation (app.py:102)
- **UI Styling**: Custom CSS in `base.html` template (lines 29-44)
- **Server Configuration**: Host/port settings in `app.run()` (app.py:230)
- **Secret Key**: Change hardcoded secret for production use

## Dependencies

Core requirements from `requirements.txt`:
- Flask==2.3.3
- sqlite3 (standard library)

Additional CDN resources:
- Bootstrap 5.1.3 (CSS/JS)
- Font Awesome 6.0.0 (icons)
- jQuery 3.6.0 (AJAX interactions)