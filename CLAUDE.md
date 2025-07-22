# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a multi-project mentoring repository containing several independent applications focused on financial tracking, web development learning, and automation tools. Each project has its own directory structure, dependencies, and documentation.

## Project Structure

### Finance Tracker (`finance_tracker/`)
Flask-based personal finance management application with SQLite backend.

**Development commands:**
```bash
cd finance_tracker
pip install -r requirements.txt
python app.py  # Runs on http://0.0.0.0:9876
```

**Excel variant (`finance_tracker/app_excel/`):**
```bash
cd finance_tracker/app_excel
pip install -r requirements.txt
python app.py  # Runs on http://0.0.0.0:9877
```

Both applications have comprehensive CLAUDE.md files with detailed architecture documentation.

### Expense Tracker (`expense-tracker/expense-tracker/`)
React + TypeScript + Vite application for expense tracking.

**Development commands:**
```bash
cd expense-tracker/expense-tracker
npm install
npm run dev      # Development server with HMR
npm run build    # TypeScript compilation + Vite build
npm run lint     # ESLint checking
npm run preview  # Preview production build
```

### Web App Classes (`web_app_classes/`)
Flask application demonstrating dynamic endpoint management and class discovery.

**Development commands:**
```bash
cd web_app_classes
pip install -r requirements.txt
python app.py
```

**Architecture:** Uses `EndpointManager` class to dynamically load Python modules from `endpoint_files/` directory and execute methods via web interface.

### Life RPG (`life_rpg/`)
Flask application for gamifying personal life management.

**Development commands:**
```bash
cd life_rpg
pip install Flask  # No requirements.txt file
python app.py      # Polish version
python app_eng.py  # English version
```

## Technology Stack

### Python Projects
- **Flask 2.3.3**: Web framework across all Python applications
- **SQLite**: Database for finance trackers and life RPG
- **Pandas**: Data manipulation in web_app_classes
- **Gunicorn**: WSGI server for production deployment

### JavaScript Projects
- **React 19**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **ESLint**: Code linting

## Development Workflow

### Project-Specific Documentation
Each major project contains its own CLAUDE.md file with detailed:
- Architecture overview
- Database schemas
- Route structures
- Calculation logic
- Customization points

**Refer to individual CLAUDE.md files for:**
- `finance_tracker/CLAUDE.md` - Flask financial app architecture
- `finance_tracker/app_excel/CLAUDE.md` - Excel-like variant details

### Common Patterns

**Flask Applications:**
- All use similar structure with `app.py` as entry point
- SQLite databases auto-created on startup via `init_db()` functions
- Bootstrap 5 + jQuery frontend stack
- No authentication (single-user applications)
- Debug mode enabled for development

**Database Management:**
- SQLite databases created automatically
- No migration systems - manual schema updates required
- Delete database files to reset schema

**Frontend Architecture:**
- Bootstrap 5 responsive design
- jQuery for AJAX interactions
- Font Awesome icons
- Flask flash messaging system

## Important Notes

### Security Considerations
- All applications use hardcoded secret keys (change for production)
- No user authentication implemented
- Single-user applications designed for local/personal use
- SQL injection protection via parameterized queries

### Port Configuration
- Finance Tracker: 9876
- Finance Tracker Excel: 9877
- Other Flask apps: Default Flask ports

### File Structure Pattern
Most Flask projects follow:
```
project/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── *.db               # SQLite database (auto-created)
├── templates/         # Jinja2 templates
├── README.md         # Project-specific documentation
└── CLAUDE.md         # Claude Code guidance (where applicable)
```

## Git Repository Management

Based on git status, the repository contains several modified files and untracked directories. When working on projects:

1. Each project is self-contained in its directory
2. Changes are typically isolated to individual projects
3. Database files (*.db) are committed to repository
4. Screenshots and documentation are version controlled

## Jupyter Notebooks

The repository contains several Jupyter notebooks:
- `listing_all_files.ipynb`: File system exploration
- `fake_data.ipynb`: Data generation utilities
- `classess.ipynb`: Python class examples/tutorials

These appear to be learning materials and utilities for the mentoring process.