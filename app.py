from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import hashlib
import random
import string
import mysql.connector

app = Flask(__name__, template_folder="./template")
app.secret_key = 'your_secret_key'

# MySQL configurations
mysql_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="votingsystem"
)

UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_voter_id(length=15):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


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
                cursor = mysql_conn.cursor()
                # Create a new record
                sql = "INSERT INTO `voters` (`voters_id`, `password`, `firstname`, `lastname`, `photo`) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (voter_id, hashed_password, firstname, lastname, random_filename))
                mysql_conn.commit()
                cursor.close()
            except mysql.connector.Error as e:
                print("Error inserting into database:", e)
                flash('Error inserting into database', 'error')

            flash('Voter added successfully', 'success')
            return redirect(url_for('voters'))

    # Fetch data from the database to display in the template
    try:
        cursor = mysql_conn.cursor(dictionary=True)
        select_query = "SELECT * FROM voters"
        cursor.execute(select_query)
        voters_data = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        print("Error fetching data from database:", e)
        flash('Error fetching data from database', 'error')
        voters_data = []

    return render_template('voters.html', voters_data=voters_data)


@app.route('/editvoter', methods=["GET", "POST"])
def edit_voter():
    if request.method == 'GET':
        voter_id = request.args.get('id')

        try:
            cursor = mysql_conn.cursor(dictionary=True)
            # Fetch voter details based on voter ID
            select_query = "SELECT * FROM voters WHERE id = %s"
            cursor.execute(select_query, (voter_id,))
            voter = cursor.fetchone()

            if not voter:
                flash('Voter not found', 'error')
                return redirect(url_for('voters'))

            cursor.close()
        except mysql.connector.Error as e:
            print("Error fetching voter details:", e)
            flash('Error fetching voter details', 'error')
            return redirect(url_for('voters'))

        return render_template('editvoter.html', voter=voter)

    elif request.method == 'POST':
        voter_id = request.form['id']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        voter_id_new = request.form['voter_id']

        try:
            cursor = mysql_conn.cursor()
            # Update voter details in the database
            update_query = "UPDATE voters SET firstname = %s, lastname = %s, voters_id = %s WHERE id = %s"
            cursor.execute(update_query, (firstname, lastname, voter_id_new, voter_id))
            mysql_conn.commit()
            cursor.close()

            flash('Voter updated successfully', 'success')
            return redirect(url_for('voters'))

        except mysql.connector.Error as e:
            print("Error updating voter details:", e)
            flash('Error updating voter details', 'error')
            return redirect(url_for('voters'))


@app.route('/delete', methods=["GET"])
def delete():
    if request.method == 'GET':
        voter_id = request.args.get('id')

        # Delete the voter from the database
        try:
            cursor = mysql_conn.cursor()
            delete_query = "DELETE FROM voters WHERE id = %s"
            cursor.execute(delete_query, (voter_id,))
            mysql_conn.commit()
            cursor.close()
            flash('Successfully deleted', 'success')
        except mysql.connector.Error as e:
            print("Error deleting from database:", e)
            flash('An error occurred while attempting to delete the record', 'error')

        return redirect(url_for('voters'))


@app.route('/candidates', methods=["GET", "POST"])
def candidates():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['image']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            random_filename = hashlib.md5(filename.encode()).hexdigest() + '.' + file_extension

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_filename))

            firstname = request.form['firstname']
            lastname = request.form['lastname']
            position = request.form['position']
            platform = request.form['platform']

            try:
                cursor = mysql_conn.cursor()
                sql = "INSERT INTO `candidates` (`position_id`, `firstname`, `lastname`, `photo`, `platform`) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (position, firstname, lastname, random_filename, platform))
                mysql_conn.commit()
                cursor.close()
            except mysql.connector.Error as e:
                print("Error inserting into database:", e)
                flash('Error inserting into database', 'error')

            flash('Candidate added successfully', 'success')
            return redirect(url_for('candidates'))

    try:
        cursor = mysql_conn.cursor(dictionary=True)
        select_candidates_query = "SELECT *, candidates.id AS canid FROM candidates LEFT JOIN positions ON positions.id=candidates.position_id ORDER BY positions.priority ASC"
        cursor.execute(select_candidates_query)
        candidates_data = cursor.fetchall()

        select_positions_query = "SELECT * FROM positions"
        cursor.execute(select_positions_query)
        positions_data = cursor.fetchall()

        cursor.close()
    except mysql.connector.Error as e:
        print("Error fetching data from database:", e)
        flash('Error fetching data from database', 'error')
        candidates_data = []
        positions_data = []

    return render_template('candidates.html', candidates_data=candidates_data, positions=positions_data)


@app.route('/editcandidate', methods=["GET", "POST"])
def edit_candidate():
    if request.method == 'GET':
        # Retrieve the candidate ID from the request parameters
        candidate_id = request.args.get('id')

        try:
            cursor = mysql_conn.cursor(dictionary=True)
            # Fetch candidate details based on candidate ID
            select_candidate_query = "SELECT * FROM candidates WHERE id = %s"
            cursor.execute(select_candidate_query, (candidate_id,))
            candidate_data = cursor.fetchone()

            # Fetch positions data to populate the dropdown
            select_positions_query = "SELECT * FROM positions"
            cursor.execute(select_positions_query)
            positions_data = cursor.fetchall()

            cursor.close()
        except mysql.connector.Error as e:
            print("Error fetching data from database:", e)
            flash('Error fetching data from database', 'error')
            return redirect(url_for('candidates'))

        return render_template('editcandidate.html', candidate=candidate_data, positions=positions_data)

    elif request.method == 'POST':
        # Retrieve form data
        candidate_id = request.form['id']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        position_id = request.form['positionid']
        platform = request.form['platform']

        try:
            cursor = mysql_conn.cursor()
            # Update candidate details in the database
            update_query = "UPDATE candidates SET firstname = %s, lastname = %s, position_id = %s, platform = %s WHERE id = %s"
            cursor.execute(update_query, (firstname, lastname, position_id, platform, candidate_id))
            mysql_conn.commit()
            cursor.close()
            flash('Candidate updated successfully', 'success')

        except mysql.connector.Error as e:
            print("Error updating candidate in database:", e)
            flash('Error updating candidate in database', 'error')

        return redirect(url_for('candidates'))  # Redirect to candidates page or handle appropriately


@app.route('/deletecandidate', methods=["GET", "POST"])
def delete_candidate():
    if request.method == 'GET':
        candidate_id = request.args.get('id')
        try:
            cursor = mysql_conn.cursor()
            # Delete the candidate from the database
            delete_query = "DELETE FROM candidates WHERE id = %s"
            cursor.execute(delete_query, (candidate_id,))
            mysql_conn.commit()
            cursor.close()
            flash('Candidate deleted successfully', 'success')
        except Exception as e:
            flash(f'Error deleting candidate: {str(e)}', 'danger')
        finally:
            return redirect(url_for('candidates'))


if __name__ == "__main__":
    app.run(debug=True)
