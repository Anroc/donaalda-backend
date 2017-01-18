# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-16 06:41
from __future__ import unicode_literals

from django.db import migrations


def merge_product_description_and_specs(apps, schema_editor):
    Product = apps.get_model('app', 'Product')
    for product in Product.objects.all():
        product.markdown_description = (
                "#Beschreibung\n\n{0}\n\n#Spezifikationen\n\n{1}"
        ).format(product.description, product.specifications)
        product.save()

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0052_product_markdown_description'),
    ]

    operations = [
        migrations.RunPython(merge_product_description_and_specs),
    ]
