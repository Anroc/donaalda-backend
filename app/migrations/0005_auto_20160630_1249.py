# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-30 12:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20160630_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(default=0.3603810312737413, max_length=200),
        ),
        migrations.AlterField(
            model_name='providerprofile',
            name='url_name',
            field=models.CharField(default=0.28764476835584973, max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='questionset',
            name='question',
            field=models.ManyToManyField(to='app.Question', verbose_name='Dazugehörige Fragen'),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='url_name',
            field=models.CharField(default=0.37801705252937945, max_length=100, verbose_name='URL-Name'),
        ),
    ]