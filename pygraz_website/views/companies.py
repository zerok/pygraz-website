from flask import Module, render_template, abort, request, redirect, url_for,\
        current_app

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
    versions = documents.Version.view('frontend/all_versions',
            endkey=[doc['root_id']], startkey=[doc['root_id'], 'Z'],
            descending=True)
    return render_template('companies/view.html', doc=doc,
            versions=versions)

@module.route('/doc/<docid>')
def view_doc(docid):
    return current_app.view_functions['companies.view'](root_id=None,
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
                # Mark the content as unconfirmed if the current user
                # is not a designed editor of this company (or admin)
                if doc.confirmed and not utils.is_editor_for(doc):
                    new_doc.confirmed = False
                    new_doc.save()
                lock.unlock()
                return redirect(url_for('view',
                    root_id=root_id))
        else:
            form = forms.CompanyForm.from_object(doc)
        return render_template('companies/edit.html',
                doc=doc,
                form=form)

@module.route('/<root_id>/cancel_edit', methods=['GET', 'POST'])
@decorators.login_required
def cancel_edit(root_id):
    doc = documents.Company.view('frontend/company_by_id', key=root_id).first()
    with utils.DocumentLock(doc.root_id) as lock:
        lock.unlock()
    return redirect(url_for('view', root_id=root_id))

@module.route('/<root_id>/confirm')
@decorators.login_required
def confirm(root_id):
    doc = documents.Company.view('frontend/company_by_id', key=root_id).first()
    if not utils.is_editor_for(doc):
        return abort(403)
    with utils.DocumentLock(doc.root_id) as lock:
        doc.confirmed = True
        doc.save()
    return redirect(url_for('view', root_id=root_id))

@module.route('/<root_id>/unconfirm')
@decorators.login_required
def unconfirm(root_id):
    doc = documents.Company.view('frontend/company_by_id', key=root_id).first()
    if not utils.is_editor_for(doc):
        return abort(403)
    with utils.DocumentLock(doc.root_id) as lock:
        doc.confirmed = False
        doc.save()
    return redirect(url_for('view', root_id=root_id))
