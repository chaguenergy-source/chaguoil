# Create your views here.
from django.shortcuts import render,redirect
from account.models import UserExtend,ToContena,attachments,PuList,CustmDebtPayRec,Purchases,saleList,saleOnReceive,toaCash,tr_supervisor,shiftsTime,transFromTo,tankAdjust,adjustments,pumpTemper,PumpStation,notifications,fuelPriceChange,shiftSesion,tankContainer,shiftPump,rekodiMatumizi,attachments,fuelSales,receiveFromTr,TransferFuel,receivedFuel,ReceveFuel,transfer_from,PhoneMailConfirm,wekaCash,shifts,wateja,wasambazaji,fuel,fuel_pumps,fuel_tanks,Interprise,InterprisePermissions,PaymentAkaunts,staff_akaunt_permissions
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.models import F, Case, When, CharField, DateField
from django.db.models.functions import Coalesce, TruncDate
from django.core import serializers
from django.db.models import Q
# from datetime import datetime
from django.utils import timezone
import json

timezone.now()

from datetime import date,timedelta,timezone

from django.core.paginator import Paginator,EmptyPage

import requests
#Session model stores the session data
from django.contrib.sessions.models import Session
from django.utils.dateparse import parse_date, parse_datetime

import time  
import pytz
import datetime
import re
import traceback
from django.db.models import Sum, Max
import random 
import os

from account.todos import Todos,confirmMailF,invoCode,TCode
from salepurchase.views import _build_daily_sales_days

def todoFunct(request):
  usr = Todos(request)
  return usr.todoF()


@login_required(login_url='login')
def analytics(request):
  todo = todoFunct(request)
  return render(request,'analytics/analytics.html',todo)


@login_required(login_url='login')
def getsaler(request):
  if request.method == 'POST':
    try:
      tFr = request.POST.get('tFr')
      tTo = request.POST.get('tTo')

      # Frontend sends ISO datetime (e.g. 2026-06-01T00:00:00+03:00).
      # shiftSesion.date is DateField, so convert to date boundaries first.
      tFr_date = parse_date((tFr or '').split('T')[0])
      tTo_date = parse_date((tTo or '').split('T')[0])
      if not tFr_date or not tTo_date:
        tFr_dt = parse_datetime(tFr or '')
        tTo_dt = parse_datetime(tTo or '')
        tFr_date = tFr_date or (tFr_dt.date() if tFr_dt else None)
        tTo_date = tTo_date or (tTo_dt.date() if tTo_dt else None)

      if not tFr_date or not tTo_date:
        return JsonResponse({
          'success': False,
          'swa': 'Muda uliowekwa si sahihi',
          'eng': 'Invalid date range format'
        })

      todo = todoFunct(request)
      
      kampuni = todo['kampuni']
      shell = todo['shell']
      useri = todo['useri']

      daily_sales = _build_daily_sales_days(
        kampuni, shell, useri, tFr_date, tTo_date, tFr, tTo
      )

      fl = fuel_tanks.objects.filter(Interprise__company=kampuni).annotate(fname=F('fuel__name')).distinct('fuel').values('fuel','fname')

      sale = fuelSales.objects.filter(shiftBy__session__date__gte=tFr_date,shiftBy__session__date__lte=tTo_date,by__Interprise__company=kampuni,mobile_pay=False).order_by('-pk').annotate(ses=F('session__session__name'),
                                                                                                            pAtt=F('shiftBy__by'),
                                                                                                            shCode = F('shiftBy__code'),
                                                                                                            cust=F('customer'),
                                                                                                            custAddr=F('customer__address'),
                                                                                                            custN=F('customer__jina'),
                                                                                                            due=F('amount')-F('payed'),
                                                                                                            shell=F('by__Interprise'),
                                                                                                             pAtt_fname=F('shiftBy__by__user__first_name'),
                                                                                                             pAtt_lname=F('shiftBy__by__user__last_name'),
                                                                                                             st=F('by__Interprise'),
                                                                                                             stName=F('by__Interprise__name'),
                                                                                                             byFn=F('by__user__user__first_name'),
                                                                                                             byLn=F('by__user__user__last_name'),
                                                                                                             sesDate = F('shiftBy__session__date')
                                                                                                            )
      
      sL = saleList.objects.filter(sale__shiftBy__session__date__gte=tFr_date,sale__shiftBy__session__date__lte=tTo_date,sale__by__Interprise__company=kampuni,sale__mobile_pay=False).annotate(ses=F('sale__shiftBy__session__session__name'),
                                                                                                                           cust=F('sale__customer'),
                                                                                                                           shell=F('sale__by__Interprise'),
                                                                                                                           date=F('sale__date'),
                                                                                                                           pAtt=F('sale__shiftBy__by'),
                                                                                                                           Tcost=F('cost_sold')*F('qty_sold'),
                                                                                                                           st=F('sale__by__Interprise'),
                                                                                                                           sesDate=F('sale__shiftBy__session__date') 

                                                                                                                           )
      
      pay = wekaCash.objects.filter(tarehe__gte=tFr,tarehe__lte=tTo,Interprise__company=kampuni).exclude(customer=None,shift=None).order_by('pk').annotate(ses=F('shift__session__session__name'),
                                                                                                                               cust=F('customer'),
                                                                                                                               date = F('tarehe'),
                                                                                                                               pAtt=F('shift__by'),
                                                                                                                               accauntN=F('Akaunt__Akaunt_name'),
                                                                                                                               acc=F('Akaunt'),
                                                                                                                               accAmo=F('Akaunt__Amount'),
                                                                                                                               st=F('Interprise'),
                                                                                                                               stName=F('Interprise__name'),
                                                                                                                               custN=F('customer__jina'),
                                                                                                                               pAtt_fname=F('shift__by__user__first_name'),
                                                                                                                               pAtt_lname=F('shift__by__user__last_name'),
                                                                                                                               rem=F('tDebt')-F('Amount'),
                                                                                                                               sh=F('shift'),
                                                                                                                               shcode = F('shift__code'),
                                                                                                                               shfr = F('shift__From'),
                                                                                                                               shto = F('shift__To'),
                                                                                                                               shAmo = F('shift__amount'),
                                                                                                                               shPaid = F('shift__paid')
                                                                                                                               )
      custPayRec =   CustmDebtPayRec.objects.filter(pay__tarehe__gte=tFr,pay__tarehe__lte=tTo,pay__Interprise__company=kampuni).annotate(date=F('pay__tarehe'),
                                                                                                                                         st=F('pay__Interprise'),
                                                                                                                                         py = F('pay'),
                                                                                                                                         invoAmo = F('sale__amount'),
                                                                                                                                         invoPaid = F('sale__payed'),
                                                                                                                                         postDue = F('sale__payed')-F('Apay'),
                                                                                                                                         invoCode=F('sale__code'),
                                                                                                                                         invoDate = F('sale__recDate'),
                                                                                                                                         due = F('sale__amount') - F('sale__payed')
                                                                                                                                         )
      data = {
        'sale':list(sale.values()),
        'saL':list(sL.values()),
        'pay':list(pay.values()),
        'fuel':list(fl),
        'payRec':list(custPayRec.values()),
        'dailySales': daily_sales,
        'success':True
      }
      return JsonResponse(data)
    
    except:
      traceback.print_exc()
      data = {'success':False}
      return JsonResponse(data)
  else:
    data = {'success':False}
    return JsonResponse(data)
  
@login_required(login_url='login')
def getEvaluation(request):
  if request.method == 'POST':
    try:
      tFr = request.POST.get('tFr')
      tTo = request.POST.get('tTo')

      tFr_date = parse_date((tFr or '').split('T')[0])
      tTo_date = parse_date((tTo or '').split('T')[0])
      if not tFr_date or not tTo_date:
        tFr_dt = parse_datetime(tFr or '')
        tTo_dt = parse_datetime(tTo or '')
        tFr_date = tFr_date or (tFr_dt.date() if tFr_dt else None)
        tTo_date = tTo_date or (tTo_dt.date() if tTo_dt else None)

      if not tFr_date or not tTo_date:
        return JsonResponse({'success': False})

      todo = todoFunct(request)
      kampuni = todo['kampuni']

      sale = fuelSales.objects.filter(
        shiftBy__session__date__gte=tFr_date,
        shiftBy__session__date__lte=tTo_date,
        by__Interprise__company=kampuni,
        mobile_pay=False,
        shiftBy__isnull=False,
      ).annotate(
        st=F('by__Interprise'),
        sesDate=F('shiftBy__session__date'),
      )

      saL = saleList.objects.filter(
        sale__shiftBy__session__date__gte=tFr_date,
        sale__shiftBy__session__date__lte=tTo_date,
        sale__by__Interprise__company=kampuni,
        sale__mobile_pay=False,
        sale__shiftBy__isnull=False,
      ).annotate(
        st=F('sale__by__Interprise'),
        sesDate=F('sale__shiftBy__session__date'),
        fuelName=F('theFuel__name'),
        fuelId=F('theFuel'),
      )

      puch = PuList.objects.filter(
        pu__date__gte=tFr,
        pu__date__lte=tTo,
        pu__vendor__compan=kampuni,
      ).annotate(
        date=F('pu__date'),
        closed=F('pu__closed'),
        fuelName=F('Fuel__name'),
        fuelId=F('Fuel'),
        st=F('pu__vendor'),
      )

      recv = receivedFuel.objects.filter(
        receive__by__Interprise__company=kampuni,
      ).filter(
        Q(receive__ses__date__gte=tFr_date, receive__ses__date__lte=tTo_date) |
        Q(receive__ses__isnull=True, receive__date__gte=tFr, receive__date__lte=tTo)
      ).annotate(
        st=F('receive__by__Interprise'),
        sesDate=Coalesce(F('receive__ses__date'), TruncDate('receive__date'), output_field=DateField()),
        fuelName=F('Fuel__name'),
        fuelId=F('Fuel'),
        toTank=F('To__name'),
      )

      trf = transFromTo.objects.filter(
        transfer__record_by__Interprise__company=kampuni,
      ).filter(
        Q(shift__shift__session__date__gte=tFr_date, shift__shift__session__date__lte=tTo_date) |
        Q(shift__isnull=True, transfer__date__gte=tFr, transfer__date__lte=tTo)
      ).annotate(
        trFr=F('From__tank'),
        st=F('transfer__record_by__Interprise'),
        sesDate=Coalesce(F('shift__shift__session__date'), TruncDate('transfer__date'), output_field=DateField()),
        fuelName=F('Fuel__name'),
        fuelId=F('Fuel'),
      )

      expx = rekodiMatumizi.objects.filter(
        Interprise__company=kampuni,
      ).filter(
        Q(fromShift__shift__session__date__gte=tFr_date, fromShift__shift__session__date__lte=tTo_date) |
        Q(fromShift__isnull=True, tarehe__gte=tFr, tarehe__lte=tTo)
      ).annotate(
        st=F('Interprise'),
        tank=F('fromShift__pump__tank'),
        fuelName=F('Fuel__name'),
        fuelId=F('Fuel'),
        sesDate=Coalesce(F('fromShift__shift__session__date'), TruncDate('tarehe'), output_field=DateField()),
      )

      adj = tankAdjust.objects.filter(
        adj__tarehe__gte=tFr,
        adj__tarehe__lte=tTo,
        adj__by__Interprise__company=kampuni,
      ).order_by('-pk').annotate(
        st=F('adj__by__Interprise'),
        date=F('adj__tarehe'),
        fuelName=F('fuel__name'),
        fuelId=F('fuel'),
        stock_reconcile=F('adj__stock_reconcile'),
      )
     
      def _as_date(val):
        if val is None:
          return None
        return val.date() if hasattr(val, 'date') and callable(val.date) else val

      def _fqty(val):
        return float(val or 0)

      def _aware_date(val, end=False):
        if val is None:
          return None
        d = _as_date(val)
        from datetime import datetime as dt_cls, time as dt_time
        from django.utils import timezone as dj_tz
        t = dt_time.max if end else dt_time.min
        return dj_tz.make_aware(dt_cls.combine(d, t))

      def _stock_recv_sum(tank, date_from, date_to, use_lte=False):
        q_ses = Q(receive__ses__isnull=False, To=tank)
        if date_from is not None:
          q_ses &= Q(receive__ses__date__gt=date_from)
        if date_to is not None:
          q_ses &= Q(receive__ses__date__lte=date_to) if use_lte else Q(receive__ses__date__lt=date_to)
        ses_sum = receivedFuel.objects.filter(
          q_ses, receive__by__Interprise__company=kampuni
        ).aggregate(sumi=Sum('qty'))['sumi'] or 0
        q_dt = Q(receive__ses__isnull=True, To=tank)
        if date_from is not None:
          q_dt &= Q(receive__date__gt=_aware_date(date_from))
        if date_to is not None:
          q_dt &= Q(receive__date__lte=_aware_date(date_to, end=True)) if use_lte else Q(receive__date__lt=_aware_date(date_to))
        dt_sum = receivedFuel.objects.filter(
          q_dt, receive__by__Interprise__company=kampuni
        ).aggregate(sumi=Sum('qty'))['sumi'] or 0
        return float(ses_sum) + float(dt_sum)

      def _stock_trf_out_sum(tank, date_from, date_to, use_lte=False):
        q = Q(From__tank=tank, transfer__record_by__Interprise__company=kampuni)
        q_ses = q & Q(shift__isnull=False)
        q_dt = q & Q(shift__isnull=True)
        if date_from is not None:
          q_ses &= Q(shift__shift__session__date__gte=date_from)
          q_dt &= Q(transfer__date__gte=_aware_date(date_from))
        if date_to is not None:
          if use_lte:
            q_ses &= Q(shift__shift__session__date__lte=date_to)
            q_dt &= Q(transfer__date__lte=_aware_date(date_to, end=True))
          else:
            q_ses &= Q(shift__shift__session__date__lt=date_to)
            q_dt &= Q(transfer__date__lt=_aware_date(date_to))
        return float(transFromTo.objects.filter(q_ses).aggregate(sumi=Sum('qty'))['sumi'] or 0) + float(transFromTo.objects.filter(q_dt).aggregate(sumi=Sum('qty'))['sumi'] or 0)

      def _stock_trf_in_sum(tank, date_from, date_to, use_lte=False):
        q = Q(to=tank, transfer__record_by__Interprise__company=kampuni)
        q_ses = q & Q(shift__isnull=False)
        q_dt = q & Q(shift__isnull=True)
        if date_from is not None:
          q_ses &= Q(shift__shift__session__date__gte=date_from)
          q_dt &= Q(transfer__date__gte=_aware_date(date_from))
        if date_to is not None:
          if use_lte:
            q_ses &= Q(shift__shift__session__date__lte=date_to)
            q_dt &= Q(transfer__date__lte=_aware_date(date_to, end=True))
          else:
            q_ses &= Q(shift__shift__session__date__lt=date_to)
            q_dt &= Q(transfer__date__lt=_aware_date(date_to))
        return float(transFromTo.objects.filter(q_ses).aggregate(sumi=Sum('qty'))['sumi'] or 0) + float(transFromTo.objects.filter(q_dt).aggregate(sumi=Sum('qty'))['sumi'] or 0)

      def _stock_sold_sum(tank, date_from, date_to, use_lte=False):
        q = Q(tank=tank, sale__by__Interprise__company=kampuni, sale__mobile_pay=False, sale__shiftBy__isnull=False)
        if date_from is not None:
          q &= Q(sale__shiftBy__session__date__gte=date_from)
        if date_to is not None:
          q &= Q(sale__shiftBy__session__date__lte=date_to) if use_lte else Q(sale__shiftBy__session__date__lt=date_to)
        return float(saleList.objects.filter(q).aggregate(sumi=Sum('qty_sold'))['sumi'] or 0)

      def _stock_used_sum(tank, date_from, date_to, use_lte=False):
        q_ses = Q(fromShift__pump__tank=tank, Interprise__company=kampuni, fromShift__isnull=False)
        if date_from is not None:
          q_ses &= Q(fromShift__shift__session__date__gte=date_from)
        if date_to is not None:
          q_ses &= Q(fromShift__shift__session__date__lte=date_to) if use_lte else Q(fromShift__shift__session__date__lt=date_to)
        return float(rekodiMatumizi.objects.filter(q_ses).aggregate(sumi=Sum('fuel_qty'))['sumi'] or 0)

      #  get the opening and closing stock from adjustment modal 
      allTanks= fuel_tanks.objects.filter(Interprise__company=kampuni)
      #get opening stock
      StockR = []
      for tk in allTanks:
        tankOp = tankAdjust.objects.filter(adj__tarehe__lt=tFr,adj__by__Interprise__company=kampuni,tank=tk).order_by('-pk').first()
        # tankCl = tankAdjust.objects.filter(adj__tarehe__lte=tTo,adj__by__Interprise__company=kampuni,tank=tk).order_by('-pk').first()
       

        OpnDate = tankOp.adj.tarehe if tankOp else None
        opn_date = _as_date(OpnDate)
        fuelCost = tankOp.cost if tankOp else tk.cost
        
        opening = _fqty(tankOp.stick) if tankOp else 0
        closing = 0
        closingcost = 0

        # print({'opndate':OpnDate,'open':opening})
        if OpnDate:
            #calculate all stock movements from time starting date of the query tFr
            recevd = _stock_recv_sum(tk, opn_date, tFr_date)
            transfr = _stock_trf_out_sum(tk, opn_date, tFr_date)
            trTo = _stock_trf_in_sum(tk, opn_date, tFr_date)
            transf = transfr - trTo
            sold = _stock_sold_sum(tk, opn_date, tFr_date)
            used = _stock_used_sum(tk, opn_date, tFr_date)
            opening = (opening + recevd) - (transf + sold + used)
        else:
          # if there is no opening adjustment get the first tankOp after tFr and all stock movements before tFr
          tankOp = tankAdjust.objects.filter(adj__tarehe__gte=tFr,adj__by__Interprise__company=kampuni,tank=tk).order_by('pk').first()
          opening = 0
          if tankOp:
            OpnDate = tankOp.adj.tarehe
            opn_date = _as_date(OpnDate)
            fuelCost = tankOp.cost
            

            # calculate all stock movements from time starting date of the query tFr to tTo
            recevd = _stock_recv_sum(tk, tFr_date, opn_date)
            transfr = _stock_trf_out_sum(tk, tFr_date, opn_date)
            trTo = _stock_trf_in_sum(tk, tFr_date, opn_date)
            transf = transfr - trTo
            sold = _stock_sold_sum(tk, tFr_date, opn_date)
            used = _stock_used_sum(tk, tFr_date, opn_date)
            opening = (_fqty(tankOp.stick) - recevd) + (transf + sold + used)

            

        tnkClosing = tankAdjust.objects.filter(adj__tarehe__lte=tTo,adj__by__Interprise__company=kampuni,tank=tk).order_by('-pk').first()
        closingDate = tnkClosing.adj.tarehe if tnkClosing else None
        closing_date = _as_date(closingDate)
        closingcost = tnkClosing.cost if tnkClosing else fuelCost
        # Track if there is any stock movement after the closing date to adjust the closing stock
        if closingDate:
            recevd = _stock_recv_sum(tk, closing_date, tTo_date, use_lte=True)
            transfr = _stock_trf_out_sum(tk, closing_date, tTo_date, use_lte=True)
            trTo = _stock_trf_in_sum(tk, closing_date, tTo_date, use_lte=True)
            transf = transfr - trTo
            sold = _stock_sold_sum(tk, closing_date, tTo_date, use_lte=True)
            used = _stock_used_sum(tk, closing_date, tTo_date, use_lte=True)
            closing = (_fqty(tnkClosing.stick) + recevd) - (transf + sold + used)

            # print({'tank':tk.name,'recv':recevd,'opening':tnkClosing.stick,'transf':transf,'sold':sold,'used':used,'opening':opening,'closing':closing,'closingPrice':closingcost})






        

        StockR.append(
          {
            'tank':tk.id,
            'TankName':tk.name,
            'fuelName':tk.fuel.name,
            'stationId':tk.Interprise.id,
            'stationName':tk.Interprise.name,
            'fuel':tk.fuel.id,
            'opening':opening,
            'closing':closing,
            'tFr':tFr,
            'tTo':tTo,
            'OpnDate':OpnDate,
            'OpenCost':fuelCost,
            'CloseCost':closingcost,
            'st':tk.Interprise.id
            }
          )
      
      data = {
        'sale':list(sale.values()),
        'puch':list(puch.values()),
        'recv':list(recv.values()),
        'trf':list(trf.values()),
        'expx':list(expx.values()),
        'adj':list(adj.values()),
        'saL':list(saL.values()),
        'success':True,
        'stock':StockR
      }
      return JsonResponse(data)
    
    except Exception:
      traceback.print_exc()
      data = {'success':False}
      return JsonResponse(data)
  else:
    data = {'success':False}
    return JsonResponse(data)
  

@login_required(login_url='login')
def salesr(request):
  todo = todoFunct(request)
  kampuni = todo['kampuni']
  fl = fuel_tanks.objects.filter(Interprise__company=kampuni).distinct('fuel')
  staxns = InterprisePermissions.objects.filter(Interprise__company=kampuni,Allow=True).distinct('Interprise')
  sexns = shiftsTime.objects.filter(Interprise__company=kampuni).distinct('name')
  attends = InterprisePermissions.objects.filter(Interprise__company=kampuni,pumpIncharge=True)

  todo.update({
    'fl':fl,
    'staxns':staxns,
    'sexns':sexns,
    'attends':attends
  })
  return render(request,'analytics/salesr.html',todo)

@login_required(login_url='login')
def evaluationr(request):
  todo = todoFunct(request)
  kampuni = todo['kampuni']
  fl = fuel_tanks.objects.filter(Interprise__company=kampuni).distinct('fuel')
  staxns = InterprisePermissions.objects.filter(Interprise__company=kampuni,Allow=True).distinct('Interprise')

  todo.update({
    'fl':fl,
    'staxns':staxns,
   
  })
  return render(request,'analytics/evaluation.html',todo) # this is the view for evaluation report which is used to evaluate the performance of the station by looking at the stock movements, sales and expenses in a given period. it will be used to make decision on how to improve the performance of the station and also to identify any issues that may be affecting the performance of the station. it will also be used to compare the performance of different stations and to identify any best practices that can be shared among the stations.

@login_required(login_url='login')
def expensesr(request):
  todo = todoFunct(request)
  kampuni = todo['kampuni']
  fl = fuel_tanks.objects.filter(Interprise__company=kampuni).distinct('fuel')
  staxns = InterprisePermissions.objects.filter(Interprise__company=kampuni, Allow=True).distinct('Interprise')


  # allRec = rekodiMatumizi.objects.filter(Interprise__company=kampuni.id)
  # for rc in allRec:
  #     rekodiMatumizi.objects.filter(pk=rc.id).update(tax_group=rc.matumizi.taxGroup)
  

  todo.update({
    'fl': fl,
    'staxns': staxns,
    'isExpRep':True
  })
  return render(request, 'analytics/expenser.html', todo)

@login_required(login_url='login')
def getExpenses(request):
  if request.method == 'POST':
    try:
      tFr = request.POST.get('tFr')
      tTo = request.POST.get('tTo')

      todo = todoFunct(request)
      kampuni = todo['kampuni']

      expenses = rekodiMatumizi.objects.filter(
        tarehe__gte=tFr,
        tarehe__lte=tTo,
        Interprise__company=kampuni
      ).annotate(
        st=F('Interprise'),
        tank=F('fromShift__pump__tank'),
        pump=F('fromShift__pump'),
        shift=F('fromShift'),
        fuelName=F('fromShift__Fuel__name'),
        stationName=F('Interprise__name'),
        expN = F('matumizi__matumizi'),
        expId = F('matumizi__id'),
        salary = F('matumizi__paye'),
        posho = F('matumizi__posho'),
        mafuta = F('matumizi__mafuta'),
        manunuzi = F('matumizi__manunuzi'),
        givenTo = F('kabidhiwa'),
        tinNumber = Case(
          When(staff__isnull=True, then=F('tin_number')),
          default=F('staff__tin'),
          output_field=CharField()
        ),
        byFName = F('by__user__first_name'),
        byLname = F('by__user__last_name'),
        staffId = F('staff__id'),
        staffFName = F('staff__user__first_name'),
        staffLName = F('staff__user__last_name'),
        dateRec=F('matumiziDeti__date'),
        tax=F('tax_group'),
        taxGroup=F('tax_group__name')
      ).values()
      
      attach = []
      exp_ids = [e.get('id') for e in expenses if e.get('id')]
      attachm = attachments.objects.filter(
        expAttach_id__in=exp_ids,
        expAttach__isnull=False,
      ).exclude(file='').select_related(
        'expAttach',
        'expAttach__matumizi',
        'expAttach__matumizi__taxGroup',
      )
      for a in attachm:
        exp_row = a.expAttach
        matumizi = exp_row.matumizi if exp_row else None
        tax_group = matumizi.taxGroup if matumizi else None
        attach.append({
          'rekodiMatumizi': exp_row.id if exp_row else None,
          'date': exp_row.tarehe.isoformat() if exp_row and exp_row.tarehe else None,
          'matumizi': matumizi.id if matumizi else None,
          'expId': matumizi.id if matumizi else None,
          'expN': matumizi.matumizi if matumizi else '',
          'salary': bool(matumizi.paye) if matumizi else False,
          'kiasi': float(exp_row.kiasi or 0) if exp_row else 0,
          'tax': tax_group.id if tax_group else None,
          'taxGroup': tax_group.name if tax_group else '',
          'file': request.build_absolute_uri(a.file.url) if a.file else None,
          'attach_name': a.attach_name or '',
        })

      data = {
        'expenses': list(expenses),
        'attachments': attach,
        'success': True
      }
      return JsonResponse(data)
    except Exception:
      data = {'success': False}
      traceback.print_exc() 
      return JsonResponse(data)
  else:
      data = {'success': False}
      return JsonResponse(data)

def _sum_by_tank(qs, group_field, sum_field='qty'):
  rows = qs.values(group_field).annotate(total=Sum(sum_field))
  return {row[group_field]: float(row['total'] or 0) for row in rows if row[group_field] is not None}


def _build_dashboard_stock(tanks_qs, kampuni, tFr, tTo, shell_id=None):
  """Opening at tFr from current qty + batched period movements (fixed query count)."""
  tank_list = list(tanks_qs.select_related('fuel', 'Interprise'))
  if not tank_list:
    return []

  tank_ids = [t.id for t in tank_list]
  recv_q = receivedFuel.objects.filter(
    receive__date__gte=tFr, receive__date__lte=tTo,
    receive__by__Interprise__company=kampuni, To_id__in=tank_ids,
  )
  sold_q = saleList.objects.filter(
    sale__date__gte=tFr, sale__date__lte=tTo,
    sale__by__Interprise__company=kampuni, tank_id__in=tank_ids, sale__mobile_pay=False,
  )
  wast_q = tankAdjust.objects.filter(
    adj__tarehe__gte=tFr, adj__tarehe__lte=tTo,
    adj__by__Interprise__company=kampuni, adj__stock_reconcile=False, tank_id__in=tank_ids,
  )
  trf_out_q = transFromTo.objects.filter(
    transfer__date__gte=tFr, transfer__date__lte=tTo,
    transfer__record_by__Interprise__company=kampuni, From__tank_id__in=tank_ids,
  )
  trf_in_q = transFromTo.objects.filter(
    transfer__date__gte=tFr, transfer__date__lte=tTo,
    transfer__record_by__Interprise__company=kampuni, to_id__in=tank_ids,
  )
  used_q = rekodiMatumizi.objects.filter(
    tarehe__gte=tFr, tarehe__lte=tTo, Interprise__company=kampuni,
    fromShift__pump__tank_id__in=tank_ids,
  )
  if shell_id:
    recv_q = recv_q.filter(receive__by__Interprise_id=shell_id)
    sold_q = sold_q.filter(sale__by__Interprise_id=shell_id)
    wast_q = wast_q.filter(adj__by__Interprise_id=shell_id)
    trf_out_q = trf_out_q.filter(transfer__record_by__Interprise_id=shell_id)
    trf_in_q = trf_in_q.filter(transfer__record_by__Interprise_id=shell_id)
    used_q = used_q.filter(Interprise_id=shell_id)

  recv_map = _sum_by_tank(recv_q, 'To_id')
  sold_map = _sum_by_tank(sold_q, 'tank_id', 'qty_sold')
  wast_map = _sum_by_tank(wast_q, 'tank_id', 'diff')
  trf_out_map = _sum_by_tank(trf_out_q, 'From__tank_id')
  trf_in_map = _sum_by_tank(trf_in_q, 'to_id')
  used_map = _sum_by_tank(used_q, 'fromShift__pump__tank_id', 'fuel_qty')

  stock_rows = []
  for tk in tank_list:
    recv = recv_map.get(tk.id, 0)
    sold = sold_map.get(tk.id, 0)
    wast = wast_map.get(tk.id, 0)
    tr_out = trf_out_map.get(tk.id, 0)
    tr_in = trf_in_map.get(tk.id, 0)
    used = used_map.get(tk.id, 0)
    closing = float(tk.qty or 0)
    opening = closing - recv - wast + sold + tr_out - tr_in + used
    stock_rows.append({
      'tank': tk.id,
      'TankName': tk.name,
      'fuelName': tk.fuel.name,
      'stationId': tk.Interprise_id,
      'stationName': tk.Interprise.name,
      'fuel': tk.fuel_id,
      'opening': opening,
      'closing': closing,
      'OpenCost': float(tk.cost or 0),
      'CloseCost': float(tk.cost or 0),
      'st': tk.Interprise_id,
    })
  return stock_rows


def _build_fuel_prices(tanks_qs, kampuni):
  tank_fuels = list(tanks_qs.select_related('fuel').order_by('fuel_id', 'id').distinct('fuel_id'))
  if not tank_fuels:
    return []
  fuel_ids = [t.fuel_id for t in tank_fuels]
  latest_pks = fuelPriceChange.objects.filter(
    Interprise__company=kampuni, fuel_id__in=fuel_ids,
  ).values('fuel_id').annotate(max_pk=Max('pk'))
  pk_list = [row['max_pk'] for row in latest_pks if row['max_pk']]
  prev_map = {
    p.fuel_id: float(p.Bprice or 0)
    for p in fuelPriceChange.objects.filter(pk__in=pk_list).only('fuel_id', 'Bprice')
  }
  return [{
    'fuel': t.fuel_id,
    'fuelName': t.fuel.name,
    'prevCost': prev_map.get(t.fuel_id, 0),
    'newCost': float(t.price or 0),
  } for t in tank_fuels]


# function to retrive monthly data for home page
@login_required(login_url='login')
def homePageData(request):
  if request.method == 'POST':
    try:
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        general = todo['general']

        tFr = request.POST.get('tFr')
        tTo = request.POST.get('tTo')
        shell_id = None

        Sales = fuelSales.objects.filter(
          date__gte=tFr,
          date__lte=tTo,
          by__Interprise__company=kampuni,
          mobile_pay=False,
        )

        saL = saleList.objects.filter(
          sale__date__gte=tFr,
          sale__date__lte=tTo,
          sale__by__Interprise__company=kampuni,
          sale__mobile_pay=False,
        ).annotate(fuelName=F('theFuel__name'))

        Transf = transFromTo.objects.filter(
          transfer__date__gte=tFr,
          transfer__date__lte=tTo,
          transfer__record_by__Interprise__company=kampuni,
        ).annotate(fuelName=F('Fuel__name'))

        Recev = receivedFuel.objects.filter(
          receive__date__gte=tFr,
          receive__date__lte=tTo,
          receive__by__Interprise__company=kampuni,
        ).annotate(fuelName=F('Fuel__name'))

        Expenses = rekodiMatumizi.objects.filter(
          tarehe__gte=tFr,
          tarehe__lte=tTo,
          Interprise__company=kampuni,
        ).annotate(fuelName=F('Fuel__name'))

        pAtt = fuel_pumps.objects.filter(
          tank__Interprise__company=kampuni, Incharge__company=kampuni,
        )
        Sess = None

        wastage = tankAdjust.objects.filter(
          adj__tarehe__gte=tFr,
          adj__tarehe__lte=tTo,
          adj__by__Interprise__company=kampuni,
          adj__stock_reconcile=False,
        ).annotate(fuelName=F('fuel__name'), qty=F('diff'))

        tanks = fuel_tanks.objects.filter(Interprise__company=kampuni)

        Creditors = Purchases.objects.filter(
          record_by__company=kampuni,
          payed__lt=F('amount'),
        ).values('vendor_id').annotate(due=Sum(F('amount') - F('payed'))).filter(due__gt=0)

        Debtors = fuelSales.objects.filter(
          by__Interprise__company=kampuni,
          payed__lt=F('amount'),
          customer__isnull=False,
          mobile_pay=False,
        ).values('customer_id').annotate(due=Sum(F('amount') - F('payed'))).filter(due__gt=0)

        if not general:
          shell = todo['shell']
          shell_id = shell.id
          Sales = Sales.filter(by__Interprise=shell)
          Debtors = Debtors.filter(by__Interprise=shell)
          Expenses = Expenses.filter(Interprise=shell)
          pAtt = pAtt.filter(tank__Interprise=shell)
          wastage = wastage.filter(adj__by__Interprise=shell)
          tanks = tanks.filter(Interprise=shell)
          Transf = Transf.filter(transfer__record_by__Interprise=shell)
          Recev = Recev.filter(receive__by__Interprise=shell)
          saL = saL.filter(sale__by__Interprise=shell)
          Sess = shiftSesion.objects.filter(
            session__Interprise=shell, complete=False,
          ).annotate(
            From=F('session__shFrom'), To=F('session__shTo'), shift_name=F('session__name'),
          )

        fp = _build_fuel_prices(tanks, kampuni)
        StockR = _build_dashboard_stock(tanks, kampuni, tFr, tTo, shell_id)

        data = {
            'sale': list(Sales.values('amount', 'payed')),
            'transf': list(Transf.values('fuelName', 'qty')),
            'recev': list(Recev.values('fuelName', 'qty')),
            'Creditors': list(Creditors),
            'Debtors': list(Debtors),
            'expenses': list(Expenses.values('fuel_qty', 'kiasi', 'fuelName')),
            'pAtt': list(pAtt.values('Incharge_id')),
            'fuelPrice': fp,
            'wastage': list(wastage.values('fuelName', 'qty', 'diff')),
            'general': general,
            'Sess': list(Sess.values()) if Sess else None,
            'saL': list(saL.values('fuelName', 'qty_sold')),
            'success': True,
            'isAdmin': todo['useri'].admin,
            'stock': StockR,
        }

        return JsonResponse(data)
    
    except Exception as e:
      traceback.print_exc()
      data = {'success': False}
      return JsonResponse(data)