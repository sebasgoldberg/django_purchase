# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-24 16:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductUOM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ShippingMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
            ],
        ),
        migrations.CreateModel(
            name='UOM',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=3, verbose_name='Nombre')),
            ],
        ),
        migrations.CreateModel(
            name='VendorProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nombre')),
                ('quantity', models.PositiveIntegerField(help_text='La cantidad en la unidad de medida de referencia', verbose_name='Cantidad')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.Partner', verbose_name='Proveedor')),
                ('product_uom', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.ProductUOM', verbose_name='Producto y UM')),
            ],
        ),
        migrations.CreateModel(
            name='VendorProductCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_date', models.DateField(default=datetime.date.today, verbose_name='Fecha de inicio')),
                ('end_date', models.DateField(default=datetime.date(9999, 12, 31), verbose_name='Fecha de fin')),
                ('value', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Valor')),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.VendorProduct', verbose_name='Producto')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VendorShippingMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.Partner', verbose_name='Proveedor')),
                ('shipping_method', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.ShippingMethod', verbose_name='Forma de envío')),
            ],
        ),
        migrations.CreateModel(
            name='VendorShippingMethodCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('begin_date', models.DateField(default=datetime.date.today, verbose_name='Fecha de inicio')),
                ('end_date', models.DateField(default=datetime.date(9999, 12, 31), verbose_name='Fecha de fin')),
                ('value', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Valor')),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.VendorShippingMethod', verbose_name='Forma de envío')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='productuom',
            name='UOM',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.UOM', verbose_name='UM'),
        ),
        migrations.AddField(
            model_name='productuom',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.Product', verbose_name='Producto'),
        ),
    ]