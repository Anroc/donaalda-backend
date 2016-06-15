# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-15 12:02
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_auto_20160612_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='page_url',
            field=models.URLField(default=''),
        ),
        migrations.AlterField(
            model_name='comment',
            name='rating',
            field=models.PositiveSmallIntegerField(default='0', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Bewertung'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(default=0.9280866984231487, max_length=200),
        ),
        migrations.AlterField(
            model_name='providerprofile',
            name='url_name',
            field=models.CharField(default=0.46955394753714896, max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='url_name',
            field=models.CharField(default=0.6068874675941326, max_length=100),
        ),
    ]
