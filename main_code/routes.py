import flask
import flask_login
from sqlalchemy import or_

from main_code import app, bcrypt, db
from main_code.forms import (PostForm, Update_account_form, login_form,
                             register_form)
from main_code.models import Post, User
from main_code.pic_saver import save_picture


@app.route('/sign_up', methods=['GET', 'POST'])
def register_page():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('main_page'))
    form = register_form()
    context = {
        'form': form
    }
    if form.validate_on_submit():
        password = bcrypt.generate_password_hash(form.pwd.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=password)
        db.session.add(user)
        db.session.commit()
        flask_login.login_user(user)
        flask.flash(f'New account {user.username} is created')
        return flask.redirect(flask.url_for('main_page'))
    return flask.render_template('sign_up.html', context=context)


@app.route('/auth',  methods=['GET', 'POST'])
def auth_page():
    if flask_login.current_user.is_authenticated:
        return flask.redirect(flask.url_for('main_page'))
    form = login_form()
    context = {
        'form': form
    }
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.pwd.data):
            flask_login.login_user(user, remember=True)
            next_page = flask.request.args.get('next')
            return flask.redirect(next_page) if next_page else flask.redirect(flask.url_for('main_page'))
        flask.flash('Login is unsuccessful. Try again')
    return flask.render_template('auth_page.html', context=context)


@app.route('/sign_out', methods=['GET', 'POST'])
def sign_out_page():
    if flask_login.current_user.is_anonymous:
        return flask.redirect(flask.url_for('main_page'))
    flask_login.logout_user()
    return flask.render_template('sign_out.html')


@app.route('/', methods=['GET'])
def main_page():
    user = flask_login.current_user
    if user.is_authenticated:
        username = user.username
    else:
        username = 'Noname'
    if flask.request.args.get('query'):
        query = flask.request.args.get('query')
    else:
        query = ''
    posts = Post.query.filter(or_(Post.content.contains(query), Post.title.contains(query))).order_by('date_created')
    context = {
        'username': username,
        'posts': posts
    }
    return flask.render_template('main_page.html', context=context)

@app.route('/search')
def search():
    query = flask.request.args.get('query')
    return flask.redirect(flask.url_for('main_page', query=query))


@app.route('/profile', methods=['GET', 'POST'])
@flask_login.login_required
def profile():
    image = flask.url_for('static', filename='user_pics/' + flask_login.current_user.image)
    form = Update_account_form()
    user = flask_login.current_user
    context = {
        'image': image,
        'form': form
    }
    if form.validate_on_submit():
        if form.image.data:
            user.image = save_picture(form.image.data)
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flask.flash(f'Your account is updated')
        return flask.redirect(flask.url_for('profile'))
    elif flask.request.method == 'GET':
        form.username.data = user.username
        form.email.data = user.email
    return flask.render_template('profile.html', context=context)



@app.route('/post_create', methods=['GET', 'POST'])
@flask_login.login_required
def post_create():
    form = PostForm()
    context = {
        'form': form
    }
    if form.validate_on_submit():
        user_id = flask_login.current_user.id
        post = Post(title=form.title.data, content=form.content.data, user_id=user_id)
        db.session.add(post)
        db.session.commit()
        flask.flash('A new post has been created')
        return flask.redirect(flask.url_for('main_page'))
    return flask.render_template('post_create.html', context=context)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    post_user = User.query.get(post.user_id)
    image = flask.url_for('static', filename='user_pics/' + post_user.image)
    check_user = [True if flask_login.current_user == post_user else False]
    context = {
        'post': post,
        'post_user': post_user,
        'image': image,
        'check_user': check_user
    }
    return flask.render_template('post_detail.html', context=context)

@app.route('/post/<post_id>/update', methods=['GET', 'POST'])
@flask_login.login_required
def post_update(post_id):
    user = flask_login.current_user
    post = Post.query.get_or_404(post_id)
    if user.id != post.user_id:
        flask.abort(403, 'Permission denied')
    form = PostForm()
    context = {
        'form': form,
        'post': post
    }
    if form.validate_on_submit():
        post.title, post.content = form.title.data, form.content.data
        db.session.commit()
        flask.flash('The post is updated')
        return flask.redirect(flask.url_for('post', post_id=post_id))
    elif flask.request.method == 'GET':
        form.content.data = post.content
        form.title.data = post.title
    return flask.render_template('post_update.html', context=context)

@app.route('/post/<post_id>/delete', methods=['POST'])
@flask_login.login_required
def post_delete(post_id):
    user = flask_login.current_user
    post = Post.query.get_or_404(post_id)
    if user.id != post.user_id:
        flask.abort(403, 'Permission denied')
    db.session.delete(post)
    db.session.commit()
    flask.flash('The post is deleted')
    return flask.redirect(flask.url_for('main_page'))
