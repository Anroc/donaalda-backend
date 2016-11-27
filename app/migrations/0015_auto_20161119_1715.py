# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-19 16:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0014_auto_20161119_1615'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('belongs_to_category', models.ManyToManyField(to='app.Category', verbose_name='Gehört zu den folgenden Kategorien')),
                ('used_as_filter_by', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Benutzer die diese Subkategorie als Szenariofilter verwenden')),
            ],
        ),
        migrations.AddField(
            model_name='producttype',
            name='used_as_product_type_filter_by',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Als Produkttypfilter verwendet von'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(default=0.5911038997846447, max_length=200),
        ),
        migrations.AlterField(
            model_name='providerprofile',
            name='url_name',
            field=models.CharField(default=0.039302045076924585, max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='categories',
            field=models.ManyToManyField(to='app.Category', verbose_name='Bewertung'),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='url_name',
            field=models.CharField(default=0.45736953143654346, max_length=100, verbose_name='URL-Name'),
        ),
        migrations.AddField(
            model_name='scenario',
            name='subcategory',
            field=models.ManyToManyField(to='app.SubCategory', verbose_name='Dieses Szenario ist Teil dieser Subkategorie'),
        ),
    ]