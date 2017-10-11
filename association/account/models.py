import uuid
import datetime
from django.contrib.auth.models import AbstractUser
from django.db import models

from payment.models import Subscription, Product


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, verbose_name="Username")
    address = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)
    first_name = models.CharField(max_length=255, null=True)
    postcode = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True, verbose_name="Email Address")
    accreditation = models.IntegerField(default=0, verbose_name="Accreditation")  # To manage rights on the site
    # payments = PaymentsUser(models.Model)
    # card = SaveCardUser(models.Model)

    def test_any_payment_valide(self):
        try:
            return any(payment.status == "is_paid" for payment in self.get_all_payments())
        except IndexError:
            return None

    def test_user_data(self):
        return not self.address

    def get_last_payment(self):
        try:
            return self.payments.order_by("-date")[0]
        except IndexError:
            return None

    def get_all_payments(self):
        return self.payments.all()

    def get_last_validate_payment(self):
        try:
            return self.payments.filter(status="is_paid", subscribed_until__date__gte=datetime.date.today()).order_by("-date")[0]
        except IndexError:
            pass
        return None

    def get_last_validate_card(self):
        try:
            return self.card.filter(card_exp_date__date__gte=datetime.date.today(), card_available=True).order_by("-date")[0]
        except IndexError:
            self.set_accreditation(1)
            return None

    def get_subscription(self):
        payment = self.get_last_validate_payment()
        if payment is not None:
            return payment.subscription
        return None

    def get_product(self):
        payment = self.get_last_validate_payment()
        if payment is not None:
            return payment.product
        return None

    def get_recurrent(self):
        product = self.get_product()
        if product is not None:
            return product.recurrent
        return None

    def set_accreditation(self, lvl):
        if self.accreditation != lvl:
            self.accreditation = lvl
            self.save()

    def unsuscribe(self):
        self.set_accreditation(1)
        payment = self.get_last_validate_payment()
        payment.status = "unsuscribe"
        payment.save()
        card = self.get_last_validate_payment()
        if card is not None:
            card.card_available = False
            card.save()


class ValidateUser(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ResetUserPassword(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class PaymentsUser(models.Model):
    reference = models.CharField(max_length=255, unique=True, editable=False)  # Payment id generated by Payplug
    date = models.DateTimeField(auto_now=True)
    subscribed_until = models.DateTimeField("End of your subscription ", null=True)

    status = models.CharField("Status of the payment: ", default="", max_length=255, null=True)  # To manage errors
    error_message = models.CharField("Error message: ", default="", max_length=255, null=True)

    price = models.IntegerField()
    tva = models.IntegerField()

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")

    @property
    def ht_cost(self):
        return int(self.price / (1 + self.tva / 100))


class SaveCardUser(models.Model):
    date = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=255, editable=False)
    last_name = models.CharField(max_length=255, editable=False)
    card_id = models.CharField(max_length=255, editable=False)
    card_exp_date = models.DateTimeField(editable=False)
    card_available = models.BooleanField(default=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="card")
