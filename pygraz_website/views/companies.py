from flask import Module, render_template, abort, request

from pygraz_website import documents, decorators, utils, forms


module = Module(__name__, url_prefix='/companies')

@module.route('/')
def index():
    rows = documents.Company.view('frontend/companies_by_name')
    return render_template('companies/index.html', rows=rows)

@module.route('/<root_id>')
def view(root_id, docid=None):
    if docid is None:
        doc = documents.Company.view('frontend/company_by_id', key=root_id).first()
    else:
        doc = documents.Company.get(docid)
    if doc is None: abort(404)
    return render_template('companies/view.html', doc=doc)

@module.route('/doc/<docid>')
def view_doc(docid):
    return current_app.view_functions['companies.view'](date=None,
            docid=docid)


@module.route('/<root_id>/edit', methods=['GET', 'POST'])
@decorators.login_required
def edit(root_id):
    doc = documents.Company.view('frontend/company_by_id', key=root_id).first()
    with utils.DocumentLock(doc.root_id) as lock:
        if doc.next_version:
            return abort(403)
        if request.method == 'POST':
            form = forms.CompanyForm.from_flat(request.form)
            if form.validate({'doc': doc}):
                new_doc = utils.save_edit(doc, form)
                lock.unlock()
                return redirect(url_for('view',
                    date=root_id))
        else:
            form = forms.CompanyForm.from_object(doc)
        return render_template('companies/edit.html',
                doc=doc,
                form=form)

@module.route('/<date>/cancel_edit', methods=['GET', 'POST'])
@decorators.login_required
def cancel_edit_meetup(date):
    doc = documents.Meetup.view('frontend/meetups_by_date', key=date,
            include_docs=True).first()
    with utils.DocumentLock(doc.root_id) as lock:
        lock.unlock()
    return redirect(url_for('meetup', date=date))
