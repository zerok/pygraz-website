from jinja2.exceptions import TemplateNotFound
from flask import render_template
from pygraz_website import postmark, exceptions


def _fill_msg_with_template(msg, template_base, ctx):
    html_template = template_base + '.html'
    txt_template = template_base + '.txt'
    html_template_available = True
    txt_template_available = True

    try:
        msg.text_body = render_template(txt_template, **ctx)
    except TemplateNotFound, e:
        if e.templates != [txt_template]:
            raise
        txt_template_available = False

    try:
        msg.html_body = render_template(html_template, **ctx)
    except TemplateNotFound, e:
        if e.templates != [html_template]:
            raise 
        html_template_available = False

    if not html_template_available and not txt_template_available:
        raise exceptions.NoEmailTemplateFound("No mail templates found",
                (html_template, txt_template))


def send_mass_email(recipients, subject, template_base, ctx):
    msg = postmark.create_mail(subject=subject)
    _fill_msg_with_template(msg, template_base, ctx)
    postmark.send_bcc_batch(msg, recipients)

def send_email(recipient, subject, template_base, ctx):
    msg = postmark.create_mail(subject=subject, to=recipient)
    _fill_msg_with_template(msg, template_base, ctx)
    msg.send()
