import uuid

from django.db import models


class Subscription(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False, verbose_name="Name")
    informations = models.TextField(max_length=500, editable=True)


class Product(models.Model):
    name = models.CharField(max_length=255, null=False, verbose_name="Name")
    informations = models.TextField(max_length=500, editable=True)
    price = models.IntegerField()
    duration = models.IntegerField("duration of the subscription in days")
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='products')
