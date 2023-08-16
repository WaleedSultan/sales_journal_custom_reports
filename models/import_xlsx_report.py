from odoo import models, fields
import xlrd
import base64
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class ImportExcelReport(models.TransientModel):
    _name = 'import.excel.wizard'

    excel_file = fields.Binary(string="File for Upload")

    def get_onHand_stock_valuation_difference(self):
        products_data = []
        binary_data = self.excel_file
        # First, decode the binary data
        decoded_data = base64.b64decode(binary_data)
        # Next, create a workbook object from the decoded data
        try:
            xlrd.open_workbook(file_contents=decoded_data)
            file = True
        except:
            file = False

        if file:
            workbook = xlrd.open_workbook(file_contents=decoded_data)
            # Select the first sheet of the workbook
            sheet = workbook.sheet_by_index(0)
            # Iterate over the rows in the sheet, starting from the second row
            for row_index in range(1, sheet.nrows):
                # Get the row data as a list
                row = sheet.row_values(row_index)
                # Create a dictionary from the row data
                row_dict = {'product_name': row[0], 'internal_reference': row[1], 'quantity': row[2]}

                product_by_code = self.env['product.product'].search(
                    [('default_code', '=', row_dict['internal_reference'])])

                product_by_name = self.env['product.product'].search(
                    [('name', '=', row_dict['product_name'])])

                location_check = False

                if product_by_code:
                    if product_by_code.stock_quant_ids:
                        for obj in product_by_code.stock_quant_ids:
                            loc_id = self.env.ref('stock.stock_location_stock').id
                            stock_valuation_objs = self.env['stock.valuation.layer'].search([('product_id', '=', product_by_code.id)])
                            svq = sum([obj.quantity for obj in stock_valuation_objs])
                            if obj.location_id.id == loc_id:
                                location_check = True
                                if obj.quantity != svq:
                                    if obj.quantity > svq:
                                        difference = obj.quantity + (-1 * svq)
                                        row_dict['quantity'] = difference
                                    elif obj.quantity < svq:
                                        difference = obj.quantity + (-1 * svq)
                                        row_dict['quantity'] = difference
                                else:
                                    row_dict['quantity'] = 0
                                break

                        if not location_check:
                            stock_valuation_objs = self.env['stock.valuation.layer'].search(
                                [('product_id', '=', product_by_code.id)])
                            svq = sum([obj.quantity for obj in stock_valuation_objs])
                            difference = 0 + (-1 * svq)
                            row_dict['quantity'] = difference
                    else:
                        stock_valuation_objs = self.env['stock.valuation.layer'].search(
                            [('product_id', '=', product_by_code.id)])
                        svq = sum([obj.quantity for obj in stock_valuation_objs])
                        difference = 0 + (-1 * svq)
                        row_dict['quantity'] = difference
                    products_data.append(row_dict)

                elif product_by_name:
                    if product_by_name[0].stock_quant_ids:
                        for obj in product_by_name[0].stock_quant_ids:
                            loc_id = self.env.ref('stock.stock_location_stock').id
                            stock_valuation_objs = self.env['stock.valuation.layer'].search(
                                [('product_id', '=', product_by_name[0].id)])
                            svq = sum([obj.quantity for obj in stock_valuation_objs])
                            if obj.location_id.id == loc_id:
                                location_check = True
                                if obj.quantity != svq:
                                    if obj.quantity > svq:
                                        difference = obj.quantity + (-1 * svq)
                                        row_dict['quantity'] = difference
                                    elif obj.quantity < svq:
                                        difference = obj.quantity + (-1 * svq)
                                        row_dict['quantity'] = difference
                                else:
                                    row_dict['quantity'] = 0
                                break

                        if not location_check:
                            stock_valuation_objs = self.env['stock.valuation.layer'].search(
                                [('product_id', '=', product_by_name[0].id)])
                            svq = sum([obj.quantity for obj in stock_valuation_objs])
                            difference = 0 + (-1 * svq)
                            row_dict['quantity'] = difference

                    else:
                        stock_valuation_objs = self.env['stock.valuation.layer'].search(
                            [('product_id', '=', product_by_code.id)])
                        svq = sum([obj.quantity for obj in stock_valuation_objs])
                        difference = 0 + (-1 * svq)
                        row_dict['quantity'] = difference
                    products_data.append(row_dict)

                    if len(product_by_name) != 1:
                        for prod in product_by_name[1:]:
                            products_data.append({
                                'product_name': prod.name,
                                'internal_reference': ' ',
                                'quantity': 'Duplicate Product'
                            })
                else:
                    print('Product does not exist')
        else:
            raise ValidationError("TRY TO ENTER EXCEL FILE!")

        print("end")
        data = {
            'not_updated_products': products_data,
            'title': 'Difference'
        }
        if products_data:
            return self.env.ref('sale_excel_report.product_report_xlsx').report_action(self, data=data)

    def update_onHand_stock_valuation_qty(self):
        print("start")
        products_data = []
        binary_data = self.excel_file
        # First, decode the binary data
        decoded_data = base64.b64decode(binary_data)
        # Next, create a workbook object from the decoded data
        try:
            xlrd.open_workbook(file_contents=decoded_data)
            file = True
        except:
            file = False

        if file:
            workbook = xlrd.open_workbook(file_contents=decoded_data)
            # Select the first sheet of the workbook
            sheet = workbook.sheet_by_index(0)
            # Iterate over the rows in the sheet, starting from the second row
            i = 0
            for row_index in range(1, sheet.nrows):
                # Get the row data as a list
                row = sheet.row_values(row_index)
                # Create a dictionary from the row data
                row_dict = {'product_name': row[0], 'internal_reference': row[1], 'quantity': row[2]}

                product_by_code = self.env['product.product'].search(
                    [('default_code', '=', row_dict['internal_reference'])])

                product_by_name = self.env['product.product'].search(
                    [('name', '=', row_dict['product_name'])])

                location_check = False

                if product_by_code:
                    loc_id = self.env.ref('stock.stock_location_stock').id
                    if product_by_code.stock_quant_ids:
                        for obj in product_by_code.stock_quant_ids:
                            if obj.location_id.id == loc_id:
                                location_check = True
                                obj.inventory_quantity = row_dict['quantity']
                                obj.action_apply_inventory()
                                break

                        if not location_check:
                            self.env['stock.quant'].create({
                                'product_id': product_by_code.id,
                                'inventory_quantity': row_dict['quantity'],
                                'location_id': loc_id
                            }).action_apply_inventory()
                    else:
                        self.env['stock.quant'].create({
                            'product_id': product_by_code.id,
                            'inventory_quantity': row_dict['quantity'],
                            'location_id': loc_id
                        }).action_apply_inventory()

                elif product_by_name:
                    loc_id = self.env.ref('stock.stock_location_stock').id
                    if product_by_name[0].stock_quant_ids:
                        for obj in product_by_name[0].stock_quant_ids:
                            if obj.location_id.id == loc_id:
                                location_check = True
                                obj.inventory_quantity = row_dict['quantity']
                                obj.action_apply_inventory()
                                break
                        if not location_check:
                            self.env['stock.quant'].create({
                                'product_id': product_by_name[0].id,
                                'inventory_quantity': row_dict['quantity'],
                                'location_id': loc_id
                            }).action_apply_inventory()
                    else:
                        self.env['stock.quant'].create({
                            'product_id': product_by_name[0].id,
                            'inventory_quantity': row_dict['quantity'],
                            'location_id': loc_id
                        }).action_apply_inventory()

                else:
                    print('Product does not exist')
                    products_data.append(row_dict)

                i +=1
# <<<<<<< HEAD
                print(i)
# =======
                _logger.info("Updated Records are %s"%(str(i)))
# >>>>>>> e07f80bdee894ec2ca60fc4ab7937f1b20a9a51e
        else:
            raise ValidationError("TRY TO ENTER EXCEL FILE!")

        print("end")
        data = {
            'not_updated_products': products_data,
            'title': 'stock updation'
        }
        if products_data:
            return self.env.ref('sale_excel_report.product_report_xlsx').report_action(self, data=data)

    def update_onHand_qty(self):
        print("start")
        products_data = []
        binary_data = self.excel_file
        # First, decode the binary data
        decoded_data = base64.b64decode(binary_data)
        # Next, create a workbook object from the decoded data
        try:
            xlrd.open_workbook(file_contents=decoded_data)
            file = True
        except:
            file = False

        if file:
            workbook = xlrd.open_workbook(file_contents=decoded_data)
            # Select the first sheet of the workbook
            sheet = workbook.sheet_by_index(0)
            # Iterate over the rows in the sheet, starting from the second row
            for row_index in range(1, sheet.nrows):
                # Get the row data as a list
                row = sheet.row_values(row_index)
                # Create a dictionary from the row data
                row_dict = {'product_name': row[0], 'internal_reference': row[1], 'quantity': row[2]}

                product_by_code = self.env['product.product'].search(
                    [('default_code', '=', row_dict['internal_reference'])])
                product_by_name = self.env['product.product'].search(
                    [('name', '=', row_dict['product_name'])])

                if product_by_code:
                    if product_by_code.stock_quant_ids:
                        for obj in product_by_code.stock_quant_ids:
                            loc_id = self.env.ref('stock.stock_location_stock').id
                            if obj.location_id.id == loc_id:
                                obj.quantity = row_dict['quantity']
                    # else:
                    #     self.env['stock.quant'].create({
                    #         'product_id': product_by_code.id,
                    #         'inventory_quantity': row_dict['quantity'],
                    #         'location_id': loc_id
                    #     }).action_apply_inventory()

                elif product_by_name:
                    if product_by_name[0].stock_quant_ids:
                        for obj in product_by_name[0].stock_quant_ids:
                            loc_id = self.env.ref('stock.stock_location_stock').id
                            if obj.location_id.id == loc_id:
                                obj.quantity = row_dict['quantity']

                else:
                    print('Product does not exist')
                    products_data.append(row_dict)
        else:
            raise ValidationError("TRY TO ENTER EXCEL FILE!")

        print("end")
        data = {
            'not_updated_products': products_data,
            'title': 'update onHand'
        }
        if products_data:
            return self.env.ref('sale_excel_report.product_report_xlsx').report_action(self, data=data)


class ProductXlsx(models.AbstractModel):
    _name = 'report.sale_excel_report.product_report_xls'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Product Excel Wizard'

    def generate_xlsx_report(self, workbook, data, wizard):
        print("Here")
        data['not_updated_products']
        sheetwt = workbook.add_worksheet('Sale Excel Report')
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'EDEEF2', 'border': True})
        row = 0
        col = 0

        if data['title'] == 'Difference':
            sheetwt.write(row, col, 'Products', bold)
            sheetwt.write(row, col + 1, 'Internal Reference', bold)
            sheetwt.write(row, col + 2, 'Difference', bold)
            row = 1

            for dict in data['not_updated_products']:
                sheetwt.write(row, 0, dict['product_name'])
                sheetwt.write(row, 1, dict['internal_reference'])
                sheetwt.write(row, 2, dict['quantity'])
                row += 1
        else:
            sheetwt.write(row, col, 'Products', bold)
            sheetwt.write(row, col + 1, 'Internal Reference', bold)
            sheetwt.write(row, col + 2, 'Quantity', bold)
            # sheetwt.write(row, col + 3, 'Unit of Measurement', bold)
            row = 1

            for dict in data['not_updated_products']:
                sheetwt.write(row, 0, dict['product_name'])
                sheetwt.write(row, 1, dict['internal_reference'])
                sheetwt.write(row, 2, dict['quantity'])
                # sheetwt.write(row, col + 3, dict.get('unit_of_measurement'))
                row += 1
