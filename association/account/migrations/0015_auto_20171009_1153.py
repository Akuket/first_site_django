# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-09 09:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_auto_20171006_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentsuser',
            name='price',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentsuser',
            name='tva',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]