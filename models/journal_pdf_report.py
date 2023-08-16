from odoo import models, fields
import json


class PdfReportJournal(models.TransientModel):
    _name = 'journal.pdf.wizard'

    journals_ids = fields.Many2many('account.journal')
    from_date = fields.Date(string='From date')
    to_date = fields.Date(string='To date')

    def get_pdf_report(self):
        journal_names = []
        all_journals_data = []
        for journal_id in self.journals_ids:
            journal_names.append(journal_id.name)
            report_data = []
            all_payments = self.env['account.payment'].search([('journal_id', '=', journal_id.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date)])
            for val in all_payments:
                for var in val.reconciled_invoice_ids:
                    if var.name.startswith('R'):
                        break
                    else:
                        if var.ref:
                            sale_order = self.env['sale.order'].search([('name', '=', var.ref)])
                            report_data.append(
                                {
                                    'customer_name': val.partner_id.name,
                                    'sale_order_date': sale_order.date_order,
                                    'sale_order_number': sale_order.name,
                                    'sale_order_amount': json.loads(sale_order.tax_totals_json)[
                                        'amount_total'] if sale_order.tax_totals_json else "",
                                    'invoice_number': var.name,
                                    'invoice_amount': json.loads(var.tax_totals_json)[
                                        'amount_total'] if var.tax_totals_json else "",
                                    'payment_status': var.payment_state,
                                    'payment_name': val.name,
                                    'payment_amount': val.amount_total
                                }
                            )
                        else:
                            report_data.append(
                                {
                                    'customer_name': val.partner_id.name,
                                    'sale_order_date': "",
                                    'sale_order_number': "",
                                    'sale_order_amount': "",
                                    'invoice_number': var.name,
                                    'invoice_amount': json.loads(var.tax_totals_json)[
                                        'amount_total'] if var.tax_totals_json else "",
                                    'payment_status': var.payment_state,
                                    'payment_name': val.name,
                                    'payment_amount': val.amount_total
                                }
                            )
            all_journals_data.append(report_data)

        data = {
            'report_data': all_journals_data,
            'journal_names': journal_names
        }

        return self.env.ref('sale_excel_report.journal_report_id').report_action(self, data=data)
