
# Create your views here.
from django.shortcuts import render,redirect
from account.models import UserExtend,ToContena,PuList,Purchases,creditDebtOrder,CustmDebtPayRec,saleList,saleOnReceive,toaCash,tr_supervisor,shiftsTime,transFromTo,tankAdjust,adjustments,pumpTemper,PumpStation,notifications,fuelPriceChange,shiftSesion,tankContainer,shiftPump,rekodiMatumizi,attachments,fuelSales,receiveFromTr,TransferFuel,receivedFuel,ReceveFuel,transfer_from,PhoneMailConfirm,wekaCash,shifts,wateja,wasambazaji,fuel,fuel_pumps,fuel_tanks,Interprise,InterprisePermissions,PaymentAkaunts,staff_akaunt_permissions
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
from django.conf import settings


from account.todos import Todos,confirmMailF,invoCode,TCode
from django.views.decorators.http import require_POST
import json
def todoFunct(request):
  usr = Todos(request)
  return usr.todoF()


@login_required(login_url='login')
def customers(request):
  todo = todoFunct(request)
  cust = todo['customers']
  general = todo['general']
  wateja = []
  madeni = 0
  for c in cust:
      denitr = fuelSales.objects.filter(customer=c.id,amount__gt=F('payed'))
      if not general:
          denitr = denitr.filter(by__Interprise=todo['shell'])

      deni = denitr.aggregate(sumi=Sum(F('amount')-F('payed')))['sumi'] or 0
      wateja.append({
          'cust':c,
          'deni':deni
      })

      madeni += deni

      

  todo.update({
      'isCustomer':True,
      'wateja':wateja,
      'madeni':madeni
  })
  return render(request,'customers.html',todo)

@login_required(login_url='login')
def ViewCustomer(request):
  try:
    i = int(request.GET.get('i',0))
    todo = todoFunct(request)
    shell = todo['shell']
    kampuni = todo['kampuni']
    general = todo['general']


    leo = datetime.datetime.now().astimezone()
    thisMonth = leo.strftime('%Y-%m-01 00:00:00%z') 
    #   print(int(leo.strftime('%m')))

    cust = wateja.objects.get(Q(Interprise__company=kampuni)|Q(allEntp=True),pk=i)

    saleAll = fuelSales.objects.filter(customer=cust.id,by__Interprise__company=kampuni).annotate(due=F('amount')-F('payed')).order_by('-pk')
    saleLst = saleList.objects.filter(sale__in=saleAll).order_by('theFuel')
    cdOrder =   creditDebtOrder.objects.filter(customer=cust.id,by__user__company=kampuni).annotate(due=F('amount')-F('consumed'),credit=F('paid')-F('consumed')).order_by('-pk')
    lastCd = cdOrder.first()

    # Add new credit debt order if the last order amount = consumed
    addNewOrder = not cdOrder.exists() or (lastCd and lastCd.amount == lastCd.consumed) if not general else False
    newcode = '01'
    if cdOrder.exists():
        newcode = cdOrder.last().Invo_no + 1
    # entry = fuelSales.objects.filter(by__Interprise=shell)
    
    # code = invoCode(entry)
    # sale.code = TCode({'code':code,'shell':shell.id})

    # sale.Invo_no = int(code)   
    saleAll = saleAll.filter(by__Interprise=shell)
    saleMonth = saleAll.filter(date__gte=thisMonth)
 
    sale_prev = saleAll.filter(date__lt=thisMonth,payed__lt=F('amount')) 
    # print(addNewOrder)

    totprev = sale_prev.aggregate(Amo=Sum('amount'))['Amo'] or 0
    paidprev = sale_prev.aggregate(Paid=Sum('payed'))['Paid'] or 0
    debtprev = totprev - paidprev

    totAmo = saleMonth.aggregate(Amo=Sum('amount'))['Amo'] or 0
    paid = saleMonth.aggregate(Paid=Sum('payed'))['Paid'] or 0
    debt = totAmo - paid
    # Group saleList by sale
  
    sale_data_prev = []
    def getsale_data(theSales):
        sale_data_prev = []
        for sale in theSales:
            items = saleLst.filter(sale=sale)
            StTanks = fuel_tanks.objects.filter(Interprise__company=kampuni)
            # Prepare fuel data for each sale
            fuels = []
            totRAmo = 0
            for item in StTanks.distinct('fuel'):
                fuel_items = items.filter(theFuel=item.fuel)
                total_Amo = fuel_items.aggregate(sumi=Sum(F('qty_sold')*F('sa_price_og')))['sumi'] or 0
                fuels.append({
                    'fuel': item.fuel.name,
                    'qty':fuel_items.aggregate(sumi=Sum('qty_sold'))['sumi'] or 0,
                    'price': total_Amo / (fuel_items.aggregate(sumi=Sum('qty_sold'))['sumi'] or 1),
                    'total': total_Amo ,
                })
                totRAmo += total_Amo

        
              

            sale_data_prev.append({
                'sale': sale,
                'fuels': fuels,
                'discount': float(totRAmo - sale.amount),   
                'totRAmo':totRAmo
            })
        return sale_data_prev
    
    def thetotSummary(totSale):
        fuel_items= saleLst.filter(sale__in=totSale)
        
        StTanks = fuel_tanks.objects.filter(Interprise__company=kampuni)
        theFuel = StTanks.distinct('fuel')

        fuels = []
        for fl in theFuel:
            itmsFuel = fuel_items.filter(theFuel=fl.fuel)
            total_Amo = itmsFuel.aggregate(sumi=Sum(F('qty_sold')*F('sa_price_og')))['sumi'] or 0
            fuels.append({
                'fuel': fl.fuel.name,
                'qty':itmsFuel.aggregate(sumi=Sum('qty_sold'))['sumi'] or 0,
                'price': total_Amo / (itmsFuel.aggregate(sumi=Sum('qty_sold'))['sumi'] or 1),
                'total': total_Amo ,
            })  

        

        totSummary={
            'fuels': fuels,
            'invo':len(totSale),
            'totAmo':fuel_items.aggregate(sumi=Sum(F('qty_sold')*F('sa_price_og')))['sumi'] or 0,
            'payable':totSale.aggregate(sumi=Sum('amount'))['sumi'] or 0,
            'totPaid':totSale.aggregate(sumi=Sum('payed'))['sumi'] or 0,
            'totDebt':(totSale.aggregate(sumi=Sum('amount'))['sumi'] or 0) - (totSale.aggregate(sumi=Sum('payed'))['sumi'] or 0),
            'discount': float((fuel_items.aggregate(sumi=Sum(F('qty_sold')*F('sa_price_og')))['sumi'] or 0) - (totSale.aggregate(sumi=Sum('amount'))['sumi'] or 0)),

            
        }    

        return totSummary


    sale_data_prev = getsale_data(sale_prev)
    sale_data=getsale_data(saleMonth)
    totSummary_prev = thetotSummary(sale_prev)
    totSummary = thetotSummary(saleMonth)
   

    todo.update({
        'isCustomer':True,
        'isCustomerView':True,
        'cust':cust,
        'addOrder':addNewOrder,
        'sale':sale_data,
         'newcode':newcode,    
        'totAmo':totAmo,
        'baki':debt,
        'paid':paid,
        'lastCd':lastCd,
        'debtprev':debtprev,
        'totprev':totprev,
        'prevsale':sale_data_prev,
        'paidprev':paidprev,

        'totSummary':totSummary,
        'totSummary_prev':totSummary_prev,

        'thereIsPrev':len(sale_prev),
        'thereIsThis':len(saleMonth),

        'totA':totAmo+totprev,
        'totD':debtprev+debt,
        'totP':paid+paidprev,
        'totI':len(saleMonth) + len(sale_prev)

        

    })
    return render(request,'customerView.html',todo)
  except:
      return render(request,'pagenotFound.html')

@login_required(login_url='login')
def save_credit_order(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            useri = todo['useri']
            manager = todo['manager']
            shell = todo['shell']
            kampuni = todo['kampuni']

            if useri.admin or manager:
                cust_id = int(request.POST.get('custId', 0))
                amount = float(request.POST.get('orderAmount', 0))
                paid = float(request.POST.get('paidAmount', 0))
                payAcc = int(request.POST.get('paymentAccount', 0))
                prepaid = int(request.POST.get('prepaid', 0))
                NewOda = int(request.POST.get('NewOda', 0))
                customer = wateja.objects.get(pk=cust_id, Interprise__company=kampuni)
                entry = creditDebtOrder.objects.filter(customer=customer, by__user__company=kampuni)


                order = creditDebtOrder()
                order.customer = customer
                order.amount = amount
                if prepaid:
                    order.paid = paid
                new_code = invoCode(entry)

                order.by = todo['cheo']
                order.Invo_no = int(new_code)
                order.code = TCode({'code': new_code, 'shell': customer.id})
                order.save()
                consume = fuelSales.objects.filter(customer=customer,amount__gt=F('payed')).annotate(deni=F('amount')-F('payed'))
                if consume.exists():
                    deni = consume.aggregate(sumi=Sum('deni'))['sumi'] or 0
                    if float(deni) > float(order.amount):
                       order.amount = float(deni)
                    order.consumed = deni
                    order.save()



                if prepaid and paid > 0 and payAcc:
                    acc = PaymentAkaunts.objects.get(pk=payAcc, Interprise__company=kampuni)
                    accAmo = float(acc.Amount)
                    payRec = wekaCash()
                    payRec.Interprise = shell
                    payRec.tarehe = datetime.datetime.now(tz=timezone.utc)
                    payRec.Amount = paid
                    payRec.Akaunt = acc
                    payRec.before = accAmo
                    if NewOda:
                        payRec.After = float(float(accAmo) + float(paid))
                    else:
                        payRec.After =   accAmo  
                    payRec.maelezo = 'Malipo ya sehemu ya deni kwa oda namba ' + str(order.code) + ' kwa mteja ' + str(
                        customer.jina)
                    payRec.by = useri
                    payRec.cdOrder = order
                    payRec.save()
                    if consume.exists():
                        paid_amo = paid
                        for b in consume.order_by('pk'):
                            if paid_amo > 0:  
                                deni = float(b.amount - b.payed)
                                lipwa = float(b.payed)
                                theP = paid_amo
                                if deni < paid_amo:
                                    b.payed = float(lipwa + deni)
                                    paid_amo = paid_amo - deni
                                    theP = deni
                                else:
                                    b.payed = float(lipwa + paid_amo)
                                    paid_amo = 0  
                                    exit 
                                b.cdorder = order     
                                b.save()

                                # if b.cdorder is not None:
                                #     cdOd = b.cdorder
                                #     cdOd.paid = float(float(cdOd.paid)+float(theP))
                                #     cdOd.save()

                                custP = CustmDebtPayRec()  
                                custP.sale = b
                                custP.pay = payRec   
                                custP.Debt =  deni 
                                custP.Apay =  float(theP)
                                custP.save()
                                            
                                            





                    #Check the other paid or unapaid sales
                





                    # Update the account balance
                    if NewOda:
                        acc.Amount = float(float(acc.Amount) + float(paid))
                        acc.save()





                data = {
                    'success': True,
                    'swa': 'Oda ya deni imehifadhiwa kikamilifu',
                    'eng': 'Credit order saved successfully',
                    'id': order.id
                }
            else:
                data = {
                    'success': False,
                    'swa': 'Hauna ruhusa ya kitendo hiki kwa sasa',
                    'eng': 'You have no permission for this action'
                }
            return JsonResponse(data)
        except Exception:
            data = {
                'success': False,
                'swa': 'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena baadaye',
                'eng': 'The action was unsuccessfully please try again later'
            }
            return JsonResponse(data)
    else:
        return JsonResponse({'success': False, 'swa': 'Bad Request', 'eng': 'Bad Request'})


@login_required(login_url='login')
def saveReceive(request):
    if request.method == "POST":
        try:
            tr_date = request.POST.get('tr_date')
            desc = request.POST.get('desc')
            toCont = int(request.POST.get('ToCont',0))
            Frcont = int(request.POST.get('cont'))
            op = int(request.POST.get('op'))
            rec_tr =json.loads(request.POST.get('tr_dt'))
            is_tnk = int(request.POST.get('is_tnk',0))
            is_pu = int(request.POST.get('is_pu',0))
            ToSt = int(request.POST.get('ToSt',0))
            is_othr = int(request.POST.get('is_othr',0))
             
            todo = todoFunct(request)
            useri = todo['useri']
            cheo = todo['cheo']
            shell = todo['shell']
            manager = todo['manager']
            kampuni = todo['kampuni']

            if useri.admin or manager:
                cont_to = None
                ToCont = None
                cont_From = None
                if toCont:
                    cont_to = tankContainer.objects.get(pk=toCont,compan=kampuni)
                    
                    isThere = ToContena.objects.filter(cont=cont_to,Incharge=cont_to.by)
                    if isThere.exists():
                        ToCont = isThere.last()
                    else:
                        ToCont = ToContena() 
                        ToCont.cont = cont_to
                        ToCont.Incharge = cont_to.by
                        ToCont.save()
                supV = None
                oprt = None
                if is_pu:

                    if ToSt:
                        shell = Interprise.objects.get(pk=ToSt,company=kampuni) 
                    else:
                        theCont = fuel_tanks.objects.filter(tank=cont_to).last()
                        shell = theCont.Interprise
                    cheo = InterprisePermissions.objects.get(Interprise=shell,user=useri)

                    oprt = InterprisePermissions.objects.get(pk=op,Interprise__company=kampuni).user
                else:
                    oprt = InterprisePermissions.objects.get(pk=op,Interprise=shell).user    
                supVs =  tr_supervisor.objects.filter(sup=oprt)

                
                if supVs.exists():
                    supV=supVs.last()
                else:
                    supV = tr_supervisor()
                    supV.sup = oprt
                    supV.save()
 
                
                rcv = ReceveFuel()
                entry = ReceveFuel.objects.filter(by__Interprise=shell.id) 
                ses = shiftSesion.objects.filter(session__Interprise=shell,complete=False)
                Lses = None
                if ses.exists():
                    Lses = ses.last()

                code = invoCode(entry)
                rcv.code = TCode({'code':code,'shell':shell.id}) 

                rcv.Invo_no = int(code)
                rcv.date = datetime.datetime.now(tz=timezone.utc)

                rcv.recDate = tr_date
                
                rcv.Tocont = ToCont
                rcv.by = cheo
                rcv.op = supV
                rcv.ses = Lses 
                rcv.desc = desc

                if is_tnk:
                    cont_From=tankContainer.objects.get(pk=Frcont,compan=kampuni)
                    rcv.Fromcont =  cont_From
                    rcv.Incharge = cont_From.by

                if is_othr:
                    cont_From = TransferFuel.objects.get(pk=Frcont,record_by__Interprise__company=kampuni)  
                    rcv.FromTransf = cont_From
                    rcv.Incharge = cont_From.Transfer_by

                if is_pu:
                     cont_From =  Purchases.objects.get(pk=Frcont,record_by__company=kampuni)   
                     rcv.FromPurchase = cont_From
                     rcv.Incharge = cont_From.record_by

                rcv.save()


  
                
                for rec in rec_tr:

                    rcf = receivedFuel()
                    trqty = float(rec['qtyA']-rec['qtyB'])
                    tnkTo = fuel_tanks.objects.get(Interprise__company=kampuni,pk=rec['toTnk'])
                    trFuel = fuel.objects.get(pk=rec['t_fuel'])
                    if is_tnk:
                        FromT = None
                        TnkExists = transfer_from.objects.filter(tank=rec['tnk'],tank__Interprise__company=kampuni)
                        if TnkExists.exists():
                            FromT = TnkExists.last()
                        else:
                            FromT =   transfer_from()  
                            f_t = fuel_tanks.objects.get(pk=rec['tnk'],Interprise__company=kampuni)
                            FromT.tank = f_t
                            FromT.save()

                        rcf.From = FromT
                        tnkFrom = FromT.tank
                        tnkFrmQty = float(tnkFrom.qty)
                        tnkFrom.qty = float(tnkFrmQty - trqty)
                        tnkFrom.save()
                    
                    if is_othr:
                        # Reduce the fuel when no oficial container used
                        trRec = transFromTo.objects.filter(Fuel=trFuel,transfer=cont_From,qty__gt=F('taken'))
                        rcvqty = trqty
                        for t in trRec:
                            rem =  float(t.qty - t.taken)
                            
                            if rem < trqty:
                                t.taken = float(t.qty)
                                rcvqty = rcvqty - rem
                                t.save()
                            else:
                                t.taken = float(float(t.taken)+rcvqty)
                                rcvqty = 0
                                t.save()

                    if is_pu:
                        puRec = PuList.objects.get(pk=rec['tnk'],pu=cont_From)
                        puRec.rcvd = float(float(puRec.rcvd) + trqty)
                        puRec.save()
                        puLst = PuList.objects.filter(pu=cont_From,qty__gt=F('rcvd'))
                        if not puLst.exists():
                            cont_From.closed = True


                        
               

                    rcf.To = tnkTo
                    rcf.qty = trqty
                    rcf.qtyB = float(rec['qtyB'])
                    rcf.qtyA = float(rec['qtyA'])
                    rcf.Fuel = trFuel
                    rcf.receive = rcv
                    rcf.cost = float(rec['fcost'])
                    rcf.price = float(fuel_tanks.objects.filter(Interprise=shell,fuel=rec['t_fuel']).last().price)
                    rcf.save()

                    tnkqty = float(tnkTo.qty)
                    tnkcost = float(tnkTo.cost)
                    tnkTcost = float(float(rec['qtyB']) * tnkcost)
                    trTcost = float(trqty * float(rec['fcost']))
                    Totqty = float(rec['qtyA'])
                    Totcost = float(tnkTcost + trTcost)      

                    if tnkTo.moving or Lses is None:
                        # if tnkqty != float(tnkTo.qty):
                            adj = None
                            recAdjs = adjustments.objects.filter(receive=rcv)
                            if recAdjs.exists():
                                adj = recAdjs.last()
                            else:    
                                adj = adjustments()
                                entry = adjustments.objects.filter(Interprise=shell)
                                code = invoCode(entry)

                                adj.code = TCode({'code':code,'shell':shell.id}) 

                                adj.Invo_no = int(code)
                                adj.tarehe = datetime.datetime.now(tz=timezone.utc)
                                adj.operator =  oprt
                                adj.by = cheo
                                adj.Interprise = shell
                                # adj.maelezo = desc
                                adj.receive = rcv
                                adj.container = cont_to
                      
                                
                                adj.save()
                            recAdj =   tankAdjust()
                            recAdj.adj = adj
                            recAdj.tank = tnkTo
                            recAdj.read = tnkqty
                            recAdj.fuel = trFuel
                            recAdj.stick = float(rec['qtyB'])
                            recAdj.diff = float(float(rec['qtyB']-tnkqty ))
                            recAdj.price = float(tnkTo.price)
                            recAdj.cost = float(tnkTo.cost)
                            recAdj.save()
                            tnkTo.qty = float(rec['qtyA'])
                            tnkTo.cost = float(Totcost/Totqty)
                            tnkTo.save()
                    else:
                        tnkExist = receivedFuel.objects.filter(To=tnkTo,receive=rcv)
                        # Check whether there is fuel sold during the session so as record its cost then use it ro regurate the cost for sold fuel at the end of session
                        if tnkExist.count() == 1:
                            trsf = transFromTo.objects.filter(pump__tank=tnkTo,shift__shift__session=Lses)
                            used = rekodiMatumizi.objects.filter(fromShift__pump__tank=tnkTo,fromShift__shift__session=Lses)
                            sold = saleList.objects.filter(shift__shift__session=Lses,shift__pump__tank=tnkTo)
                            AsoldB = saleOnReceive.objects.filter(ses=Lses).exclude(receive__receive=rcv)
                            recevd = receivedFuel.objects.filter(receive__ses=Lses,To=tnkTo).exclude(receive=rcv)
                            # To get the sold fuel sum the sold + transfered + used then take the initial tank reading before session and substract the sum  
                            recevdQty = recevd.aggregate(sumi=Sum('qty'))['sumi']  or 0
                            AsoldQty = AsoldB.aggregate(sumi=Sum('qty'))['sumi']  or 0
                            trQty = trsf.aggregate(sumi=Sum('qty'))['sumi']  or 0
                            usedQty = used.aggregate(sumi=Sum('fuel_qty'))['sumi'] or 0
                            soldQty = sold.aggregate(sumi=Sum('qty_sold'))['sumi'] or 0
                            # get the qty of fuel out of the tank after session ......//  
                            diff = float(tnkqty + float(recevdQty))-float(rec['qtyB']) 

                            if diff > 0:
                                sale = float(diff) - float(trQty+usedQty+soldQty+AsoldQty)
                                if sale > 0:
                                    soldB = saleOnReceive()
                                    soldB.tank = tnkTo
                                    soldB.ses = Lses
                                    soldB.receive = rcf
                                    soldB.qty = float(sale)
                                    soldB.cost = float(tnkTo.cost)
                                    soldB.save()

                        


              
                data = {
                    'id':rcv.id,
                    'success':True,
                    'msg_swa':'Data za Kuhamisha mafuta zimehifadhiwa kikamilifu',
                    'msg_eng':'Fuel Transfer data saved successfully'
                }

                return JsonResponse(data)




            else:
                data = {
                    'success':False,
                    'msg_swa':'Hauna Ruhusa ya kitendo hiki kwa sasa',
                    'msg_eng':'You have no permission for this please contact user'
                }
                return JsonResponse(data)


        except:
            data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena baadaye',
                'msg_eng':'The action was unsuccessfully please try again later'
            }

            return JsonResponse(data)
    else:
        data = {
            'success':False,
            'msg_swa':'Haikufanikiwa',
            'msg_eng':'Bad Request'
        }

        return JsonResponse(data)


@login_required(login_url='login')
def LimitOrderSet(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            useri = todo['useri']
            manager = todo['manager']
            cheo = todo['cheo']
            kampuni = todo['kampuni']
            shell = todo['shell']

            if useri.admin or manager:
                cust = int(request.POST.get('cust'))
                custm = wateja.objects.get(pk=cust,Interprise__company=kampuni)
                custm.limited_order = not custm.limited_order
                custm.save()

                data ={
                    'success':True,
                    'swa':'manunuzi ya oda kwa mteja yamerekebishwa kikamilifu',
                    'eng':'Order Limit to customer changed successfully'
                }

                return JsonResponse(data)

            else:
                data = {
                    'success':False,
                    'swa':'Huna ruhusa hii kwa sasa',
                    'eng':'You have no permission for this now'
                }   
                return  JsonResponse(data)

        except:
            data = {
                'success':False,
                'swa':'kitendo hakikufanikiwa kutokana na hitilafu',
                'eng':'The action was not successfully due to erro please try again'
            }   

            return JsonResponse(data)


@login_required(login_url='login')
def fuelsales(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            useri = todo['useri']
            manager = todo['manager']
            cheo = todo['cheo']
            kampuni = todo['kampuni']
            shell = todo['shell']

            if useri.admin or manager:
                cust = int(request.POST.get('cust'))
                mv = int(request.POST.get('mv'))
                date = request.POST.get('saDate')
                phone = request.POST.get('phone')
                driver = request.POST.get('rcvd')
                vihecle = request.POST.get('vihecle')
                cont =  request.POST.get('cont')
                saleDt = json.loads(request.POST.get('saDt'))

                data = {
                    'success':True,
                    'msg_swa':'Taarifa za mauzo zimehifadhiwa kikamilifu',
                    'msg_eng':'Fuel sales recorded successfully'
                }

                custm = wateja.objects.get(pk=cust,Interprise__company=kampuni)
                cdOrder =   creditDebtOrder.objects.filter(customer=custm.id,by__user__company=kampuni,amount__gt=F('consumed'))
                lcdorder = None  

                if custm.limited_order and not cdOrder.exists():
                    data = {
                        'success':False,
                        'msg_swa':'Rekodi ya mauzo haijafanikiwa kwa sababu mteja huyu amewekwa katika ukomo wa oda lakini hakuna oda iliyopatikana',
                        'msg_eng':'The customer is set to limited credit/debt order but no order record found for customer '
                    }

                    return JsonResponse(data)

                sale = fuelSales()
                sale.by = cheo
                sale.customer = custm
                entry = fuelSales.objects.filter(by__Interprise=shell)
               
                code = invoCode(entry)
                sale.code = TCode({'code':code,'shell':shell.id})

                sale.Invo_no = int(code)   
                # sale.due_date = date
                sale.recDate = datetime.datetime.now(tz=timezone.utc)
                sale.date = date
             
                sale.driver = driver
                sale.vihecle = vihecle
                if phone != '':
                    sale.phone = phone
                contn = None    
                if mv:
                    contn = tankContainer.objects.get(pk=cont,compan=kampuni)
                    sale.cont = contn
                    sale.contInchage = contn.by
                else:
                    ses = shiftSesion.objects.filter(session__Interprise=shell,complete=False)    
                    sale.session = ses.last()
                sale.save()    
                amo = 0    
                try: 
                    for sa in saleDt:
                        saL = saleList()
                        saL.sale = sale
                        theF = None
                        cost = 0
                        pr_og = 0
                        if mv:
                            tnk = fuel_tanks.objects.get(pk=sa['tnk'],tank=contn)
                            theF = tnk.fuel
                            cost = float(tnk.cost)  
                            pr_og = float(tnk.price)
                            saL.tank = tnk
                            tnk.qty = float(float(tnk.qty) - float(sa['totAmo']/sa['price']))
                            tnk.save()
                        else:
                            pmp = fuel_pumps.objects.get(pk=sa['pmp'],tank__Interprise=shell)
                            # shpId = []
                            
                            # for sh in shppm:
                            #     shpId.append({
                            #         'id':sh.id,
                            #         'pmp':sh.pump.id,
                            #         'shId': sh.id if sh.shift else None,
                            #         'datFr':sh.shift.From if sh.shift else None,
                            #         'datTo':sh.shift.To if sh.shift else None
                            #         })
                            # print(shpId)   

                            shppm = shiftPump.objects.filter(pump=pmp,shift__To=None).exclude(shift=None).order_by('pk')
                            shpmp = shppm.last()

                            saL.shift = shpmp
                            saL.tank = pmp.tank
                            theF = pmp.tank.fuel
                            cost = float(pmp.tank.cost)  
                            pr_og = float(pmp.tank.price)   

                        saL.theFuel =  theF
                        saL.qty_sold = float(sa['totAmo']/sa['price'])   
                        saL.sa_price = float(sa['price'])
                        saL.sa_price_og = pr_og
                        saL.cost_sold = cost
                        saL.save()

                        amo += (sa['totAmo']) 
                except:
                    sale.delete()
                    data = {
                        'success':False,
                        'msg_swa':'Rekodi ya mauzo haijafanikiwa tafadhari hakikisha umejaza taarifa zote kikamilifu',        
                         'msg_eng':'Sales record was not successful please make sure you fill all required information correctly'
                    }
                    return JsonResponse(data)
                sale.amount = float(amo)
                

                if cdOrder.exists():
                    lcdorder = cdOrder.last()
                    if float(lcdorder.amount) < float(float(lcdorder.consumed)+float(amo)):
                        fuelSales.objects.filter(pk=sale.id).delete()
                        data = {
                            'success':False,
                            'msg_swa':'Kiasi cha mafuta kimezidi kiwango cha ukomo kilichowekwa',
                            'msg_eng':'the fuel amount exceeds the order limit set for customer'
                        }

                        return JsonResponse(data)




                    if lcdorder.paid > lcdorder.consumed:
                        Od_balance = float(float(lcdorder.paid) - float(lcdorder.consumed))
                        if Od_balance >= float(amo):
                            sale.payed = float(amo)
                        else:
                            sale.payed =  Od_balance 

                    lcdorder.consumed = float(float(amo)+float(lcdorder.consumed))
                    sale.cdorder = lcdorder
                    lcdorder.save()

                
                sale.save()

                

                if cdOrder.exists() and int(lcdorder.paid) > 0:
                    ilolipwa = wekaCash.objects.get(cdOrder=lcdorder)
                    custPay = CustmDebtPayRec()
                    custPay.pay = ilolipwa
                    custPay.sale = sale
                    custPay.Debt = float(sale.payed)
                    custPay.Apay = float(sale.payed)
                    custPay.save()
                    
                else:

                    weka = wekaCash()
                    deni_nyuma = entry.filter(amount__gt=F('payed'))
                    weka.Amount = float(0)
                    weka.before = 0               
                    weka.After = 0 
                    weka.kutoka = 'mauzo'
                    weka.maelezo = 'desc'
                    weka.tarehe = datetime.datetime.now(tz=timezone.utc)
                    weka.by=useri
                    weka.Interprise=shell
                    weka.saRec=True
                    weka.mauzo=True
                    weka.tInvo = len(deni_nyuma)
                    weka.tDebt = float(deni_nyuma.aggregate(sumi=Sum(F('amount')-F('payed')))['sumi'])
                #   if pall:
                    weka.customer = custm
                #   else:
                #     weka.sales = bill
                        
                    weka.save()


                data.update({'id':sale.id}) 
                return JsonResponse(data)

            else:
                data = {
                     'success':False,
                    'msg_swa':'Hauna Ruhusa hii kwa sasa tafadhari wasiliana na uongozi',
                    'msg_eng':'You have no permission for this please try again later'

                }

                return JsonResponse(data)

        except:
            data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena baadaye',
                'msg_eng':'The action was unsuccessfully please try again later'
            }

            return JsonResponse(data)
    else:
        data = {
            'success':False
        }
        return JsonResponse(data)

@login_required(login_url='login')
def fueltranfer(request):
    if request.method == "POST":
        try:
            mv = int(request.POST.get('mv'))
            sto = int(request.POST.get('Sto'))
            cont = int(request.POST.get('cont'))
            op = int(request.POST.get('op'))
            gvenTo = int(request.POST.get('gvenTo'))

            
           
            # qty = float(request.POST.get('qty'))
            # tank = int(request.POST.get('tank'))
            desc = request.POST.get('desc')
            otherSto = request.POST.get('otherSto')
            tr_date = request.POST.get('tr_date')

            tr_rec = json.loads(request.POST.get('tr_dt'))

    

            todo = todoFunct(request)
            useri = todo['useri']
            manager = todo['manager']
            shell = todo['shell']
            cheo = todo['cheo']
            kampuni=todo['kampuni']

            if useri.admin or manager:
               
                sup = InterprisePermissions.objects.get(pk=op,user__tankSup=True)
                tr_by = None
                tankCont = None
                if mv:
                    tr_by = UserExtend.objects.get(pk=gvenTo,op=True)
                
                    if cont and not sto:
                        tankCont = tankContainer.objects.get(pk=cont,compan=kampuni)



                err = 0

                ftr = TransferFuel()
                trSup = tr_supervisor()
                trSup.sup = sup.user
                trSup.save()

                entry = TransferFuel.objects.filter(record_by__Interprise=shell.id)
                code = invoCode(entry)
                ftr.code = TCode({'code':code,'shell':shell.id})
                ftr.Invo_no = int(code)
                ftr.container = tankCont
                if sto:
                    ftr.otherCont = otherSto
                ftr.date = tr_date
                ftr.recDate = datetime.datetime.now(tz=timezone.utc)
                ftr.record_by = cheo

                ftr.Transfer_by = tr_by

                ftr.trSup = trSup
                ftr.desc = desc
                ftr.save()

                data = {
                    'success':True,
                    'swa':'Mafuta yamehamishwa kikamilifu',
                    'eng':'Fuel transfered successfully',
                    'id':ftr.id
                }
                
                for t in tr_rec:
                    trFrT = transFromTo()
                    trFr = transfer_from()
                    
                    to_tank = None

                    frm_pump = fuel_pumps.objects.get(pk=t['trpmp'],tank__Interprise=shell)
               
                        
                    if not sto:
                        to_tank = fuel_tanks.objects.get(pk=t['tnk'],Interprise__company=kampuni)
                        tankContUnMatch = False
                        if mv:
                            try:
                               to_tank = fuel_tanks.objects.get(pk=t['tnk'],tank=cont,Interprise__company=kampuni)
                            except:
                                tankContUnMatch = True

                        if  tankContUnMatch:
                              ftr.delete()  

                    frm_tank = frm_pump.tank
                    shift = None
                    if frm_pump.Incharge is not None:
                        shift = shiftPump.objects.filter(pump=frm_pump,shift__To=None).last()
                   
                    trFr.tank = frm_tank
                    trFr.save()
                
                    trFrT.transfer = ftr 
                    trFrT.shift =  shift
                    trFrT.pump = frm_pump
                    trFrT.Fuel = frm_tank.fuel
                    trFrT.cost = float(frm_tank.cost)
                    trFrT.saprice = float(frm_tank.price)
                    trFrT.qty = float(t['tqty'])
                    trFrT.From = trFr
                    trFrT.to = to_tank
                    trFrT.save()
                    

                    if shift is None:
                        frm_pump.readings = float(float(frm_pump.readings)+float(t['tqty']))
                        frm_pump.save()                       
                        frm_tank.qty = float(float(frm_tank.qty) - float(t['tqty']))
                        frm_tank.save()

                    if to_tank is not None:
                        FtnkCost = float(t['tqty']) * float(frm_tank.cost)   
                        TtnkCost = float(to_tank.qty * to_tank.cost)
                        Tcost = float(FtnkCost + TtnkCost)
                        toqty = float(float(t['tqty']) + float(to_tank.qty))
                        to_tank.qty = toqty
                        to_tank.cost = float(Tcost/toqty)
                        to_tank.fuel = frm_tank.fuel
                        to_tank.save()

        
                return JsonResponse(data) 

                
            else:
                data = {
                     'success':False,
                    'swa':'Hauna Ruhusa hii kwa sasa tafadhari wasiliana na uongozi',
                    'eng':'You have no permission for this please try again later'

                }

                return JsonResponse(data)


            

        except:
            data = {
                'success':False,
                'swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena baadaye',
                'eng':'The action was unsuccessfully please try again later'
            }

            return JsonResponse(data)
    else:
        data = {
            'success':False,
            'swa':'Haikufanikiwa',
            'eng':'Bad Request'
        }

        return JsonResponse(data)

@login_required(login_url='login')
def getTr(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            shell = todo['shell']
            tr = int(request.POST.get('t'))

            trs = TransferFuel.objects.filter(closed=False).order_by('-pk').annotate(
                # FRom = F('From__tank__name'),
                shell_id = F('From__tank__Interprise'),
                shell_name = F('From__tank__Interprise__name'),

            )

            tanks = fuel_tanks.objects.filter(Interprise=shell.id).values()

            data = {
                'success':True,
                'trs':list(trs.values()),
                'tanks':list(tanks)
            }
            return JsonResponse(data)

        except:
            data = {
                'success':False
            }
            return JsonResponse(data)            
    else:
        data = {
            'success':False
        }
        return JsonResponse(data)

def traList(request):
    todo = todoFunct(request)
    
    general = todo['general']
    kampuni = todo['kampuni']

    tr = TransferFuel.objects.filter(record_by__Interprise__company=kampuni)

    if not general:
        shell = todo['shell']
        tr = tr.filter(record_by__Interprise=shell.id)

    num = tr.count()
    ttr = tr.order_by("-pk")

    p=Paginator(ttr,15)
    page_num =request.GET.get('page',1)
       

    try:
          page = p.page(page_num)

    except EmptyPage:
         page= p.page(1)

    pg_number = p.num_pages
    

    todo.update({
        'tr':page,
        'istransfer':True,
        'p_num':page_num,
        'pages':pg_number,
        'bil_num':num,
    })

    return todo

def recList(request):
    todo = todoFunct(request)
    
    general = todo['general']
    kampuni = todo['kampuni']

    tr = ReceveFuel.objects.filter(by__Interprise__company=kampuni.id)

    if not general:
        shell = todo['shell']
        tr = tr.filter(by__Interprise=shell.id)

    num = tr.count()
    ttr = tr.order_by("-pk")

    p=Paginator(ttr,15)
    page_num =request.GET.get('page',1)
       

    try:
          page = p.page(page_num)

    except EmptyPage:
         page= p.page(1)

    pg_number = p.num_pages

    todo.update({
        'tr':page,
        'isreceive':True,
        'p_num':page_num,
        'pages':pg_number,
        'bil_num':num,
    })

    return todo

def saList(request):
    todo = todoFunct(request)
    
    general = todo['general']
    kampuni = todo['kampuni']


    sa = fuelSales.objects.filter(by__Interprise__company=kampuni.id,shiftBy=None)

    if not general:
        shell = todo['shell']
        sa = sa.filter(by__Interprise=shell.id)

    num = sa.count()
    tsa = sa.order_by("-pk")

    p=Paginator(tsa,15)
    page_num =request.GET.get('page',1)
       

    try:
          page = p.page(page_num)

    except EmptyPage:
         page= p.page(1)

    pg_number = p.num_pages

    todo.update({
        'tr':page,
        'isSales':True,
        'p_num':page_num,
        'pages':pg_number,
        'bil_num':num,
    })

    return todo

def shList(request):
    todo = todoFunct(request)
    
    general = todo['general']
    kampuni = todo['kampuni']

    sh = shifts.objects.filter(record_by__Interprise__company=kampuni.id)

    if not general:
        shell = todo['shell']
        sh = sh.filter(record_by__Interprise=shell.id)

    num = sh.count()
    tsh = sh.order_by("-pk")

    p=Paginator(tsh,15)
    page_num =request.GET.get('page',1)
       

    try:
          page = p.page(page_num)

    except EmptyPage:
         page= p.page(1)

    pg_number = p.num_pages

    todo.update({
        'tr':page,
        'isShift':True,
        'p_num':page_num,
        'pages':pg_number,
        'bil_num':num,
    })

    return todo

def adjList(request):
    todo = todoFunct(request)
    
    general = todo['general']
    kampuni = todo['kampuni']

    adj = adjustments.objects.filter(by__Interprise__company=kampuni.id)

    if not general:
        shell = todo['shell']
        adj = adj.filter(by__Interprise=shell.id)

    num = adj.count()
    tadj = adj.order_by("-pk")

    p=Paginator(tadj,15)
    page_num =request.GET.get('page',1)
       

    try:
          page = p.page(page_num)

    except EmptyPage:
         page= p.page(1)

    pg_number = p.num_pages

    todo.update({
        'tr':page,
        'isAdjst':True,
        'p_num':page_num,
        'pages':pg_number,
        'bil_num':num,
    })

    return todo


def SesList(request):
    todo = todoFunct(request)
    
    general = todo['general']
    kampuni = todo['kampuni']

    sh = shiftSesion.objects.filter(session__Interprise__company=kampuni.id)

    if not general:
        shell = todo['shell']
        sh = sh.filter(session__Interprise=shell.id)

    num = sh.count()
    tsh = sh.order_by("-pk")

    p=Paginator(tsh,15)
    page_num =request.GET.get('page',1)
       

    try:
          page = p.page(page_num)

    except EmptyPage:
         page= p.page(1)

    pg_number = p.num_pages
    
    ses = []
    for p in page:
      ses.append({
          's':p,
          'sh':shifts.objects.filter(session=p).count()
      })  

  
    todo.update({
        'tr':ses,
        'isSession':True,
        
        'p_num':page_num,
        'pages':pg_number,
        'bil_num':num,
    })

    return todo


@login_required(login_url='login')
def addSession(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            sfrom = request.POST.get('sfrom')
            sTo = request.POST.get('sTo')
            todo = todoFunct(request)
            useri = todo['useri']
            shell = todo['shell']
            data = {
                'success':True,
                'swa':'Muda wa zamu umeongezwa kikamilifu',
                'eng':'Session added successfully'
            }
            if useri.admin:
                ses = shiftsTime()
                ses.name = name
                ses.shFrom = sfrom
                ses.shTo = sTo
                ses.Interprise = shell
                ses.save()
            else:
                data = {
                    'success':False,
                    'swa':'Hauna ruhusa hii kwa sasa tafadhari wasiliana na uongozi',
                    'eng':'You have no permission for this please contact admin'
                }
            
            return JsonResponse(data)


        except:
            data = {
                'success':False,
                'swa':'Kitendo hakikufanikiwa tafadhari jaribu tena baadaye',
                'eng':'The action was not successfully please try again later'
            }
            return JsonResponse(data)
    else:
        return render(request,'pagenotFound.html')

@login_required(login_url='login')
def shiftsDate(request):
     todo =  SesList(request)
     return render(request,'SessionsList.html',todo)
    

@login_required(login_url='login')
def theshiftsTime(request):
    todo = todoFunct(request)
    shell = todo['shell']
    kampuni = todo['kampuni']
    general = todo['general']

    shT = shiftsTime.objects.filter(Interprise__company=kampuni)

    if not general:
        shT = shT.filter(Interprise=shell.id)
    todo.update({
        'shT':shT,
        'isShiftTime':True
    })

    return render(request,'shiftsTime.html',todo)


@login_required(login_url='login')
@require_POST
def deleteShiftExpenses(request):
    try:
        todo = todoFunct(request)
        shell = todo['shell']
        manager = todo['manager']
        if not manager and not todo['useri'].admin:
            return JsonResponse({'success': False, 'eng': 'Permission denied.','swa':'Ruhusa imeruhusiwa.'})
        expense_ids = request.POST.getlist('expense_ids[]')
        if not expense_ids:
            # Try as JSON string if not sent as array
            expense_ids = json.loads(request.POST.get('expense_ids', '[]'))
        # Ensure all ids are integers
        expense_ids = [int(eid) for eid in expense_ids if str(eid).isdigit()]
        if not expense_ids:
            return JsonResponse({'success': False, 'eng': 'No valid expense IDs provided.','swa':'Hakuna vitambulisho halali vya matumizi vilivyotolewa.'})
        deleted, _ = rekodiMatumizi.objects.filter(pk__in=expense_ids,Interprise=shell.id).delete()
        if deleted > 0:
            return JsonResponse({'success': True, 'eng': 'Expenses deleted successfully.','swa':'Matumizi yamefutwa kwa mafanikio.'})
        else:
            return JsonResponse({'success': False, 'eng': 'No expenses deleted.','swa':'Hakuna matumizi yaliyofutwa.'})
    except Exception as e:
        return JsonResponse({'success': False, 'eng': f'Error: {str(e)}'})

@login_required(login_url='login')
def theAdjst(request):
    todo = adjList(request)
    return render(request,'adjList.html',todo)

@login_required(login_url='login')
def truckView(request):
    try:
        t = int(request.GET.get('t',0))
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        cont = tankContainer.objects.get(pk=t,compan=kampuni)
        tanks = fuel_tanks.objects.filter(tank=cont).annotate(Tcost=F('qty')*F('cost'),Tprice=F('qty')*F('price'),Tprof=(F('price')-F('cost'))*F('qty'))
        todo.update({
            'cont':cont,
            'tanks':tanks,
            'istruck':True,
            'Tqty':tanks.aggregate(tqty=Sum('qty'))['tqty'],
            'Tcost':tanks.aggregate(tcost=Sum(F('qty')*F('cost')))['tcost'],
            'Tprice':tanks.aggregate(tprice=Sum(F('qty')*F('price')))['tprice'],
            'Tprof':tanks.aggregate(tprof=Sum(F('qty')*(F('price')-F('cost'))))['tprof']
        })
        return render(request,'fuelTruckView.html',todo)
    except:
        return render(request,'pagenotFound.html')

@login_required(login_url='login')
def ChangeTruckIncharge(request):
    if request.method == "POST":
        try:
            inc = int(request.POST.get('inc',0))
            cont = int(request.POST.get('cont',0))
            todo = todoFunct(request)
            useri = todo['useri']
            kampuni = todo['kampuni']
            if useri.admin:
                Truck = tankContainer.objects.get(pk=cont,compan=kampuni)
                gvnT = UserExtend.objects.get(pk=inc,company=kampuni)
                Truck.by = gvnT
                Truck.save()
                data = {
                    'success':True,
                    'swa':'Mhusika amebadilishwa kikamilifu',
                    'eng':'Truck Incharge chaged successfully',
                }
                return JsonResponse(data)
            else:
                data = {
                     'swa':'Hauna ruhusa hii kwa sasa tafadhari wasiliana na uongozi',
                    'eng':'You have no permission for this please contact admin',
                    'success':False
                }  
                return JsonResponse(data)  
        except:
            data={
                'swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi',
                'eng':'The action was not successfull due to error please try again correctly',
                'success':False
            }
            return JsonResponse(data)
    else:
        data = {'success':False}
        return JsonResponse(data)

@login_required(login_url='login')
def trucks(request):
    todo = todoFunct(request)
    ftrucks = []
    general = todo['general']
    kampuni = todo['kampuni']

   

    tanks = fuel_tanks.objects.filter(tank__compan=kampuni)

    if not general:
        shell = todo['shell']
        tanks = tanks.filter(Interprise=shell)

    TFuel = tanks.distinct('fuel')
    Fsum = [] 

    for f in TFuel:
        theF = tanks.filter(fuel=f.fuel.id).annotate(Tcost=F('qty')*F('cost'),Tprice=F('qty')*F('price'),Tprof=(F('price')-F('cost'))*F('qty'))
        Fsum.append({
            'Fuel':f,
            
            'qty':theF.aggregate(qty=Sum('qty'))['qty'],
            'cost':theF.aggregate(theCost=Sum('Tcost'))['theCost'],
            'price':theF.aggregate(thePrice=Sum('Tprice'))['thePrice'],
            'prof':theF.aggregate(theProf=Sum('Tprof'))['theProf']
        })    

    ftr = tanks.distinct('tank')  


    for tn in ftr:
        tF = []
        Ct = tanks.filter(tank=tn.tank).annotate(thecost=F('qty')*F('cost'))
        Df=Ct.distinct('fuel')
        for f in Df:
            tF.append({
                'Fuel':f,
                'qty':Ct.filter(fuel=f.fuel).aggregate(thesum=Sum('qty'))['thesum']
            })

        ftrucks.append({
            'cont':tn,
             'fuel':tF,
             'Tcost':Ct.aggregate(tcost=Sum('thecost'))['tcost'],
             'Tprice':Ct.aggregate(tprice=Sum(F('qty')*F('price')))['tprice'],
             'Tprof':Ct.aggregate(tprof=Sum(F('qty')*(F('price')-F('cost'))))['tprof']
        }) 

    todo.update({
        'cont':ftrucks,
        'istruck':True,
        'Fsum':Fsum,
        'Tcost':tanks.aggregate(tcost=Sum(F('qty')*F('cost')))['tcost'],
        'Tprice':tanks.aggregate(tprice=Sum(F('qty')*F('price')))['tprice'],
        'Tprof':tanks.aggregate(tprof=Sum(F('qty')*(F('price')-F('cost'))))['tprof']
    }) 

    return render(request,'fuelTruck.html',todo)


@login_required(login_url='login')
def adjView(request):
    val = int(request.GET.get('i'))
    todo = adjList(request)
    general = todo['general']
    kampuni = todo['kampuni']
    tr = adjustments.objects.filter(pk=val,Interprise__company=kampuni)
       
    # print(tr.count())
     
    trf = tr.last()
    tankAdj = tankAdjust.objects.filter(adj=trf)
    attach = attachments.objects.filter(adj=trf)

    diffSum = tankAdj.aggregate(diff=Sum('diff') )['diff']
    amoSum = tankAdj.aggregate(diff=Sum(F('diff') * F('price')))['diff']

    todo.update({
    'attach':attach,
    'trf':trf,
    'tankAdj':tankAdj,
    'isAdjView':True,
    'diffSum':diffSum,
    'amoSum':amoSum
   
})
    
    html = 'adjView.html'
    pr = int(request.GET.get('t',0))
    lang = int(request.GET.get('lang',0))

    if pr:
        todo.update({
            'langSet':lang
        })
        html = 'adjViewPrint.html'

    return render(request,html,todo)

@login_required(login_url='login')
def theshifts(request):
    todo = shList(request)
    return render(request,'shifts.html',todo)

@login_required(login_url='login')
def viewTransfer(request):
    val = int(request.GET.get('i'))
    todo = traList(request)

    general = todo['general']
    trf = TransferFuel.objects.get(pk=val)

    # if not general:
    #     shell = todo['shell']
    #     tr = tr.filter(From__tank__Interprise=shell.id)
    
    # trf = tr.last()
    attach = attachments.objects.filter(transfer=trf.id)
    rcd = receiveFromTr.objects.filter(From=trf.id)

    trFrTo = transFromTo.objects.filter(transfer=trf).annotate(worth=F('qty')*F('saprice'))
    totqty = trFrTo.aggregate(Qty=Sum('qty'))['Qty']
    totAmo = trFrTo.aggregate(Amo=Sum('worth'))['Amo']
    
    rcdTr = []
    for r in rcd:
        attachr = None
        at = None
        if r.To_Rc is not None:
            at = attachments.objects.filter(receive=r.To_Rc.id)

        if r.To_Sa is not None:
            at = attachments.objects.filter(sales=r.To_Sa.id)

        if at.exists():
            attachr = at.last()
        rcdTr.append({
            't':r,
            'received':r.To_Rc is not None,
            'sales':r.To_Sa is not None,
            'attach':attachr
        })
    todo.update({
        'attach':attach,
        'trf':trf,
        'tr_rec':trFrTo,
        'rcd':rcdTr,
        'isViewTransfer':True,
        'totqty':totqty,
        'totAmo':totAmo
    })

    html = 'transferNoteview.html'
    pr = int(request.GET.get('t',0))
    lang = int(request.GET.get('lang',0))

    if pr:
        todo.update({
            'langSet':lang
        })
        html = 'transferNotePrint.html'

    return render(request,html,todo)

@login_required(login_url='login')
def SessionView(request):
    val = int(request.GET.get('i'))
    todo = SesList(request)
    general = todo['general']
    kampuni = todo['kampuni']

    ss = shiftSesion.objects.get(pk=val,session__Interprise__company=kampuni.id)
    shell = ss.session.Interprise
    attach = attachments.objects.filter(Q(shift__session=ss.id)|Q(session=ss.id))

    if not general:
        shell = todo['shell']
        ss = shiftSesion.objects.get(pk=val,session__Interprise=shell.id)

   
    tAdj = []
    flP = shiftPump.objects.filter(shift__session=ss) 
    tanks = flP.distinct('pump__tank')
    adj = None
    sesadj = adjustments.objects.filter(session=ss) 
    hasAdjst = False
    for t in tanks:
        rcq = float(receivedFuel.objects.filter(receive__ses=ss,To=t.pump.tank).aggregate(qty=Sum('qty'))['qty'] or 0)
       
        sesFlow = float(flP.filter(pump__tank=t.pump.tank).aggregate(qty=Sum('qty'))['qty'] or 0) 
        Bses =  float(t.pump.tank.qty) + (sesFlow - rcq)
        AFlow = float(t.pump.tank.qty) - rcq
        tAdj.append({
            'Bses':Bses,
            'AFlow':AFlow,
            'sesFlow':sesFlow,
            'rcq':rcq,
            'tank':t.pump.tank,
            'stick':0,
            'diff':0,
            'read':t.pump.tank.qty
        })

    if sesadj.exists():
        tanks = tankAdjust.objects.filter(adj__session=ss)
        hasAdjst = True
        tAdj = []
        adj = sesadj.last()
        for t in tanks:
            rcq = float(receivedFuel.objects.filter(receive__ses=ss,To=t.tank).aggregate(qty=Sum('qty'))['qty'] or 0)
            sesFlow = float(flP.filter(pump__tank=t.tank).aggregate(qty=Sum('qty'))['qty'] or 0) 
            Bses =  float(t.read) + (sesFlow - rcq)

            AFlow = float(t.read) - rcq
            
            tAdj.append({
                'Bses':Bses,
                'rcq':rcq,
                'AFlow':AFlow,
                'sesFlow':sesFlow,
                'tank':t.tank,
                'stick':t.stick,
                'diff':t.diff,
                'read':t.read
            })
        
    IsLast = shiftSesion.objects.filter(session__Interprise=shell).last() == ss
    
  

    

    Fld = flP.distinct('Fuel') 
    FuelEv = []
    TFlowQ = 0
    TFlowA = 0
    TtrA= 0
    TtrQ = 0
    TsaA = 0
    TsaQ = 0
    TexpA =0 
    TexpQ =0 
    TpmpA =0 
    TpmpQ =0 

    for fl in Fld:

        sale = saleList.objects.filter(sale__session=ss,sale__shiftBy=None,theFuel=fl.Fuel.id).annotate(amount=F('qty_sold')*F('sa_price'))

        tr = transFromTo.objects.filter(shift__shift__session=ss,shift__Fuel=fl.Fuel.id).annotate(worth=F('qty')*F('saprice'))
        exp = rekodiMatumizi.objects.filter(fromShift__shift__session=ss,Fuel=fl.Fuel.id)
        FlowQ = flP.filter(Fuel=fl.Fuel.id).aggregate(Qty=Sum('qty'))['Qty'] or 0
        FlowA = flP.filter(Fuel=fl.Fuel.id).aggregate(Amo=Sum('amount'))['Amo'] or 0
        trA = tr.aggregate(Amo=Sum('worth'))['Amo'] or 0
        trQ = tr.aggregate(Sum('qty'))['qty__sum'] or 0
        saA = sale.aggregate(Sum('amount'))['amount__sum'] or 0
        saQ = sale.aggregate(Sum('qty_sold'))['qty_sold__sum'] or 0
        expA = exp.aggregate(Sum('kiasi'))['kiasi__sum'] or 0
        expQ = exp.aggregate(Sum('fuel_qty'))['fuel_qty__sum'] or 0
        
        pmpA = FlowA - (trA+saA+expA)
        pmpQ = FlowQ - (trQ+saQ+expQ)
    
        FuelEv.append({
            'Fuel':fl.Fuel,
            'FlowA':FlowA,
            'FlowQ':FlowQ,
            'price':fl.price,
            'trA':trA,
            'trQ':trQ,
            'saA':saA,
            'saQ':saQ,
            'expA':expA,
            'expQ':expQ,
            'pmpQ':pmpQ,
            'pmpA':pmpA

        })

        TFlowQ += FlowQ
        TFlowA += FlowA
        TtrA += trA
        TtrQ += trQ
        TsaA += saA
        TsaQ += saQ
        TexpA +=expA 
        TexpQ +=expQ 
        TpmpA +=pmpA 
        TpmpQ +=pmpQ 


           
    shft = shifts.objects.filter(session=ss)
    shfts = []
    TotPSA = 0
    TotEXP = 0
    TotCAB = 0
    TotREQ = 0
    TotPAID = 0
    TotLPR = 0

    for s in shft:
         
        sale = saleList.objects.filter(shift__shift=s,sale__shiftBy=None).annotate(amount=F('qty_sold')*F('sa_price'))
        tr = transFromTo.objects.filter(shift__shift=s).annotate(worth=F('qty')*F('saprice'))
        exp = rekodiMatumizi.objects.filter(fromShift__shift=s)
        cashB = wekaCash.objects.filter(shift=s.id,biforeShift=True)



        exclude = {
            'cashB':cashB,
            'cashBA':cashB.aggregate(Amo=Sum('Amount'))['Amo'] or 0,
            'trAmo':tr.aggregate(Amo=Sum('worth'))['Amo'] or 0,

            # 'salep':sale.aggregate(Sum('payed'))['payed__sum'] or 0,
            'saleA':sale.aggregate(Sum('amount'))['amount__sum'] or 0,
            'sale':sale.aggregate(Sum('qty_sold'))['qty_sold__sum'] or 0,
            'tr':tr.aggregate(Sum('qty'))['qty__sum'] or 0,

            'expfA':exp.filter(fuel_cost__gt=0).aggregate(Sum('kiasi'))['kiasi__sum'] or 0,

            'expf':exp.aggregate(Sum('fuel_qty'))['fuel_qty__sum'] or 0,
            'expamo':exp.filter(fuel_cost=0).aggregate(Sum('kiasi'))['kiasi__sum'] or 0

        }

        
       
        pmps =  shiftPump.objects.filter(shift=s.id)
        fl_shp = pmps.distinct('Fuel')
        flt = []
        for fl in fl_shp:
            flt.append({
                'f':fl,
                'totA':pmps.filter(Fuel=fl.Fuel.id).aggregate(Amo=Sum('amount'))['Amo'] or 0,
                'totQ':pmps.filter(Fuel=fl.Fuel.id).aggregate(Qty=Sum('qty'))['Qty'] or 0,
               
            
            })
        totQ =  pmps.aggregate(Qty=Sum('qty'))['Qty'] or 0  
        totA =  s.amount + exclude['expamo']+exclude['cashBA']
        toexludeA = exclude['saleA'] + exclude['trAmo'] + exclude['expfA']+exclude['expamo']+exclude['cashBA']
        toexludeQ = exclude['sale'] + exclude['tr'] + exclude['expf']



        

        lossprof = s.paid - s.amount
        calcA = {
            'PmpSA':totA,
            'PmpSQ':totQ - toexludeQ,
            'shQ':totQ,
            'shA':s.amount + toexludeA,
            'lossProf':abs(lossprof)
        
        }    

        TotPSA += totA
        TotEXP += exclude['expamo']
        TotCAB +=exclude['cashBA']
        TotREQ += s.amount
        TotPAID += s.paid
        TotLPR += lossprof

        shfts.append({
            'trf':s,
            'pmps':pmps,
            'disp':pmps.distinct('pump__station'),
            'fuel':flt,
            'exclude':exclude,
           'calcA':calcA,


        })
    
    todo.update({
        'ses':ss,
        'trf':ss,
        'shifts':shfts,
        'TotPSA':TotPSA,
        'TotEXP':TotEXP,
        'TotCAB':TotCAB,
        'TotREQ':TotREQ,
        'TotPAID':TotPAID,
        'TotLPR':TotLPR,
        'isSessionView':True,
        'FuelEv':FuelEv,
        'attach':attach,
        'TFlowQ':TFlowQ,
        'TFlowA':TFlowA,
        'TtrA':TtrA,
        'TtrQ' :TtrQ,
        'TsaA' :TsaA,
        'TsaQ' :TsaQ,
        'TexpA' : TexpA,
        'TexpQ' : TexpQ,
        'TpmpA' :TpmpA,
        'TpmpQ' :TpmpQ,
        'IsLast':IsLast,
        'hasAdj':hasAdjst,
        'Adj_tanks':tAdj,
        'adj':adj,


    })
    
    html = 'sessionView.html'
    pr = int(request.GET.get('t',0))
    lang = int(request.GET.get('lang',0))

    if pr:
        todo.update({
            'langSet':lang
        })
        html = 'sessionViewPrint.html'

    return render(request,html,todo)


@login_required(login_url='login')
def savaAdjst(request):
    todo = todoFunct(request)
    if request.method == "POST":
        try:
            tanks = json.loads(request.POST.get('tanks'))
            move = int(request.POST.get('move',0))
            cont = int(request.POST.get('cont',0))
            op = int(request.POST.get('op',0))
            desc = request.POST.get('desc')
            general = todo['general']
            shell = todo['shell']
            cheo = todo['cheo']
            kampuni = todo['kampuni']
            useri = todo['useri']
            manager = todo['manager']

            if useri.admin or manager:
                Sup = UserExtend.objects.get(pk=op,tankSup=True)
                
                adj = adjustments()
                entry = adjustments.objects.filter(Interprise=shell)
                code = invoCode(entry)

                adj.code = TCode({'code':code,'shell':shell.id}) 

                adj.Invo_no = int(code)
                adj.tarehe = datetime.datetime.now(tz=timezone.utc)
                adj.operator =  Sup
                adj.by = cheo
                adj.Interprise = shell
                adj.maelezo = desc
                if move:
                    TankContainer = tankContainer.objects.get(pk=cont,compan=kampuni)
                    adj.container = TankContainer
                else:
                    
                    Lses = shiftSesion.objects.filter(session__Interprise=shell).last()
                    
                    if Lses.complete:
                        sesAdj = adjustments.objects.filter(session=Lses)
                        if not sesAdj.exists():
                            adj.session = Lses
                
                adj.save()

                for t in tanks:
                    TAdj = tankAdjust()
                    tankAdj = fuel_tanks.objects.get(pk=t['val'],Interprise__company=kampuni)
                    init = float(tankAdj.qty)
                    stick = float(t['stick'])
                    TAdj.adj = adj
                    TAdj.tank = tankAdj
                    TAdj.read=init
                    TAdj.stick = stick
                    TAdj.fuel = tankAdj.fuel
                    TAdj.diff = float(stick-init)
                    TAdj.cost = float(tankAdj.cost)
                    TAdj.price = float(tankAdj.price)
                    TAdj.save()

                    tankAdj.qty = stick
                    tankAdj.save()

                data = {
                    'success':True,
                    'swa':'Taarifa za marekebisho kwenye tanki yamehifadhiwa kikamilifu',
                    'eng':'Tank Fuel adjustment saved successfully',
                    'id': adj.id
                }

                return JsonResponse(data)



            else:
                data = {
                    'success':False,
                    'swa':'hauna ruhusa hii kwa sasa tafadhari wasiliana na uongozi',
                    'eng':'You have no permission by now please contact admin'
                }

          
        except:
            data = {
                'success':False,
                'swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi',
                'eng':'the action was not successfully please try again correctly'
            }
            return JsonResponse(data)
        
    else:

        return render(request,'pagenotFound.html',todo) 

@login_required(login_url='login')
def TankAdjst(request):
    todo = todoFunct(request)
    try:
        ss = int(request.GET.get('ses',0))
       

        shell = todo['shell']
    
           

        todo.update({
            'isAdjst':True,
           
        })    
        if ss:
            try:

                
                ses = shiftSesion.objects.get(pk=ss,session__Interprise=shell,complete=True)
                todo.update({
                    'ses':ses
                    
                })
            except:
                pass    
        

        return render(request,'adjustments.html',todo)
    except:
        return render(request,'pagenotFound.html',todo)
    
    
@login_required(login_url='login')
def getStationData(request):
    if request.method == 'POST':
        try:
            todo = todoFunct(request)
            kampuni = todo['kampuni']
            tt = int(request.POST.get('tt',0))
            is_pu = int(request.POST.get('is_pu',0))
            cont = int(request.POST.get('cont',0))

            tr_tanks = todo['tr_tank'].annotate(cont=F('tank'),Fname=F('fuel__name'),Fuel=F('fuel')).values()
            pmp_tanks = todo['shell_tanks'].annotate(Fuel=F('fuel'),Fname=F('fuel__name')).values()


            disp = todo['disp'].annotate(dis_name=F('station__name')).values()
            pumps = todo['tr_pump'].annotate(Fuel=F('tank__fuel'),Fname=F('tank__fuel__name'),disp_name=F('station__name'),AF_name=F('Incharge__user__first_name'),AL_name=F('Incharge__user__last_name')).values()
            
            othF = []
           
            if tt:
                if is_pu:
                    pmp_tanks = fuel_tanks.objects.filter(Interprise__company=kampuni,moving=False).annotate(shell=F('Interprise'),Fuel=F('fuel'),Fname=F('fuel__name')).values()
                    pu = Purchases.objects.get(pk=cont,record_by__company=kampuni)
                    pL = PuList.objects.filter(pu=pu)
                    for p in pL:
                        othF.append({
                            'id':p.id,
                            'Fuel':p.Fuel.id,
                            'fname':p.Fuel.name,
                            'qty':p.qty - p.rcvd,
                            'othTr':False,
                            'pu':True,
                            'tr':pu.id,
                            'cost':p.cost
                        })
                else:

                    trRec = transFromTo.objects.filter(to=None,transfer__record_by__Interprise__company=kampuni,qty__gt=F('taken'))
                    theTr = trRec.distinct('transfer')
                    
                    for tr in theTr:
                        trRecs = trRec.filter(transfer=tr.transfer.id)
                        distF = trRecs.distinct('Fuel')
                        for d in distF:

                            getF = trRecs.filter(Fuel=d.Fuel.id).annotate(fcost=F('qty')*F('cost'))
                            TotCost = getF.aggregate(sumi=Sum('fcost'))['sumi']
                            fqty = getF.aggregate(sumi=Sum(F('qty')-F('taken')))['sumi']

                            othF.append({
                                'Fuel':d.Fuel.id,
                                'fname':d.Fuel.name,
                                'qty':fqty,
                                'othTr':True,
                                'pu':False,
                                'tr':d.transfer.id,
                                'cost':TotCost/fqty
                            })
         
            data = {
                'success':True,
                'sta_tanks':list(pmp_tanks),
                'tr_tanks':list(tr_tanks),
                'disp':list(disp),
                'pumps':list(pumps),
                'otherF':othF,
            
            }

            return JsonResponse(data)

        except:
            data = {'success':False}
            return JsonResponse(data)

    else:
        data = {'success':False}
        return JsonResponse(data)
    
@login_required(login_url='login')
def FuelTrans(request):
    todo = todoFunct(request)
    try:
        ss = int(request.GET.get('ses',0))
        todo.update({
            'istransfer':True,
            'isTrPanel':True
        })    
        if ss:
            try:
                shell = todo['shell']
                ses = shiftSesion.objects.get(pk=ss,session__Interprise=shell,complete=True)
                todo.update({
                    'ses':ses
                    
                })
            except:
                pass    
        

        return render(request,'transferFuel.html',todo)
    except:
        return render(request,'pagenotFound.html',todo)
    
@login_required(login_url='login')
def FuelReceive(request):
    todo = todoFunct(request)
    try:
        kampuni = todo['kampuni'] 
        trRec = transFromTo.objects.filter(to=None,transfer__record_by__Interprise__company=kampuni,qty__gt=F('taken'))
        theTr = trRec.distinct('transfer')
        othF = []
        for tr in theTr:
            trRecs = trRec.filter(transfer=tr.transfer.id)
            distF = trRecs.distinct('Fuel')
            for d in distF:
                getF = trRecs.filter(Fuel=d.Fuel.id).annotate(fcost=F('qty')*F('cost'))
                TotCost = getF.aggregate(sumi=Sum('fcost'))['sumi']
                fqty = getF.aggregate(sumi=Sum(F('qty')-F('taken')))['sumi']

                othF.append({
                    'Fuel':d.Fuel,
                    'qty':fqty,
                    'othTr':True,
                    'pu':False,
                    'tr':d.transfer.id,
                    'cost':TotCost/fqty
                })

        todo.update({
            'isreceive':True,
            'otherTr':theTr,
            'trFuel':othF
            
        })    
          

        return render(request,'receiveFuel.html',todo)
    except:
        return render(request,'pagenotFound.html',todo)
    

@login_required(login_url='login')
def viewShift(request):
    val = int(request.GET.get('i'))
    todo = shList(request)

    general = todo['general']
    
    kampuni = todo['kampuni']

    sh = shifts.objects.get(pk=val,record_by__Interprise__company=kampuni.id)
    shell = sh.record_by.Interprise

    if not general:
        shell = todo['shell']
        sh = shifts.objects.get(pk=val,record_by__Interprise=shell.id)
        

    if sh.To is  None:
        shby = InterprisePermissions.objects.get(user=sh.by,Interprise=shell.id)
        return redirect(f'/salepurchase/StartEndShift?usr={shby.id}')
       
  

    attach = attachments.objects.filter(Q(shift=sh.id)|Q(session=sh.session.id))
 
    sale = saleList.objects.filter(shift__shift=sh,sale__shiftBy=None).annotate(amount=F('qty_sold')*F('sa_price'))
    tr = transFromTo.objects.filter(shift__shift=sh).annotate(worth=F('qty')*F('saprice'))
    exp = rekodiMatumizi.objects.filter(fromShift__shift=sh)
    cashB = wekaCash.objects.filter(shift=sh.id,biforeShift=True)



    exclude = {
        'cashB':cashB,
        'cashBA':cashB.aggregate(Amo=Sum('Amount'))['Amo'] or 0,
        'trAmo':tr.aggregate(Amo=Sum('worth'))['Amo'] or 0,

        # 'salep':sale.aggregate(Sum('payed'))['payed__sum'] or 0,
        'saleA':sale.aggregate(Sum('amount'))['amount__sum'] or 0,
        'sale':sale.aggregate(Sum('qty_sold'))['qty_sold__sum'] or 0,
        'tr':tr.aggregate(Sum('qty'))['qty__sum'] or 0,

        'expfA':exp.filter(fuel_cost__gt=0).aggregate(Sum('kiasi'))['kiasi__sum'] or 0,

        'expf':exp.aggregate(Sum('fuel_qty'))['fuel_qty__sum'] or 0,
        'expamo':exp.filter(fuel_cost=0).aggregate(Sum('kiasi'))['kiasi__sum'] or 0

    }

    pmps = fuel_pumps.objects.filter(tank__Interprise=shell.id,Incharge=None)
    fl = pmps.distinct('tank__fuel')

    # spancer = pmps.distinct('station')
    shp = shiftPump.objects.filter(shift=sh.id)
    fl_shp = shp.distinct('Fuel')
    spancer_shp = shp.distinct('pump__station')
    flt = []
    for fl in fl_shp:
        flt.append({
            'f':fl,
            'totA':shp.filter(Fuel=fl.Fuel.id).aggregate(Amo=Sum('amount'))['Amo'] or 0,
            'totQ':shp.filter(Fuel=fl.Fuel.id).aggregate(Qty=Sum('qty'))['Qty'] or 0,
          
        })

    totQ =  shp.aggregate(Qty=Sum('qty'))['Qty'] or 0  
    totA =  sh.amount + exclude['expamo']+exclude['cashBA']
    toexludeA = exclude['saleA'] + exclude['trAmo'] + exclude['expfA']+exclude['expamo']+exclude['cashBA']
    toexludeQ = exclude['sale'] + exclude['tr'] + exclude['expf']
    

    calcA = {
        'PmpSA':totA,
        'PmpSQ':totQ - toexludeQ,
        'shQ':totQ,
        'shA':sh.amount + toexludeA,
        'lossProf':abs(sh.amount - sh.paid)
       
    }

    todo.update({
        'fshp':flt,
         'calcA':calcA,
        'shpmp':shp,
        'spancer_shp':spancer_shp,
        'attach':attach,
        'trf':sh,
         'sale':sale,
         'expF':exp.filter(fuel_qty__gt=0),
         'expA':exp.filter(fuel_qty=0),
         'exp':exp,
         'trd':tr,
         'exclude':exclude,
        'isShiftView':True
    })

    html = 'shiftView.html'
    pr = int(request.GET.get('t',0))
    lang = int(request.GET.get('lang',0))

    if pr:
        todo.update({
            'langSet':lang
        })
        html = 'shiftViewPrint.html'

    return render(request,html,todo)

@login_required(login_url='login')
def viewFuelReceive(request):
    try:
        val = int(request.GET.get('i'))
        todo = recList(request)
        kampuni = todo['kampuni']
        useri = todo['useri']
        general = todo['general']
        tr = ReceveFuel.objects.filter(Q(by__Interprise__company=kampuni)|Q(Tocont__cont__compan=kampuni),pk=val)
        if not general and not useri.admin:
            shell = todo['shell']
            tr = tr.filter(by__Interprise=shell.id)
        
        trf = tr.last()
        attach = attachments.objects.filter(receive=trf.id)
        rcd = receivedFuel.objects.filter(receive=trf.id).annotate(thamani=(F('qty')*F('price')))
        Tqty = rcd.aggregate(sumi=Sum('qty'))['sumi']
        Tworth = rcd.aggregate(sumi=Sum('thamani'))['sumi']

        adj = adjustments.objects.filter(receive=trf,Interprise__company=kampuni)
        
        # print(tr.count())
        tankAdj = None
        Adj = None
        diffSum = 0
        amoSum = 0
        hasAdj = adj.exists()
        if hasAdj:
            Adj = adj.last()
            tankAdj = tankAdjust.objects.filter(adj=Adj)
       

            diffSum = tankAdj.aggregate(diff=Sum('diff') )['diff'] or 0
            amoSum = tankAdj.aggregate(diff=Sum(F('diff') * F('price')))['diff'] or 0

        todo.update({
            'attach':attach,
            'trf':trf,
            'rcd':rcd,
            'isreceiveView':True,
            'Tqty':Tqty,
            'Tworth':Tworth,
            'Adj':Adj,
            'tankAdj':tankAdj,
            'diffSum':diffSum,
            'amoSum':amoSum,
            'hasAdj':hasAdj


        })

        html = 'receivenoteView.html'
        pr = int(request.GET.get('t',0))
        lang = int(request.GET.get('lang',0))

        if pr:
            todo.update({
                'langSet':lang
            })
            html = 'receivenotePrint.html'

        return render(request,html,todo)
    except:
        return render(request,'pagenotFound.html')
# pay  INVOINCE .........................................//
@login_required(login_url='login')
def  lipaInvo(request):
      
      if request.method == 'POST':
            try:
                  value=int(request.POST.get('invo'))
                  ac=int(request.POST.get('ac'))
                  pall=int(request.POST.get('all',0))
                  isCredit = int(request.POST.get('isCredit',0))
           

                  paid_amo = float(request.POST.get('pay_amo'))  
                  pay_d = request.POST.get('date')
                  desc = request.POST.get('desc','')
                  
                  kutoka = ''
                  todo = todoFunct(request)
                  cheo = todo['cheo']
                  shell = cheo.Interprise
                  kampuni = todo['kampuni']

                  acc = PaymentAkaunts.objects.get(pk=ac,Interprise=shell.id)

                  ilolipwa = 0
                  malipo = 0
                  kiasi = 0
                  bill = None 
                  cust = None

                  if pall:
                     cust = wateja.objects.get(pk=value,Interprise__company=kampuni.id)
                     bill = fuelSales.objects.filter(customer=cust,payed__lt=F('amount'))
              
                     kutoka = cust.jina
                     ilolipwa = float(bill.aggregate(lipwa=Sum('payed'))['lipwa'])
                     malipo = float(paid_amo+ilolipwa) 
                     kiasi = float(bill.aggregate(kiasi=Sum('amount'))['kiasi'])
                  else:    
                        
                        bill = fuelSales.objects.get(by__Interprise=shell,pk=value)
                        ilolipwa = float(bill.payed)
                        malipo =   float(paid_amo+ilolipwa) 
                        kiasi = float(bill.amount) 
                        kutoka = bill.theFuel.name+" Sales"
                        
                  manager = todo['manager']
                  useri = todo['useri']


                  after={
                        'pay':True,  
                        'success':True,
                        'msg_swa' : 'Data za Malipo ya ankara zimehifadhiwa kikamilifu' ,
                        'msg_eng' : 'Invoice Payment recorded succefully',
                  }
            
                  if  useri.admin or manager:
                  
                        if malipo <= kiasi and malipo>0:
                            #   bill.akaunt = PaymentAkaunts.objects.get(pk=ac,Interprise=duka.Interprise.id)   

                            #   if  malipo != float(bill.amount):
                            #         bill.due_date = pay_d
                              lipwaAmo = paid_amo

                              wekakwa= acc
                              beforweka=float(wekakwa.Amount)    
                              weka = wekaCash()
                              weka.Akaunt = wekakwa
                              weka.Amount = float(lipwaAmo)
                              weka.before = beforweka               
                              weka.After = float(beforweka + lipwaAmo) 
                              weka.kutoka = kutoka
                              weka.maelezo = desc
                              weka.tarehe = datetime.datetime.now(tz=timezone.utc)
                              weka.by=useri
                              weka.Interprise=shell
                              weka.mauzo=True
                              weka.tInvo = len(bill)
                              weka.tDebt = float(bill.aggregate(sumi=Sum(F('amount')-F('payed')))['sumi'])
                            #   if pall:
                              weka.customer = cust
                            #   else:
                            #     weka.sales = bill
                              if not wekakwa.onesha:
                                    weka.usiri =True               
                              wekakwa.Amount = float(beforweka + lipwaAmo)   
                              wekakwa.save()              
                              weka.save()

                              if not pall: 
                                bill.payed = malipo
                                bill.save()
                              else:
                                  for b in bill.order_by('pk'):
                                      if paid_amo > 0:  
                                        deni = float(b.amount - b.payed)
                                        lipwa = float(b.payed)
                                        theP = paid_amo
                                        if deni < paid_amo:
                                            b.payed = float(lipwa + deni)
                                            paid_amo = paid_amo - deni
                                            theP = deni
                                        else:
                                            b.payed = float(lipwa + paid_amo)
                                            paid_amo = 0  
                                            exit  
                                        b.save()

                                        if b.cdorder is not None:
                                            cdOd = b.cdorder
                                            cdOd.paid = float(float(cdOd.paid)+float(theP))
                                            cdOd.save()

                                        custP = CustmDebtPayRec()  
                                        custP.sale = b
                                        custP.pay = weka   
                                        custP.Debt =  deni 
                                        custP.Apay =  float(theP)
                                        custP.save()
                                          
                                        



                            #   acc.Amount = float(float(acc.Amount)+lipwaAmo)
                            #   acc.save()
                              
                        else:
                              after={
                                    'pay':True,  
                                    'success':False,
                                    'msg_swa' : 'Data za Malipo ya ankara hazijafanikiwa  kutokana na kiasi kinacholipwa kuzidi kiasi halisi cha ankara' ,
                                    'msg_eng' : 'Invoice Payment was not recorded, because the paid amount exceeds the invoice amount',
                              }     
                  else:
                        after={
                                    'pay':True,  
                                    'success':False,
                                    'msg_swa' : 'Data za Malipo ya ankara hazijafanikiwa  kutokana na akaunti ya malipo kutokutambulika tafadhari jaribu tena kwa usahihi' ,
                                    'msg_eng' : 'Invoice Payment was not recorded, because The selected payment account does not exists please again to submit payment correctly',
                              }
                  return JsonResponse(after)    
            except:
                  data={
                         
                                    'success':False,
                                    'msg_swa' : 'Oparesheni haikufanikiwa kutokana na hitilafu tafadhari jaribu tena' ,
                                    'msg_eng' : 'Action was not successfully please try again',
                              
                  }  

                  return JsonResponse(data)

         
      else:
         return render(request,'pagenotFound.html',todoFunct(request))      

    
@login_required(login_url='login')
def viewFuelSales(request):
    val = int(request.GET.get('i'))
    todo = saList(request)

    general = todo['general']
    kampuni = todo['kampuni']

    tr = fuelSales.objects.filter(pk=val,by__Interprise__company=kampuni).annotate(debt=F('amount')-F('payed'))
    if not general:
        shell = todo['shell']
        tr = tr.filter(by__Interprise=shell)
   
    # print(tr.count())

    trf = tr.last()

    attach = attachments.objects.filter(sales=trf.id)
    saL = saleList.objects.filter(sale=trf).annotate(amounti=F('sa_price_og')*F('qty_sold'),pamo=F('sa_price')*F('qty_sold'))

   
    akaunts = wekaCash.objects.filter(sales=trf.id,saRec=False).order_by('-pk')

    baki = trf.amount - trf.payed

    total_og = saL.aggregate(sumi=Sum('amounti'))['sumi'] or 0
    disc = total_og - trf.amount
  
    todo.update({
        'attach':attach,
        'trf':trf,
        
        'isSalesView':True,
        'malipo':akaunts,  
        'baki':baki,
        'tot_og':total_og,
        'disc':disc,
        'saList':saL
    })

    html = 'salesView.html'
    pr = int(request.GET.get('t',0))
    lang = int(request.GET.get('lang',0))

    if pr:
        pmpA = saL.distinct('shift__shift__by')
        todo.update({
            'langSet':lang,
            'pmpA':pmpA
        })
        html = 'salesViewPrint.html'

    return render(request,html,todo)


@login_required(login_url='login')
def addAttach(request):
    if request.method == "POST":
        try:
            file = request.FILES['attachment']
            tr = int(request.POST.get('tr',0))
            sh = int(request.POST.get('sh',0))
            rc = int(request.POST.get('rc',0))
            sa = int(request.POST.get('sa',0))
            ses = int(request.POST.get('ses',0))
            adj = int(request.POST.get('adj',0))
            pu = int(request.POST.get('pu',0))

            attName = request.POST.get('attach_name')
            printDoc = int(request.POST.get('printedDoc',0))

            todo = todoFunct(request)
            manager = todo['manager']
            useri = todo['useri']
            kampuni = todo['kampuni']
                  
            if useri.admin or manager:
                gcs_storage = settings.GCS_STORAGE_INSTANCE
                ext = file.name.split('.')[-1]
                filename = f"attachments/{kampuni.id}_{int(time.time())}.{ext}"
                path = gcs_storage.save(filename, file)

                att = attachments()
                att.file = path
                att.date = datetime.datetime.now(tz=timezone.utc)
                att.by = useri

                att.printedDocu = printDoc
                att.attach_name = attName

                # print(printDoc)

                if tr:
                    ftr=TransferFuel.objects.get(pk=tr)
                    att.transfer = ftr
                if rc:
                    ftr=ReceveFuel.objects.get(pk=rc)
                    att.receive = ftr

                if sa:
                    ftr=fuelSales.objects.get(pk=sa)
                    att.sales = ftr

                if sh:
                    ftr=shifts.objects.get(pk=sh)
                    att.shift = ftr

                if ses:
                    ftr=shiftSesion.objects.get(pk=ses)
                    att.session = ftr

                if adj:
                    ftr = adjustments.objects.get(pk=adj) 
                    att.adj = ftr

                if pu:
                    ftr = Purchases.objects.get(pk=pu) 
                    att.purchase = ftr

                att.save()    

                data = {
                    'success':True,
                    'msg_swa':'Kiambatanisho kimeongezwa kikamilifu',
                    'msg_eng':'Attachment added successfully'
                }

                return JsonResponse(data)

            else:
                data = {
                    'success':False,
                    'msg_swa':'Hauna ruhusa ya kitendo hiki kwa sasa tafadhari wasiliana na mhusika',
                    'msg_eng':'You have no permission for this action please contact admin'
                }
        except:
            data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena baadaye',
                'msg_eng':'The action was unsuccessfull please try again later'
            }

            return JsonResponse(data)
    else:
        data = {
            "success":False
        }
        return JsonResponse(data)

@login_required(login_url='login')
def fueltransfer(request):
    
    todo = traList(request)
    return render(request,'transfernotes.html',todo)

@login_required(login_url='login')
def soldFuel(request):
    todo = saList(request)
    return render(request,'sales.html',todo)

@login_required(login_url='login')
def fuelreceives(request):
    todo = recList(request)
    
    return render(request,'receivenotes.html',todo)


@login_required(login_url='login')
def changePrice(request):
    if request.method == "POST":
        try:
            pr = json.loads(request.POST.get('pr'))
            allSt = int(request.POST.get('all'))
            desc = request.POST.get('desc')

            todo = todoFunct(request)
            
            general = todo['general']
            useri = todo['useri']
            kampuni = todo['kampuni']

            if useri.admin:
                
                for p in pr:

                    price = float(p['price'])
                    fu = p['fuel']
                    Fu = fuel.objects.get(pk=fu)
                    tanks = fuel_tanks.objects.filter(Interprise__company=kampuni,fuel=fu)
                     

                    if price:

                        if allSt:
                            iniPr = tanks.last().price
                            tanks.update(price=float(price))
                            statn = Interprise.objects.filter(company=kampuni)
                            for st in statn:
                                change = fuelPriceChange()
                                change.Interprise = st
                                change.fuel = Fu
                                change.desc = desc
                                change.Bprice = float(iniPr)
                                change.Aprice = price
                                change.date = datetime.datetime.now(tz=timezone.utc)
                                change.by = useri
                                change.save()

                                usr = InterprisePermissions.objects.filter(Interprise=st,Allow=True) 
                                for us in usr:
                                    notify = notifications()
                                    notify.usr = us.user
                                    notify.price = change
                                    notify.date = datetime.datetime.now(tz=timezone.utc)
                                    notify.save()



                        else:
                            shell = todo['shell']
                            tanks = tanks.filter(Interprise=shell.id)
                            iniPr = tanks.last().price

                            tanks.update(price=float(price))

                            change = fuelPriceChange()
                            change.Interprise = shell
                            change.fuel = Fu
                            change.desc = desc
                            change.Bprice = float(iniPr)
                            change.Aprice = price
                            change.date = datetime.datetime.now(tz=timezone.utc)
                            change.by = useri
                            change.save()    
                            usr = InterprisePermissions.objects.filter(Interprise=shell,Allow=True) 
                            for us in usr:
                                notify = notifications()
                                notify.usr = us.user
                                notify.price = change
                                notify.date = datetime.datetime.now(tz=timezone.utc)
                                
                                notify.save()
                                

                data = {
                    'success':True,
                    'swa':'Bei imebadilishwa kikamilifu',
                    'eng':'Price changed successfully'
                } 
                return JsonResponse(data)
            else:
                data = {
                    'success':False,
                    'swa':'Hauna Ruhusa hii kwa sasa tafadhari wasiliana na uongozi',
                    'eng':'You have no permission for this action please contact admin'
                }

                return JsonResponse(data)
        except:
            data={
                'success':False,
                'swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
                'eng':'The action was not successfully please try again'
            }
            return JsonResponse(data)
    else:
        return render(request,'pagenotFound.html')

@login_required(login_url='login')
def startshift(request):
    if request.method == 'POST':
        try:
            pumps = json.loads(request.POST.get('pumps'))
       
            incharge = int(request.POST.get('incharge'))
            FrShift = int(request.POST.get('FrShift'))
            tFrom = request.POST.get('tFrom')
            ses = int(request.POST.get('ses'))

            todo = todoFunct(request)
            useri = todo['useri']
            manager = todo['manager']
            general = todo['general']
            cheo = todo['cheo']
            shell = cheo.Interprise
            

            data = {
                'success':True,
                'msg_swa':'Zamu tayari imeshaanzishwa',
                'msg_eng':'Shift started successfully'
            }

            if( useri.admin or manager) and not general:
                sh = shifts()
                inch = InterprisePermissions.objects.get(pk=incharge)
                ssn = shiftsTime.objects.get(pk=ses,Interprise=shell)
                
                sesSt = None
                sesSh = shiftSesion.objects.filter(session=ssn,date=date.today())
                if sesSh.exists():
                   sesSt = sesSh.last()
                else:
                    sesSt = shiftSesion()
                    sesSt.date = date.today()
                    sesSt.session = ssn
                    sesSt.save()

                if FrShift:
                    sh = shifts.objects.get(pk=FrShift,record_by__Interprise=cheo.Interprise,by=inch.user)
               
                else:
                    shfts = shifts.objects.filter(record_by__Interprise=cheo.Interprise.id)
                    code = invoCode(shfts)

                    sh.code = TCode({'code':code,'shell':shell.id})
                    sh.Invo_no = int(code)

                    sh.From = tFrom
                
                    sh.by = inch.user
                    sh.record_by = cheo
                    sh.session = sesSt
                
                    sh.save()

                for p in pumps:
                    pmp = fuel_pumps.objects.get(pk=p['pump'],tank__Interprise=shell.id)
                    shfp = shiftPump()
                    shfp.pump = pmp
                    shfp.Fuel = pmp.tank.fuel
                    shfp.shift = sh
                    shfp.initial = float(pmp.readings)
                    shfp.save()

                    pmp.fromi = tFrom
                    pmp.Incharge = inch.user
                    pmp.save()

                # try:
                    
                #     url = "https://messaging-service.co.tz/api/sms/v1/text/single"
                #     txt = f"Zamu yako katika Pambu {pmp.name} imeshaanza "
                #     txt+= f"na inasoma  lita.{read}"
                #     txt+=f"kama ilivyohakikiwa na {useri.user.first_name} {useri.user.last_name}({cheo.cheo})"
                #     phn = inch.user.phone
                #     phn = phn.replace("+","")

                    
                #     payload = json.dumps({
                #         "from": "fbiashara",
                #         "to": phn,
                #         "text": txt,
                #         "reference": "aswqetgcv"
                #     })
                #     headers = {
                #         'Authorization': 'Basic bXVzYWo6TXVzYUBtZTEy',
                #         'Content-Type': 'application/json',
                #         'Accept': 'application/json'
                #     }

                #     response = requests.request("POST", url, headers=headers, data=payload)
                # except:
                #     pass

            else:
                data = {
                    'success':False,
                    'msg_swa':'Hauna Ruhusa hii kwa sasa',
                    'msg_eng':'You have no permision for this'
                } 

            return JsonResponse(data)
                
        except:
            data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
                'msg_eng':'The action was not successfully please try again',
            }
            return JsonResponse(data)
        

@login_required(login_url='login')
def get_shift_data(request):
    todo = todoFunct(request)
    useri = todo['useri']
    manager = todo['manager']
    pump = int(request.POST.get('pump'))
    shell = todo['shell']

    shpump = fuel_pumps.objects.get(pk=pump,tank__Interprise=shell.id)

    shift = shifts.objects.get(pump=shpump,To=None)

    sale = saleList.objects.filter(shift__shift=shift,sale__shiftBy=None).aggregate(Sum('qty_sold'))['qty_sold__sum'] or 0
    tr = TransferFuel.objects.filter(shift=shift.id).aggregate(Sum('qty'))['qty__sum'] or 0
    exp = rekodiMatumizi.objects.filter(fromShift=shift.id)
    exp_fuel = exp.aggregate(Sum('fuel_qty'))['fuel_qty__sum'] or 0
    exp_amo = exp.filter(fuel_cost=0).aggregate(Sum('kiasi'))['kiasi__sum'] or 0

    data = {
        'success':True,
        'sale':sale,
        'tr':tr,
        'expf':exp_fuel,
        'expA':exp_amo
    }

    return JsonResponse(data)


@login_required(login_url='login')
def endshift(request):
    if request.method == 'POST':
        try:
            pumps = json.loads(request.POST.get('pumps'))
            # read = float(request.POST.get('fread'))
            incharge = int(request.POST.get('usr'))
            shift = int(request.POST.get('shift'))
            lossprof = int(request.POST.get('lossprof',0))
            tto = request.POST.get('shiftTo')
            remarks = request.POST.get('remarks')

            payed = json.loads(request.POST.get('acc'))
            totpaid = int(request.POST.get('totpay'))
            netReq = float(request.POST.get('netreqAmo'))

            todo = todoFunct(request)
            useri = todo['useri']
            manager = todo['manager']
            general = todo['general']
            cheo = todo['cheo']
            shell=todo['shell']
            kampuni = todo['kampuni']

            data = {
                'success':True,
                'msg_swa':'Zamu imekamirishwa kikamilifu',
                'msg_eng':'Shift Ended successfully'
            }

            if( useri.admin or manager) and not general:


                
                inch = InterprisePermissions.objects.get(pk=incharge)
                
                sh = shifts.objects.get(Q(record_by=cheo)|Q(record_by__Interprise__owner=useri),pk=shift,by=inch.user)
                
                

                sh.To = tto
                sh.amount = netReq
                
                sh.paid = totpaid
           
                # sh.final = float(read)
                sh.remarks = remarks
                sh.lossprof = lossprof
                # sh.puprice = float(pmp.tank.cost)
                # sh.saprice = float(pmp.tank.price)
                sh.save()
                sales = None   
                

              
                sales = fuelSales()
                entry = fuelSales.objects.filter(by__Interprise=shell)
                code = invoCode(entry)
                sales.code = TCode({'code':code,'shell':shell.id})
                sales.Invo_no = int(code)
                sales.by = cheo
                sales.shiftBy = sh
                # sales.theFuel = pmp.tank.fuel
                sales.session = sh.session
                sales.date = tto
                sales.recDate = datetime.datetime.now(tz=timezone.utc)

                sales.save()

                dpb = wekaCash.objects.filter(shift=sh,biforeShift=True).aggregate(sumi=Sum('Amount'))['sumi'] or 0
                expA = rekodiMatumizi.objects.filter(fromShift__shift=sh,fuel_qty=0).aggregate(sumi=Sum('kiasi'))['sumi'] or 0
              
                t_payed = float(dpb+expA)

                saleamo = float(0)

                for p in pumps:

                    pmpsh = shiftPump.objects.get(pk=p['pmp'],shift=sh)
                    pmp = pmpsh.pump
                    sh_diff = float(float(p['final'])-float(pmp.readings))
                    pmpsh.final = float(p['final'])
                    pmpsh.qty = sh_diff
                    pmpsh.cost = float(pmp.tank.cost)
                    pmpsh.price = float(pmp.tank.price)
                    pmpsh.amount = float(sh_diff * float(pmp.tank.price))
                    pmpsh.save()

               
                    sale = saleList.objects.filter(shift=pmpsh.id,sale__customer__Interprise__company=kampuni).aggregate(Sum('qty_sold'))['qty_sold__sum'] or 0
                    tr = transFromTo.objects.filter(shift=pmpsh.id).aggregate(Sum('qty'))['qty__sum'] or 0
                    exp = rekodiMatumizi.objects.filter(fromShift=pmpsh.id)

                    exp_fuel = exp.aggregate(Sum('fuel_qty'))['fuel_qty__sum'] or 0
                    exp_amo = exp.filter(fuel_cost=0).aggregate(Sum('kiasi'))['kiasi__sum'] or 0
                    
                    exclude = float(sale + tr + exp_fuel)
                    
                    pump_Sale = float(sh_diff - exclude)  

                    saleamo += float(pump_Sale*float(pmpsh.pump.tank.price)) 


                    saL = saleList()
                    saL.sale = sales 
                    saL.theFuel = pmpsh.pump.tank.fuel
                    saL.tank = pmpsh.pump.tank
                    saL.shift = pmpsh
                    saL.qty_sold = float(pump_Sale)
                    saL.cost_sold = float(pmpsh.pump.tank.cost)
                    saL.sa_price = float(pmpsh.pump.tank.price)
                    saL.sa_price_og = float(pmpsh.pump.tank.price)
                    saL.save()

                   


                    tank = pmp.tank
                    tank.qty =float(float(tank.qty) -sh_diff)
                    tank.save()
                    
                    pmp.fromi = None
                    pmp.Incharge = None
                    pmp.readings = float(p['final'])
                    pmp.save()
                 
                    
                
                for p in payed:
                    acc = PaymentAkaunts.objects.get(pk=p['ac'],Interprise__company=kampuni)
                    acc_b = acc.Amount
                    acc.Amount = float(float(acc.Amount) + float(p['amo']))
                    acc.save()

                    t_payed += float(p['amo'])

                    wk=wekaCash()
                    wk.Interprise = shell
                    wk.tarehe = tto
                    wk.Akaunt = acc

                    wk.Amount = float(p['amo'])
                    wk.before = float(acc_b)
                    wk.After = acc.Amount
                    wk.kutoka = "Mauzo"
                    wk.maelezo = ""
                    wk.mauzo = True
                    wk.by = useri
                    wk.shift = sh
                    wk.sales = sales
                    wk.save()

                sales.amount = saleamo
                sales.payed = t_payed 
                sales.save()

                data.update({
                    'id':sh.id
                })

                allSesSh = shifts.objects.filter(session=sh.session,To=None)
                
                if not allSesSh.exists():
                    ses = sh.session
                   
                    ses.complete = True
                    ses.save()

                    # Addjust pump sales during the shift if there is added fuel ....//
                    soldBreceive =  saleOnReceive.objects.filter(ses=ses)
                  
        

                    rcvdF =   receivedFuel.objects.filter(receive__ses=ses)
                    if rcvdF.exists():
                        tnks = rcvdF.distinct('To')
                        for rt in tnks:
                            stT = fuel_tanks.objects.get(pk=rt.To.id)
                            rcvqty = rcvdF.filter(To=rt.To.id).aggregate(sumi=Sum('qty'))['sumi'] or 0
                            stT.qty = float(float(stT.qty)+float(rcvqty))
                            stT.save()   
                        if soldBreceive.exists():
                            rcTanks  = soldBreceive.distinct('tank')
                            for rt in rcTanks:
                                TheTnk=soldBreceive.filter(tank=rt.tank)
                                BsoldCost = float(TheTnk.aggregate(sumi=Sum(F('qty')*F('cost')))['sumi'] or 0)
                                BsoldQty = float(TheTnk.aggregate(sumi=Sum('qty'))['sumi'] or 0)
                                shiftSale = saleList.objects.filter(sale__session=ses,shift__pump__tank=rt.tank,shiftBy__session=ses)
                                SoldQty = float(shiftSale.aggregate(sumi=Sum('qty_sold'))['sumi'] or 0)
                                soldAfterRc = float(SoldQty - BsoldQty)
                                Soldcost = soldAfterRc * float(rt.tank.cost) 
                                TotCost = float(float(BsoldCost) + float(Soldcost))
                                if SoldQty > 0:
                                    avgCost = TotCost/SoldQty
                                    shiftSale.update(cost_sold=float(avgCost))





                
                # try:
                    
                #     url = "https://messaging-service.co.tz/api/sms/v1/text/single"
                #     txt = f"Zamu yako katika Pambu {pmp.name} imemalizika "
                #     txt+= f"na inasoma  lita.{read}"
                #     txt+=f"kama ilivyohakikiwa na {useri.user.first_name} {useri.user.last_name}({cheo.cheo})"
                #     phn = sh.by.phone
                #     phn = phn.replace("+","")

                    
                #     payload = json.dumps({
                #         "from": "fbiashara",
                #         "to": phn,
                #         "text": txt,
                #         "reference": "aswqetgcv"
                #     })
                #     headers = {
                #         'Authorization': 'Basic bXVzYWo6TXVzYUBtZTEy',
                #         'Content-Type': 'application/json',
                #         'Accept': 'application/json'
                #     }

                #     response = requests.request("POST", url, headers=headers, data=payload)
                # except:
                #     pass

            else:
                data = {
                    'success':False,
                    'msg_swa':'Hauna Ruhusa hii kwa sasa',
                    'msg_eng':'You have no permision for this'
                } 

            return JsonResponse(data)
                
        except:
            data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
                'msg_eng':'The action was not successfully please try again',
            }
            return JsonResponse(data)


@login_required(login_url='login')
def pumps(request):
  todo = todoFunct(request)
  useri = todo['useri']
  shell = todo['shell']
  general = todo['general']
  kampuni = todo['kampuni']

  tanks = None 
  pumps=fuel_pumps.objects.filter(tank__Interprise__company=kampuni.id)
  pumpIncharge = None
  station = None

#   pumps.delete() 
  if  not general:
      pumps = pumps.filter(tank__Interprise=shell.id).order_by('-pk')
      tanks = fuel_tanks.objects.filter(Interprise=shell.id)
      pumpIncharge  = InterprisePermissions.objects.filter(Interprise=shell.id,pumpIncharge=True)
      station = PumpStation.objects.filter(Interprise=shell.id).order_by('-pk')
  todo.update({
      'pumps':pumps,
      'tanks':tanks,
      'Incharges':pumpIncharge,
      'ispump':True,
      'station':station
  })
  return render(request,'fuelpump.html',todo)

  
@login_required(login_url='login')
def theshiftsAttend(request):
  todo = todoFunct(request)
#   useri = todo['useri']
  
  general = todo['general']
  kampuni = todo['kampuni']
  
  pumpIncharge  = InterprisePermissions.objects.filter(Interprise__company=kampuni.id,pumpIncharge=True)
 

  shiftAttend = []

  if  not general:
      shell = todo['shell']
      pumpIncharge  = pumpIncharge.filter(Interprise=shell.id)

  for at in pumpIncharge:
        hasShift = None
        shift = shifts.objects.filter(by=at.user.id,To=None)
        if shift.exists():
            hasShift = shift.last()
        shiftAttend.append({
            'user':at,
            'hasShift':hasShift
        })

  todo.update({
 
   
      'Incharges':shiftAttend,
      'isShiftAttend':True,
     
  })
  return render(request,'pumpAttends.html',todo)

@login_required(login_url='login')
def StartEndShift(request):
  todo = todoFunct(request)
  useri = todo['useri']
  
  general = todo['general']
  kampuni = todo['kampuni']

  inch = int(request.GET.get('usr',0))
  by = None
  shift = None
  shp = None
  fl_shp = None
 

  if  not general:
      shell = todo['shell']
      by  = InterprisePermissions.objects.get(pk=inch,Interprise=shell.id,pumpIncharge=True)
     

      hasshift = shifts.objects.filter(by=by.user.id,To=None)
      if hasshift.exists():
            shift = hasshift.last()
            shp = shiftPump.objects.filter(shift=shift)
            fl_shp = shp.distinct('Fuel')
            spancer_shp = shp.distinct('pump__station')

            # print(spancer_shp.count())

            sale = saleList.objects.filter(shift__shift=shift.id,sale__shiftBy=None).annotate(amount=F('qty_sold')*F('sa_price'))
            tr = transFromTo.objects.filter(shift__shift=shift.id).annotate(worth=F('qty')*F('saprice'))
            exp = rekodiMatumizi.objects.filter(fromShift__shift=shift.id)

            cashB = wekaCash.objects.filter(shift=shift)

            tr_pump = fuel_pumps.objects.filter(Incharge=shift.by.id)
            disp = tr_pump.distinct('station')

            exclude = {
                'cashB':cashB,
                'cashBA':cashB.aggregate(Amo=Sum('Amount'))['Amo'] or 0,
                'trAmo':tr.aggregate(Amo=Sum('worth'))['Amo'] or 0,
                # 'salep':sale.aggregate(Sum('payed'))['payed__sum'] or 0,
                'saleA':sale.aggregate(Sum('amount'))['amount__sum'] or 0,
                'sale':sale.aggregate(Sum('qty_sold'))['qty_sold__sum'] or 0,
                'tr':tr.aggregate(Sum('qty'))['qty__sum'] or 0,
                'expf':exp.aggregate(Sum('fuel_qty'))['fuel_qty__sum'] or 0,
                'expfA':exp.filter(fuel_cost__gt=0).aggregate(Sum('kiasi'))['kiasi__sum'] or 0,
                'expamo':exp.filter(fuel_cost=0).aggregate(Sum('kiasi'))['kiasi__sum'] or 0

            }
            

            todo.update({
                'tr_pump':tr_pump,
                'disp':disp,
                'fshp':fl_shp,
                'sale':sale,
                'expA':exp.filter(fuel_cost=0),
                'expF':exp.filter(fuel_cost__gt=0),
                'exp':exp,
                'trd':tr,
                'exclude':exclude,
                'shpmp':shp,
                
                'spancer_shp':spancer_shp,
            })
      
      pmps = fuel_pumps.objects.filter(tank__Interprise=shell.id,Incharge=None)
      fl = pmps.distinct('tank__fuel')
      
      spancer = pmps.distinct('station')

      sessions = shiftsTime.objects.filter(Interprise=shell)


  todo.update({
      'trf':by,
      'shift':shift,
      'pumps':pmps.order_by('pk'),
      'fuel':fl,
      
      'sessions':sessions,
      'spancer':spancer,
      'isShiftAttend':True,
     
  })

  

  return render(request,'pumpAttendsView.html',todo)

@login_required(login_url='login')
@require_POST
def deleteShift(request):
    try:
        todo = todoFunct(request)
        shell = todo['shell']
        manager = todo['manager']
        useri = todo['useri']
        shift_id = int(request.POST.get('shift_id', 0))
        if not (manager or useri.admin):
            return JsonResponse({'success': False, 'eng': 'Permission denied.', 'swa': 'Ruhusa haijarusiwa.'})
        if not shift_id:
            return JsonResponse({'success': False, 'eng': 'No shift ID provided.', 'swa': 'Hakuna ID ya zamu iliyotolewa.'})
        
        shiftToD = shifts.objects.get(pk=shift_id, record_by__Interprise=shell.id,To=None)
        ses = shiftToD.session
        sale = saleList.objects.filter(shift__shift=shiftToD.id)
        for s in sale:
            theSale = s.sale
            s.delete()
            rems = saleList.objects.filter(sale=theSale.id)

            if not rems.exists():
                saleAmo = theSale.amount
                payedAmo = theSale.payed
                accs = wekaCash.objects.filter(sales=theSale.id)
                for ac in accs:
                    acc = ac.Akaunt
                    acc.Amount = float(float(acc.Amount) - float(payedAmo))
                    acc.save()
                    ac.delete()
                IsCreditor = theSale.cdorder
                if IsCreditor:
                    IsCreditor.consumed = float(float(IsCreditor.consumed) - float(saleAmo))
                    IsCreditor.save()

                theSale.delete()

        tr = transFromTo.objects.filter(shift__shift=shiftToD.id)
        for ft in tr:
            totnk = ft.to
            totnk.qty = float(float(totnk.qty) - float(ft.qty))
            totnk.save()
            theTr = ft.transfer
            ft.delete()
            remft = transFromTo.objects.filter(transfer=theTr.id)
            if not remft.exists():
                theTr.delete()

       
        exp = rekodiMatumizi.objects.filter(fromShift__shift=shiftToD.id)
        exp.delete()

        cashB = wekaCash.objects.filter(shift=shiftToD)
        if cashB.exists():  
            for bf in cashB:
                acc = bf.Akaunt
                acc.Amount = float(float(acc.Amount) - float(bf.Amount))
                acc.save()
                bf.delete()

        fuel_pumps.objects.filter(Incharge=shiftToD.by.id).update(Incharge=None,fromi=None)


        deleted, _ = shifts.objects.filter(pk=shiftToD.id, record_by__Interprise=shell.id).delete()



        if deleted > 0:
            sesShifts = shifts.objects.filter(session=ses.id)
            if not sesShifts.exists():
                ses.delete()

            shiftPump.objects.filter(shift=None).delete()

            return JsonResponse({'success': True, 'eng': 'Shift deleted successfully.', 'swa': 'Zamu imefutwa kikamilifu.'})
        else:
            return JsonResponse({'success': False, 'eng': 'No shift deleted.', 'swa': 'Hakuna zamu iliyofutwa.'})
    except Exception as e:
        return JsonResponse({'success': False, 'eng': f'Error: {str(e)}'})

@login_required(login_url='login')
@require_POST
def deleteCDSales(request):
    try:
        todo = todoFunct(request)
        useri = todo['useri']
        manager = todo['manager']
        shell = todo['shell']
        order_id = json.loads(request.POST.get('cd_order_ids', '[]'))
        if not (manager or useri.admin):
            return JsonResponse({'success': False, 'eng': 'Permission denied.', 'swa': 'Ruhusa haijarusiwa.'})

        saleL = saleList.objects.filter(pk__in=order_id,shift__shift__To=None, shift__shift__record_by__Interprise=shell.id)
        if saleL.exists():
            for saL in saleL:

                    sale = saL.sale
                    accs = wekaCash.objects.filter(sales=sale.id)
                    for ac in accs:
                        acc = ac.Akaunt
                        acc.Amount = float(float(acc.Amount) - float(sale.payed))
                        acc.save()
                        ac.delete()
                    IsCreditor = sale.cdorder
                    if IsCreditor:
                        IsCreditor.consumed = float(float(IsCreditor.consumed) - float(sale.amount))
                        IsCreditor.save()

                    sale.delete()  
                
            data = {
                'success':True,
                'swa':'Mauzo yamefutwa kikamilifu',
                'eng':'Sales deleted successfully'
            } 

            return JsonResponse(data)
        else:
            data = {
                'success':False,
                'swa':'Hakuna mauzo yaliyopatikana kufutwa',
                'eng':'No sales found to delete'
            }
            return JsonResponse(data)

    except:
        data = {
            'success':False,
            'swa':'Kitendo hakikufanikiwa tafadhari jaribu tena',
            'eng':'The action was unsuccessfull please try again'
        }
        return JsonResponse(data)
    

@login_required(login_url='login')
def fuell(request):
  todo = todoFunct(request)
  general = todo['general']
  admin = todo['admin']
  shell  = todo['shell']
  kampuni = todo['kampuni']

  mv = int(request.GET.get('mv',0))
  st = int(request.GET.get('st',0)) 
   
  wese = fuel_tanks.objects.filter(Interprise__company=kampuni)
  if not general:
      wese = wese.filter(Interprise=shell)

  movable = wese.filter(tank__compan=kampuni.id)
  if mv:
      wese = movable
  if st:
      wese = wese.filter(tank=None)    

  fuels = fuel.objects.all()
  contain = tankContainer.objects.filter(compan=kampuni.id).order_by('-pk')
  



  TFuel = wese.distinct('fuel')
  Fsum = [] 

  for f in TFuel:
      theF = wese.filter(fuel=f.fuel.id).annotate(Tcost=F('qty')*F('cost'),Tprice=F('qty')*F('price'),Tprof=(F('price')-F('cost'))*F('qty'))
      Fsum.append({
          'Fuel':f,
          
          'qty':theF.aggregate(qty=Sum('qty'))['qty'],
          'cost':theF.aggregate(theCost=Sum('Tcost'))['theCost'],
          'price':theF.aggregate(thePrice=Sum('Tprice'))['thePrice'],
          'prof':theF.aggregate(theProf=Sum('Tprof'))['theProf']
      })

  if not general:
      wese = wese.filter(Interprise = shell.id)
   
  tot_p = 0
  tcost = 0
  tprof = 0
  thefuel = []
  if wese.exists(): 
    for w in wese.order_by('-pk'):
        tp = w.price * w.qty
        tc = w.cost * w.qty
        prf = tp-tc
        thefuel.append({
            'name':w.name,
            'fuel':w.fuel.name,
            'units':w.fuel.units,
            'shell':w.Interprise,
            'qty':w.qty,
            'price':w.price,
            'cost':w.cost,
            'totcost':tc,
            'totpr':tp,
            'totprof':prf,
            'tank':w

        })

        tot_p += tp
        tcost += tc
        tprof += prf

  todo.update({
       'Tcost':tcost,
       'Tprice':tot_p,
       'Tqty':wese.aggregate(qtySum=Sum('qty'))['qtySum'],
       'Tprof':tprof,
        'fuels':fuels,
      'fuel':thefuel,
      'istank':True,
      'move':movable,
      'contain':contain,
      'Fsum':Fsum,
      'mv':mv,
      'st':st
  })
  return render(request,'fuel.html',todo)

@login_required(login_url='login')
def addTank(request):
    if request.method == "POST":
        # try:
            name = request.POST.get('name')
            Cont_name = request.POST.get('Cont_name')
            fue = int(request.POST.get('fuel'))
            qty = float(request.POST.get('qty'))
            cost = int(request.POST.get('cost'))
            price = int(request.POST.get('price'))
            Cont = int(request.POST.get("Cont"))
            newCont = int(request.POST.get("newCont"))
            moving = int(request.POST.get("moving"))
            maxm = float(request.POST.get("tankCapacity"))
            inch = int(request.POST.get("incharge",0))
            minm = float(request.POST.get("minAmo",0))

            

            todo = todoFunct(request)

            useri = todo['useri']
            shell = todo['shell']
            general = todo['general']
            kampuni = todo['kampuni']
            cheo = todo['cheo']
            if useri.admin and not general:
                Container = None
                if moving:
                    if newCont:
                        Container = tankContainer()
                        Container.compan = kampuni
                        Container.name = Cont_name
                        if inch:
                            inCh = UserExtend.objects.get(pk=inch,company=kampuni)
                            Container.by = inCh

                        Container.save()
                    else:
                        Container = tankContainer.objects.get(pk=Cont,compan=kampuni)


       

                oil = fuel.objects.get(pk=fue)
                tank = fuel_tanks()
                tank.name = name
                tank.Interprise = shell
                tank.fuel = oil
                tank.qty = float(qty)
                tank.cost = float(cost)
                tank.price = float(price)
                tank.moving = moving
                if moving:
                    tank.tank = Container
                tank.maxm = maxm
                tank.minm = minm
                tank.save()

                # Add it to adjusment to track the date that the tank was added and its fuel qty
                adj = adjustments()
                adj.by = cheo  
                adj.tarehe = datetime.datetime.now(tz=timezone.utc)
                adj.code = TCode({'code':invoCode(adjustments.objects.filter(by__user__company=kampuni)),'shell':shell.id})
                adj.Invo_no = int(invoCode(adjustments.objects.filter(by__user__company=kampuni)))
                adj.Interprise = shell
                adj.container = Container
                adj.save()

                adjL = tankAdjust()
                adjL.adj = adj
                adjL.tank = tank
                adjL.fuel = tank.fuel
                adjL.read = float(qty)
                adjL.stick = float(qty)
                
                adjL.cost = float(cost)
                adjL.price = float(price)
                adjL.save()

                data = {
                    'success':True,
                    'msg_swa':'Tank la mafuta limeongezwa kikamilifu',
                    'msg_eng':'Tank added successfully'
                    
                }
            else:
                data = {
                    'success':False,
                    'msg_swa':'Hauna Ruhusa ya kuongeza tank',
                    'msg_eng':'You have no permition to add tank',
                } 
            return JsonResponse(data)

        # except:
        #     data = {
        #         'success':False,
        #         'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
        #         'msg_eng':'The action was not successfully please try again',
        #     }
        #     return JsonResponse(data)
    
@login_required(login_url='login')
def pumpSetting(request):
    if request.method == "POST":
        try:
            pmp = int(request.POST.get('pmp'))
            read = float(request.POST.get('read'))
            # isSh = int(request.POST.get('isSh'))
            desc = request.POST.get('desc')

                 
            todo = todoFunct(request)
            useri = todo['useri']
            cheo = todo['cheo']
            shell = todo['shell']

            pump = fuel_pumps.objects.get(pk=pmp,tank__Interprise=shell)

                 
            if  not pump.Incharge: 
                temp = pumpTemper()
                temp.by = cheo
                temp.pump = pump
                temp.BRead = float(pump.readings)
                temp.ARead = read
                temp.desc = desc
                temp.date = datetime.datetime.now(tz=timezone.utc) 
                temp.save()

                pump.readings = read
                pump.save()

                membrs = InterprisePermissions.objects.filter(Interprise=shell,Allow = True) 
                for m in membrs:
                    ntfy = notifications()
                    ntfy.usr = m.user
                    ntfy.temper = temp
                    ntfy.date = datetime.datetime.now(tz=timezone.utc) 
                    ntfy.save()

                data = {
                    'success':True,
                    'swa':'Number za kipimo cha pampu kimebadilishwa kikamilifu',
                    'eng':'Meter readings changed successfully'
                }    

                return JsonResponse(data)



            else:
                data = {
                    'success':False,
                    'swa':'Kipimo cha mita kwenye pampu hakiwezi kubadilishwa iwapo pampu ikiwa kwenye zamu',
                    'eng':'Meter readings cannot be changed when the pump is in shift'
                }

                return JsonResponse(data)

                



        except:
            data={
                'success':False,
                'swa':'Kitendo hakkikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi',
                'eng':'The action was unsuccessfull please try again correctly '
            }
            return JsonResponse(data)
    else:
       return render(request,'pagenotFound.html')


@login_required(login_url='login')
def addpump(request):
    if request.method == "POST":
        try:
            name = request.POST.get('name')
            fue = int(request.POST.get('fuel'))
            val = int(request.POST.get('pumpval',0))
            isNew = int(request.POST.get('isNew'))
            newPmp = request.POST.get('NewPump')
            cnt = float(request.POST.get('cnt'))

            todo = todoFunct(request)

            useri = todo['useri']
            general = todo['general']
            shell = todo['shell']


            if useri.admin and not general:
                stat = None
                if isNew:
                    stat = PumpStation()
                    stat.name = newPmp
                    stat.Interprise = shell
                    stat.save()
                else:
                    stat = PumpStation.objects.get(pk=val)    

                tank = fuel_tanks.objects.get(pk=fue)
                pump = fuel_pumps()
                pump.name = name
                pump.station = stat
                pump.readings = cnt
                pump.tank = tank
              
                pump.save()

                data = {
                    'success':True,
                    'msg_swa':'Pump ya mafuta limeongezwa kikamilifu',
                    'msg_eng':'Pump added successfully'
                    
                }
            else:
                data = {
                    'success':False,
                    'msg_swa':'Hauna Ruhusa ya kuongeza Pampu',
                    'msg_eng':'You have no permition to add Pump',
                } 
            return JsonResponse(data)

        except:
            data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
                'msg_eng':'The action was not successfully please try again',
            }
            return JsonResponse(data)
    
@login_required(login_url='login')
def cashOut(request):
    if request.method == "POST":
        # try:
            shift = int(request.POST.get('shift'))
            amoC = float(request.POST.get('amoC'))
            To_acco = int(request.POST.get('To_acco',0))
            giveTo = request.POST.get('To')
            desc = request.POST.get('desc')
            FromPmp = int(request.POST.get('FromPmp',0))
            FrmAcc = int(request.POST.get('FrmAcc',0))
            todo = todoFunct(request)
   
            useri = todo['useri']
            general = todo['general']
            shell = todo['shell']
            manager = todo['manager']
            kampuni = todo['kampuni']

            data = {
                'success':True,
                'msg_swa':'Fedha zimehamishwa kikamilifu',
                'msg_eng':'Cash transferred successfully'
            }

            

            if (useri.admin or manager) and not general:
                fA = None
                acount = PaymentAkaunts.objects.get(pk=To_acco,Interprise__company=kampuni.id)

                if not FromPmp:
                    fA = PaymentAkaunts.objects.get(pk=FrmAcc,Interprise=shell.id)
                    fA_Amo = float(fA.Amount) 
                    if float(fA_Amo) >= float(amoC):
                        
                        fA.Amount = float(fA_Amo - amoC)
                        fA.save()

                        toa = toaCash()
                        toa.Akaunt = fA
                        toa.Amount = amoC
                        toa.before = fA_Amo
                        toa.After = fA.Amount
                        if To_acco:
                            toa.kwenda = acount.Akaunt_name
                            if not acount.onesha:
                                toa.kwenda_siri = True
                        else:
                            toa.kwenda = "Personal"
                        if not fA.onesha:
                            toa.usiri =True       
                        toa.maelezo = desc
                        toa.makato = 0
                        toa.tarehe = datetime.datetime.now(tz=timezone.utc)
                        toa.by=useri
                        toa.Interprise=fA.Interprise
                        
                        toa.kuhamisha = True

                        toa.kuhamishaNje =  acount.Interprise is not fA.Interprise
                        toa.save()

                    else:
                        data = {
                            'success':False,
                            'msg_swa':'Kitendo hakikufanikiwa. Akaunti ya kutoa fedha haina kiasi cha kutosha',
                            'msg_eng':'The action was not successfully. The account to withdraw from has no sufficient amount',
                        }
                        return JsonResponse(data)
                sh = None

                weka =  wekaCash() 
                ac_Amo = float(acount.Amount) 
                afterAmo = float(ac_Amo+amoC)
                acount.Amount = afterAmo
                acount.save()

                weka.Interprise = shell
                weka.tarehe = datetime.datetime.now(tz=timezone.utc)
                weka.Akaunt = acount
                weka.Amount =amoC
                weka.before = ac_Amo
                weka.After = afterAmo

                if FromPmp:
                    sh = shifts.objects.get(pk=shift,record_by__Interprise=shell.id)
                    weka.shift = sh
                    weka.biforeShift = True                    
                    weka.kutoka = f'SHF-{sh.code}'

                else:
                    weka.kutoka = fA.Akaunt_name   
                    weka.kuhamisha = True
                weka.by = useri
                weka.giveTo = giveTo
                weka.maelezo = desc 
                weka.save()

            
            else:
                data = {
                    'success':False,
                    'msg_swa':'Hauna Ruhusa ya kuongeza Pampu',
                    'msg_eng':'You have no permition to add Pump',
                }


            return JsonResponse(data)

        # except:
        #     data = {
        #         'success':False,
        #         'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
        #         'msg_eng':'The action was not successfully please try again',
        #     }
        #     return JsonResponse(data)
    

@login_required(login_url='login')
def addcustomer(request):
     if request.method == "POST":
        try: 
            #  intp= InterprisePermissions.objects.get(user__user=request.user,default=True)
             todo = todoFunct(request)
             useri = todo['useri']
             cheo = todo['cheo']
             admin = todo['admin']
             manager = todo['manager']
             shell = todo['shell']

             if useri.admin or manager:  

                name=request.POST.get('jina')
                address=request.POST.get('adress')
                code=request.POST.get('code')
                simu1=request.POST.get('simu1')
                simu2=request.POST.get('simu2')
                mail=request.POST.get('mail')
                # isActive=request.POST.get('isactive')
                value=request.POST.get('value')
                edit=int(request.POST.get('edit',0))
                valued=int(request.POST.get('valued',0))
                un = int(request.POST.get('u',0))

                

                teja=wateja()
                wtj = wateja.objects.filter(pk=valued)
                if edit and wtj.exists() and useri.admin:
                    teja = wtj.last()
                else:
                    teja.added_by = useri
                    teja.Interprise = shell
               
               
                teja.allEntp = un    
                teja.jina = name
                     
                teja.address = address
                teja.code = code
                teja.simu1 = simu1
                teja.simu2 = simu2
                teja.email = mail
                    
                if wateja.objects.filter(simu1=simu1).exists() and not edit:
                    data={
                        'success':False,
                        'message_swa':'Tayari kuna Mteja mwingine mwenye jina kama hili kama ni mwinginae unaweza kubadili jina au ondoa taarifa za mteja zilizowekwa awali',
                        'message_eng':'The same  Customer name  exists you can change the name or remove the previos saved Customer details'
                    
                    }

                else:
                    teja.save()    
                    data={
                        'success':True,
                        'message_swa':'Taarifa za mteja zimehifadhiwa kikamilifu',
                        'message_eng':'new Customer added successfully'
                        
                    }
                return JsonResponse(data)  
             else:
                 data={
                     'success':False,
                     'message_swa':'Hauna ruhusa ya kuongeza mteja kwa sasa tafadhari wasiliana na uongozi wako kupata ruhusa',
                     'message_eng':'You have no permission to add Customer please contact your administrator',
                 } 
                 return JsonResponse(data)    
        except:
             data={
                 'success':False,
                 'message_swa':'Taarifa za mteja hazijahifadhiwa kutokana na hitilafu. tafadhari jaribu tena kuweka data kwa usahihi',
                 'message_eng':'Customer info was not successfully saved. Please try again to fill correct Customer informations'
             }
             return JsonResponse(data)          
     else:
       return render(request,'pagenotFound.html',todoFunct(request)) 



@login_required(login_url='login')
def vendors(request):
  todo = todoFunct(request)
  useri = todo['useri']
  if useri.admin or (useri.ceo and useri.pu):
        kampuni = todo['kampuni']
        vendors = wasambazaji.objects.filter(compan = kampuni.id)
        vend = []
        madeni = 0
        for v in vendors:
            denitr = Purchases.objects.filter(vendor=v.id)
            deni = denitr.aggregate(sumi=Sum(F('amount')-F('payed')))['sumi'] or 0
            vend.append({
                'ven':v,
                'deni':deni
            })
            madeni += deni
            
        todo.update({
            'vendors':vend,
            'isVendor':True,
            'madeni':madeni
        })
        return render(request,'vendors.html',todo)
  else:
      return redirect('/userdash')
  

@login_required(login_url='login')
def addPurchase(request):
     if request.method == "POST":    
        try:
            puDate = request.POST.get('puDate')
            puRef = request.POST.get('puRef')
            ven = int(request.POST.get('ven',0))
            puData = json.loads(request.POST.get('puDt',[]))
            todo = todoFunct(request)
            useri = todo['useri']
            kampuni = todo['kampuni']
            vendor = wasambazaji.objects.get(pk=ven,compan=kampuni)
            if useri.admin:
                pu = Purchases()
                entry = Purchases.objects.filter(record_by__company=kampuni)
                code = invoCode(entry)
  
                pu.code = TCode({'code':code,'shell':kampuni.id})
                pu.Invo_no = int(code)
                pu.recDate = datetime.datetime.now(tz=timezone.utc)
                pu.date = puDate
                pu.record_by = useri
                pu.vendor = vendor
                pu.ref = puRef
                pu.save()
                totAmo = 0
                for rec in puData:

                    pL = PuList()
                    fl = fuel.objects.get(pk=rec['fuel'])
                    pL.pu = pu
                    pL.cost = float(rec['puPr'])
                    pL.qty = float(rec['puQty'])
                    pL.Fuel = fl
                    pL.save()

                    totPr = rec['puPr'] * rec['puQty']
                    totAmo += totPr
                pu.amount = float(totAmo)
                pu.save()

                data = {
                    'success':True,
                    'swa':'Taarifa za manunuzi ya mafuta zimehifadhiwa kikamilifu',
                    'eng':'Fuel purchase data saved successfully',
                    'pu':pu.id

                }
                return JsonResponse(data)

            else:
                data = {
                    'swa':'Hauna Ruhusa kwa kitendo hiki tafadhari wasiliana na uongozi',
                    'eng':'You have no permission for this please contact admin',
                    'success':False
                }
                return JsonResponse(data)
        except:
             data={
                 'success':False,
                 'swa':'Taarifa za Manunuzi hazijahifadhiwa kutokana na hitilafu. tafadhari jaribu tena kuweka data kwa usahihi',
                 'eng':'Fuel Purchases info was not successfully saved. Please try again to fill correct Supplier informations'
             }
             return JsonResponse(data)          
     else:
       return render(request,'pagenotFound.html',todoFunct(request))      


@login_required(login_url='login')
def lipaBill(request):
    if request.method == "POST":
         try:
               value=int(request.POST.get('bill',0))
               ac=int(request.POST.get('acc'))
               paid_set=int(request.POST.get('pay_set'))
               paid=float(request.POST.get('pay'))
               bal=float(request.POST.get('baki'))
               bal_set=int(request.POST.get('bal_set'))
               ven = int(request.POST.get('ven',0))
               todo = todoFunct(request) 
               duka = todo['shell']
               kampuni = todo['kampuni']
               useri = todo['useri']   

               if useri.admin:
                    pu = None
                    vendor = None
                    if value:
                        pu = Purchases.objects.filter(pk=value,vendor__compan=kampuni)
                    if ven:
                        pu = Purchases.objects.filter(vendor=ven,record_by__company=kampuni)
                    pu = pu.filter(amount__gt=F('payed'))    
                    toakwa= PaymentAkaunts.objects.get(pk=ac,Interprise__company=kampuni)
                    daiwa = float(pu.aggregate(sumi=Sum(F('amount')-F('payed')))['sumi'])
                    if paid <= daiwa:
                        vendor = pu.last().vendor 
                        lipwa = paid
                        for bill in pu:
                        
                                deni = float(bill.amount - bill.payed)
                                
                                if deni < lipwa:
                                    bill.payed = float(bill.amount)
                                    bill.save()
                                    lipwa = float(lipwa - deni)
                                else:
                                    bill.payed = float(float(bill.payed) + lipwa)
                                    lipwa = 0
                                    bill.save()
                                    exit

                    
                        
                        beforetoa=float(toakwa.Amount) 
            
                        toa = toaCash()
                        toa.Akaunt = toakwa
                        toa.Amount = paid
                        toa.before = beforetoa
                        if bool(bal_set):
                                toa.After = bal 
                                toa.makato = float(beforetoa-float(bal+paid))
            
                        else :
                                toa.After = float(beforetoa - paid) 
                                toa.makato = 0
                                                
                        toa.kwenda = "Bill Payment"
                        toa.maelezo = 'Bill Payment'
                        toa.tarehe = datetime.datetime.now(tz=timezone.utc)
                        toa.by=useri
                        toa.Interprise=duka
                        
                        toa.bill = vendor
                    
                        toa.usiri = toakwa.onesha
            
                        
                        if bool(bal_set): 
                            toakwa.Amount =  bal
                        else:
                            toakwa.Amount =float(float(toakwa.Amount) - paid)

                        toakwa.save()              
                        toa.save() 


                       
                     

                        data={
                                    'success':True,
                                    'swa':'Malipo ya bili yamefanikiwa',
                                    'eng':'Bill payment recorded successfully'
                                }  
                        return JsonResponse(data)

                    else:
                            data={
                                'success':False,
                                
                                'swa':'Malipo ya bili hayajafanikiwa kiasi kilicholipwa ni kikubwa kuliko kiasi cha bili',
                                'eng':'Bill payment was not recorded because the paid amount exceed the bill amount'
                    
                            }        

                            return JsonResponse(data)     
               else:
                   data = {
                       'success':False,
                       'swa':'Hauna ruhusa kwa kitendo hiki tafadhari wasiliana na uongozi',
                       'eng':'You have no permission for this please contanct administration'
                   } 
                   return JsonResponse(data)
         except:
 
                  data={
                           'success':False,
                           'swa':'Malipo ya bili hayakufanikiwa kutokana na hitilafu Tafadhari Jaribu tene kwa usahihi',
                           'eng':'Bill payment was not recorded please try again by selecting the bill'
                     }          
                     
                  return JsonResponse(data)     
    else:  
       return render(request,'pagenotFound.html',todoFunct(request))


@login_required(login_url='login')
def PuLIST(request):
    todo = todoFunct(request)
   
    general = todo['general']
    kampuni = todo['kampuni']

    puchs = Purchases.objects.filter(vendor__compan=kampuni.id)

  

    num = puchs.count()
    tpuchs = puchs.order_by("-pk")

    p=Paginator(tpuchs,15)
    page_num =request.GET.get('page',1)
       

    try:
          page = p.page(page_num)

    except EmptyPage:
         page= p.page(1)

    pg_number = p.num_pages

    bills = []
    for b in page:
        puL = PuList.objects.filter(pu=b.id)
        rcvd = puL.aggregate(sumi=Sum('rcvd'))['sumi'] or 0
        qty=puL.aggregate(sumi=Sum('qty'))['sumi'] or 0
        bills.append({
            'b':b,
            'rcvd':rcvd,
            'qty':qty,
            'rperc':100*rcvd/qty
        })

    todo.update({
        'bills':bills,
        'tr':page,
        'isPu':True,
        'p_num':page_num,
        'pages':pg_number,
        'bil_num':num,
    })

    return todo

@login_required(login_url='login')
def viewPurchase(request):
    try:
        todo = PuLIST(request)
        useri = todo['useri']
      
        if  useri.admin or (useri.ceo and useri.pu):
            kampuni = todo['kampuni']
            i = request.GET.get('i',0)
            pu = Purchases.objects.get(pk=i,vendor__compan=kampuni)
            pL = PuList.objects.filter(pu=pu).annotate(totAmo = (F('qty')*F('cost')),remain = (F('qty')-F('rcvd')))
            RL = receivedFuel.objects.filter(receive__FromPurchase=pu)
            attach = attachments.objects.filter(purchase=pu)

            rcvd=pL.aggregate(sumi=Sum('rcvd'))['sumi'] or 0
            qty=pL.aggregate(sumi=Sum('qty'))['sumi'] or 0



            todo.update({
                'trf':pu,
                'puList':pL,
                'isPuchView':True,
                'attach':attach,
                'baki':pu.amount-pu.payed,
                'rcvd':rcvd,
                'qty':qty,
                'rperc':100*rcvd/qty ,
                'rcd':RL
            })

            return render(request,'venPurchasesView.html',todo)
        
        else:
            return redirect('/userdash')


    except:
        return render(request,'pagenotFound.html')

@login_required(login_url='login')
def viewVendor(request):
    try:
        todo = todoFunct(request)
        useri = todo['useri']
        if useri.admin or (useri.ceo and useri.pu):
            v = int(request.GET.get('v',0))
            
            kampuni = todo['kampuni']

            vendor = wasambazaji.objects.get(pk=v,compan=kampuni)
            bills = Purchases.objects.filter(record_by__company=kampuni,vendor=vendor).annotate(deni=F('amount')-F('payed'))
            baki = bills.aggregate(sumi=Sum(F('amount')-F('payed')))['sumi']

            leo = datetime.datetime.now().astimezone()
            thisMonth = leo.strftime('%Y-%m-01 00:00:00%z') 
            #   print(int(leo.strftime('%m')))

        
            
            MonthBill = bills.filter(date__gte=thisMonth)
            bill_prev = bills.filter(date__lt=thisMonth,payed__lt=F('amount')) 

            totprev = bill_prev.aggregate(Amo=Sum('amount'))['Amo'] or 0
            paidprev = bill_prev.aggregate(Paid=Sum('payed'))['Paid'] or 0
            debtprev = totprev - paidprev

            totAmo = MonthBill.aggregate(Amo=Sum('amount'))['Amo'] or 0
            paid = MonthBill.aggregate(Paid=Sum('payed'))['Paid'] or 0
            debt = totAmo - paid

            TheFuel = fuel.objects.all()
            montBill = []
            for b in MonthBill:
                puL = PuList.objects.filter(pu=b.id)
                qty = puL.aggregate(sumi=Sum('qty'))['sumi'] or 0
                rcvd = puL.aggregate(sumi=Sum('rcvd'))['sumi'] or 0
                montBill.append({
                    'b':b,
                    'rcvd':rcvd,
                    'qty':qty,
                    'rperc':100*rcvd/qty,
                })
            prevBill = []
            for b in bill_prev:
                puL = PuList.objects.filter(pu=b.id)
                qty = puL.aggregate(sumi=Sum('qty'))['sumi'] or 0
                rcvd = puL.aggregate(sumi=Sum('rcvd'))['sumi'] or 0
                prevBill.append({
                    'b':b,
                    'rcvd':puL.aggregate(sumi=Sum('rcvd'))['sumi'] or 0,
                    'qty':puL.aggregate(sumi=Sum('qty'))['sumi'] or 0,
                    'rperc':100*rcvd/qty,
                })
        
        
            todo.update({
                'allfuel':TheFuel,
                'isVendor':True,
                'isViewVend':True,
                
                'ven':vendor,

                'sale':montBill,
                'saleLen':len(montBill),
                'totAmo':totAmo,
                'bakiM':debt,
                'baki':baki,
                'paid':paid,
                
                'debtprev':debtprev,
                'totprev':totprev,
                'prevsale':prevBill,
                'prevsaleLen':len(prevBill),
                'paidprev':paidprev,

                'totA':totAmo+totprev,
                'totD':debtprev+debt,

                'totP':paid+paidprev,
                'totI':len(MonthBill) + len(bill_prev)

                

            })


        
        
            return render(request,'vendorView.html',todo)
        else:
            return redirect('/userdash')  
    except:
        return render(request,'pagenotFound.html',todoFunct(request))

@login_required(login_url='login')
def addvendor(request):
     if request.method == "POST":
        try: 
            #  intp= InterprisePermissions.objects.get(user__user=request.user,default=True)
             todo = todoFunct(request)
             useri = todo['useri']
             cheo = todo['cheo']
             admin = todo['admin']

             if useri.admin:  

                name=request.POST.get('jina')
                address=request.POST.get('adress')
                code=request.POST.get('code')
                simu1=request.POST.get('simu1')
                simu2=request.POST.get('simu2')
                mail=request.POST.get('mail')
                # isActive=request.POST.get('isactive')
                value=request.POST.get('value')
                edit=int(request.POST.get('edit',0))
                valued=int(request.POST.get('valued',0))

                kampuni = todo['kampuni']

                teja=wasambazaji()
                wtj = wasambazaji.objects.filter(pk=valued)
                if edit and wtj.exists():
                    teja = wtj.last()
          
               
               
                    
                teja.jina = name
                    
                teja.address = address
                teja.code = code
                teja.simu1 = simu1
                teja.simu2 = simu2
                teja.email = mail
                teja.compan = kampuni
                    
                if wasambazaji.objects.filter(Q(simu1=simu1)|Q(simu2=simu2)).exists() and not edit:
                    data={
                        'success':False,
                        'message_swa':'Tayari kuna Msambazaji mwingine mwenye jina kama hili kama ni mwinginae unaweza kubadili jina au ondoa taarifa za Msambazaji zilizowekwa awali',
                        'message_eng':'The same  Supplier name  exists you can change the name or remove the previos saved Supplier details'
                    
                    }

                else:
                    teja.save()    
                    data={
                        'success':True,
                        'message_swa':'Taarifa za Msambazaji zimehifadhiwa kikamilifu',
                        'message_eng':'new Supplier added successfully'
                        
                    }
                return JsonResponse(data)  
             else:
                 data={
                     'success':False,
                     'message_swa':'Hauna ruhusa ya kuongeza Msambazaji kwa sasa tafadhari wasiliana na uongozi wako kupata ruhusa',
                     'message_eng':'You have no permission to add Supplier please contact your administrator',
                 } 
                 return JsonResponse(data)    
        except:
             data={
                 'success':False,
                 'message_swa':'Taarifa za Msambazaji hazijahifadhiwa kutokana na hitilafu. tafadhari jaribu tena kuweka data kwa usahihi',
                 'message_eng':'Supplier info was not successfully saved. Please try again to fill correct Supplier informations'
             }
             return JsonResponse(data)          
     else:
       return render(request,'pagenotFound.html',todoFunct(request)) 
     
@login_required(login_url='login')
def puchases(request):
        try: 
             todo = PuLIST(request)  
             useri = todo['useri']
             if useri.admin or (useri.ceo and useri.pu): 
                return render(request,'vendorPurchases.html',todo)
             else:
                 return redirect('/userdash')
        except:
             
             return render(request,'pagenotFound.html')          
    
 

@login_required(login_url='login')
def puClosed(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            useri = todo['useri']
            kampuni = todo['kampuni']
            pu = int(request.POST.get('pu'))
            if useri.admin:
                pu = Purchases.objects.get(pk=pu,record_by__company=kampuni)
                pu.closed = True
                pu.save()
                data = {
                    'success':True,
                    'swa':'Kupokea mafuta kumefungwa kikamilifu',
                    'eng':'Fuel Receive closed successfully'
                }
                return JsonResponse(data)
            else:
                data = {
                    'success':False,
                    'swa':'Hauna Ruhusa ya kitendo hiki kwa sasa tafadhari wasiliana na uongozi',
                    'eng':'You have no permission for this please contact admin'
                    }
                
                return JsonResponse(data)
        
        except:
            data = {
                'success':False,
                'swa':'kitendo hakikufanikiwa kutokana na hitilafu',
                'eng':'The action was not successfully due to error please try again'
            }
            return JsonResponse(data)
    else:
        data = {'success':False}
        return JsonResponse(data)

@login_required(login_url='login')
def puReceive(request):
       
    try:
        todo = todoFunct(request)
        kampuni = todo['kampuni'] 
        i = request.GET.get('i',0)
        useri = todo['useri']
        if useri.admin:
            pu = Purchases.objects.get(pk=i,record_by__company=kampuni) 
            PL = PuList.objects.filter(pu=pu,qty__gt=F('rcvd'))
            Intp = Interprise.objects.filter(company=kampuni)
           

            tanks = fuel_tanks.objects.filter(Interprise__company=kampuni)
            tr_tank = tanks.filter(moving=True)
            shell_tanks = tanks.filter(moving=False)

            tankContainer = tr_tank.distinct('tank')
        
            tanksSup = InterprisePermissions.objects.filter(Interprise__company=kampuni,user__tankSup=True)


            todo.update({
                'isreceive':True,
                 'trf':pu,
                 'list':PL,
                'Intp':Intp,
                'shell_tanks':shell_tanks,
                'tr_tank':tr_tank,
                'isPu':True,
                'tanksSup':tanksSup,
                'tankContainer':tankContainer
            })    
            

            return render(request,'receivePuFuel.html',todo)
        else:
            return redirect('/userdash') 

    except:
        return render(request,'pagenotFound.html')
  
@login_required(login_url='login')
def search_records(request):
    keyword = request.POST.get('search', '').strip()
    todo = todoFunct(request)
    kampuni = todo['kampuni']
    general = todo['general']
    shell = todo.get('shell', None)

    result = None
    model = None
    if '-' in keyword:
        prefix, num = keyword.split('-', 1)
        num = num.strip()
        prefix = prefix.strip().upper()
      
        if prefix and num:

            if prefix == 'INVO':
                model = fuelSales
                qs = model.objects.filter(code__endswith=num, by__Interprise__company=kampuni)
                if not general and shell:
                    qs = qs.filter(by__Interprise=shell.id)
                result = qs.last()
            elif prefix == 'PTR':
                model = TransferFuel
                qs = model.objects.filter(code__endswith=num, record_by__Interprise__company=kampuni)
                if not general and shell:
                    qs = qs.filter(record_by__Interprise=shell.id)
                result = qs.last()
            elif prefix == 'TTR':
                model = ReceveFuel
                qs = model.objects.filter(code__endswith=num, by__Interprise__company=kampuni)
                if not general and shell:
                    qs = qs.filter(by__Interprise=shell.id)
                result = qs.last()
            elif prefix == 'ADJ':
                model = adjustments
                qs = model.objects.filter(code__endswith=num, Interprise__company=kampuni)
                if not general and shell:
                    qs = qs.filter(Interprise=shell.id)
                result = qs.last()
            elif prefix == 'PU':
                model = Purchases
                qs = model.objects.filter(code__endswith=num, record_by__company=kampuni)
                result = qs.last()
            elif prefix == 'SHF':
                model = shifts
                qs = model.objects.filter(code__endswith=num, record_by__Interprise__company=kampuni)
                if not general and shell:
                    qs = qs.filter(record_by__Interprise=shell.id)
                result = qs.last()

    # Return JSON response with redirect URL
    if result and model:
        if model == fuelSales:
            theUrl = f'/salepurchase/viewFuelSales?i={result.id}'
        elif model == TransferFuel:
            theUrl = f'/salepurchase/viewTransfer?i={result.id}'
        elif model == ReceveFuel:
            theUrl = f'/salepurchase/viewFuelReceive?i={result.id}'
        elif model == adjustments:
            theUrl = f'/salepurchase/adjView?i={result.id}'
        elif model == Purchases:
            theUrl = f'/salepurchase/viewPurchase?i={result.id}'
        elif model == shifts:
            theUrl = f'/salepurchase/viewShift?i={result.id}'
        else:
            theUrl = ''
        return JsonResponse({"success": True, "url": theUrl})# Redirect to the appropriate view

    else:
        return JsonResponse({"success": False, "url": ''})