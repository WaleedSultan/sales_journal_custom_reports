# -*- coding: utf-8 -*-

from odoo import models, fields, api
import base64
import io
from datetime import datetime
from datetime import timedelta
from PIL import Image
from collections import defaultdict


class ExcelReportSale(models.TransientModel):
    _name = 'sale.excel.wizard'
    _description = 'Sale Excel Wizard'
    date = fields.Char()
    country = fields.Char()

    def get_excel_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {}
        }
        return self.env.ref('sale_excel_report.sale_report_xlsx').report_action(self, data=data)


class SaleXlsx(models.AbstractModel):
    _name = 'report.sale_excel_report.sale_report_xls'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Sale Excel Wizard'

    def generate_xlsx_report(self, workbook, data, wizard):
        all_tags = self.env['shopify.additional.tags'].search([('value', '=', str(wizard.date))])
        filtered_sale_orders = []
        for order in all_tags.order_id:
            filtered_order = order.filtered(lambda order: wizard.country in order.shopify_tag_ids.mapped('value'))
            if filtered_order:
                filtered_sale_orders.append(filtered_order)

        product_qty = defaultdict(int)
        for order in filtered_sale_orders:
            for line in order.order_line:
                product_qty[line.product_id] += line.product_uom_qty
        sheetwt = workbook.add_worksheet('Sale Excel Report')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'EDEEF2', 'border': True})
        row = 0
        col = 0

        sheetwt.write(row, col, 'Product Name', bold)
        sheetwt.write(row, col + 1, 'Variant Attributes', bold)
        sheetwt.write(row, col + 2, 'Sku', bold)
        sheetwt.write(row, col + 3, 'Quantity', bold)
        row = 1
        for product, qty in product_qty.items():
            attributes_list = []
            attributes = product.product_template_variant_value_ids
            for attribute in attributes:
                attributes_list.append(attribute.display_name)
            sheetwt.write(row, 0, product.name)
            sheetwt.write(row, 1, str(attributes_list) if len(attributes_list) else '')
            sheetwt.write(row, 2, product.default_code)
            sheetwt.write(row, 3, qty)
            row += 1
