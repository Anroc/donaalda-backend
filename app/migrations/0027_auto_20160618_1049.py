# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-18 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_auto_20160615_2159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='scenario_set',
        ),
        migrations.AddField(
            model_name='scenario',
            name='categories',
            field=models.ManyToManyField(to='app.Category', verbose_name='passende Kategorien'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(default=0.9310414613489739, max_length=200),
        ),
        migrations.AlterField(
            model_name='providerprofile',
            name='url_name',
            field=models.CharField(default=0.9516664987484033, max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='url_name',
            field=models.CharField(default=0.3630148838322994, max_length=100),
        ),
    ]
