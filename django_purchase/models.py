from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_conditions.models import AbstractCondition as Condition
from .loader import get_loader
from datetime import date
from django.core.exceptions import ValidationError

loader = get_loader()

Product = loader.get_product_model()
Partner = loader.get_partner_model()

class UOM(models.Model):
    name = models.CharField(max_length=3, verbose_name=_('Nombre'))

class ProductUOM(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Producto'), on_delete=models.PROTECT)
    uom = models.ForeignKey(UOM, verbose_name=_('UM'), on_delete=models.PROTECT)

    def get_vendors_products(self):
        return self.vendorproduct_set.all()


class Vendor(Partner):

    class Meta:
        proxy = True

    def get_min_delivery_price(self):
        delivery_prices = VendorShippingMethodCondition.current.filter(
            instance__vendor=self)
        if delivery_prices.count() == 0:
            raise ValidationError(_('Debe ser definida la forma de envio y su precio para el proveedor %s') % self)
        return min([x.value for x in 
            VendorShippingMethodCondition.current.filter(
                instance__vendor=self)])

class VendorProduct(models.Model):
    vendor = models.ForeignKey(Vendor, verbose_name=_('Proveedor'), on_delete=models.PROTECT)
    name = models.CharField(max_length=255, verbose_name=_('Nombre'))
    product_uom = models.ForeignKey(ProductUOM, verbose_name=_('Producto y UM'), on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=8, decimal_places=2,
        verbose_name=_('Cantidad'),
        help_text=_('La cantidad en la unidad de medida de referencia'))

    def set_price(self, price):
        VendorProductCondition(
            instance=self,
            value=price
        ).save()

    def get_price(self):
        return VendorProductCondition.current.get(
            instance=self).value

    def get_content(self):
        return self.quantity


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Nombre'))

class VendorShippingMethod(models.Model):
    vendor = models.ForeignKey(Vendor, verbose_name=_('Proveedor'), on_delete=models.PROTECT)
    shipping_method = models.ForeignKey(ShippingMethod, verbose_name=_('Forma de envío'), on_delete=models.PROTECT)

    def set_price(self, price):
        VendorShippingMethodCondition(
            instance=self,
            value=price
        ).save()


class VendorProductCondition(Condition):
    instance = models.ForeignKey(VendorProduct, verbose_name=_('Producto'), on_delete=models.PROTECT)

class VendorShippingMethodCondition(Condition):
    instance = models.ForeignKey(VendorShippingMethod, verbose_name=_('Forma de envío'), on_delete=models.PROTECT)


class PurchaseList(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Nombre'), null=True)
    date = models.DateField(_('Fecha'), default=date.today)

    def get_items(self):
        return self.purchaselistitem_set.all()

class PurchaseListItem(models.Model):
    purchase_list = models.ForeignKey(PurchaseList, verbose_name=_('Lista de compras'), on_delete=models.PROTECT)
    product_uom = models.ForeignKey(ProductUOM, verbose_name=_('Producto y UM'), on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=8, decimal_places=2,
        verbose_name=_('Cantidad'))

