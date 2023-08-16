from odoo import models, fields, api
import json
from datetime import date
from datetime import timedelta
import dateutil.parser
# import dateutil.parser
# import dateutil.parser
# import dateutil.parser
# import dateutil.parser


class ExcelReportSale(models.TransientModel):
    _name = 'sale.pdf.wizard'

    customer_id = fields.Many2one('res.partner')
    # customer_id = fields.Many2one('res.partner')
    from_date = fields.Date(string='From date')
    to_date = fields.Date(string='To date')

    def get_pdf_report(self):
        report_data = []
        balance = 0
        amount_due = 0

        sale_order_data = self.env['sale.order'].search([('partner_id', '=', self.customer_id.id)])
        # For finding previous balance
        for val in sale_order_data:
            for x in val.invoice_ids:
                if x.payment_state == 'not_paid':
                    if val.date_order:
                        if dateutil.parser.parse(str(val.date_order)).date() < self.from_date:
                            balance += json.loads(x.tax_totals_json)['amount_total']

        amount_due += balance
        y = balance

        for val in sale_order_data[::-1]:
            for x in val.invoice_ids:
                if x.payment_state == 'not_paid':
                    if val.date_order:
                        if self.from_date <= dateutil.parser.parse(str(val.date_order)).date() and self.to_date >= dateutil.parser.parse(str(val.date_order)).date():
                            y += json.loads(x.tax_totals_json)['amount_total']
                            report_data.append(
                                {
                                    'sale_order_number': val.name,
                                    'date': dateutil.parser.parse(str(val.date_order)).date(),
                                    'invoice_number': x.name,
                                    'amount': json.loads(x.tax_totals_json)['amount_total'],
                                    'balance': y
                                }
                            )
                            amount_due += json.loads(x.tax_totals_json)['amount_total']

        previous_date = self.from_date - timedelta(days=1)
        data = {
            'report_data': report_data,
            'forward_balance': balance,
            'forward_balance_date': previous_date,
            'amount_due': amount_due,
            'from_date': self.from_date,
            'to_date': self.to_date
        }
        print(report_data)

        return self.env.ref('sale_excel_report.sales_customer_report_id').report_action(self, data=data)





