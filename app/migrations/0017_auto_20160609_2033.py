# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-09 20:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_auto_20160607_0940'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name': 'Kategorie', 'verbose_name_plural': 'Kategorien'},
        ),
        migrations.AlterModelOptions(
            name='employee',
            options={'ordering': ['username'], 'verbose_name': 'Angestellter', 'verbose_name_plural': 'Angestellte'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ['name'], 'verbose_name': 'Produkt', 'verbose_name_plural': 'Produkte'},
        ),
        migrations.AlterModelOptions(
            name='productset',
            options={'ordering': ['name'], 'verbose_name': 'Produktsammlung', 'verbose_name_plural': 'Produktsammlungen'},
        ),
        migrations.AlterModelOptions(
            name='producttype',
            options={'ordering': ['type_name'], 'verbose_name': 'Produktart', 'verbose_name_plural': 'Produktarten'},
        ),
        migrations.AlterModelOptions(
            name='provider',
            options={'ordering': ['name'], 'verbose_name': 'Hersteller', 'verbose_name_plural': 'Hersteller'},
        ),
        migrations.AlterModelOptions(
            name='providerprofile',
            options={'ordering': ['public_name'], 'verbose_name': 'Herstellerprofil', 'verbose_name_plural': 'Herstellerprofile'},
        ),
        migrations.AlterModelOptions(
            name='scenario',
            options={'ordering': ['name'], 'verbose_name': 'Szenario', 'verbose_name_plural': 'Szenarien'},
        ),
        migrations.AlterModelOptions(
            name='scenariodescription',
            options={'ordering': ['order'], 'verbose_name': 'Szenariobeschreibung', 'verbose_name_plural': 'Szenariobeschreibungen'},
        ),
        migrations.AddField(
            model_name='category',
            name='backgroundPicture',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Bild für den Hintergrund'),
        ),
        migrations.AddField(
            model_name='category',
            name='iconString',
            field=models.CharField(default='gift', max_length=20),
        ),
    ]
