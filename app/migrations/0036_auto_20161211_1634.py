# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-11 16:34
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_auto_20161211_1609'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenariocategoryrating',
            name='rating',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)], verbose_name='Passfaehigkeit'),
        ),
    ]
