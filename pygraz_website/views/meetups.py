# -*- encoding: utf-8 -*-
from flask import Blueprint, render_template, request, redirect, url_for,\
        current_app, g, flash, abort
from flaskext.babel import gettext as _
import datetime
import collections
from sqlalchemy.orm import joinedload

from pygraz_website import forms, decorators, utils, filters, db, models


module = Blueprint('meetups', __name__)


def _extract_date(date):
    """
    Converts the date passed in via URL into a native and localized
    datetime object.

    :param date: date string in %Y-%m-%d
    :type date: string
    :returns: native date object
    """
    return datetime.datetime.strptime(date, "%Y-%m-%d")\
            .replace(tzinfo=current_app.config['local_timezone'])


def _get_meetup(date):
    """
    Returns the meetup with the given date. If no matching meetup could be
    found this raises a 404 error page.

    :param date: date string in %Y-%m%-d
    :type date: string
    """
    real_date = _extract_date(date)
    meetup = models.Meetup.query_by_date(real_date).first()
    if meetup is None:
        abort(404)
    return meetup


def _get_idea(id_, meetup):
    """
    Fetches the idea with the given idea associated with the given meetup. If
    the idea can't be found a 404 error page is raised.

    :param id_: id of an idea
    :param meetup: meetup object
    :returns: idea object
    """
    idea = db.session.query(models.Sessionidea)\
            .filter(models.Sessionidea.id == id_)\
            .filter(models.Sessionidea.meetup == meetup).first()
    if idea is None:
        abort(404)
    return idea


def do_vote(date, id, value):
    """
    Executes a voting for an idea with the given id associated with a meetup
    taking place on the given date (string). The value indicates whether the
    voting is positive or negative.

    :param date: date of a meetup. See `_get_meetup` for details
    :param id: id of an idea associated with the meetup
    :param value: 1 or -1 for voting the idea up or down
    :returns: Response initiating a redirect to the meetup
    """
    meetup = _get_meetup(date)
    idea = _get_idea(id, meetup)
    voted_users = [vote.user for vote in idea.votes.all()]
    if g.user not in voted_users:
        vote = models.SessionideaVote()
        vote.user = g.user
        vote.sessionidea_id = idea.id
        vote.value = value
    else:
        vote = db.session.query(models.SessionideaVote)\
                .filter(models.SessionideaVote.user == g.user)\
                .filter(models.SessionideaVote.sessionIdea == idea).first()
        vote.value = value
    db.session.add(vote)
    db.session.commit()
    flash(_(u"Thank you for your vote!"))
    return redirect(url_for('.meetup', date=filters.datecode(meetup.start)))


@module.route('/')
def meetups():
    """
    List all meetups in chronological order
    """
    return render_template('meetups.html',
            meetups=db.session.query(models.Meetup)\
                    .filter(models.Meetup.end > datetime.datetime.utcnow()))


@module.route('/<date>')
def meetup(date):
    """
    Displays the meetup taking place on the given date.
    """
    meetup = _get_meetup(date)
    user_upvotes = []
    user_downvotes = []
    ideas = meetup.sessionideas
    idea_ids = [idea.id for idea in ideas]
    vote_results = collections.defaultdict(int)
    for vote in db.session.query(models.SessionideaVote)\
            .filter(models.SessionideaVote.sessionidea_id.in_(idea_ids)):
        vote_results[vote.sessionidea_id] += vote.value
    if g.user:
        for vote in db.session.query(models.SessionideaVote)\
                .options(joinedload('sessionIdea'))\
                .filter(models.SessionideaVote.user == g.user)\
                .filter(models.SessionideaVote.sessionidea_id.in_(idea_ids)):
            if vote.value > 0:
                user_upvotes.append(vote.sessionIdea.id)
            else:
                user_downvotes.append(vote.sessionIdea.id)
    return render_template('meetup.html',
            meetup=meetup, ideas=ideas,
            vote_results=vote_results,
            user_upvotes=user_upvotes,
            user_downvotes=user_downvotes)


@module.route('/<date>/sessionideas/add', methods=['GET', 'POST'])
@decorators.login_required
def add_sessionidea(date):
    """
    Form handling for adding a new session idea to the meetup
    taking place on the passed date.
    """
    meetup = _get_meetup(date)
    now = datetime.datetime.utcnow()
    if now > meetup.start:
        flash(_('Session ideas can only be added to future meetups'))
        return redirect(url_for('.meetup', date=date))
    if request.method == 'POST':
        form = forms.SessionIdeaForm.from_flat(request.form)
        if form.validate():
            idea = models.Sessionidea()
            idea.author = g.user
            idea.summary = form['summary'].value
            idea.details = form['details'].value
            idea.url = form['url'].value
            idea.meetup = meetup
            db.session.add(idea)
            db.session.commit()
            return redirect(url_for('.meetup',
                date=filters.datecode(meetup.start)))
    else:
        form = forms.SessionIdeaForm()
    return render_template('meetups/add_idea.html',
            meetup=meetup, form=form)


@module.route('/<date>/sessionideas/<id>/delete', methods=['GET', 'POST'])
@decorators.login_required
def delete_sessionidea(date, id):
    """
    Form handler for deleting a session idea.
    """
    meetup = _get_meetup(date)
    idea = _get_idea(id, meetup)
    if request.method == 'GET':
        return render_template('meetups/confirm_delete_idea.html',
                idea=idea, meetup=meetup)
    db.session.delete(idea)
    db.session.commit()
    return redirect(url_for('.meetup', date=filters.datecode(meetup.start)))


@module.route('/<date>/sessionideas/<id>/edit', methods=['GET', 'POST'])
@decorators.login_required
def edit_sessionidea(date, id):
    """
    Form handler for editing a session idea.
    """
    meetup = _get_meetup(date)
    idea = _get_idea(id, meetup)
    if g.user != idea.author:
        abort(404)
    if request.method == 'POST':
        form = forms.SessionIdeaForm.from_flat(request.form)
        if form.validate():
            idea.summary = form['summary'].value
            idea.details = form['details'].value
            idea.url = form['url'].value
            db.session.add(idea)
            db.session.commit()
            return redirect(url_for('.meetup',
                date=filters.datecode(meetup.start)))
    else:
        form = forms.SessionIdeaForm.from_object(idea)
    return render_template('meetups/edit_idea.html',
            meetup=meetup, idea=idea, form=form)


@module.route('/<date>/sessionideas/<id>/up')
@decorators.login_required
def vote_up_sessionidea(date, id):
    return do_vote(date, id, 1)


@module.route('/<date>/sessionideas/<id>/down')
@decorators.login_required
def vote_down_sessionidea(date, id):
    return do_vote(date, id, -1)


@module.route('/<date>/sessionideas/<id>/unvote')
@decorators.login_required
def unvote_sessionidea(date, id):
    meetup = _get_meetup(date)
    idea = _get_idea(id, meetup)
    vote = db.session.query(models.SessionideaVote)\
            .filter(models.SessionideaVote.user == g.user)\
            .filter(models.SessionideaVote.sessionIdea == idea).first()
    if vote is not None:
        db.session.delete(vote)
        db.session.commit()
        flash(_('Vote removed'))
    return redirect(url_for('.meetup', date=filters.datecode(meetup.start)))


@module.route('/<date>/edit', methods=['GET', 'POST'])
@decorators.admin_required
def edit_meetup(date):
    real_date = _extract_date(date)
    meetup = models.Meetup.query_by_date(real_date).first()
    with utils.DocumentLock(meetup) as lock:
        if request.method == 'POST':
            form = forms.MeetupForm.from_flat(request.form)
            if form.validate({'meetup': meetup}):
                if 'preview' not in request.form:
                    meetup.start = form['start'].value
                    meetup.end = form['end'].value
                    meetup.location = form['location'].value
                    meetup.address = form['address'].value
                    meetup.notes = form['notes'].value
                    db.session.add(meetup)
                    db.session.commit()
                    lock.unlock()
                    return redirect(url_for('.meetup',
                        date=filters.datecode(meetup.start)))
        else:
            form = forms.MeetupForm.from_object(meetup)
        return render_template('meetups/edit.html',
                meetup=meetup,
                preview='preview' in request.form,
                form=form)


@module.route('/<date>/delete', methods=['GET', 'POST'])
@decorators.admin_required
def delete_meetup(date):
    real_date = _extract_date(date)
    meetup = models.Meetup.query_by_date(real_date).first()
    if meetup is None:
        abort(404)
    if request.method == 'POST':
        with utils.DocumentLock(meetup) as lock:
            db.session.delete(meetup)
            db.session.commit()
            lock.unlock()
        return redirect(url_for('.meetups'))
    else:
        return render_template('meetups/confirm_delete_meetup.html',
                meetup=meetup)


@module.route('/<date>/cancel_edit', methods=['GET', 'POST'])
@decorators.admin_required
def cancel_edit_meetup(date):
    real_date = _extract_date(date)
    meetup = models.Meetup.query_by_date(real_date)
    with utils.DocumentLock(meetup) as lock:
        lock.unlock()
    return redirect(url_for('.meetup', date=date))


@module.route('/create', methods=['GET', 'POST'])
@decorators.admin_required
def create_meetup():
    if request.method == 'POST':
        form = forms.MeetupForm.from_flat(request.form)
        if form.validate():
            if 'preview' not in request.form:
                meetup = models.Meetup(start=form['start'].value,
                        end=form['end'].value, location=form['location'].value,
                        address=form['address'].value,
                        notes=form['notes'].value)
                db.session.add(meetup)
                db.session.commit()
                return redirect(url_for('.meetup',
                    date=filters.datecode(form['start'].value)))
    else:
        form = forms.MeetupForm()
    return render_template('meetups/create.html',
            preview='preview' in request.form,
            form=form)


@module.route('/archive/')
def meetup_archive():
    return render_template('meetups/archive.html',
            meetups=db.session.query(models.Meetup)\
                    .filter(models.Meetup.end < datetime.datetime.utcnow())\
                    .order_by(models.Meetup.start.desc()))
