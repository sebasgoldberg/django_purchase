from .models import ProductUOM, UOM, VendorProduct, PurchaseList, ShippingMethod
from .strategy import PurchasePlanner

def map_multi(f, v):
    r = []
    for x in v:
        r.append(f(*x))
    return r

def create_or_update_vendor_product(vendor, vendor_product_name,
    price, content_quantity, quantity_uom_name, product):
    
    vproduct = None

    uom, _ = UOM.objects.get_or_create(name=quantity_uom_name)
    product_uom, _ = ProductUOM.objects.get_or_create(
        product=product, uom=uom)

    try:

        vproduct = vendor.vproducts.get(
            name=vendor_product_name, quantity=content_quantity)

        if vproduct.product_uom.id != product_uom.id or \
            vproduct.quantity != content_quantity:
            vproduct.product_uom = product_uom
            vproduct.quantity = content_quantity
            vproduct.save()

        if vproduct.get_price() != price:
            vproduct.set_price(price)

    except VendorProduct.DoesNotExist:

        vproduct = vendor.vproducts.create(
            name=vendor_product_name,
            product_uom=product_uom,
            quantity=content_quantity
            )
        vproduct.set_price(price)

    return vproduct

def create_purchase_list_and_resolve(products_uom_and_quantities, vendors=None):

    plist = None
    if vendors is None:
        plist = PurchaseList.objects.create()
    else:
        plist = PurchaseList.objects.create(
            filter_vendors=True,
            )
        plist.vendors = vendors
        plist.save()

    for product_uom, quantity in products_uom_and_quantities:
        plist.items.create(
            product_uom=product_uom, quantity=quantity)

    pp = PurchasePlanner()

    pp.resolve_purchase(plist)

    return plist

def create_or_update_vendor_shipping(vendor, shipping_method_name, price):
    
    shipping_method, _ = ShippingMethod.objects.get_or_create(
        name=shipping_method_name)
    vshipping_method, _ = vendor.shipping_methods.get_or_create(
        shipping_method=shipping_method)
    vshipping_method.set_price(price)
    return vshipping_method

