# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-15 21:49
from __future__ import unicode_literals

from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0052_auto_20170117_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='markdown_description',
            field=markdownx.models.MarkdownxField(default='', verbose_name='Beschreibung'),
            preserve_default=False,
        ),
    ]
