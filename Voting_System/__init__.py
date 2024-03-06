from flask import Flask, redirect, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('base.html')


@app.route('/admin')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/voter')
def voter_login():
    return render_template('voter_login.html')
