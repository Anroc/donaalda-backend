# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-23 18:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0057_auto_20170123_1918'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='feature',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='protocol',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'ordering': ['name']},
        ),
    ]
