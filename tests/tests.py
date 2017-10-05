from django.test import TestCase
from django.conf import settings
from django_purchase.models import PurchaseList, Product, Vendor, VendorProduct
from django_purchase import helpers

class HelpersTestCase(TestCase):

    def test_create_or_update_vendor_product(self):

        product = Product.objects.create()
        vendor = Vendor.objects.create()

        vproduct_t0 = helpers.create_or_update_vendor_product(
            vendor, 'VP1', 13.1, 12, 'UN', product
        )

        self.assertEquals(vproduct_t0.vendor.id, vendor.id)
        self.assertEquals(float(vproduct_t0.get_price()), 13.1)
        self.assertEquals(vproduct_t0.quantity, 12)
        self.assertEquals(vproduct_t0.product_uom.uom.name, 'UN')
        self.assertEquals(vproduct_t0.product_uom.product.id, product.id)

        vproduct_t1 = helpers.create_or_update_vendor_product(
            vendor, 'VP1', 130.1, 12, 'UN', product
        )

        self.assertEquals(vproduct_t1.vendor.id, vendor.id)
        self.assertEquals(float(vproduct_t1.get_price()), 130.1)
        self.assertEquals(vproduct_t1.quantity, 12)
        self.assertEquals(vproduct_t1.product_uom.uom.name, 'UN')
        self.assertEquals(vproduct_t1.product_uom.product.id, product.id)

        self.assertEquals(vproduct_t0.id, vproduct_t1.id)


from django_purchase.strategy import PurchasePlanner

class PurchasePlannerTestCase(TestCase):
    
    def test_empty_purchase_list(self):

        plist = helpers.create_purchase_list_and_resolve([
            ])

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

        self.assertEqual(plist.items.count(), 1)
        item = plist.items.first()
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

        self.assertEqual(plist.items.count(), 1)

        item = plist.items.first()

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

        self.assertEqual(plist.items.count(), 1)

        item = plist.items.first()

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

        self.assertEqual(plist.items.count(), 1)

        item = plist.items.first()

        self.assertEqual(item.resolutions.count(), 1)
        self.assertEqual(item.resolutions.get(vendor_product=vp2).quantity, 6)


    def test_same_product_different_vendors_units_best_price(self):

        vendor1 = Vendor.objects.create()
        vendor2 = Vendor.objects.create()
        product1 = Product.objects.create()


        v1p1, v2p1 = helpers.map_multi(
            helpers.create_or_update_vendor_product, [
                [ vendor1, 'VP1', 1300.1, 12, 'UN', product1 ],
                [ vendor2, 'VP1', 700.1, 6, 'UN', product1 ],
        ])

        helpers.map_multi(
            helpers.create_or_update_vendor_shipping, [
                [ vendor1, 'SM1', 32.3 ],
                [ vendor2, 'SM2', 32.3 ],
        ])

        plist = helpers.create_purchase_list_and_resolve([
            [v1p1.product_uom, 29],
            ])


        self.assertEqual(plist.items.count(), 1)

        item = plist.items.first()

        self.assertEqual(item.resolutions.count(), 2)
        self.assertEqual(item.resolutions.get(vendor_product=v1p1).quantity, 2)
        self.assertEqual(item.resolutions.get(vendor_product=v2p1).quantity, 1)

        self.assertAlmostEqual(float(plist.get_total()), 2*1300.1 + 700.1 + 2*32.3)

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

        self.assertEqual(plist.items.count(), 2)

        items = plist.items

        item1 = items.get(product_uom__product=product1)
        self.assertEqual(item1.resolutions.count(), 1)
        self.assertEqual(item1.resolutions.first().quantity, 3)


        item2 = items.get(product_uom__product=product2)
        self.assertEqual(item2.resolutions.count(), 1)
        self.assertEqual(item2.resolutions.first().quantity, 2)

        self.assertAlmostEqual(float(plist.get_total()), 3*13.1 + 2*7.1 + 32.3)

    def test_two_products_different_vendors(self):

        vendor1 = Vendor.objects.create()
        vendor2 = Vendor.objects.create()
        product1 = Product.objects.create()
        product2 = Product.objects.create()

        v1p1, v2p2 = helpers.map_multi(
            helpers.create_or_update_vendor_product, [
                [ vendor1, 'VP1', 13.1, 12, 'UN', product1 ],
                [ vendor2, 'VP2', 7.1, 7, 'UN', product2 ],
        ])

        helpers.map_multi(
            helpers.create_or_update_vendor_shipping, [
                [ vendor1, 'SM1', 32.3 ],
                [ vendor2, 'SM2', 32.3 ],
        ])

        plist = helpers.create_purchase_list_and_resolve([
            [v1p1.product_uom, 11],
            [v2p2.product_uom, 13],
            ])

        self.assertEqual(plist.items.count(), 2)

        items = plist.items

        item1 = items.get(product_uom__product=product1)
        self.assertEqual(item1.resolutions.count(), 1)
        r1 = item1.resolutions.first()
        self.assertEqual(r1.quantity, 1)
        self.assertEqual(r1.vendor_product.id, v1p1.id)

        item2 = items.get(product_uom__product=product2)
        self.assertEqual(item2.resolutions.count(), 1)
        r2 = item2.resolutions.first()
        self.assertEqual(r2.quantity, 2)
        self.assertEqual(r2.vendor_product.id, v2p2.id)

        self.assertAlmostEqual(float(plist.get_total()), 13.1 + 2*7.1 + 32.3*2)

    def test_two_products_two_vendors(self):

        vendor1 = Vendor.objects.create()
        vendor2 = Vendor.objects.create()
        product1 = Product.objects.create()
        product2 = Product.objects.create()

        v1p1, v1p2, v2p1, v2p2 = helpers.map_multi(
            helpers.create_or_update_vendor_product, [
                [ vendor1, 'VP1', 13.1, 12, 'UN', product1 ],
                [ vendor1, 'VP2', 7.1, 6, 'UN', product2 ],
                [ vendor2, 'VP1', 13.1, 11, 'UN', product1 ],
                [ vendor2, 'VP2', 7.1, 7, 'UN', product2 ],
        ])

        helpers.map_multi(
            helpers.create_or_update_vendor_shipping, [
                [ vendor1, 'SM1', 32.3 ],
                [ vendor2, 'SM2', 32.3 ],
        ])

        plist = helpers.create_purchase_list_and_resolve([
            [v1p1.product_uom, 11],
            [v1p2.product_uom, 13],
            ])

        self.assertEqual(plist.items.count(), 2)

        items = plist.items

        item1 = items.get(product_uom__product=product1)
        self.assertEqual(item1.resolutions.count(), 1)
        r1 = item1.resolutions.first()
        self.assertEqual(r1.quantity, 1)
        self.assertEqual(r1.vendor_product.id, v2p1.id)

        item2 = items.get(product_uom__product=product2)
        self.assertEqual(item2.resolutions.count(), 1)
        r2 = item2.resolutions.first()
        self.assertEqual(r2.quantity, 2)
        self.assertEqual(r2.vendor_product.id, v2p2.id)

        self.assertAlmostEqual(float(plist.get_total()), 13.1 + 2*7.1 + 32.3)

class VendorShippingMethodTestCase(TestCase):
    
    def test_is_lower_price(self):
        v = Vendor.objects.create()
        vs1 = helpers.create_or_update_vendor_shipping(v, 'vs1', 10)
        vs2 = helpers.create_or_update_vendor_shipping(v, 'vs2', 4)
        self.assertFalse(vs1.is_lower_price())
        self.assertTrue(vs2.is_lower_price())

class PurchaseListTestCase(TestCase):

    def test_pending_items(self):

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

        plist = PurchaseList.objects.create()

        self.assertEquals(plist.pending_items(), 0)

        for product_uom, quantity in [
            [vp1.product_uom, 29],
            [vp2.product_uom, 10],
            ]:
            plist.items.create(
                product_uom=product_uom, quantity=quantity)

        self.assertEquals(plist.pending_items(), 2)

        pp = PurchasePlanner()

        pp.resolve_purchase(plist)

        self.assertEquals(plist.pending_items(), 0)

        plist.items.first().resolutions.all().delete()

        self.assertEquals(plist.pending_items(), 1)

        plist.items.first().delete()

        self.assertEquals(plist.pending_items(), 0)

