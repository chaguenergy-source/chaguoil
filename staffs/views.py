from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from account.models import UserExtend,PhoneMailConfirm,Interprise,InterprisePermissions,PaymentAkaunts, exptaxGroup, matumizi, rekodiMatumizi,staff_akaunt_permissions, StaffLoan
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
import calendar
from decimal import Decimal, InvalidOperation
import re
from django.db.models import Sum
import random 
import os
import traceback

from account.todos import Todos,confirmMailF
def todoFunct(request):
  usr = Todos(request)

  return usr.todoF()


def _add_months(base_date, months):
  total_month = base_date.month - 1 + months
  target_year = base_date.year + total_month // 12
  target_month = total_month % 12 + 1
  target_day = min(base_date.day, calendar.monthrange(target_year, target_month)[1])
  return date(target_year, target_month, target_day)


def _add_years(base_date, years):
  try:
    return base_date.replace(year=base_date.year + years)
  except ValueError:
    return base_date.replace(year=base_date.year + years, month=2, day=28)


def _get_payroll_schedule(pay_item):
  if not pay_item.last_paid:
    return None, None, 'not_set'

  duration = pay_item.duration or 1

  if pay_item.daily:
    next_payment_date = pay_item.last_paid + timedelta(days=duration)
  elif pay_item.weekly:
    next_payment_date = pay_item.last_paid + timedelta(weeks=duration)
  elif pay_item.yearly:
    next_payment_date = _add_years(pay_item.last_paid, duration)
  else:
    next_payment_date = _add_months(pay_item.last_paid, duration)

  days_remaining = (next_payment_date - date.today()).days

  if days_remaining < 0:
    payment_status = 'overdue'
  elif days_remaining == 0:
    payment_status = 'due_today'
  else:
    payment_status = 'pending'

  return next_payment_date, days_remaining, payment_status


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
      intp = int(request.POST.get('kituo',0))
      usrd = int(request.POST.get('user',0))
      edit = int(request.POST.get('edit',0))
      male = int(request.POST.get('male',0))
      female = int(request.POST.get('female',0))
      isPermanent = int(request.POST.get('isPermanent',0))
      tin  = request.POST.get('tin','')
      nin  = request.POST.get('nin','')
      kibarua = int(request.POST.get('kibarua',0))
      parttime = int(request.POST.get('parttime',0))    
      tax_group = int(request.POST.get('tax_group',0))

      basic_salary = float(request.POST.get('basic_salary',0))
      salary_payment_source = request.POST.get('salary_payment_source','headOffice')
      salary_station = int(request.POST.get('salary_station',0))
      salary_payment_period = request.POST.get('salary_payment_period','month')
      salary_last_paid_date = request.POST.get('salary_last_paid_date','')
      todo = todoFunct(request)
      shell = todo['shell']
      general = todo['general']
      useri = todo['useri']
      kampuni =  useri.company    

      

      data = {
        'success':True,
          'msg_swa':'Stafu ameongezwa kikamilifu',
          'msg_eng':'Staff added successfully'
      }


      


      if not useri.admin:
          data = {
          'success':False,
              'msg_eng':'You have no permissions to add User',
              'msg_swa':'Hauna ruhusa ya kuongeza Mtumiaji'
        }
          return JsonResponse(data)
      
      usr = UserExtend.objects.filter(Q(user__email__icontains=email)|Q(tin__icontains=tin)|Q(phone__icontains=phone),company=kampuni.id).exclude(user__pk=usrd)
      if  usr.filter(user__email__icontains=email).exists():
          data = {
              'success':False,
              'msg_eng':'Member email  already exists',
              'msg_swa':' Barua pepe ya mtumiaji tayari ipo'
              }
          return JsonResponse(data)   
      
      if usr.filter(tin__icontains=tin).exists() and tin != '':
          data = {
              'success':False,
              'msg_eng':'Member TIN  already exists',
              'msg_swa':' Namba ya utambulisho ya mtumiaji tayari ipo'
              }
          return JsonResponse(data) 
      
      if usr.filter(nin__icontains=nin).exists() and nin != '':
          data = {
              'success':False,
              'msg_eng':'Member NIN  already exists',
              'msg_swa':' Namba ya utambulisho ya mtumiaji tayari ipo'
              }
          return JsonResponse(data) 
      
      if usr.filter(phone__icontains=phone).exists() and phone != '':
          data = {
              'success':False,
              'msg_eng':'Member phone number  already exists',
              'msg_swa':' Namba ya simu ya mtumiaji tayari ipo'
              }
          return JsonResponse(data) 
      
      ext = UserExtend()
      salary = matumizi()
      pm = None
      if edit:
          ext = UserExtend.objects.get(pk=usrd,company=kampuni.id)
          user = ext.user
          user.first_name = f_name
          user.last_name = l_name
          user.email = email
          user.username = email
          user.save()


          pmq = InterprisePermissions.objects.filter(user=ext,Interprise__company=kampuni.id)
          pm = pmq.first()

          ext.save()
          
          staff_salary = matumizi.objects.filter(Q(heo_pay=ext)|Q(sta_pay__user=ext),compani=kampuni.id)
          salary = staff_salary.first() if staff_salary.exists() else salary
          staff_salary.update(weekly=False,monthly=False,daily=False) 
         
      else:

        user = User.objects.create_user(email=email,username=email,first_name=f_name, 
                                        last_name=l_name, password='nnPQWWEAdauiias' )
       
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
      ext.labor = kibarua
      ext.party_time = parttime
      ext.male = male
      ext.female = female
      ext.cheo = cheo
      ext.pwdResets = ceo
      ext.permanent = isPermanent
      # ext.langSet = lang
      ext.tin = tin
      ext.nin = nin
      ext.save()


      if ceo:
        intpr = Interprise.objects.filter(owner=useri)
        
        for i in intpr:
            if not InterprisePermissions.objects.filter(user=ext,Interprise=i).exists():
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
          stationi = Interprise.objects.get(company=kampuni.id,pk=intp)
          if not InterprisePermissions.objects.filter(user=ext,Interprise=stationi).exists():  
            pm = InterprisePermissions()
            pm.Interprise = stationi
            pm.user = ext
            pm.cheo = cheo
            
            pm.save()   
      
      pay_station = Interprise.objects.get(pk=salary_station,company=kampuni.id) if salary_payment_source == 'station' else None
      stf_station_perm = pm
      if pay_station is not None:
          station_staff = InterprisePermissions.objects.filter(Interprise=pay_station.id,user=ext.id)
         
          if not station_staff.exists():
              stf_station_perm = InterprisePermissions()
              stf_station_perm.Interprise = pay_station
              stf_station_perm.user = ext
              stf_station_perm.cheo = cheo
              stf_station_perm.save()
          else:
              stf_station_perm = station_staff.first()    
              
           

        
      has_salary = parttime or isPermanent
      tax = None
      if tax_group:
         taxi = exptaxGroup.objects.filter(pk=tax_group,company=kampuni.id)
         tax = taxi.first() if taxi.exists() else None

      salary.heo_pay = ext if salary_payment_source == 'headOffice' and has_salary else None
      salary.sta_pay = stf_station_perm if salary_payment_source == 'station' and has_salary else None
      salary.amount = basic_salary    
      salary.last_paid = salary_last_paid_date if salary_last_paid_date and has_salary else  None
      salary.paye = has_salary
      salary.Isactive = has_salary
      salary.duration = 1
      salary.monthly = salary_payment_period == 'month'
      salary.weekly = salary_payment_period == 'week'
      salary.daily = salary_payment_period == 'day'
      salary.taxGroup = tax
      salary.compani = kampuni
      salary.save()

      matumRec=rekodiMatumizi.objects.filter(staff=ext,Interprise__company=kampuni.id,tax_group__isnull=True)
      matumRec = matumRec.filter(Q(matumizi__manunuzi=False)|Q(matumizi__mafuta=False)).update(tax_group=tax)

      # allRec = rekodiMatumizi.objects.filter(staff=ext,Interprise__company=kampuni.id)
      # for rc in allRec:
      #     rekodiMatumizi.objects.filter(pk=rc.id).update(tax_group=rc.matumizi.taxGroup)
      

      if not has_salary:
          salary.delete()
      
      data = {
          'success':True,
            'msg_swa':'Stafu ameongezwa kikamilifu',
            'msg_eng':'Staff added successfully',
            'id':pm.id if pm else 0
        }
      
     
        
      return JsonResponse(data)

    except Exception as err:
      print(err)
      traceback.print_exc()
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
       'staffs':staff.distinct('user'),
       'staffTab':True
    })

    return render(request, 'staff.html',todo)
  except:
    traceback.print_exc()
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
        dsup = int(request.POST.get('dsup',0))
        isActive = int(request.POST.get('isActive',0))
        payee = int(request.POST.get('payee',0))
        fn = int(request.POST.get('fn',0))
        loan = int(request.POST.get('loan',0))
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
            has_once_allowed = InterprisePermissions.objects.filter(user=userr.id,default=True)

            if not userr.hakikiwa and allow and check and not has_once_allowed.exists():
                  
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
            permited = InterprisePermissions.objects.filter(user=userr.id,Interprise=shell.id)
            if permited.exists():
               perm = permited.last()      
            else:
                  perm = InterprisePermissions()
                  perm.Interprise = shell
                  perm.user = userr
                  perm.cheo = perm.cheo
                  perm.save() 
                  

            
            if allow:
              perm.Allow =  check 
              perm.save()

            if incharge:
              if shell == perm.Interprise:
                perm.pumpIncharge =  check 
                perm.save()
             

            if manager:
              perm.fullcontrol =  check 
              perm.save()
            
            if ceo:
              userr.ceo =  check 
              userr.save()

            if op:
              userr.op =  check 
              userr.save()

            if dsup:
              userr.acc_supv =  check 
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

            if isActive:
              perm.isActive =  check 
              perm.save()

            if payee:
              userr.payee =  check 
              userr.save()  

            if fn:
              userr.finance =  check 
              userr.save()  
            if loan:
              userr.kopesheka =  check 
              userr.save()  

        else:
           data = {
              'success':False,
              'msg_eng':'You have no permissions to add User',
              'msg_swa':'Hauna ruhusa ya kuongeza Mtumiaji'
           }     
        return JsonResponse(data) 
        
  except Exception as err :
     print(err)
     data = {
         'msg_eng':'The action was not successfully due to error try again correctly',
         'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi'

     }

     return JsonResponse(data)
     

@login_required(login_url='login')
def payroll(request):
   try:
      todo = todoFunct(request)
      general = todo['general']
      kampuni = todo['kampuni']  
      general = todo['general']
      shell = todo['shell']
      useri = todo['useri']

      payroll = matumizi.objects.filter(paye=True, compani=kampuni.id).distinct('pk')

      if not general:
          payroll = payroll.filter(sta_pay__Interprise=shell.id)

      if not (useri.admin or useri.payee):
          payroll = None
      elif payroll is not None:
          payroll = list(payroll.select_related('sta_pay__user__user', 'heo_pay__user'))

          for pay_item in payroll:
              next_payment_date, days_remaining, payment_status = _get_payroll_schedule(pay_item)
              pay_item.next_payment_date = next_payment_date
              pay_item.days_remaining = days_remaining
              pay_item.payment_status = payment_status

      todo.update({
        'payroll':payroll,
        'payrollTab':True
      })    

      return render(request, 'staffpayroll.html',todo)

   except:
      traceback.print_exc()
      return render(request, 'pagenotFound.html')


@login_required(login_url='login')
def AddLoan(request):
  try:
    if request.method != 'POST':
      return JsonResponse({
        'success': False,
        'msg_swa': 'Njia ya maombi si sahihi',
        'msg_eng': 'Invalid request method'
      })

    todo = todoFunct(request)
    kampuni = todo['kampuni']
    shell = todo['shell']
    general = todo['general']
    useri = todo['useri']

    if not useri.admin:
      return JsonResponse({
        'success': False,
        'msg_swa': 'Hauna ruhusa ya kurekodi mkopo',
        'msg_eng': 'You have no permission to record loan'
      })

    staff_perm_id = int(request.POST.get('staff', 0))
    amount_raw = request.POST.get('amount', '0')
    due_date = request.POST.get('due_date', '')
    salary_deduction_raw = request.POST.get('salary_deduction', '0')
    paid_amount_raw = request.POST.get('paid_amount', '0')

    if not due_date:
      return JsonResponse({
        'success': False,
        'msg_swa': 'Tarehe ya mwisho kulipa inahitajika',
        'msg_eng': 'Due date is required'
      })

    try:
      amount = Decimal(amount_raw or '0')
      salary_deduction = Decimal(salary_deduction_raw or '0')
      paid_amount = Decimal(paid_amount_raw or '0')
    except (InvalidOperation, TypeError):
      return JsonResponse({
        'success': False,
        'msg_swa': 'Kiasi si sahihi, tafadhali hakiki namba ulizoingiza',
        'msg_eng': 'Invalid numeric values provided'
      })

    if amount <= 0:
      return JsonResponse({
        'success': False,
        'msg_swa': 'Kiasi cha mkopo lazima kiwe zaidi ya sifuri',
        'msg_eng': 'Loan amount must be greater than zero'
      })

    perm_qs = InterprisePermissions.objects.filter(
      pk=staff_perm_id,
      Interprise__company=kampuni.id,
      user__kopesheka=True,
    )

    if not general:
      perm_qs = perm_qs.filter(Interprise=shell.id)

    if not perm_qs.exists():
      return JsonResponse({
        'success': False,
        'msg_swa': 'Staff uliyochagua haruhusiwi kukopeshwa au haipo kwenye kituo husika',
        'msg_eng': 'Selected staff is not loan-eligible or not in your station'
      })

    perm = perm_qs.first()
    loan = StaffLoan()
    loan.staff = perm.user
    loan.compani = kampuni
    loan.shell = perm.Interprise
    loan.amount = amount
    loan.due_date = due_date
    loan.salary_deduction = salary_deduction
    loan.paid_amount = paid_amount
    loan.by = useri
    loan.save()

    return JsonResponse({
      'success': True,
      'msg_swa': 'Mkopo wa staff umehifadhiwa kikamilifu',
      'msg_eng': 'Staff loan saved successfully',
      'id': loan.id
    })

  except Exception as err:
    print(err)
    traceback.print_exc()
    return JsonResponse({
      'success': False,
      'msg_swa': 'Kuna hitilafu wakati wa kuhifadhi mkopo',
      'msg_eng': 'An error occurred while saving loan'
    })


@login_required(login_url='login')
def LoansStaff(request):
  try:
    todo = todoFunct(request)
    kampuni = todo['kampuni']
    shell = todo['shell']
    general = todo['general']
    useri = todo['useri']

    loan_staffs = InterprisePermissions.objects.filter(
      Interprise__company=kampuni.id,
      user__kopesheka=True,
      isActive=True,
    ).select_related('user__user', 'Interprise')

    if not general:
      loan_staffs = loan_staffs.filter(Interprise=shell.id)

    loan_staffs = loan_staffs.distinct('user')

    loans = StaffLoan.objects.filter(compani=kampuni.id).select_related('staff__user', 'shell')

    if not general:
      loans = loans.filter(shell=shell.id)

    loans = list(loans.order_by('-id'))
    for ln in loans:
      balance = (ln.amount or Decimal('0')) - (ln.paid_amount or Decimal('0'))
      ln.balance = balance if balance > 0 else Decimal('0')

    todo.update({
      'loan_staffs': loan_staffs,
      'staff_loans': loans,
      'loansTab': True,
    })

    return render(request, 'staffloans.html', todo)
  except Exception as err:
    print(err)
    traceback.print_exc()
    return render(request, 'pagenotFound.html')

       

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
          rec_salary = matumizi.objects.filter(Q(heo_pay=staff.user)|Q(sta_pay__user=staff.user),compani=kampuni.id)
          salary = rec_salary.first() if rec_salary.exists() else None
          tax_group = exptaxGroup.objects.filter(company=kampuni.id)
          usr = staff.user
          isActive = False
          if not general:
              belongs = InterprisePermissions.objects.filter(Interprise=shell.id,user=usr,isActive=True)
              isActive = belongs.last().isActive if belongs.exists() else False
              if staff.Interprise != shell and  belongs.exists():
                  staff = InterprisePermissions.objects.get(Interprise=shell.id,user=usr)

          todo.update({
            's':staff,
            'isActive': isActive,
            'salary': salary,
            'staffTab':True,
            'tax_group': tax_group
          })
          return render(request, 'staffView.html',todo)
    else:
       return render(request, 'pagenotFound.html')
  except:
    traceback.print_exc()
    return render(request, 'pagenotFound.html')
  