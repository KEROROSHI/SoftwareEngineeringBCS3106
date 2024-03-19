import hashlib
import os
import random
import string
from datetime import datetime

import mysql.connector
import mysql.connector
from flask import Flask, flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="./templates")
app.secret_key = 'your_secret_key'
app.config['SECRET_KEY'] = "8939e180f759844a0a5d0947"

# MySQL configurations
mysql_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="votingsystem"
)

UPLOAD_FOLDER = 'Voting_System/static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def hash_password(password):  # Function to hash the given password when creating a user
    hashed_password = generate_password_hash(password)
    return hashed_password


def checked_hashed_password(fetched_password,
                            attempted_password):  # Function to compare hashed password to the given password
    return check_password_hash(fetched_password, attempted_password)


def get_positions_count(cursor):
    sql = "SELECT COUNT(*) FROM positions"
    cursor.execute(sql)
    return cursor.fetchone()[0]


# Function to get the count of candidates from the database
def get_candidates_count(cursor):
    sql = "SELECT COUNT(*) FROM candidates"
    cursor.execute(sql)
    return cursor.fetchone()[0]


# Function to get the count of voters from the database
def get_voters_count(cursor):
    sql = "SELECT COUNT(*) FROM voters"
    cursor.execute(sql)
    return cursor.fetchone()[0]


# Function to get the count of voters who voted from the database
def get_voters_voted_count(cursor):
    sql = "SELECT COUNT(DISTINCT voters_id) FROM votes"
    cursor.execute(sql)
    return cursor.fetchone()[0]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_voter_id(length=15):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def hashed_password(password):
    return generate_password_hash(password)


def check_password(password, hashed_password):
    return check_password_hash(hashed_password, password)


def get_total_votes(cursor):
    sql = "SELECT COUNT(*) from votes"
    cursor.execute(sql)
    return cursor.fetchone()[0]


def get_top_candidates(cursor):
    sql = """SELECT c.firstname, c.lastname, COUNT(*) as votes_count FROM votes v 
                JOIN candidates c ON v.candidate_id = c.id GROUP BY v.candidate_id ORDER BY votes_count DESC"""
    cursor.execute(sql)
    return cursor.fetchall()


def get_voter_turnout(cursor):
    total_voters = get_voters_count(cursor)
    voters_voted = get_voters_voted_count(cursor)

    if total_voters == 0:
        return 0

    turnout_percentage = (voters_voted / total_voters) * 100
    return turnout_percentage


@app.route('/')
def hello_world():
    return render_template('voterslandingpage.html')


@app.route('/admin/voters', methods=["GET", "POST"])
def voters():
    if 'username' in session:
        if request.method == 'POST':
            # Check if the post request has the file part
            if 'image' not in request.files:
                flash('No file part', category='danger')
                return redirect(request.url)

            file = request.files['image']
            print(file.filename)

            # If the user does not select a file, the browser submits an empty file without a filename.
            if file.filename == '':
                flash('No uploaded picture. A default one has been assigned to the voter!', category='info')

            if file and allowed_file(file.filename):
                # Secure the filename before saving it
                filename = secure_filename(file.filename)

                # Generate a unique filename to prevent overwriting files
                file_extension = filename.rsplit('.', 1)[1].lower()
                random_filename = hashlib.md5(filename.encode()).hexdigest() + '.' + file_extension

                # Save the file to the upload folder
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_filename))
            else:
                random_filename = ''

            # Process form data
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            password = request.form['password']

            # Hash the password using the function
            hashed_pass = hashed_password(password)

            # Generate voter ID
            voter_id = generate_voter_id()

            # Insert data into the database
            try:
                cursor = mysql_conn.cursor()
                # Create a new record
                sql = """INSERT INTO `voters` (`voters_id`, `password`, `firstname`, `lastname`, `photo`) 
                            VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (voter_id, hashed_pass, firstname, lastname, random_filename))
                mysql_conn.commit()
                cursor.close()
            except mysql.connector.Error as e:
                print("Error inserting into database:", e)
                flash('Error inserting into database', category='error')

            flash('Voter added successfully', category='success')
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
            flash('Error fetching data from database', category='error')
            voters_data = []

        placeholder_photo = '/static/images/istockphoto-1327592449-612x612.jpg'
        return render_template('voters.html', voters_data=voters_data,
                               placeholder_photo=placeholder_photo)
    else:
        flash("You must be logged in as an Administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin/edit_voter', methods=["GET", "POST"])
def edit_voter():
    if 'username' in session:
        if request.method == 'GET':
            voter_id = request.args.get('id')

            try:
                cursor = mysql_conn.cursor(dictionary=True)
                # Fetch voter details based on voter ID
                select_query = "SELECT * FROM voters WHERE id = %s"
                cursor.execute(select_query, (voter_id,))
                voter = cursor.fetchone()

                if not voter:
                    flash('Voter not found', category='error')
                    return redirect(url_for('voters'))

                cursor.close()
            except mysql.connector.Error as e:
                print("Error fetching voter details:", e)
                flash('Error fetching voter details', category='error')
                return redirect(url_for('voters'))

            return render_template('edit_voter.html', voter=voter)

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

                flash('Voter updated successfully', category='success')
                return redirect(url_for('voters'))

            except mysql.connector.Error as e:
                print("Error updating voter details:", e)
                flash('Error updating voter details', category='error')
                return redirect(url_for('voters'))
    else:
        flash("You must be logged in as an Administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin/delete', methods=["GET"])
def delete():
    if 'username' in session:
        if request.method == 'GET':
            voter_id = request.args.get('id')

            # Delete the voter from the database
            try:
                cursor = mysql_conn.cursor()
                delete_query = "DELETE FROM voters WHERE id = %s"
                cursor.execute(delete_query, (voter_id,))
                mysql_conn.commit()
                cursor.close()
                flash('Successfully deleted', category='success')
            except mysql.connector.Error as e:
                print("Error deleting from database:", e)
                flash('An error occurred while attempting to delete the record', category='error')

            return redirect(url_for('voters'))
    else:
        flash("You must be logged in as an Administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin/candidates', methods=["GET", "POST"])
def candidates():
    if 'username' in session:
        if request.method == 'POST':
            if 'image' not in request.files:
                flash('No file part', category='danger')
                return redirect(request.url)

            file = request.files['image']

            # If the user does not select a file, the browser submits an empty file without a filename.
            if file.filename == '':
                flash('No uploaded picture. A default one has been assigned to the candidate!', category='info')

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_extension = filename.rsplit('.', 1)[1].lower()
                random_filename = hashlib.md5(filename.encode()).hexdigest() + '.' + file_extension

                file.save(os.path.join(app.config['UPLOAD_FOLDER'], random_filename))
            else:
                random_filename = ''

            firstname = request.form['firstname']
            lastname = request.form['lastname']
            position = request.form['position']
            platform = request.form['platform']

            try:
                cursor = mysql_conn.cursor()
                sql = """INSERT INTO `candidates` (`position_id`, `firstname`, `lastname`, `photo`, `platform`) 
                            VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (position, firstname, lastname, random_filename, platform))
                mysql_conn.commit()
                cursor.close()
            except mysql.connector.Error as e:
                print("Error inserting into database:", e)
                flash('Error inserting into database', category='error')

            flash('Candidate added successfully', category='success')
            return redirect(url_for('candidates'))

        try:
            cursor = mysql_conn.cursor(dictionary=True)
            select_candidates_query = """SELECT *, candidates.id AS canid FROM candidates 
                                            LEFT JOIN positions ON positions.id=candidates.position_id 
                                            ORDER BY positions.priority ASC"""
            cursor.execute(select_candidates_query)
            candidates_data = cursor.fetchall()

            select_positions_query = "SELECT * FROM positions"
            cursor.execute(select_positions_query)
            positions_data = cursor.fetchall()

            cursor.close()
        except mysql.connector.Error as e:
            print("Error fetching data from database:", e)
            flash('Error fetching data from database', category='error')
            candidates_data = []
            positions_data = []

        placeholder_photo = '/static/images/istockphoto-1327592449-612x612.jpg'
        return render_template('candidates.html', candidates_data=candidates_data,
                               positions=positions_data,
                               placeholder_photo=placeholder_photo)
    else:
        flash("You must be logged in as an Administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin/edit_candidate', methods=["GET", "POST"])
def edit_candidate():
    if 'username' in session:
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
                flash('Error fetching data from database', category='error')
                return redirect(url_for('candidates'))

            return render_template('edit_candidate.html', candidate=candidate_data,
                                   positions=positions_data)

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
                update_query = """UPDATE candidates SET firstname = %s, lastname = %s, position_id = %s, platform = %s 
                                    WHERE id = %s"""
                cursor.execute(update_query, (firstname, lastname, position_id, platform, candidate_id))
                mysql_conn.commit()
                cursor.close()
                flash('Candidate updated successfully', category='success')

            except mysql.connector.Error as e:
                print("Error updating candidate in database:", e)
                flash('Error updating candidate in database', category='error')

            return redirect(url_for('candidates'))  # Redirect to candidates page or handle appropriately
    else:
        flash("You must be logged in as an Administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin/delete_candidate', methods=["GET", "POST"])
def delete_candidate():
    if 'username' in session:
        if request.method == 'GET':
            candidate_id = request.args.get('id')
            try:
                cursor = mysql_conn.cursor()
                # Delete the candidate from the database
                delete_query = "DELETE FROM candidates WHERE id = %s"
                cursor.execute(delete_query, (candidate_id,))
                mysql_conn.commit()
                cursor.close()
                flash('Candidate deleted successfully', category='success')
            except Exception as e:
                flash(f'Error deleting candidate: {str(e)}', category='danger')
            finally:
                return redirect(url_for('candidates'))
    else:
        flash("You must be logged in as an Administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    print(session)
    if 'voters_id' not in session or 'id' not in session or 'voters_name' not in session:
        if 'username' not in session:
            if request.method == 'POST':
                # Takes the data from the form
                username = request.form['username']
                password = request.form['password']
                if username == '':
                    flash('Username is required', category='danger')
                    return redirect(url_for('admin_login'))
                elif password == '':
                    flash('Password is required', category='danger')
                    return redirect(url_for('admin_login'))
                # Fetches the user data form the database
                cursor = mysql_conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
                mysql_result = cursor.fetchone()
                print(mysql_result)
                cursor.close()

                if mysql_result is None:
                    # Handle case where no admin with the provided username exists
                    flash("User does not exist", category='danger')
                    return redirect(url_for('admin_login'))

                fetched_password = mysql_result['password']
                print(fetched_password)
                print(password)
                # Confirms the given password's hash value matches with the value retrieved from the database
                password_checker = checked_hashed_password(fetched_password, password)
                if mysql_result['username'] == username and password_checker is True:
                    # Set session of the successfully logged-in user/admin
                    session['username'] = username
                    if mysql_result['voting_session_id'] is not None:
                        session['voting_session_id'] = mysql_result['voting_session_id']
                        print(f'This :{session["voting_session_id"]}')
                    else:
                        session['voting_session_id'] = random.randint(8000000, 80000000)
                        cursor = mysql_conn.cursor()
                        cursor.execute('UPDATE admin SET voting_session_id=%s WHERE username=%s',
                                       (session['voting_session_id'], username,))
                        mysql_conn.commit()
                        cursor.close()
                    cursor = mysql_conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM session where voting_session_id=%s", (session['voting_session_id'],))
                    session_result = cursor.fetchone()
                    cursor.close()
                    print(session['username'])
                    print(session['voting_session_id'])
                    flash("Successfully logged-in!", category='success')
                    if session_result:
                        flash(f'Current Session is {session_result["election_title"]}', category='info')
                    else:
                        flash('The is no session currently created!', category='info')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash("Invalid username or password", category='danger')
                    return redirect(url_for('admin_login'))
            return render_template('admin_login.html')
        else:
            flash("You are already logged-in!", category='info')
            return redirect(url_for('admin_dashboard'))
    else:
        flash("You must log out as a voter to log in as an Administrator!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin_logout')
def admin_logout():
    # Destroys the session that was set when the user clicks the logout button in the navbar
    session.pop('username', None)
    return redirect(url_for('admin_login'))


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'username' in session:
        cursor_non_dict = mysql_conn.cursor()
        cursor = mysql_conn.cursor(dictionary=True)
        voter_turnout = get_voter_turnout(cursor_non_dict)
        total_votes = get_total_votes(cursor_non_dict)
        top_candidates = get_top_candidates(cursor)
        print(top_candidates)

        if request.method == 'POST' and 'reset_votes' in request.form:
            # Reset votes by deleting records from specified tables
            tables_to_reset = ['candidates', 'positions', 'voters', 'votes']
            for table in tables_to_reset:
                if table != 'admin':
                    cursor_non_dict.execute(f"TRUNCATE TABLE {table}")

            flash("Successfully reset votes and deleted records.", category='success')

        return render_template('admin_dashboard.html', top_candidates=top_candidates,
                               total_votes=total_votes,
                               voter_turnout=voter_turnout)
    else:
        flash("You must be logged in as an Administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def dashboard():
    if 'username' in session:
        # Establish database connection
        cursor = mysql_conn.cursor()

        # Execute SQL queries
        positions_count = get_positions_count(cursor)
        candidates_count = get_candidates_count(cursor)
        voters_count = get_voters_count(cursor)
        voters_voted_count = get_voters_voted_count(cursor)

        # Close database connection
        cursor.close()
        return render_template('dashboard.html', positions_count=positions_count,
                               candidates_count=candidates_count,
                               voters_count=voters_count, voters_voted_count=voters_voted_count)
    else:
        flash("You must be logged in as an Administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/voter_login', methods=['GET', 'POST'])
def voter_login():
    print(session)
    if 'username' not in session:
        if 'voters_id' not in session or 'id' not in session or 'voters_name' not in session:
            if request.method == 'POST':
                voters_id = request.form['voters_id']
                password = request.form['password']
                print(voters_id, password)
                if voters_id == '':
                    flash("Voters ID is required", category='danger')
                    return redirect(url_for('voter_login'))
                elif password == '':
                    flash("Password is required", category='danger')
                    return redirect(url_for('voter_login'))
                cursor = mysql_conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM voters WHERE voters_id = %s", (voters_id,))
                results = cursor.fetchone()
                cursor.close()
                print(results)
                if results is None:
                    flash("Voter ID does not exists!", category='danger')
                    return redirect('voter_login')
                confirm_password = checked_hashed_password(results['password'], password)
                if results['voters_id'] == voters_id and confirm_password is True:
                    session['id'] = results['id']
                    session['voters_id'] = voters_id
                    session['voters_name'] = results['firstname'] + ' ' + results['lastname']
                    print(session)
                    flash("You have successfully logged-in!", category='success')
                    return redirect(url_for('ballot'))
                elif not confirm_password:
                    flash("Invalid Voter ID or Password!", category='danger')
                    return redirect(url_for('voter_login'))
            return render_template('voter_login.html')
        else:
            flash("You are already logged in!", category='info')
            return redirect(url_for('ballot'))
    else:
        flash("You must log out as an Administrator to log in as a Voter!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/voter_logout')
def voter_logout():
    # Destroys the session that was set when the user clicks the logout button in the navbar
    cursor = mysql_conn.cursor()
    cursor.execute('UPDATE voters SET voting_session_id=Null WHERE voters_id=%s', (session['voters_id'],))
    mysql_conn.commit()
    cursor.close()
    session.pop('id', None)
    session.pop('voters_id', None)
    session.pop('voters_name', None)
    return redirect(url_for('voter_login'))


@app.route('/admin/positions', methods=['GET', 'POST'])
def positions():
    print(session)
    # Checks if the admin is logged-in in order to access the page
    if 'username' in session:
        # Fetch data position data from database
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM positions ORDER BY priority ASC")
        positions_result = cursor.fetchall()
        print(positions_result)
        cursor.close()

        if request.method == 'POST':
            position_id = int(request.form['position_id'])
            # Iterate over the dictionary to find and return specific values from the dictionary
            position_description = next(
                position['description'] for position in positions_result if position['id'] == position_id)
            position_max_vote = next(
                position['max_vote'] for position in positions_result if position['id'] == position_id)
            return render_template('position_update.html', position_id=position_id,
                                   position_description=position_description, position_max_vote=position_max_vote)
        return render_template('positions.html', positions=positions_result)
    else:
        flash("You must be logged in as an administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin/position_create', methods=['GET', 'POST'])
def position_create():
    # Checks if the admin is logged-in in order to access the page
    if 'username' in session:
        # Fetches data from the database
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM positions ORDER BY priority desc LIMIT 1")
        positions_result = cursor.fetchall()
        if positions_result:
            priority = positions_result[0]['priority'] + 1
        else:
            priority = 1
        cursor.close()
        if request.method == 'POST':
            position_name = request.form['position_name']
            max_votes = request.form['max_votes']
            print("MySQL connection is", mysql_conn)
            if mysql_conn.is_connected():
                # Inserts position data into the database
                cursor = mysql_conn.cursor()
                cursor.execute("INSERT INTO positions (description, max_vote, priority) VALUES (%s, %s, %s)",
                               (position_name, max_votes, priority))
                mysql_conn.commit()
                cursor.close()
                flash('Position added successfully!', category='success')
                return redirect(url_for('positions'))
            else:
                flash('An error has occurred!', category='error')
                return "MySQL connection failed"
        return render_template('position_create.html')
    else:
        flash("You must be logged in as an administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin/position_update/<int:position_id>', methods=['GET', 'POST'])
def position_update(position_id):
    print(session)
    # Checks if the admin is logged-in in order to access the page
    if 'username' in session:
        # Fetch position data from the database
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM positions WHERE id = %s", (position_id,))
        position = cursor.fetchone()
        cursor.close()

        if request.method == "POST":
            position_name = request.form['position_name']
            max_votes = request.form['max_votes']

            # Update the position in the database
            if mysql_conn.is_connected():
                cursor = mysql_conn.cursor()
                cursor.execute("UPDATE positions SET description=%s, max_vote=%s WHERE id=%s",
                               (position_name, max_votes, position_id))
                mysql_conn.commit()
                cursor.close()
                flash("Position details updated successfully", category='success')
                return redirect(url_for('positions'))  # Redirect to the positions page after update
            else:
                flash('An error has occurred!', category='error')
                return "MySQL connection failed"

        # Pass position data to the template
        return render_template("position_update.html", position_id=position_id,
                               position_name=position['description'], max_votes=position['max_vote'])
    else:
        flash("You must be logged in as an administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/admin/position_delete/<int:position_id>', methods=['GET', 'POST'])
def position_delete(position_id):
    print(session)
    # Checks if the admin is logged-in in order to access the page
    if 'username' in session:
        if mysql_conn.is_connected():
            # Deletes data from teh database
            cursor = mysql_conn.cursor(dictionary=True)
            cursor.execute("DELETE FROM positions WHERE id=%s", (position_id,))
            mysql_conn.commit()
            cursor.close()
            flash('The position has been deleted!', category='info')
            return redirect(url_for('positions'))
        else:
            flash('An error has occurred!', category='error')
            return "MySQL connection failed"
    else:
        flash("You must be logged in as an administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/voter/ballot', methods=['GET', 'POST'])
def ballot():
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM session WHERE end_date is Null and start_date is not Null')
    session_result = cursor.fetchone()
    cursor.close()
    if session_result:
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute('UPDATE voters SET voting_session_id=%s WHERE voters_id=%s',
                       (session_result['voting_session_id'], session['voters_id'],))
        mysql_conn.commit()
        cursor.close()
        elec_title = session_result['election_title']
        if 'voters_id' in session:
            cursor = mysql_conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM votes WHERE voters_id = %s", (session['id'],))
            # print(session['id'])
            votes = cursor.fetchall()
            # print(votes)
            cursor.close()
            if len(votes) > 0:
                flash("You have already voted for this", category='danger')
                return redirect(url_for('already_voted'))
            else:
                cursor = mysql_conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM positions ORDER BY priority ASC")
                positions = cursor.fetchall()
                cursor.close()
                for position in positions:
                    cursor = mysql_conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM candidates WHERE position_id = %s", (position['id'],))
                    candidates = cursor.fetchall()
                    cursor.close()
                    for candidate in candidates:
                        checked = ''
                        if position['description'] in request.form:
                            value = request.form.getlist(position['description'])
                            if str(candidate['id']) in value:
                                checked = 'checked'
                        input_type = 'checkbox' if position['max_vote'] > 1 else 'radio'
                        candidate[
                            'input'] = f'<input type="{input_type}" class="flat-red {position["description"]}" name="{position["description"]}" value="{candidate["id"]}" {checked}>'
                        candidate['image'] = candidate['photo'] if candidate[
                            'photo'] else url_for("static", filename="images/9691288a3fadba6a8e6173d4eea20488.jpg")
                    position['instruct'] = f'You may select up to {position["max_vote"]} candidates' if position[
                                                                                                            'max_vote'] > 1 else 'Select only one candidate'
                    position['candidates'] = candidates
                placeholder_photo = '/static/images/istockphoto-1327592449-612x612.jpg'
                return render_template('ballot.html', positions=positions, placeholder_photo=placeholder_photo,
                                       elec_title=elec_title)
        else:
            flash('Please login to access that page!', category='danger')
            return redirect(url_for('voter_login'))
    else:
        flash('There is no available session to vote for!', category='info')
        return render_template('no_voter_session.html')


@app.route('/voter/submit_ballot', methods=['POST'])
def submit_ballot():
    if 'voters_id' in session:
        if request.method == 'POST':
            cursor = mysql_conn.cursor(dictionary=True)
            if 'vote' in request.form:
                if len(request.form) == 1:
                    flash('Please vote for at least one candidate', category='danger')
                    return redirect(url_for('ballot'))
                else:
                    # print(request.form)
                    session['post'] = request.form
                    # print(session)
                    cursor.execute("SELECT * FROM positions")
                    positions = cursor.fetchall()
                    error = False
                    sql_array = []
                    for position in positions:
                        pos_id = position['id']
                        print(f"The {position['description']}")
                        if position['description'] in request.form:
                            # print(position['description'])
                            if position['max_vote'] > 1:
                                if len(request.form.getlist(position['description'])) > position['max_vote']:
                                    error = True
                                    # print(position['description'])
                                    flash('You can only choose ' + str(position['max_vote']) + ' candidates for ' +
                                          position['description'], category='danger')
                                else:
                                    for candidate in request.form.getlist(position['description']):
                                        # print(candidate)
                                        sql_array.append(
                                            (
                                                "INSERT INTO votes (voters_id, candidate_id, position_id) VALUES (%s, %s, %s)",
                                                (session['id'], candidate, pos_id)))
                            else:
                                candidate = request.form[position['description']]
                                # print(candidate)
                                sql_array.append(
                                    ("INSERT INTO votes (voters_id, candidate_id, position_id) VALUES (%s, %s, %s)",
                                     (session['id'], candidate, pos_id)))
                        else:
                            print("Error")
                            flash('You must vote for at least one candidate from each position!', category='danger')
                            return redirect(url_for('ballot'))
                    if not error:
                        try:
                            for sql_query, values in sql_array:
                                cursor.execute(sql_query, values)
                                mysql_conn.commit()
                            if 'post' in session:
                                session.pop('post', None)
                            flash('Ballot Submitted', category='success')
                            return redirect(url_for('already_voted'))
                        except Exception as e:
                            mysql_conn.rollback()  # Rollback in case of any error
                            flash('An error occurred while submitting the ballot!', category='danger')
                            print("An error occurred: ", e)
                            return redirect(url_for('ballot'))
            else:
                flash('Select candidates to vote first!', category='error')
                return redirect(url_for('ballot'))
        return redirect(url_for('ballot'))  # Redirect to the ballot page if method is not POST
    else:
        return redirect(url_for('voter_login'))  # Redirect to the login page if voters_id is not in session


@app.route('/voter/ballot/already_voted')
def already_voted():
    return render_template('already_voted.html')


@app.route('/admin/ballot_position')
def ballot_position():
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM positions ORDER BY priority ASC")
    positions = cursor.fetchall()
    cursor.close()
    for position in positions:
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM candidates WHERE position_id = %s", (position['id'],))
        candidates = cursor.fetchall()
        cursor.close()
        for candidate in candidates:
            checked = ''
            if position['description'] in request.form:
                value = request.form.getlist(position['description'])
                if str(candidate['id']) in value:
                    checked = 'checked'
            input_type = 'checkbox' if position['max_vote'] > 1 else 'radio'
            candidate[
                'input'] = f'<input type="{input_type}" class="flat-red {position["description"]}" name="{position["description"]}" value="{candidate["id"]}" {checked}>'
            candidate['image'] = candidate['photo'] if candidate[
                'photo'] else url_for("static", filename="images/9691288a3fadba6a8e6173d4eea20488.jpg")
        position['instruct'] = f'You may select up to {position["max_vote"]} candidates' if position[
                                                                                                'max_vote'] > 1 else 'Select only one candidate'
        position['candidates'] = candidates
    placeholder_photo = '/static/images/istockphoto-1327592449-612x612.jpg'
    return render_template('ballot_position.html', positions=positions, placeholder_photo=placeholder_photo)


@app.route('/create_session', methods=['GET', 'POST'])
def create_session():
    if 'voting_session_id' not in session:
        session['voting_session_id'] = random.randint(8000000, 80000000)
        cursor = mysql_conn.cursor()
        cursor.execute('UPDATE admin SET voting_session_id=%s WHERE username=%s',
                       (session['voting_session_id'], session['username'],))
        mysql_conn.commit()
        cursor.close()
    cursor = mysql_conn.cursor()
    cursor.execute('SELECT * from session where voting_session_id = %s', (session['voting_session_id'],))
    session_result = cursor.fetchone()
    cursor.close()
    if session_result is None:
        elec_title = request.form['election_title']
        voting_session = 0
        cursor = mysql_conn.cursor()
        cursor.execute('INSERT INTO session(election_title,voting_session,voting_session_id)VALUES (%s,%s,%s)',
                       (elec_title, voting_session, session["voting_session_id"]))
        mysql_conn.commit()
        cursor.close()
        session['election_title'] = elec_title
        flash('Voting session successfully created!', category='success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash(
            "A voting session has already been created. You'll need to end the current session to create and start a new one!",
            category='danger')
        return redirect(url_for('admin_dashboard'))


@app.route('/start_session', methods=['GET', 'POST'])
def start_session():
    if 'voting_session_id' in session:
        print(session['voting_session_id'])
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute('SELECT * from session where voting_session_id = %s', (session['voting_session_id'],))
        session_result = cursor.fetchone()
        print(session)
        print(session_result)
        cursor.close()
        if session_result:
            if session_result['voting_session'] == 0:
                voting_session = 1
                voting_session_id = session['voting_session_id']
                start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor = mysql_conn.cursor()
                cursor.execute(
                    'UPDATE session SET voting_session=%s,start_date=%s,voting_session_id=%s where election_title=%s',
                    (voting_session, start_date, voting_session_id, session['election_title'],))
                mysql_conn.commit()
                cursor.close()
                flash('The voting session has been started successfully!', category='success')
                return redirect(url_for('admin_dashboard'))
            elif session_result['voting_session'] == 1:
                flash('A voting session has already been started. End the current voting session to start a new one.',
                      category='danger')
                return redirect(url_for('admin_dashboard'))
            elif session_result['voting_session'] == 2:
                flash('This voting session has already been ended!', category='danger')
                return redirect(url_for('admin_dashboard'))
            elif session_result['voting_session'] is None:
                flash('Invalid voting session state!', category='danger')
                return redirect(url_for('admin_dashboard'))
        else:
            flash('A voting session has not been created. Create one in order to start it', category='danger')
            return redirect(url_for('admin_dashboard'))
    else:
        flash('A voting session has not been created. Create one in order to start it', category='danger')
        return redirect(url_for('admin_dashboard'))


@app.route('/end_session')
def end_session():
    if 'voting_session_id' in session:
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute('SELECT * from session where voting_session_id = %s', (session['voting_session_id'],))
        session_result = cursor.fetchone()
        print(session_result)
        cursor.close()
        if session_result:
            if session_result['voting_session'] == 1:
                voting_session = 2
                end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor = mysql_conn.cursor()
                cursor.execute('UPDATE session SET voting_session=%s,end_date=%s WHERE election_title=%s',
                               (voting_session, end_date, session['election_title'],))
                mysql_conn.commit()
                cursor.execute('UPDATE admin SET voting_session_id=Null WHERE username=%s', (session['username'],))
                mysql_conn.commit()
                cursor.close()
                session.pop("voting_session_id", None)
                flash('Voting session successfully ended!', category='success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('A session has to be started in order to be ended!', category='danger')
                return redirect(url_for('admin_dashboard'))
        else:
            flash('A session has not been created or started. Please create and start one in order to end it!',
                  category='danger')
            return redirect(url_for('admin_dashboard'))
    else:
        flash('A session has not been created or started. Please create and start one in order to end it!',
              category='danger')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/election_title')
def election_title():
    elec_title = session['election_title']
    return render_template('election_title.html', election_title=elec_title)
