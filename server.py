"""View medMinder site."""
from flask import Flask, session, render_template, url_for, request, flash, redirect, jsonify
# Import SQLAlchemy constructor functionn
from flask_sqlalchemy import SQLAlchemy
from model import connect_to_db, db
import crud
import rx_search
from jinja2 import StrictUndefined
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.jinja_env.undefined = StrictUndefined


# Creates route to view homepage
@app.route("/")
def home():
    """View homepage."""

    return render_template("homepage.html")


# Route for user login
@app.route("/login", methods=["POST", "GET"])
def login():
    """Process login for user."""

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = crud.get_user_by_email(email)

        if user and user.password == password:
        # if user.id and user.password == password:
            session['user_id'] = user.user_id
            flash(f"Hello, {user.fname}!")
        return redirect('/profile')

    # If login fails, display a message asking the user to try logging in again
    else:
        flash('The email or password you entered is incorrect. Please try again.')
    return render_template('homepage.html')


# Route for user to register for account
@app.route('/register', methods=['POST', 'GET'])
def register_user():
    """Register a user."""

    if request.method =='POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user is exists
        existing_user = crud.get_user_by_email('email')

        # If user is registered but not logged in, redirect user to login
        if existing_user:
            # Display a message asking the user to login
            flash('A user account already exists with this email. Please log into your account.')
            # Take user to the login form
            return redirect('/login')

        # Add new user to the database
        new_user = crud.add_new_user(fname, lname, email, password)

        # Save user to session
        session['user_id'] = new_user.user_id
        # Display message confirming successful login
        flash(f'Welcome, {fname}! Thank you for registering with medMinder.')
        # If login successful, redirect to profile page
        return redirect ('/profile')

    return render_template('register.html')


# Route to view profile
@app.route('/profile')
def view_profile():
    """View user profile."""

    user_id = session.get('user_id')
    existing_user = crud.get_user_by_id(user_id)

    if existing_user:
        # Retrieve User's prescriptions
        user_prescriptions = existing_user.prescriptions

    # Create list to store results
    results = []

    return render_template('profile.html', user=existing_user, results=results)


# Route to handle user selecting a med
@app.route('/profile', methods =['POST'])
def add_prescription():

    # Get data and extract brand name, generic name, and unii
    data = request.json
    brand_name = data.get('brandName')
    generic_name = data.get('genericName')
    unii = data.get('unii')

    # Check if user in session
    user_id = session.get('user_id')
    # If user logged in, get user from the database
    if user_id:
        user = crud.get_user_by_id(user_id)

        # Add a new prescription which is linked to medication and user
        prescription = crud.create_prescription(brand_name, generic_name, unii)
        user.prescriptions.append(prescription)
        db.session.commit()

        # Return JSON response confirming prescription added
        return jsonify({'brandName': brand_name, 'message':'New prescription added successfully'})

    # If user not logged in:
    return jsonify({'Error':'Please try logging in'})


if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True)

# Add route for user to edit a prescription
# @app.route('/edit_prescription', methods='POST')
# def edit_prescription():

    # check if prescription is in db
    # if prescription already exists...
    # redirect to prescriptions list where user can choose and edit a prescription
    # if prescription doesn't exist, display 'not found' message to user
    # redirect user to add a prescription

