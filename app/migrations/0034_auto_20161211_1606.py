# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-11 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_auto_20161210_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenario',
            name='categories',
            field=models.ManyToManyField(related_name='scenario_category_rating', through='app.ScenarioCategoryRating', to='app.Category', verbose_name='Bewertung'),
        ),
    ]
