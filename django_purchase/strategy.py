from pulp import *
from django.core.exceptions import ValidationError
import math

INFINITE = 9999999

class ModeloLinealNoResuelto(ValidationError):
    pass

class PurchasePlanner:

    def resolve_purchase(self, purchase_list):
        
        # Definimos el modelo
        model = LpProblem('Planificar estrategia de compra para lista %s' % purchase_list.id, LpMinimize)

        # Definimos el funcional
        total_cost = LpVariable("COSTO_TOTAL",0)

        # Creamos la función objetivo
        model += total_cost, "Costo total de la compra."

        # Definimos las variables
        
        vendor_cost = {}
        V_I_VP = {}
        I_VP = {}
        buy_to_vendor = {}
        items = {}
        vendors = {}
        vproducts = {}

        for item in purchase_list.get_items():

            items[item.id] = item

            for vproduct in item.product_uom.get_vendors_products():

                vendor = vproduct.vendor

                vproducts[vproduct.id] = vproduct

                if vendor.id not in vendors:

                    vendors[vendor.id] = vendor

                    vendor_cost[vendor.id] = LpVariable(
                        "COSTO_PROVEEDOR_%s" % vendor.id, 0)

                    buy_to_vendor[vendor.id] = LpVariable(
                        "COMPRAMOS_AL_PROVEEDOR_%s" % vendor.id, 0, 1, LpInteger)

                V_I_VP[vendor.id] = V_I_VP.get(
                    vendor.id, {})

                V_I_VP[vendor.id][item.id] = V_I_VP[vendor.id].get(
                    item.id, {})
                V_I_VP[vendor.id][item.id][vproduct.id] = \
                    LpVariable("CANTIDAD_PROD_%s_DEL_PROVEEDOR_%s_PARA_ITEM_%s" %
                        (vproduct.id, item.id, vendor.id), 0, None, LpInteger)
                
                I_VP[item.id] = {}
                I_VP[item.id][vproduct.id] = \
                    V_I_VP[vendor.id][item.id][vproduct.id]


        model += total_cost - lpSum([cost for vendor_id,cost in vendor_cost.items()]) == 0, \
            "El costo total es la suma de los costos por vendedor."

        for vendor_id, items_for_vendor in V_I_VP.items():
            vendor = vendors[vendor_id]
            model += vendor_cost[vendor_id] - lpSum(
                [quan*float(vproducts[vproduct_id].get_price())
                    for item_id, vproduct_for_item in items_for_vendor.items() \
                        for vproduct_id, quan in vproduct_for_item.items() ]) - \
                        float(vendors[vendor_id].get_min_delivery_price())*buy_to_vendor[vendor_id] == 0, \
                    "La suma de las cantidades por sus precios de los productos más el costo de envio, es igual al costo total del vendedor %s" % vendor_id

        for vendor_id, to_vendor in buy_to_vendor.items():
            model += vendor_cost[vendor_id] - to_vendor*INFINITE <= 0, \
                "Mecanismo para determinar al proveedor que le compramos"
        
        for item_id, vproducts_for_item in I_VP.items():
            item = items[item_id]
            model += float(item.quantity) - lpSum([quan*float(vproducts[vproduct_id].get_content())
                for vproduct_id, quan in vproducts_for_item.items()]) <= 0, \
                    "La cantidad a comprar debe ser mayor o igual a la cantidad solicitada"

        #model.writeLP("/tmp/agroeco.lp")

        # Redirige la salida a /dev/null
        model.setSolver()
        model.solver.msg = False

        model.solve()

        if model.status != LpStatusOptimal:
            raise ModeloLinealNoResuelto(_(u'No fue posible determinar cómo realizar la compra.'))


