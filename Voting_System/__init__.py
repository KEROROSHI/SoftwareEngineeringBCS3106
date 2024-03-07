from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
import mysql.connector

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flask'
app.config['SECRET_KEY'] = "My secret key"
db = SQLAlchemy(app)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('base.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    return render_template('admin_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/voter')
def voter_login():
    return render_template('voter_login.html')
