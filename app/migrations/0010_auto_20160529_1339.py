# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-29 11:39
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0007_alter_validators_add_error_messages'),
        ('app', '0009_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Angestellte',
                'verbose_name': 'Angestellter',
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Produktarten',
                'verbose_name': 'Produktart',
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Hersteller',
                'verbose_name': 'Hersteller',
            },
        ),
        migrations.CreateModel(
            name='ProviderProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_name', models.CharField(max_length=200, unique=True)),
                ('logo_image', models.ImageField(upload_to='')),
                ('banner_image', models.ImageField(upload_to='')),
                ('introduction', models.TextField()),
                ('contact_email', models.EmailField(max_length=254)),
                ('website', models.URLField()),
                ('owner', models.OneToOneField(default='1', on_delete=django.db.models.deletion.CASCADE, to='app.Provider')),
            ],
            options={
                'verbose_name_plural': 'Herstellerprofile',
                'verbose_name': 'Herstellerprofil',
            },
        ),
        migrations.RenameField(
            model_name='product',
            old_name='end_of_Life',
            new_name='end_of_life',
        ),
        migrations.RemoveField(
            model_name='product',
            name='thumbnail',
        ),
        migrations.AddField(
            model_name='product',
            name='serial_number',
            field=models.CharField(default='------', max_length=255),
        ),
        migrations.AddField(
            model_name='scenario',
            name='scenario_product_set',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.ProductSet'),
        ),
        migrations.AlterField(
            model_name='category',
            name='picture',
            field=models.ImageField(upload_to='categories', verbose_name='Bild für die Kategorie'),
        ),
        migrations.AlterField(
            model_name='product',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='product',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='employee',
            name='employer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Provider'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.ForeignKey(default='0', on_delete=django.db.models.deletion.CASCADE, to='app.ProductType'),
        ),
        migrations.AddField(
            model_name='product',
            name='provider',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='app.Provider'),
        ),
        migrations.AddField(
            model_name='productset',
            name='creator',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='app.Provider'),
        ),
        migrations.AddField(
            model_name='scenario',
            name='provider',
            field=models.ForeignKey(default='1', on_delete=django.db.models.deletion.CASCADE, to='app.Provider'),
        ),
    ]