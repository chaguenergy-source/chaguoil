from django.urls import path

from . import views

urlpatterns=[
   
        path('payaccounts',views.payaccounts, name='payaccounts'),
        path('addAkaunt',views.addAkaunt, name='addAkaunt'),
        path('editAkaunt',views.editAkaunt, name='editAkaunt'),
        path('kuwekapesa',views.kuwekapesa, name='kuwekapesa'),
        path('kutoaPesa',views.kutoaPesa, name='kutoaPesa'),
        path('addExpense',views.addExpense, name='addExpense'),
        path('deposit',views.deposit, name='deposit'),
        path('withdraw',views.withdraw, name='withdraw'),
        path('pdcBills',views.pdcBills, name='pdcBills'),
        path('addPBill',views.addPBill, name='addPBill'),
        path('pdcBillsView',views.pdcBillsView, name='pdcBillsView'),
        path('expenseRecords',views.expenseRecords, name='expenseRecords'),
        path('getExpData',views.getExpData, name='getExpData'),

]