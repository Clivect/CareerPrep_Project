from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from config import Config
from models import db, JobApplication, User, Message
from forms import JobApplicationForm, RegistrationForm, LoginForm, JobSearchForm, ResumeBuilderForm
from adzuna import get_job_listings
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
import weasyprint
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resume-builder', methods=['GET', 'POST'])
@login_required
def resume_builder():
    form = ResumeBuilderForm()
    if form.validate_on_submit():
        resume_data = {
            'name': form.name.data,
            'email': form.email.data,
            'phone': form.phone.data,
            'summary': form.summary.data,
            'experience': form.experience.data,
            'education': form.education.data,
            'skills': form.skills.data
        }
        
        # Generate PDF with inline CSS
        html = render_template('resume_template.html', resume=resume_data)
        pdf = weasyprint.HTML(string=html, base_url=request.url_root).write_pdf()

        # Return PDF as a downloadable file
        return send_file(BytesIO(pdf), as_attachment=True, download_name='resume.pdf', mimetype='application/pdf')
    
    return render_template('resume_builder.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('You have successfully registered!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/track', methods=['GET', 'POST'])
@login_required
def track():
    form = JobApplicationForm()
    if form.validate_on_submit():
        new_application = JobApplication(
            company=form.company.data,
            position=form.position.data,
            status=form.status.data,
            user_id=current_user.id  # Associate the application with the current user
        )
        db.session.add(new_application)
        db.session.commit()
        flash('Application added successfully!', 'success')
        return redirect(url_for('track'))
    
    # Filter applications based on the logged-in user
    applications = JobApplication.query.filter_by(user_id=current_user.id).all()
    return render_template('track.html', form=form, applications=applications)

@app.route('/delete_application/<int:application_id>', methods=['POST'])
@login_required
def delete_application(application_id):
    application = JobApplication.query.get_or_404(application_id)
    if application.user_id != current_user.id:
        flash('You are not authorized to delete this application.', 'danger')
        return redirect(url_for('track'))
    
    db.session.delete(application)
    db.session.commit()
    flash('Application deleted successfully.', 'success')
    return redirect(url_for('track'))

@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    form = JobSearchForm()
    job_listings = []
    if form.validate_on_submit():
        query = form.query.data
        job_listings = get_job_listings(query)
        print("Job Listings:", job_listings)  # To check the output in your logs
    return render_template('job_lists.html', form=form, job_listings=job_listings)

@app.route('/community', methods=['GET', 'POST'])
@login_required
def community():
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            message = Message(content=content, username=current_user.username)
            db.session.add(message)
            db.session.commit()
            flash('Message posted successfully!', 'success')
        else:
            flash('Message cannot be empty!', 'danger')
    
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    return render_template('community.html', messages=messages)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
