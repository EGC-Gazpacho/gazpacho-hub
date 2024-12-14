from flask import render_template, redirect, url_for, request, flash
from flask_login import current_user, login_user, logout_user


from app.modules.auth import auth_bp
from app.modules.auth.forms import SignupForm, LoginForm
from app.modules.auth.services import AuthenticationService
from app.modules.profile.services import UserProfileService


# Instanciar los servicios aquí para evitar la creación repetida
authentication_service = AuthenticationService()
user_profile_service = UserProfileService()


@auth_bp.route("/signup/", methods=["GET", "POST"])
def show_signup_form():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = SignupForm()
    if form.validate_on_submit():
        email = form.email.data
        if not authentication_service.is_email_available(email):
            return render_template("auth/signup_form.html", form=form, error=f'Email {email} in use')

        try:
            user = authentication_service.create_with_profile(**form.data)
        except Exception as exc:
            return render_template("auth/signup_form.html", form=form, error=f'Error creating user: {exc}')

        # Log user
        login_user(user, remember=True)
        return redirect(url_for('public.index'))

    return render_template("auth/signup_form.html", form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('public.index'))

    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        if authentication_service.login(form.email.data, form.password.data):
            return redirect(url_for('public.index'))

        return render_template("auth/login_form.html", form=form, error='Invalid credentials')

    return render_template('auth/login_form.html', form=form)


@auth_bp.route('/listarUsuarios', methods=['GET'])
def listar():
    if current_user.is_authenticated:
        if request.method == 'GET':
            users = authentication_service.list_users()
            return render_template("auth/list_users.html", users=users)
    else:
        return render_template('auth/login_form.html', form=LoginForm())


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.index'))


# Ruta de recuperación de contraseña
@auth_bp.route('/password_recovery', methods=['GET', 'POST'])
def password_recovery():
    if request.method == 'POST':
        email = request.form.get('email')
        user = authentication_service.get_user_by_email(email)
        print("hello", user)  # Get user by email
        if user:
            # Call `generate_recovery_token` using the service instance
            token = authentication_service.generate_recovery_token(user)
            print("hello2", user)
            try:
                authentication_service.send_recovery_email(user.email, token)  # Send email
                flash("A recovery link has been sent to your email.", 'success')
                return redirect(url_for('auth.password_recovery'))
            except Exception as e:
                flash(f"An error occurred while sending the recovery email: {str(e)}", 'error')
                return redirect(url_for('auth.password_recovery'))
        else:
            flash("Email not registered.", 'error')  # If email is not registered
            return redirect(url_for('auth.password_recovery'))  # Redirect to try again

    return render_template('auth/password_recovery.html')


# Reset password route

@auth_bp.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    user_id = authentication_service.verify_recovery_token(token)
    if not user_id:
        flash("The recovery link is invalid or has expired.")
        return redirect(url_for('auth.password_recovery'))

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        if authentication_service.update_password(user_id, new_password):
            flash("Your password has been successfully updated.")
            return redirect(url_for('auth.login'))

    return render_template('auth/password_reset.html', token=token)
