# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-27 17:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0055_auto_20170116_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenario',
            name='title',
            field=models.CharField(default='---', max_length=255),
        ),
    ]
