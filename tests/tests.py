from django.test import TestCase
from django.conf import settings
from django_purchase.loader import get_loader
from django_purchase.loader import Loader as DefaultLoader
from loader_tests.models import Loader as CustomLoader
from loader_tests.models import MyProduct

from django_purchase.models import PurchaseList, Product, Vendor, VendorProduct
from django_purchase import helpers

# Create your tests here.
class LoaderTestCase(TestCase):

    def test_get_default_loader(self):
        
        loader = get_loader()

        self.assertEquals(loader.__class__,  DefaultLoader)


    def test_get_custom_loader(self):
        
        with self.settings(PURCHASE_LOADER='loader_tests.models.Loader'):
            loader = get_loader()
            self.assertEquals(loader.__class__,  CustomLoader)

    def test_get_default_product_model(self):

        loader = get_loader()
        
        product_model = loader.get_product_model()

        self.assertNotEquals(product_model, MyProduct)


    def test_get_custom_product_model(self):


        with self.settings(PURCHASE_LOADER='loader_tests.models.Loader'):
            loader = get_loader()
            
            product_model = loader.get_product_model()

            self.assertEquals(product_model, MyProduct)


from django_purchase.strategy import PurchasePlanner

class PurchasePlannerTestCase(TestCase):
    
    def test_empty_purchase_list(self):
        
        plist = PurchaseList.objects.create()

        pp = PurchasePlanner()

        pp.resolve_purchase(plist)

    def test_one_product(self):

        vendor = Vendor.objects.create()

        vp1 = helpers.create_or_update_vendor_product(
            vendor,
            'VP1',
            13.1,
            12,
            'UN',
            Product.objects.create()
        )

        helpers.create_or_update_vendor_shipping(
            vendor,
            'SM1',
            32.3
        )

        plist = helpers.create_purchase_list_and_resolve([
            [vp1.product_uom, 10],
            ])

        self.assertEqual(plist.purchaselistitem_set.count(), 1)
        item = plist.purchaselistitem_set.first()
        self.assertEqual(item.resolutions.first().quantity, 1)
        self.assertEqual(item.resolutions.first().vendor_product.id, vp1.id)


    def test_same_product_different_vendor_units(self):

        vendor = Vendor.objects.create()
        product = Product.objects.create()

        vp1 = helpers.create_or_update_vendor_product(
            vendor,
            'VP1',
            13.1,
            12,
            'UN',
            product
        )

        vp2 = helpers.create_or_update_vendor_product(
            vendor,
            'VP2',
            7.1,
            6,
            'UN',
            product
        )

        helpers.create_or_update_vendor_shipping(
            vendor,
            'SM1',
            32.3
        )

        plist = helpers.create_purchase_list_and_resolve([
            [vp1.product_uom, 30],
            ])

        self.assertEqual(plist.purchaselistitem_set.count(), 1)

        item = plist.purchaselistitem_set.first()

        self.assertEqual(item.resolutions.count(), 2)
        self.assertEqual(item.resolutions.get(vendor_product=vp1).quantity, 2)
        self.assertEqual(item.resolutions.get(vendor_product=vp2).quantity, 1)

    def test_same_product_different_vendors_best_price(self):

        vendor1 = Vendor.objects.create()
        vendor2 = Vendor.objects.create()
        product = Product.objects.create()

        vp1 = helpers.create_or_update_vendor_product(
            vendor1,
            'VP1',
            13.1,
            12,
            'UN',
            product
        )

        vp2 = helpers.create_or_update_vendor_product(
            vendor2,
            'VP2',
            7.1,
            6,
            'UN',
            product
        )

        helpers.create_or_update_vendor_shipping(
            vendor1,
            'SM1',
            32.3
        )

        helpers.create_or_update_vendor_shipping(
            vendor2,
            'SM2',
            32.3
        )

        plist = helpers.create_purchase_list_and_resolve([
            [vp1.product_uom, 36],
            ])

        self.assertEqual(plist.purchaselistitem_set.count(), 1)

        item = plist.purchaselistitem_set.first()

        self.assertEqual(item.resolutions.count(), 1)
        self.assertEqual(item.resolutions.get(vendor_product=vp1).quantity, 3)


    def test_same_product_different_vendors_best_shipping(self):

        vendor1 = Vendor.objects.create()
        vendor2 = Vendor.objects.create()
        product = Product.objects.create()

        vp1 = helpers.create_or_update_vendor_product(
            vendor1,
            'VP1',
            13.1,
            12,
            'UN',
            product
        )

        vp2 = helpers.create_or_update_vendor_product(
            vendor2,
            'VP2',
            7.1,
            6,
            'UN',
            product
        )

        helpers.create_or_update_vendor_shipping(
            vendor1,
            'SM1',
            32.3
        )

        helpers.create_or_update_vendor_shipping(
            vendor2,
            'SM2',
            15.2
        )

        plist = helpers.create_purchase_list_and_resolve([
            [vp1.product_uom, 36],
            ])

        self.assertEqual(plist.purchaselistitem_set.count(), 1)

        item = plist.purchaselistitem_set.first()

        self.assertEqual(item.resolutions.count(), 1)
        self.assertEqual(item.resolutions.get(vendor_product=vp2).quantity, 6)


    def test_two_products(self):

        vendor1 = Vendor.objects.create()
        product1 = Product.objects.create()
        product2 = Product.objects.create()

        vp1 = helpers.create_or_update_vendor_product(
            vendor1,
            'VP1',
            13.1,
            12,
            'UN',
            product1
        )

        vp2 = helpers.create_or_update_vendor_product(
            vendor1,
            'VP2',
            7.1,
            6,
            'UN',
            product2
        )

        helpers.create_or_update_vendor_shipping(
            vendor1,
            'SM1',
            32.3
        )

        plist = helpers.create_purchase_list_and_resolve([
            [vp1.product_uom, 29],
            [vp2.product_uom, 10],
            ])

        self.assertEqual(plist.purchaselistitem_set.count(), 2)

        items = plist.purchaselistitem_set

        item1 = items.get(product_uom__product=product1)
        self.assertEqual(item1.resolutions.count(), 1)
        self.assertEqual(item1.resolutions.first().quantity, 3)


        item2 = items.get(product_uom__product=product2)
        self.assertEqual(item2.resolutions.count(), 1)
        self.assertEqual(item2.resolutions.first().quantity, 2)

