import payplug
import datetime
from django.http import HttpResponseRedirect

from account.models import PaymentsUser, SaveCardUser, User

payplug.set_secret_key('sk_test_5FVRtiAo2p1luWvHMmHa8z')


def classic_payment(user, subscription, product, data=None):
    """
    Create a classic payment with Payplug

    :param user: The user related to the payment
    :param subscription: The subscription related to the payment
    :param product: The product related to the payment
    :param data: Optional parameter to complete the creation of the payment
    :return: Redirect to Payplug site
    """
    payment_data = {
        'amount': int(product.price * 100),  # In cents, 1 euro minimum
        'customer': {'email': str(user.email)},
        'save_card': False,
        'currency': 'EUR',
        'metadata': {
            'customer_id': user.id,
        },
    }

    if data:
        payment_data.update(data)

    payment = payplug.Payment.create(**payment_data)  # Create the payment object
    payment_user = PaymentsUser(reference=str(payment.id), subscription=subscription, product=product, user=user)
    payment_user.save()
    return HttpResponseRedirect(payment.hosted_payment.payment_url)  # redirect to Payplug's site


def recursive_payment(user, subscription, product, data=None):
    """
    Create a recursive payment with Payplug

    :param user: The user related to the payment
    :param subscription: The subscription related to the payment
    :param product: The product related to the payment
    :param data: Optional parameter to complete the creation of the payment
    """
    try:
        card = SaveCardUser.objects.get(user=user, card_exp_date__gte=datetime.date.today(), card_available=True)
    except SaveCardUser.DoesNotExist:
        user.accreditation = 1
        user.subscription = None
        user.product = None
        user.subscriber = None
        user.save()
    else:
        payment_data = {
            'amount': int(product.price * 100),  # In cents, 1 euro minimum
            'customer': {'email': str(user.email)},
            'save_card': True,
            'currency': 'EUR',
            'payment_method': card.id,
            'metadata': {
                'customer_id': user.id,
            },
        }

        if data:
            payment_data.update(data)

        payment = payplug.Payment.create(**payment_data)  # creation de l'object payment
        payment_user = PaymentsUser(reference=str(payment.id), subscription=subscription, product=product, user=user)
        payment_user.save()


def update_user(response, user, payment):
    """
    Update the user's accreditation on the site and save the card if needed

    :param response: An api provide by Payplug to manage the post response of the Payplug's site for the payment.
    :param user: The user related to the payment
    :param payment: Data about the payment, stored in db. Refers to the model PaymentsUser
    """
    if response.save_card:  # Store the blank card in db
        save_card(response=response, user=user)

    date = datetime.date.today()
    user.accreditation = 2
    user.subscription = payment.subscription.name
    user.product = payment.product.name
    user.subscriber = date + datetime.timedelta(payment.product.duration)
    user.save()


def save_card(response, user):
    """
    Save the bank card imprint in db if it doesn't in.

    :param response: An api provide by Payplug to manage the post response of the Payplug's site for the payment.
    :param user: The user related to the payment
    """
    try:
        SaveCardUser.objects.get(card_id=response.card.id)
    except SaveCardUser.DoesNotExist:
        card_id = response.card.id
        card_exp_date = datetime.date(response.card.exp_year, response.card.exp_month, 30)
        card = SaveCardUser(card_id=card_id, card_exp_date=card_exp_date, user=user)
        card.save()


def checks():
    """
    Check if cards stored in db are already available
    Check user's accreditation on the site, based on subscription duration
    """
    today = datetime.date.today()
    SaveCardUser.objects.filter(card_available=True, card_exp_date__lt=today).update(card_available=False)

    User.objects.filter(accreditation=2, subscriber__lt=today)\
                .update(accrediation=1, subscriber=None, subscription=None, product=None)
