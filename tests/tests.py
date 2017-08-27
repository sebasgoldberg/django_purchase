from django.test import TestCase
from django.conf import settings
from django_purchase.loader import get_loader
from django_purchase.loader import Loader as DefaultLoader
from loader_tests.models import Loader as CustomLoader
from loader_tests.models import MyProduct

from django_purchase.models import PurchaseList, Product, Vendor
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

    def test_one(self):

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
        self.assertEqual(item.resolution.quantity, 1)
        self.assertEqual(item.resolution.vendor_product.id, vp1.id)
