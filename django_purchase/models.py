from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_conditions.models import AbstractCondition as Condition
from datetime import date
from django.core.exceptions import ValidationError

class Product(models.Model):
    pass

class UOM(models.Model):
    name = models.CharField(max_length=3, verbose_name=_('Nombre'), unique=True)

class ProductUOM(models.Model):
    product = models.ForeignKey(Product, verbose_name=_('Producto'), on_delete=models.CASCADE)
    uom = models.ForeignKey(UOM, verbose_name=_('UM'), on_delete=models.PROTECT)

    class Meta:
        unique_together = (("product", "uom"),)

    def get_vendors_products(self, vendors=None):
        if vendors is None:
            return self.vendorproduct_set.all()
        return self.vendorproduct_set.filter(vendor__in=vendors)


class Vendor(models.Model):

    def get_min_delivery_price(self):
        delivery_prices = VendorShippingMethodCondition.current.filter(
            instance__vendor=self)
        if delivery_prices.count() == 0:
            raise ValidationError(_('Debe ser definida la forma de envio y su precio para el proveedor %s') % self.partner.name)
        return min([x.value for x in 
            VendorShippingMethodCondition.current.filter(
                instance__vendor=self)])

class VendorProduct(models.Model):
    vendor = models.ForeignKey(Vendor, verbose_name=_('Proveedor'), on_delete=models.CASCADE, related_name='vproducts')
    name = models.CharField(max_length=255, verbose_name=_('Nombre'))
    product_uom = models.ForeignKey(ProductUOM, verbose_name=_('Producto y UM'), on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=8, decimal_places=2,
        verbose_name=_('Cantidad'),
        help_text=_('La cantidad en la unidad de medida de referencia'))

    class Meta:
        unique_together = (("vendor", "name", 'quantity'),)

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
    name = models.CharField(max_length=100, verbose_name=_('Nombre'), unique=True)

class VendorShippingMethod(models.Model):
    vendor = models.ForeignKey(Vendor, verbose_name=_('Proveedor'), on_delete=models.CASCADE, related_name='shipping_methods')
    shipping_method = models.ForeignKey(ShippingMethod, verbose_name=_('Forma de envío'), on_delete=models.PROTECT)

    def set_price(self, price):
        VendorShippingMethodCondition(
            instance=self,
            value=price
        ).save()

    class Meta:
        unique_together = (("vendor", "shipping_method"),)

    def get_price(self):
        return VendorShippingMethodCondition.current.get(
            instance=self).value

    def is_lower_price(self):
        return self.vendor.get_min_delivery_price() == self.get_price()


class VendorProductCondition(Condition):
    instance = models.ForeignKey(VendorProduct, verbose_name=_('Producto'), on_delete=models.CASCADE)

class VendorShippingMethodCondition(Condition):
    instance = models.ForeignKey(VendorShippingMethod, verbose_name=_('Forma de envío'), on_delete=models.CASCADE)


class PurchaseList(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Nombre'), null=True)
    date = models.DateField(_('Fecha'), default=date.today)
    filter_vendors = models.BooleanField(_('Solo Proveedores Seleccionados'), default=False)
    vendors = models.ManyToManyField(Vendor)

    def get_items(self):
        return self.items.all()

    def get_items_to_solve(self):
        if self.filter_vendors:
            return self.items.filter(product_uom__vendorproduct__vendor__in=self.vendors.all()).distinct()
        return self.get_items()

    def get_vendors_for_item(self, item):
        if self.filter_vendors:
            return item.product_uom.get_vendors_products(self.vendors.all())
        return item.product_uom.get_vendors_products()

    def get_vendors_subtotals(self):

        vendors = {}

        for i in self.get_items():
            for r in i.resolutions.all():
                if r.vendor_product.vendor.id not in vendors:
                    vendors[r.vendor_product.vendor.id] = 0
                vendors[r.vendor_product.vendor.id] += r.vendor_product.get_price() * r.quantity

        return vendors

        
    def calc_total(self):

        total = 0

        vendors = {}

        for i in self.get_items():
            for r in i.resolutions.all():
                total += r.vendor_product.get_price() * r.quantity
                if r.vendor_product.vendor.id not in vendors:
                    vendors[r.vendor_product.vendor.id] = r.vendor_product.vendor

        for _, v in vendors.items():
            total += v.get_min_delivery_price()

        return total

    def get_total(self):
        return self.calc_total()

    def pending_items(self):
        result = 0
        for i in self.items.all():
            if not i.is_solved():
                result += 1
        return result


class PurchaseListItem(models.Model):
    purchase_list = models.ForeignKey(PurchaseList, verbose_name=_('Lista de compras'), on_delete=models.CASCADE, 
        related_name='items')
    product_uom = models.ForeignKey(ProductUOM, verbose_name=_('Producto y UM'), on_delete=models.PROTECT,
        related_name='plist_items')
    quantity = models.DecimalField(max_digits=8, decimal_places=2,
        verbose_name=_('Cantidad'))

    def resolve_purchase_with(self, vproduct, quantity):
        self.resolutions.create(
            item=self,
            vendor_product=vproduct,
            quantity=quantity
            )

    def get_solved_quantity(self): # @todo Test.
        """
        Gets the sum of uom quantities of self.resolutions.
        """
        return sum([r.get_uom_quantity() for r in self.resolutions.all()])

    def is_solved(self): # @todo Test.
        return self.quantity > 0 and self.quantity <= self.get_solved_quantity()

    def get_surplus_quantity(self): # @todo Test.
        return self.get_solved_quantity() - self.quantity

class PurchaseListItemResolution(models.Model):
    item = models.ForeignKey(PurchaseListItem, on_delete=models.CASCADE,
        related_name='resolutions')
    vendor_product = models.ForeignKey(VendorProduct, verbose_name=_('Producto Proveedor'), on_delete=models.PROTECT,
        related_name='resolutions')
    quantity = models.DecimalField(max_digits=8, decimal_places=2,
        verbose_name=_('Cantidad'))

    class Meta:
        unique_together = (("item", "vendor_product"),)

    def get_total(self):
        return self.vendor_product.get_price()*self.quantity

    def get_uom_quantity(self):
        return self.quantity * self.vendor_product.quantity

