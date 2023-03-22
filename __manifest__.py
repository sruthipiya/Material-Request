{
    'name': 'Material Request',
    'description': 'Meterial request',
    'sequence': 3,
    'installable': True,
    'application': True,
    'depends': ['base', 'hr', 'product', 'purchase', 'stock'],
    'data': ['security/security.xml', 'security/ir.model.access.csv', 'views/material_request.xml',
             'views/material_request_line.xml',
             'views/material_request_menu.xml']
}
