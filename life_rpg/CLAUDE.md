# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Life RPG is a Flask web application that gamifies personal development by turning daily tasks and habits into an RPG-style progression system. Users earn XP and coins by completing tasks and maintaining habits, progressing through levels across different life areas.

## Development Commands

### Running the Application
```bash
python app.py           # Polish version
python app_eng.py       # English version
```

The application runs on http://localhost:5000 with debug mode enabled.

### Database Management
- SQLite database (`instance/life_rpg.db`) is created automatically on first run
- Database initialization happens in `init_database()` function in app.py:309 and app_eng.py:87
- Demo reset endpoint available: `POST /api/demo/reset`

## Architecture Overview

### Core Models (SQLAlchemy)
- **User**: Player profile with level, total XP, and coins
- **LifeArea**: Categories for tasks/habits (Health, Career, etc.) with individual XP/levels
- **Task**: One-time or daily quests that award XP and coins
- **Habit**: Recurring activities with streak tracking
- **HabitCompletion**: Daily completion records for habits
- **Reward**: Items players can purchase with coins

### Key Systems

**XP/Level Calculation**: 100 XP per level (app.py:72-78, app_eng.py:78-84)
- `calculate_level_from_xp(xp)`: Returns level based on total XP
- `get_xp_for_current_level(xp)`: Returns XP progress within current level

**Habit Streaks**: Calculated based on consecutive daily completions, checking previous day completion in app.py:232-244, app_eng.py:278-290

**Life Areas**: Default areas created in `init_database()` with icons, colors, and individual progression

### API Structure
- RESTful JSON API under `/api/` prefix
- User data: `/api/user/<user_id>`
- CRUD operations for tasks, habits, rewards
- Completion endpoints that update XP and levels

### Frontend Architecture
- Single-page application with tab-based navigation
- Embedded HTML template (over 1000 lines) within Python files
- Real-time UI updates after completing tasks/habits
- Modal forms for creating new items
- Dark theme with gradient styling

## File Structure

```
life_rpg/
├── app.py              # Main Polish application
├── app_eng.py          # English version  
├── readme.md           # Polish documentation
├── readme_eng.md       # English documentation
├── instance/
│   └── life_rpg.db     # SQLite database (auto-created)
└── templates/
    └── dashboard.html  # Generated from embedded template
```

## Important Implementation Details

### Database Initialization
Both app files contain identical database models and logic but with different language strings. The `init_database()` function creates:
- Default user (ID=1) named "Gracz"/"Player"
- Six default life areas with emojis and colors
- Templates directory and HTML file generation

### HTML Template Generation
The complete frontend is embedded as a multi-line string (`HTML_TEMPLATE`) and written to `templates/dashboard.html` on startup. This includes all CSS and JavaScript inline.

### Single-User Design
Currently designed for demo/single-user mode (hardcoded user_id=1). Production deployment would need user authentication and session management.

### XP Distribution
When completing tasks or habits:
1. User's total XP increases
2. Associated life area XP increases
3. Both user and life area levels recalculated
4. Coins awarded for tasks only

## Customization Points

- **Life Areas**: Modify `default_areas` arrays in app.py:320-327, app_eng.py:98-105
- **XP Scaling**: Adjust level calculation in `calculate_level_from_xp()`
- **Styling**: Edit embedded CSS in `HTML_TEMPLATE` variables
- **Database**: Replace SQLite URI for production databases

## Dependencies

The application uses Flask with SQLAlchemy but no explicit requirements.txt file exists. Core dependencies:
- Flask
- Flask-SQLAlchemy
- Standard library: datetime, json, os