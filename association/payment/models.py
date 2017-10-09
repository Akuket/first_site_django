import uuid

from django.db import models


class Subscription(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, verbose_name="Name")
    description = models.TextField(max_length=500, editable=True)
    # products = Product(models.Model)
    # payments = PaymentsUser(models.Model)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, null=False, verbose_name="Name")
    description = models.TextField(max_length=500, editable=True)
    price = models.IntegerField()
    tva = models.IntegerField()
    ht = models.IntegerField()
    recurrent = models.BooleanField(default=False)  # recursive payment
    duration = models.IntegerField("duration of the subscription in days")
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='products')
    # payments = PaymentsUser(models.Model)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.price = self.ht + (self.tva / 100) * self.ht
        super(Product, self).save(*args, **kwargs)

