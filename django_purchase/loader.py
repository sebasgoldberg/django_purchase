from django.conf import settings
import importlib
from . import custom_models

class Loader:

    def get_product_model(self):
        return custom_models.Product

    def get_partner_model(self):
        return custom_models.Partner

def get_loader():
    loader_name = getattr(settings, 'PURCHASE_LOADER', None)
    if loader_name is None:
        return Loader()
    components = loader_name.split('.')
    module_path = '.'.join(components[:-1])
    class_name = components[-1]
    module = importlib.import_module(module_path)
    loader_class = getattr(module, class_name)
    return loader_class()
