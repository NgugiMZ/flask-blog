from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegistrationForm, LoginForm, PostForm
import models  # import the module, not the classes

# App config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'xgongive'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init DB and Login
models.db.init_app(app)
models.login_manager.init_app(app)
models.login_manager.login_view = 'login'
models.login_manager.login_message_category = 'info'

@app.route("/")
def home():
    posts = models.Post.query.all()
    return render_template("home.html", posts=posts)

#register route
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = models.User(username=form.username.data, email=form.email.data, password=hashed_pw)
        models.db.session.add(user)
        models.db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

#login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("You are now logged in.", "success")
            return redirect(url_for('home'))
        else:
            flash("Login unsuccessful. Check email and password.", "danger")
    return render_template("login.html", form=form)

#logout route
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

#post route
@app.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = models.Post(title=form.title.data, content=form.content.data, author=current_user)
        models.db.session.add(post)
        models.db.session.commit()
        flash("Post created!", "success")
        return redirect(url_for('home'))
    return render_template("create_post.html", form=form)


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = models.Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash("You can't edit this post.", "danger")
        return redirect(url_for('home'))

    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        models.db.session.commit()
        flash("Post updated!", "success")
        return redirect(url_for('home'))

    return render_template("edit_post.html", form=form, post=post)


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = models.Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash("You can't delete this post.", "danger")
        return redirect(url_for('home'))

    models.db.session.delete(post)
    models.db.session.commit()
    flash("Post deleted!", "info")
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
