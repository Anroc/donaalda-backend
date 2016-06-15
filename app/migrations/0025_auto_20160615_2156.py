# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-15 19:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_auto_20160615_2134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(default=0.9430191281287251, max_length=200),
        ),
        migrations.AlterField(
            model_name='providerprofile',
            name='url_name',
            field=models.CharField(default=0.8895789071667275, max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='url_name',
            field=models.CharField(default=0.07435448072300532, max_length=100),
        ),
    ]
