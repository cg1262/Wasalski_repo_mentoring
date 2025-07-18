# Life RPG - Gamification System
# A Flask web application for tracking progress across different life areas through gamification

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///life_rpg.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    """User model representing the player in the Life RPG system"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    level = db.Column(db.Integer, default=1)
    total_xp = db.Column(db.Integer, default=0)
    coins = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class LifeArea(db.Model):
    """Life areas represent different categories of personal development"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50))
    color = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    current_xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)

class Task(db.Model):
    """Tasks are quests that users complete to earn XP and coins"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    xp_reward = db.Column(db.Integer, default=10)
    coin_reward = db.Column(db.Integer, default=1)
    life_area_id = db.Column(db.Integer, db.ForeignKey('life_area.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_completed = db.Column(db.Boolean, default=False)
    is_daily = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)

class Habit(db.Model):
    """Habits are recurring activities that build streaks"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    life_area_id = db.Column(db.Integer, db.ForeignKey('life_area.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    xp_per_completion = db.Column(db.Integer, default=5)
    
class HabitCompletion(db.Model):
    """Tracks daily habit completions"""
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'))
    completed_date = db.Column(db.Date, default=datetime.utcnow().date)

class Reward(db.Model):
    """Rewards that users can claim by spending coins"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cost = db.Column(db.Integer, default=10)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_claimed = db.Column(db.Boolean, default=False)

# Helper Functions
def calculate_level_from_xp(xp):
    """Calculate level based on total XP (100 XP per level)"""
    return (xp // 100) + 1

def get_xp_for_current_level(xp):
    """Get XP progress within current level"""
    return xp % 100

# Database Initialization
def init_database():
    """Initialize database with default data"""
    with app.app_context():
        db.create_all()
        
        # Create default user if doesn't exist
        if not User.query.get(1):
            user = User(id=1, username='Player', level=1, total_xp=0, coins=0)
            db.session.add(user)
            
            # Create default life areas
            default_areas = [
                {'name': 'Health', 'icon': '💪', 'color': '#FF6B6B'},
                {'name': 'Personal Growth', 'icon': '📚', 'color': '#4ECDC4'},
                {'name': 'Career', 'icon': '💼', 'color': '#45B7D1'},
                {'name': 'Finance', 'icon': '💰', 'color': '#96CEB4'},
                {'name': 'Relationships', 'icon': '❤️', 'color': '#DDA0DD'},
                {'name': 'Hobbies', 'icon': '🎨', 'color': '#FFD93D'}
            ]
            
            for area_data in default_areas:
                area = LifeArea(
                    name=area_data['name'],
                    icon=area_data['icon'],
                    color=area_data['color'],
                    user_id=1
                )
                db.session.add(area)
            
            db.session.commit()

# Routes
@app.route('/')
def index():
    """Main dashboard route"""
    # For demo we'll use user_id = 1
    user = User.query.get(1)
    if not user:
        init_database()
        user = User.query.get(1)
    return render_template('dashboard.html', user=user)

@app.route('/api/user/<int:user_id>')
def get_user_data(user_id):
    """Get user data including life areas"""
    user = User.query.get_or_404(user_id)
    life_areas = LifeArea.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'level': user.level,
            'total_xp': user.total_xp,
            'current_level_xp': get_xp_for_current_level(user.total_xp),
            'coins': user.coins
        },
        'life_areas': [{
            'id': area.id,
            'name': area.name,
            'icon': area.icon,
            'color': area.color,
            'current_xp': area.current_xp,
            'level': area.level
        } for area in life_areas]
    })

@app.route('/api/tasks/<int:user_id>')
def get_tasks(user_id):
    """Get all tasks for a user"""
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.desc()).all()
    return jsonify([{
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'xp_reward': task.xp_reward,
        'coin_reward': task.coin_reward,
        'life_area_id': task.life_area_id,
        'is_completed': task.is_completed,
        'is_daily': task.is_daily,
        'due_date': task.due_date.isoformat() if task.due_date else None
    } for task in tasks])

@app.route('/api/tasks/create', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.json
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        xp_reward=data.get('xp_reward', 10),
        coin_reward=data.get('coin_reward', 1),
        life_area_id=data.get('life_area_id'),
        user_id=data['user_id'],
        is_daily=data.get('is_daily', False),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'success': True, 'task_id': task.id})

@app.route('/api/tasks/complete/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    """Mark task as complete and award XP/coins"""
    task = Task.query.get_or_404(task_id)
    if task.is_completed and not task.is_daily:
        return jsonify({'error': 'Task already completed'}), 400
    
    # Award XP and coins
    user = User.query.get(task.user_id)
    user.total_xp += task.xp_reward
    user.coins += task.coin_reward
    user.level = calculate_level_from_xp(user.total_xp)
    
    # Update life area XP
    if task.life_area_id:
        life_area = LifeArea.query.get(task.life_area_id)
        life_area.current_xp += task.xp_reward
        life_area.level = calculate_level_from_xp(life_area.current_xp)
    
    task.is_completed = True
    task.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'xp_gained': task.xp_reward,
        'coins_gained': task.coin_reward,
        'new_level': user.level,
        'new_total_xp': user.total_xp
    })

@app.route('/api/habits/<int:user_id>')
def get_habits(user_id):
    """Get all habits for a user"""
    habits = Habit.query.filter_by(user_id=user_id).all()
    today = datetime.utcnow().date()
    
    habits_data = []
    for habit in habits:
        completed_today = HabitCompletion.query.filter_by(
            habit_id=habit.id,
            completed_date=today
        ).first() is not None
        
        habits_data.append({
            'id': habit.id,
            'name': habit.name,
            'life_area_id': habit.life_area_id,
            'streak': habit.streak,
            'best_streak': habit.best_streak,
            'xp_per_completion': habit.xp_per_completion,
            'completed_today': completed_today
        })
    
    return jsonify(habits_data)

@app.route('/api/habits/create', methods=['POST'])
def create_habit():
    """Create a new habit"""
    data = request.json
    habit = Habit(
        name=data['name'],
        life_area_id=data.get('life_area_id'),
        user_id=data['user_id'],
        xp_per_completion=data.get('xp_per_completion', 5)
    )
    db.session.add(habit)
    db.session.commit()
    return jsonify({'success': True, 'habit_id': habit.id})

@app.route('/api/habits/complete/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    """Mark habit as complete for today"""
    habit = Habit.query.get_or_404(habit_id)
    today = datetime.utcnow().date()
    
    # Check if already completed today
    existing = HabitCompletion.query.filter_by(
        habit_id=habit_id,
        completed_date=today
    ).first()
    
    if existing:
        return jsonify({'error': 'Habit already completed today'}), 400
    
    # Add completion record
    completion = HabitCompletion(habit_id=habit_id, completed_date=today)
    db.session.add(completion)
    
    # Update streak
    yesterday = today - timedelta(days=1)
    yesterday_completion = HabitCompletion.query.filter_by(
        habit_id=habit_id,
        completed_date=yesterday
    ).first()
    
    if yesterday_completion:
        habit.streak += 1
    else:
        habit.streak = 1
    
    habit.best_streak = max(habit.streak, habit.best_streak)
    
    # Award XP
    user = User.query.get(habit.user_id)
    user.total_xp += habit.xp_per_completion
    user.level = calculate_level_from_xp(user.total_xp)
    
    if habit.life_area_id:
        life_area = LifeArea.query.get(habit.life_area_id)
        life_area.current_xp += habit.xp_per_completion
        life_area.level = calculate_level_from_xp(life_area.current_xp)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'xp_gained': habit.xp_per_completion,
        'new_streak': habit.streak
    })

@app.route('/api/rewards/<int:user_id>')
def get_rewards(user_id):
    """Get all rewards for a user"""
    rewards = Reward.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': reward.id,
        'name': reward.name,
        'description': reward.description,
        'cost': reward.cost,
        'is_claimed': reward.is_claimed
    } for reward in rewards])

@app.route('/api/rewards/create', methods=['POST'])
def create_reward():
    """Create a new reward"""
    data = request.json
    reward = Reward(
        name=data['name'],
        description=data.get('description', ''),
        cost=data.get('cost', 10),
        user_id=data['user_id']
    )
    db.session.add(reward)
    db.session.commit()
    return jsonify({'success': True, 'reward_id': reward.id})

@app.route('/api/rewards/claim/<int:reward_id>', methods=['POST'])
def claim_reward(reward_id):
    """Claim a reward using coins"""
    reward = Reward.query.get_or_404(reward_id)
    user = User.query.get(reward.user_id)
    
    if reward.is_claimed:
        return jsonify({'error': 'Reward already claimed'}), 400
    
    if user.coins < reward.cost:
        return jsonify({'error': 'Not enough coins'}), 400
    
    user.coins -= reward.cost
    reward.is_claimed = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'coins_remaining': user.coins
    })

# Demo helper function
@app.route('/api/demo/reset', methods=['POST'])
def reset_demo():
    """Reset demo data"""
    db.drop_all()
    db.create_all()
    init_database()
    return jsonify({'success': True})

# HTML Template (save as templates/dashboard.html)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Life RPG - Gamify Your Life</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f0f1e;
            color: #ffffff;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .user-info {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        
        .level-badge {
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 30px;
            font-size: 24px;
            font-weight: bold;
        }
        
        .stats {
            display: flex;
            gap: 30px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: bold;
            display: block;
        }
        
        .stat-label {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .xp-bar {
            background: rgba(255,255,255,0.2);
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            position: relative;
        }
        
        .xp-fill {
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            height: 100%;
            width: 0%;
            transition: width 0.5s ease;
        }
        
        .xp-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: bold;
            font-size: 14px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: #1a1a2e;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        
        .card-title {
            font-size: 20px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .life-area {
            background: #2a2a3e;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .area-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .area-icon {
            font-size: 30px;
        }
        
        .task-item, .habit-item {
            background: #2a2a3e;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .task-item:hover, .habit-item:hover {
            background: #3a3a4e;
            transform: translateX(5px);
        }
        
        .task-checkbox, .habit-checkbox {
            width: 24px;
            height: 24px;
            border: 2px solid #667eea;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
        }
        
        .task-checkbox.completed, .habit-checkbox.completed {
            background: #667eea;
        }
        
        .task-checkbox.completed::after, .habit-checkbox.completed::after {
            content: "✓";
            color: white;
        }
        
        .task-info {
            flex: 1;
        }
        
        .task-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .task-rewards {
            font-size: 14px;
            color: #ffd700;
        }
        
        .streak-badge {
            background: #ff6b6b;
            color: white;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        
        .btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
        }
        
        .modal-content {
            background: #1a1a2e;
            padding: 30px;
            border-radius: 20px;
            max-width: 500px;
            margin: 50px auto;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #3a3a4e;
            background: #2a2a3e;
            color: white;
        }
        
        .reward-item {
            background: #2a2a3e;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .reward-cost {
            background: #ffd700;
            color: #1a1a2e;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .tab {
            padding: 10px 20px;
            background: #2a2a3e;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .tab.active {
            background: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="user-info">
                <h1>🎮 Life RPG</h1>
                <div class="level-badge">Level <span id="userLevel">1</span></div>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-value" id="totalXP">0</span>
                    <span class="stat-label">Total XP</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value" id="coins">0</span>
                    <span class="stat-label">Coins</span>
                </div>
            </div>
            
            <div class="xp-bar">
                <div class="xp-fill" id="xpFill"></div>
                <span class="xp-text" id="xpText">0/100 XP</span>
            </div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="showTab('overview')">📊 Overview</div>
            <div class="tab" onclick="showTab('tasks')">📝 Tasks</div>
            <div class="tab" onclick="showTab('habits')">🔄 Habits</div>
            <div class="tab" onclick="showTab('rewards')">🏆 Rewards</div>
        </div>
        
        <div id="overview" class="tab-content">
            <div class="grid">
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">🎯 Life Areas</h2>
                    </div>
                    <div id="lifeAreas"></div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h2 class="card-title">📈 Weekly Stats</h2>
                    </div>
                    <div style="text-align: center; padding: 40px;">
                        <span style="font-size: 48px;">📊</span>
                        <p>Coming soon!</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="tasks" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">📝 Tasks</h2>
                    <button class="btn" onclick="showModal('taskModal')">+ New Task</button>
                </div>
                <div id="tasksList"></div>
            </div>
        </div>
        
        <div id="habits" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">🔄 Daily Habits</h2>
                    <button class="btn" onclick="showModal('habitModal')">+ New Habit</button>
                </div>
                <div id="habitsList"></div>
            </div>
        </div>
        
        <div id="rewards" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">🏆 Rewards</h2>
                    <button class="btn" onclick="showModal('rewardModal')">+ New Reward</button>
                </div>
                <div id="rewardsList"></div>
            </div>
        </div>
    </div>
    
    <!-- Modals -->
    <div id="taskModal" class="modal">
        <div class="modal-content">
            <h2>New Task</h2>
            <form id="taskForm">
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" name="title" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description"></textarea>
                </div>
                <div class="form-group">
                    <label>Life Area</label>
                    <select name="life_area_id" id="taskAreaSelect"></select>
                </div>
                <div class="form-group">
                    <label>XP Reward</label>
                    <input type="number" name="xp_reward" value="10" min="1">
                </div>
                <div class="form-group">
                    <label>Coin Reward</label>
                    <input type="number" name="coin_reward" value="1" min="0">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="is_daily"> Daily Task
                    </label>
                </div>
                <button type="submit" class="btn">Add Task</button>
                <button type="button" class="btn" onclick="hideModal('taskModal')">Cancel</button>
            </form>
        </div>
    </div>
    
    <div id="habitModal" class="modal">
        <div class="modal-content">
            <h2>New Habit</h2>
            <form id="habitForm">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Life Area</label>
                    <select name="life_area_id" id="habitAreaSelect"></select>
                </div>
                <div class="form-group">
                    <label>XP per Completion</label>
                    <input type="number" name="xp_per_completion" value="5" min="1">
                </div>
                <button type="submit" class="btn">Add Habit</button>
                <button type="button" class="btn" onclick="hideModal('habitModal')">Cancel</button>
            </form>
        </div>
    </div>
    
    <div id="rewardModal" class="modal">
        <div class="modal-content">
            <h2>New Reward</h2>
            <form id="rewardForm">
                <div class="form-group">
                    <label>Name</label>
                    <input type="text" name="name" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description"></textarea>
                </div>
                <div class="form-group">
                    <label>Cost (coins)</label>
                    <input type="number" name="cost" value="10" min="1">
                </div>
                <button type="submit" class="btn">Add Reward</button>
                <button type="button" class="btn" onclick="hideModal('rewardModal')">Cancel</button>
            </form>
        </div>
    </div>
    
    <script>
        let currentUser = { id: 1 };
        let userData = {};
        let lifeAreas = [];
        
        // Helper functions
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.style.display = 'none';
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            document.getElementById(tabName).style.display = 'block';
            event.target.classList.add('active');
        }
        
        function showModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }
        
        function hideModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // Load user data
        async function loadUserData() {
            const response = await fetch(`/api/user/${currentUser.id}`);
            const data = await response.json();
            userData = data.user;
            lifeAreas = data.life_areas;
            
            updateUI();
            populateAreaSelects();
            loadTasks();
            loadHabits();
            loadRewards();
        }
        
        function updateUI() {
            document.getElementById('userLevel').textContent = userData.level;
            document.getElementById('totalXP').textContent = userData.total_xp;
            document.getElementById('coins').textContent = userData.coins;
            
            const xpInLevel = userData.current_level_xp;
            const xpPercent = (xpInLevel / 100) * 100;
            document.getElementById('xpFill').style.width = xpPercent + '%';
            document.getElementById('xpText').textContent = `${xpInLevel}/100 XP`;
            
            // Display life areas
            const areasHtml = lifeAreas.map(area => `
                <div class="life-area">
                    <div class="area-info">
                        <span class="area-icon">${area.icon}</span>
                        <div>
                            <strong>${area.name}</strong>
                            <div style="font-size: 14px; color: #888;">Level ${area.level} • ${area.current_xp} XP</div>
                        </div>
                    </div>
                </div>
            `).join('');
            document.getElementById('lifeAreas').innerHTML = areasHtml;
        }
        
        function populateAreaSelects() {
            const options = '<option value="">None</option>' + 
                lifeAreas.map(area => `<option value="${area.id}">${area.icon} ${area.name}</option>`).join('');
            document.getElementById('taskAreaSelect').innerHTML = options;
            document.getElementById('habitAreaSelect').innerHTML = options;
        }
        
        // Tasks
        async function loadTasks() {
            const response = await fetch(`/api/tasks/${currentUser.id}`);
            const tasks = await response.json();
            
            const tasksHtml = tasks.filter(task => !task.is_completed).map(task => {
                const area = lifeAreas.find(a => a.id === task.life_area_id);
                return `
                    <div class="task-item" onclick="completeTask(${task.id})">
                        <div class="task-checkbox"></div>
                        <div class="task-info">
                            <div class="task-title">${task.title}</div>
                            <div class="task-rewards">+${task.xp_reward} XP • +${task.coin_reward} 🪙 ${area ? '• ' + area.icon : ''}</div>
                        </div>
                    </div>
                `;
            }).join('');
            
            document.getElementById('tasksList').innerHTML = tasksHtml || '<p style="text-align: center; opacity: 0.5;">No tasks yet</p>';
        }
        
        async function completeTask(taskId) {
            const response = await fetch(`/api/tasks/complete/${taskId}`, { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                showNotification(`+${result.xp_gained} XP • +${result.coins_gained} 🪙`);
                loadUserData();
            }
        }
        
        // Habits
        async function loadHabits() {
            const response = await fetch(`/api/habits/${currentUser.id}`);
            const habits = await response.json();
            
            const habitsHtml = habits.map(habit => {
                const area = lifeAreas.find(a => a.id === habit.life_area_id);
                return `
                    <div class="habit-item" onclick="completeHabit(${habit.id})">
                        <div class="habit-checkbox ${habit.completed_today ? 'completed' : ''}"></div>
                        <div class="task-info">
                            <div class="task-title">${habit.name}</div>
                            <div class="task-rewards">+${habit.xp_per_completion} XP ${area ? '• ' + area.icon : ''}</div>
                        </div>
                        ${habit.streak > 0 ? `<span class="streak-badge">🔥 ${habit.streak}</span>` : ''}
                    </div>
                `;
            }).join('');
            
            document.getElementById('habitsList').innerHTML = habitsHtml || '<p style="text-align: center; opacity: 0.5;">No habits yet</p>';
        }
        
        async function completeHabit(habitId) {
            const response = await fetch(`/api/habits/complete/${habitId}`, { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                showNotification(`+${result.xp_gained} XP • Streak: ${result.new_streak} 🔥`);
                loadUserData();
            }
        }
        
        // Rewards
        async function loadRewards() {
            const response = await fetch(`/api/rewards/${currentUser.id}`);
            const rewards = await response.json();
            
            const rewardsHtml = rewards.filter(r => !r.is_claimed).map(reward => `
                <div class="reward-item">
                    <div>
                        <strong>${reward.name}</strong>
                        ${reward.description ? `<div style="font-size: 14px; opacity: 0.7;">${reward.description}</div>` : ''}
                    </div>
                    <button class="btn" onclick="claimReward(${reward.id})" 
                        ${userData.coins < reward.cost ? 'disabled' : ''}>
                        ${reward.cost} 🪙
                    </button>
                </div>
            `).join('');
            
            document.getElementById('rewardsList').innerHTML = rewardsHtml || '<p style="text-align: center; opacity: 0.5;">No rewards yet</p>';
        }
        
        async function claimReward(rewardId) {
            const response = await fetch(`/api/rewards/claim/${rewardId}`, { method: 'POST' });
            const result = await response.json();
            
            if (result.success) {
                showNotification('Reward claimed! 🎉');
                loadUserData();
            }
        }
        
        // Forms
        document.getElementById('taskForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            data.user_id = currentUser.id;
            data.is_daily = formData.get('is_daily') === 'on';
            
            await fetch('/api/tasks/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            hideModal('taskModal');
            e.target.reset();
            loadTasks();
        });
        
        document.getElementById('habitForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            data.user_id = currentUser.id;
            
            await fetch('/api/habits/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            hideModal('habitModal');
            e.target.reset();
            loadHabits();
        });
        
        document.getElementById('rewardForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            data.user_id = currentUser.id;
            
            await fetch('/api/rewards/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            hideModal('rewardModal');
            e.target.reset();
            loadRewards();
        });
        
        // Notifications
        function showNotification(message) {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #667eea;
                color: white;
                padding: 15px 30px;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                z-index: 2000;
                animation: slideIn 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.remove();
            }, 3000);
        }
        
        // Close modals when clicking outside
        window.onclick = function(event) {
            if (event.target.classList.contains('modal')) {
                event.target.style.display = 'none';
            }
        }
        
        // Load data on startup
        loadUserData();
    </script>
</body>
</html>
'''

# Create templates directory
import os
if not os.path.exists('templates'):
    os.makedirs('templates')

# Save HTML template
with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(HTML_TEMPLATE)

if __name__ == '__main__':
    init_database()  # Initialize database on startup
    app.run(debug=True)