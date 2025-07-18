# Life RPG - Gamification System 🎮

A web application inspired by the Notion Life RPG template that transforms daily tasks into an engaging role-playing game experience.

## 📋 Requirements

- Python 3.8+
- pip (Python package manager)

## 🚀 Installation

1. **Clone or download the project files**
   
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   
   # Windows:
   venv\Scripts\activate
   
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## 🎮 How to Use

### Dashboard
- Main view displays your level, total XP, coins, and progress bar
- Tabs: Overview, Tasks, Habits, Rewards

### Tasks
- Click "+ New Task" to add a quest
- Set XP and coin rewards
- Assign to a life area
- Click on a task to complete it and earn rewards

### Habits
- Add daily habits you want to track
- Each completion awards XP
- Track streaks - consecutive days of completion

### Rewards
- Create rewards you can "purchase" with earned coins
- Motivate yourself with real-life rewards (e.g., "Watch a TV episode" for 10 coins)

### Life Areas
The application includes 6 default areas:
- 💪 Health - exercise, diet, sleep
- 📚 Personal Growth - learning, reading, courses
- 💼 Career - work projects, networking
- 💰 Finance - saving, investing
- ❤️ Relationships - time with loved ones, social activities
- 🎨 Hobbies - passions, creativity

## 🛠️ Project Structure

```
life-rpg/
│
├── app.py              # Main Flask application file
├── requirements.txt    # Python dependencies
├── life_rpg.db        # SQLite database (created automatically)
│
└── templates/
    └── dashboard.html  # HTML template (created by app.py)
```

## 📊 Database

The application uses SQLite - a lightweight database that requires no installation. 
The database is created automatically on first run.

### Data Models:
- **User** - player with level and statistics
- **LifeArea** - life categories to track
- **Task** - quests to complete
- **Habit** - daily recurring activities
- **HabitCompletion** - habit completion records
- **Reward** - rewards to claim

## 🎨 Customization

### Changing Life Areas
In `app.py`, find the `default_areas` section and customize as needed:

```python
default_areas = [
    {'name': 'Health', 'icon': '💪', 'color': '#FF6B6B'},
    # Add your own areas...
]
```

### Changing Appearance
Edit CSS styles in `dashboard.html` template to customize colors and design.

### Level System
Default: 100 XP = 1 level. 
Modify in the `calculate_level_from_xp()` function.

## 🔧 Extensions

Ideas for future development:
- Achievement/badge system
- Weekly/monthly statistics with charts
- Task categories (easy/medium/hard)
- Friends and leaderboards system
- Habit notifications
- Data export functionality
- Dark/light theme toggle
- Mobile application

## ⚠️ Notes

- Application runs locally on your computer
- Data is stored in `life_rpg.db` file
- For production use, PostgreSQL is recommended instead of SQLite
- Remember to regularly backup your database

## 📝 License

Open source project - feel free to modify and use as you wish.

---

**Enjoy gamifying your life! 🎮✨**