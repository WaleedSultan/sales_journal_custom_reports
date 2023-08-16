from odoo import models, fields
import xlrd
import base64
from odoo.exceptions import ValidationError
import json


class SaleCrosscheckReport(models.TransientModel):
    _name = 'sale.crosscheck.wizard'

    excel_file = fields.Binary(string="File for Upload")

    def get_excel_data_for_sale_crosscheck(self):
        print("start")
        sale_orders_data = []
        binary_data = self.excel_file
        seen_ids =set()
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
                row_dict = {'so_name': row[0], 'total': row[11]}

                so_by_name = self.env['sale.order'].search([('name', '=', row_dict['so_name'])])

                if so_by_name:
                    json_form = json.loads(so_by_name.tax_totals_json)
                    if so_by_name.name not in seen_ids:
                        if json_form['amount_total'] == row_dict['total']:
                            print('satisfied')
                            seen_ids.add(so_by_name.name)
                        else:
                            print('Not Satisfied')
                            row_dict['status'] = 'Total amount not matched'
                            row_dict['date'] = so_by_name.date_order
                            seen_ids.add(so_by_name.name)
                            sale_orders_data.append(row_dict)

                elif not so_by_name and row_dict['so_name'] not in seen_ids:
                    print('Not Satisfied')
                    row_dict['status'] = 'Sale order not found'
                    row_dict['date'] = " "
                    seen_ids.add(row_dict['so_name'])
                    sale_orders_data.append(row_dict)
        else:
            raise ValidationError("TRY TO ENTER EXCEL FILE (.xlsx)!")

        print("end")
        data = {
            'not_updated_products': sale_orders_data
        }
        if sale_orders_data:
            return self.env.ref('sale_excel_report.sales_crosscheck_report_xlsx').report_action(self, data=data)


class ProductXlsx(models.AbstractModel):
    _name = 'report.sale_excel_report.sales_crosscheck_report_xls'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Report Sales Crosscheck Excel Wizard'

    def generate_xlsx_report(self, workbook, data, wizard):
        print("Here")
        sheetwt = workbook.add_worksheet('Sales Crosscheck Report')
        sheetwt.set_column('A:A', 15)
        sheetwt.set_column('B:B', 25)
        sheetwt.set_column('C:C', 25)
        bold = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'EDEEF2', 'border': True})
        row = 0
        col = 0

        sheetwt.write(row, col, 'Sale Order no', bold)
        sheetwt.write(row, col + 1, 'Status', bold)
        sheetwt.write(row, col + 2, 'Order Date', bold)
        row = 1

        for dict in data['not_updated_products']:
            sheetwt.write(row, 0, dict['so_name'])
            sheetwt.write(row, 1, dict['status'])
            sheetwt.write(row, 2, dict['date'])
            row += 1



