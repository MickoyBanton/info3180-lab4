import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm
from app.forms import UploadForm
from werkzeug.security import check_password_hash

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
@login_required

def upload():
    # Instantiate your form class
    uploadform = UploadForm()

    if request.method == 'POST':

        if uploadform.validate_on_submit():
          
          photo = uploadform.photo.data
          filename = secure_filename(photo.filename) 
          photo.save(os.path.join(
            app.config['UPLOAD_FOLDER'], filename
        ))

          flash('File Saved', 'success')
          return redirect(url_for('home')) # Update this to redirect the user to a route that displays all uploaded image files

    return render_template('upload.html',form=uploadform)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # change this to actually validate the entire form submission
    # and not just one field
    if form.validate_on_submit():
        
        username = form.username.data
        password = form.password.data

        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()

        if user is not None and check_password_hash(user.password, password):
            # Gets user id, load into sessionLoginForm
            login_user(user)

            flash('Logged in successfully.', 'success')

            return redirect(url_for('upload'))

        # Remember to flash a message to the user
        return redirect(url_for("home"))  # The user should be redirected to the upload form instead
    return render_template("login.html", form=form)

@app.route("/uploads/<filename>")
def get_image(filename):
    return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

@app.route("/files")
def files():

    images=get_uploaded_images()
    return render_template("files.html", images=images)



# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

def get_uploaded_images():

    upload_folder = app.config['UPLOAD_FOLDER']
    uploaded_images = []

    # Ensure the folder exists
    if not os.path.exists(upload_folder):
        return uploaded_images  # Return an empty list if the folder doesn't exist

    # Iterate over files in the upload directory
    for subdir, _, files in os.walk(upload_folder):
        for file in files:
            if file.lower().endswith(('jpg', 'png')):  # Filter only image files
                uploaded_images.append(file)

    return uploaded_images


# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
