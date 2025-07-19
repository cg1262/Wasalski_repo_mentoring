# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the Excel-based Finance Tracker application.

## Project Overview

Finance Tracker Excel is a Flask web application that replicates Excel-based financial planning with automatic calculations for carryover between months, lease tracking, yearly planned expenses, and savings management. The application is designed to feel and function like an Excel spreadsheet with a web interface.

## Development Commands

### Running the Application
```bash
cd app_excel
pip install -r requirements.txt
python app.py
```

The application runs on http://0.0.0.0:9877 with debug mode enabled.

### Database Management
- SQLite database (`finance_tracker_excel.db`) is created automatically on startup
- Database initialization happens in `init_db()` function (app.py:22)
- No migration system - schema changes require manual database updates

## Architecture Overview

### Core Data Models (SQLite Tables)

**Control Panel Settings:**
- `control_panel`: Main financial parameters (monthly income, hourly rate, VAT, etc.)

**Monthly Financial Data:**
- `monthly_data`: Excel-like monthly sheets with carryover calculations
- `monthly_expenses`: Detailed expense breakdown by category and month

**Planning & Tracking:**
- `leasing`: Lease installment tracking with automatic monthly calculations
- `yearly_planned_expenses`: Planned annual expenses with date scheduling
- `savings_transactions`: Savings account with deposit/withdrawal tracking

**Configuration:**
- `expense_categories`: Color-coded expense categories (like Excel)

### Key Financial Calculations (Excel-like)

**Monthly Carryover Calculation:**
```
zostaje_na_nastepny = przychod_netto + przeniesienie_z_poprzedniego - wydatki_razem
```

**Control Panel Calculations:**
```
przychod_brutto = monthly_hours × hourly_rate
vat_amount = przychod_brutto × (vat_rate / 100)
przychod_z_vat = przychod_brutto + vat_amount
```

**Automatic Expense Integration:**
- Lease installments automatically appear in monthly projections
- Yearly planned expenses automatically included in target months
- Carryover automatically calculated between consecutive months

### Route Structure

**Main Dashboard:**
- `/` - Excel-like overview with control panel and summaries
- `/control_panel` - Settings for income, hours, rates (like Excel input cells)

**Monthly Management:**
- `/month/<year>/<month>` - Individual month sheets (like Excel tabs)
- `/month/<year>/<month>/add_expense` - Add expenses to specific month

**Planning & Tracking:**
- `/leasing` - Lease management (like Excel leasing section)
- `/yearly_planned` - Annual planned expenses
- `/savings` - Savings account transactions

**API Endpoints:**
- `/add_leasing` - Create new lease
- `/add_yearly_planned` - Add planned expense
- `/add_savings_transaction` - Savings transactions

### Frontend Architecture (Excel-like Design)

**Color Scheme:**
- Excel Green (#107c41) for primary actions
- Category-based colors: Red (leasing), Orange (regular expenses), Yellow (VAT)
- Excel-like table styling with borders and cell formatting

**Excel-like Features:**
- Tabular data presentation with Excel cell styling
- Real-time calculations and previews
- Keyboard shortcuts (Ctrl+N, Ctrl+S, Escape, etc.)
- Auto-save functionality for drafts
- Tooltips and formula displays

**Responsive Design:**
- Bootstrap 5 with custom Excel-themed CSS
- Mobile-friendly while maintaining Excel aesthetics
- Progressive enhancement for touch interfaces

## Important Implementation Details

### Database Schema

**control_panel table:**
- `monthly_income_net`: Target monthly income after taxes
- `monthly_hours`: Planned work hours per month
- `hourly_rate`: Gross hourly billing rate
- `vat_rate`: VAT percentage (default 23%)
- `rent_cost`: Monthly rent/office costs

**monthly_data table:**
- `przeniesienie_z_poprzedniego`: Carryover from previous month (Excel-like)
- `zostaje_na_nastepny`: Amount left for next month
- Automatic calculation: `income + carryover - expenses = leftover`

**monthly_expenses table:**
- Detailed expense tracking by category and month
- `is_recurring`: Automatically copies to future months
- Integrated with category color coding

**leasing table:**
- `months_paid` vs `total_months` for progress tracking
- `is_active`: Automatically deactivated when fully paid
- Automatic monthly installment calculation

**yearly_planned_expenses table:**
- `planned_month`/`planned_year` for automatic scheduling
- `is_paid`: Track payment status
- `actual_payment_date`: When actually paid

### Excel-like Calculation Engine

**Monthly Totals Update Function:**
```python
def update_monthly_totals(conn, year, month):
    # Calculates carryover between months like Excel
    # Updates next month's przeniesienie_z_poprzedniego
    # Maintains chain of calculations across months
```

**Automatic Lease Integration:**
- Active leases appear in monthly expense projections
- Progress tracking with visual indicators
- End date calculations with month/day precision

**Yearly Planned Integration:**
- Planned expenses automatically appear in target months
- Status tracking (pending, paid)
- Integration with monthly budget calculations

### Security Considerations
- Secret key: 'excel-finance-tracker-secret-key' (change for production)
- No user authentication - single-user Excel-like application
- SQL injection protection via parameterized queries
- Form validation on both client and server side

### Excel-like UI/UX Features

**Keyboard Shortcuts:**
- `Ctrl+N`: New expense/transaction
- `Ctrl+S`: Save form
- `Escape`: Return to previous view
- `F1`: Help/formulas display

**Visual Excel Elements:**
- Grid-based layouts with cell borders
- Color-coded categories matching Excel conventions
- Progress bars for lease payments
- Formula displays showing calculations
- Real-time preview calculations

## File Structure

```
app_excel/
├── app.py                      # Main Flask application with Excel logic
├── requirements.txt            # Dependencies
├── finance_tracker_excel.db    # SQLite database (auto-created)
├── CLAUDE.md                  # This documentation
├── CHANGELOG.md               # Version history
└── templates/
    ├── base.html              # Excel-themed base template
    ├── index.html             # Main dashboard (Excel overview)
    ├── control_panel.html     # Settings panel (Excel inputs)
    ├── month_detail.html      # Monthly sheet view
    ├── add_month_expense.html # Expense entry form
    ├── leasing.html          # Lease management
    ├── yearly_planned.html   # Annual planning
    └── savings.html          # Savings account
```

## Customization Points

**Financial Parameters:**
- Default income/hours in control_panel initialization
- VAT and tax rates in control panel
- Expense categories in `expense_categories` table

**Excel Styling:**
- CSS custom properties in `base.html` for color themes
- Category color mappings in stylesheet
- Grid and table styling to match Excel look

**Calculation Logic:**
- Monthly carryover formulas in `update_monthly_totals()`
- Lease installment calculations in leasing routes
- Automatic expense integration logic

**UI Behavior:**
- Keyboard shortcuts in JavaScript
- Auto-save intervals and form persistence
- Real-time calculation updates

## Dependencies

Core requirements:
- Flask==2.3.3
- sqlite3 (standard library)

Frontend resources (CDN):
- Bootstrap 5.1.3 (Excel-like styling base)
- Font Awesome 6.0.0 (icons)
- jQuery 3.6.0 (Excel-like interactions)

## Excel Logic Implementation

**Carryover Between Months:**
Like Excel's month-to-month calculations, each month automatically receives the leftover amount from the previous month and passes its remainder to the next month.

**Automatic Expense Inclusion:**
- Lease installments appear automatically in monthly budgets
- Yearly planned expenses show up in their target months
- All calculations update in real-time like Excel formulas

**Color-Coded Categories:**
- Red: Leasing (high-impact recurring costs)
- Orange: Regular expenses (food, transport, entertainment)
- Yellow: VAT and tax-related
- Gray: Miscellaneous/other

**Formula Transparency:**
Templates show Excel-like formulas so users understand calculations:
- `= Przeniesienie + Przychód - Wydatki`
- `= SUMA(Faktyczne + Leasing + Planowane)`

This creates a familiar Excel experience in a web application with automatic data persistence and multi-device access.

## Troubleshooting

**Database Issues:**
- Delete `finance_tracker_excel.db` to recreate with fresh schema
- Check `init_db()` function for table creation errors

**Calculation Errors:**
- Verify `update_monthly_totals()` function for carryover logic
- Check control panel settings for base income/rate values

**Template Errors:**
- Ensure all month_names arrays are consistent
- Verify route parameter matching between templates and Flask routes

**Excel-like Features:**
- JavaScript keyboard shortcuts defined in base template
- Form validation combines client-side and server-side checks
- Auto-save functionality requires localStorage support