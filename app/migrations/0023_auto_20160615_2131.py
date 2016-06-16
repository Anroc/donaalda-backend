# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-15 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0022_auto_20160615_1412'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-creation_date', 'comment_title', '-rating'], 'verbose_name': 'Kommentar', 'verbose_name_plural': 'Kommentare'},
        ),
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(default=0.09897083354066016, max_length=200),
        ),
        migrations.AlterField(
            model_name='providerprofile',
            name='url_name',
            field=models.CharField(default=0.4770776137188697, max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='url_name',
            field=models.CharField(default=0.18132264089390815, max_length=100),
        ),
    ]