from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from account.models import StaffLoan, UserExtend, attachments, exptaxGroup, loanPayMent,shifts,shiftPump,fuel_pumps,DepositTo,matumizi,rekodiMatumizi,wekaCash,toaCash,PhoneMailConfirm,wateja,wasambazaji,Interprise,InterprisePermissions,PaymentAkaunts,staff_akaunt_permissions
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.models import F
from django.db import transaction
from django.core import serializers
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage

# from datetime import datetime
from django.utils import timezone as django_tz
from django.utils.dateparse import parse_datetime
django_tz.now()

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
import json
import traceback
from decimal import Decimal, InvalidOperation


from account.todos import Todos,confirmMailF
def todoFunct(request):
  usr = Todos(request)
  return usr.todoF()


def payments_nav_context(todo, request, nav_key=None):
    from salepurchase.views import toApprovalPayments
    approval = toApprovalPayments(request) or {}
    if isinstance(approval, dict) and approval.get('success') is False:
        approval = {}
    todo['approval'] = approval
    if nav_key:
        todo['payment_nav_active'] = nav_key
    return todo


def _payment_statement_account_qs(todo):
    useri = todo['useri']
    payacc = todo['payacc']
    if not (useri.admin or useri.ceo):
        payacc = payacc.filter(no_amount=False)
    return payacc


def _payment_statement_recorded_by_qs(todo):
    kampuni = todo['kampuni']
    general = todo['general']
    shell = todo['shell']
    allowed_accounts = _payment_statement_account_qs(todo).values_list('id', flat=True)

    weka_by = wekaCash.objects.filter(
        Interprise__company=kampuni,
        Amount__gt=0,
        Akaunt_id__in=allowed_accounts,
        by__isnull=False,
    )
    toa_by = toaCash.objects.filter(
        Interprise__company=kampuni,
        Amount__gt=0,
        Akaunt_id__in=allowed_accounts,
        by__isnull=False,
    )

    if not general:
        weka_by = weka_by.filter(Interprise=shell.id)
        toa_by = toa_by.filter(Interprise=shell.id)

    recorder_ids = set(
        weka_by.values_list('by_id', flat=True).distinct()
    ) | set(
        toa_by.values_list('by_id', flat=True).distinct()
    )

    return UserExtend.objects.filter(pk__in=recorder_ids).order_by(
        'user__first_name', 'user__last_name'
    )


def _classify_weka_payment(row):
    if row.get('sales__mobile_pay') or row.get('mobile_pay'):
        return 'mobile_payment'
    if row.get('customer_id'):
        return 'customer_payment'
    if row.get('biforeShift'):
        return 'cash_deposit'
    if row.get('mauzo') or row.get('shift_id'):
        return 'pump_attendant'
    if row.get('kuhamisha'):
        return 'bank_deposit'
    return 'other_receive'


def _classify_toa_payment(row):
    if row.get('matumizi_id'):
        return 'expense'
    if row.get('bill_id') or row.get('trsp_bill_id'):
        return 'bill_payment'
    if row.get('kuhamisha'):
        return 'bank_deposit'
    if row.get('personal'):
        return 'personal'
    return 'other_payment'


def _serialize_weka_rows(rows):
    data = []
    for row in rows:
        data.append({
            'id': row['id'],
            'direction': 'in',
            'date': row['tarehe'].isoformat() if row['tarehe'] else None,
            'amount': float(row['Amount'] or 0),
            'before': float(row['before'] or 0),
            'after': float(row['After'] or 0),
            'received_amount': float(row['Amount'] or 0),
            'withdrawal_amount': None,
            'account_id': row['Akaunt_id'],
            'account_name': row.get('account_name') or '',
            'station_id': row['Interprise_id'],
            'station_name': row.get('station_name') or '',
            'recorded_by': f"{row.get('BFname') or ''} {row.get('BLname') or ''}".strip(),
            'kutoka': row.get('kutoka') or '',
            'mauzo': bool(row.get('mauzo')),
            'shift_id': row.get('shift_id'),
            'cd_order_id': row.get('cdOrder_id'),
            'kuhamisha': bool(row.get('kuhamisha')),
            'huduma': bool(row.get('huduma')),
            'bifore_shift': bool(row.get('biforeShift')),
            'maelezo': row.get('maelezo') or '',
            'customer_id': row.get('customer_id'),
            'customer_name': row.get('custN') or '',
            'mobile_pay': bool(row.get('mobile_pay')),
            'shift_code': row.get('shift_code') or '',
            'shift_by_name': f"{row.get('shiftBFname') or ''} {row.get('shiftBLname') or ''}".strip(),
            'payment_type': _classify_weka_payment(row),
            'approved': bool(row.get('admin_approval')),
        })
    return data


def _serialize_toa_rows(rows):
    data = []
    for row in rows:
        data.append({
            'id': row['id'],
            'direction': 'out',
            'date': row['tarehe'].isoformat() if row['tarehe'] else None,
            'amount': float(row['Amount'] or 0),
            'before': float(row['before'] or 0),
            'after': float(row['After'] or 0),
            'received_amount': None,
            'withdrawal_amount': float(row['Amount'] or 0),
            'account_id': row['Akaunt_id'],
            'account_name': row.get('account_name') or '',
            'station_id': row['Interprise_id'],
            'station_name': row.get('station_name') or '',
            'recorded_by': f"{row.get('BFname') or ''} {row.get('BLname') or ''}".strip(),
            'kwenda': row.get('kwenda') or '',
            'kuhamisha': bool(row.get('kuhamisha')),
            'personal': bool(row.get('personal')),
            'expense_name': row.get('expense_name') or '',
            'bill_id': row.get('bill_id'),
            'bill_name': row.get('bill_name') or '',
            'matumizi_id': row.get('matumizi_id'),
            'trsp_bill_id': row.get('trsp_bill_id'),
            'trsp_bill_name': row.get('trsp_bill_name') or '',
            'maelezo': row.get('maelezo') or '',
            'payment_type': _classify_toa_payment(row),
            'approved': bool(row.get('admin_approval')),
        })
    return data


def _payment_statement_summary(weka_qs, toa_qs):
    received = Decimal(str(weka_qs.aggregate(total=Sum('Amount'))['total'] or 0))
    paid = Decimal(str(toa_qs.aggregate(total=Sum('Amount'))['total'] or 0))
    return {
        'received': float(received),
        'paid': float(paid),
        'net': float(received - paid),
        'count_in': weka_qs.count(),
        'count_out': toa_qs.count(),
    }


def _parse_payment_statement_dt(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        dt = value
    else:
        dt = parse_datetime(str(value))
        if dt is None:
            try:
                dt = datetime.datetime.fromisoformat(str(value))
            except ValueError:
                return None
    if django_tz.is_naive(dt):
        dt = django_tz.make_aware(dt, django_tz.get_current_timezone())
    return dt


def _payment_statement_overview(todo, account_id=0, recorded_by=0, payment_type='', direction='', station_id=0):
    now = django_tz.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - datetime.timedelta(days=today_start.isoweekday() - 1)
    month_start = today_start.replace(day=1)
    last_month_end = month_start - datetime.timedelta(seconds=1)
    last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year_start = today_start.replace(month=1, day=1)
    last_year_start = year_start.replace(year=year_start.year - 1)
    last_year_end = year_start - datetime.timedelta(seconds=1)

    ranges = {
        'today': (today_start, now),
        'week': (week_start, now),
        'month': (month_start, now),
        'last_month': (last_month_start, last_month_end),
        'this_year': (year_start, now),
        'last_year': (last_year_start, last_year_end),
    }
    overview = {}
    for key, (t_fr, t_to) in ranges.items():
        weka, toa = _build_payment_statement_qs(
            todo, t_fr, t_to, account_id, recorded_by, payment_type, direction, station_id
        )
        overview[key] = _payment_statement_summary(weka, toa)
    return overview


def _filter_weka_by_type(qs, payment_type):
    if not payment_type:
        return qs
    if payment_type == 'mobile_payment':
        return qs.filter(sales__mobile_pay=True)
    if payment_type == 'customer_payment':
        return qs.filter(customer__isnull=False).exclude(sales__mobile_pay=True)
    if payment_type == 'cash_deposit':
        return qs.filter(biforeShift=True)
    if payment_type == 'pump_attendant':
        return qs.filter(Q(mauzo=True) | Q(shift__isnull=False))
    if payment_type == 'bank_deposit':
        return qs.filter(kuhamisha=True)
    return qs.none()


def _filter_toa_by_type(qs, payment_type):
    if not payment_type:
        return qs
    if payment_type == 'expense':
        return qs.filter(matumizi__isnull=False)
    if payment_type == 'bank_deposit':
        return qs.filter(kuhamisha=True)
    if payment_type == 'bill_payment':
        return qs.filter(Q(bill__isnull=False) | Q(trsp_bill__isnull=False))
    if payment_type == 'personal':
        return qs.filter(personal=True)
    return qs.none()


_WEKA_PAYMENT_TYPES = {
    'mobile_payment', 'customer_payment', 'cash_deposit', 'pump_attendant', 'other_receive',
}
_TOA_PAYMENT_TYPES = {'expense', 'bill_payment', 'personal', 'other_payment'}


def _build_payment_statement_qs(todo, t_fr, t_to, account_id=0, recorded_by=0, payment_type='', direction='', station_id=0):
    kampuni = todo['kampuni']
    useri = todo['useri']
    general = todo['general']
    shell = todo['shell']
    allowed_accounts = _payment_statement_account_qs(todo).values_list('id', flat=True)

    weka = wekaCash.objects.filter(
        Interprise__company=kampuni,
        Amount__gt=0,
        Akaunt_id__in=allowed_accounts,
        tarehe__range=[t_fr, t_to],
    ).annotate(
        station_name=F('Interprise__name'),
        account_name=F('Akaunt__Akaunt_name'),
        custN=F('customer__jina'),
        BFname=F('by__user__first_name'),
        BLname=F('by__user__last_name'),
    )

    toa = toaCash.objects.filter(
        Interprise__company=kampuni,
        Amount__gt=0,
        Akaunt_id__in=allowed_accounts,
        tarehe__range=[t_fr, t_to],
    ).annotate(
        station_name=F('Interprise__name'),
        account_name=F('Akaunt__Akaunt_name'),
        BFname=F('by__user__first_name'),
        BLname=F('by__user__last_name'),
    )

    if station_id:
        weka = weka.filter(Interprise_id=station_id)
        toa = toa.filter(Interprise_id=station_id)
    elif not general:
        weka = weka.filter(Interprise=shell.id)
        toa = toa.filter(Interprise=shell.id)

    if account_id:
        weka = weka.filter(Akaunt_id=account_id)
        toa = toa.filter(Akaunt_id=account_id)

    if recorded_by:
        weka = weka.filter(by_id=recorded_by)
        toa = toa.filter(by_id=recorded_by)

    if payment_type:
        if direction in ('', 'in'):
            if payment_type == 'bank_deposit' or payment_type in _WEKA_PAYMENT_TYPES:
                weka = _filter_weka_by_type(weka, payment_type)
            else:
                weka = weka.none()
        if direction in ('', 'out'):
            if payment_type == 'bank_deposit' or payment_type in _TOA_PAYMENT_TYPES:
                toa = _filter_toa_by_type(toa, payment_type)
            else:
                toa = toa.none()
    elif direction == 'in':
        toa = toa.none()
    elif direction == 'out':
        weka = weka.none()

    return weka, toa


@login_required(login_url='login')
def pdcBillsView(request):
    try:
        i = int(request.GET.get('i',0))
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        exp = matumizi.objects.get(pk=i,compani=kampuni)
        todo.update({
            'exp':exp,
            'isPdBills':True
        })
        payments_nav_context(todo, request, 'pdcbills')

        return render(request,'paypdcBillsView.html',todo)
    except:
        return redirect('/pdcBills') 
    
@login_required(login_url='login')
def pdcBills(request):
  todo = todoFunct(request)
  general = todo['general']
  kampuni = todo['kampuni']
  shell = todo['shell']
  stations = Interprise.objects.filter(company = kampuni)
  pbills = matumizi.objects.filter(compani=kampuni,duration__gt=0) 
  if not general:
      pbills = pbills.filter(shell=shell)

  todo.update({
     'stations':stations,
    #   'payacc':payacc,
      'pbills':pbills,
      'isPdBills':True
  })
  payments_nav_context(todo, request, 'pdcbills')
  return render(request,'paypdcBills.html',todo)

@login_required(login_url='login')
def expensespanel(request):
  todo = todoFunct(request)
  general = todo['general']
  kampuni = todo['kampuni']
  useri = todo['useri']
  
  taxtgroup = exptaxGroup.objects.filter(company=kampuni)
  expses = matumizi.objects.filter(compani=kampuni,paye=False)

  todo.update({
        'taxtgroup':taxtgroup,
        'expses':expses,
        'isExpenses':True,
        'expenseList':True
  })

  return render(request,'matumiziAll.html',todo)
@login_required(login_url='login')
def taxgroups(request):
  todo = todoFunct(request)
  general = todo['general']
  kampuni = todo['kampuni']
  useri = todo['useri']
  
  taxtgroup = exptaxGroup.objects.filter(company=kampuni)
  

  todo.update({
        'taxtgroup':taxtgroup,
        'expenseList':True,
        'isTaxGroup':True
  })

  return render(request,'matumiziTaxGroup.html',todo)

@login_required(login_url='login')
def payaccounts(request):
  todo = todoFunct(request)
  general = todo['general']
  kampuni = todo['kampuni']
  useri = todo['useri']
  
  stations = None
  payaacc = todo['payacc']
  if general:
     stations = Interprise.objects.filter(company = kampuni)
  if not (useri.ceo or useri.admin):
      shell = todo['shell']
      payaacc = payaacc.filter(Interprise=shell.id, no_amount=False)
  elif not useri.admin:
      payaacc = payaacc.filter(no_amount=False)

  AccSum = payaacc.filter(no_amount=False).aggregate(sumi=Sum('Amount'))['sumi'] or 0

  todo.update({
      'stations':stations,
      'payaacc':payaacc,
      'AccSum':AccSum,
      'isAkaunti':True
  })
  payments_nav_context(todo, request, 'payaccounts')
  return render(request,'payaccounts.html',todo)



@login_required(login_url='login')
def addPBill(request):
    try:
        if request.method == "POST":
            name=request.POST.get('name')
            amount= float(request.POST.get('amount',0))
            is_general = int(request.POST.get('general',0))
            it_depends = int(request.POST.get('depends',0))
            station= int(request.POST.get('station',0))
            nextPay= request.POST.get('nextPay')
            Period= int(request.POST.get('payPiriod'))
            dura= int(request.POST.get('payDura'))
            edit = int(request.POST.get('edit',0))

            newTaxGroup = int(request.POST.get('newTaxGroup',0))
            TaxGroup = int(request.POST.get('taxGroup',0))
            TaxGroupName = request.POST.get('taxGroupName','')
            TaxGroupRate = float(request.POST.get('taxGroupRate',0))

            attchReceipt = int(request.POST.get('attchReceipt',0))
            todo = todoFunct(request)
            kampuni = todo['kampuni']
            admin = todo['admin']
            theShell = None
            if not is_general:
                theShell = Interprise.objects.get(pk=station,company=kampuni)

            Eexp = matumizi.objects.filter(matumizi__icontains=name,shell=theShell,compani=kampuni)   

            data = {
                'success':True,
                'swa':'Bili imehifadhiwa kikamilifu',
                'eng':'Bill added successfully'
            }
            exp = matumizi()
             
            if not (Eexp.exists() and  edit) or (edit and matumizi.objects.filter(pk=edit).exists()):
                expTaxGroup = exptaxGroup()
                if newTaxGroup:
                    expTaxGroup.name = TaxGroupName
                    expTaxGroup.rate = TaxGroupRate
                    expTaxGroup.company = kampuni
                    expTaxGroup.save()
                else:
                    expTaxGroup = exptaxGroup.objects.get(pk=TaxGroup)

                exp.taxGroup = expTaxGroup
                
                exp.matumizi = name
             
                exp.general = is_general
                exp.amount = amount
                exp.duration = dura
                exp.shell = theShell
                exp.depends = it_depends
                exp.next_pay = nextPay
                exp.attachReceipt = attchReceipt
                exp.compani = kampuni
                exp.save()
            else:
                data = {
                    'success':False,
                    'swa':'Tayari kuna bili nyingine yenye jina kama hili',
                    'eng':'Bill name arleady existed'
                }
               
            return JsonResponse(data)
        else:
            data = {'success':False}    
            return JsonResponse(data)
    except:
        data = {
            'swa':'Bili haikuongezwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi',
            'eng':'The bill was not saved please try again correctly',
            'success':False
        }   
        return JsonResponse(data)
    
@login_required(login_url='login')
def addAkaunt(request):
    try:
        if request.method == "POST":
            name=request.POST.get('name')
            amount= request.POST.get('amount')
            allow= int(request.POST.get('allow',0))
            station= int(request.POST.get('station',0))
            aina= request.POST.get('aina')
            todo = todoFunct(request)

            cheo = todo['cheo']
            useri = todo['useri']
            duka= Interprise.objects.get(pk=station)

            if useri.admin:  
            
                if PaymentAkaunts.objects.filter(Akaunt_name=name ,Interprise=duka.id).exists():
                    data={
                        'success':False,
                        'message_swa':'Taarifa kuhusu akaunti hazijafanikiwa kutokana na kuwepo akaunti nyingine yenye jina kama hili tafadhari badili jina la akaunti',
                        'message_eng':'The same account name appear, Payment account info was not recorded. Please change the account name'
                    }

                    
                else:
                    ak = PaymentAkaunts() 
                    ak.Interprise = duka
                    ak.Akaunt_name = name
                    ak.Amount = float(amount)
                    ak.onesha = allow
                    ak.aina = aina
                    ak.addedDate = datetime.datetime.now(tz=timezone.utc)

                    ak.save()

                    data={
                        'success':True,
                        'message_swa':'Taarifa kuhusu Akaunti ya malipo zimefanikiwa kurekodiwa kikamilifu',
                        'message_eng':'Payment account info added successfully'
                    }

                return JsonResponse(data) 
        else:
          return render(request,'pagenotFound.html',todoFunct(request))     
    except:
        data={
            'success':False,
            'message_swa':'Akaunti ya malipo haijatengenezwa kutokana na hitilafu. Tafadhari jaribu tena kwa kujaza taarifa kwa usahihi',
            'message_eng':'Payment account info was not added. Please try again'
        }

        return JsonResponse(data)

@login_required(login_url='login')
def editAkaunt(request):
    try:
        if request.method == "POST":
            name=request.POST.get('name')
            amount= request.POST.get('amount')
            allow= int(request.POST.get('allow',0))
            aina= request.POST.get('aina')
            idn= int(request.POST.get('value',0))
            no_show= int(request.POST.get('no_show'))
            todo = todoFunct(request)
            cheo = todo['cheo']
            useri = todo['useri'] 
            kampuni = todo['kampuni']
            if not useri.admin:
                data = {
                        'success':False,
                        'swa':'Hauna ruhusa hii kwa sasa tafadhari wasiliana na uongozi',
                        'eng':'you have no permision for this action please contact admin'
                        
                        }
                return JsonResponse(data)

            ak = PaymentAkaunts.objects.get(pk=idn,Interprise__company=kampuni ) 
            #  ak.Interprise = InterprisePermissions.objects.get(user=request.user.id, default=True).Interprise
            ak.Akaunt_name = name
            ak.Amount = float(amount)
            ak.onesha = allow
            ak.aina = aina
            ak.no_amount = no_show 
            ak.save()

            data={
                'success':True,
                'swa':'Akaunti imehaririwa kikamilifu',
                'eng':'Account edited successfuly'
            }

            return JsonResponse(data) 

        else:
          return render(request,'pagenotFound.html',todoFunct(request))         
    except:
        data={
            'success':False,
            'swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
            'eng':'The action was not successfully due to error please try again'
        }

        return JsonResponse(data)
    

@login_required(login_url='login')
def kuwekapesa(request):
     if request.method == "POST":
        
         try:
            ac=request.POST.get('ac')
            idn= request.POST.get('valued')
            hdm =request.POST.get('sel')
            hd = int(request.POST.get('hd'))
            eleza= request.POST.get('Maelezo')
            fromi= request.POST.get('kutoka')
            amounti= int(request.POST.get('kiasi'))
            acid= int(request.POST.get('is'))
            todo = todoFunct(request)
            useri = todo['useri']
            cheo = todo['cheo']
            admin = todo['admin']
            manager = todo['manager']

            if useri.admin or manager:  
                #  kuapdate inapoenda
                # entp=InterprisePermissions.objects.get(user__user=request.user,default=True).Interprise
                
                wekakwa= PaymentAkaunts.objects.get(pk=acid)
                beforweka=wekakwa.Amount

                PaymentAkaunts.objects.filter(pk=acid).update(Amount=F('Amount')+amounti)

                wekapesa = wekaCash()
                wekapesa.Akaunt = wekakwa
                wekapesa.Amount = amounti
                wekapesa.before = beforweka
                wekapesa.After = beforweka+amounti
                wekapesa.kutoka = fromi
                wekapesa.maelezo = eleza
                # if hd:
                #     wekapesa.huduma_nyingine = HudumaNyingine.objects.get(pk=hdm,Interprise=entp.id)    

                wekapesa.tarehe = datetime.datetime.now(tz=timezone.utc)
                wekapesa.by=todoFunct(request)['useri']
                wekapesa.Interprise=wekakwa.Interprise

                if not wekakwa.onesha:
                    wekapesa.usiri =True
                wekapesa.save()
    
                data={
                    'success':True,
                    'message_swa':'Muamala wa kuweka fedha umefanikiwa',
                    'message_eng':'Cash deposit transaction recorded succeffully'
                }
            else:
                data = {
                    'success':False,
                    'message_swa':'Hauna ruhusa kwa kitendo hiki kwa sasa tafadhari wasiliana na uongozi',
                    'message_eng':'You have no permission for this action please contact your admin'

                }
            return JsonResponse(data) 
         except:
            data={
                'success':False,
                'message_swa':'Muamala wa kuweka fedha Haukufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi',
                'message_eng':'Cash deposit transaction was not recorded. please try again'
            }

            return JsonResponse(data) 
     else:
       return render(request,'pagenotFound.html',todoFunct(request)) 

# kutoa pesa
@login_required(login_url='login')
def kutoaPesa(request):
    if request.method == "POST":    
        try:
            ac=int(request.POST.get('ac',0))
            idn= request.POST.get('value')
            eleza= request.POST.get('Maelezo')
            fromi= request.POST.get('kutoka')
            amounti= float(request.POST.get('kiasi'))
            baki= float(request.POST.get('baki'))
            acid= int(request.POST.get('is'))
            todo = todoFunct(request)
            cheo = todo['cheo']
            useri = todo['useri']
            admin = todo['admin']
            manager = todo['manager']
            kampuni = todo['kampuni']
            #  kuapdate inapoenda
            if manager or useri.admin : 
                # entp=cheo.Interprise
                toakwa= PaymentAkaunts.objects.get(pk=acid,Interprise__company=kampuni)
                beforweka=float(toakwa.Amount)
                akaunti = toakwa # Initialize the other destination account ...............//
                if ac:
                    akaunti=PaymentAkaunts.objects.get(pk=idn,Interprise__company=kampuni)

                # PaymentAkaunts.objects.filter(pk=acid).update(Amount=baki)

                toa = toaCash()
                toa.Akaunt = toakwa
                toa.Amount = amounti
                toa.before = beforweka
                toa.After = baki
                if ac:
                    toa.kwenda = akaunti.Akaunt_name
                    if not akaunti.onesha:
                        toa.kwenda_siri = True
                else:
                    toa.kwenda = "Personal"
                if not toakwa.onesha:
                    toa.usiri =True       
                toa.maelezo = eleza
                toa.makato = float(beforweka+amounti-baki)
                toa.tarehe = datetime.datetime.now(tz=timezone.utc)
                toa.by=useri
                toa.Interprise=toakwa.Interprise
                toa.kuhamisha = ac  
                toa.personal = not ac  
                toa.kuhamishaNje =  akaunti.Interprise is not toakwa.Interprise
                toa.admin_approval = useri.admin
                toa.save()
                     
                toakwa.Amount = float(baki)
                toakwa.save()

                # kuapdate inapotoka
                if ac:
                    before=float(akaunti.Amount)
                    PaymentAkaunts.objects.filter(pk=idn).update(Amount=F('Amount')+amounti)

                    Change=wekaCash()
                    Change.Akaunt=akaunti
                    Change.Amount = amounti
                    Change.before=before
                    Change.After=float(before + amounti)
                    Change.kutoka= PaymentAkaunts.objects.get(pk=acid, Interprise__owner=admin.id).Akaunt_name
                    Change.maelezo = eleza
                    Change.tarehe = datetime.datetime.now(tz=timezone.utc)
                    Change.by=todoFunct(request)['useri']
                    Change.Interprise=akaunti.Interprise
                    Change.kuhamisha = ac
                    Change.kuhamishaNje =  akaunti.Interprise is not toakwa.Interprise
                    Change.admin_approval = useri.admin
                    if not PaymentAkaunts.objects.get(pk=idn, Interprise__owner=admin.id).onesha:
                        Change.usiri = True
                    if not toakwa.onesha:
                        Change.kutoka_siri = True    
                    Change.save()

                    depoTo = DepositTo()
                    depoTo.weka = Change
                    depoTo.save()

                    toa.depoTo = depoTo
                    toa.save()


                data={
                    'success':True,
                    'message_swa':'Taarifa za Muamala wa kuhamisha pesa zimefanikiwa kurekodiwa kikamilifu',
                    'message_eng':'Cash withdraw transaction recorded successfully'

                }

            
                return JsonResponse(data) 
            else:
                data = {
                     'success':False,
                    'message_swa':'Huna Ruhusa ya Kufanya Kitendo hiki kwa sasa tafadhari wasiliana na uongozi',
                    'message_eng':'You have no permission for this action please contact admin'
  
                }
                return JsonResponse(data)
        except Exception as err:
            print(err)
            traceback.print_exc()
            data={
                'success':False,
                'message_swa':'Taarifa za Muamala wa kuhamisha pesa hazijafanikiwa kurekodiwa kutokana na hitilafu. Tafadhari jaribu tena kwa usahihi',
                'message_eng':'Cash withdraw transaction was not recorded. Please try again'
            }
        return JsonResponse(data)
    else:
           return render(request,'pagenotFound.html',todoFunct(request)) 
    
@login_required(login_url='login')
def deposit(request):
    try:
        todo = todoFunct(request)
        useri = todo['useri']
        admin = todo['admin']
        cheo = todo['cheo']
        general = todo['general']
        kampuni = todo['kampuni']
        

        page_num = request.GET.get('page',1)
        shell = todo['shell']
        
        weka = wekaCash.objects.filter(Interprise__company=kampuni,saRec=False)
        if not general:
            weka = weka.filter(Interprise=shell.id)

        weka = weka.order_by('-pk')
        p = Paginator(weka,15)

        try:
            page = p.page(page_num)   

        except:
            page = p.page(1)   

        pg_number = p.num_pages

        todo.update({
            # 'weka':weka,
            'weka':page,
            'p_num':page_num,
            'pages':pg_number,
            'exists':weka.exists(),
            'isdeposit':True
        })    
        payments_nav_context(todo, request, 'acct_deposit')

        return render(request,'payaDiposti.html',todo)

    except:
        return render(request,'pagenotFound.html')
    

@login_required(login_url='login')
def withdraw(request):
    try:
        todo = todoFunct(request)
        useri = todo['useri']
        admin = todo['admin']
        cheo = todo['cheo']
        general = todo['general']
        kampuni = todo['kampuni']

        page_num = request.GET.get('page',1)
        shell = todo['shell']
        
        toa = toaCash.objects.filter(Interprise__company=kampuni)
        if not general:
            toa = toa.filter(Interprise=shell.id)

        toa = toa.order_by('-pk')
        p = Paginator(toa,15)

        try:
            page = p.page(page_num)   

        except:
            page = p.page(1)   

        pg_number = p.num_pages

       

        todo.update({
            'toa':page,
            'page':page,
            'p_num':page_num,
            'pages':pg_number,
            'exists':toa.exists(),
            'iswithdraw':True
        })    
        payments_nav_context(todo, request, 'acct_withdraw')

        return render(request,'payawithdraw.html',todo)

    except:
        return render(request,'pagenotFound.html')


@login_required(login_url='login')
def paymentStatement(request):
    try:
        todo = todoFunct(request)
        useri = todo['useri']
        kampuni = todo['kampuni']
        general = todo['general']
        shell = todo['shell']

        stations = Interprise.objects.filter(company=kampuni)
        payacc = _payment_statement_account_qs(todo)
        staff = _payment_statement_recorded_by_qs(todo)

        if not general:
            stations = stations.filter(pk=shell.id)
            payacc = payacc.filter(Interprise=shell.id)

        payments_nav_context(todo, request, 'payment_statement')
        todo.update({
            'stations': stations,
            'payacc': payacc,
            'staff_users': staff,
            'isPaymentStatement': True,
        })
        return render(request, 'paymentStatement.html', todo)
    except Exception as err:
        print(err)
        traceback.print_exc()
        return render(request, 'pagenotFound.html')


@login_required(login_url='login')
def paymentStatementData(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'swa': 'Bad Request', 'eng': 'Bad Request'})

    try:
        todo = todoFunct(request)
        t_fr = request.POST.get('tFr')
        t_to = request.POST.get('tTo')
        account_id = int(request.POST.get('account', 0) or 0)
        recorded_by = int(request.POST.get('recordedBy', 0) or 0)
        payment_type = request.POST.get('paymentType', '').strip()
        direction = request.POST.get('direction', '').strip()
        station_id = int(request.POST.get('station', 0) or 0)
        overview = int(request.POST.get('overview', 0) or 0)
        summary_only = int(request.POST.get('summaryOnly', 0) or 0)

        if overview:
            payload = {
                'success': True,
                'overview': _payment_statement_overview(
                    todo, account_id, recorded_by, payment_type, direction, station_id
                ),
            }
            return JsonResponse(payload)

        t_fr_dt = _parse_payment_statement_dt(t_fr)
        t_to_dt = _parse_payment_statement_dt(t_to)
        if not t_fr_dt or not t_to_dt:
            return JsonResponse({'success': False, 'swa': 'Tarehe hazipo', 'eng': 'Dates are required'})

        weka, toa = _build_payment_statement_qs(
            todo, t_fr_dt, t_to_dt, account_id, recorded_by, payment_type, direction, station_id
        )
        summary = _payment_statement_summary(weka, toa)

        payload = {
            'success': True,
            'summary': summary,
        }

        if not summary_only:
            weka_rows = list(weka.annotate(
                mobile_pay=F('sales__mobile_pay'),
                shift_code=F('shift__code'),
                shiftBFname=F('shift__by__user__first_name'),
                shiftBLname=F('shift__by__user__last_name'),
            ).values(
                'id', 'tarehe', 'Amount', 'before', 'After', 'Akaunt_id', 'Interprise_id', 'kutoka', 'maelezo',
                'admin_approval', 'biforeShift', 'mauzo', 'kuhamisha', 'huduma', 'cdOrder_id', 'customer_id', 'shift_id',
                'account_name', 'station_name', 'custN', 'BFname', 'BLname', 'mobile_pay',
                'shift_code', 'shiftBFname', 'shiftBLname',
            ))
            toa_rows = list(toa.annotate(
                expense_name=F('matumizi__matumizi__matumizi'),
                bill_name=F('bill__jina'),
                trsp_bill_name=F('trsp_bill__jina'),
            ).values(
                'id', 'tarehe', 'Amount', 'before', 'After', 'Akaunt_id', 'Interprise_id', 'kwenda', 'maelezo',
                'admin_approval', 'kuhamisha', 'personal', 'matumizi_id', 'bill_id', 'trsp_bill_id',
                'account_name', 'station_name', 'BFname', 'BLname', 'expense_name', 'bill_name', 'trsp_bill_name',
            ))
            transactions = _serialize_weka_rows(weka_rows) + _serialize_toa_rows(toa_rows)
            transactions.sort(key=lambda x: x['date'] or '', reverse=True)
            payload['transactions'] = transactions

        return JsonResponse(payload)
    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({'success': False, 'swa': 'Imeshindikana', 'eng': 'Request failed'})


@login_required(login_url='login')
def expenseRecords(request):
    try:
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        taxtgroup = exptaxGroup.objects.filter(company=kampuni)
        todo.update({
            'taxtgroup':taxtgroup,
            'isExpRec':True
        })
        
        return render(request, 'matumiziRec.html', todo)
    
    except:
        traceback.print_exc()
        return render(request, 'pagenotFound.html', todoFunct(request))
    

@login_required(login_url='login')
def expattachments(request):
    try:
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        general = todo['general']
        uns = int(request.GET.get('uns',0))
        exp_recepts = todo['exp_recept'] 
        
        if uns and not exp_recepts:
            uns = 0
        missingAttachments = []    
        all_attachments = None
        if uns and exp_recepts:
           expAttach = rekodiMatumizi.objects.filter(by__company=kampuni.id,attachReceipt=True).order_by('-pk')     
           if not general:
                    shell = todo['shell']
                    expAttach = expAttach.filter(Interprise=shell)
           for exp in expAttach:
                 exp_recept = attachments.objects.filter(expAttach=exp.id)
                
                 if not exp_recept.exists() :
                     missingAttachments.append(exp)
        else:
            all_attachments = attachments.objects.filter(expAttach__by__company=kampuni.id).order_by('-pk')  
            if not general:
                shell = todo['shell']
                all_attachments = all_attachments.filter(expAttach__Interprise=shell)
            
            # Add pagination
            num = all_attachments.count()
            p = Paginator(all_attachments, 15)
            page_num = request.GET.get('page', 1)
            
            try:
                page = p.page(page_num)
            except EmptyPage:
                page = p.page(1)
            
            pg_number = p.num_pages
            all_attachments = page  

            todo.update({
            'pg_number':pg_number,
            'p_num':page_num,
            'all_attachments':all_attachments,
            
            })
   
       


        todo.update({
            
            'isExpAttach':True,
            'uns':uns,
            'missingAttachments':missingAttachments,
        })
        
        return render(request, 'matumiziAttachments.html', todo)
    
    except:
        traceback.print_exc()
        return render(request, 'pagenotFound.html', todoFunct(request))



def _apply_loan_deduction(matum, rec, amount, kampuni):
    """
    Ikiwa matumizi ina bendera ya paye=True na staff amepewa,
    angalia kama staff ana mkopo hai. Deduction = matum.amount - amount.
    Ongeza deduction kwenye StaffLoan.paid_amount (bila kuzidi deni lililobaki).
    """
    if rec.salary_advance:
        return

    if not (matum.paye and rec.staff):
        return
    try:
        deduction = Decimal(str(matum.amount or 0)) - amount
        if deduction <= 0:
            return
        active_loan = StaffLoan.objects.filter(
            staff=rec.staff,
            compani=kampuni,
        ).filter(
            paid_amount__lt=F('amount')
        ).order_by('created').first()
        if not active_loan:
            return
        remaining = active_loan.amount - active_loan.paid_amount
        actual_deduction = min(deduction, remaining)
        if actual_deduction > 0:
            active_loan.paid_amount = active_loan.paid_amount + actual_deduction
            active_loan.save(update_fields=['paid_amount'])
            loan_pay_rec = loanPayMent()
            loan_pay_rec.loan = active_loan
            loan_pay_rec.amount = actual_deduction
            loan_pay_rec.record = rec
            loan_pay_rec.save()
    except Exception:
        traceback.print_exc()


def _apply_salary_last_paid_update(matum, exp, category):
    """
    Kwa category ya mishahara, tumia period (YYYY-MM) kusasisha matumizi.last_paid.
    """
    if category != 'mishahara':
        return

    if _is_truthy_value(exp.get('is_salary_advance')):
        return

    raw_period = str(exp.get('period') or exp.get('salary_period') or '').strip()
    if not raw_period:
        return

    try:
        year_str, month_str = raw_period.split('-', 1)
        year = int(year_str)
        month = int(month_str)
        if month < 1 or month > 12:
            raise ValueError('Invalid month')

        if month == 12:
            next_month_first = date(year + 1, 1, 1)
        else:
            next_month_first = date(year, month + 1, 1)
        period_date = next_month_first - timedelta(days=1)
    except Exception:
        raise ValueError('Invalid salary period format. Expected YYYY-MM')

    matum.last_paid = period_date
    matum.save(update_fields=['last_paid'])


def _is_truthy_value(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return int(value) == 1
    if isinstance(value, str):
        return value.strip().lower() in ['1', 'true', 'yes', 'on']
    return False


def _save_salary_advance_loan(exp, rec, amount, kampuni, shell, useri, category):
    """
    Ikiwa rekodi ni salary advance/mkopo wa staff,
    hifadhi mkopo kwenye StaffLoan.

    Ikiwa kuna mkopo ambao bado haujaisha kwa staff huyu,
    ongeza amount kwenye mkopo huo (merge) badala ya kuunda mpya.
    """
    if category != 'mishahara' or not rec.salary_advance:
        return

    if not rec.staff:
        raise ValueError('Staff is required for salary advance')

    raw_deduction = exp.get('salary_advance_deduction')
    try:
        salary_deduction = Decimal(str(raw_deduction or 0))
    except InvalidOperation:
        raise ValueError('Invalid salary advance deduction amount')

    if salary_deduction <= 0:
        raise ValueError('Salary advance deduction must be greater than zero')

    loan_shell = rec.Interprise or shell or rec.matumizi.shell

    active_loan = StaffLoan.objects.filter(
        staff=rec.staff,
        compani=kampuni,
        paid_amount__lt=F('amount')
    ).order_by('created').first()

    if active_loan:
        active_loan.amount = Decimal(str(active_loan.amount or 0)) + amount
        active_loan.salary_deduction = salary_deduction
        if not active_loan.shell and loan_shell:
            active_loan.shell = loan_shell
        if not active_loan.by:
            active_loan.by = useri
        active_loan.save(update_fields=['amount', 'salary_deduction', 'shell', 'by'])
        return

    StaffLoan.objects.create(
        staff=rec.staff,
        compani=kampuni,
        shell=loan_shell,
        amount=amount,
        salary_deduction=salary_deduction,
        paid_amount=Decimal('0'),
        by=useri
    )


@login_required(login_url='login')
def addExpense(request):
      if request.method != "POST":
           return render(request,'pagenotFound.html',todoFunct(request))

      try:
            todo = todoFunct(request)
            useri = todo['useri']
            cheo = todo['cheo']
            shell = todo['shell']
            manager = todo['manager']
            kampuni = todo['kampuni']

            if not (useri.admin or cheo is not None or manager):
                return JsonResponse({
                    'success':False,
                    'message_eng':'You have no permission to add expenses',
                    'message_swa':'Hauna ruhusa ya kuongeza matumizi'
                })

            raw_entries = request.POST.get('expenses_json') or request.POST.get('expenses') or '[]'
            entries = json.loads(raw_entries)

            if not isinstance(entries, list) or not entries:
                return JsonResponse({
                    'success':False,
                    'message_eng':'No expense data received',
                    'message_swa':'Hakuna taarifa ya matumizi iliyopokelewa'
                })

            expDate = request.POST.get('expDate','')
            rec_datetime = datetime.datetime.now(tz=timezone.utc)
            if expDate:
                try:
                    parsed = datetime.datetime.fromisoformat(str(expDate).replace('Z', '+00:00'))
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=timezone.utc)
                    # Reject dates more than 1 day in the future
                    now_utc = datetime.datetime.now(tz=timezone.utc)
                    if parsed > now_utc + datetime.timedelta(days=1):
                        return JsonResponse({
                            'success': False,
                            'message_eng': 'Expense date cannot be far in the future',
                            'message_swa': 'Tarehe ya matumizi haiwezi kuwa mbele sana ya leo'
                        })
                    rec_datetime = parsed
                except (ValueError, OverflowError):
                    rec_datetime = datetime.datetime.now(tz=timezone.utc)

            with transaction.atomic():
                for exp in entries:
                    if not isinstance(exp, dict):
                        raise ValueError('Invalid expense row format')

                    category = str(exp.get('category') or '').strip().lower()
                    if category == 'customer_discounts':
                        matum = matumizi.objects.filter(compani=kampuni, discount=True).order_by('pk').first()
                        if not matum:
                            matum = matumizi.objects.create(
                                shell=shell,
                                compani=kampuni,
                                matumizi='Discount',
                                discount=True
                            )
                    else:
                        exp_group_id = exp.get('expense_group_id') or exp.get('group_id')
                        if not exp_group_id:
                            raise ValueError('Expense group is required')
                        matum = matumizi.objects.get(pk=int(exp_group_id), compani=kampuni)

                    raw_amount = exp.get('amount')
                    if raw_amount in [None, '']:
                        raw_amount = exp.get('amount_cash')
                    if raw_amount in [None, '']:
                        raw_amount = exp.get('amount_total')

                    try:
                        amount = Decimal(str(raw_amount or 0))
                    except InvalidOperation:
                        raise ValueError('Invalid amount value')

                    if amount <= 0:
                        raise ValueError('Amount must be greater than zero')

                    source_details = exp.get('source_details') if isinstance(exp.get('source_details'), dict) else {}
                    source_type = str(exp.get('source_type') or '').strip()
                    recipient_type = str(exp.get('recipient_type') or '').strip().lower()
                    is_salary_advance = _is_truthy_value(exp.get('is_salary_advance'))

                    receiver_name = str(exp.get('customer_name') or exp.get('receiver_name') or exp.get('recipient') or '').strip()
                    if category == 'fuel' and not receiver_name:
                        raise ValueError('Recipient is required for fuel expense')
                    if category == 'customer_discounts' and not receiver_name:
                        raise ValueError('Customer name is required for customer discount')

                    if category != 'customer_discounts' and recipient_type == 'staff' and exp.get('staff_id') in [None, '']:
                        raise ValueError('Staff recipient is required')

                    if is_salary_advance and category != 'mishahara':
                        raise ValueError('Salary advance option is only allowed for salary expenses')
                    
                    tax_gr = matum.taxGroup
                    
                       
                    rec = rekodiMatumizi()

                    staff_id = exp.get('staff_id')
                    if category != 'customer_discounts' and staff_id not in [None, '']:
                        try:
                            staff_obj = UserExtend.objects.get(pk=int(staff_id), company=kampuni)
                            rec.staff = staff_obj
                            if matum.posho or matum.paye:
                                salr = matumizi.objects.filter(Q(heo_pay=staff_obj.id)|Q(sta_pay__user=staff_obj.id),Isactive=True)
                                if salr.exists():
                                    tax_gr = salr.last().taxGroup if salr.exists() else tax_gr

                          
                        except Exception:
                            pass

                    rec.matumizi = matum
                    rec.tarehe = rec_datetime
                    rec.date = rec_datetime.date()
                    rec.kiasi = amount
                    rec.by = useri
                    rec.kabidhiwa = receiver_name[:500]
                    rec.maelezo = exp.get('remarks') or exp.get('desc') or ''
                    rec.attachReceipt = matum.attachReceipt
                    rec.salary_advance = is_salary_advance and category == 'mishahara'
                    rec.tax_group = tax_gr
                    tin_number = str(exp.get('tin_number') or '').strip()
                    nin_number = str(exp.get('nin_number') or '').strip()
                    if tin_number:
                        rec.tin_number = tin_number[:100]
                    if nin_number:
                        rec.maelezo = f'{rec.maelezo} | NIN: {nin_number}' if rec.maelezo else f'NIN: {nin_number}'


                    shift_obj = None
                    attendant_id = source_details.get('attendant_id')
                    if attendant_id not in [None, '']:
                        shift_qs = shifts.objects.filter(pk=int(attendant_id), record_by__Interprise__company=kampuni)
                        if shell:
                            shift_qs = shift_qs.filter(record_by__Interprise=shell)
                        shift_obj = shift_qs.last()

                    nozzle_id = source_details.get('nozzle_id')
                    if (category == 'fuel' or matum.mafuta or nozzle_id not in [None, '']):
                        if nozzle_id in [None, '']:
                            raise ValueError('Nozzle is required for fuel expense')

                        pump_qs = fuel_pumps.objects.filter(pk=int(nozzle_id), tank__Interprise__company=kampuni)
                        if shell:
                            pump_qs = pump_qs.filter(tank__Interprise=shell)
                        sh_pump = pump_qs.select_related('tank', 'tank__fuel', 'tank__Interprise').last()

                        if sh_pump:
                            sp_qs = shiftPump.objects.filter(pump=sh_pump)
                            if shift_obj:
                                sp_qs = sp_qs.filter(shift=shift_obj)
                            else:
                                sp_qs = sp_qs.filter(shift__To=None)

                            rec.fromShift = sp_qs.last()
                            rec.fuel_price = Decimal(str(sh_pump.tank.price or 0))
                            rec.fuel_cost = Decimal(str(sh_pump.tank.cost or 0))
                            rec.Fuel = sh_pump.tank.fuel

                            fuel_qty = source_details.get('quantity_litres') or exp.get('quantity_litres')
                            if fuel_qty in [None, '']:
                                if rec.fuel_price and rec.fuel_price > 0:
                                    rec.fuel_qty = amount / rec.fuel_price
                            else:
                                rec.fuel_qty = Decimal(str(fuel_qty))

                            rec.Interprise = sh_pump.tank.Interprise

                    if shift_obj and not rec.fromShift:
                        rec.fromShift = shiftPump.objects.filter(shift=shift_obj).last()
                    if shift_obj and not rec.Interprise:
                        rec.Interprise = shift_obj.record_by.Interprise

                    account_id = source_details.get('account_id')
                    use_account = source_type == 'headOffice' or account_id not in [None, '']
                    if use_account:
                        if account_id in [None, '']:
                            raise ValueError('Payment account is required')

                        acc_qs = PaymentAkaunts.objects.filter(pk=int(account_id), Interprise__company=kampuni)
                        if shell:
                            acc_qs = acc_qs.filter(Interprise=shell)
                        acc = acc_qs.select_related('Interprise').last()
                        if not acc:
                            raise ValueError('Selected payment account is not valid')

                        acc_amount = Decimal(str(acc.Amount or 0))
                        if amount > acc_amount:
                            raise ValueError(f'Insufficient balance in account {acc.Akaunt_name}')

                        rec.akaunti = acc
                        if not rec.Interprise:
                            rec.Interprise = acc.Interprise

                        rec.save()
                        _save_salary_advance_loan(exp, rec, amount, kampuni, shell, useri, category)
                        _apply_salary_last_paid_update(matum, exp, category)
                        _apply_loan_deduction(matum, rec, amount, kampuni)

                        toa = toaCash()
                        toa.Akaunt = acc
                        toa.Amount = amount
                        toa.matumizi = rec
                        toa.before = acc_amount
                        toa.After = acc_amount - amount
                        toa.makato = 0
                        toa.kwenda = matum.matumizi
                        toa.maelezo = f"{matum.matumizi} ({rec.maelezo})"[:500]
                        toa.tarehe = rec_datetime
                        toa.by = useri
                        toa.Interprise = acc.Interprise
                        if not acc.onesha:
                            toa.usiri = True

                        acc.Amount = acc_amount - amount
                        acc.save(update_fields=['Amount'])
                        toa.save()
                        continue

                    if not rec.Interprise:
                        rec.Interprise = shell or matum.shell

                    rec.save()
                    _save_salary_advance_loan(exp, rec, amount, kampuni, shell, useri, category)
                    _apply_salary_last_paid_update(matum, exp, category)
                    _apply_loan_deduction(matum, rec, amount, kampuni)

            return JsonResponse({
                'success':True,
                'message_eng':'Expense was saved successfully',
                'message_swa':'Matumizi yamerekodiwa kikamilifu'
            })
      except Exception as err:
            traceback.print_exc()
            return JsonResponse({
                'success':False,
                'message_eng':f'Expense was not saved: {str(err)}',
                'message_swa':f'Matumizi hayakurekodiwa: {str(err)}'
            })


@login_required(login_url='login')
def addExpenseGroup(request):
    if request.method == "POST":
        try:
            exp_name = request.POST.get('groupName')
            isFuel = int(request.POST.get('isFuel', 0))
            isSupplies = int(request.POST.get('isSupplies', 0))
            isAllowance = int(request.POST.get('isAllowance', 0))
            isBill = int(request.POST.get('isBills', 0))
            billPeriodType = request.POST.get('billPeriodType','')
            billPeriodCount =  int(request.POST.get('billPeriodCount',0)) 

            basic_salary = float(request.POST.get('basic_salary',0))
            salary_payment_source = int(request.POST.get('salary_payment_source',0))
            salary_station = int(request.POST.get('salary_station',0))
            salary_payment_period = int(request.POST.get('salary_payment_period',0))
            salary_last_paid_date = request.POST.get('salary_last_paid_date','')

            billAmount = float(request.POST.get('billAmount',0))
            isRecurringAmount = int(request.POST.get('isRecurringAmount',0))
            lastPaymentDate = request.POST.get('lastPaymentDate','')
            edit = int(request.POST.get('edit',0))
            newTaxGroup = int(request.POST.get('newTaxGroup',0))
            TaxGroup = int(request.POST.get('taxGroup',0))
            TaxGroupName = request.POST.get('TaxGroupName','')
            TaxGroupRate = float(request.POST.get('TaxGroupRate',0))
            attachReceipt = int(request.POST.get('attachReceipt',0))
            todo = todoFunct(request)
            admin = todo['admin']
            useri = todo['useri']
            shell = todo['shell']
            kampuni = todo['kampuni']
            manager = todo['manager']
            
            if useri.admin or manager:
                # Check if expense group already exists
                if matumizi.objects.filter(matumizi__iexact=exp_name, compani=kampuni.id).exists() and not edit:
                    data = {
                        'success': False,
                        'message_eng': 'Expense group with this name already exists',
                        'message_swa': 'Kundi la matumizi lenye jina hili tayari lipo'
                    }
                else:
                    # Create new expense group
                    expTaxGroup = exptaxGroup()
                    if newTaxGroup:
                        expTaxGroup.name = TaxGroupName
                        expTaxGroup.rate = TaxGroupRate
                        expTaxGroup.company = admin.company
                        expTaxGroup.save()
                    else:
                        expTaxGroup = exptaxGroup.objects.get(pk=TaxGroup)

                    matum = matumizi()
                    if edit:
                        matum = matumizi.objects.get(pk=edit, compani=kampuni.id)
                    matum.attachReceipt = attachReceipt
                    matum.taxGroup = expTaxGroup
                   
                    matum.shell = shell
                    matum.matumizi = exp_name
                    matum.mafuta = isFuel
                    matum.attachReceipt = attachReceipt
                    matum.manunuzi = isSupplies
                    matum.bili = isBill
                    matum.posho = isAllowance
                    matum.compani = kampuni
                    # matum.period_type = billPeriodType

                    matum.monthly = billPeriodType == 'Monthly'
                    matum.weekly = billPeriodType == 'Weekly'
                    matum.yearly = billPeriodType == 'Yearly'
                    matum.daily = billPeriodType == 'Daily'

                    if isBill:
                        matum.duration = billPeriodCount
                        matum.last_paid = lastPaymentDate
                        matum.amount = billAmount
                        matum.depends = isRecurringAmount

                    matum.save()
                    
                    data = {
                        'success': True,
                        'message_eng': 'Expense group added successfully',
                        'message_swa': 'Kundi la matumizi limeongezwa kikamilifu',
                        'id': matum.id
                    }
            else:
                data = {
                    'success': False,
                    'message_eng': 'You have no permission to add expense groups',
                    'message_swa': 'Hauna ruhusa ya kuongeza makundi ya matumizi'
                }
            
            return JsonResponse(data)
            
        except Exception as e:
            print(e)
            traceback.print_exc()
            data = {
                'success': False,
                'message_eng': 'Expense group was not added, please try again',
                'message_swa': 'Kundi la matumizi halikuongezwa, tafadhali jaribu tena'
            }
            return JsonResponse(data)
    else:
        return render(request, 'pagenotFound.html', todoFunct(request))


@login_required(login_url='login')
def addTaxGroup(request):
    try:
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        general = todo['general']

        if request.method == "POST":
            name = request.POST.get('TaxGroupName')
            rate = float(request.POST.get('TaxGroupRate', 0))
            edit = int(request.POST.get('edit', 0))

            if not exptaxGroup.objects.filter(name__iexact=name, company=kampuni).exists() or edit:
                tax_group = exptaxGroup()
                if edit:
                    tax_group = exptaxGroup.objects.get(pk=edit, company=kampuni)
                tax_group.name = name
                tax_group.rate = rate
                tax_group.company = kampuni
                tax_group.save()

                data = {
                    'success': True,
                    'message_eng': 'Tax group saved successfully',
                    'message_swa': 'Kundi la ushuru limehifadhiwa kikamilifu',
                    'id': tax_group.id
                }
            else:
                data = {
                    'success': False,
                    'message_eng': 'Tax group with this name already exists',
                    'message_swa': 'Kundi la ushuru lenye jina hili tayari lipo'
                }
            
            return JsonResponse(data)

    except Exception as err:
        print(err)
        traceback.print_exc()
        data = {
            'success': False,
            'message_eng': 'Failed to load tax group data, please try again',
            'message_swa': 'Imeshindikana kupakia taarifa za kundi la ushuru, tafadhali jaribu tena'
        }
        return JsonResponse(data)

@login_required(login_url='login')
def getExpData(request):
    try:
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        general = todo['general']
        shell = todo['shell']
        payacc = todo['payacc']
        useri = todo['useri']

        if not useri.admin or not (useri.ceo and useri.exp): 
            payacc = payacc.filter(Interprise=shell.id,aina='Cash')
        
        # Get expenses
        expenses = matumizi.objects.filter(compani=kampuni).annotate(name=F('matumizi'),ho_fname=F('heo_pay__user__first_name'),ho_lname=F('heo_pay__user__last_name'),
                                                                     sta_fname=F('sta_pay__user__user__first_name'),sta_lname=F('sta_pay__user__user__last_name'))
        # Get payment accounts

        payacc_data = list(payacc.annotate(name=F('Akaunt_name')).values('id', 'name', 'Amount', 'aina'))

        posho_staff = InterprisePermissions.objects.filter(isActive=True).annotate(staff_fname=F('user__user__first_name'), staff_lname=F('user__user__last_name'))
        payee = expenses.filter(Q(sta_pay__isnull=False) | Q(heo_pay__isnull=False),Isactive=True)

        shift_pumps_data = []
        attendants = []
        if not general:
            # expenses = expenses.filter(Q(shell=shell) | Q(general=True))
            # Get pump attendants, pumps and nozzles from shiftPump
            payee = payee.filter(sta_pay__Interprise=shell)
            posho_staff = posho_staff.filter(Interprise=shell.id)
            shf = shifts.objects.filter(To=None, record_by__Interprise=shell)
            attendants = [{'id': s.id,  'name': f'{s.by.user.first_name.capitalize()} {s.by.user.last_name.capitalize()}' if s.by else None} for s in shf]

            shift_pumps = shiftPump.objects.filter(shift__in=shf)
          
            # Group shift pumps by station to create the pump/nozzle structure
            if shift_pumps.exists():
                pumps_dict = {}
                for sp in shift_pumps:
                    station_id = sp.pump.station.id
                    station_name = sp.pump.station.name
                    
                    if station_id not in pumps_dict:
                        pumps_dict[station_id] = {
                            'id': station_id,
                            'name': station_name,
                            'shift': sp.shift.id if sp.shift else None,
                            'nozzles': []
                        }
                    
                    pumps_dict[station_id]['nozzles'].append({
                        'id': sp.pump.id,
                        
                        'name': sp.pump.name,
                        'fuel': sp.pump.tank.fuel.name if sp.pump.tank else None,
                        'price': float(sp.pump.tank.price) if sp.pump.tank else 0
                    })



                shift_pumps_data = list(pumps_dict.values())

      
        
        salary_expenses = []
        for py in payee:
            staff_id = None
            kopesheka = False
            payee_name = 'N/A'

            if py.sta_pay:
                staff_id = py.sta_pay.user.id
                kopesheka = py.sta_pay.user.kopesheka
                payee_name = f'{py.sta_pay.user.user.first_name.capitalize()} {py.sta_pay.user.user.last_name.capitalize()}'
            elif py.heo_pay:
                staff_id = py.heo_pay.id
                kopesheka = py.heo_pay.kopesheka
                payee_name = f'{py.heo_pay.user.first_name.capitalize()} {py.heo_pay.user.last_name.capitalize()}'

            has_loan = False
            loan_amount = 0
            salary_deduction = 0

            if staff_id is not None:
                loan = StaffLoan.objects.filter(staff=staff_id, amount__gt=F('paid_amount')).first()
                if loan:
                    deni = float(loan.amount - loan.paid_amount)
                    makato = float(loan.salary_deduction)
                    has_loan = True
                    loan_amount = deni
                    salary_deduction = makato if deni >= makato else deni

            salary_expenses.append({
                'id': py.id,
               'kopesheka': kopesheka,
                'payee_name': payee_name,
                'staff_id': staff_id,
                'has_loan': has_loan,
                'loan_amount': loan_amount,
                'paid_loan': float(loan.paid_amount) if loan else 0,
                'salary_deduction': salary_deduction,
                'payee_Amount': float(py.amount) 
            })
        
        expenses_data = list(expenses.exclude(paye=True).values('id', 'name','mafuta','bili','posho','manunuzi','discount','amount','depends'))
        
        staff_posho = list(posho_staff.distinct('user').values('user', 'staff_fname', 'staff_lname','Interprise')) 

        data = {
            'success': True,
            'expenses': expenses_data,
            'payment_accounts': payacc_data,
            'shift_pumps': shift_pumps_data,
            'attendants': attendants,
            'staff_posho': staff_posho,
            'salary_expenses': salary_expenses
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        traceback.print_exc()
        data = {
            'success': False,
            'message_eng': 'Failed to retrieve expense data',
            'message_swa': 'Imeshindikana kupata taarifa za matumizi'
        }
        return JsonResponse(data)