import payplug
from django.core.mail import EmailMessage, mail_admins
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from datetime import datetime, timedelta, time

from account.models import PaymentsUser, User

payplug.set_secret_key('sk_test_5FVRtiAo2p1luWvHMmHa8z')


class Payment(object):
    def __init__(self, user, subscription, product, payment_infos=None):
        self.__user = user
        self.__product = product

        payment_data = {
            'amount': int(self.__product.price * 100),  # en cents, 1 euro minimum
            'customer': {'email': str(self.__user.email)},
            'save_card': False,  # option premium
            'currency': 'EUR',
            'metadata': {
                'customer_id': self.__user.id,
            },
        }

        if payment_infos:
            payment_data.update(payment_infos)

        self.payment = payplug.Payment.create(**payment_data)  # creation de l'object payment
        self.payment_id = str(self.payment.id)
        self.status_payment = None
        payment_user = PaymentsUser(reference=self.payment_id, subscription=subscription, product=self.__product, user=self.__user)
        payment_user.save()

    def redirect_payment(self):
        url = self.payment.hosted_payment.payment_url
        return HttpResponseRedirect(url)

    # payplug envoie automatiquement le status de la transaction par mail à l'adresse mail renseignée pour le compte
    # payplug.
    def status_mail_admin(self):
        subject = "Status payment for %s" % self.__user.name
        message = "The payment for %s is %s" % self.__product.name, self.status_payment
        mail_admins(subject=subject, message=message)


def resend_pay():
    today_start = datetime.combine(datetime.now().date(), time())
    today_end = datetime.combine(datetime.now().date() + timedelta(1), time())
    payments_db = PaymentsUser.objects.filter(date__range=(today_start, today_end))
    per_page, page = 10, -1
    possible = True

    while possible:
        page += 1
        for payment in payplug.Payment.list(per_page=per_page, page=page):
            if payment.failure is not None:
                code_error, message_error = payment.failure.code, payment.failure.message
                if code_error == 'card_declined' or 'processing_error' or 'insufficient_funds' or 'incorrect_number':
                    url = payment.hosted_payment.payment_url
                    user = User.objects.get(id=payment.metadata.customer_id)
                    email = user.email
                    send_error_payment(link=url, name=user, message_error=message_error, email=email)


def send_error_payment(link, name, message_error, email):
    subject = "An error occurred..."
    context = {'link_id': link, 'name': name, 'message_error': message_error}
    template = render_to_string("payment/error_payment__mail.html", context)
    EmailMessage(subject, template, to=[email]).send()











