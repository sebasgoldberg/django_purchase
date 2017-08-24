from django.test import TestCase
from django.conf import settings
from django_purchase.loader import get_loader
from django_purchase.loader import Loader as DefaultLoader
from loader_tests.models import Loader as CustomLoader
from loader_tests.models import MyProduct

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
