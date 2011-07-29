"""
Basic account handling. Most of the openid methods are adapted from the
Flask-OpenID documentation.
"""
from flask import Blueprint, session, redirect, abort, render_template, request,\
        flash, g, url_for
import pygraz_website as site

from pygraz_website import forms, decorators, models, db


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

@module.route('/account/login', methods=['GET','POST'])
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
    user = db.session.query(models.User).join(models.OpenID).filter(models.OpenID.id==session['openid']).first()
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
    if request.method == 'POST':
        form = forms.EditProfileForm.from_flat(request.form)
        if form.validate():
            g.user.username = form['username'].u
            g.user.email = form['email'].u
            db.session.add(g.user)
            db.session.commit()
            flash("Benutzerdaten gespeichert")
            return redirect(url_for('.edit_profile'))
    else:
        form = forms.EditProfileForm.from_object(g.user)
    return render_template('account/edit_profile.html', form=form)
