from django.urls import path

from . import views

urlpatterns=[
    path('confirmMail',views.confirmMail, name='confirmMail'),
    path('register',views.register, name='register'),
    # path('saveuserimg',views.saveuserimg, name='saveuserimg'),
    path('stations',views.stations, name='stations'), 

    path('',views.login, name='login'),
   
    path('fogotpwd',views.fogotpwd, name='fogotpwd'),
    path('confirmMailPwdFoggot',views.confirmMailPwdFoggot, name='confirmMailPwdFoggot'),
    path('passWordResset',views.passWordResset, name='passWordResset'),
    path('passWordResset',views.passWordResset, name='passWordResset'),
    path('changePwd',views.changePwd, name='changePwd'),
    path('langSet',views.langSet, name='langSet'),
    path('resetpwd',views.resetpwd, name='resetpwd'),
    path('userdash',views.userdash, name='userdash'),
    path('addstetion',views.addstetion, name='addstetion'),
    path('enterstation',views.enterstation, name='enterstation'),
   
    path('logout',views.logout, name='logout'),
    path('notify',views.notify, name='notify'),
    path('markreadNotify',views.markreadNotify, name='markreadNotify'),
    path('darkMode',views.darkMode, name='darkMode'),
    path('settings',views.settings, name='settings'),
    path('companyDetails',views.companyDetails, name='companyDetails'),
    path('upload_company_logo',views.upload_company_logo, name='upload_company_logo'),

 

]

