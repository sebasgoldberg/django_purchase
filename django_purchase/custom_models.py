from django.db import models

class AbstractProduct(models.Model):
    class Meta:
        abstract = True

class AbstractPartner(models.Model):
    class Meta:
        abstract = True

class Product(AbstractProduct):
    pass

class Partner(AbstractPartner):
    pass
