{
    'name': 'Ophthalmology',
    'summary': "Manage patients, appointments, prescriptions, and reports for eye clinic",
   'description': "This module is designed for ophthalmology clinics",
    'author': "benjarrari",
    'email': "benjarrariimane@gmail.com",
    'category': 'Medical',
    'version': '0.1',
    'depends': ['base', 'web','mail'], 
    'data': [
        'security/ir.model.access.csv',
       'views/menus.xml',
        'views/patient_views.xml',
        'views/appointment_views.xml',
        'views/test_report_views.xml',
        'views/prescription_views.xml',
        'views/vitals_views.xml',
        'views/dashboard_views.xml',
        'views/examination_view.xml',
        
    ],
    'assets': {
    'web.assets_backend': [
        'ophthalmology/static/src/js/dashboard.js',
    ],
  },

 
    'demo': [
        'demo/demo.xml',
    ],
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
 
}
