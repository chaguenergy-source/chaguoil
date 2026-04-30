from django.urls import path

from . import views

urlpatterns=[
   
        path('staffs',views.staffs, name='staffs'),
        path('addStaff',views.addStaff, name='addStaff'),
        path('viewStaff',views.viewStaff, name='viewStaff'),
        path('permit',views.permit, name='permit'),
        path('payroll',views.payroll, name='payroll'),
        path('loans',views.LoansStaff, name='LoansStaff'),
        path('AddLoan',views.AddLoan, name='AddLoan'),

]