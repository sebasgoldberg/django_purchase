from django.db import models
from django_purchase import loader

class MyProduct(models.Model):
    pass

class Loader(loader.Loader):

    def get_product_model(self):
        return MyProduct
