from flask import Module, render_template, abort

from pygraz_website import documents


module = Module(__name__, url_prefix='/companies')

@module.route('/')
def index():
    rows = documents.Company.view('frontend/companies_by_name')
    return render_template('companies/index.html', rows=rows)

@module.route('/<root_id>')
def view(root_id):
    doc = documents.Company.view('frontend/company_by_id', key=root_id).first()
    if doc is None: abort(404)
    return render_template('companies/view.html', doc=doc)
