# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-10 14:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_question_icon_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttype',
            name='house_overlay_picture',
            field=models.ImageField(blank=True, null=True, upload_to='productType/house_overlay_picture', verbose_name='Bild'),
        ),
        migrations.AlterField(
            model_name='producttype',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='productType', verbose_name='Bild'),
        ),
    ]
