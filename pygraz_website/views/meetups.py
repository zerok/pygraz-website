from flask import Module, render_template, request, redirect, url_for, current_app
import datetime

from pygraz_website import forms, decorators, utils, filters, db, models


module = Module(__name__, url_prefix='/meetups')


@module.route('/')
def meetups():
    """List all meetups in chronological order"""
    return render_template('meetups.html',
            meetups = db.session.query(models.Meetup).filter(models.Meetup.end > datetime.datetime.utcnow()))

@module.route('/<date>')
def meetup(date):
    real_date = datetime.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=current_app.config['local_timezone'])
    meetup = models.Meetup.query_by_date(real_date).first()
    return render_template('meetup.html',
            meetup = meetup)

@module.route('/<date>/edit', methods=['GET', 'POST'])
@decorators.admin_required
def edit_meetup(date):
    real_date = datetime.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=current_app.config['local_timezone'])
    meetup = models.Meetup.query_by_date(real_date).first()
    with utils.DocumentLock(meetup) as lock:
        if request.method == 'POST':
            form = forms.MeetupForm.from_flat(request.form)
            if form.validate({'meetup': meetup}):
                if 'preview' not in request.form:
                    print form

                    meetup.start = form['start'].value
                    meetup.end = form['end'].value
                    meetup.location = form['location'].value
                    meetup.address = form['address'].value
                    db.session.add(meetup)
                    db.session.commit()
                    lock.unlock()
                    return redirect(url_for('meetup',
                        date=filters.datecode(meetup.start)))
        else:
            form = forms.MeetupForm.from_object(meetup)
            print form
        return render_template('meetups/edit.html',
                meetup=meetup,
                preview='preview' in request.form,
                form=form)

@module.route('/<date>/cancel_edit', methods=['GET', 'POST'])
@decorators.admin_required
def cancel_edit_meetup(date):
    real_date = datetime.datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=current_app.config['local_timezone'])
    meetup = models.Meetup.query_by_date(real_date)
    with utils.DocumentLock(meetup) as lock:
        lock.unlock()
    return redirect(url_for('meetup', date=date))

@module.route('/create', methods=['GET','POST'])
@decorators.admin_required
def create_meetup():
    if request.method == 'POST':
        form = forms.MeetupForm.from_flat(request.form)
        if form.validate():
            if 'preview' not in request.form:
                meetup = models.Meetup(start=form['start'].value,
                        end=form['end'].value, location=form['location'].value,
                        address=form['address'].value, notes=form['notes'].value)
                db.session.add(meetup)
                db.session.commit()
                return redirect(url_for('meetup',
                    date=filters.datecode(form['start'].value)))
    else:
        form = forms.MeetupForm()
    return render_template('meetups/create.html',
            preview='preview' in request.form,
            form=form)

@module.route('/archive/')
def meetup_archive():
    return render_template('meetups/archive.html',
            meetups=db.session.query(models.Meetup).filter(models.Meetup.end < datetime.datetime.utcnow())
            )
