from flask import Flask, render_template, request, redirect, flash, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
import datetime
from datetime import date
# from itsdangerous import URLSafeTimedSerializer
# from flask_mail import Mail, Message
# from threading import Thread
from models import db, connect_db, User, Recipe
from forms import RegisterForm, LoginForm, RecipeForm, LeftoverForm
from sqlalchemy.exc import IntegrityError
import requests, os
from key import API_KEY

API_BASE_URL = 'https://api.spoonacular.com'
CURR_USER_KEY = 'curr_user'
# API_KEY = os.getenv("API_KEY", "optional-default")

app = Flask(__name__)
# mail = Mail(app)
migrate = Migrate(app, db)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nomnom'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'ihaveasecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

# # HELPERS


# def send_async_email(msg):
#     with app.app_context():
#         mail.send(msg)


# def send_email(subject, recipients, html_body):
#     msg = Message(subject, recipients=recipients)
#     msg.html = html_body
#     thr = Thread(target=send_async_email, args=[msg])
#     thr.start()

# def send_confirmation_email(user_email):
#     """Send email to confirm user's email address."""

#     confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

#     confirm_url = url_for(
#         '.confirm_email',
#         token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'),
#         _external=True
#     )

#     html = render_template('email_confirmation.html', confirm_url=confirm_url)

#     send_email('Confirm Your Email Address', [user_email], html)


###############################################################
# User register/login/logout


@app.before_request
def add_user_to_g():
    """If logged in, add current user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


# @app.route('/confirm/<token>')
# def confirm_email(token):
#     """Processing unique token."""

#     try:
#         confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#         email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)

#     except:
#         flash('The confirmation link is invalid or has expired', 'error')
#         return redirect('/login')

#     user = User.query.filter_by(email=email).first()

#     if user.email_confirmed:
#         flash('Account already confirmed. Please login.', 'info')
#     else:
#         user.email_confirmed = True
#         user.email_confirmed_on = datetime.now()
#         db.session.add(user)
#         db.session.commit()
#         flash('Thanks for confirming your email address!', 'success')

#     return redirect(f'/users/{user.id}/recipes')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Show register form and handle user registration."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = RegisterForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        image_url = form.image_url.data
        
        new_user = User.register(first_name, last_name, email, password, image_url)

        db.session.add(new_user)
        try:
            db.session.commit()
            # send_confirmation_email(new_user.email)
            # flash('Please check your email to confirm your email address.', 'success')
            # return redirect('/login')

        except IntegrityError:
            # db.session.rollback()
            form.email.errors.append('Account with this email already exists. Please try again.')
            return render_template('users/register.html', form=form)

        do_login(new_user)

        flash(f'Welcome, {new_user.first_name}!', 'primary')
        return redirect(f'/users/{new_user.id}/recipes')

    return render_template('users/register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # authenticate will return a user or False
        user = User.authenticate(email, password)

        if user:
            do_login(user)
            flash(f'Welcome back, {user.full_name}!', 'primary')
            return redirect(f'/users/{user.id}/recipes')

        else:
            form.email.errors = ['Incorrect email or password. Please try again.']

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Logs user out and redirect to homepage."""

    do_logout()
    flash('You have successfully logged out.', 'secondary')

    return redirect('/')


################################################################
# General user routes


@app.route('/')
def show_search_form():
    """Show homepage with search bar."""

    return render_template('index.html')


@app.route('/users/<int:user_id>')
def show_user(user_id):
    """Show user's info."""

    if not g.user:
        flash('Please log in first.', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)

    return render_template('users/show.html', user=user)


@app.route('/users/profile', methods=['GET', 'POST'])
def edit_profile():
    """Update profile for current user."""

    if not g.user:
        flash('Please log in first.', 'danger')
        return redirect('/')

    user = g.user
    form = RegisterForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.email, form.password.data):
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.image_url = form.image_url.data

            db.session.commit()
            return redirect(f'/users/{user.id}')

        flash('Wrong password, please try again.', 'danger')

    return render_template('users/edit.html', form=form, user_id=user.id)


@app.route('/users/delete', methods=['POST'])
def delete_user():
    """Delete user."""

    if not g.user:
        flash('Please log in first.', 'danger')
        return redirect('/')

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    flash('Account deleted.', 'danger')
    return redirect('/')


################################################################
# Recipes routes


@app.route('/recipes')
def search_recipes():
    """Search recipes by ingredients."""
    try:
        tags = request.args['tags']

        res = requests.get(f'{API_BASE_URL}/recipes/random?apiKey={API_KEY}&tags={tags}&number=1')


        data = res.json()
        entry = data['recipes'][0]

        title = entry['title']
        image = entry['image']
        readyInMinutes = entry['readyInMinutes']
        servings = entry['servings']
        sourceUrl = entry['sourceUrl']

        new_recipes = {
            'title': title,
            'image': image, 
            'readyInMinutes': readyInMinutes,
            'servings': servings,
            'sourceUrl': sourceUrl
            }
        return render_template('index.html', new_recipes=new_recipes)
    except IndexError:
        return render_template('404.html')


@app.route('/recipes/new', methods=['GET', 'POST'])
def add_recipe():
    """Show add recipe form & handle adding recipes."""

    if not g.user:
        flash('Please log in first.', 'danger')
        return redirect('/')

    form = RecipeForm()

    title = form.title.data
    source_url = form.source_url.data
    ingredients = form.ingredients.data
    instructions = form.instructions.data
    image_url = form.image_url.data

    new_recipe = Recipe(
        title=title,
        source_url=source_url,
        ingredients=ingredients,
        instructions=instructions,
        image_url=image_url,
        user_id=g.user.id
        )

    if form.validate_on_submit():
        db.session.add(new_recipe)
        db.session.commit()

        flash('New recipe added.', 'success')
        return redirect(f'/users/{g.user.id}/recipes')

    return render_template('recipes/new.html', form=form, new_recipe=new_recipe)


@app.route('/users/<int:user_id>/recipes', methods=['GET', 'POST'])
def list_recipes(user_id):
    """Show user's recipes when logged in."""

    if not g.user:
        flash('Please log in first.', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)
    recipes = (Recipe
              .query
              .filter(Recipe.user_id == user_id)
              .order_by(Recipe.created_on.desc())
              .all())

    return render_template('recipes/list.html', user=user, recipes=recipes)


@app.route('/users/<int:user_id>/recipes/random', methods=['GET', 'POST'])
def add_random_recipe(user_id):
    """Add a random recipe to user's list."""

    if not g.user:
        flash('Please log in first.', 'danger')
        return redirect('/')

    tags = request.args['tags']
    res = requests.get(f'{API_BASE_URL}/recipes/random?apiKey={API_KEY}&number=1&tags={tags}')

    data = res.json()
    entry = data['recipes'][0]

    title = entry['title']
    source_url = entry['sourceUrl']
    image_url = entry['image']

    random_recipe = Recipe(
        title=title,
        source_url=source_url,
        image_url=image_url,
        user_id=g.user.id
        )

    db.session.add(random_recipe)
    g.user.recipes.append(random_recipe)
    db.session.commit()

    return redirect(f'/users/{g.user.id}/recipes')


@app.route('/recipes/<int:recipe_id>')
def show_recipe(recipe_id):
    """Show an added recipe."""

    if not g.user:
        flash('Please log in first.', 'danger')
        return redirect('/')

    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipes/show.html', recipe=recipe)


@app.route('/recipes/<int:recipe_id>/done')
def cooked_recipe(recipe_id):
    """Mark as done after making a recipe."""

    if not g.user:
        flash('Please log in first.', 'danger')
        return redirect('/')

    
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    recipe.done = not recipe.done
    db.session.commit()

    return redirect(f'/users/{g.user.id}/recipes')
    # return redirect(f'/recipes/{recipe.id}/leftovers')


# @app.route('/recipes/<int:recipe_id>/leftovers', methods=['GET', 'POST'])
# def leftovers(recipe_id):
#     """Show a form asking if the recipe has leftovers. 
    
#     If yes, show the cooked date; else, strike through.
#     """

#     if not g.user:
#         flash('Please log in first.', 'danger')
#         return redirect('/')

#     form = LeftoverForm()

#     leftovers = form.leftovers.data
#     done_on = form.done_on.data

#     # friendly_date = done_on.strftime('%Y, %m, %d')

#     recipe = Recipe.query.filter_by(id=recipe_id, done=True).first()
#     if form.validate_on_submit():
#         recipe.leftovers = not recipe.leftovers
#         # db.session.add(done_on)
#         # g.user.recipes.append(done_on)
#         db.session.commit()

#         return redirect(f'/users/{g.user.id}/recipes')

#     return render_template('recipes/leftovers.html', form=form, done_on=done_on, recipe=recipe)


@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    """Show a form to edit an existing recipe."""

    if not g.user:
        flash('Please log in first.', 'danger')
        return redirect('/')

    recipe = Recipe.query.get_or_404(recipe_id)
    form = RecipeForm(obj=recipe)

    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.source_url = form.source_url.data
        recipe.ingredients = form.ingredients.data
        recipe.instructions = form.instructions.data
        recipe.image_url = form.image_url.data
        db.session.commit()
        flash(f"{recipe.title} updated.", 'success')
        return redirect(f'/recipes/{recipe.id}')

    # failed; re-present form for editing
    return render_template('recipes/edit.html', form=form, recipe=recipe)


@app.route('/recipes/<int:recipe_id>/delete', methods=['GET', 'POST'])
def delete_recipe(recipe_id):
    """Delete a recipe."""

    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != g.user.id:
        flash('Please log in first.', 'danger')
        return redirect("/")

    db.session.delete(recipe)
    db.session.commit()

    flash(f"{recipe.title} deleted.", 'danger')
    return redirect(f'/users/{g.user.id}/recipes')

# @app.route('/recipes/<int:user_id>/delete_all', methods=['GET', 'POST'])
# def delete_all(user_id):
#     """Delete all user's recipes."""

#     if not g.user:
#         flash('Please log in first.', 'danger')
#         return redirect("/")

#     recipes = (Recipe
#               .query
#               .filter(Recipe.user_id == user_id)
#               .all())

#     db.session.delete(recipes)
#     db.session.commit()

#     return redirect(f'/users/{g.user.id}/recipes')


################################################################
# About and 404 pages


@app.route("/about")
def about_page():
    """Show About page."""

    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(e):
    """Show 404 page."""

    return render_template('404.html'), 404
