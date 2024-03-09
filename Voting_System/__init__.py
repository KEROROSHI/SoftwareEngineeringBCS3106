import mysql.connector
from flask import Flask, flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = "8939e180f759844a0a5d0947"

mysql_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="votingsystem"
)


@app.route('/')
def hello_world():
    return render_template('base.html')


def hash_password(password):  # Function to hash the given password when creating a user
    hashed_password = generate_password_hash(password)
    return hashed_password


def checked_hashed_password(fetched_password,
                            attempted_password):  # Function to compare hashed password to the given password
    return check_password_hash(fetched_password, attempted_password)


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Takes the data from the form
        username = request.form['username']
        password = request.form['password']
        # Fetches the user data form the database
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
        mysql_result = cursor.fetchone()
        print(mysql_result)
        cursor.close()

        if mysql_result is None:
            # Handle case where no admin with the provided username exists
            flash("User does not exist")
            return redirect(url_for('admin_login'))

        fetched_password = mysql_result['password']
        print(fetched_password)
        print(password)
        # Confirms the given password's hash value matches with the value retrieved from the database
        password_checker = checked_hashed_password(fetched_password, password)
        if mysql_result['username'] == username and password_checker is True:
            # Set session of the successfully logged-in user/admin
            session['username'] = username
            print(session['username'])
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid username or password", category='danger')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')


@app.route('/admin_logout')
def admin_logout():
    # Destroys the session that was set when the user clicks the logout button in the navbar
    session.pop('username', None)
    return redirect(url_for('admin_login'))


@app.route('/admin_dashboard')
def admin_dashboard():
    print(session)
    # Checks if the admin is logged-in in order to access the page
    if 'username' in session:
        return render_template('admin_dashboard.html')
    else:
        flash("You must be logged in as an administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/voter', methods=['GET', 'POST'])
def voter_login():
    if request.method == 'POST':
        voters_id = request.form['voters_id']
        password = request.form['password']
        if voters_id is None:
            flash("Voters ID is required", category='danger')
            return redirect(url_for('voter_login'))
        elif password is None:
            flash("Password is required", category='danger')
            return redirect(url_for('voter_login'))
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM voters WHERE voters_id = %s", (voters_id,))
        results = cursor.fetchone()
        cursor.close()
        print(results)
        confirm_password = checked_hashed_password(results['password'], password)
        if results is None:
            flash("Voter ID does not exists!", category='danger')
            return redirect('voter_login')
        elif results['voters_id'] == voters_id and confirm_password is True:
            session['voters_id'] = voters_id
            session['voters_name'] = results['firstname'] + ' ' + results['lastname']
            flash("You have successfully logged-in!", category='success')
            return redirect(url_for('ballot'))
        elif not confirm_password:
            flash("Invalid Voter ID or Password!", category='danger')
            return redirect(url_for('voter_login'))
    return render_template('voter_login.html')


@app.route('/voter_logout')
def voter_logout():
    # Destroys the session that was set when the user clicks the logout button in the navbar
    session.pop('voter_id', None)
    session.pop('voters_name', None)
    return redirect(url_for('voter_login'))


@app.route('/positions', methods=['GET', 'POST'])
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


@app.route('/position_create', methods=['GET', 'POST'])
def position_create():
    # Checks if the admin is logged-in in order to access the page
    if 'username' in session:
        # Fetches data from the database
        cursor = mysql_conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM positions ORDER BY priority desc LIMIT 1")
        positions_result = cursor.fetchall()
        priority = positions_result[0]['priority'] + 1
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
                return redirect(url_for('admin_dashboard'))
            else:
                return "MySQL connection failed"
        return render_template('position_create.html')
    else:
        flash("You must be logged in as an administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/position_update/<int:position_id>', methods=['GET', 'POST'])
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
                return redirect(url_for('positions'))  # Redirect to the positions page after update
            else:
                return "MySQL connection failed"

        # Pass position data to the template
        return render_template("position_update.html", position_id=position_id,
                               position_name=position['description'], max_votes=position['max_vote'])
    else:
        flash("You must be logged in as an administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/position_delete/<int:position_id>', methods=['GET', 'POST'])
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
            return redirect(url_for('positions'))
        else:
            return "MySQL connection failed"
    else:
        flash("You must be logged in as an administrator to access that page!", category='danger')
        return redirect(url_for('admin_login'))


@app.route('/ballot', methods=['GET', 'POST'])
def ballot():
    cursor = mysql_conn.cursor(dictionary=True)
    print(session)

    if 'voters_id' in session:
        cursor.execute("SELECT * FROM votes WHERE voters_id = %s", (session['voters_id'],))
        votes = cursor.fetchall()
        cursor.close()

        if len(votes) > 0:
            flash("You have already voted for this")
            return render_template('already_voted.html')
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
                        'input'] = f'<input type="{input_type}" class="flat-red {position["description"]}" name="{position["description"]}[]" value="{candidate["id"]}" {checked}>'
                    candidate['image'] = candidate['photo'] if candidate[
                        'photo'] else 'images/9691288a3fadba6a8e6173d4eea20488.jpg'
                position['instruct'] = f'You may select up to {position["max_vote"]} candidates' if position[
                                                                                                        'max_vote'] > 1 else 'Select only one candidate'
                position['candidates'] = candidates
            return render_template('ballot.html', positions=positions)
    else:
        return redirect(url_for('voter_login'))


@app.route('/submit_ballot', methods=['GET', 'POST'])
def submit_ballot():
    return render_template('base.html')
