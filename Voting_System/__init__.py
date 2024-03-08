from flask import Flask, redirect, render_template, request, url_for
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = "My secret key"

mysql_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="votingsystem"
)


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


@app.route('/positions', methods=['GET', 'POST'])
def positions():
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM positions ORDER BY priority ASC")
    positions_result = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        position_id = int(request.form['position_id'])
        position_description = next(
            position['description'] for position in positions_result if position['id'] == position_id)
        position_max_vote = next(position['max_vote'] for position in positions_result if position['id'] == position_id)
        return render_template('position_update.html', position_id=position_id,
                               position_description=position_description, position_max_vote=position_max_vote)

    return render_template('positions.html', positions=positions_result)


@app.route('/position_create', methods=['GET', 'POST'])
def position_create():
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
            cursor = mysql_conn.cursor()
            cursor.execute("INSERT INTO positions (description, max_vote, priority) VALUES (%s, %s, %s)",
                           (position_name, max_votes, priority))
            mysql_conn.commit()
            cursor.close()
            return redirect(url_for('admin_dashboard'))
        else:
            return "MySQL connection failed"
    return render_template('position_create.html')


# @app.route('/position_update', methods=['GET', 'POST'])
# def position_update():
#     if request.method == "POST":
#         position_name = request.form['position_name']
#         max_votes = request.form['max_votes']
#         position_id = request.form['position_id']
#         print(position_id)
#
#         # Determine the new priority
#         cursor = mysql_conn.cursor()
#         cursor.execute("SELECT MAX(priority) FROM positions")
#         max_priority = cursor.fetchone()[0]
#         new_priority = max_priority + 1 if max_priority is not None else 1
#         cursor.close()
#
#         # Update the position in the database
#         if mysql_conn.is_connected():
#             cursor = mysql_conn.cursor(dictionary=True)
#             cursor.execute("UPDATE positions SET description=%s, max_vote=%s, priority=%s WHERE id=%s",
#                            (position_name, max_votes, new_priority, position_id))
#             mysql_conn.commit()
#             cursor.close()
#             return "success"

@app.route('/position_update/<int:position_id>', methods=['GET', 'POST'])
def position_update(position_id):
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

    # Fetch position data from the database
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM positions WHERE id = %s", (position_id,))
    position = cursor.fetchone()
    cursor.close()

    # Pass position data to the template
    return render_template("position_update.html", position_id=position_id,
                           position_name=position['description'], max_votes=position['max_vote'])
