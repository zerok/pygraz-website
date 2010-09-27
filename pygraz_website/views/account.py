from flask import Module, session, redirect, abort, render_template, request,\
        flash, g, url_for
import pygraz_website as site

from pygraz_website import documents, forms, decorators


module = Module(__name__, url_prefix='/account')

@module.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        form = forms.RegisterForm.from_flat(request.form)
        if form.validate():
            doc = dict(form.flatten())
            doc['openids'] = [session['openid']]
            doc['doc_type'] = 'user'
            doc['username'] = doc['username'].lstrip().rstrip()
            site.couchdb.save_doc(doc)
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
    user = documents.User.view('frontend/users_by_openid',
            key=session['openid']).first()
    if user is None:
        return redirect(url_for('register',
                name=response.fullname,
                email=response.email, next=site.oid.get_next_url()))
    else:
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
            g.user.save()
            flash("Benutzerdaten gespeichert")
            return redirect(url_for('edit_profile'))
    else:
        form = forms.EditProfileForm.from_object(g.user)
    return render_template('account/edit_profile.html', form=form)
