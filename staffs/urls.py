from django.urls import path

from . import views

urlpatterns=[
   
        path('staffs',views.staffs, name='staffs'),
        path('addStaff',views.addStaff, name='addStaff'),
        path('viewStaff',views.viewStaff, name='viewStaff'),
        path('permit',views.permit, name='permit'),

]