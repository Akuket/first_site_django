import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

from payment.models import Subscription, Product


class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True, verbose_name="Username")
    email = models.EmailField(unique=True, verbose_name="Email Address")
    accreditation = models.IntegerField(default=0, verbose_name="Accreditation")
    subscriber = models.DateTimeField("Time before end of your subscription: ", null=True)
    subscription = models.CharField("Type of subscription: ", max_length=255, null=True)
    product = models.CharField("Type of product: ", max_length=255, null=True)


class ValidateUser(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class ResetUserPassword(models.Model):
    token = models.UUIDField(default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class PaymentsUser(models.Model):
    reference = models.CharField(max_length=255, unique=True)
    date = models.DateTimeField(auto_now=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="payments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
