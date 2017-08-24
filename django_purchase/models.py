from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_conditions.models import AbstractCondition as Condition
from .loader import get_loader

loader = get_loader()

Product = loader.get_product_model()
Partner = loader.get_partner_model()

class UOM(models.Model):
    name = models.CharField(max_length=3, verbose_name=_('Nombre'))

class ProductUOM(models.Model):
    name = models.CharField(max_length=3, verbose_name=_('Nombre'), null=True)
    product = models.ForeignKey(Product, verbose_name=_('Producto'), on_delete=models.PROTECT)
    UOM = models.ForeignKey(UOM, verbose_name=_('UM'), on_delete=models.PROTECT)

class VendorProduct(models.Model):
    partner = models.ForeignKey(Partner, verbose_name=_('Proveedor'), on_delete=models.PROTECT)
    name = models.CharField(max_length=255, verbose_name=_('Nombre'))
    product_uom = models.ForeignKey(ProductUOM, verbose_name=_('Producto y UM'), on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(_('Cantidad'),
        help_text=_('La cantidad en la unidad de medida de referencia'))

class ShippingMethod(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Nombre'))

class VendorShippingMethod(models.Model):
    partner = models.ForeignKey(Partner, verbose_name=_('Proveedor'), on_delete=models.PROTECT)
    shipping_method = models.ForeignKey(ShippingMethod, verbose_name=_('Forma de envío'), on_delete=models.PROTECT)

class VendorProductCondition(Condition):
    instance = models.ForeignKey(VendorProduct, verbose_name=_('Producto'), on_delete=models.PROTECT)

class VendorShippingMethodCondition(Condition):
    instance = models.ForeignKey(VendorShippingMethod, verbose_name=_('Forma de envío'), on_delete=models.PROTECT)
