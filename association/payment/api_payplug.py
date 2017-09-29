import payplug
from django.core.mail import mail_admins
from django.http import HttpResponseRedirect

payplug.set_secret_key('sk_test_5FVRtiAo2p1luWvHMmHa8z')


class Payment(object):
    def __init__(self, user, product, payment_infos=None):
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

    def redirect_payment(self):
        url = self.payment.hosted_payment.payment_url
        return HttpResponseRedirect(url)

    # payplug envoie automatiquement le status de la transaction par mail à l'adresse mail renseignée pour le compte
    # payplug.
    def status_mail_admin(self):
        subject = "Status payment for %s" % self.__user.name
        message = "The payment for %s is %s" % self.__product.name, self.status_payment
        mail_admins(subject=subject, message=message)
