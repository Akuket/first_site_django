from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def send_register_mail(link, name, email, association):
    subject = "Your ask for registration on %s." % association
    context = {'link_id': link, 'name': name}
    template = render_to_string("account/register_mail.html", context)
    # sender = ["guillaume.cassou@supinfo.com"]
    EmailMessage(subject, template, to=[email]).send()


def send_reset_password_mail(link, name, email, association):
    subject = "Your ask for reset your password on %s" % association
    context = {'link_id': link, 'name': name}
    template = render_to_string("account/forgot_password__mail.html", context)
    # sender = ["guillaume.cassou@supinfo.com"]
    EmailMessage(subject, template, to=[email]).send()
