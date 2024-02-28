# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash

app = Flask(__name__, template_folder="./template")
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'votting_db'

mysql = MySQL(app)


@app.route('/registration', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        details = request.form
        fname = details['fname']
        lname = details['lname']
        student_year = details['student_year']
        gender = details['gender']
        email = details['email']
        pass1 = details['pass1']
        pass2 = details['pass2']

        # Password hashing
        hashed_password = generate_password_hash(pass1)

        # Input validation
        if not (fname and lname and student_year and gender and email and pass1 and pass2):
            flash('All fields are required!', 'error')
            return redirect(url_for('registration'))

        if pass1 != pass2:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('registration'))

        # Check for duplicate email entry
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM voters WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            flash('Email already exists!', 'error')
            return redirect(url_for('registration'))

        # Insertion
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO voters (first_name, last_name, student_year, gender, email, password, user_level) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                    (fname, lname, student_year, gender, email, hashed_password, 1))  # assuming user_level = 1 for regular users
        mysql.connection.commit()
        cur.close()

        flash('Registration successful!', 'success')
        return redirect(url_for('registration'))

    return render_template("registration.html")


if __name__ == "__main__":
    app.run(debug=True)
