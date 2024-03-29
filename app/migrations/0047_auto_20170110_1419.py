# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-10 14:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0046_auto_20170109_0942'),
    ]

    operations = [
        migrations.RenameField(
            model_name='producttype',
            old_name='house_overlay_picture',
            new_name='icon',
        ),
        migrations.RemoveField(
            model_name='producttype',
            name='thumbnail',
        ),
        migrations.AddField(
            model_name='producttype',
            name='svg_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Id of the svg in the house overview'),
        ),
    ]
