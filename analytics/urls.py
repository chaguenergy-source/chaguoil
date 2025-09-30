from django.urls import path

from . import views

urlpatterns=[
   
        path('analytics',views.analytics, name='analytics'),
        path('salesr',views.salesr, name='salesr'),
        path('getsaler',views.getsaler, name='getsaler'),
        path('evaluationr',views.evaluationr, name='evaluationr'),
        path('getEvaluation',views.getEvaluation, name='getEvaluation'),
        path('expensesr',views.expensesr, name='expensesr'),
        path('getExpenses',views.getExpenses, name='getExpenses'),
        path('homePageData',views.homePageData, name='homePageData'),


]