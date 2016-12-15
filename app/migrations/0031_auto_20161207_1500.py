# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-07 14:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_merge_20161205_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='description',
            field=models.CharField(blank=True, default='Diese Antwort hat noch keine Beschreibung erhalten', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='producttype',
            name='house_overlay_picture',
            field=models.ImageField(blank=True, null=True, upload_to='productType\\house_overlay_picture', verbose_name='Bild'),
        ),
        migrations.AddField(
            model_name='producttype',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='productType\\thumbnail', verbose_name='Bild'),
        ),
        migrations.AddField(
            model_name='question',
            name='description',
            field=models.CharField(blank=True, default='Diese Frage hat noch keine Beschreibung erhalten', max_length=255, null=True),
        ),
    ]