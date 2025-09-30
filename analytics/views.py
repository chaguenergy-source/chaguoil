# Create your views here.
from django.shortcuts import render,redirect
from account.models import UserExtend,ToContena,PuList,CustmDebtPayRec,Purchases,saleList,saleOnReceive,toaCash,tr_supervisor,shiftsTime,transFromTo,tankAdjust,adjustments,pumpTemper,PumpStation,notifications,fuelPriceChange,shiftSesion,tankContainer,shiftPump,rekodiMatumizi,attachments,fuelSales,receiveFromTr,TransferFuel,receivedFuel,ReceveFuel,transfer_from,PhoneMailConfirm,wekaCash,shifts,wateja,wasambazaji,fuel,fuel_pumps,fuel_tanks,Interprise,InterprisePermissions,PaymentAkaunts,staff_akaunt_permissions
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
import json

timezone.now()

from datetime import date,timedelta,timezone

from django.core.paginator import Paginator,EmptyPage

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

from account.todos import Todos,confirmMailF,invoCode,TCode

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

      todo = todoFunct(request)
      
      kampuni = todo['kampuni']

      fl = fuel_tanks.objects.filter(Interprise__company=kampuni).annotate(fname=F('fuel__name')).distinct('fuel').values('fuel','fname')

      sale = fuelSales.objects.filter(date__gte=tFr,date__lte=tTo,by__Interprise__company=kampuni).order_by('-pk').annotate(ses=F('session__session__name'),
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
                                                                                                            )
      
      sL = saleList.objects.filter(sale__date__gte=tFr,sale__date__lte=tTo,sale__by__Interprise__company=kampuni).annotate(ses=F('sale__session__session__name'),
                                                                                                                           cust=F('sale__customer'),
                                                                                                                           shell=F('sale__by__Interprise'),
                                                                                                                           date=F('sale__date'),
                                                                                                                           pAtt=F('sale__shiftBy__by'),
                                                                                                                           Tcost=F('cost_sold')*F('qty_sold'),
                                                                                                                           st=F('sale__by__Interprise'),
                                                                                                                          

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
        'success':True
      }
      return JsonResponse(data)
    
    except:
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

      todo = todoFunct(request)
      
      kampuni = todo['kampuni']
      sale = fuelSales.objects.filter(date__gte=tFr,date__lte=tTo,by__Interprise__company=kampuni).annotate(st=F('by__Interprise'))
      saL = saleList.objects.filter(sale__in=sale).annotate(st=F('sale__by__Interprise'),date=F('sale__date'),fuelName=F('theFuel__name'),fuelId=F('theFuel'))
      puch = PuList.objects.filter(pu__date__gte=tFr,pu__date__lte=tTo,pu__vendor__compan=kampuni).annotate(date=F('pu__date'),closed=F('pu__closed'),fuelName=F('Fuel__name'),fuelId=F('Fuel'),st=F('pu__vendor'))
      recv = receivedFuel.objects.filter(receive__date__gte=tFr,receive__date__lte=tTo,receive__by__Interprise__company=kampuni).annotate(st=F('receive__by__Interprise'),date=F('receive__date'),fuelName=F('Fuel__name'),fuelId=F('Fuel'),toTank=F('To__name'))
      trf = transFromTo.objects.filter(transfer__date__gte=tFr,transfer__date__lte=tTo,transfer__record_by__Interprise__company=kampuni).annotate(trFr=F('From__tank'),st=F('transfer__record_by__Interprise'),date=F('transfer__date'),fuelName=F('Fuel__name'),fuelId=F('Fuel'))
      
      expx = rekodiMatumizi.objects.filter(tarehe__gte=tFr,tarehe__lte=tTo,Interprise__company=kampuni).annotate(st=F('Interprise'),tank=F('fromShift__pump__tank'),fuelName=F('Fuel__name'),fuelId=F('Fuel'))
      adj = tankAdjust.objects.filter(adj__tarehe__gte=tFr,adj__tarehe__lte=tTo,adj__by__Interprise__company=kampuni,).order_by('-pk').annotate(st=F('adj__by__Interprise'),date=F('adj__tarehe'),fuelName=F('fuel__name'),fuelId=F('fuel'))
     
      #  get the opening and closing stock from adjustment modal 
      allTanks= fuel_tanks.objects.filter(Interprise__company=kampuni)
      #get opening stock
      StockR = []
      for tk in allTanks:
        tankOp = tankAdjust.objects.filter(adj__tarehe__lt=tFr,adj__by__Interprise__company=kampuni,tank=tk).order_by('-pk').first()
        # tankCl = tankAdjust.objects.filter(adj__tarehe__lte=tTo,adj__by__Interprise__company=kampuni,tank=tk).order_by('-pk').first()
       

        OpnDate = tankOp.adj.tarehe if tankOp else None
        fuelCost = tankOp.cost if tankOp else tk.cost
        
        opening = (tankOp.stick) if tankOp else 0
        closing = 0 
        closingcost = 0

        # print({'opndate':OpnDate,'open':opening})
        if OpnDate:
            #calculate all stock movements from time starting date of the query tFr
            recevd = receivedFuel.objects.filter(receive__date__gt=OpnDate,receive__date__lt=tFr,receive__by__Interprise__company=kampuni,To=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transfr = transFromTo.objects.filter(transfer__date__gte=OpnDate,transfer__date__lt=tFr,transfer__record_by__Interprise__company=kampuni,From__tank=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            trTo = transFromTo.objects.filter(transfer__date__gte=OpnDate,transfer__date__lt=tFr,transfer__record_by__Interprise__company=kampuni,to=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transf = transfr - trTo
            sold = saleList.objects.filter(sale__date__gte=OpnDate,sale__date__lt=tFr,sale__by__Interprise__company=kampuni,tank=tk).aggregate(sumi=Sum('qty_sold'))['sumi'] or 0
            used = rekodiMatumizi.objects.filter(tarehe__gte=OpnDate,tarehe__lt=tFr,Interprise__company=kampuni,fromShift__pump__tank=tk).aggregate(sumi=Sum('fuel_qty'))['sumi'] or 0
            opening = (opening + recevd) - (transf + sold + used)
        else:
          # if there is no opening adjustment get the first tankOp after tFr and all stock movements before tFr
          tankOp = tankAdjust.objects.filter(adj__tarehe__gte=tFr,adj__by__Interprise__company=kampuni,tank=tk).order_by('pk').first()
          opening = 0
          if tankOp:
            OpnDate = tankOp.adj.tarehe
            fuelCost = tankOp.cost
            

            # calculate all stock movements from time starting date of the query tFr to tTo
            recevd = receivedFuel.objects.filter(receive__date__gt=tFr,receive__date__lt=OpnDate,receive__by__Interprise__company=kampuni,To=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transfr = transFromTo.objects.filter(transfer__date__gte=tFr,transfer__date__lt=OpnDate,transfer__record_by__Interprise__company=kampuni,From__tank=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            trTo = transFromTo.objects.filter(transfer__date__gte=tFr,transfer__date__lt=OpnDate,transfer__record_by__Interprise__company=kampuni,to=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transf = transfr - trTo
            sold = saleList.objects.filter(sale__date__gte=tFr,sale__date__lt=OpnDate,sale__by__Interprise__company=kampuni,tank=tk).aggregate(sumi=Sum('qty_sold'))['sumi'] or 0
            used = rekodiMatumizi.objects.filter(tarehe__gte=tFr,tarehe__lt=OpnDate,Interprise__company=kampuni,fromShift__pump__tank=tk).aggregate(sumi=Sum('fuel_qty'))['sumi'] or 0
            opening = (tankOp.stick - recevd) + (transf + sold + used)

            

        tnkClosing = tankAdjust.objects.filter(adj__tarehe__lte=tTo,adj__by__Interprise__company=kampuni,tank=tk).order_by('-pk').first()
        closingDate = tnkClosing.adj.tarehe if tnkClosing else None
        closingcost = tnkClosing.cost if tnkClosing else fuelCost
        # Track if there is any stock movement after the closing date to adjust the closing stock
        if closingDate:
            recevd = receivedFuel.objects.filter(receive__date__gt=closingDate,receive__date__lte=tTo,receive__by__Interprise__company=kampuni,To=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transfr = transFromTo.objects.filter(transfer__date__gt=closingDate,transfer__date__lte=tTo,transfer__record_by__Interprise__company=kampuni,From__tank=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            trTo = transFromTo.objects.filter(transfer__date__gt=closingDate,transfer__date__lte=tTo,transfer__record_by__Interprise__company=kampuni,to=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transf = transfr - trTo
            sold = saleList.objects.filter(sale__date__gt=closingDate,sale__date__lte=tTo,sale__by__Interprise__company=kampuni,tank=tk).aggregate(sumi=Sum('qty_sold'))['sumi'] or 0
            used = rekodiMatumizi.objects.filter(tarehe__gt=closingDate,tarehe__lte=tTo,Interprise__company=kampuni,fromShift__pump__tank=tk).aggregate(sumi=Sum('fuel_qty'))['sumi'] or 0
            closing = (tnkClosing.stick + recevd) - (transf + sold + used)

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
    
    except:
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
  return render(request,'analytics/evaluation.html',todo)

@login_required(login_url='login')
def expensesr(request):
  todo = todoFunct(request)
  kampuni = todo['kampuni']
  fl = fuel_tanks.objects.filter(Interprise__company=kampuni).distinct('fuel')
  staxns = InterprisePermissions.objects.filter(Interprise__company=kampuni, Allow=True).distinct('Interprise')

  todo.update({
    'fl': fl,
    'staxns': staxns,
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
        givenTo = F('kabidhiwa'),
        byFName = F('by__user__first_name'),
        byLname = F('by__user__last_name')
      ).values()

      data = {
        'expenses': list(expenses),
        'success': True
      }
      return JsonResponse(data)
    except Exception:
      data = {'success': False}
      return JsonResponse(data)
  else:
    data = {'success': False}
    return JsonResponse(data)

# function to retrive monthly data for home page
@login_required(login_url='login')
def homePageData(request):
  if request.method == 'POST':
    # try:
      todo = todoFunct(request)
      kampuni = todo['kampuni']
      general = todo['general']

      tFr = request.POST.get('tFr')
      tTo = request.POST.get('tTo')

      # Total Sales for the month
      Sales = fuelSales.objects.filter(
        date__gte=tFr,
        date__lte=tTo,
        by__Interprise__company=kampuni
      ).annotate(due=F('amount') - F('payed'))

      saL = saleList.objects.filter(
        sale__in=Sales
      ).annotate(fuelName=F('theFuel__name'))

      Transf = transFromTo.objects.filter(
        transfer__date__gte=tFr,
        transfer__date__lte=tTo,
        transfer__record_by__Interprise__company=kampuni
      ).annotate(fuelName=F('Fuel__name'))

      Recev = receivedFuel.objects.filter(
        receive__date__gte=tFr,
        receive__date__lte=tTo,
        receive__by__Interprise__company=kampuni
      ).annotate(fuelName=F('Fuel__name'))

      # Total Purchases for the month


      # Total Expenses for the month
      Expenses = rekodiMatumizi.objects.filter(
        tarehe__gte=tFr,
        tarehe__lte=tTo,
        Interprise__company=kampuni
      ).annotate(fuelName=F('Fuel__name'))

      pAtt = fuel_pumps.objects.filter(tank__Interprise__company=kampuni,Incharge__company=kampuni)
      Sess = None

      # priceChange = fuelPriceChange.objects.filter(
      #   date__gte=tFr,
      #   date__lte=tTo,
      #   Interprise__company=kampuni
      # )



      wastage = tankAdjust.objects.filter(
        adj__tarehe__gte=tFr,
        adj__tarehe__lte=tTo,
        adj__by__Interprise__company=kampuni
      ).annotate(fuelName=F('fuel__name'))

      tanks = fuel_tanks.objects.filter(Interprise__company=kampuni).annotate(fuelName=F('fuel__name'))

      # Total Vendor Credits for the month
      Creditors = Purchases.objects.filter(
       
        record_by__company=kampuni,
        payed__lt=F('amount')
      ).annotate(due=F('amount') - F('payed'))

      Debtors = fuelSales.objects.filter(
        by__Interprise__company=kampuni,
        payed__lt=F('amount')
      ).annotate(due=F('amount') - F('payed'))

      if not general:
        shell = todo['shell']
        Sales = Sales.filter(by__Interprise=shell)
        Debtors = Debtors.filter(by__Interprise=shell)
        Expenses = Expenses.filter(Interprise=shell)
        pAtt = pAtt.filter(tank__Interprise=shell)
        
        wastage = wastage.filter(adj__by__Interprise=shell)
        tanks = tanks.filter(Interprise=shell)
        Sess = shiftSesion.objects.filter(session__Interprise=shell,complete=False).annotate(From=F('session__shFrom'),To=F('session__shTo'),shift_name=F('session__name'))
        saL = saL.filter(sale__by__Interprise=shell)

      fuelPrices = fuelPriceChange.objects.filter(Interprise__company=kampuni).order_by('-pk')
      fp = []
      for t in tanks.distinct('fuel'):
        fp.append({
          'fuel':t.fuel.id,
          'fuelName':t.fuel.name,
          'prevCost':fuelPrices.filter(fuel=t.fuel).order_by('-pk').first().Bprice if fuelPrices.filter(fuel=t.fuel).exists() else 0,
          'newCost':t.price if t.price else 0
        })

      StockR = []
      for tk in tanks:
        tankOp = tankAdjust.objects.filter(adj__tarehe__lt=tFr,adj__by__Interprise__company=kampuni,tank=tk).order_by('-pk').first()
        # tankCl = tankAdjust.objects.filter(adj__tarehe__lte=tTo,adj__by__Interprise__company=kampuni,tank=tk).order_by('-pk').first()
       

        OpnDate = tankOp.adj.tarehe if tankOp else None
        fuelCost = tankOp.cost if tankOp else tk.cost
        
        opening = (tankOp.stick) if tankOp else 0
   

        # print({'opndate':OpnDate,'open':opening})
        if OpnDate:
            #calculate all stock movements from time starting date of the query tFr
            recevd = receivedFuel.objects.filter(receive__date__gt=OpnDate,receive__date__lt=tFr,receive__by__Interprise__company=kampuni,To=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transfr = transFromTo.objects.filter(transfer__date__gte=OpnDate,transfer__date__lt=tFr,transfer__record_by__Interprise__company=kampuni,From__tank=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            trTo = transFromTo.objects.filter(transfer__date__gte=OpnDate,transfer__date__lt=tFr,transfer__record_by__Interprise__company=kampuni,to=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transf = transfr - trTo
            sold = saleList.objects.filter(sale__date__gte=OpnDate,sale__date__lt=tFr,sale__by__Interprise__company=kampuni,tank=tk).aggregate(sumi=Sum('qty_sold'))['sumi'] or 0
            used = rekodiMatumizi.objects.filter(tarehe__gte=OpnDate,tarehe__lt=tFr,Interprise__company=kampuni,fromShift__pump__tank=tk).aggregate(sumi=Sum('fuel_qty'))['sumi'] or 0
            opening = (opening + recevd) - (transf + sold + used)
        else:
          # if there is no opening adjustment get the first tankOp after tFr and all stock movements before tFr
          tankOp = tankAdjust.objects.filter(adj__tarehe__gte=tFr,adj__by__Interprise__company=kampuni,tank=tk).order_by('pk').first()
          opening = 0
          if tankOp:
            OpnDate = tankOp.adj.tarehe
            fuelCost = tankOp.cost
            

            # calculate all stock movements from time starting date of the query tFr to tTo
            recevd = receivedFuel.objects.filter(receive__date__gt=tFr,receive__date__lt=OpnDate,receive__by__Interprise__company=kampuni,To=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transfr = transFromTo.objects.filter(transfer__date__gte=tFr,transfer__date__lt=OpnDate,transfer__record_by__Interprise__company=kampuni,From__tank=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            trTo = transFromTo.objects.filter(transfer__date__gte=tFr,transfer__date__lt=OpnDate,transfer__record_by__Interprise__company=kampuni,to=tk).aggregate(sumi=Sum('qty'))['sumi'] or 0
            transf = transfr - trTo
            sold = saleList.objects.filter(sale__date__gte=tFr,sale__date__lt=OpnDate,sale__by__Interprise__company=kampuni,tank=tk).aggregate(sumi=Sum('qty_sold'))['sumi'] or 0
            used = rekodiMatumizi.objects.filter(tarehe__gte=tFr,tarehe__lt=OpnDate,Interprise__company=kampuni,fromShift__pump__tank=tk).aggregate(sumi=Sum('fuel_qty'))['sumi'] or 0
            opening = (tankOp.stick - recevd) + (transf + sold + used)

            

     

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
            'closing':tk.qty,
             
            'OpnDate':OpnDate,
            'OpenCost':fuelCost,
            'CloseCost':tk.cost,
            'st':tk.Interprise.id
            }
          )  


      data = {
          'sale':list(Sales.values()),
          'transf':list(Transf.values()),
          'recev':list(Recev.values()),
          'Creditors':list(Creditors.values()),
          'Debtors':list(Debtors.values()),
          'expenses':list(Expenses.values()),
          'pAtt':list(pAtt.values()),
          'fuelPrice':fp,
          'wastage':list(wastage.values()),
          'tanks':list(tanks.values()),
          'general':general,
          'Sess':list(Sess.values()) if Sess else None,
          'saL':list(saL.values()),
          'success': True,
          'isAdmin':todo['useri'].admin,
          'stock':StockR
      }

      return JsonResponse(data)
    
    # except Exception as e:
    #   print(e)
    #   data = {'success': False}
    #   return JsonResponse(data)