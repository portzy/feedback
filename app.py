from flask import Flask, render_template, redirect, session, flash
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///hashing_login"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "akina123"

connect_db(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home_page():
    """shows homepage"""
    return redirect('/register')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """handle form submission for register as a new user"""
    form = RegisterForm()

    if "username" in session:
        return redirect(f"/users/{session['username']}")
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username, password, first_name, last_name, email)

        db.session.commit()
        session['username'] = user.username
        return redirect(f"/users/{user.username}")
    return render_template('users/register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """handle user log in"""
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)  
        if user:
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid username/password."]
            return render_template("users/login.html", form=form)
    return render_template("users/login.html", form=form)

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/login')

@app.route('/users/<username>')
def user_profile(username):
    if 'username' not in session or session['username'] != username:
        flash('You do not have permession to view this page.')
        return redirect('/login')
    user = User.query.filter_by(username=username).first()
    form = DeleteForm()

    return render_template("users/show.html", user=user, form=form)

@app.route("/users/<username>/delete", methods=["POST"])
def remove_user(username):
    """Delete user"""
    if 'username' not in session or username != session['username']:
        flash('You do not have permession to view this page.')
    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect('/register')

@app.route("/users/<username>/feedback/new", methods=["GET", "POST"])
def add_feedback(username):
    """show add feedback form"""
    if 'username' not in session or username != session['username']:
        flash('You do not have permession to view this page.')
    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{feedback.username}")
    else:
        return render_template("feedback/new.html", form=form)

@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):
    """shows update feedback form"""
    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        flash('You do not have permission to view this page.')
        return redirect('/login')
    
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    return render_template("feedback/edit.html", form=form, feedback=feedback)

@app.route("/feedback/<int:feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""
    feedback = Feedback.query.get(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        flash('You do not have permission to view this page.')
        return redirect('/login')
    
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")

if __name__ == '__main__':
    app.run(debug=True)


