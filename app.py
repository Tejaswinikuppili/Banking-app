from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Simple in-memory storage for demonstration
users = {}
transactions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return "User already exists!"
        users[username] = {'password': password, 'balance': 0}
        transactions[username] = []
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        return "Invalid username or password!"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = users[session['user']]
    return render_template('dashboard.html', user={'username': session['user'], 'balance': user['balance']})

@app.route('/deposit', methods=['POST'])
def deposit():
    if 'user' not in session:
        return redirect(url_for('login'))
    amount = float(request.form['amount'])
    users[session['user']]['balance'] += amount
    transactions[session['user']].append({'type': 'Deposit', 'amount': amount, 'target_user': None})
    return redirect(url_for('dashboard'))

@app.route('/withdraw', methods=['POST'])
def withdraw():
    if 'user' not in session:
        return redirect(url_for('login'))
    amount = float(request.form['amount'])
    if amount > users[session['user']]['balance']:
        return "Insufficient balance!"
    users[session['user']]['balance'] -= amount
    transactions[session['user']].append({'type': 'Withdraw', 'amount': amount, 'target_user': None})
    return redirect(url_for('dashboard'))

@app.route('/transfer', methods=['POST'])
def transfer():
    if 'user' not in session:
        return redirect(url_for('login'))
    target = request.form['target']
    amount = float(request.form['amount'])
    if target not in users:
        return "Target user does not exist!"
    if amount > users[session['user']]['balance']:
        return "Insufficient balance!"
    users[session['user']]['balance'] -= amount
    users[target]['balance'] += amount
    transactions[session['user']].append({'type': 'Transfer', 'amount': amount, 'target_user': target})
    transactions[target].append({'type': 'Received', 'amount': amount, 'target_user': session['user']})
    return redirect(url_for('dashboard'))

@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_transactions = transactions[session['user']]
    return render_template('history.html', transactions=user_transactions)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
