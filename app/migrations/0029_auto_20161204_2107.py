# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-04 21:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_auto_20161204_2051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='follower_protocol',
            field=models.ManyToManyField(blank=True, related_name='protocol_follower', to='app.Protocol', verbose_name='Spricht Protokoll im follower modus'),
        ),
        migrations.AlterField(
            model_name='product',
            name='leader_protocol',
            field=models.ManyToManyField(blank=True, related_name='protocol_leader', to='app.Protocol', verbose_name='Spricht Protokoll im leader modus'),
        ),
    ]
