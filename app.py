from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash

app = Flask(__name__, template_folder="./template")
app.secret_key = 'your_secret_key'

# MySQL configurations
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

        # Initialize errors array
        errors = []

        # Password hashing
        hashed_password = generate_password_hash(pass1)

        # Input validation
        if not (fname and lname and student_year and gender and email and pass1 and pass2):
            errors.append('All fields are required!')

        if pass1 != pass2:
            errors.append('Passwords do not match!')

        # Check for duplicate email entry
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM voters WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()

        if user:
            errors.append('Email already exists!')

        if not errors:
            # Insertion
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO voters (first_name, last_name, student_year, gender, email, password, user_level) VALUES(%s, %s, %s, %s, %s, %s, %s)",
                        (fname, lname, student_year, gender, email, hashed_password, 1))  # assuming user_level = 1 for regular users
            mysql.connection.commit()
            cur.close()

            flash('Registration successful!', 'success')
            return redirect(request.url)

        # If errors exist, flash and redirect back to registration form
        for error in errors:
            flash(error, 'error')
        
        # Return to registration form with sticky values
        return render_template("registration.html", form_data=request.form)

    # GET request: render registration form
    return render_template("registration.html", form_data={})

if __name__ == "__main__":
    app.run(debug=True)
