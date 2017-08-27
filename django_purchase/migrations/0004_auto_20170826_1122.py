# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-26 11:22
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_purchase', '0003_remove_productuom_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('date', models.DateField(default=datetime.date.today, verbose_name='Fecha')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseListItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Cantidad')),
                ('product_uom', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.ProductUOM', verbose_name='Producto y UM')),
                ('purchase_list', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='django_purchase.PurchaseList', verbose_name='Lista de compras')),
            ],
        ),
        migrations.AlterField(
            model_name='vendorproduct',
            name='quantity',
            field=models.DecimalField(decimal_places=2, help_text='La cantidad en la unidad de medida de referencia', max_digits=8, verbose_name='Cantidad'),
        ),
    ]
