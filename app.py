# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import hashlib
import random
import string
import pymysql.cursors

app = Flask(__name__, template_folder="./template")
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'votingsystem'

UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

connection = pymysql.connect(host=app.config['MYSQL_HOST'],
                             user=app.config['MYSQL_USER'],
                             password=app.config['MYSQL_PASSWORD'],
                             db=app.config['MYSQL_DB'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_voter_id(length=15):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


@app.route('/login', methods=["GET", "POST"])
def login():
    errors = []  # Define errors variable here

    if request.method == 'POST':
        # Process form data
        voter_ID = request.form['voter_ID']
        password = request.form['password']

        # Validate input
        if not (voter_ID and password):
            errors.append("All fields are required")
        else:
            # Retrieve user from the database
            with connection.cursor() as cursor:
                select_query = "SELECT * FROM voters WHERE voters_id = %s"
                cursor.execute(select_query, (voter_ID,))
                result = cursor.fetchone()

                if result:
                    stored_password = result['password']

                    if check_password_hash(stored_password, password) == True:
                        flash('Login successful', 'success')
                        return redirect(url_for('voters'))
                    else:
                        errors.append("Password did not match our records")
                else:
                    errors.append("Voter ID did not match our records")

        # Display errors
        for error in errors:
            flash(error, 'error')

    return render_template('login.html', errors=errors, voter_ID=request.form.get('voter_ID', ''))


@app.route('/voters', methods=["GET", "POST"])
def voters():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['image']

        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Secure the filename before saving it
            filename = secure_filename(file.filename)

            # Generate a unique filename to prevent overwriting files
            file_extension = filename.rsplit('.', 1)[1].lower()
            random_filename = hashlib.md5(filename.encode()).hexdigest() + '.' + file_extension

            # Save the file to the upload folder
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_filename))

            # Process form data
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            password = request.form['password']

            # Hash the password
            hashed_password = generate_password_hash(password)

            # Generate voter ID
            voter_id = generate_voter_id()

            # Insert data into the database
            try:
                with connection.cursor() as cursor:
                    # Create a new record
                    sql = "INSERT INTO `voters` (`voters_id`, `password`, `firstname`, `lastname`, `photo`) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (voter_id, hashed_password, firstname, lastname, random_filename))
                    connection.commit()
            except pymysql.Error as e:
                print("Error inserting into database:", e)
                flash('Error inserting into database', 'error')

            flash('Voter added successfully', 'success')
            return redirect(url_for('voters'))

    # Fetch data from the database to display in the template
    try:
        with connection.cursor() as cursor:
            select_query = "SELECT * FROM voters"
            cursor.execute(select_query)
            voters_data = cursor.fetchall()
    except pymysql.Error as e:
        print("Error fetching data from database:", e)
        flash('Error fetching data from database', 'error')
        voters_data = []

    return render_template('voters.html', voters_data=voters_data)


if __name__ == "__main__":
    app.run(debug=True)
