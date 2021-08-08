from helpers import quote, quote_length, login_required, stuck, get_metadata, get_courses, get_progression, get_now, good_work, yt_playlist
import bcrypt
from flask import Flask, flash, redirect, render_template, request, session, send_file
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from tempfile import mkdtemp
from datetime import datetime
import random
import uuid
import time
import csv
from sqlalchemy import create_engine

app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite to use the database
db = create_engine('postgresql+psycopg2://pwbznxyzdvfvsd:90859372f9d60e0a16687c5020f8cbb59389916d8fd545cf06ebff09f836fb01@ec2-54-196-65-186.compute-1.amazonaws.com:5432/dbpf8a9abului7')

# Needed variables
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route("/")
@login_required
def index():
    """First page to show after log in"""
    return redirect("/path")

@app.context_processor
def alert_center():

    data = db.execute("SELECT * FROM alerts ORDER BY alert_id DESC LIMIT 3").fetchall()

    def alert_color_icon(val):
        if val == 1:
            return {'icon': 'fa-exclamation-triangle', 'color': 'danger'}
        elif val == 2:
            return {'icon': 'fa-exclamation-triangle', 'color': 'warning'}
        elif val == 3:
            return {'icon': 'fa-info-circle', 'color': 'info'}
        elif val == 4:
            return {'icon': 'fa-check-circle', 'color': 'success'}

    alerts = []
    for index, row in enumerate(data):
        tmp = {
            'id': row[0],
            'msg': row[1],
            'urgency': alert_color_icon(row[2]),
            'link': row[3],
            'date': datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S').strftime("%B %d, %Y")
        }
        alerts.append(tmp)


    return dict(alerts=alerts, alertslen=len(alerts))

@app.route("/path", methods=["GET", "POST"])
@login_required
def path():
    if request.method == "POST":
        data = get_metadata(request.form.get("linkCourse"))

        if not data:
            flash("Invalid URL or website not supported. Make sure to check if the link is properly working before submiting.")
            return redirect("/path")

        # Query add link
        db.execute("INSERT INTO path (user_id, course_uuid, course_domain, course_url, course_title, course_desc, course_img, finished, created_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", session["user_id"], str(uuid.uuid1()), data['hostname'], data['url'], data['title'], data['desc'], data['img'], 0, get_now())

        # Update progress
        session["progress"] = get_progression()

        # Success message
        flash("Course added successfully.")

    # Display courses
    courses = get_courses(session["user_id"])

    return render_template('path.html', courses=courses)

@app.route("/delete/<uuid>", methods=['POST'])
@login_required
def delete_course(uuid):

    title_deleted = db.execute("SELECT course_title FROM path WHERE course_uuid = %s AND user_id = %s", uuid, session['user_id']).fetchone()
    db.execute("DELETE FROM path WHERE course_uuid = %s AND user_id = %s", uuid, session["user_id"])

    # Show removed item
    flash(f'Course deleted: "{title_deleted[0].strip()}".')

    # Update progress
    session["progress"] = get_progression()

    return redirect("/path")

@app.route("/finish/<uuid>", methods=['POST'])
@login_required
def toggle_finish(uuid):

    curr_progression = db.execute("SELECT finished FROM path WHERE course_uuid = %s AND user_id = %s", uuid, session["user_id"]).fetchone()
    selected_course = db.execute("SELECT course_title FROM path WHERE course_uuid = %s AND user_id = %s", uuid, session["user_id"]).fetchone()

    # Check if finished or not
    if not curr_progression[0]:
        db.execute("UPDATE path SET finished = 1 WHERE course_uuid = %s AND user_id = %s", uuid, session["user_id"])
        flash(f'Congratulation on finishing: {selected_course[0].strip()}.')
    else:
        db.execute("UPDATE path SET finished = 0 WHERE course_uuid = %s AND user_id = %s", uuid, session["user_id"])

    # Update progress
    session["progress"] = get_progression()

    return redirect(f"/path#{uuid}")

@app.route("/timetracker", methods=["GET", "POST"])
@login_required
def timetracker():

    # Get current courses
    current_courses = db.execute("SELECT course_uuid, course_title FROM path WHERE user_id = %s AND finished = 0", session['user_id']).fetchall()

    # Get DESC history
    timetrack_history = db.execute("SELECT * FROM timetracker WHERE user_id = %s ORDER BY started_at DESC", session['user_id']).fetchall()

    # Progress started timetrack
    def tt_progress():
        check_last = db.execute("SELECT * FROM timetracker WHERE user_id = %s ORDER BY started_at DESC LIMIT 1", session['user_id']).fetchone()

        if check_last is not None:
            time_start = datetime.strptime(check_last[4],"%Y-%m-%d %H:%M:%S")
            time_now = datetime.strptime(get_now(),"%Y-%m-%d %H:%M:%S")
            time_inverval = time_now - time_start
            return str(datetime.strptime(str(time_inverval),"%H:%M:%S"))[11:]
        else:
            return False

    return render_template('timetracker.html', current_courses=current_courses, timetrack_history=timetrack_history, progress=tt_progress())

@app.route("/update_tt", methods=["POST"])
@login_required
def update_tt():

    # Get selected course data from path
    get_data = db.execute("SELECT * FROM path WHERE user_id = %s AND course_uuid = %s", session['user_id'], request.form.get("this_course")).fetchone()

    # Return last row to check
    check_last = db.execute("SELECT * FROM timetracker WHERE user_id = %s ORDER BY started_at DESC LIMIT 1", session['user_id']).fetchone()
    check_count = db.execute("SELECT COUNT(*) FROM timetracker WHERE user_id = %s", session['user_id']).fetchone()

    # Timetracker
    if int(check_count[0]) == 0:
        # New history if empty
        db.execute("INSERT INTO timetracker (user_id, course_uuid, course_domain, course_title, started_at, track_uuid) VALUES (%s, %s, %s, %s, %s, %s)", session['user_id'], get_data[1], get_data[2], get_data[4], get_now(), str(uuid.uuid1()))
        flash("Congratulations on starting your first study timesheet. Don't forget to stop the counter once finished.")

    elif check_last[5] and check_last[5] is not None:
        # New row if last row finished
        db.execute("INSERT INTO timetracker (user_id, course_uuid, course_domain, course_title, started_at, track_uuid) VALUES (%s, %s, %s, %s, %s, %s)", session['user_id'], get_data[1], get_data[2], get_data[4], get_now(), str(uuid.uuid1()))
        flash(good_work())

    else:
        # If row history have started_at then add finished_at
        db.execute("UPDATE timetracker SET finished_at = %s WHERE user_id = %s AND course_uuid = %s AND finished_at IS NULL", get_now(), session['user_id'], get_data[1])

        # Calculate difference time
        time_interval = str(datetime.strptime(get_now(),"%Y-%m-%d %H:%M:%S") - datetime.strptime(check_last[4],"%Y-%m-%d %H:%M:%S"))

        # Update duration
        db.execute("UPDATE timetracker SET duration = %s WHERE user_id = %s AND course_uuid = %s AND duration IS NULL", time_interval, session['user_id'], get_data[1])

        # Keep up the good work
        flash(good_work())

    return redirect('/timetracker')

@app.route("/delete_tt/<uuid>", methods=['POST'])
@login_required
def delete_tt(uuid):

    if request.method == 'POST':
        db.execute("DELETE FROM timetracker WHERE track_uuid = %s AND user_id = %s", uuid, session["user_id"])
        flash("Entry removed successfully.")

    return redirect("/timetracker")

@app.route("/motivation")
@login_required
def motivation():
    rand_int = random.randint(0, quote_length())
    return render_template('motivation.html', quote=quote, rand_int=rand_int, yt_playlist=yt_playlist())

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    # Get account details
    user_info = db.execute("SELECT * FROM users WHERE id = %s;", session['user_id']).fetchone()

    # Date created (NOT USED, PREPARED FOR SCALING)
    joined = str(datetime.strftime(datetime.strptime(user_info[6],"%Y-%m-%d %H:%M:%S"), '%B %d, %Y'))

    if request.method == "POST":
        fname = request.form.get("first_name")
        lname = request.form.get("last_name")
        email = request.form.get("email")
        passwd = request.form.get("password")
        new_pass = request.form.get("new_password")
        new_pass_verify = request.form.get("verify_password")

        # 'Reset' data or 'Delete' account
        check_confirmation = request.form.get("check_confirmation")

        # Ensure username exists and password is correct
        checkpassword = bcrypt.checkpw(passwd.encode("utf-8"), user_info[2].encode())
        if not checkpassword:
            flash("Invalid password.")
            return render_template('settings.html', user_info=user_info)

        elif fname and lname and email:
            db.execute("UPDATE users SET email = %s, first_name = %s, last_name = %s WHERE id = %s;", email, fname, lname, session['user_id'])
            user_info = db.execute("SELECT * FROM users WHERE id = %s;", session['user_id']).fetchone()

            session["full_name"] = f'{user_info[3]} {user_info[4]}'
            session["api"] = f'@{user_info[3]}{str(int(time.mktime(datetime.strptime(user_info[6], "%Y-%m-%d %H:%M:%S").timetuple())))[::-1]}'

            flash("Personal details successfully updated.")

        elif new_pass and new_pass_verify:
            if new_pass == new_pass_verify:
                db.execute("UPDATE users SET hash = %s WHERE id = %s;", (bcrypt.hashpw(new_pass.encode("utf-8"), bcrypt.gensalt())).decode(), session['user_id'])
                flash("Password successfully changed.")
            else:
                flash("Please make sure your passwords match.")

        elif check_confirmation:
            if check_confirmation == 'Reset':
                # Delete user from Timetracker & Path
                db.execute("DELETE FROM timetracker WHERE user_id = %s;", session['user_id'])
                db.execute("DELETE FROM path WHERE user_id = %s;", session['user_id'])
                flash("Data reset successfully.")
            elif check_confirmation == 'Delete':
                # Delete user from Timetracker & Path & Users
                db.execute("DELETE FROM timetracker WHERE user_id = %s;", session['user_id'])
                db.execute("DELETE FROM path WHERE user_id = %s;", session['user_id'])
                db.execute("DELETE FROM users WHERE id = %s;", session['user_id'])
                session.clear()
                return redirect("/")

    return render_template('settings.html', user_info=user_info, joined=joined)

@app.route("/settings/dl", methods=['POST'])
@login_required
def download():

    if request.method == 'POST':

        # Query timetracker for records
        data_fields = ['Website', 'Course', 'Started at', 'Ended at', 'Duration']
        data_rows = db.execute("SELECT course_domain, course_title, started_at, finished_at, duration FROM timetracker WHERE user_id = %s", session["user_id"]).fetchall()

        # Random CSV file name
        random_csv = 'timetracker-data' # str(uuid.uuid1())

        # Generate CSV file from database
        with open(f'{random_csv}.csv', 'w', newline='') as f:
            # using csv.writer method from CSV package
            write = csv.writer(f)
            write.writerow(data_fields)
            write.writerows(data_rows)

        # Send file when requested
        return send_file(f'{random_csv}.csv',
                            mimetype='text/csv',
                            attachment_filename=f'{random_csv}.csv',
                            as_attachment=True)

    return redirect("/settings")

@app.route("/faq")
@login_required
def faq():
    return render_template('faq.html')

# Chunk of code from CS50 Finance
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            flash("You must provide an Email.")
            return render_template('login.html')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("You must provide a password.")
            return render_template('login.html')

        # Query database for username
        query = db.execute("SELECT * FROM users WHERE email = %s", request.form.get("email").lower()).fetchone()

        # Check if query None
        if query is None:
            flash("Sorry, we couldn't find an account with that email.")
            return render_template('login.html')

        # Ensure username exists and password is correct
        checkpassword = bcrypt.checkpw(request.form.get("password").encode("utf-8"), query[2].encode())
        if not checkpassword:
            flash("Invalid username and/or password.")
            return render_template('login.html')

        # Remember which user has logged in
        session["user_id"] = query[0]
        session["full_name"] = f'{query[3]} {query[4]}'
        session["api"] = f'@{query[3]}{str(int(time.mktime(datetime.strptime(query[6], "%Y-%m-%d %H:%M:%S").timetuple())))[::-1]}'
        session["progress"] = get_progression()

        # Redirect user to home page
        return redirect("/")

    return render_template('login.html')

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Ensure first and last name were submitted
        if not request.form.get("first_name") or not request.form.get("last_name"):
            flash("Both first and last name are required.")
            return render_template('register.html')

        # Ensure username was submitted
        if not request.form.get("email"):
            flash("You must provide an email.")
            return render_template('register.html')

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("You must provide a password.")
            return render_template('register.html')

        # Password confirmation
        elif request.form.get("password") != request.form.get("password_repeat"):
            flash("Please make sure your passwords match.")
            return render_template('register.html')

        # Register user if email doesn't exist
        result = db.execute("SELECT email FROM users WHERE email = %s", request.form.get("email").lower()).fetchone()

        if result:
            flash("Username already used.")
            return render_template('register.html')

        else:
            # Query database for username
            db.execute("INSERT INTO users (email, hash, first_name, last_name, is_verified, created_at) VALUES(%s, %s, %s, %s, %s, %s)", request.form.get("email").lower(), (bcrypt.hashpw(request.form.get("password").encode('utf-8'), bcrypt.gensalt())).decode(), request.form.get("first_name").capitalize(), request.form.get("last_name").capitalize(), 0, get_now())
            # session["user_id"] = query[0]

            # Alert when registered successfully
            flash("Registered successfully, please login.")

            return render_template("/login.html")

    else:
        return render_template('register.html')

@app.route("/forgot")
def forgot():
    return render_template('forgot.html')

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return stuck(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
