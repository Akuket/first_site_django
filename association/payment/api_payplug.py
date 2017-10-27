import datetime
import uuid

import payplug

from account.models import PaymentsUser, SaveCardUser, User
from .config import SECRET_KEY

payplug.set_secret_key(SECRET_KEY)

PAID_PAYMENT_STATUS = "is_paid"


def create_classic_payment(user, subscription, product, data=None):
    """
    Create a classic payment with Payplug

    :param user: The user related to the payment
    :param subscription: The subscription related to the payment
    :param product: The product related to the payment
    :param data: Optional parameter to complete the creation of the payment
    :return: A redirect url to Payplug
    """
    token = uuid.uuid4()
    cents_price = 100 * product.price
    if cents_price != int(cents_price):
        raise ValueError("au centime pres")

    payment_data = {
        'amount': int(cents_price),  # In cents, 1 euro minimum
        'customer': {'email': str(user.email)},
        'save_card': product.recurrent,
        'currency': 'EUR',
        'metadata': {
            'token': token.hex,
        },
    }
    if data:
        payment_data.update(data)

    subscribed_until = datetime.date.today() + datetime.timedelta(product.duration)
    payment = payplug.Payment.create(**payment_data)  # Create the payment object
    payment_user = PaymentsUser(reference=str(payment.id), subscription=subscription, product=product, user=user,
                                price=product.price, tva=product.tva, subscribed_until=subscribed_until, token=token)
    payment_user.save()
    return payment


def make_recurring_payment(user, data=None):
    """
    Create a recursive payment with Payplug

    :param user: The user related to the payment
    :param data: Optional parameter to complete the creation of the payment
    """
    card_object = user.get_last_validate_card()
    product = user.get_product()
    subscription = user.get_subscription()
    token = uuid.uuid4()

    if card_object is not None and product is not None and subscription is not None:
        cents_price = 100 * product.price
        if cents_price != int(cents_price):
            raise ValueError("au centime pres")

        payment_data = {
            'amount': int(cents_price),  # In cents, 1 euro minimum
            'customer': {'email': str(user.email), 'first_name': str(card_object.first_name),
                         'last_name': str(card_object.last_name)},
            'save_card': False,
            'currency': 'EUR',
            'payment_method': str(card_object.card_id),  # Important to make a recurring payment
            'metadata': {
                'token': token.hex,
            },
        }

        if data:
            payment_data.update(data)

        duration = datetime.date.today() + datetime.timedelta(product.duration)
        payment = payplug.Payment.create(**payment_data)  # creation de l'object payment
        if payment.is_paid:
            payment_user = PaymentsUser(reference=str(payment.id), subscription=subscription, product=product,
                                        user=user, price=product.price, tva=product.tva, subscribed_until=duration,
                                        token=token)
            payment_user.save()


def update_payment(payment_object):
    """
    Update the payment next to the post of Payplug on the notification url
    :param payment_object: Response provide by Payplug
    """
    status = None
    payment = PaymentsUser.objects.get(reference=str(payment_object.id))
    if payment_object.object == 'payment' and payment_object.is_paid:  # Update user's subscription if the payment is done
        if payment_object.metadata["token"] == payment.token.hex:
            status = PAID_PAYMENT_STATUS
            update_user(payment_object=payment_object, user=payment.user)

        else:
            status = "Fraud_suspected"
            payment.error_message = "Caution, the token provided not match with the token stored in data base"

    elif payment_object.object == 'payment' and payment_object.failure:  # An error is occurred
        status = str(payment_object.failure.code)
        payment.error_message = str(payment_object.failure.message)

    # elif response.object == 'refund':  # The refund method
    #    pass

    payment.status = status
    payment.save()


def update_user(payment_object, user):
    """
    Update the user's accreditation on the site and save the card if needed

    :param payment_object: An api provide by Payplug to manage the post response of the Payplug's site for the payment.
    :param user: The user related to the payment
    """
    if payment_object.save_card:  # Store the blank card in db
        save_card(response=payment_object, user=user)

    user.set_accreditation(2)


def save_card(response, user):
    """
    Save the bank card imprint in db if it doesn't in.

    :param response: An api provide by Payplug to manage the post response of the Payplug's site for the payment.
    :param user: The user related to the payment
    """
    try:
        SaveCardUser.objects.get(card_id=response.card.id)
    except SaveCardUser.DoesNotExist:
        first_name = response.customer.first_name
        last_name = response.customer.last_name
        card_id = response.card.id
        card_exp_date = datetime.date(response.card.exp_year, response.card.exp_month, 30)
        card = SaveCardUser(first_name=first_name, last_name=last_name, card_id=card_id,
                            card_exp_date=card_exp_date, user=user)
        card.save()


def find_recurring_payments():
    today = datetime.date.today()
    try:
        for user in User.objects.filter(accreditation=2, payments__subscribed_until=today,
                                        payments__product__recurrent=True):
            make_recurring_payment(user)
    except TypeError:
        pass


def checks():
    """
    Check if cards stored in db are already available
    Check user's accreditation on the site, based on subscription duration
    """
    today = datetime.date.today()
    SaveCardUser.objects.filter(card_available=True, card_exp_date__lt=today).update(card_available=False)
    User.objects.filter(accreditation=2, payments__subscribed_until__lt=today).update(accreditation=1)
