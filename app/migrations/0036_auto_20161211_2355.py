# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-11 23:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0035_merge_20161211_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttype',
            name='house_overlay_picture',
            field=models.ImageField(blank=True, null=True, upload_to='productType/house_overlay_picture', verbose_name='Bildicon in der Hausvorschau'),
        ),
        migrations.AlterField(
            model_name='producttype',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='productType/thumbnail', verbose_name='Thumbnail'),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='url_name',
            field=models.CharField(max_length=255, verbose_name='URL-Name'),
        ),
    ]
