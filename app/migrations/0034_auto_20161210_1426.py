# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-10 14:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_auto_20161210_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttype',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='productType/thumbnail', verbose_name='Bild'),
        ),
    ]