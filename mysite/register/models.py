from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    is_subscriber = models.BooleanField(default=False)
    date_end_subscription = models.DateTimeField('End of subscription')


