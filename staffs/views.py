from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from account.models import UserExtend,PhoneMailConfirm,Interprise,InterprisePermissions,PaymentAkaunts,staff_akaunt_permissions
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.models import F
from django.core import serializers
from django.db.models import Q
# from datetime import datetime
from django.utils import timezone
timezone.now()

from datetime import date,timedelta,timezone

import requests
#Session model stores the session data
from django.contrib.sessions.models import Session

import time  
import pytz
import datetime
import re
from django.db.models import Sum
import random 
import os


from account.todos import Todos,confirmMailF
def todoFunct(request):
  usr = Todos(request)

  return usr.todoF()


@login_required(login_url='login')
def addStaff(request):
  if request.method == "POST":
    try:
      f_name = request.POST.get('f_name')
      l_name = request.POST.get('l_name')
      phone = request.POST.get('phone')
      email = request.POST.get('email')
      cheo = request.POST.get('cheo')
      city = request.POST.get('city')
      address = request.POST.get('address')
      ceo = int(request.POST.get('ceo'))
      intp = int(request.POST.get('entp',0))
      usrd = int(request.POST.get('user',0))
      edit = int(request.POST.get('edit',0))
      
      data = {
        'success':True,
          'msg_swa':'Stafu ameongezwa kikamilifu',
          'msg_eng':'Staff added successfully'
      }

      todo = todoFunct(request)
      shell = todo['shell']
      general = todo['general']
      

      useri = todo['useri']
      kampuni =  useri.company
      if useri.admin and (ceo or not general):
        usr = UserExtend.objects.filter(user__email__icontains=email)
        if not usr.exists() or (usr.exists() and edit):
                usrr = None
                if edit:
                    usrr = UserExtend.objects.get(pk=usrd,company=kampuni.id)
                    user = usrr.user
                    user.first_name = f_name
                    user.last_name = l_name
                    user.email = email
                    user.username = email
                    user.save()

                 
                    usrr.region = city
                    usrr.address = address
                    usrr.phone = phone
                    usrr.country = 'Tanzania'
                    usrr.postal = useri.postal
                    usrr.cheo = cheo

                    pmq = InterprisePermissions.objects.filter(user=usrr,Interprise__company=kampuni.id)
                    pm = pmq.first()

                    usrr.save()
                    
                    data = {
                        'success':True,
                          'msg_swa':'Stafu ameongezwa kikamilifu',
                          'msg_eng':'Staff added successfully',
                          'id':pm.id
                      }
                    return JsonResponse(data)
                user = User.objects.create_user(email=email,username=email,first_name=f_name, 
                                                last_name=l_name, password='nnPQWWEAdauiias' )
                ext = UserExtend()
                # user.save()
                ext.regstatue = 1
                ext.user = user
                ext.company = kampuni 
                ext.region = city
                ext.address = address
                ext.phone = phone
                ext.country = 'Tanzania'
                ext.postal = useri.postal
                ext.ceo = ceo
                ext.hakikiwa = ceo
 
                ext.cheo = cheo
                ext.pwdResets = ceo

                # ext.langSet = lang

                ext.save()


                pm = None
                if ceo:
                  intpr = Interprise.objects.filter(owner=useri)
                  
                  for i in intpr:
                      pm = InterprisePermissions()
                      pm.Interprise = i
                      pm.user = ext
                      pm.cheo = cheo
                      pm.Allow = True
                      pm.save()

                      paya = PaymentAkaunts.objects.filter(Interprise=i.id)
                      for pya in paya:
                        payAp = staff_akaunt_permissions()
                        payAp.Akaunt = pya
                        payAp.user = ext
                        payAp.Allow = True
                        
                        payAp.save()
                  hostname = os.environ.get("HOST", default="cfspump.com")
                 
                  cfm = {
                      'num':0,
                       'user':{
                                'useri':ext.id,
                                 'host':hostname
                               },

                        'to':email       
                        
                     
                  } 

                  confirmMailF(cfm)     
                else:
                      
                    pm = InterprisePermissions()
                    pm.Interprise = shell
                    pm.user = ext
                    pm.cheo = cheo
                    
                    pm.save()    

                    
                data = {
                    'success':True,
                      'msg_swa':'Stafu ameongezwa kikamilifu',
                      'msg_eng':'Staff added successfully',
                      'id':pm.id
                  }


                   
        else:
          data={
              'success':False,
                'msg_eng':'Member has already added',
                'msg_swa':'Mtumiaji tayari ameshahifadhiwa'
          }
      else:
        data = {
          'success':False,
              'msg_eng':'You have no permissions to add User',
              'msg_swa':'Hauna ruhusa ya kuongeza Mtumiaji'
        }

      return JsonResponse(data)

    except:
      data = {
            'success':False,
            'msg_eng':'The action was not successfully due to error try again correctly',
            'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi'
         }   
      return JsonResponse(data)

@login_required(login_url='login')
def staffs(request):
  try:
    todo = todoFunct(request)
    general = todo['general']
    # User.objects.filter(pk__gt=1).delete()
    shell = todo['shell']
    useri = todo['useri']
    staff = InterprisePermissions.objects.filter(Interprise__company=useri.company)

    if not useri.admin:
      staff = staff.filter(Interprise=shell.id)

    todo.update({
       'staffs':staff.distinct('user')
    })

    return render(request, 'staff.html',todo)
  except:
    return render(request, 'pagenotFound.html')
  
@login_required(login_url='login')
def permit(request):
  try:
     if request.method == 'POST':
        usr = int(request.POST.get('user'))
        check = int(request.POST.get('check'))
        ceo = int(request.POST.get('ceo'))
        allow = int(request.POST.get('allow'))
        incharge = int(request.POST.get('incharge'))
        manager = int(request.POST.get('manager'))
        op = int(request.POST.get('op'))
        sup = int(request.POST.get('sup'))
        pu = int(request.POST.get('pu'))
        exp = int(request.POST.get('exp',0))
        cust = int(request.POST.get('cust',0))
        todo = todoFunct(request)
        useri = todo['useri']
        kampuni = todo['kampuni']
        shell = todo['shell']
        data = {
           'success':True,
           'msg_swa':'Ruhusa kwa mhusika imebadirishwa kikamilifu',
           'msg_eng':'Permission changed successfully',
        }

        if useri.admin:
            perm = InterprisePermissions.objects.get(pk=usr,Interprise__company=kampuni.id)
            userr = perm.user
            if not userr.hakikiwa and allow and check:
                  hostname = os.environ.get("HOST", default="cfspump.com")
                 
                  cfm = {
                      'num':0,
                       'user':{
                                'useri':userr.id,
                                 'host':hostname
                               },

                        'to':userr.user.email       
                        
                     
                  } 

                  confirmMailF(cfm)
                  userr.staff =  True 
                  userr.pwdResets = True
                  userr.save()
                  

            if allow:
              perm.Allow =  check 
              perm.save()

            if incharge:
              if shell == perm.Interprise:
                perm.pumpIncharge =  check 
                perm.save()
             
              if shell != perm.Interprise and check:
                    pm = InterprisePermissions()
                    pm.Interprise = shell
                    pm.user = userr
                    pm.cheo = perm.cheo
                    pm.pumpIncharge =  check
                    pm.save()  



            if manager:
              perm.fullcontrol =  check 
              perm.save()
            
            if ceo:
              userr.ceo =  check 
              userr.save()

            if op:
              userr.op =  check 
              userr.save()

            if sup:
              userr.tankSup =  check 
              userr.save()

            if pu:
              userr.pu =  check 
              userr.save()

            if exp:
              userr.exp =  check 
              userr.save()  

            if cust:
              userr.cust =  check 
              userr.save()

        else:
           data = {
              'success':False,
              'msg_eng':'You have no permissions to add User',
              'msg_swa':'Hauna ruhusa ya kuongeza Mtumiaji'
           }     
        return JsonResponse(data) 
        
  except:
     data = {
         'msg_eng':'The action was not successfully due to error try again correctly',
         'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi'

     }

     return JsonResponse(data)
     

@login_required(login_url='login')
def viewStaff(request):
  try:
    
    st = int(request.GET.get('usr',0))
    todo = todoFunct(request)
    # User.objects.filter(pk__gt=1).delete()
    if todo['useri'].admin:
          kampuni = todo['kampuni']  
          general = todo['general']
          shell = todo['shell']
          staff =  InterprisePermissions.objects.get(pk=st,Interprise__company=kampuni.id)
          usr = staff.user
          if not general:
              belongs = InterprisePermissions.objects.filter(Interprise=shell.id,user=usr)
              if staff.Interprise != shell and  belongs.exists():
                  staff = InterprisePermissions.objects.get(Interprise=shell.id,user=usr)

          todo.update({
            's':staff
          })
          return render(request, 'staffView.html',todo)
    else:
       return render(request, 'pagenotFound.html')
  except:
    return render(request, 'pagenotFound.html')
  