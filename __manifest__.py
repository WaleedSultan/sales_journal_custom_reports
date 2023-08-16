# -*- coding: utf-8 -*-
{
    'name': "sale_excel_report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,
    'license': 'LGPL-3',

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report_xlsx', 'sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_report_wizard.xml',

        'report/header_footer_layout.xml',
        'report/header_footer_layout.xml',
        'report/sales_customer_report.xml',
        'report/import_excel_report.xml',
        'report/journal_report.xml',
        'report/sales_crosscheck_return_report.xml',
        'report/sale_order_template_inherit.xml',
        'views/import_xlxs_report.xml',
        'views/journals_customer_pdf_wizard.xml',
        'views/views.xml',
        'views/sale_customer_pdf_wizard.xml',
        'views/import_sale_crosscheck_wizard_form.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
