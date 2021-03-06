# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-12 01:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_purchase', '0002_auto_20170901_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaselist',
            name='filter_vendors',
            field=models.BooleanField(default=False, verbose_name='Solo Proveedores Seleccionados'),
        ),
        migrations.AddField(
            model_name='purchaselist',
            name='vendors',
            field=models.ManyToManyField(to='django_purchase.Vendor'),
        ),
        migrations.AlterField(
            model_name='productuom',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_purchase.Product', verbose_name='Producto'),
        ),
        migrations.AlterField(
            model_name='purchaselistitem',
            name='product_uom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='plist_items', to='django_purchase.ProductUOM', verbose_name='Producto y UM'),
        ),
        migrations.AlterField(
            model_name='purchaselistitem',
            name='purchase_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='django_purchase.PurchaseList', verbose_name='Lista de compras'),
        ),
        migrations.AlterField(
            model_name='purchaselistitemresolution',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resolutions', to='django_purchase.PurchaseListItem'),
        ),
        migrations.AlterField(
            model_name='purchaselistitemresolution',
            name='vendor_product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='resolutions', to='django_purchase.VendorProduct', verbose_name='Producto Proveedor'),
        ),
        migrations.AlterField(
            model_name='vendorproduct',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vproducts', to='django_purchase.Vendor', verbose_name='Proveedor'),
        ),
        migrations.AlterField(
            model_name='vendorproductcondition',
            name='instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_purchase.VendorProduct', verbose_name='Producto'),
        ),
        migrations.AlterField(
            model_name='vendorshippingmethod',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_methods', to='django_purchase.Vendor', verbose_name='Proveedor'),
        ),
        migrations.AlterField(
            model_name='vendorshippingmethodcondition',
            name='instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_purchase.VendorShippingMethod', verbose_name='Forma de envío'),
        ),
    ]
