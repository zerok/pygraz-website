# -*- encoding: utf-8 -*-
"""
Basic account handling. Most of the openid methods are adapted from the
Flask-OpenID documentation.
"""
from flask import Blueprint, session, redirect, render_template, request,\
        flash, g, url_for
import pygraz_website as site
import uuid
import hashlib

from pygraz_website import forms, decorators, models, db, signals, email


module = Blueprint('account', __name__)


@module.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        form = forms.RegisterForm.from_flat(request.form)
        if form.validate():
            data = dict(form.flatten())
            openid = models.OpenID(id=session['openid'])
            db.session.add(openid)
            user = models.User()
            user.username = data['username'].lstrip().rstrip()
            user.email = data['email'].lstrip().rstrip()
            user.openids.append(openid)
            db.session.add(user)
            db.session.commit()
            return redirect(site.oid.get_next_url())
    else:
        default = {}
        for k, v in request.args.items():
            if k == 'name':
                default['username'] = v
            else:
                default[k] = v
        form = forms.RegisterForm.from_flat(default)
    return render_template('account/register.html',
            form=form, next=site.oid.get_next_url())


@module.route('/account/login', methods=['GET', 'POST'])
@site.oid.loginhandler
def login():
    if request.method == 'POST':
        form = forms.LoginForm.from_flat(request.form)
        if form.validate():
            return site.oid.try_login(form['openid'].u,
                    ask_for=['fullname', 'email'])
    else:
        form = forms.LoginForm()
    return render_template('account/login.html',
            form=form, next=request.args.get('next', '/'))


@site.oid.after_login
def login_or_register(response):
    session['openid'] = response.identity_url
    user = db.session.query(models.User).join(models.OpenID)\
            .filter(models.OpenID.id == session['openid']).first()
    if user is None:
        return redirect(url_for('.register',
                name=response.fullname,
                email=response.email, next=site.oid.get_next_url()))
    else:
        g.user = user
        return redirect(site.oid.get_next_url())


@module.route('/logout')
def logout():
    del session['openid']
    return redirect(request.args.get('next', '/'))


@module.route('/profile', methods=['GET', 'POST'])
@decorators.login_required
def edit_profile():
    # Fake the email status for now
    if request.method == 'POST':
        form = forms.EditProfileForm.from_flat(request.form)
        if form.validate():
            old_email = g.user.email
            g.user.username = form['username'].u
            g.user.email = form['email'].u
            g.user.email_notify_new_meetup = form['email_notify_new_meetup'].value
            g.user.email_notify_new_sessionidea = form['email_notify_new_sessionidea'].value
            if old_email != g.user.email:
                g.user.email_status = 'not_verified'
            db.session.add(g.user)
            db.session.commit()
            flash("Benutzerdaten gespeichert")
            return redirect(url_for('.edit_profile'))
    else:
        form = forms.EditProfileForm.from_object(g.user)
    return render_template('account/edit_profile.html', form=form)

@module.route('/email-activation/start', methods=['GET'])
@decorators.login_required
def start_email_activation():
    """
    Sends out an activation email to the address currently associated
    with the user and sets the current email as inactive.
    """
    if g.user.email_status == 'active':
        flash("Ihre E-Mail-Adresse wurde bereits aktiviert")
        return redirect(url_for('.edit_profile'))
    code = _generate_activation_code(g.user)
    activation_url = request.url_root + url_for('.activate_email', code=code)
    g.user.email_activation_code = code
    db.session.add(g.user)
    db.session.commit()
    email.send_email(g.user.email, "Aktivieren Sie Ihre E-Mail-Adresse",
        'account/emails/activation', {'user': g.user,
            'url': activation_url})
    flash(u"Es wurde eine Aktivierungsemail an {} versandt".format(g.user.email))
    return redirect(url_for('.edit_profile'))

@module.route('/email-activation/finalize')
@decorators.login_required
def activate_email():
    code = request.args.get('code', None)
    if code is not None:
        if code == g.user.email_activation_code:
            g.user.email_status = 'active'
            g.user.email_activation_code = None
            db.session.add(g.user)
            db.session.commit()
            flash("Ihre E-Mail-Adresse wurde aktiviert")
            return redirect(url_for('.edit_profile'))
        flash(u"Der von Ihnen angegebene Code ist leider ungültig")
    return render_template('account/email_activation_finalize.html')

def handle_meetup_created(meetup):
    """
    Is called when a new meetup is created and notifies all users that requested such
    a notification.
    """
    users = db.session.query(models.User)\
            .filter_by(email_status='active')\
            .filter_by(email_notify_new_meetup=True)
    emails = [user.email for user in users]
    email.send_mass_email(emails, 'Neues Stammtisch', 'emails/new-meetup', ctx=dict(meetup=meetup))


def handle_sessionidea_created(sessionidea):
    users = db.session.query(models.User)\
            .filter_by(email_status='active')\
            .filter_by(email_notify_new_sessionidea=True)
    emails = [user.email for user in users]
    url = '{}{}#idea-{}'.format(request.url_root, sessionidea.meetup.get_absolute_url(), sessionidea.id)
    email.send_mass_email(emails, 'Neue Sessionidea', 'emails/new-sessionidea',
            ctx=dict(idea=sessionidea, url=url))


signals.meetup_created.connect(handle_meetup_created)
signals.sessionidea_created.connect(handle_sessionidea_created)

def _generate_activation_code(user):
    raw = "{}.{}.{}".format(user.id, user.email, str(uuid.uuid4()))
    return hashlib.sha1(raw).hexdigest()[:5]

