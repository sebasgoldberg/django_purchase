from pulp import *
from django.core.exceptions import ValidationError

class ModeloLinealNoResuelto(ValidationError):
    pass

class PurchasePlanner:

    def create_purchase_orders(self, purchase_list):
        
        # Definimos el modelo
        model = LpProblem('Planificar estrategia de compra para lista %s' % purchase_list.id, LpMinimize)

        # Definimos el funcional
        total_cost = LpVariable("COSTO_TOTAL",0)

        # Creamos la función objetivo
        model += total_cost, "Costo total de la compra."

        # Definimos las variables
        
        vendor_cost = {}
        item_quan_for_vendor = {
            'VI': {}
            'IV': {}
            }
        buy_to_vendor = {}
        items = {}
        vendors = {}

        for item in purchase_list.get_items():

            items[item.id] = item

            for vendor in item.product_uom.get_vendors():

                if vendor.id not in vendors:

                    vendors[vendor.id] = vendor

                    vendor_cost[vendor.id] = LpVariable(
                        "COSTO_PROVEEDOR_%s" % vendor.id, 0)

                    buy_to_vendor[vendor.id] = LpVariable(
                        "COMPRAMOS_AL_PROVEEDOR_%s" % vendor.id, 0, 1, LpInteger)

                item_quan_for_vendor['VI'][vendor.id] = item_quan_for_vendor.get(
                    vendor.id, {})

                item_quan_for_vendor['IV'][item.id][vendor.id] = \
                    item_quan_for_vendor['VI'][vendor.id][item.id] = \
                    LpVariable("CANTIDAD_ITEM_%s_AL_PROVEEDOR_%s" %
                        (item.id, vendor.id), 0, None, LpInteger)
                

        model += total_cost - lpSum([cost for vendor_id,cost in vendor_cost.items()]) == 0, \
            "El costo total es la suma de los costos por vendedor."

        for vendor_id, items_for_vendor in item_quan_for_vendor['VI']:
            vendor = vendors[vendor_id]
            model += vendor_cost[vendor_id] - lpSum(
                [quan*vendor.get_price_for_product(items[item_id].product_uom)
                    for item_id,quan in items_for_vendor.items()]) - \
                        vendors[vendor_id].get_delivery_price()*buy_to_vendor[vendor_id] == 0, \
                    "La suma de las cantidades por sus precios de los productos más el costo de envio, es igual al costo total del vendedor %s" % vendor_id

        for vendor_id, to_vendor in buy_to_vendor.items():
            model += vendor_cost[vendor_id] - to_vendor*INFINITO <= 0,
                "Mecanismo para determinar al proveedor que le compramos"
        
        for item_id, vendors_for_item in item_quan_for_vendor['IV']:
            item = items[item_id]
            model += item.quantity - lpSum([quan*vendor.get_content_for_product(item.product_uom)
                for vendor_id, quan in vendors_for_item.items()]) <= 0,
                    "La cantidad a comprar debe ser mayor o igual a la cantidad solicitada"

        modelo.writeLP("/tmp/agroeco.lp")

        # Redirige la salida a /dev/null
        modelo.setSolver()
        modelo.solver.msg = False

        modelo.solve()

        if not self.is_modelo_resuelto():
            raise ModeloLinealNoResuelto(_(u'No fue posible determinar cómo realizar la compra.'))


