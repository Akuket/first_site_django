# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-05 08:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0009_savecarduser'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentsuser',
            name='error_message',
            field=models.CharField(default='', max_length=255, null=True, verbose_name='Error message: '),
        ),
        migrations.AddField(
            model_name='savecarduser',
            name='card_available',
            field=models.BooleanField(default=True),
        ),
    ]