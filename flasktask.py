from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(24)

# In-memory databases for users and apps
users = {
    'example_user': {
        'password': bcrypt.generate_password_hash('password').decode('utf-8'),
        'credits': 10,
        'my_apps': [1, 2, 3],  # Example user owns Excel to CSV, CSV to Excel, and PDF Merger
        'favorites': [1]  # Example user has favorited Excel to CSV
    }
}

apps_list = [
    {
        'id': 1, 
        'name': 'Excel to CSV Converter', 
        'description': 'Convert Excel files to CSV format.', 
        'buy_cost': 5,  # Cost to purchase the app
        'execution_cost': 1,  # Cost per execution
        'route': 'excel_to_csv.show_app'
    },
    {
        'id': 2, 
        'name': 'CSV to Excel Converter', 
        'description': 'Convert CSV files to Excel format.', 
        'buy_cost': 5, 
        'execution_cost': 1,
        'route': 'csv_to_excel.show_app'
    },
    {
        'id': 3, 
        'name': 'PDF Merger', 
        'description': 'Merge two or more PDF files into one.', 
        'buy_cost': 10, 
        'execution_cost': 2,  # PDF merger could cost more per execution
        'route': 'pdf_merger.show_app'
    }
]

# Home route
@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('my_apps'))
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = username
            session['credits'] = user['credits']
            session['my_apps'] = user['my_apps']
            session['favorites'] = user['favorites']
            flash('Login successful!')
            return redirect(url_for('my_apps'))
        flash('Invalid username or password.')
    return render_template('general/login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists. Please choose another one.')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            users[username] = {
                'password': hashed_password,
                'credits': 10,
                'my_apps': [],
                'favorites': []
            }
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))
    return render_template('general/register.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# My Apps Grid View
@app.route('/my-apps')
def my_apps():
    if 'user' in session:
        user_apps = [app for app in apps_list if app['id'] in session['my_apps']]
        return render_template('general/my_apps.html', my_apps=user_apps)
    return redirect(url_for('login'))

# Favorite Apps Grid View
@app.route('/favorite-apps')
def favorite_apps():
    if 'user' in session:
        favorite_apps = [app for app in apps_list if app['id'] in session['favorites']]
        return render_template('general/favorite_apps.html', favorite_apps=favorite_apps)
    return redirect(url_for('login'))

# Toggle Favorite App Route
@app.route('/toggle-favorite/<int:app_id>', methods=['POST'])
def toggle_favorite(app_id):
    if 'user' in session:
        user = users[session['user']]
        if app_id in user['favorites']:
            user['favorites'].remove(app_id)
            flash(f'App {app_id} removed from favorites.')
        else:
            user['favorites'].append(app_id)
            flash(f'App {app_id} added to favorites.')
        session['favorites'] = user['favorites']
        return redirect(url_for('my_apps'))
    return redirect(url_for('login'))

# Launch App Route
@app.route('/launch-app/<int:app_id>', methods=['GET', 'POST'])
def launch_app(app_id):
    if 'user' in session:
        print(f"Current session user: {session['user']}")  # Log the session user
        user = users.get(session['user'])
        print(f"User credits before execution: {user['credits']}")  # Log user credits before deduction

        # Find the app by id in apps_list
        app = next((app for app in apps_list if app['id'] == app_id), None)

        if app and app_id in session['my_apps']:
            execution_cost = app['execution_cost']

            # Check if the user has enough credits to run the app
            if user['credits'] >= execution_cost:
                # Deduct the execution cost from the user's credits
                user['credits'] -= execution_cost
                session['credits'] = user['credits']  # Update session credits
                print(f"User credits after execution: {user['credits']}")  # Log credits after deduction

                # Flash a message about credits used
                flash(f"{execution_cost} credit(s) used. You have {user['credits']} credits remaining.")

                # Redirect to the app's route for execution
                return redirect(url_for(app['route']))
            else:
                flash("You don't have enough credits to use this app.")
                return redirect(url_for('buy_credits'))
        else:
            flash('App not found or not owned.')
            return redirect(url_for('my_apps'))
    return redirect(url_for('login'))
    
# App Store route
@app.route('/store')
def app_store():
    if 'user' in session:
        user_apps_ids = session.get('my_apps', [])
        available_apps = [app for app in apps_list if app['id'] not in user_apps_ids]
        return render_template('general/app_store.html', available_apps=available_apps)
    return redirect(url_for('login'))

# Buy App route
@app.route('/buy-app/<int:app_id>', methods=['POST'])
def buy_app(app_id):
    if 'user' in session:
        user = users[session['user']]
        app = next((app for app in apps_list if app['id'] == app_id), None)
        
        if app and app_id not in session['my_apps']:
            buy_cost = app['buy_cost']
            
            # Check if the user has enough credits to buy the app
            if user['credits'] >= buy_cost:
                user['credits'] -= buy_cost
                session['credits'] = user['credits']  # Update session credits
                session['my_apps'].append(app_id)  # Add app to the user's purchased apps
                
                flash(f"You successfully bought {app['name']} for {buy_cost} credits.")
                return redirect(url_for('my_apps'))
            else:
                flash("You don't have enough credits to buy this app.")
                return redirect(url_for('buy_credits'))
        else:
            flash('App already owned or not found.')
            return redirect(url_for('my_apps'))
    return redirect(url_for('login'))

# Buy Credits route
@app.route('/buy-credits', methods=['GET', 'POST'])
def buy_credits():
    if 'user' in session:
        if request.method == 'POST':
            credit_amount = int(request.form['credit_amount'])
            users[session['user']]['credits'] += credit_amount
            session['credits'] = users[session['user']]['credits']
            flash(f'You have successfully bought {credit_amount} credits!')
            return redirect(url_for('buy_credits'))
        return render_template('general/buy_credits.html')
    return redirect(url_for('login'))

# Profile route
@app.route('/profile')
def profile():
    if 'user' in session:
        username = session['user']
        user = users[username]
        return render_template('general/profile.html', username=username, credits=user['credits'])
    return redirect(url_for('login'))

# Import and register blueprints for apps
from apps.excel_to_csv.excel_to_csv import excel_to_csv_blueprint
from apps.csv_to_excel.csv_to_excel import csv_to_excel_blueprint
from apps.pdf_merger.pdf_merger import pdf_merger_blueprint

# Registering the blueprints
app.register_blueprint(excel_to_csv_blueprint, url_prefix='/launch-app/1')
app.register_blueprint(csv_to_excel_blueprint, url_prefix='/launch-app/2')
app.register_blueprint(pdf_merger_blueprint, url_prefix='/launch-app/3')

if __name__ == '__main__':
    app.run(debug=True)
