PURCHASE_LOADER setting
-----------------------
Example:
  
  PURCHASE_LOADER = 'loader_tests.models.Loader'

Loader class redefine django_purchase.loader.Loader default class.

Example usage:

  loader = get_loader()
  
  product_model = loader.get_product_model()

