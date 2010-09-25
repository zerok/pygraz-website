from flask import Module, session, redirect, abort, render_template, request
import pygraz_website as site

from pygraz_website import documents, forms


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

