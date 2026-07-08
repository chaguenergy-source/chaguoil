
# Create your views here.
from django.shortcuts import render,redirect
from account.models import (
    UserExtend,
    ToContena,PuList, Purchases,transporter,
    creditDebtOrder,DepositTo,CustmDebtPayRec,
    saleList,saleOnReceive,toaCash,tr_supervisor,
    shiftsTime,transFromTo,tankAdjust,adjustments,
    pumpTemper,PumpStation,notifications,fuelPriceChange,
    shiftSesion,tankContainer,shiftPump,rekodiMatumizi,
    attachments,fuelSales,receiveFromTr,TransferFuel,
    receivedFuel,ReceveFuel,transfer_from,PhoneMailConfirm,
    wekaCash,shifts,wateja,wasambazaji,fuel,fuel_pumps,fuel_tanks,
    Interprise,InterprisePermissions,PaymentAkaunts,puAttachments,staff_akaunt_permissions,
    StaffLoan,loanPayMent)
# Create your views here.

from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.db.models import F, Case, When, Value, CharField, Count, DateField
from django.db.models.functions import Coalesce, TruncDate
from django.db import transaction
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
from decimal import Decimal

import time  
import pytz
import datetime
import re
from django.db.models import Sum
import random 
import os
from django.conf import settings

from django.core.files.storage import default_storage # Hii inahitajika kwa kufuta faili la zamani

from account.todos import Todos,confirmMailF,invoCode,TCode
from django.views.decorators.http import require_POST
import json
from django.utils.dateparse import parse_datetime, parse_date
import traceback
import mimetypes
def todoFunct(request):
  usr = Todos(request)
  return usr.todoF()


def _customer_sales_and_payments_qs(cust, kampuni):
    customer_order_ids = list(
        creditDebtOrder.objects.filter(
            customer=cust,
            by__user__company=kampuni,
        ).values_list('id', flat=True)
    )
    sales_qs = fuelSales.objects.filter(
        Q(customer=cust) | Q(cdorder_id__in=customer_order_ids),
        by__Interprise__company=kampuni,
    ).order_by('recDate', 'date', 'pk')
    payments_qs = wekaCash.objects.filter(
        Interprise__company=kampuni,
        Akaunt__isnull=False,
        Amount__gt=0,
    ).filter(
        Q(customer=cust) | Q(cdOrder_id__in=customer_order_ids)
    ).order_by('tarehe', 'pk')
    return sales_qs, payments_qs, customer_order_ids


def _simulate_customer_payment_allocation(sales, payments):
    sale_payed = {sale.pk: Decimal('0') for sale in sales}
    sale_amounts = {sale.pk: Decimal(str(sale.amount or 0)) for sale in sales}
    exceeded_payments = []
    sale_index = 0

    for pay in payments:
        remaining = Decimal(str(pay.Amount or 0))
        allocated = Decimal('0')

        while remaining > 0 and sale_index < len(sales):
            sale = sales[sale_index]
            amount = sale_amounts[sale.pk]
            paid = sale_payed[sale.pk]
            due = amount - paid

            if due <= 0:
                sale_index += 1
                continue

            apay = due if due <= remaining else remaining
            sale_payed[sale.pk] = paid + apay
            allocated += apay
            remaining -= apay

            if sale_payed[sale.pk] >= amount:
                sale_index += 1

        if remaining > Decimal('0.01'):
            exceeded_payments.append({
                'pay_id': pay.pk,
                'amount': float(pay.Amount or 0),
                'allocated': float(allocated),
                'exceeded': float(remaining),
                'tarehe': pay.tarehe.strftime('%Y-%m-%d %H:%M') if pay.tarehe else '',
                'kutoka': pay.kutoka or '',
                'maelezo': pay.maelezo or '',
            })

    return exceeded_payments


def _get_customer_exceeded_payments(cust, kampuni):
    sales_qs, payments_qs, _ = _customer_sales_and_payments_qs(cust, kampuni)
    sales = list(sales_qs)
    payments = list(payments_qs)
    simulated = _simulate_customer_payment_allocation(sales, payments)
    tolerance = Decimal('0.01')

    last_order = creditDebtOrder.objects.filter(
        customer=cust,
        by__user__company=kampuni,
    ).order_by('pk').last()
    last_order_id = last_order.pk if last_order else None

    exceeded = []
    for item in simulated:
        pay = next((p for p in payments if p.pk == item['pay_id']), None)
        if pay is None:
            continue

        allocated_db = _payment_allocated_to_sales(pay)
        amount = Decimal(str(pay.Amount or 0))
        used_amount = Decimal(str(pay.used_amount or 0))
        if pay.cdOrder_id and used_amount >= amount - tolerance:
            continue
        surplus = amount - allocated_db
        if surplus <= tolerance:
            continue

        item['allocated'] = float(allocated_db)
        item['exceeded'] = float(surplus)
        item['on_order'] = bool(pay.cdOrder_id)
        item['order_id'] = pay.cdOrder_id
        item['last_order_id'] = last_order_id
        item['has_credit_order'] = last_order_id is not None
        exceeded.append(item)

    return exceeded


def _payment_allocated_to_sales(pay):
    return Decimal(str(
        CustmDebtPayRec.objects.filter(pay=pay).aggregate(total=Sum('Apay'))['total'] or 0
    ))


def check_customer_records_metrics(cust, kampuni):
    customer_order_ids = list(
        creditDebtOrder.objects.filter(
            customer=cust,
            by__user__company=kampuni,
        ).values_list('id', flat=True)
    )
    sales_qs = fuelSales.objects.filter(
        Q(customer=cust) | Q(cdorder_id__in=customer_order_ids),
        by__Interprise__company=kampuni,
    )
    payments_qs = wekaCash.objects.filter(
        Interprise__company=kampuni,
        Amount__gt=0,
    ).filter(
        Q(customer=cust) | Q(cdOrder_id__in=customer_order_ids)
    )

    total_paid = Decimal(str(payments_qs.aggregate(total=Sum('Amount'))['total'] or 0))
    total_consumed = Decimal(str(sales_qs.aggregate(total=Sum('amount'))['total'] or 0))
    difference = total_paid - total_consumed

    orders_qs = creditDebtOrder.objects.filter(customer=cust, by__user__company=kampuni)
    order_credit_surplus = Decimal('0')
    for order in orders_qs:
        order_credit_surplus += Decimal(str(order.paid or 0)) - Decimal(str(order.consumed or 0))

    apay_total = Decimal(str(
        CustmDebtPayRec.objects.filter(
            Q(pay__in=payments_qs) | Q(sale__in=sales_qs)
        ).aggregate(total=Sum('Apay'))['total'] or 0
    ))

    tolerance = Decimal('0.01')
    issues = []
    recommendations = []
    status = 'ok'
    scenario = 'balanced'

    if difference > tolerance:
        scenario = 'credit_surplus'
        excess = difference
        if abs(excess - order_credit_surplus) > tolerance:
            status = 'mismatch'
            issues.append({
                'swa': (
                    f'Malipo yamezidi matumizi kwa {excess:.2f}, '
                    f'lakini jumla ya (paid - consumed) kwenye oda za mkopo ni {order_credit_surplus:.2f}.'
                ),
                'eng': (
                    f'Payments exceed consumption by {excess:.2f}, '
                    f'but total credit order surplus (paid - consumed) is {order_credit_surplus:.2f}.'
                ),
            })
            recommendations.append({
                'swa': 'Kagua oda zote za mkopo na ulinganishe paid - consumed na kiasi kilichozidi.',
                'eng': 'Review all credit orders and compare paid - consumed with the payment surplus.',
            })
        else:
            recommendations.append({
                'swa': 'Rekodi zinaendana. Salio la mkopo linaendana na malipo yaliyozidi matumizi.',
                'eng': 'Records match. Credit order surplus aligns with excess payments.',
            })
    elif difference < -tolerance:
        scenario = 'debt'
        debt_amount = abs(difference)
        if abs(total_paid - apay_total) > tolerance:
            status = 'mismatch'
            issues.append({
                'swa': (
                    f'Jumla ya malipo kutoka wekaCash ({total_paid:.2f}) '
                    f'haifanani na jumla ya CustmDebtPayRec.Apay ({apay_total:.2f}).'
                ),
                'eng': (
                    f'Total wekaCash payments ({total_paid:.2f}) '
                    f'do not match total CustmDebtPayRec.Apay ({apay_total:.2f}).'
                ),
            })
            recommendations.append({
                'swa': 'Rekebisha linkage ya malipo na ankara, kisha jaza deni halisi au mkopo halisi hapa chini.',
                'eng': 'Fix payment-to-invoice links, then enter the actual debt or credit below.',
            })
        else:
            recommendations.append({
                'swa': 'Malipo na Apay yanaendana, lakini matumizi bado yamezidi malipo.',
                'eng': 'Payments and Apay match, but consumption still exceeds payments.',
            })
    else:
        recommendations.append({
            'swa': 'Jumla ya malipo na matumizi yanaendana.',
            'eng': 'Total payments and consumption are balanced.',
        })

    exceeded_payments = _get_customer_exceeded_payments(cust, kampuni)
    if exceeded_payments:
        status = 'mismatch' if status == 'ok' else status
        total_exceeded = sum(item['exceeded'] for item in exceeded_payments)
        issues.append({
            'swa': (
                f'Kuna malipo {len(exceeded_payments)} yaliyozidi ankara '
                f'(jumla {total_exceeded:.2f}).'
            ),
            'eng': (
                f'There are {len(exceeded_payments)} exceeded payment(s) '
                f'(total {total_exceeded:.2f}).'
            ),
        })
        recommendations.append({
            'swa': 'Chagua kufuta malipo yaliyozidi au kuongeza kiasi kilichozidi kwenye oda ya mkopo.',
            'eng': 'Choose to delete exceeded payments or add the surplus to a credit order.',
        })

    return {
        'status': status,
        'scenario': scenario,
        'total_paid': float(total_paid),
        'total_consumed': float(total_consumed),
        'difference': float(difference),
        'order_credit_surplus': float(order_credit_surplus),
        'apay_total': float(apay_total),
        'debt_amount': float(abs(difference)) if difference < -tolerance else 0,
        'credit_surplus': float(difference) if difference > tolerance else 0,
        'issues': issues,
        'recommendations': recommendations,
        'needs_correction': status == 'mismatch',
        'show_debt_input': scenario == 'debt',
        'show_credit_input': scenario == 'credit_surplus',
        'payments_count': payments_qs.count(),
        'sales_count': sales_qs.count(),
        'orders_count': orders_qs.count(),
        'exceeded_payments': exceeded_payments,
        'has_exceeded_payments': bool(exceeded_payments),
    }


@login_required(login_url='login')
def customers(request):
  todo = todoFunct(request)
  
  general = todo['general']
  shell = todo['shell']
  allcust = int(request.GET.get('allst',0))
  st = int(request.GET.get('st',0))
  kampuni = todo['kampuni']

  cust = wateja.objects.filter(Interprise__company=kampuni).order_by('jina')
#   if not general:
#         cust = cust.filter(Q(Interprise=shell.id)|Q(allEntp=True))

  watejaD = []
  madeni = 0
  for c in cust:
      denitr = fuelSales.objects.filter(customer=c.id,amount__gt=F('payed'))
      if not allcust:
          if not st and not general:
              st = todo['shell'].id
          if st:    
            denitr = denitr.filter(by__Interprise=st)

      deni = denitr.aggregate(sumi=Sum(F('amount')-F('payed')))['sumi'] or 0
      watejaD.append({
          'cust':c,
          'deni':deni
      })

      madeni += deni
  stations = Interprise.objects.filter(company=todo['kampuni'].id)
  kituo = shell
  if allcust:
      kituo = None
  if st:
    kituo = Interprise.objects.get(pk=st,company=todo['kampuni'])    

  deni_count = sum(1 for item in watejaD if item['deni'] > 0)
  todo.update({
      'stations':stations,
      'isCustomer':True,
      'wateja':watejaD,
      'madeni':madeni,
        'kituo':kituo,
        'deni_count':deni_count
  })
  return render(request,'customers.html',todo)


@login_required(login_url='login')
def toApprovalPayments(request):
    try:
        todo = todoFunct(request)
        shell = todo['shell']
        kampuni = todo['kampuni']
        useri = todo['useri']
        general = useri.admin or useri.ceo

        pym = wekaCash.objects.filter(Q(customer__isnull=False)|Q(sales__mobile_pay=True)|Q(kuhamisha=True)|Q(biforeShift=True),Interprise__company=kampuni,admin_approval=False,Amount__gt=0)
        toa = toaCash.objects.filter(kuhamisha=True,Akaunt__aina__icontains="Cash",Interprise__company=kampuni,admin_approval=False,Amount__gt=0) 
        exp = rekodiMatumizi.objects.filter(Interprise__company=kampuni,admin_approval=False)
        fuel_transfers = transFromTo.objects.filter(transfer__record_by__Interprise__company=kampuni,adminAproval=False)
        fuel_receives = receivedFuel.objects.filter(receive__by__Interprise__company=kampuni,adminAproval=False)
        fuel_adjs = tankAdjust.objects.filter(adj__Interprise__company=kampuni,adminAproval=False)
        if not general:
            pym = pym.filter(Interprise=shell.id)
            toa = toa.filter(Interprise=shell.id)
            exp = exp.filter(Interprise=shell.id)
            fuel_transfers = fuel_transfers.filter(transfer__record_by__Interprise=shell.id)
            fuel_receives = fuel_receives.filter(receive__by__Interprise=shell.id)
            fuel_adjs = fuel_adjs.filter(adj__Interprise=shell.id)

        todo.update({
            'mobile_pym':len(pym.filter(sales__mobile_pay=True)),
            'customer_pym':len(pym.filter(customer__isnull=False)),
            'cashDeposit':len(toa),
            'cashDepositBefore':len(pym.filter(biforeShift=True,shift__isnull=False,sales__mobile_pay__isnull=True)),
            'shift_expenses':len(exp),
            'fuel_transfers':fuel_transfers.count(),
            'fuel_receives':fuel_receives.count(),
            'fuel_adjs':fuel_adjs.count(),
            'isToApprovalPayments':True
        })   
        return todo
    
    except Exception as err:
        traceback.print_exc() 
        return {'success':False}


@login_required(login_url='login')
def set_ignore_amount(request):
    try:
        if request.method == 'POST':
            todo = todoFunct(request)
          
            kampuni = todo['kampuni']
            
            useri = todo['useri']

            if not useri.admin:
                data = {
                    'success': False,
                    'eng': 'You do not have permission to perform this action.',
                    'swa': 'Huna ruhusa ya kufanya kitendo hiki.'

                }
                return JsonResponse(data)

          
            ignoreAmount = float(request.POST.get('ignoreAmount', 0))
            custId = int(request.POST.get('cust',0))

            custm = wateja.objects.get(pk=custId,Interprise__company=kampuni)
            custm.toIgnore = ignoreAmount
            custm.save()


            return JsonResponse({'success': True, 'eng': 'Ignore amount updated successfully.','swa':'Kiasi cha kupuuza kimefanikiwa kusasishwa.'})
        else:
            return JsonResponse({'success': False, 'eng': 'Invalid request method.', 'swa': 'Njia ya ombi si sahihi.'})
    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({'success': False, 'eng': 'An error occurred while updating ignore amount.', 'swa': 'Kulitokea hitilafu wakati wa kusasisha kiasi cha kupuuza.'})


@login_required(login_url='login')
def ViewCustomer(request):
  try:
    i = int(request.GET.get('i',0))
    todo = todoFunct(request)
    shell = todo['shell']
    kampuni = todo['kampuni']
    general = todo['general']
    # allcust = int(request.GET.get('allst',0))
    st = int(request.GET.get('st',0))


    leo = datetime.datetime.now().astimezone()
    thisMonth = leo.strftime('%Y-%m-01 00:00:00%z') 
    kituo = None
    if st:
        kituo = Interprise.objects.get(pk=st,company=todo['kampuni'])    
    #   print(int(leo.strftime('%m')))

    cust = wateja.objects.get(Q(Interprise__company=kampuni)|Q(allEntp=True),pk=i)

    saleAll = fuelSales.objects.filter(Q(date__gte=thisMonth)|Q(payed__lt=F('amount')),customer=cust.id,by__Interprise__company=kampuni).annotate(due=F('amount')-F('payed')).order_by('-pk')
    saleLst = saleList.objects.filter(sale__in=saleAll).order_by('theFuel')
    cdOrder =   creditDebtOrder.objects.filter(customer=cust.id,by__user__company=kampuni).annotate(
        balance=F('amount')-F('consumed'),
        bal_deni = F('amount') - F('paid'),
        due=F('amount')-F('consumed'),credit=F('paid')-F('consumed')).order_by('pk')
    lastCd = cdOrder.last()
    hasLastCd = cdOrder.filter(due__gt=0).exists()

    # Add new credit debt order if the last order amount = consumed
    addNewOrder = not cdOrder.exists() or (lastCd and lastCd.amount == lastCd.consumed) if not general else False
    newcode = '01'
    if cdOrder.exists():
        newcode = cdOrder.last().Invo_no + 1
    # entry = fuelSales.objects.filter(by__Interprise=shell)
    
    # code = invoCode(entry)
    # sale.code = TCode({'code':code,'shell':shell.id})

    # sale.Invo_no = int(code)   
    if st:
        saleAll = saleAll.filter(by__Interprise=kituo)

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
            for item in saleLst.distinct('theFuel'):
                fuel_items = items.filter(theFuel=item.theFuel)
                total_Amo = fuel_items.aggregate(sumi=Sum(F('qty_sold')*F('sa_price_og')))['sumi'] or 0
                fuels.append({
                    'fuel': item.theFuel.name,
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
        theFuel = saleLst.distinct('theFuel')

        fuels = []
        for fl in theFuel:
            itmsFuel = fuel_items.filter(theFuel=fl.theFuel)
            total_Amo = itmsFuel.aggregate(sumi=Sum(F('qty_sold')*F('sa_price_og')))['sumi'] or 0
            fuels.append({
                'fuel': fl.theFuel.name,
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

    stations = Interprise.objects.filter(company=todo['kampuni'].id)
    custBalance = float(debtprev+debt) - float(cust.debt_limit)

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
        'stations':stations,
        'kituo':kituo,
        'custBalance':custBalance,
        'totSummary':totSummary,
        'totSummary_prev':totSummary_prev,

        'thereIsPrev':len(sale_prev),
        'thereIsThis':len(saleMonth),
        'hasLastCd':hasLastCd,
        'totA':totAmo+totprev,
        'totD':debtprev+debt,
        'totP':paid+paidprev,
        'totI':len(saleMonth) + len(sale_prev),

    })
    return render(request,'customerView.html',todo)
  except Exception as err:
      print(err)
      traceback.print_exc()
     
      return render(request,'pagenotFound.html')


@login_required(login_url='login')
def repairCustomerStatementLinks(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'swa': 'Bad Request', 'eng': 'Bad Request'})

    try:
        cust_id = int(request.POST.get('cust', 0))
        todo = todoFunct(request)
        useri = todo['useri']
        kampuni = todo['kampuni']

        if not useri.admin:
            return JsonResponse({
                'success': False,
                'swa': 'Hauna ruhusa ya kufanya marekebisho haya',
                'eng': 'You have no permission to run this repair'
            })

        cust = wateja.objects.get(pk=cust_id, Interprise__company=kampuni)
        sales_qs, payments_qs, customer_order_ids = _customer_sales_and_payments_qs(cust, kampuni)

        with transaction.atomic():
            sale_ids = list(sales_qs.values_list('pk', flat=True))
            payment_ids = list(payments_qs.values_list('pk', flat=True))
            sales = list(
                fuelSales.objects.filter(pk__in=sale_ids)
                .order_by('recDate', 'date', 'pk')
                .select_for_update()
            )
            payments = list(
                wekaCash.objects.filter(pk__in=payment_ids)
                .order_by('tarehe', 'pk')
                .select_for_update()
            )

            CustmDebtPayRec.objects.filter(Q(sale__in=sales) | Q(pay__in=payments)).delete()

            wekaCash.objects.filter(pk__in=payment_ids).update(used_amount=Decimal('0'), cdOrder=None)

            for s in sales:
                s.payed = Decimal('0')

            orders = list(
                creditDebtOrder.objects.filter(customer=cust, by__user__company=kampuni)
                .order_by('pk')
                .select_for_update()
            )
            last_order = orders[-1] if orders else None
            exceeded_payments = []
            created_links = 0
            sale_index = 0

            for pay in payments:
                remaining = Decimal(str(pay.Amount or 0))
                allocated = Decimal('0')

                while remaining > 0 and sale_index < len(sales):
                    sale = sales[sale_index]
                    amount = Decimal(str(sale.amount or 0))
                    paid = Decimal(str(sale.payed or 0))
                    due = amount - paid

                    if due <= 0:
                        sale_index += 1
                        continue

                    apay = due if due <= remaining else remaining

                    rec = CustmDebtPayRec()
                    rec.pay = pay
                    rec.sale = sale
                    rec.Debt = due
                    rec.Apay = apay
                    rec.save()
                    created_links += 1

                    sale.payed = paid + apay
                    allocated += apay
                    remaining -= apay

                    if sale.payed >= amount:
                        sale_index += 1

                pay.used_amount = allocated
                pay.cdOrder = None
                pay.save(update_fields=['used_amount', 'cdOrder'])

                if remaining > Decimal('0.01'):
                    exceeded_payments.append({
                        'pay_id': pay.pk,
                        'amount': float(pay.Amount or 0),
                        'allocated': float(allocated),
                        'exceeded': float(remaining),
                        'tarehe': pay.tarehe.strftime('%Y-%m-%d %H:%M') if pay.tarehe else '',
                        'kutoka': pay.kutoka or '',
                        'maelezo': pay.maelezo or '',
                        'on_order': False,
                        'order_id': None,
                        'last_order_id': last_order.pk if last_order else None,
                        'has_credit_order': last_order is not None,
                    })

            for s in sales:
                s.save(update_fields=['payed'])

            for order in orders:
                order_sales = [sale for sale in sales if sale.cdorder_id == order.id]
                order_amount = sum(Decimal(str(sale.amount or 0)) for sale in order_sales)
                order_paid_sales = sum(Decimal(str(sale.payed or 0)) for sale in order_sales)

                base_amount = order_amount if order_amount > 0 else Decimal(str(order.amount or 0))
                base_consumed = order_amount if order_amount > 0 else Decimal(str(order.consumed or 0))

                order.amount = base_amount
                order.consumed = base_consumed
                order.paid = order_paid_sales
                order.prepaid_order = order_paid_sales > base_consumed
                order.save(update_fields=['amount', 'consumed', 'paid', 'prepaid_order'])

        metrics = check_customer_records_metrics(cust, kampuni)
        exceeded_total = sum(item['exceeded'] for item in exceeded_payments)

        swa_msg = 'Marekebisho ya malipo yamekamilika'
        eng_msg = 'Payment reconciliation completed successfully'
        if exceeded_payments:
            swa_msg = (
                f'Marekebisho yamekamilika. Kuna malipo {len(exceeded_payments)} '
                f'yaliyozidi (jumla {exceeded_total:.2f}). Chagua hatua hapa chini.'
            )
            eng_msg = (
                f'Reconciliation completed. {len(exceeded_payments)} exceeded payment(s) '
                f'found (total {exceeded_total:.2f}). Choose an action below.'
            )

        return JsonResponse({
            'success': True,
            'swa': swa_msg,
            'eng': eng_msg,
            'links': created_links,
            'topup': 0,
            'exceeded_payments': exceeded_payments,
            'has_exceeded_payments': bool(exceeded_payments),
            **metrics,
        })
    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'swa': 'Marekebisho yameshindwa kutokana na hitilafu',
            'eng': 'Reconciliation failed due to an error'
        })


@login_required(login_url='login')
def checkCustomerRecords(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'swa': 'Bad Request', 'eng': 'Bad Request'})

    try:
        cust_id = int(request.POST.get('cust', 0))
        todo = todoFunct(request)
        useri = todo['useri']
        kampuni = todo['kampuni']

        if not useri.admin:
            return JsonResponse({
                'success': False,
                'swa': 'Hauna ruhusa ya kufanya ukaguzi huu',
                'eng': 'You have no permission to run this check',
            })

        cust = wateja.objects.get(Q(Interprise__company=kampuni) | Q(allEntp=True), pk=cust_id)
        metrics = check_customer_records_metrics(cust, kampuni)

        return JsonResponse({
            'success': True,
            'swa': 'Ukaguzi umekamilika',
            'eng': 'Check completed successfully',
            **metrics,
        })
    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'swa': 'Ukaguzi umeshindikana',
            'eng': 'Check failed due to an error',
        })


@login_required(login_url='login')
def applyCustomerRecordCorrection(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'swa': 'Bad Request', 'eng': 'Bad Request'})

    try:
        cust_id = int(request.POST.get('cust', 0))
        actual_debt_raw = request.POST.get('actualDebt', '').strip()
        actual_credit_raw = request.POST.get('actualCredit', '').strip()
        todo = todoFunct(request)
        useri = todo['useri']
        kampuni = todo['kampuni']

        if not useri.admin:
            return JsonResponse({
                'success': False,
                'swa': 'Hauna ruhusa ya kufanya marekebisho haya',
                'eng': 'You have no permission to apply this correction',
            })

        has_debt = actual_debt_raw not in ('', None)
        has_credit = actual_credit_raw not in ('', None)
        if has_debt == has_credit:
            return JsonResponse({
                'success': False,
                'swa': 'Jaza deni halisi AU mkopo halisi, si zote mbili',
                'eng': 'Enter either actual debt OR actual credit, not both',
            })

        cust = wateja.objects.get(Q(Interprise__company=kampuni) | Q(allEntp=True), pk=cust_id)
        last_order = creditDebtOrder.objects.filter(
            customer=cust,
            by__user__company=kampuni,
        ).order_by('pk').last()

        if last_order is None:
            return JsonResponse({
                'success': False,
                'swa': 'Hakuna oda ya mkopo ya kurekebisha',
                'eng': 'No credit order found to apply correction',
            })

        with transaction.atomic():
            order = creditDebtOrder.objects.select_for_update().get(pk=last_order.pk)
            consumed = Decimal(str(order.consumed or 0))

            if has_credit:
                actual_credit = Decimal(str(actual_credit_raw or 0))
                order.paid = consumed + actual_credit
                if order.paid > Decimal(str(order.amount or 0)):
                    order.amount = order.paid
                order.prepaid_order = actual_credit > 0
            else:
                actual_debt = Decimal(str(actual_debt_raw or 0))
                order.amount = consumed + actual_debt
                order.paid = consumed
                order.prepaid_order = False

            order.save(update_fields=['amount', 'paid', 'consumed', 'prepaid_order'])

        metrics = check_customer_records_metrics(cust, kampuni)
        return JsonResponse({
            'success': True,
            'swa': 'Marekebisho yamehifadhiwa',
            'eng': 'Correction saved successfully',
            **metrics,
        })
    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'swa': 'Marekebisho yameshindikana',
            'eng': 'Correction failed due to an error',
        })


@login_required(login_url='login')
def resolveCustomerExceededPayment(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'swa': 'Bad Request', 'eng': 'Bad Request'})

    try:
        cust_id = int(request.POST.get('cust', 0))
        pay_id = int(request.POST.get('payId', 0))
        action = (request.POST.get('action') or '').strip().lower()
        order_id_raw = request.POST.get('orderId', '').strip()
        todo = todoFunct(request)
        useri = todo['useri']
        kampuni = todo['kampuni']

        if not useri.admin:
            return JsonResponse({
                'success': False,
                'swa': 'Hauna ruhusa ya kufanya marekebisho haya',
                'eng': 'You have no permission to apply this action',
            })

        if action not in ('delete', 'apply_order'):
            return JsonResponse({
                'success': False,
                'swa': 'Chaguo halali: delete au apply_order',
                'eng': 'Valid action: delete or apply_order',
            })

        cust = wateja.objects.get(pk=cust_id, Interprise__company=kampuni)
        customer_order_ids = list(
            creditDebtOrder.objects.filter(
                customer=cust,
                by__user__company=kampuni,
            ).values_list('id', flat=True)
        )

        with transaction.atomic():
            pay = wekaCash.objects.select_for_update().get(
                pk=pay_id,
                Interprise__company=kampuni,
            )
            if not (pay.customer_id == cust.pk or pay.cdOrder_id in customer_order_ids):
                return JsonResponse({
                    'success': False,
                    'swa': 'Malipo hayo hayahusiani na mteja huyu',
                    'eng': 'This payment does not belong to this customer',
                })

            allocated = _payment_allocated_to_sales(pay)
            amount = Decimal(str(pay.Amount or 0))
            exceeded = amount - allocated
            tolerance = Decimal('0.01')

            if exceeded <= tolerance:
                return JsonResponse({
                    'success': False,
                    'swa': 'Malipo haya hayana kiasi kilichozidi',
                    'eng': 'This payment has no exceeded amount',
                })

            if action == 'delete':
                pay_recs = CustmDebtPayRec.objects.filter(pay=pay)
                for pr in pay_recs:
                    sale = fuelSales.objects.select_for_update().get(pk=pr.sale_id)
                    sale.payed = Decimal(str(sale.payed or 0)) - Decimal(str(pr.Apay or 0))
                    sale.save(update_fields=['payed'])
                    if sale.cdorder_id:
                        order = creditDebtOrder.objects.select_for_update().get(pk=sale.cdorder_id)
                        order.paid = Decimal(str(order.paid or 0)) - Decimal(str(pr.Apay or 0))
                        if order.paid < 0:
                            order.paid = Decimal('0')
                        order.prepaid_order = order.paid > Decimal(str(order.consumed or 0))
                        order.save(update_fields=['paid', 'prepaid_order'])

                if pay.cdOrder_id:
                    order = creditDebtOrder.objects.select_for_update().get(pk=pay.cdOrder_id)
                    order.paid = Decimal(str(order.paid or 0)) - exceeded
                    if order.paid < 0:
                        order.paid = Decimal('0')
                    order.prepaid_order = order.paid > Decimal(str(order.consumed or 0))
                    order.save(update_fields=['paid', 'prepaid_order'])

                pay_recs.delete()
                pay.delete()

                swa_msg = 'Malipo yaliyozidi yamefutwa'
                eng_msg = 'Exceeded payment deleted successfully'
            else:
                if order_id_raw:
                    order = creditDebtOrder.objects.select_for_update().get(
                        pk=int(order_id_raw),
                        customer=cust,
                        by__user__company=kampuni,
                    )
                else:
                    order = creditDebtOrder.objects.select_for_update().filter(
                        customer=cust,
                        by__user__company=kampuni,
                    ).order_by('pk').last()
                    if order is None:
                        return JsonResponse({
                            'success': False,
                            'swa': 'Hakuna oda ya mkopo ya kuongeza kiasi kilichozidi',
                            'eng': 'No credit order found to apply exceeded amount',
                        })

                order_paid = Decimal(str(order.paid or 0)) + exceeded
                order_amount = Decimal(str(order.amount or 0))
                order_consumed = Decimal(str(order.consumed or 0))

                order.paid = order_paid
                if order_paid > order_amount:
                    order.amount = order_paid
                order.prepaid_order = order_paid > order_consumed
                order.save(update_fields=['amount', 'paid', 'prepaid_order'])

                pay.cdOrder = order
                pay.used_amount = amount
                pay.save(update_fields=['cdOrder', 'used_amount'])

                swa_msg = f'Kiasi kilichozidi ({float(exceeded):.2f}) kimeongezwa kwenye oda ya mkopo'
                eng_msg = f'Exceeded amount ({float(exceeded):.2f}) added to credit order'

        metrics = check_customer_records_metrics(cust, kampuni)
        return JsonResponse({
            'success': True,
            'swa': swa_msg,
            'eng': eng_msg,
            **metrics,
        })
    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'swa': 'Hatua imeshindikana',
            'eng': 'Action failed due to an error',
        })


@login_required(login_url='login')
def mobileMoneySales(request):
    try:
        todo = todoFunct(request)
        return render(request, 'customerMobileMoneySales.html', todo)
    except Exception as err:
        print(err)
        traceback.print_exc() 
        return render(request, 'pagenotFound.html')

@login_required(login_url='login')
def orderPayments(request):
    try:
        i = int(request.GET.get('cust', 0))
        todo = todoFunct(request)
        shell = todo['shell']
        kampuni = todo['kampuni']
        general = todo['general']


        cust = wateja.objects.get(Q(Interprise__company=kampuni)|Q(allEntp=True), pk=i)

        orders = creditDebtOrder.objects.filter(customer=cust.id, by__user__company=kampuni).annotate(
            balance=F('amount')-F('consumed'),
            bal_deni = F('amount') - F('paid'),
            credit=F('paid')-F('consumed'),
            deni = F('consumed') - F('paid')
        ).order_by('-pk')

        hasLastCd = orders.filter(balance__gt=0).exists()
        lastCd = orders.first()

        addNewOrder = not orders.exists() or (lastCd and lastCd.amount == lastCd.consumed) if not general else False

        totD = fuelSales.objects.filter(
            customer=cust,
            by__Interprise__company=kampuni
        ).aggregate(
            total_debt=Sum(F('amount') - F('payed'))
        )['total_debt'] or 0

        # if not general:
        #     orders = orders.filter(by__Interprise=shell)

        num = orders.count()
        
        p = Paginator(orders, 15)
        page_num = request.GET.get('page', 1)

        try:
            page = p.page(page_num)
        except EmptyPage:
            page = p.page(1)

        pg_number = p.num_pages

        # Calculate totals for all orders
        totals = orders.aggregate(
            total_amount=Sum('amount'),
            total_paid=Sum('paid'),
            total_consumed=Sum('consumed')
        )

        total_due = (totals['total_amount'] or 0) - (totals['total_consumed'] or 0)
        total_credit = (totals['total_paid'] or 0) - (totals['total_consumed'] or 0)
        custBalance = float(totD) - float(cust.debt_limit)

        todo.update({
            'isCustomer': True,
            'isOrderPayments': True,
            'custBalance': custBalance,
            'cust': cust,
            'orders': page,
            'hasLastCd': hasLastCd,
            'p_num': page_num,
            'pages': pg_number,
            'order_num': num,
            'totD': totD,
            'lastCd': lastCd,
            'total_amount': totals['total_amount'] or 0,
            'total_paid': totals['total_paid'] or 0,
            'total_consumed': totals['total_consumed'] or 0,
            'total_due': total_due,
            'total_credit': total_credit,
            'addOrder': addNewOrder,
        })

        return render(request, 'custm_order.html', todo)
    except:
        return render(request, 'pagenotFound.html')



@login_required(login_url='login')
def ViewOrder(request):
    try:
        i = int(request.GET.get('i', 0))
        cust = int(request.GET.get('cust', 0))
        todo = todoFunct(request)
        shell = todo['shell']
        kampuni = todo['kampuni']
        general = todo['general']

        # Get the credit debt order
        order = creditDebtOrder.objects.get(pk=i, by__user__company=kampuni,customer=cust)
      
        # if not general:
        #     order = creditDebtOrder.objects.get(pk=i, by__Interprise=shell.id)

        # Get customer details
        customer = order.customer
        orders = creditDebtOrder.objects.filter(customer=customer.id, by__user__company=kampuni).annotate(
            bal_deni = F('amount') - F('paid'),
            balance=F('amount')-F('consumed'),
            credit=F('paid')-F('consumed'),
            deni = F('consumed') - F('paid')
        )
        
        hasLastCd = orders.filter(balance__gt=0).exists()
        lastCd = orders.filter(balance__gt=0).order_by('pk').first()

        addNewOrder =  not (orders.exists() or hasLastCd )  if not general else False
       

        # Get all sales invoices related to this order
        sales_invoices = fuelSales.objects.filter(
            cdorder=order,
            by__Interprise__company=kampuni
        ).order_by('pk')

        totD = fuelSales.objects.filter(
            customer=order.customer,
            by__Interprise__company=kampuni
        ).aggregate(
            total_debt=Sum(F('amount') - F('payed'))
        )['total_debt'] or 0

        # if not general:
        #     sales_invoices = sales_invoices.filter(by__Interprise=shell)

        # Get all payments related to this order
        payments = wekaCash.objects.filter(
            cdOrder=order,
            Interprise__company=kampuni
        ).order_by('pk')

        # print(payments.exists())

        # if not general:
        #     payments = payments.filter(Interprise=shell)

        # Get payment records for sales under this order
        payment_records = CustmDebtPayRec.objects.filter(
            sale__cdorder=order
        ).annotate(tarehe=F('pay__tarehe'),Akaunti=F('pay__Akaunt'),Amount=F('pay__Amount'),by=F('pay__by'))

        # Calculate order summary
        order_balance = float(order.amount - order.consumed)
        order_credit = float(order.paid - order.consumed)
        order_debt = float(order.consumed - order.paid) if order.consumed > order.paid else 0

        # Calculate sales summary
        total_sales_amount = sales_invoices.aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_sales_paid = sales_invoices.aggregate(
            total=Sum('payed')
        )['total'] or 0

        total_sales_debt = float(total_sales_amount - total_sales_paid)

        # Calculate payments summary
        total_payments = payments.aggregate(
            total=Sum('Amount')
        )['total'] or 0

        # Group sales by fuel type for better visualization
        sales_fuel_summary = []
        fuel_sold = saleList.objects.filter(
            sale__in=sales_invoices
        ).annotate(
            total_qty=Sum('qty_sold'),
            total_amount=Sum(F('qty_sold') * F('sa_price')),
            avg_price=Sum(F('qty_sold') * F('sa_price')) / Sum('qty_sold'),
            theFuel__name=F('theFuel__name')
        )

        fuel_sales = fuel_sold.values('theFuel__name').annotate(
            total_qty=Sum('qty_sold'),
            total_amount=Sum(F('qty_sold') * F('sa_price')),
            avg_price=Sum(F('qty_sold') * F('sa_price')) / Sum('qty_sold'),
        )

        for fuel_data in fuel_sales:
            sales_fuel_summary.append({
                'fuel_name': fuel_data['theFuel__name'],
                'total_qty': fuel_data['total_qty'],
                'total_amount': fuel_data['total_amount'],
                'avg_price': fuel_data['avg_price'] or 0
            })

        # Get all dates from wekaCash and fuelSales

        #   get all transaction dates
        cash_dates = payment_records.values_list('tarehe', flat=True) 
        prepay=payments.values_list('tarehe', flat=True)

        sales_dates = sales_invoices.values_list('date', flat=True)

        # Combine and sort dates in descending order
        all_dates = list(cash_dates) + list(sales_dates) + list(prepay)
        # Remove duplicates and sort in descending order
        unique_dates = sorted(set(all_dates))

        # Prepare a list of transactions grouped by date
        cr = order.paid 
        dr = 0
        paye = 0
        blc = order.amount
        deni = float(0)
        transactions_by_date = []
        
        prevOdaPay = CustmDebtPayRec.objects.filter(Q(pay__cdOrder=order)|Q(pay__tarehe__gte=order.date),sale__customer=customer).exclude(sale__cdorder=order).order_by('pk')
        paidDebt = float(prevOdaPay.aggregate(total=Sum('Apay'))['total'] or 0)
        deni = paidDebt

        # print(paidDebt)
        if deni > 0:
            transactions_by_date.append({
                'date': order.date,
                'sale': None,
                'pay': None,
                'cr': 0,
                'dr': round(deni,2),
                'balance': round(0, 2)
            })

        for trans_date in unique_dates:
            # Add sales invoices for this date
            daily_sales = fuel_sold.filter(sale__date = trans_date )
            daily_payments = wekaCash.objects.filter(Q(customer=customer)|Q(cdOrder=order), tarehe = trans_date)
            


            if daily_sales.exists():
                for sale in daily_sales:
                    theAmo = sale.qty_sold * sale.sa_price

                    dr += theAmo
                    blc = float(float(blc) - float(theAmo))
                    
                    

                    deni = 0 if paye >= (deni+float(theAmo)) else float(deni+float(theAmo)- float(paye))
                    paye = paye - float(theAmo) if paye >= deni else 0

                    transactions_by_date.append({
                        'date':None,
                        'sale': sale,
                        'pay':None,
                        'cr': round(paye,2) if float(round(paye,2) )> 0 else 0,
                        'dr': round(deni,2),
                        'balance': round(blc, 2)
                    })
                    cr = cr - theAmo

                         

              
            if daily_payments.exists():
                for pay in daily_payments:
                    paye = float(float(paye) + float(pay.Amount))- deni
                    deni = 0 if deni==0 or float(pay.Amount) >= deni else float(deni - float(pay.Amount))
                    
                    transactions_by_date.append({
                        'date':None,
                        'sale': None,
                        'pay':pay,
                        'cr': round(paye,2) if float(round(paye,2)) > 0 else round(float(pay.Amount),2),
                        'dr': round(deni,2),
                        'balance': round(blc, 2)
                    })

                    
                   
                    

        # Calculate totals for sales_fuel_summary
        total_qty = 0
        total_amount = 0
        for fuel_data in sales_fuel_summary:
            total_qty += fuel_data['total_qty']
            total_amount += fuel_data['total_amount']

        # Add total row to sales_fuel_summary
        sales_fuel_summary.append({
            'fuel_name': 'TOTAL',
            'total_qty': total_qty,
            'total_amount': total_amount,
            'avg_price': total_amount / total_qty if total_qty > 0 else 0
        })# Get all dates from wekaCash and fuelSales
      
     

        # Progress calculation
        progress_percentage = (order.consumed / order.amount * 100) if order.amount > 0 else 0
        payment_percentage = (order.paid / order.amount * 100) if order.amount > 0 else 0

        payAfter = payment_records.exclude(pay__in=payments).distinct('pay') 
        allPayments = []
        for p in payments:
            allPayments.append({
                'payment': p,
                'date': p.tarehe,
                'type': 'prepayment'
            })

        for p in payAfter:
            allPayments.append({
                'payment': p.pay,
                'date': p.pay.tarehe,
                'type': 'payment'
            })

        # Sort by date in descending order
        Allpaymnts = sorted(allPayments, key=lambda x: x['date'], reverse=False)

        
        custBalance = float(totD) - float(customer.debt_limit)
        todo.update({
            'isCustomer': True,
            'isOrderView': True,
            'order': order,
            'customer': customer,
            'sales_invoices': sales_invoices,
            'payments': payments,
            'allPayments': Allpaymnts,
            'payment_records': payment_records.order_by('pk'),
            'payAfter':payAfter,
            'sales_fuel_summary': sales_fuel_summary,
            'transactions_by_date': transactions_by_date,
            # Order summary
            'order_balance': order_balance,
            'order_credit': order_credit,
            'order_debt': order_debt,
            'progress_percentage': min(progress_percentage, 100),
            'payment_percentage': min(payment_percentage, 100),
            'cust': customer,
            # Totals
            'total_sales_amount': total_sales_amount,
            'total_sales_paid': total_sales_paid,
            'total_sales_debt': total_sales_debt,
            'total_payments': total_payments,
            'totD':totD,
            'custBalance':custBalance,
            # Counts
            'sales_count': sales_invoices.count(),
            'payments_count': payments.count(),
            'hasLastCd': hasLastCd,
            'addOrder': addNewOrder,
            'lastCd': lastCd,
        })

        html = 'cust_orderView.html'
        pr = int(request.GET.get('t', 0))
        lang = int(request.GET.get('lang', 0))

        if pr:
            todo.update({
                'langSet': lang
            })
            html = 'cust_orderPrint.html'

        return render(request, html, todo)
        
    except Exception as err :
        print(err)
        traceback.print_exc() 
        return render(request, 'pagenotFound.html')

@login_required(login_url='login')
def customerAttachments(request):
    try:
        i = int(request.GET.get('cust', 0))
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        general = todo['general']
        
        # Get the customer
        cust = wateja.objects.get(Interprise__company=kampuni, pk=i)
        
        # Get all attachments for this customer
        attach = attachments.objects.filter(cust=cust).order_by('-pk')

        cdOrder =   creditDebtOrder.objects.filter(customer=cust.id,by__user__company=kampuni).annotate(due=F('amount')-F('consumed'),bal_deni = F('amount') - F('paid'),credit=F('paid')-F('consumed')).order_by('-pk')
        lastCd = cdOrder.first()
        totD = fuelSales.objects.filter(
            customer=cust,
            by__Interprise__company=kampuni
        ).aggregate(
            total_debt=Sum(F('amount') - F('payed'))
        )['total_debt'] or 0

        # Add new credit debt order if the last order amount = consumed
        addNewOrder = not cdOrder.exists() or (lastCd and lastCd.amount == lastCd.consumed) if not general else False
        newcode = '01'
        if cdOrder.exists():
            newcode = cdOrder.last().Invo_no + 1
        
        todo.update({
            'isCustomer': True,
            'isCustomerAttach': True,
            'cust': cust,
            'attachments': attach,
            'addOrder':addNewOrder,
            'lastCd':lastCd,
            'newcode':newcode,
            'totD':totD,
            'custBalance': float(totD) - float(cust.debt_limit),
        })
        
        return render(request, 'custattach.html', todo)
    except:
        return render(request, 'pagenotFound.html')

        

@login_required(login_url='login')
def customerStatement(request):
    try:
        cust_id = int(request.GET.get('cust', 0))
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        general = todo['general']
        useri = todo['useri']



        cust = wateja.objects.get(pk=cust_id, Interprise__company=kampuni) 
        todo.update({
            'isCustomer': True,
            'isCustomerStatement': True,
            'cust': cust,
        })

        stxns = fuelSales.objects.filter(customer=cust, by__Interprise__company=kampuni.id).distinct('by__Interprise')
        todo.update({
            'stations': stxns,
        })

        return render(request, 'customer_statement.html', todo)

    except:
        todo = todoFunct(request)
        return render(request, 'pagenotFound.html', todo)  
      


@login_required(login_url='login')
def customerStatementData(request):
    """Return JSON data for customer statement.
    Expects POST params: cust, dur, from, to, station
    """
    try:
        cust_id = int(request.POST.get('cust', 0))
        dur = request.POST.get('dur', 'this_month')
        tFr = request.POST.get('tFr', '')
        tTo = request.POST.get('tTo', '')
        station = int(request.POST.get('station', 0) or 0)

        todo = todoFunct(request)
        kampuni = todo['kampuni']
        general = todo['general']
        useri = todo['useri']
        cust = wateja.objects.get(pk=cust_id, Interprise__company=kampuni)

        # determine date range
     
        # print(tFr,tTo)
        # sales for customer in range
        sales_qs = fuelSales.objects.filter(customer=cust, by__Interprise__company=kampuni, recDate__gte=tFr, recDate__lte=tTo).order_by('pk')
        payments_qs = wekaCash.objects.filter(Q(customer=cust)|Q(cdOrder__customer=cust), Interprise__company=kampuni,Akaunt__isnull=False,tarehe__gte=tFr, tarehe__lte=tTo).order_by('pk')
        lastPay  = wekaCash.objects.filter(Q(customer=cust)|Q(cdOrder__customer=cust), Interprise__company=kampuni,Akaunt__isnull=False,tarehe__lt=tFr).exclude(Amount=0).order_by('pk').last()
        # print('lastPay', lastPay.Amount if lastPay else None)
        # print('lastPay', lastPay.tarehe if lastPay else None)
        # print(len(sales_qs),len(payments_qs))
        invo_payed = CustmDebtPayRec.objects.filter(pay = lastPay,sale__recDate__lt=tFr).order_by('pk')
        last_payee = CustmDebtPayRec.objects.filter(sale__customer=cust).order_by('pk').last()
        

        # print('pay_Amo_last_pay',last_payee.pay.Amount)
        # print('pay_Amo_last_payBalance',( last_payee.pay.Amount - last_payee.pay.used_amount) if last_payee else None  )
        # print('Used Amount',(last_payee.pay.used_amount) if last_payee else None  )
        # print('pay_Amo_last_payApay',( last_payee.Apay) if last_payee else None  )
        # print('pay_Amo_last_pay',last_payee.pay.tarehe)

        # print('last_pay_Invo',last_payee.sale.amount)
        # print('last_pay_Invo',last_payee.sale.date)

        # print('invo_payed', invo_payed.last().sale.amount if invo_payed.exists() else None)
        opening_balance = float(lastPay.Amount if lastPay else 0)
        opening_balance -= float(invo_payed.aggregate(total=Sum('Apay'))['total'] or 0)
        last_payed_invo = invo_payed.last() if invo_payed.exists() else None
        # print('start', opening_balance)
        # print('payed_invo',invo_payed.last())
        if  last_payed_invo:
            rem_debt = last_payed_invo.Debt - last_payed_invo.Apay
            # print('RemDebt',rem_debt)
            opening_balance -= float(rem_debt)
            invo_payed_sales = fuelSales.objects.filter(customer=cust, by__Interprise__company=kampuni, recDate__lt=tFr, pk__gt=last_payed_invo.sale.pk)
            total_invo_amo = float(invo_payed_sales.aggregate(total=Sum('amount'))['total'] or 0)
            opening_balance -= total_invo_amo
            # print('after invo', opening_balance)
         

            cdorder_obj = last_payed_invo.sale.cdorder
            if cdorder_obj:
                # Safely get the cdorder date (may be None)
                allInvo_before_tFr = fuelSales.objects.filter(cdorder=cdorder_obj, recDate__lt=tFr)
                firstInvo = allInvo_before_tFr.order_by('pk').first()
                cd_date = getattr(cdorder_obj, 'date', None)
                # Build Q only with non-None values to avoid ValueError
                # print(cd_date,firstInvo.recDate if firstInvo else None)
                q = Q(cdOrder=cdorder_obj)                
                if cd_date is not None:
                    q |= Q(tarehe__gt=cd_date, customer=cust)
                else:
                    if firstInvo:
                        q |= Q(tarehe__gt=firstInvo.recDate, customer=cust)

                tot_pay_cd = wekaCash.objects.filter(q, tarehe__lt=tFr).aggregate(total=Sum('Amount'))['total'] or 0
                # opening_balance = float(tot_pay_cd)
                
                
                
                total_invo_cd_amo = float(allInvo_before_tFr.aggregate(total=Sum('amount'))['total'] or 0)
                # opening_balance -= total_invo_cd_amo
                # print('after cdorder', opening_balance)
            # else:
            #     # No cdorder linked; sum payments for the customer before tFr only
            #     tot_pay_cd = wekaCash.objects.filter(customer=cust, tarehe__lt=tFr).aggregate(total=Sum('Amount'))['total'] or 0
            #     opening_balance = float(tot_pay_cd)
              
            #     # No cdorder-related invoices to subtract
            #     allInvo_before_tFr = fuelSales.objects.none()
            #     print('after no cdorder', opening_balance)
        else:
            # No payments before tFr; sum all invoices before tFr as debt
            allInvo_before_tFr = fuelSales.objects.filter(customer=cust, by__Interprise__company=kampuni, recDate__lt=tFr)
            total_invo_amo = float(allInvo_before_tFr.aggregate(total=Sum('amount'))['total'] or 0)
            opening_balance -= total_invo_amo

            
            theLastPay = CustmDebtPayRec.objects.filter(sale__customer = cust,pay__tarehe__lt=lastPay.tarehe).order_by('pk') if lastPay is not None else None
            if theLastPay is not None and theLastPay.exists():    
                payTr = theLastPay.last().pay
                pmnts = wekaCash.objects.filter(Q(customer=cust)|Q(cdOrder__customer=cust),tarehe__gte=payTr.tarehe,tarehe__lt=tFr)
                # for pym in pmnts:
                    # print('Payment',pym.Amount)

                baybalance = float(pmnts.aggregate(total=Sum('Amount'))['total'] or 0)
                payedInvo = float(CustmDebtPayRec.objects.filter(sale__customer=cust,pay__tarehe__gte = payTr.tarehe,pay__tarehe__lt=tFr).aggregate(total=Sum('Apay'))['total'] or 0)
                opening_balance = float(baybalance-payedInvo)

                # print('Last Paid',payTr.Amount)
                # print('Pay Balance',baybalance)
                # print('apayedInvo', payedInvo)
            # print('Cust', cust.jina)
          
        # fuel summary: group by fuel type using saleList
        fuel_summary = []
        sale_items = saleList.objects.filter(sale__in=sales_qs)
        fuelSummaryData = sale_items if not station else sale_items.filter(sale__by__Interprise__pk=station)
        fuel_agg = fuelSummaryData.values('theFuel__name').annotate(total_qty=Sum('qty_sold'), total_amount=Sum(F('qty_sold') * F('sa_price')))
        for fa in fuel_agg:
            fuel_summary.append({
                'fuel': fa.get('theFuel__name'),
                'qty': float(fa.get('total_qty') or 0),
                'amount': float(fa.get('total_amount') or 0),
                'avg_price': float(fa.get('total_amount') or 0) / float(fa.get('total_qty') or 1)
            })

        # payments summary grouped by date and account
        payments_summary = []
        
        for p in payments_qs:
           
            acct = p.Akaunt.Akaunt_name if p.Akaunt else '' 
           
            payments_summary.append({
                'date': p.tarehe,
                'account': acct,
                'amount': float(getattr(p, 'Amount', 0) or 0)
            })

        # transactions ledger: combine sales and payments sorted by date
        txs = []
        for s in sale_items:
            # compute qty and amount for this sale
            # items = saleList.objects.filter(sale=s)
            # qty = items.aggregate(sumi=Sum('qty_sold'))['sumi'] or 0
            # amount = float(getattr(s, 'amount', 0) or 0)
            txs.append({
                'st': s.sale.by.Interprise.pk,
                'pay':False,
                'use':True,
                'opening':False,
                'date': s.sale.date,
                'type':'Tumia' if useri.langSet == 0 else 'Use',
                'station': str(getattr(s.sale.by, 'Interprise', '') or ''),
                'details': f'INVO-{s.sale.code}',
                'driver': getattr(s.sale, 'driver', '') or '',
                'vehicle': getattr(s.sale, 'vihecle', '') or '',
                'recorded_by':f'{s.sale.by.user.user.first_name} {s.sale.by.user.user.last_name}',
                'fuel_price': float(s.sa_price),
                'qty': float(s.qty_sold),
                'amount': float(s.qty_sold*s.sa_price),
                'fuelN':s.theFuel.name
            })

        for p in payments_qs:
            txs.append({
                'st': p.Interprise.pk,
                'pay':True,
                'use':False,
                'opening':False,
                'date': p.tarehe,
                'type': 'LipA' if useri.langSet == 0 else 'Pay',
                'station': str(getattr(p, 'Interprise', '')) or '',
                'details': p.Akaunt.Akaunt_name if p.Akaunt else '',
                'driver': '',
                'vehicle': '',
                'recorded_by': f'{p.by.user.first_name} {p.by.user.last_name}',
                'fuel_price': 0,
                'qty': 0,
                'amount': float(getattr(p, 'Amount', 0) or 0),
                'fuelN':''
            })

          
        if opening_balance != 0:
            date_val = parse_datetime(tFr) if isinstance(tFr, str) else tFr
            if date_val is None and isinstance(tFr, str):
                try:
                    date_val = datetime.datetime.fromisoformat(tFr)
                except Exception:
                    date_val = tFr

            txs.append({
                'st': 0,
                'pay': False,
                'use': False,
                'opening': True,
                'date': date_val,
                'type': 'Kianzio' if useri.langSet == 0 else 'Opening',
                'station': '',
                'details': '',
                'transporter': '',
                'driver': '',
                'vehicle': '',
                'recorded_by': '',
                'fuel_price': 0,
                'qty': 0,
                'amount': opening_balance,
                'fuelN': ''
            })  


        txs_sorted = sorted(txs, key=lambda x: x.get('date'))

        # running balance (credit reduces balance)
        # print(opening_balance)
        credit = opening_balance
        transactions = []
        running = abs(credit) if credit < 0 else 0
        
        running =(running - credit) if credit > 0 else running

        
        for t in txs_sorted:
            amt = float(t.get('amount') or 0)
            if t.get('use'):
                running += amt
                credit -= amt
                
            if t.get('pay'):
                running -= amt
                credit += amt
            
            debt = running if running > 0 else 0.0
            
            transactions.append({
                'st': t.get('st'),
                'pay': t.get('pay'),
                'use': t.get('use'),
                'opening': t.get('opening'),
                'date': t.get('date'),
                'type': t.get('type'),
                'station': t.get('station'),
                'details': t.get('details'),
                'driver': t.get('driver'),
                'vehicle': t.get('vehicle'),
                'recorded_by': t.get('recorded_by'),
                'fuel_price': t.get('fuel_price'),
                'qty': t.get('qty'),
                'amount': amt,
                'credit': credit if credit > 0 else 0.0,
                'debt': debt,
                'fuelN':t.get('fuelN'),
            })

        kituo = 'Vyote' if useri.langSet == 0 else 'All Stations'
        if station:
            st_obj = Interprise.objects.get(pk=station,company=kampuni)
            kituo = str(st_obj.name)

         # prepare final data    

        data = {
            'success': True,
            'kituo': kituo,
            'fuel_summary': fuel_summary,
            'payments_summary': payments_summary,
            'transactions': transactions,
        }

        return JsonResponse(data, safe=True)

    except Exception as e:
        print(e)
        traceback.print_exc() 
        return JsonResponse({'success': False, 'error': str(e)})


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
                debt_limit = float(request.POST.get('debt_limit', 0))
                paid = float(request.POST.get('paidAmount', 0))
                payAcc = int(request.POST.get('paymentAccount', 0))
                prepaid = int(request.POST.get('prepaid', 0))
                NewOda = int(request.POST.get('NewOda', 0))
                justLimit = int(request.POST.get('dLimit', 0))
                topUp = int(request.POST.get('topUp', 0))
                ordt = int(request.POST.get('ord', 0))

                customer = wateja.objects.get(pk=cust_id, Interprise__company=kampuni)
                entry = creditDebtOrder.objects.filter(customer=customer, by__user__company=kampuni)
                consume = fuelSales.objects.filter(customer=customer,amount__gt=F('payed')).annotate(deni=F('amount')-F('payed'))
                order = creditDebtOrder()

               

                if not justLimit and not topUp:
                    if not customer.limited_order:
                        customer.limited_order = True
                        customer.save()

                    order.customer = customer
                    order.amount = amount
                    if prepaid:
                        order.paid = paid
                        order.prepaid_order = 1
                    new_code = invoCode(entry)

                    order.by = todo['cheo']
                    order.Invo_no = int(new_code)
                    order.code = TCode({'code': new_code, 'shell': customer.id})
                    order.save()
                    order.date = datetime.datetime.now(tz=timezone.utc)
                    other_consume = consume.filter(~Q(cdorder=None)).aggregate(sumi=Sum('deni'))['sumi'] or 0
                    deni = float(consume.filter(cdorder=None).aggregate(sumi=Sum('deni'))['sumi'] or 0)

                    if float(other_consume) > float(0):
                        order.paid = float(float(paid) - float(other_consume)) if float(float(paid) - float(other_consume)) > 0 else 0
                        # order.amount = float(float(paid) - float(other_consume))

                    if consume.filter(cdorder=None).exists():
                        
                        if float(deni) > float(amount):
                           order.amount = float(deni)
                        else:
                            order.amount = float(amount+deni)   if  prepaid else float(amount)
                        order.consumed = deni

                    order.save()

                if float(customer.debt_limit) == float(0)  or not consume.exists()  or useri.admin:      
                    customer.debt_limit = debt_limit if not topUp else float(customer.debt_limit)
                    customer.save()
                else:
                    if justLimit:
                        data = {
                            'success': False,
                            'swa': 'Huwezi kuweka kikomo cha deni kwa mteja huyu kwa sasa kwani ana deni linalosubiri kulipwa',
                            'eng': 'You cannot set debt limit to this customer now because he has pending debt'
                        }
                        return JsonResponse(data)

                    

                if topUp:
                    order = creditDebtOrder.objects.get(pk=ordt,by__user__company=kampuni)
                    tot_p = float(float(order.paid) + float(amount))
                    order.amount = tot_p  if float(order.amount) < tot_p else float(order.amount)
                    order.paid = tot_p
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
                    payRec.customer = customer
                    payRec.admin_approval = useri.admin
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
                                    break
                                if b.cdorder is None:    
                                    b.cdorder = order
                                else:
                                    updatePayed = b.cdorder
                                    updatePayed.paid = float(float(updatePayed.paid) + float(theP))    
                                    updatePayed.save()    
                                b.save()


                                custP = CustmDebtPayRec()  
                                custP.sale = b
                                custP.pay = payRec   
                                custP.pay.used_amount = float(custP.pay.used_amount) + float(theP)
                                custP.pay.save()
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
                    # 'id': order.id
                }
            else:
                data = {
                    'success': False,
                    'swa': 'Hauna ruhusa ya kitendo hiki kwa sasa',
                    'eng': 'You have no permission for this action'
                }
            return JsonResponse(data)
        except Exception as err:
            print(err)
            traceback.print_exc() 
            data = {
                'success': False,
                'swa': 'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena baadaye',
                'eng': 'The action was unsuccessfully please try again later'
            }
            return JsonResponse(data)
    else:
        return JsonResponse({'success': False, 'swa': 'Bad Request', 'eng': 'Bad Request'})


@login_required(login_url='login')
def delete_unused_order(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            useri = todo['useri']
            manager = todo['manager']
            kampuni = todo['kampuni']

            if useri.admin or manager:
                ord_id = int(request.POST.get('orderId', 0))
                order = creditDebtOrder.objects.get(pk=ord_id, by__user__company=kampuni)
                if order.consumed == 0:
                    # delete all its associated payment and reduct the amount paid from payment accounts and sales invoices
                    pay = wekaCash.objects.filter(cdOrder=order)
                    pay_invo = CustmDebtPayRec.objects.filter(pay__in=pay)
                    for p in pay_invo:
                        sale = p.sale
                        lipwa = float(sale.payed)
                        sale.payed = float(lipwa - float(p.Apay))
                        sale.save()

                        sale.cdorder.paid = float(float(sale.cdorder.paid) - float(p.Apay))
                        sale.cdorder.save()

                        p.delete()
                    order.delete()

                    data = {
                        'success': True,
                        'swa': 'Oda ya deni imefutwa kikamilifu',
                        'eng': 'Credit order deleted successfully'
                    }
                else:
                    data = {
                        'success': False,
                        'swa': 'Oda ya deni haiwezi kufutwa kwani tayari kuna mauzo yarirekodiwa',
                        'eng': 'Credit order cannot be deleted because it has already incurred consumption'
                    }
            else:
                data = {
                    'success': False,
                    'swa': 'Hauna ruhusa ya kitendo hiki kwa sasa',
                    'eng': 'You have no permission for this action'
                }
            return JsonResponse(data)
        except Exception as err:
            print(err)
            traceback.print_exc() 
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
                     if Frcont:
                         cont_From = Purchases.objects.get(pk=Frcont, record_by__company=kampuni)
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
                        puRec = PuList.objects.select_related('pu').get(pk=rec['tnk'])
                        line_pu = puRec.pu
                        if rcv.FromPurchase_id is None:
                            rcv.FromPurchase = line_pu
                            rcv.Incharge = line_pu.record_by
                            rcv.save(update_fields=['FromPurchase', 'Incharge'])
                            cont_From = line_pu
                        puRec.rcvd = float(float(puRec.rcvd) + trqty)
                        puRec.save()
                        if not PuList.objects.filter(pu=line_pu, qty__gt=F('rcvd')).exists():
                            line_pu.closed = True
                            line_pu.save()


                        
               

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
                            sold = saleList.objects.filter(shift__shift__session=Lses,shift__pump__tank=tnkTo,sale__mobile_pay=False)
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
def saveFuelSaleMobileMoney(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            useri = todo['useri']
            manager = todo['manager']
            cheo = todo['cheo']
            kampuni = todo['kampuni']
            shell = todo['shell']

            if useri.admin or manager:
                custN = request.POST.get('name')
                date = request.POST.get('saDate')
                phone = request.POST.get('phone')
          
                saleDt = json.loads(request.POST.get('sale'))
                payDt = json.loads(request.POST.get('pay'))

                # Save the mobile money payment details
                sale = fuelSales()
                sale.by = cheo
                entry = fuelSales.objects.filter(by__Interprise=shell)
                code = invoCode(entry)
                sale.code = TCode({'code':code,'shell':shell.id})
                sale.Invo_no = int(code)   
                sale.recDate = datetime.datetime.now(tz=timezone.utc)
                sale.date = date
                sale.mobile_pay = 1
                sale.customer_name = custN  
                if phone != '':
                    sale.phone = phone
                sale.save()    
                amo = 0
                for sa in saleDt:
                    saL = saleList()
                    saL.sale = sale
                    theF = None
                    cost = 0
                    pr_og = 0
                    
                    pmp = fuel_pumps.objects.get(pk=sa['pmp'],tank__Interprise=shell)
                    saL.shift = shiftPump.objects.filter(pump=pmp,shift__To=None).exclude(shift=None).order_by('pk').last()
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
                sale.amount = float(amo)
                sale.payed = float(amo)
                sale.save()

                # To save the payment records in wekaCash there are few important things to consider
                # 1.One customer can take two different fuel from different pump attendand but make payment at once
                # 2.The customer may use more than one payment account means with different accounts
                # 3. The payment should be recorded against each pump attendant shift


                
                # Save the payment details
                # Pump attendants ...//
                                # ...existing code...
                # Retrieve distinct shiftPump records for the current shell
                pmpAtt = shiftPump.objects.filter(pump__tank__Interprise=shell, shift__To=None).exclude(shift=None).distinct('shift')
                
                # Iterate through each pump attendant
                for pmpA in pmpAtt:
                    amo = saleList.objects.filter(shift__shift=pmpA.shift.id, shift__pump__tank__Interprise=shell, sale=sale).aggregate(sumi=Sum(F('qty_sold') * F('sa_price')))['sumi'] or 0
                    if amo > 0:

                        for pay in payDt:
                            pay_acc = pay['accId']
                            pay_amount = float(pay['amount'])
                            to_be_paid = pay_amount if pay_amount <= amo else float(amo)
                            acc = PaymentAkaunts.objects.get(pk=pay_acc, Interprise__company=kampuni)
                            accAmo = float(acc.Amount)
                
                            payRec = wekaCash()
                            payRec.Interprise = shell
                            payRec.tarehe = datetime.datetime.now(tz=timezone.utc)
                            payRec.Amount = to_be_paid
                            payRec.maelezo = f'{sale.customer_name} {sale.phone}'
                            payRec.by = useri
                            payRec.sales = sale
                            payRec.biforeShift = True
                            payRec.admin_approval = useri.admin
                            payRec.shift = pmpA.shift
                            payRec.Akaunt = acc
                            payRec.before = accAmo
                            payRec.After = float(accAmo + to_be_paid)
                            acc.Amount = float(float(acc.Amount) + to_be_paid)
                            acc.save()
                
                            payRec.save()



                data = {
                    'success':True,
                    'msg_swa':'Taarifa za mauzo zimehifadhiwa kikamilifu',
                    'msg_eng':'Fuel sales recorded successfully'
                }
                return JsonResponse(data)
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena baadaye',
                'msg_eng':'The action was unsuccessfully please try again later'
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
                cdOrder =   creditDebtOrder.objects.filter(customer=custm.id,by__user__company=kampuni,amount__gt=F('consumed')).order_by('pk')
                lcdorder = None  
                madeni = fuelSales.objects.filter(by__Interprise__company=kampuni,customer=custm.id,amount__gt=F('payed')).annotate(deni=F('amount')-F('payed')).aggregate(sumi=Sum('deni'))['sumi'] or 0

                if  custm.limited_order  and not cdOrder.exists():
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
                lcdorder = cdOrder.first()
                creditBalance = float(lcdorder.paid) - float(lcdorder.consumed) if cdOrder.exists() and lcdorder.paid > lcdorder.consumed else 0
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

                #    Reject if customer debt limit exceeds

                   

                    if float(float(custm.debt_limit)+float(creditBalance)) < float(float(madeni)+float(amo)):
                        sale.delete()
                        data = {
                            'success':False,
                            'msg_swa':'Rekodi ya mauzo haijafanikiwa ukomo wa mkopo umefika mwisho',
                            'msg_eng': 'the customer debt limit has reached its maximum allowed limit'
                        }

                        return JsonResponse(data)
                except:
                    sale.delete()
                    data = {
                        'success':False,
                        'msg_swa':'Rekodi ya mauzo haijafanikiwa tafadhari hakikisha umejaza taarifa zote kikamilifu',        
                         'msg_eng':'Sales record was not successful please make sure you fill all required information correctly'
                    }
                    return JsonResponse(data)
                sale.amount = float(amo)
                
                order_balance = 0
                order_amount = 0
                order_consumed = 0
                order_paid = 0 
                if cdOrder.exists():
                    order_amount = float(lcdorder.amount)
                    order_consumed = float(lcdorder.consumed)
                    order_paid = float(lcdorder.paid)
                    order_balance = float(lcdorder.amount) - float(lcdorder.consumed)
                    
                    if order_amount < float(order_consumed+float(amo)):

                        lcdorder.amount = float(order_consumed + float(amo))
                        lcdorder.save()
                        custm.limited_order = False
                        custm.save()
                        # fuelSales.objects.filter(pk=sale.id).delete()
                        # data = {
                        #     'success':False,
                        #     'msg_swa':'Kiasi cha mafuta kimezidi kiwango cha ukomo kilichowekwa',
                        #     'msg_eng':'the fuel amount exceeds the order limit set for customer'
                        # }

                        # return JsonResponse(data)


                    if order_paid > order_consumed:
                        Od_balance = float(float(order_paid) - float(order_consumed))

                        
                        if Od_balance >= float(amo):
                            sale.payed = float(amo)
                        else:
                            sale.payed =  Od_balance 

                    lcdorder.consumed = float(float(amo)+float(lcdorder.consumed))
                    sale.cdorder = lcdorder
                    lcdorder.save()
                    remBalance = float(float(lcdorder.amount) - float(lcdorder.consumed))
                    largerPr = fuel_tanks.objects.filter(Interprise__company=kampuni).order_by('price').last().price
                    remAmo = remBalance / float(largerPr) 
                    # print({"remqty":remAmo,'largerPr':largerPr,'remBalance':remBalance})
                    if remAmo <= float(0.5) :
                        lcdorder.consumed = float(lcdorder.amount)
                        lcdorder.save()

                
                sale.save()

                

                if cdOrder.exists() and order_paid > order_consumed:
                    ilolipwa = 0
                    daiwa = 0
                    zilizolipwa = wekaCash.objects.filter(cdOrder=lcdorder,used_amount__lt=F('Amount')).order_by('pk')
                    for paye in zilizolipwa:
                        denii = daiwa if daiwa > 0 else sale.payed 
                        paye_balance = float(float(paye.Amount) - float(paye.used_amount))

                        if paye_balance >= float(denii):
                            ilolipwa = float(denii)
                            paye.used_amount = float(float(paye.used_amount) + float(denii))
                            paye.save()
                            break
                        else:
                            ilolipwa = paye_balance  
                            paye.used_amount = float(float(paye.used_amount) + float(paye_balance))
                            paye.save()  
                            daiwa = float(float(denii) - float(ilolipwa))
                         
                        custPay = CustmDebtPayRec()
                        custPay.pay = paye
                        custPay.sale = sale
                        custPay.Debt = ilolipwa
                        custPay.Apay = ilolipwa
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
                    weka.admin_approval = useri.admin
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
                    trFrT.qty = float(float(t['tAmo'])/float(frm_tank.price))
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
        'approval':toApprovalPayments(request)
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
         "page":page,
        'p_num':page_num,
        'pages':pg_number,
        'bil_num':num,
        'approval':toApprovalPayments(request)
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
def customerPayments(request):
     stations = None
     todo =  todoFunct(request)
     useri = todo['useri']
     kampuni = todo['kampuni']
     shell = todo['shell']
     if useri.admin or useri.ceo:
         stations= Interprise.objects.filter(company=kampuni)
     todo.update({
        'stations':stations,
        'approval':toApprovalPayments(request),
        'payment_nav_active':'mobile_payments',
     })

     return render(request,'shiftCustomerPayments.html',todo)

@login_required(login_url='login')
def customerDebtPayments(request):
     stations = None
     todo =  todoFunct(request)
     useri = todo['useri']
     kampuni = todo['kampuni']
     shell = todo['shell']
     if useri.admin or useri.ceo:
         stations= Interprise.objects.filter(company=kampuni)
     todo.update({
        'stations':stations,
        'approval':toApprovalPayments(request),
        'payment_nav_active':'customer_payments',
     }) 

     return render(request,'shiftCustomerDebtPay.html',todo)

@login_required(login_url='login')
def CashDepositBefore(request):
     stations = None
     todo =  todoFunct(request)
     useri = todo['useri']
     kampuni = todo['kampuni']
     shell = todo['shell']
     if useri.admin or useri.ceo:
         stations= Interprise.objects.filter(company=kampuni)
     todo.update({
        'stations':stations,
        'approval':toApprovalPayments(request),
        'payment_nav_active':'deposits_before',
     }) 

     return render(request,'shiftCashDepositBefore.html',todo)

@login_required(login_url='login')
def CashDeposit(request):
     stations = None
     todo =  todoFunct(request)
     useri = todo['useri']
     kampuni = todo['kampuni']
     shell = todo['shell']
     if useri.admin or useri.ceo:
         stations= Interprise.objects.filter(company=kampuni)
     todo.update({
        'stations':stations,
        'approval':toApprovalPayments(request),
        'payment_nav_active':'shift_deposits',
     }) 

     return render(request,'shiftCashDeposit.html',todo)


@login_required(login_url='login')
def shiftExpenses(request):
     stations = None
     todo =  todoFunct(request)
     useri = todo['useri']
     kampuni = todo['kampuni']
     shell = todo['shell']
     if useri.admin or useri.ceo:
         stations= Interprise.objects.filter(company=kampuni)
     todo.update({
        'stations':stations,
        'approval':toApprovalPayments(request),
        'payment_nav_active':'expenses',
     })

     return render(request,'shiftExpenseList.html',todo)


@login_required(login_url='login')
def shiftTransfersActivity(request):
     stations = None
     todo = todoFunct(request)
     useri = todo['useri']
     kampuni = todo['kampuni']
     if useri.admin or useri.ceo:
         stations = Interprise.objects.filter(company=kampuni)
     todo.update({
        'stations':stations,
        'approval':toApprovalPayments(request)
     })

     return render(request,'shiftTransfersActivity.html',todo)


@login_required(login_url='login')
def shiftReceivesActivity(request):
     stations = None
     todo = todoFunct(request)
     useri = todo['useri']
     kampuni = todo['kampuni']
     if useri.admin or useri.ceo:
         stations = Interprise.objects.filter(company=kampuni)
     todo.update({
        'stations':stations,
        'approval':toApprovalPayments(request)
     })

     return render(request,'shiftReceivesActivity.html',todo)


@login_required(login_url='login')
def shiftAdjustmentsActivity(request):
     stations = None
     todo = todoFunct(request)
     useri = todo['useri']
     kampuni = todo['kampuni']
     if useri.admin or useri.ceo:
         stations = Interprise.objects.filter(company=kampuni)
     todo.update({
        'stations':stations,
        'approval':toApprovalPayments(request)
     })

     return render(request,'shiftAdjustmentsActivity.html',todo)


def _parse_shift_session_date_range(tFr, tTo):
    tFr_date = parse_date((tFr or '').split('T')[0])
    tTo_date = parse_date((tTo or '').split('T')[0])
    if not tFr_date or not tTo_date:
        tFr_dt = parse_datetime(tFr or '')
        tTo_dt = parse_datetime(tTo or '')
        tFr_date = tFr_date or (tFr_dt.date() if tFr_dt else None)
        tTo_date = tTo_date or (tTo_dt.date() if tTo_dt else None)
    return tFr_date, tTo_date


def _empty_daily_sales_row(ses_date, st, stN):
    return {
        'date': ses_date.isoformat() if ses_date else '',
        'st': st,
        'stN': stN or '',
        'sales_count': 0,
        'sales_amount': 0.0,
        'flow_sa_amount': 0.0,
        'flow_pmp_amount': 0.0,
        'pump_tot_req': 0.0,
        'pump_tot_paid': 0.0,
        'flow_qty': 0.0,
        'flow_amount': 0.0,
        'credit_sales_count': 0,
        'credit_sales_amount': 0.0,
        'cash_payment_count': 0,
        'cash_payment_amount': 0.0,
        'mobile_count': 0,
        'mobile_amount': 0.0,
        'total_received': 0.0,
        'loss_bonus': 0.0,
        'customer_pay_count': 0,
        'customer_pay_amount': 0.0,
        'dep_before_count': 0,
        'dep_before_amount': 0.0,
        'cash_dep_count': 0,
        'cash_dep_amount': 0.0,
        'expenses_count': 0,
        'expenses_amount': 0.0,
        'transfer_count': 0,
        'transfer_qty': 0.0,
        'transfer_worth': 0.0,
        'receive_count': 0,
        'receive_qty': 0.0,
        'receive_worth': 0.0,
    }


def _finalize_daily_sales_bucket(row):
    row['sales_amount'] = row['flow_sa_amount'] + row['flow_pmp_amount']
    row['loss_bonus'] = row['pump_tot_req'] - row['pump_tot_paid']
    row['total_received'] = row['cash_payment_amount'] + row['mobile_amount']
    return row


def _credit_debt_sale_list_qs(session_ids):
    session_credit = Q(
        sale__session_id__in=session_ids,
        sale__shiftBy__isnull=True,
        sale__mobile_pay=False,
    )
    shift_credit = Q(
        shift__shift__session_id__in=session_ids,
        sale__customer__isnull=False,
        sale__mobile_pay=False,
    )
    return saleList.objects.filter(session_credit | shift_credit)


def _total_shift_sale_list_qs(session_ids):
    return saleList.objects.filter(shift__shift__session_id__in=session_ids)


def _apply_daily_sales_station_filter(qs, st, shell, useri):
    if st:
        return qs.filter(Interprise=st)
    if useri and not useri.admin and not useri.ceo and shell:
        return qs.filter(Interprise=shell.id)
    return qs


def _customer_debt_payments_qs(kampuni, pay_date, st=0, shell=None, useri=None):
    qs = wekaCash.objects.filter(
        Interprise__company=kampuni,
        Amount__gt=0,
    ).filter(
        Q(customer__isnull=False) | Q(cdOrder__isnull=False),
    ).exclude(sales__mobile_pay=True).annotate(
        pay_date=TruncDate('tarehe'),
    ).filter(pay_date=pay_date)
    return _apply_daily_sales_station_filter(qs, st, shell, useri)


def _compute_session_stock_tanks(ss):
    fl_p = shiftPump.objects.filter(shift__session=ss)
    sesadj = adjustments.objects.filter(session=ss)
    rows = []
    if sesadj.exists():
        for t in tankAdjust.objects.filter(adj__session=ss).select_related('tank', 'tank__fuel', 'fuel'):
            tank = t.tank
            if not tank:
                continue
            rcq = _fval(receivedFuel.objects.filter(receive__ses=ss, To=tank).aggregate(v=Sum('qty'))['v'])
            ses_flow = _fval(fl_p.filter(pump__tank=tank).aggregate(v=Sum('qty'))['v'])
            read = _fval(t.read)
            fuel_name = ''
            if t.fuel:
                fuel_name = t.fuel.name or ''
            elif tank.fuel:
                fuel_name = tank.fuel.name or ''
            rows.append({
                'tank_id': tank.id,
                'tank_name': tank.name or '',
                'fuel_name': fuel_name,
                'bses': read + (ses_flow - rcq),
                'ses_flow': ses_flow,
                'a_flow': read - rcq,
                'rcq': rcq,
                'read': read,
                'stick': _fval(t.stick),
                'diff': _fval(t.diff),
            })
        return rows, True

    for t in fl_p.distinct('pump__tank'):
        tank = t.pump.tank if t.pump else None
        if not tank:
            continue
        rcq = _fval(receivedFuel.objects.filter(receive__ses=ss, To=tank).aggregate(v=Sum('qty'))['v'])
        ses_flow = _fval(fl_p.filter(pump__tank=tank).aggregate(v=Sum('qty'))['v'])
        read = _fval(tank.qty)
        rows.append({
            'tank_id': tank.id,
            'tank_name': tank.name or '',
            'fuel_name': tank.fuel.name if tank.fuel else '',
            'bses': read + (ses_flow - rcq),
            'ses_flow': ses_flow,
            'a_flow': read - rcq,
            'rcq': rcq,
            'read': read,
            'stick': 0.0,
            'diff': 0.0,
        })
    return rows, False


def _compute_session_fuel_flow(ss):
    fl_p = shiftPump.objects.filter(shift__session=ss)
    rows = []
    totals = {
        'flow_q': 0.0, 'flow_a': 0.0, 'tr_q': 0.0, 'tr_a': 0.0,
        'sa_q': 0.0, 'sa_a': 0.0, 'exp_q': 0.0, 'exp_a': 0.0,
        'pmp_q': 0.0, 'pmp_a': 0.0,
    }
    for fl in fl_p.distinct('Fuel'):
        if not fl.Fuel_id:
            continue
        fuel_id = fl.Fuel_id
        sale = saleList.objects.filter(
            sale__session=ss,
            sale__shiftBy__isnull=True,
            theFuel=fuel_id,
            sale__mobile_pay=False,
        ).annotate(amount=F('qty_sold') * F('sa_price'))
        tr = transFromTo.objects.filter(shift__shift__session=ss, Fuel_id=fuel_id).annotate(
            worth=F('qty') * F('saprice')
        )
        exp = rekodiMatumizi.objects.filter(fromShift__shift__session=ss, Fuel_id=fuel_id)
        flow_q = _fval(fl_p.filter(Fuel_id=fuel_id).aggregate(v=Sum('qty'))['v'])
        flow_a = _fval(fl_p.filter(Fuel_id=fuel_id).aggregate(v=Sum('amount'))['v'])
        tr_a = _fval(tr.aggregate(v=Sum('worth'))['v'])
        tr_q = _fval(tr.aggregate(v=Sum('qty'))['v'])
        sa_a = _fval(sale.aggregate(v=Sum('amount'))['v'])
        sa_q = _fval(sale.aggregate(v=Sum('qty_sold'))['v'])
        exp_a = _fval(exp.aggregate(v=Sum('kiasi'))['v'])
        exp_q = _fval(exp.aggregate(v=Sum('fuel_qty'))['v'])
        pmp_a = flow_a - (tr_a + sa_a + exp_a)
        pmp_q = flow_q - (tr_q + sa_q + exp_q)
        rows.append({
            'fuel_id': fuel_id,
            'fuel_name': fl.Fuel.name if fl.Fuel else '',
            'price': _fval(fl.price),
            'flow_q': flow_q,
            'flow_a': flow_a,
            'tr_q': tr_q,
            'tr_a': tr_a,
            'sa_q': sa_q,
            'sa_a': sa_a,
            'exp_q': exp_q,
            'exp_a': exp_a,
            'pmp_q': pmp_q,
            'pmp_a': pmp_a,
        })
        totals['flow_q'] += flow_q
        totals['flow_a'] += flow_a
        totals['tr_q'] += tr_q
        totals['tr_a'] += tr_a
        totals['sa_q'] += sa_q
        totals['sa_a'] += sa_a
        totals['exp_q'] += exp_q
        totals['exp_a'] += exp_a
        totals['pmp_q'] += pmp_q
        totals['pmp_a'] += pmp_a
    return rows, totals


def _compute_session_pump_payments(ss):
    totals = {
        'tot_psa': 0.0, 'tot_exp': 0.0, 'tot_cab': 0.0,
        'tot_req': 0.0, 'tot_paid': 0.0, 'tot_lpr': 0.0,
    }
    for s in shifts.objects.filter(session=ss):
        sale = saleList.objects.filter(
            shift__shift=s, sale__shiftBy__isnull=True, sale__mobile_pay=False,
        ).annotate(amount=F('qty_sold') * F('sa_price'))
        tr = transFromTo.objects.filter(shift__shift=s).annotate(worth=F('qty') * F('saprice'))
        exp = rekodiMatumizi.objects.filter(fromShift__shift=s)
        cash_b = wekaCash.objects.filter(shift=s.id, biforeShift=True)
        cash_ba = _fval(cash_b.aggregate(v=Sum('Amount'))['v'])
        tr_amo = _fval(tr.aggregate(v=Sum('worth'))['v'])
        sale_a = _fval(sale.aggregate(v=Sum('amount'))['v'])
        exp_amo = _fval(exp.filter(fuel_cost=0).aggregate(v=Sum('kiasi'))['v'])
        tot_a = _fval(s.amount) + exp_amo + cash_ba
        totals['tot_psa'] += tot_a
        totals['tot_exp'] += exp_amo
        totals['tot_cab'] += cash_ba
        totals['tot_req'] += _fval(s.amount)
        totals['tot_paid'] += _fval(s.paid)
        totals['tot_lpr'] += _fval(s.paid) - _fval(s.amount)
    return totals


def _empty_day_evaluations():
    zero_flow = {
        'flow_q': 0.0, 'flow_a': 0.0, 'tr_q': 0.0, 'tr_a': 0.0,
        'sa_q': 0.0, 'sa_a': 0.0, 'exp_q': 0.0, 'exp_a': 0.0,
        'pmp_q': 0.0, 'pmp_a': 0.0,
    }
    zero_pay = {
        'tot_psa': 0.0, 'tot_exp': 0.0, 'tot_cab': 0.0,
        'tot_req': 0.0, 'tot_paid': 0.0, 'tot_lpr': 0.0,
    }
    return {
        'stock': {'tanks': [], 'has_adj': False, 'all_complete': False},
        'fuel_flow': {'rows': [], 'totals': dict(zero_flow)},
        'pump_payments': dict(zero_pay),
    }


def _build_day_evaluations(session_ids):
    if not session_ids:
        return _empty_day_evaluations()

    sessions = shiftSesion.objects.filter(pk__in=session_ids).order_by('session__shFrom', 'pk')
    tank_merge = {}
    has_adj = False
    all_complete = True
    fuel_merge = {}
    fuel_totals = {
        'flow_q': 0.0, 'flow_a': 0.0, 'tr_q': 0.0, 'tr_a': 0.0,
        'sa_q': 0.0, 'sa_a': 0.0, 'exp_q': 0.0, 'exp_a': 0.0,
        'pmp_q': 0.0, 'pmp_a': 0.0,
    }
    pump_totals = {
        'tot_psa': 0.0, 'tot_exp': 0.0, 'tot_cab': 0.0,
        'tot_req': 0.0, 'tot_paid': 0.0, 'tot_lpr': 0.0,
    }

    for ss in sessions:
        if not ss.complete:
            all_complete = False

        stock_rows, session_has_adj = _compute_session_stock_tanks(ss)
        if session_has_adj:
            has_adj = True
        for row in stock_rows:
            tid = row['tank_id']
            if tid not in tank_merge:
                tank_merge[tid] = dict(row)
            else:
                merged = tank_merge[tid]
                merged['ses_flow'] += row['ses_flow']
                merged['rcq'] += row['rcq']
                merged['a_flow'] = row['a_flow']
                merged['read'] = row['read']
                if session_has_adj:
                    merged['stick'] = row['stick']
                    merged['diff'] = row['diff']

        fuel_rows, session_fuel_totals = _compute_session_fuel_flow(ss)
        for row in fuel_rows:
            fid = row['fuel_id']
            if fid not in fuel_merge:
                fuel_merge[fid] = dict(row)
            else:
                merged = fuel_merge[fid]
                for key in ('flow_q', 'flow_a', 'tr_q', 'tr_a', 'sa_q', 'sa_a', 'exp_q', 'exp_a', 'pmp_q', 'pmp_a'):
                    merged[key] += row[key]
        for key in fuel_totals:
            fuel_totals[key] += session_fuel_totals[key]

        session_pump = _compute_session_pump_payments(ss)
        for key in pump_totals:
            pump_totals[key] += session_pump[key]

    return {
        'stock': {
            'tanks': sorted(tank_merge.values(), key=lambda r: (r.get('tank_name') or '', r.get('fuel_name') or '')),
            'has_adj': has_adj,
            'all_complete': all_complete,
        },
        'fuel_flow': {
            'rows': sorted(fuel_merge.values(), key=lambda r: r.get('fuel_name') or ''),
            'totals': fuel_totals,
        },
        'pump_payments': pump_totals,
    }


def _daily_sales_bucket_key(ses_date, st):
    return (ses_date.isoformat() if ses_date else '', int(st or 0))


def _merge_daily_sales_bucket(buckets, ses_date, st, stN, updates):
    key = _daily_sales_bucket_key(ses_date, st)
    if key not in buckets:
        buckets[key] = _empty_daily_sales_row(ses_date, st, stN)
    for field, val in updates.items():
        buckets[key][field] += val


def _build_daily_sales_days(kampuni, shell, useri, tFr_date, tTo_date, tFr, tTo):
    buckets = {}

    session_rows = shiftSesion.objects.filter(
        session__Interprise__company=kampuni,
        date__gte=tFr_date,
        date__lte=tTo_date,
    ).values('date', st_id=F('session__Interprise'), stN=F('session__Interprise__name')).distinct()
    if not useri.admin and not useri.ceo:
        session_rows = session_rows.filter(session__Interprise=shell.id)
    for row in session_rows:
        _merge_daily_sales_bucket(buckets, row['date'], row['st_id'], row['stN'], {})

    eval_sessions = shiftSesion.objects.filter(
        session__Interprise__company=kampuni,
        date__gte=tFr_date,
        date__lte=tTo_date,
    ).select_related('session', 'session__Interprise')
    if not useri.admin and not useri.ceo:
        eval_sessions = eval_sessions.filter(session__Interprise=shell.id)
    for ss in eval_sessions:
        _, fuel_totals = _compute_session_fuel_flow(ss)
        pump_totals = _compute_session_pump_payments(ss)
        st_id = ss.session.Interprise_id if ss.session else 0
        st_name = ss.session.Interprise.name if ss.session and ss.session.Interprise else ''
        _merge_daily_sales_bucket(buckets, ss.date, st_id, st_name, {
            'flow_qty': fuel_totals['flow_q'],
            'flow_amount': fuel_totals['flow_a'],
            'flow_sa_amount': fuel_totals['sa_a'],
            'flow_pmp_amount': fuel_totals['pmp_a'],
            'pump_tot_req': pump_totals['tot_req'],
            'pump_tot_paid': pump_totals['tot_paid'],
        })

    credit_rows = _credit_debt_sale_list_qs(
        shiftSesion.objects.filter(
            session__Interprise__company=kampuni,
            date__gte=tFr_date,
            date__lte=tTo_date,
        ).values_list('pk', flat=True)
    ).annotate(
        sesDate=Coalesce(F('shift__shift__session__date'), F('sale__session__date')),
        st=Coalesce(F('shift__shift__session__session__Interprise'), F('sale__by__Interprise')),
        stN=Coalesce(F('shift__shift__session__session__Interprise__name'), F('sale__by__Interprise__name')),
        line_amount=F('qty_sold') * F('sa_price'),
    )
    if not useri.admin and not useri.ceo:
        credit_rows = credit_rows.filter(
            Q(shift__shift__session__session__Interprise=shell.id) |
            Q(sale__by__Interprise=shell.id)
        )
    for row in credit_rows.values('sesDate', 'st', 'stN').annotate(
        cnt=Count('sale_id', distinct=True),
        total=Sum('line_amount'),
    ):
        if not row['sesDate']:
            continue
        _merge_daily_sales_bucket(buckets, row['sesDate'], row['st'], row['stN'], {
            'credit_sales_count': row['cnt'],
            'credit_sales_amount': float(row['total'] or 0),
        })

    cash_pay_rows = shifts.objects.filter(
        session__session__Interprise__company=kampuni,
        session__date__gte=tFr_date,
        session__date__lte=tTo_date,
    ).annotate(
        sesDate=F('session__date'),
        st=F('session__session__Interprise'),
        stN=F('session__session__Interprise__name'),
    )
    if not useri.admin and not useri.ceo:
        cash_pay_rows = cash_pay_rows.filter(session__session__Interprise=shell.id)
    for row in cash_pay_rows.values('sesDate', 'st', 'stN').annotate(cnt=Count('id'), total=Sum('paid')):
        _merge_daily_sales_bucket(buckets, row['sesDate'], row['st'], row['stN'], {
            'cash_payment_count': row['cnt'],
            'cash_payment_amount': float(row['total'] or 0),
        })

    mobile_rows = wekaCash.objects.filter(
        Interprise__company=kampuni,
        Amount__gt=0,
        sales__mobile_pay=True,
        shift__session__date__gte=tFr_date,
        shift__session__date__lte=tTo_date,
    ).annotate(
        sesDate=F('shift__session__date'),
        st=F('Interprise'),
        stN=F('Interprise__name'),
    )
    if not useri.admin and not useri.ceo:
        mobile_rows = mobile_rows.filter(Interprise=shell.id)
    for row in mobile_rows.values('sesDate', 'st', 'stN').annotate(cnt=Count('id'), total=Sum('Amount')):
        _merge_daily_sales_bucket(buckets, row['sesDate'], row['st'], row['stN'], {
            'mobile_count': row['cnt'],
            'mobile_amount': float(row['total'] or 0),
        })

    cust_rows = wekaCash.objects.filter(
        Interprise__company=kampuni,
        Amount__gt=0,
        tarehe__range=[tFr, tTo],
    ).filter(
        Q(customer__isnull=False) | Q(cdOrder__isnull=False),
    ).exclude(sales__mobile_pay=True).annotate(
        sesDate=TruncDate('tarehe'),
        st=F('Interprise'),
        stN=F('Interprise__name'),
    )
    if not useri.admin and not useri.ceo:
        cust_rows = cust_rows.filter(Interprise=shell.id)
    for row in cust_rows.values('sesDate', 'st', 'stN').annotate(cnt=Count('id'), total=Sum('Amount')):
        if not row['sesDate']:
            continue
        _merge_daily_sales_bucket(buckets, row['sesDate'], row['st'], row['stN'], {
            'customer_pay_count': row['cnt'],
            'customer_pay_amount': float(row['total'] or 0),
        })

    dep_before_rows = wekaCash.objects.filter(
        Interprise__company=kampuni,
        Amount__gt=0,
        biforeShift=True,
        sales__mobile_pay__isnull=True,
        shift__session__date__gte=tFr_date,
        shift__session__date__lte=tTo_date,
    ).annotate(
        sesDate=F('shift__session__date'),
        st=F('Interprise'),
        stN=F('Interprise__name'),
    )
    if not useri.admin and not useri.ceo:
        dep_before_rows = dep_before_rows.filter(Interprise=shell.id)
    for row in dep_before_rows.values('sesDate', 'st', 'stN').annotate(cnt=Count('id'), total=Sum('Amount')):
        _merge_daily_sales_bucket(buckets, row['sesDate'], row['st'], row['stN'], {
            'dep_before_count': row['cnt'],
            'dep_before_amount': float(row['total'] or 0),
        })

    cash_dep_rows = toaCash.objects.filter(
        kuhamisha=True,
        Akaunt__supv_acc=False,
        Interprise__company=kampuni,
        Amount__gt=0,
        tarehe__range=[tFr, tTo],
    ).annotate(
        sesDate=TruncDate('tarehe'),
        st=F('Interprise'),
        stN=F('Interprise__name'),
    )
    if not useri.admin and not useri.ceo:
        cash_dep_rows = cash_dep_rows.filter(Interprise=shell.id)
    for row in cash_dep_rows.values('sesDate', 'st', 'stN').annotate(cnt=Count('id'), total=Sum('Amount')):
        if not row['sesDate']:
            continue
        _merge_daily_sales_bucket(buckets, row['sesDate'], row['st'], row['stN'], {
            'cash_dep_count': row['cnt'],
            'cash_dep_amount': float(row['total'] or 0),
        })

    expense_rows = rekodiMatumizi.objects.filter(
        Interprise__company=kampuni,
    ).filter(
        Q(fromShift__shift__session__date__gte=tFr_date, fromShift__shift__session__date__lte=tTo_date) |
        Q(fromShift__isnull=True, tarehe__gte=tFr, tarehe__lte=tTo)
    ).annotate(
        sesDate=Coalesce(F('fromShift__shift__session__date'), TruncDate('tarehe'), output_field=DateField()),
        st=F('Interprise'),
        stN=F('Interprise__name'),
    )
    if not useri.admin and not useri.ceo:
        expense_rows = expense_rows.filter(Interprise=shell.id)
    for row in expense_rows.values('sesDate', 'st', 'stN').annotate(cnt=Count('id'), total=Sum('kiasi')):
        if not row['sesDate']:
            continue
        _merge_daily_sales_bucket(buckets, row['sesDate'], row['st'], row['stN'], {
            'expenses_count': row['cnt'],
            'expenses_amount': float(row['total'] or 0),
        })

    transfer_rows = transFromTo.objects.filter(
        transfer__record_by__Interprise__company=kampuni,
    ).filter(
        Q(shift__shift__session__date__gte=tFr_date, shift__shift__session__date__lte=tTo_date) |
        Q(shift__isnull=True, transfer__date__gte=tFr, transfer__date__lte=tTo)
    ).annotate(
        sesDate=Coalesce(F('shift__shift__session__date'), TruncDate('transfer__date'), output_field=DateField()),
        st=F('transfer__record_by__Interprise'),
        stN=F('transfer__record_by__Interprise__name'),
        worth=F('qty') * F('cost'),
    )
    if not useri.admin and not useri.ceo:
        transfer_rows = transfer_rows.filter(transfer__record_by__Interprise=shell.id)
    for row in transfer_rows.values('sesDate', 'st', 'stN').annotate(
        cnt=Count('id'),
        qty_total=Sum('qty'),
        worth_total=Sum('worth'),
    ):
        if not row['sesDate']:
            continue
        _merge_daily_sales_bucket(buckets, row['sesDate'], row['st'], row['stN'], {
            'transfer_count': row['cnt'],
            'transfer_qty': float(row['qty_total'] or 0),
            'transfer_worth': float(row['worth_total'] or 0),
        })

    receive_rows = receivedFuel.objects.filter(
        receive__by__Interprise__company=kampuni,
    ).filter(
        Q(receive__ses__date__gte=tFr_date, receive__ses__date__lte=tTo_date) |
        Q(receive__ses__isnull=True, receive__date__gte=tFr, receive__date__lte=tTo)
    ).annotate(
        sesDate=Coalesce(F('receive__ses__date'), TruncDate('receive__date'), output_field=DateField()),
        st=F('receive__by__Interprise'),
        stN=F('receive__by__Interprise__name'),
        worth=F('qty') * F('price'),
    )
    if not useri.admin and not useri.ceo:
        receive_rows = receive_rows.filter(receive__by__Interprise=shell.id)
    for row in receive_rows.values('sesDate', 'st', 'stN').annotate(
        cnt=Count('id'),
        qty_total=Sum('qty'),
        worth_total=Sum('worth'),
    ):
        if not row['sesDate']:
            continue
        _merge_daily_sales_bucket(buckets, row['sesDate'], row['st'], row['stN'], {
            'receive_count': row['cnt'],
            'receive_qty': float(row['qty_total'] or 0),
            'receive_worth': float(row['worth_total'] or 0),
        })

    days = [_finalize_daily_sales_bucket(row) for row in buckets.values()]
    days.sort(key=lambda d: (d['date'], d['stN']), reverse=True)
    return days


@login_required(login_url='login')
def dailySalesActivity(request):
    stations = None
    todo = todoFunct(request)
    useri = todo['useri']
    kampuni = todo['kampuni']
    if useri.admin or useri.ceo:
        stations = Interprise.objects.filter(company=kampuni)
    todo.update({
        'stations': stations,
        'approval': toApprovalPayments(request),
    })
    return render(request, 'shiftDailySalesActivity.html', todo)


@login_required(login_url='login')
def getDailySalesActivity(request):
    if request.method == 'POST':
        try:
            todo = todoFunct(request)
            shell = todo['shell']
            kampuni = todo['kampuni']
            useri = todo['useri']
            tFr = request.POST.get('tFr')
            tTo = request.POST.get('tTo')

            tFr_date, tTo_date = _parse_shift_session_date_range(tFr, tTo)
            if not tFr_date or not tTo_date:
                return JsonResponse({
                    'success': False,
                    'swa': 'Muda uliowekwa si sahihi',
                    'eng': 'Invalid date range',
                })

            days = _build_daily_sales_days(kampuni, shell, useri, tFr_date, tTo_date, tFr, tTo)
            return JsonResponse({
                'success': True,
                'days': days,
            })
        except Exception as err:
            print(err)
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'swa': 'Haikufanikiwa',
                'eng': 'Bad Request',
            })
    return JsonResponse({
        'success': False,
        'swa': 'Haikufanikiwa',
        'eng': 'Bad Request',
    })


def _person_name(fname, lname):
    return f'{fname or ""} {lname or ""}'.strip().title()


def _fval(val):
    return float(val or 0)


def _serialize_shift_transactions(shift_obj):
    sales = list(saleList.objects.filter(
        shift__shift=shift_obj,
        sale__shiftBy__isnull=True,
        sale__mobile_pay=False,
    ).annotate(
        amount=F('qty_sold') * F('sa_price'),
        sale_code=F('sale__code'),
        cust_name=F('sale__customer__jina'),
        fuel_name=F('theFuel__name'),
    ).values('sale_id', 'sale_code', 'cust_name', 'fuel_name', 'qty_sold', 'amount'))

    transfers = list(transFromTo.objects.filter(shift__shift=shift_obj).annotate(
        worth=F('qty') * F('saprice'),
        fuel_name=F('Fuel__name'),
        from_tank=F('From__tank__name'),
        to_tank=F('to__name'),
        transfer_code=F('transfer__code'),
    ).values('id', 'transfer_id', 'transfer_code', 'fuel_name', 'from_tank', 'to_tank', 'qty', 'worth'))

    expenses = list(rekodiMatumizi.objects.filter(fromShift__shift=shift_obj).annotate(
        exp_name=F('matumizi__matumizi'),
    ).values('id', 'exp_name', 'kiasi', 'fuel_qty', 'tarehe'))

    cash_before = list(wekaCash.objects.filter(shift=shift_obj.id, biforeShift=True,sales__mobile_pay=False).annotate(
        account_name=F('Akaunt__Akaunt_name'),
    ).values('id', 'Amount', 'account_name', 'tarehe', 'maelezo'))

    mobile_pays = list(wekaCash.objects.filter(
        shift=shift_obj.id,
        sales__mobile_pay=True,
        Amount__gt=0,
    ).annotate(
        account_name=F('Akaunt__Akaunt_name'),
        cust_name=F('customer__jina'),
        cust_label=F('sales__customer_name'),
    ).values('id', 'Amount', 'account_name', 'cust_name', 'cust_label', 'tarehe'))

    customer_pays = list(wekaCash.objects.filter(
        shift=shift_obj.id,
        customer__isnull=False,
        Amount__gt=0,
    ).exclude(sales__mobile_pay=True).annotate(
        account_name=F('Akaunt__Akaunt_name'),
        cust_name=F('customer__jina'),
    ).values('id', 'Amount', 'account_name', 'cust_name', 'tarehe'))

    for row in sales:
        row['qty_sold'] = _fval(row.get('qty_sold'))
        row['amount'] = _fval(row.get('amount'))
    for row in transfers:
        row['qty'] = _fval(row.get('qty'))
        row['worth'] = _fval(row.get('worth'))
    for row in expenses:
        row['kiasi'] = _fval(row.get('kiasi'))
        row['fuel_qty'] = _fval(row.get('fuel_qty'))
    for row in cash_before + mobile_pays + customer_pays:
        row['Amount'] = _fval(row.get('Amount'))

    return {
        'sales': sales,
        'transfers': transfers,
        'expenses': expenses,
        'cash_before': cash_before,
        'mobile_pays': mobile_pays,
        'customer_pays': customer_pays,
    }


def _serialize_shift_pumps(shift_obj):
    pmps = shiftPump.objects.filter(shift=shift_obj.id).annotate(
        fuel_name=F('Fuel__name'),
        fuel_id=F('Fuel_id'),
        pump_name=F('pump__name'),
        station_name=F('pump__station__name'),
    ).values('fuel_id', 'fuel_name', 'pump_name', 'station_name', 'initial', 'final', 'price', 'qty', 'amount', 'analog_used')

    fuels_map = {}
    for p in pmps:
        fid = p['fuel_id']
        if fid not in fuels_map:
            fuels_map[fid] = {
                'fuel_name': p['fuel_name'] or '',
                'pumps': [],
                'total_qty': 0.0,
                'total_amount': 0.0,
            }
        fuels_map[fid]['pumps'].append({
            'station_name': p['station_name'] or '',
            'pump_name': p['pump_name'] or '',
            'initial': _fval(p['initial']),
            'final': _fval(p['final']),
            'price': _fval(p['price']),
            'qty': _fval(p['qty']),
            'amount': _fval(p['amount']),
            'analog_used': bool(p.get('analog_used')),
        })
        fuels_map[fid]['total_qty'] += _fval(p['qty'])
        fuels_map[fid]['total_amount'] += _fval(p['amount'])
        if p.get('analog_used'):
            fuels_map[fid]['analog_used'] = True

    result = list(fuels_map.values())
    for fuel in result:
        fuel.setdefault('analog_used', False)
    return result


def _compute_shift_summary(shift_obj):
    pmps = shiftPump.objects.filter(shift=shift_obj.id)
    sale_qs = saleList.objects.filter(
        shift__shift=shift_obj,
        sale__shiftBy__isnull=True,
        sale__mobile_pay=False,
    ).annotate(
        amount=F('qty_sold') * F('sa_price')
    )
    tr_qs = transFromTo.objects.filter(shift__shift=shift_obj).annotate(worth=F('qty') * F('saprice'))
    exp_qs = rekodiMatumizi.objects.filter(fromShift__shift=shift_obj)
    cash_b = wekaCash.objects.filter(shift=shift_obj.id, biforeShift=True)

    sale_a = _fval(sale_qs.aggregate(v=Sum('amount'))['v'])
    sale_q = _fval(sale_qs.aggregate(v=Sum('qty_sold'))['v'])
    tr_a = _fval(tr_qs.aggregate(v=Sum('worth'))['v'])
    tr_q = _fval(tr_qs.aggregate(v=Sum('qty'))['v'])
    exp_f_a = _fval(exp_qs.filter(fuel_cost__gt=0).aggregate(v=Sum('kiasi'))['v'])
    exp_f_q = _fval(exp_qs.aggregate(v=Sum('fuel_qty'))['v'])
    exp_a = _fval(exp_qs.filter(fuel_cost=0).aggregate(v=Sum('kiasi'))['v'])
    cash_b_a = _fval(cash_b.aggregate(v=Sum('Amount'))['v'])
    tot_q = _fval(pmps.aggregate(v=Sum('qty'))['v'])
    tot_a = _fval(shift_obj.amount) + exp_a + cash_b_a
    toex_q = sale_q + tr_q + exp_f_q
    toex_a = sale_a + tr_a + exp_f_a + exp_a + cash_b_a
    loss_prof = _fval(shift_obj.paid) - _fval(shift_obj.amount)

    return {
        'flow_qty': tot_q,
        'flow_amount': _fval(shift_obj.amount) + toex_a,
        'sale_qty': sale_q,
        'sale_amount': sale_a,
        'transfer_qty': tr_q,
        'transfer_amount': tr_a,
        'expense_fuel_qty': exp_f_q,
        'expense_fuel_amount': exp_f_a,
        'expense_cash': exp_a,
        'cash_before': cash_b_a,
        'pump_sale_qty': tot_q - toex_q,
        'pump_sale_amount': tot_a,
        'required': _fval(shift_obj.amount),
        'paid': _fval(shift_obj.paid),
        'loss_profit': abs(loss_prof),
        'is_loss': _fval(shift_obj.amount) > _fval(shift_obj.paid),
        'is_bonus': _fval(shift_obj.amount) < _fval(shift_obj.paid),
    }


def _serialize_shift_detail(shift_obj):
    attendant = shift_obj.by
    manager = shift_obj.record_by.user if shift_obj.record_by else None
    txs = _serialize_shift_transactions(shift_obj)

    return {
        'id': shift_obj.id,
        'code': shift_obj.code or '',
        'from_dt': shift_obj.From.isoformat() if shift_obj.From else None,
        'to_dt': shift_obj.To.isoformat() if shift_obj.To else None,
        'amount': _fval(shift_obj.amount),
        'paid': _fval(shift_obj.paid),
        'attendant': _person_name(
            attendant.user.first_name if attendant else '',
            attendant.user.last_name if attendant else '',
        ),
        'manager': _person_name(
            manager.user.first_name if manager else '',
            manager.user.last_name if manager else '',
        ),
        'fuels': _serialize_shift_pumps(shift_obj),
        'summary': _compute_shift_summary(shift_obj),
        **txs,
    }


def _serialize_shift_attachments_map(shift_ids, request=None):
    shift_ids = [sid for sid in set(shift_ids) if sid]
    if not shift_ids:
        return {}
    img_ext = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
    qs = attachments.objects.filter(
        shift_id__in=shift_ids,
    ).exclude(file='').select_related('by__user').order_by('date', 'pk')
    by_shift = {}
    for att in qs:
        sid = att.shift_id
        if sid not in by_shift:
            by_shift[sid] = []
        ext = os.path.splitext(att.file.name)[1].lower() if att.file else ''
        file_url = None
        if att.file:
            file_url = request.build_absolute_uri(att.file.url) if request else att.file.url
        by_user = att.by
        by_shift[sid].append({
            'id': att.id,
            'url': file_url,
            'name': att.attach_name or '',
            'date': att.date.isoformat() if att.date else None,
            'printed_doc': bool(att.printedDocu),
            'is_image': ext in img_ext,
            'by': _person_name(
                by_user.user.first_name if by_user else '',
                by_user.user.last_name if by_user else '',
            ),
        })
    return by_shift


def _serialize_shift_light(shift_obj, attachments=None):
    attendant = shift_obj.by
    manager_ue = shift_obj.record_by.user if shift_obj.record_by else None
    fuels = _serialize_shift_pumps(shift_obj)
    return {
        'id': shift_obj.id,
        'code': shift_obj.code or '',
        'from_dt': shift_obj.From.isoformat() if shift_obj.From else None,
        'to_dt': shift_obj.To.isoformat() if shift_obj.To else None,
        'amount': _fval(shift_obj.amount),
        'paid': _fval(shift_obj.paid),
        'analog_used': any(f.get('analog_used') for f in fuels) or shiftPump.objects.filter(shift=shift_obj, analog_used=True).exists(),
        'attendant': _person_name(
            attendant.user.first_name if attendant else '',
            attendant.user.last_name if attendant else '',
        ),
        'manager': _person_name(
            manager_ue.user.first_name if manager_ue else '',
            manager_ue.user.last_name if manager_ue else '',
        ),
        'fuels': fuels,
        'attachments': attachments or [],
        'summary': _compute_shift_summary(shift_obj),
    }


def _serialize_session_shifts_only(ss, attach_map=None):
    sh_from = ss.session.shFrom.strftime('%H:%M') if ss.session and ss.session.shFrom else ''
    sh_to = ss.session.shTo.strftime('%H:%M') if ss.session and ss.session.shTo else ''
    shift_list = shifts.objects.filter(session=ss).select_related(
        'by__user', 'record_by__user__user'
    ).order_by('From', 'pk')
    return {
        'id': ss.id,
        'session_name': ss.session.name if ss.session else '',
        'time_from': sh_from,
        'time_to': sh_to,
        'complete': bool(ss.complete),
        'shifts': [
            _serialize_shift_light(s, (attach_map or {}).get(s.id, []))
            for s in shift_list
        ],
    }


def _attach_session_label(rows, session_name):
    for row in rows:
        row['session_name'] = session_name
    return rows


def _build_day_activity_tables(session_ids, kampuni, day_start, day_end, st=0, shell=None, useri=None, day_date=None):
    empty = {
        'sales': [], 'customer_pays': [], 'mobile_pays': [], 'cash_deposits': [],
        'transfers': [], 'receives': [], 'expenses': [],
    }
    session_ids = session_ids or []
    pay_date = day_date or day_start.date()

    customer_pays = list(_customer_debt_payments_qs(
        kampuni, pay_date, st, shell, useri,
    ).annotate(
        account_name=F('Akaunt__Akaunt_name'),
        cust_name=Coalesce(F('customer__jina'), F('cdOrder__customer__jina')),
        order_code=F('cdOrder__code'),
        session_name=F('shift__session__session__name'),
        shift_code=F('shift__code'),
        attendant_fname=F('shift__by__user__first_name'),
        attendant_lname=F('shift__by__user__last_name'),
        by_fname=F('by__user__first_name'),
        by_lname=F('by__user__last_name'),
    ).values(
        'id', 'Amount', 'account_name', 'cust_name', 'order_code', 'tarehe',
        'session_name', 'shift_id', 'shift_code',
        'attendant_fname', 'attendant_lname', 'by_fname', 'by_lname', 'maelezo',
    ).order_by('-tarehe', '-pk'))

    cash_bank_q = toaCash.objects.filter(
        kuhamisha=True,
        Akaunt__aina='Cash',
        Interprise__company=kampuni,
        Amount__gt=0,
    ).annotate(dep_date=TruncDate('tarehe')).filter(dep_date=pay_date)
    cash_bank_q = _apply_daily_sales_station_filter(cash_bank_q, st, shell, useri)

    cash_bank = list(cash_bank_q.annotate(
        account_name=F('Akaunt__Akaunt_name'),
        stN=F('Interprise__name'),
        by_fname=F('by__user__first_name'),
        by_lname=F('by__user__last_name'),
    ).values('id', 'Amount', 'account_name', 'stN', 'tarehe', 'maelezo', 'by_fname', 'by_lname'))

    if not session_ids:
        for row in customer_pays:
            row['Amount'] = _fval(row.get('Amount'))
            tarehe = row.pop('tarehe', None)
            row['tarehe'] = tarehe.isoformat() if tarehe else None
            row['attendant'] = _person_name(row.pop('attendant_fname', ''), row.pop('attendant_lname', ''))
            if not row['attendant']:
                row['attendant'] = _person_name(row.pop('by_fname', ''), row.pop('by_lname', ''))
            else:
                row.pop('by_fname', None)
                row.pop('by_lname', None)
        for row in cash_bank:
            row['Amount'] = _fval(row.get('Amount'))
            row['by'] = _person_name(row.pop('by_fname', ''), row.pop('by_lname', ''))
            row['deposit_type'] = 'bank'
            row['session_name'] = '—'
        cash_deposits = list(cash_bank)
        summary = {
            'sales_count': 0,
            'sales_amount': 0.0,
            'sales_qty': 0.0,
            'credit_sales_count': 0,
            'credit_sales_amount': 0.0,
            'credit_sales_qty': 0.0,
            'cash_payment_count': 0,
            'cash_payment_amount': 0.0,
            'customer_pay_count': len(customer_pays),
            'customer_pay_amount': sum(r['Amount'] for r in customer_pays),
            'mobile_count': 0,
            'mobile_amount': 0.0,
            'total_received': 0.0,
            'loss_bonus': 0.0,
            'cash_dep_count': len(cash_deposits),
            'cash_dep_amount': sum(r['Amount'] for r in cash_deposits),
            'transfer_count': 0,
            'transfer_qty': 0.0,
            'transfer_worth': 0.0,
            'receive_count': 0,
            'receive_qty': 0.0,
            'receive_worth': 0.0,
            'expense_count': 0,
            'expense_amount': 0.0,
            'expense_fuel_qty': 0.0,
            'shift_count': 0,
            'session_count': 0,
        }
        return {
            **empty,
            'customer_pays': customer_pays,
            'cash_deposits': cash_deposits,
        }, summary

    credit_sales = list(_credit_debt_sale_list_qs(session_ids).annotate(
        amount=F('qty_sold') * F('sa_price'),
        sale_code=F('sale__code'),
        cust_name=Coalesce(F('sale__customer__jina'), F('sale__cdorder__customer__jina')),
        fuel_name=F('theFuel__name'),
        session_name=Coalesce(
            F('shift__shift__session__session__name'),
            F('sale__session__session__name'),
        ),
        sale_dt=Coalesce(F('sale__date'), F('sale__recDate')),
        linked_shift_id=F('shift__shift_id'),
        shift_code=F('shift__shift__code'),
        attendant_fname=F('shift__shift__by__user__first_name'),
        attendant_lname=F('shift__shift__by__user__last_name'),
    ).values(
        'sale_id', 'sale_code', 'cust_name', 'fuel_name', 'sa_price',
        'qty_sold', 'amount', 'session_name', 'sale_dt', 'linked_shift_id', 'shift_code',
        'attendant_fname', 'attendant_lname',
    ).order_by('-sale_dt', '-pk'))

    total_sales_qs = _total_shift_sale_list_qs(session_ids).annotate(
        line_amount=F('qty_sold') * F('sa_price'),
    )

    mobile_pays = list(wekaCash.objects.filter(
        shift__session_id__in=session_ids,
        sales__mobile_pay=True,
        Amount__gt=0,
    ).annotate(
        account_name=F('Akaunt__Akaunt_name'),
        cust_name=F('customer__jina'),
        cust_label=F('sales__customer_name'),
        session_name=F('shift__session__session__name'),
        attendant_fname=F('shift__by__user__first_name'),
        attendant_lname=F('shift__by__user__last_name'),
    ).values('id', 'Amount', 'account_name', 'cust_name', 'cust_label', 'tarehe', 'session_name', 'attendant_fname', 'attendant_lname'))

    cash_before = list(wekaCash.objects.filter(
        shift__session_id__in=session_ids,
        biforeShift=True,
        Amount__gt=0,
        sales__mobile_pay=False,
    ).annotate(
        account_name=F('Akaunt__Akaunt_name'),
        session_name=F('shift__session__session__name'),
        attendant_fname=F('shift__by__user__first_name'),
        attendant_lname=F('shift__by__user__last_name'),
    ).values('id', 'Amount', 'account_name', 'tarehe', 'maelezo', 'session_name', 'attendant_fname', 'attendant_lname'))

    transfers = list(transFromTo.objects.filter(
        shift__shift__session_id__in=session_ids,
    ).annotate(
        worth=F('qty') * F('saprice'),
        fuel_name=F('Fuel__name'),
        from_tank=F('From__tank__name'),
        to_tank=F('to__name'),
        transfer_code=F('transfer__code'),
        session_name=F('shift__shift__session__session__name'),
        attendant_fname=F('shift__shift__by__user__first_name'),
        attendant_lname=F('shift__shift__by__user__last_name'),
    ).values('id', 'transfer_id', 'transfer_code', 'fuel_name', 'from_tank', 'to_tank', 'qty', 'worth', 'session_name', 'attendant_fname', 'attendant_lname'))

    receives = list(receivedFuel.objects.filter(
        receive__ses_id__in=session_ids,
    ).annotate(
        receive_code=F('receive__code'),
        fuel_name=F('Fuel__name'),
        to_tank=F('To__name'),
        worth=F('qty') * F('price'),
        session_name=F('receive__ses__session__name'),
    ).values('id', 'receive_id', 'receive_code', 'fuel_name', 'to_tank', 'qty', 'worth', 'session_name'))

    expenses = list(rekodiMatumizi.objects.filter(
        fromShift__shift__session_id__in=session_ids,
    ).annotate(
        exp_name=F('matumizi__matumizi'),
        exp_paye=F('matumizi__paye'),
        attendant_fname=F('fromShift__shift__by__user__first_name'),
        attendant_lname=F('fromShift__shift__by__user__last_name'),
        staff_fname=F('staff__user__first_name'),
        staff_lname=F('staff__user__last_name'),
        record_fname=F('by__user__first_name'),
        record_lname=F('by__user__last_name'),
    ).values(
        'id', 'exp_name', 'exp_paye', 'salary_advance', 'kiasi', 'fuel_qty', 'tarehe', 'kabidhiwa',
        'attendant_fname', 'attendant_lname', 'staff_fname', 'staff_lname',
        'record_fname', 'record_lname',
    ))

    for row in credit_sales:
        row['qty_sold'] = _fval(row.get('qty_sold'))
        row['amount'] = _fval(row.get('amount'))
        row['sa_price'] = _fval(row.get('sa_price'))
        sale_dt = row.pop('sale_dt', None)
        row['sale_dt'] = sale_dt.isoformat() if sale_dt else None
        row['attendant'] = _person_name(row.pop('attendant_fname', ''), row.pop('attendant_lname', ''))
    for row in customer_pays:
        row['Amount'] = _fval(row.get('Amount'))
        tarehe = row.pop('tarehe', None)
        row['tarehe'] = tarehe.isoformat() if tarehe else None
        row['attendant'] = _person_name(row.pop('attendant_fname', ''), row.pop('attendant_lname', ''))
        if not row['attendant']:
            row['attendant'] = _person_name(row.pop('by_fname', ''), row.pop('by_lname', ''))
        else:
            row.pop('by_fname', None)
            row.pop('by_lname', None)
    for rows in (mobile_pays, cash_before, transfers, receives, expenses):
        for row in rows:
            for k in ('Amount', 'qty', 'worth', 'kiasi', 'fuel_qty'):
                if k in row:
                    row[k] = _fval(row.get(k))
            if 'attendant_fname' in row:
                row['attendant'] = _person_name(row.pop('attendant_fname', ''), row.pop('attendant_lname', ''))
    for row in expenses:
        given_to = (row.pop('kabidhiwa', '') or '').strip()
        if not given_to:
            given_to = _person_name(row.pop('staff_fname', ''), row.pop('staff_lname', ''))
        else:
            row.pop('staff_fname', None)
            row.pop('staff_lname', None)
        row['given_to'] = given_to
        row['recorded_by'] = _person_name(row.pop('record_fname', ''), row.pop('record_lname', ''))
    for row in cash_before:
        if 'attendant_fname' in row:
            row['attendant'] = _person_name(row.pop('attendant_fname', ''), row.pop('attendant_lname', ''))
    for row in cash_bank:
        row['Amount'] = _fval(row.get('Amount'))
        row['by'] = _person_name(row.pop('by_fname', ''), row.pop('by_lname', ''))
        row['deposit_type'] = 'bank'
        row['session_name'] = '—'

    cash_deposits = []
    for row in cash_before:
        cash_deposits.append({
            **row,
            'deposit_type': 'before_shift',
            'by': row.get('attendant', ''),
        })
    for row in cash_bank:
        cash_deposits.append(row)

    all_sales = credit_sales
    total_sales_amount = _fval(total_sales_qs.aggregate(v=Sum('line_amount'))['v'])
    total_sales_count = total_sales_qs.values('sale_id').distinct().count()
    credit_sales_amount = sum(r['amount'] for r in all_sales)
    credit_sales_count = _credit_debt_sale_list_qs(session_ids).values('sale_id').distinct().count()
    cash_payment_amount = _fval(shifts.objects.filter(session_id__in=session_ids).aggregate(v=Sum('paid'))['v'])
    mobile_amount = sum(r['Amount'] for r in mobile_pays)
    total_received = cash_payment_amount + mobile_amount
    loss_bonus = total_sales_amount - total_received
    tables = {
        'sales': all_sales,
        'customer_pays': customer_pays,
        'mobile_pays': mobile_pays,
        'cash_deposits': cash_deposits,
        'transfers': transfers,
        'receives': receives,
        'expenses': expenses,
    }
    summary = {
        'sales_count': total_sales_count,
        'sales_amount': total_sales_amount,
        'sales_qty': _fval(total_sales_qs.aggregate(v=Sum('qty_sold'))['v']),
        'credit_sales_count': credit_sales_count,
        'credit_sales_amount': credit_sales_amount,
        'credit_sales_qty': sum(r['qty_sold'] for r in all_sales),
        'cash_payment_count': shifts.objects.filter(session_id__in=session_ids).count(),
        'cash_payment_amount': cash_payment_amount,
        'customer_pay_count': len(customer_pays),
        'customer_pay_amount': sum(r['Amount'] for r in customer_pays),
        'mobile_count': len(mobile_pays),
        'mobile_amount': mobile_amount,
        'total_received': total_received,
        'loss_bonus': loss_bonus,
        'cash_dep_count': len(cash_deposits),
        'cash_dep_amount': sum(r['Amount'] for r in cash_deposits),
        'transfer_count': len(transfers),
        'transfer_qty': sum(r['qty'] for r in transfers),
        'transfer_worth': sum(r['worth'] for r in transfers),
        'receive_count': len(receives),
        'receive_qty': sum(r['qty'] for r in receives),
        'receive_worth': sum(r['worth'] for r in receives),
        'expense_count': len(expenses),
        'expense_amount': sum(r['kiasi'] for r in expenses),
        'expense_fuel_qty': sum(r['fuel_qty'] for r in expenses),
        'shift_count': shifts.objects.filter(session_id__in=session_ids).count(),
        'session_count': len(session_ids),
    }
    return tables, summary


def _serialize_session_detail(ss):
    fl_p = shiftPump.objects.filter(shift__session=ss)
    shift_list = shifts.objects.filter(session=ss).select_related('by__user', 'record_by__user').order_by('From', 'pk')
    shift_details = [_serialize_shift_detail(s) for s in shift_list]

    session_sales = list(saleList.objects.filter(
        sale__session=ss,
        sale__shiftBy__isnull=True,
        sale__mobile_pay=False,
    ).annotate(
        amount=F('qty_sold') * F('sa_price'),
        sale_code=F('sale__code'),
        cust_name=F('sale__customer__jina'),
        fuel_name=F('theFuel__name'),
    ).values('sale_id', 'sale_code', 'cust_name', 'fuel_name', 'qty_sold', 'amount'))

    session_receives = list(receivedFuel.objects.filter(receive__ses=ss).annotate(
        receive_code=F('receive__code'),
        fuel_name=F('Fuel__name'),
        to_tank=F('To__name'),
        worth=F('qty') * F('price'),
    ).values('id', 'receive_id', 'receive_code', 'fuel_name', 'to_tank', 'qty', 'worth'))

    session_transfers = list(transFromTo.objects.filter(
        shift__shift__session=ss,
    ).annotate(
        worth=F('qty') * F('saprice'),
        fuel_name=F('Fuel__name'),
        from_tank=F('From__tank__name'),
        to_tank=F('to__name'),
        transfer_code=F('transfer__code'),
        attendant_fname=F('shift__shift__by__user__first_name'),
        attendant_lname=F('shift__shift__by__user__last_name'),
    ).values('id', 'transfer_code', 'fuel_name', 'from_tank', 'to_tank', 'qty', 'worth', 'attendant_fname', 'attendant_lname'))

    session_expenses = list(rekodiMatumizi.objects.filter(fromShift__shift__session=ss).annotate(
        exp_name=F('matumizi__matumizi'),
        attendant_fname=F('fromShift__shift__by__user__first_name'),
        attendant_lname=F('fromShift__shift__by__user__last_name'),
    ).values('id', 'exp_name', 'kiasi', 'fuel_qty', 'tarehe', 'attendant_fname', 'attendant_lname'))

    session_mobile = list(wekaCash.objects.filter(
        shift__session=ss,
        sales__mobile_pay=True,
        Amount__gt=0,
    ).annotate(
        account_name=F('Akaunt__Akaunt_name'),
        cust_name=F('customer__jina'),
        cust_label=F('sales__customer_name'),
        attendant_fname=F('shift__by__user__first_name'),
        attendant_lname=F('shift__by__user__last_name'),
    ).values('id', 'Amount', 'account_name', 'cust_name', 'cust_label', 'tarehe', 'attendant_fname', 'attendant_lname'))

    session_customer = list(wekaCash.objects.filter(
        shift__session=ss,
        customer__isnull=False,
        Amount__gt=0,
    ).exclude(sales__mobile_pay=True).annotate(
        account_name=F('Akaunt__Akaunt_name'),
        cust_name=F('customer__jina'),
        attendant_fname=F('shift__by__user__first_name'),
        attendant_lname=F('shift__by__user__last_name'),
    ).values('id', 'Amount', 'account_name', 'cust_name', 'tarehe', 'attendant_fname', 'attendant_lname'))

    session_cash_before = list(wekaCash.objects.filter(
        shift__session=ss,
        biforeShift=True,
        Amount__gt=0,
    ).annotate(
        account_name=F('Akaunt__Akaunt_name'),
        attendant_fname=F('shift__by__user__first_name'),
        attendant_lname=F('shift__by__user__last_name'),
    ).values('id', 'Amount', 'account_name', 'tarehe', 'maelezo', 'attendant_fname', 'attendant_lname'))

    for rows in (session_sales, session_receives, session_transfers, session_expenses, session_mobile, session_customer, session_cash_before):
        for row in rows:
            for k, v in list(row.items()):
                if k in ('qty_sold', 'amount', 'qty', 'worth', 'kiasi', 'fuel_qty', 'Amount'):
                    row[k] = _fval(v)
            if 'attendant_fname' in row:
                row['attendant'] = _person_name(row.pop('attendant_fname', ''), row.pop('attendant_lname', ''))

    fuel_ids = set(fl_p.values_list('Fuel_id', flat=True))
    fuel_ev = []
    t_flow_q = t_flow_a = t_tr_q = t_tr_a = t_sa_q = t_sa_a = t_exp_q = t_exp_a = t_pmp_q = t_pmp_a = 0.0

    for fuel_id in fuel_ids:
        if not fuel_id:
            continue
        fuel_name = fuel.objects.filter(pk=fuel_id).values_list('name', flat=True).first() or ''
        sale = saleList.objects.filter(sale__session=ss, sale__shiftBy__isnull=True, sale__mobile_pay=False, theFuel=fuel_id).annotate(
            amount=F('qty_sold') * F('sa_price')
        )
        tr = transFromTo.objects.filter(shift__shift__session=ss, shift__Fuel=fuel_id).annotate(worth=F('qty') * F('saprice'))
        exp = rekodiMatumizi.objects.filter(fromShift__shift__session=ss, Fuel=fuel_id)
        flow_q = _fval(fl_p.filter(Fuel=fuel_id).aggregate(v=Sum('qty'))['v'])
        flow_a = _fval(fl_p.filter(Fuel=fuel_id).aggregate(v=Sum('amount'))['v'])
        tr_a = _fval(tr.aggregate(v=Sum('worth'))['v'])
        tr_q = _fval(tr.aggregate(v=Sum('qty'))['v'])
        sa_a = _fval(sale.aggregate(v=Sum('amount'))['v'])
        sa_q = _fval(sale.aggregate(v=Sum('qty_sold'))['v'])
        exp_a = _fval(exp.aggregate(v=Sum('kiasi'))['v'])
        exp_q = _fval(exp.aggregate(v=Sum('fuel_qty'))['v'])
        pmp_a = flow_a - (tr_a + sa_a + exp_a)
        pmp_q = flow_q - (tr_q + sa_q + exp_q)
        price = _fval(fl_p.filter(Fuel=fuel_id).values_list('price', flat=True).first())
        fuel_ev.append({
            'fuel_name': fuel_name,
            'price': price,
            'flow_qty': flow_q,
            'flow_amount': flow_a,
            'transfer_qty': tr_q,
            'transfer_amount': tr_a,
            'expense_qty': exp_q,
            'expense_amount': exp_a,
            'sale_qty': sa_q,
            'sale_amount': sa_a,
            'pump_qty': pmp_q,
            'pump_amount': pmp_a,
        })
        t_flow_q += flow_q
        t_flow_a += flow_a
        t_tr_q += tr_q
        t_tr_a += tr_a
        t_sa_q += sa_q
        t_sa_a += sa_a
        t_exp_q += exp_q
        t_exp_a += exp_a
        t_pmp_q += pmp_q
        t_pmp_a += pmp_a

    tot_psa = sum(s['summary']['pump_sale_amount'] for s in shift_details)
    tot_exp = sum(s['summary']['expense_cash'] for s in shift_details)
    tot_cab = sum(s['summary']['cash_before'] for s in shift_details)
    tot_req = sum(s['summary']['required'] for s in shift_details)
    tot_paid = sum(s['summary']['paid'] for s in shift_details)

    sh_from = ss.session.shFrom.strftime('%H:%M') if ss.session and ss.session.shFrom else ''
    sh_to = ss.session.shTo.strftime('%H:%M') if ss.session and ss.session.shTo else ''

    return {
        'id': ss.id,
        'session_name': ss.session.name if ss.session else '',
        'time_from': sh_from,
        'time_to': sh_to,
        'complete': bool(ss.complete),
        'shifts': shift_details,
        'session_sales': session_sales,
        'session_receives': session_receives,
        'session_transfers': session_transfers,
        'session_expenses': session_expenses,
        'session_mobile': session_mobile,
        'session_customer': session_customer,
        'session_cash_before': session_cash_before,
        'fuel_ev': fuel_ev,
        'fuel_ev_total': {
            'flow_qty': t_flow_q,
            'flow_amount': t_flow_a,
            'transfer_qty': t_tr_q,
            'transfer_amount': t_tr_a,
            'expense_qty': t_exp_q,
            'expense_amount': t_exp_a,
            'sale_qty': t_sa_q,
            'sale_amount': t_sa_a,
            'pump_qty': t_pmp_q,
            'pump_amount': t_pmp_a,
        },
        'session_pay_total': {
            'pump_sales': tot_psa,
            'expenses': tot_exp,
            'cash_before': tot_cab,
            'required': tot_req,
            'paid': tot_paid,
            'bonus_loss': tot_paid - tot_req,
        },
    }


@login_required(login_url='login')
def getDailySalesDayDetail(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'swa': 'Haikufanikiwa', 'eng': 'Bad Request'})

    try:
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        shell = todo['shell']
        useri = todo['useri']
        day_date = parse_date((request.POST.get('date') or '').split('T')[0])
        st = int(request.POST.get('st') or 0)

        if not day_date:
            return JsonResponse({'success': False, 'swa': 'Tarehe si sahihi', 'eng': 'Invalid date'})

        sessions_qs = shiftSesion.objects.filter(
            date=day_date,
            session__Interprise__company=kampuni,
        ).select_related('session', 'session__Interprise').order_by('session__shFrom', 'pk')

        if st:
            sessions_qs = sessions_qs.filter(session__Interprise=st)
        elif not useri.admin and not useri.ceo:
            sessions_qs = sessions_qs.filter(session__Interprise=shell.id)

        shift_ids = list(
            shifts.objects.filter(session_id__in=sessions_qs.values_list('pk', flat=True))
            .values_list('pk', flat=True)
        )
        attach_map = _serialize_shift_attachments_map(shift_ids, request)
        sessions = [_serialize_session_shifts_only(ss, attach_map) for ss in sessions_qs]
        session_ids = list(sessions_qs.values_list('pk', flat=True))

        stN = ''
        if st:
            stN = Interprise.objects.filter(pk=st).values_list('name', flat=True).first() or ''
        elif sessions_qs.exists():
            stN = sessions_qs.first().session.Interprise.name if sessions_qs.first().session else ''

        day_start = datetime.datetime.combine(day_date, datetime.time.min)
        day_end = datetime.datetime.combine(day_date, datetime.time.max)
        from django.utils import timezone as dj_timezone
        day_start = dj_timezone.make_aware(day_start)
        day_end = dj_timezone.make_aware(day_end)

        tables, summary = _build_day_activity_tables(
            session_ids, kampuni, day_start, day_end, st, shell, useri, day_date=day_date,
        )
        evaluations = _build_day_evaluations(session_ids)

        return JsonResponse({
            'success': True,
            'date': day_date.isoformat(),
            'st': st,
            'stN': stN,
            'sessions': sessions,
            'tables': tables,
            'summary': summary,
            'evaluations': evaluations,
        })
    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({'success': False, 'swa': 'Haikufanikiwa', 'eng': 'Bad Request'})


 

@login_required(login_url='login')
def getShiftCustomerMobilePayments(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            shell = todo['shell']
            kampuni = todo['kampuni']
            tFr = request.POST.get('tFr')
            tTo = request.POST.get('tTo')
            mob = int(request.POST.get('mob',0))
            debt_pay = int(request.POST.get('debt_pay',0))
            CdepoB = int(request.POST.get('CdepoB',0))
            cashD = int(request.POST.get('cashD',0))
            from_session = int(request.POST.get('from_session',0))
            pay_ids = json.loads(request.POST.get('pay_ids','[]'))
            useri = todo['useri']
            # print(tFr,tTo)
            payments = wekaCash.objects.filter(Interprise__company=kampuni,Amount__gt=0).annotate(
                stN=F('Interprise__name'),
                st=F('Interprise'),
                account_name = F('Akaunt__Akaunt_name'),
                custN = F('customer__jina'),
                BFname = F('by__user__first_name'),
                BLname = F('by__user__last_name'),
                attFname = F('shift__by__user__first_name'),
                attLname = F('shift__by__user__last_name')
            ).order_by('-pk')

            if from_session:
                payments = payments.filter(pk__in=pay_ids)
            else:
                payments = payments.filter(tarehe__range=[tFr,tTo])

            if mob:
                payments = payments.filter(sales__mobile_pay=True)

            if debt_pay:
                payments = payments.filter(customer__isnull=False)    
                
            if CdepoB:
                payments = payments.filter(biforeShift=True,sales__mobile_pay__isnull=True)    

            if cashD:
                payments = toaCash.objects.filter(kuhamisha=True,Akaunt__supv_acc=False,Interprise__company=kampuni,Amount__gt=0).annotate(
                stN=F('Interprise__name'),
                st=F('Interprise'),
                account_name = F('Akaunt__Akaunt_name'),
                
                BFname = F('by__user__first_name'),
                BLname = F('by__user__last_name'),
                supFname = F('depoTo__supv__user__first_name'),
                supLname = F('depoTo__supv__user__last_name'),
                To_acc = F('depoTo__weka__Akaunt__Akaunt_name')

                
            ).order_by('-pk')

                if from_session:
                    payments = payments.filter(pk__in=pay_ids)
                else:
                    payments = payments.filter(tarehe__range=[tFr,tTo])

                # payments = payments.filter(kuhamisha=True,sales__mobile_pay__isnull=True)    


            if not useri.admin and not useri.ceo:
                payments = payments.filter(Interprise=shell.id)

            
            data = {
                'success':True,
                'payments':list(payments.values()),
                'isadmin':useri.admin 
            }
            return JsonResponse(data)

        except Exception as err:
            print(err)
            traceback.print_exc() 
            data = {
                'success':False,
                'swa':'Haikufanikiwa',
                'eng':'Bad Request'
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
def getShiftExpenses(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            shell = todo['shell']
            kampuni = todo['kampuni']
            tFr = request.POST.get('tFr')
            tTo = request.POST.get('tTo')
            from_session = int(request.POST.get('from_session',0))

            exp_ids = request.POST.getlist('exp_Ids[]')
            if not exp_ids:
                exp_ids = json.loads(request.POST.get('exp_Ids','[]'))

            useri = todo['useri']

            expenses = rekodiMatumizi.objects.filter(Interprise__company=kampuni).annotate(
                stN=F('Interprise__name'),
                st=F('Interprise'),
                account_name=F('akaunti__Akaunt_name'),
                BFname=F('by__user__first_name'),
                BLname=F('by__user__last_name'),
                expN=F('matumizi__matumizi'),
                staffFname=F('staff__user__first_name'),
                staffLname=F('staff__user__last_name'),
                fuel_name=F('Fuel__name'),
                pump_attendant_fname=F('fromShift__shift__by__user__first_name'),
                paye = F('matumizi__paye'),
                pump_attendant_lname=F('fromShift__shift__by__user__last_name'),
                payment_source=Case(
                    When(fromShift__isnull=False, then=Value('pump_attendant')),
                    When(akaunti__isnull=False, then=Value('payment_account')),
                    default=Value('unknown'),
                    output_field=CharField()
                )
            ).order_by('-pk')

            if from_session and exp_ids:
                expense_ids = [int(eid) for eid in exp_ids if str(eid).isdigit()]
                expenses = expenses.filter(pk__in=expense_ids)
            else:
                expenses = expenses.filter(tarehe__range=[tFr,tTo])

            if not useri.admin and not useri.ceo:
                expenses = expenses.filter(Interprise=shell.id)

            data = {
                'success':True,
                'expenses':list(expenses.values()),
                'isadmin':useri.admin
            }
            return JsonResponse(data)

        except Exception as err:
            print(err)
            traceback.print_exc()
            data = {
                'success':False,
                'swa':'Haikufanikiwa',
                'eng':'Bad Request'
            }
            return JsonResponse(data)
    else:
        data = {
            'success':False,
            'swa':'Haikufanikiwa',
            'eng':'Bad Request'
        }
        return JsonResponse(data)


def _shift_attachment_allowed(att, todo):
    kampuni = todo['kampuni']
    shell = todo['shell']
    useri = todo['useri']
    parent_q = None

    if att.transfer_id:
        parent_q = TransferFuel.objects.filter(pk=att.transfer_id, record_by__Interprise__company=kampuni)
        if not useri.admin and not useri.ceo:
            parent_q = parent_q.filter(record_by__Interprise=shell.id)
    elif att.receive_id:
        parent_q = ReceveFuel.objects.filter(pk=att.receive_id, by__Interprise__company=kampuni)
        if not useri.admin and not useri.ceo:
            parent_q = parent_q.filter(by__Interprise=shell.id)
    elif att.adj_id:
        parent_q = adjustments.objects.filter(pk=att.adj_id, Interprise__company=kampuni)
        if not useri.admin and not useri.ceo:
            parent_q = parent_q.filter(Interprise=shell.id)
    else:
        return False

    return parent_q.exists()


@login_required(login_url='login')
@xframe_options_sameorigin
def embedShiftAttachment(request):
    att_id = request.GET.get('i')
    if not att_id:
        raise Http404

    try:
        att = attachments.objects.get(pk=att_id)
    except attachments.DoesNotExist:
        raise Http404

    if not att.file:
        raise Http404

    todo = todoFunct(request)
    if not _shift_attachment_allowed(att, todo):
        raise Http404

    content_type, _ = mimetypes.guess_type(att.file.name)
    if not content_type:
        content_type = 'application/octet-stream'

    filename = os.path.basename(att.file.name)
    response = FileResponse(att.file.open('rb'), content_type=content_type)
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


def _shift_flow_attachments(request, parent_ids, link_field):
    parent_ids = [pid for pid in set(parent_ids) if pid]
    if not parent_ids:
        return []
    filt = {f'{link_field}_id__in': parent_ids}
    qs = attachments.objects.filter(**filt).exclude(file='').order_by('date', 'pk')
    result = []
    for att in qs:
        parent_id = getattr(att, f'{link_field}_id', None)
        result.append({
            'parent_id': parent_id,
            'id': att.id,
            'file': request.build_absolute_uri(att.file.url) if att.file else None,
            'embed_url': request.build_absolute_uri(f'/salepurchase/embedShiftAttachment?i={att.id}'),
            'attach_name': att.attach_name or '',
            'date': att.date.isoformat() if att.date else None,
            'printedDocu': bool(att.printedDocu),
        })
    return result


@login_required(login_url='login')
def getShiftTransfers(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            shell = todo['shell']
            kampuni = todo['kampuni']
            tFr = request.POST.get('tFr')
            tTo = request.POST.get('tTo')
            from_session = int(request.POST.get('from_session',0))

            tr_ids = request.POST.getlist('item_ids[]')
            if not tr_ids:
                tr_ids = json.loads(request.POST.get('item_ids','[]'))

            useri = todo['useri']

            transfers = transFromTo.objects.filter(
                transfer__record_by__Interprise__company=kampuni
            ).annotate(
                tarehe=F('transfer__date'),
                stN=F('transfer__record_by__Interprise__name'),
                st=F('transfer__record_by__Interprise'),
                transfer_code=F('transfer__code'),
                fuel_name=F('Fuel__name'),
                from_tank=F('From__tank__name'),
                to_tank=F('to__name'),
                by_fname=F('transfer__record_by__user__user__first_name'),
                by_lname=F('transfer__record_by__user__user__last_name'),
                worth=F('qty')*F('cost')
            ).order_by('-pk')

            if from_session and tr_ids:
                transfer_ids = [int(tid) for tid in tr_ids if str(tid).isdigit()]
                transfers = transfers.filter(pk__in=transfer_ids)
            else:
                transfers = transfers.filter(transfer__date__range=[tFr,tTo])

            if not useri.admin and not useri.ceo:
                transfers = transfers.filter(transfer__record_by__Interprise=shell.id)

            rec_values = list(transfers.values())
            transfer_ids = [r.get('transfer_id') for r in rec_values if r.get('transfer_id')]

            data = {
                'success':True,
                'records':rec_values,
                'attachments': _shift_flow_attachments(request, transfer_ids, 'transfer'),
                'isadmin':useri.admin
            }
            return JsonResponse(data)

        except Exception as err:
            print(err)
            traceback.print_exc()
            data = {
                'success':False,
                'swa':'Haikufanikiwa',
                'eng':'Bad Request'
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
def getShiftReceives(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            shell = todo['shell']
            kampuni = todo['kampuni']
            tFr = request.POST.get('tFr')
            tTo = request.POST.get('tTo')
            from_session = int(request.POST.get('from_session',0))

            rc_ids = request.POST.getlist('item_ids[]')
            if not rc_ids:
                rc_ids = json.loads(request.POST.get('item_ids','[]'))

            useri = todo['useri']

            receives = receivedFuel.objects.filter(
                receive__by__Interprise__company=kampuni
            ).annotate(
                tarehe=F('receive__date'),
                stN=F('receive__by__Interprise__name'),
                st=F('receive__by__Interprise'),
                receive_code=F('receive__code'),
                fuel_name=F('Fuel__name'),
                from_tank=F('From__tank__name'),
                to_tank=F('To__name'),
                by_fname=F('receive__by__user__user__first_name'),
                by_lname=F('receive__by__user__user__last_name'),
                worth=F('qty')*F('price'),
                from_purchase_id=F('receive__FromPurchase'),
                from_purchase_code=F('receive__FromPurchase__code'),
                from_transf_id=F('receive__FromTransf'),
                from_transf_code=F('receive__FromTransf__code')
            ).order_by('-pk')

            if from_session and rc_ids:
                receive_ids = [int(rid) for rid in rc_ids if str(rid).isdigit()]
                receives = receives.filter(pk__in=receive_ids)
            else:
                receives = receives.filter(receive__date__range=[tFr,tTo])

            if not useri.admin and not useri.ceo:
                receives = receives.filter(receive__by__Interprise=shell.id)

            rec_values = list(receives.values())
            rec_ids = [r['id'] for r in rec_values]
            sold_map = {
                x['receive_id']: x['qty_sum'] for x in saleOnReceive.objects.filter(receive_id__in=rec_ids)
                .values('receive_id').annotate(qty_sum=Sum('qty'))
            }

            for r in rec_values:
                r['sold_on_receive'] = sold_map.get(r['id'], 0)

            receive_ids = [r.get('receive_id') for r in rec_values if r.get('receive_id')]

            data = {
                'success':True,
                'records':rec_values,
                'attachments': _shift_flow_attachments(request, receive_ids, 'receive'),
                'isadmin':useri.admin
            }
            return JsonResponse(data)

        except Exception as err:
            print(err)
            traceback.print_exc()
            data = {
                'success':False,
                'swa':'Haikufanikiwa',
                'eng':'Bad Request'
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
@require_POST
def approveFuelActivity(request):
    try:
        item_ids = json.loads(request.POST.get('item_ids','[]'))
        activity = request.POST.get('activity','')  # 'transfer', 'receive', 'adjustment'
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        useri = todo['useri']

        if not useri.admin:
            return JsonResponse({'success':False,'swa':'Huna ruhusa hii','eng':'Permission denied'})

        if not item_ids or not activity:
            return JsonResponse({'success':False,'swa':'Data haikutolewa','eng':'Missing data'})

        ids = [int(i) for i in item_ids if str(i).isdigit()]
        if not ids:
            return JsonResponse({'success':False,'swa':'Vitambulisho sivyo sahihi','eng':'Invalid IDs'})

        if activity == 'transfer':
            updated = transFromTo.objects.filter(pk__in=ids,transfer__record_by__Interprise__company=kampuni).update(adminAproval=True)
        elif activity == 'receive':
            updated = receivedFuel.objects.filter(pk__in=ids,receive__by__Interprise__company=kampuni).update(adminAproval=True)
        elif activity == 'adjustment':
            updated = tankAdjust.objects.filter(pk__in=ids,adj__Interprise__company=kampuni).update(adminAproval=True)
        else:
            return JsonResponse({'success':False,'swa':'Aina si sahihi','eng':'Invalid activity type'})

        return JsonResponse({
            'success':True,
            'updated':updated,
            'swa':'Imehakikiwa kwa mafanikio',
            'eng':'Approved successfully'
        })
    except Exception as err:
        traceback.print_exc()
        return JsonResponse({'success':False,'swa':'Hitilafu','eng':str(err)})


def _recalc_session_receive_costs(ses, tank):
    soldBreceive = saleOnReceive.objects.filter(ses=ses, tank=tank)
    if not soldBreceive.exists():
        return
    BsoldCost = float(soldBreceive.aggregate(sumi=Sum(F('qty') * F('cost')))['sumi'] or 0)
    BsoldQty = float(soldBreceive.aggregate(sumi=Sum('qty'))['sumi'] or 0)
    shiftSale = saleList.objects.filter(
        sale__session=ses,
        shift__pump__tank=tank,
        shift__shift__session=ses,
        sale__mobile_pay=False
    )
    SoldQty = float(shiftSale.aggregate(sumi=Sum('qty_sold'))['sumi'] or 0)
    soldAfterRc = float(SoldQty - BsoldQty)
    Soldcost = soldAfterRc * float(tank.cost)
    TotCost = float(BsoldCost) + float(Soldcost)
    if SoldQty > 0:
        avgCost = TotCost / SoldQty
        shiftSale.update(cost_sold=float(avgCost))


def _reverse_received_fuel_line(rcf):
    """Reverse stock and movement effects of a single receivedFuel line."""
    rcv = rcf.receive
    if rcv is None:
        return

    trqty = float(rcf.qty or 0)
    trFuel = rcf.Fuel
    tnkTo = rcf.To
    qtyB = float(rcf.qtyB or 0)
    qtyA = float(rcf.qtyA or 0)
    fcost = float(rcf.cost or 0)

    if trqty <= 0 or tnkTo is None:
        return

    if rcv.Fromcont_id:
        if rcf.From_id and rcf.From.tank_id:
            tnkFrom = fuel_tanks.objects.select_for_update().get(pk=rcf.From.tank_id)
            tnkFrom.qty = float(tnkFrom.qty or 0) + trqty
            tnkFrom.save(update_fields=['qty'])

    elif rcv.FromTransf_id:
        cont_From = rcv.FromTransf
        trRec = transFromTo.objects.filter(
            Fuel=trFuel, transfer=cont_From, taken__gt=0
        ).order_by('-pk')
        remaining = trqty
        for t in trRec:
            if remaining <= 0:
                break
            cur_taken = float(t.taken or 0)
            reduce_by = min(cur_taken, remaining)
            t.taken = cur_taken - reduce_by
            t.save(update_fields=['taken'])
            remaining -= reduce_by

    elif rcv.FromPurchase_id:
        cont_From = rcv.FromPurchase
        pu_lines = PuList.objects.filter(
            pu=cont_From, Fuel=trFuel, rcvd__gt=0
        ).order_by('-rcvd')
        remaining = trqty
        for pl in pu_lines:
            if remaining <= 0:
                break
            cur_rcvd = float(pl.rcvd or 0)
            reduce_by = min(cur_rcvd, remaining)
            pl.rcvd = cur_rcvd - reduce_by
            pl.save(update_fields=['rcvd'])
            remaining -= reduce_by
        if cont_From.closed:
            cont_From.closed = False
            cont_From.save(update_fields=['closed'])

    tnkTo = fuel_tanks.objects.select_for_update().get(pk=tnkTo.pk)
    ses = rcv.ses

    if tnkTo.moving or ses is None:
        if qtyB > 0:
            current_cost = float(tnkTo.cost or 0)
            old_cost = (qtyA * current_cost - trqty * fcost) / qtyB
            tnkTo.qty = qtyB
            tnkTo.cost = old_cost
        else:
            tnkTo.qty = qtyB
        tnkTo.save(update_fields=['qty', 'cost'])

        tank_adj_qs = tankAdjust.objects.filter(
            adj__receive=rcv, tank=tnkTo, fuel=trFuel, stick=rcf.qtyB
        )
        adj_ids = list(tank_adj_qs.values_list('adj_id', flat=True).distinct())
        tank_adj_qs.delete()
        for adj_id in adj_ids:
            if adj_id and not tankAdjust.objects.filter(adj_id=adj_id).exists():
                adjustments.objects.filter(pk=adj_id).delete()

    elif ses.complete:
        tnkTo.qty = float(tnkTo.qty or 0) - trqty
        tnkTo.save(update_fields=['qty'])
        saleOnReceive.objects.filter(receive=rcf).delete()
        _recalc_session_receive_costs(ses, tnkTo)
    else:
        saleOnReceive.objects.filter(receive=rcf).delete()


def _cleanup_receive_header(rcv):
    if receivedFuel.objects.filter(receive=rcv).exists():
        return
    attachments.objects.filter(receive=rcv.id).delete()
    adj_qs = adjustments.objects.filter(receive=rcv)
    for adj in adj_qs:
        tankAdjust.objects.filter(adj=adj).delete()
    adj_qs.delete()
    rcv.delete()


@login_required(login_url='login')
@require_POST
def deleteFuelReceive(request):
    try:
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        shell = todo['shell']
        manager = todo['manager']
        useri = todo['useri']

        if not (useri.admin or manager):
            return JsonResponse({
                'success': False,
                'swa': 'Huna ruhusa ya kufuta receive',
                'eng': 'Permission denied'
            })

        item_ids = request.POST.getlist('item_ids[]')
        if not item_ids:
            item_ids = json.loads(request.POST.get('item_ids', '[]'))

        ids = [int(i) for i in item_ids if str(i).isdigit()]
        if not ids:
            return JsonResponse({
                'success': False,
                'swa': 'Hakuna rekodi zilizochaguliwa',
                'eng': 'No records selected'
            })

        rcf_qs = receivedFuel.objects.filter(
            pk__in=ids,
            receive__by__Interprise__company=kampuni,
            adminAproval=False
        )

        if not useri.admin and not useri.ceo:
            rcf_qs = rcf_qs.filter(receive__by__Interprise=shell.id)

        with transaction.atomic():
            rcf_ids = list(rcf_qs.values_list('id', flat=True))
            if not rcf_ids:
                return JsonResponse({
                    'success': False,
                    'swa': 'Hakuna rekodi zisizohakikiwa zilizopatikana',
                    'eng': 'No unapproved receive records found'
                })

            if len(rcf_ids) != len(ids):
                return JsonResponse({
                    'success': False,
                    'swa': 'Baadhi ya rekodi haziwezi kufutwa (zimehakikiwa au hazipo)',
                    'eng': 'Some records cannot be deleted (approved or not found)'
                })

            # Lock receivedFuel rows only — avoid select_related with select_for_update (PostgreSQL outer join issue)
            list(receivedFuel.objects.filter(pk__in=rcf_ids).select_for_update())

            rcf_list = list(
                receivedFuel.objects.filter(pk__in=rcf_ids).select_related(
                    'receive', 'To', 'From', 'From__tank', 'Fuel',
                    'receive__FromPurchase', 'receive__FromTransf', 'receive__ses'
                )
            )

            receive_ids = set()
            for rcf in rcf_list:
                receive_ids.add(rcf.receive_id)
                _reverse_received_fuel_line(rcf)
                rcf.delete()

            for rcv_id in receive_ids:
                rcv = ReceveFuel.objects.filter(pk=rcv_id).first()
                if rcv:
                    _cleanup_receive_header(rcv)

        return JsonResponse({
            'success': True,
            'deleted': len(rcf_list),
            'swa': 'Receive imefutwa na stock imerejeshwa',
            'eng': 'Receive deleted and stock restored'
        })
    except Exception as err:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'swa': 'Hitilafu wakati wa kufuta receive',
            'eng': str(err)
        })


@login_required(login_url='login')
def getShiftAdjustments(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            shell = todo['shell']
            kampuni = todo['kampuni']
            tFr = request.POST.get('tFr')
            tTo = request.POST.get('tTo')
            from_session = int(request.POST.get('from_session',0))

            adj_ids = request.POST.getlist('item_ids[]')
            if not adj_ids:
                adj_ids = json.loads(request.POST.get('item_ids','[]'))

            useri = todo['useri']

            adj_rows = tankAdjust.objects.filter(
                adj__Interprise__company=kampuni
            ).annotate(
                tarehe=F('adj__tarehe'),
                stN=F('adj__Interprise__name'),
                st=F('adj__Interprise'),
                adj_code=F('adj__code'),
                fuel_name=F('fuel__name'),
                tank_name=F('tank__name'),
                by_fname=F('adj__by__user__user__first_name'),
                by_lname=F('adj__by__user__user__last_name'),
                worth=F('diff')*F('price')
            ).order_by('-pk')

            if from_session and adj_ids:
                adjustment_ids = [int(aid) for aid in adj_ids if str(aid).isdigit()]
                adj_rows = adj_rows.filter(pk__in=adjustment_ids)
            else:
                adj_rows = adj_rows.filter(adj__tarehe__range=[tFr,tTo])

            if not useri.admin and not useri.ceo:
                adj_rows = adj_rows.filter(adj__Interprise=shell.id)

            adj_values = list(adj_rows.values())
            adj_parent_ids = [r.get('adj_id') for r in adj_values if r.get('adj_id')]

            data = {
                'success':True,
                'records':adj_values,
                'attachments': _shift_flow_attachments(request, adj_parent_ids, 'adj'),
                'isadmin':useri.admin
            }
            return JsonResponse(data)

        except Exception as err:
            print(err)
            traceback.print_exc()
            data = {
                'success':False,
                'swa':'Haikufanikiwa',
                'eng':'Bad Request'
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
        'isShiftTime':True,
        'approval':toApprovalPayments(request)
    })

    return render(request,'shiftsTime.html',todo)


@login_required(login_url='login')
@require_POST
def deleteShiftExpenses(request):
    try:
        todo = todoFunct(request)
        shell = todo['shell']
        kampuni = todo['kampuni']
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
        
        # Allow deletion of:
        # 1. Payment account expenses (akaunti__isnull=False) with admin_approval=False
        # 2. Pump attendant expenses (fromShift__isnull=False) regardless of approval status
        expenses_queryset = rekodiMatumizi.objects.filter(
            pk__in=expense_ids,
            Interprise__company=kampuni
        ).filter(
            Q(akaunti__isnull=False, admin_approval=False) |  # Account expenses, unapproved
            Q(fromShift__isnull=False)  # Pump attendant expenses (already managed by station manager)
        )
        if not todo['useri'].admin:
            expenses_queryset = expenses_queryset.filter(Interprise=shell.id)

        with transaction.atomic():
            # Get expense IDs first without select_for_update (to avoid nullable join lock issue)
            expense_list = list(expenses_queryset.values_list('id', flat=True))
            if not expense_list:
                return JsonResponse({'success': False, 'eng': 'No eligible expenses deleted. Only unapproved account-based expenses or pump attendant expenses can be deleted.','swa':'Hakuna matumizi yanayoruhusiwa kufutwa. Matumizi ambayo hayajahakikiwa na yametoka kwenye akaunti au matumizi ya pump attendant ndiyo yanaweza kufutwa.'})
            
            # Now lock and fetch the actual records
            expenses = list(rekodiMatumizi.objects.filter(pk__in=expense_list).select_for_update())
            if not expenses:
                return JsonResponse({'success': False, 'eng': 'No eligible expenses deleted. Only unapproved account-based expenses or pump attendant expenses can be deleted.','swa':'Hakuna matumizi yanayoruhusiwa kufutwa. Matumizi ambayo hayajahakikiwa na yametoka kwenye akaunti au matumizi ya pump attendant ndiyo yanaweza kufutwa.'})

            expense_ids = [exp.id for exp in expenses]

            # Rudisha fedha kwenye payment account husika
            account_totals = {}
            for exp in expenses:
                if exp.akaunti_id:
                    account_totals[exp.akaunti_id] = account_totals.get(exp.akaunti_id, Decimal('0')) + Decimal(exp.kiasi or 0)

            if account_totals:
                accounts = PaymentAkaunts.objects.filter(pk__in=account_totals.keys()).select_for_update()
                for acc in accounts:
                    acc.Amount = Decimal(acc.Amount or 0) + Decimal(account_totals.get(acc.id, Decimal('0')))
                    acc.save(update_fields=['Amount'])

            # Kama kuna repayment iliyofungwa kwenye record, punguza paid_amount ya StaffLoan
            repayments = loanPayMent.objects.filter(record_id__in=expense_ids).select_for_update()
            loan_totals = {}
            repayment_ids = []
            for rep in repayments:
                repayment_ids.append(rep.id)
                loan_totals[rep.loan_id] = loan_totals.get(rep.loan_id, Decimal('0')) + Decimal(rep.amount or 0)

            if loan_totals:
                loans = StaffLoan.objects.filter(pk__in=loan_totals.keys()).select_for_update()
                for loan in loans:
                    current_paid = Decimal(loan.paid_amount or 0)
                    to_reverse = Decimal(loan_totals.get(loan.id, Decimal('0')))
                    loan.paid_amount = current_paid - to_reverse if current_paid > to_reverse else Decimal('0')
                    loan.save(update_fields=['paid_amount'])

            if repayment_ids:
                loanPayMent.objects.filter(pk__in=repayment_ids).delete()

            deleted, _ = rekodiMatumizi.objects.filter(pk__in=expense_ids).delete()

        if deleted > 0:
            return JsonResponse({'success': True, 'eng': 'Expenses deleted successfully.','swa':'Matumizi yamefutwa kwa mafanikio.'})
        else:
            return JsonResponse({'success': False, 'eng': 'No eligible expenses deleted. Only unapproved account-based expenses or pump attendant expenses can be deleted.','swa':'Hakuna matumizi yanayoruhusiwa kufutwa. Matumizi ambayo hayajahakikiwa na yametoka kwenye akaunti au matumizi ya pump attendant ndiyo yanaweza kufutwa.'})
    except Exception as e:
        traceback.print_exc()
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

        sale = saleList.objects.filter(sale__session=ss,sale__shiftBy=None,theFuel=fl.Fuel.id,sale__mobile_pay=False).annotate(amount=F('qty_sold')*F('sa_price'))

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
         
        sale = saleList.objects.filter(shift__shift=s,sale__shiftBy=None,sale__mobile_pay=False).annotate(amount=F('qty_sold')*F('sa_price'))
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
           'has_analog': pmps.filter(analog_used=True).exists(),


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
            simpleAdjst = int(request.POST.get('simpleAdjst',0))
            desc = request.POST.get('desc')
            general = todo['general']
            
            shell = todo['shell']
            cheo = todo['cheo']
            kampuni = todo['kampuni']
            useri = todo['useri']
            manager = todo['manager']

            if useri.admin or manager:
                Sup = UserExtend.objects.get(pk=op,tankSup=True)
                adj = None

                def _new_adj_record(*, stock_reconcile=False, maelezo=''):
                    record = adjustments()
                    entry = adjustments.objects.filter(Interprise=shell)
                    code = invoCode(entry)
                    record.code = TCode({'code': code, 'shell': shell.id})
                    record.Invo_no = int(code)
                    record.tarehe = datetime.datetime.now(tz=timezone.utc)
                    record.operator = Sup
                    record.by = cheo
                    record.Interprise = shell
                    record.maelezo = maelezo
                    record.stock_reconcile = stock_reconcile
                    if move:
                        TankContainer = tankContainer.objects.get(pk=cont, compan=kampuni)
                        record.container = TankContainer
                    elif not stock_reconcile:
                        Lses = shiftSesion.objects.filter(session__Interprise=shell).last()
                        if Lses.complete if Lses else False:
                            sesAdj = adjustments.objects.filter(session=Lses)
                            if not sesAdj.exists():
                                record.session = Lses
                    record.save()
                    return record

                if simpleAdjst:
                    reconcile_items = []
                    for t in tanks:
                        if t.get('stick') in (None, ''):
                            continue
                        tankObj = fuel_tanks.objects.get(pk=t['val'], Interprise__company=kampuni)
                        stick = float(t['stick'])
                        if float(tankObj.qty) != stick:
                            reconcile_items.append((tankObj, stick))

                    if not reconcile_items:
                        return JsonResponse({
                            'success': True,
                            'swa': 'Hakuna mabadiliko ya stoku',
                            'eng': 'No stock changes to reconcile',
                            'id': None,
                        })

                    default_desc = (
                        'Marekebisho ya msingi wa stoku — kuweka kiasi halisi kilichopo '
                        '(stock reconciliation baseline)'
                    )
                    adj = _new_adj_record(
                        stock_reconcile=True,
                        maelezo=(desc or '').strip() or default_desc,
                    )

                    for tankObj, stick in reconcile_items:
                        init = float(tankObj.qty)
                        TAdj = tankAdjust()
                        TAdj.adj = adj
                        TAdj.tank = tankObj
                        TAdj.read = init
                        TAdj.stick = stick
                        TAdj.fuel = tankObj.fuel
                        TAdj.diff = float(stick - init)
                        TAdj.cost = float(tankObj.cost)
                        TAdj.price = float(tankObj.price)
                        TAdj.save()
                        tankObj.qty = stick
                        tankObj.save()

                    return JsonResponse({
                        'success': True,
                        'swa': 'Marekebisho ya msingi wa stoku yamehifadhiwa kikamilifu',
                        'eng': 'Stock reconciliation baseline saved successfully',
                        'id': adj.id,
                    })

                adj = _new_adj_record(maelezo=desc)

                for t in tanks:
                    if t.get('stick') in (None, ''):
                        continue
                    tankAdj = fuel_tanks.objects.get(pk=t['val'], Interprise__company=kampuni)
                    stick = float(t['stick'])
                    init = float(tankAdj.qty)

                    TAdj = tankAdjust()
                    TAdj.adj = adj
                    TAdj.tank = tankAdj
                    TAdj.read = init
                    TAdj.stick = stick
                    TAdj.fuel = tankAdj.fuel
                    TAdj.diff = float(stick - init)
                    TAdj.cost = float(tankAdj.cost)
                    TAdj.price = float(tankAdj.price)
                    TAdj.save()

                    tankAdj.qty = stick
                    tankAdj.save()

                return JsonResponse({
                    'success': True,
                    'swa': 'Taarifa za marekebisho kwenye tanki yamehifadhiwa kikamilifu',
                    'eng': 'Tank Fuel adjustment saved successfully',
                    'id': adj.id,
                })



            else:
                data = {
                    'success':False,
                    'swa':'hauna ruhusa hii kwa sasa tafadhari wasiliana na uongozi',
                    'eng':'You have no permission by now please contact admin'
                }

          
        except Exception as err :
            print(f"Error in savaAdjst: {err}")
            traceback.print_exc() 
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
    
    
def _build_purchase_trip_payload(pu_lines):
    transporter_map = {}
    driver_seen = set()
    vehicle_seen = set()
    trip_drivers = []
    trip_vehicles = []
    lines = []

    for line in pu_lines:
        pending = Decimal(str(line.qty or 0)) - Decimal(str(line.rcvd or 0))
        if pending <= Decimal('0.01'):
            continue

        att = line.puAttach
        tr = att.transp if att is not None else None
        tr_id = tr.id if tr is not None else 0
        tr_name = tr.jina if tr is not None else ''
        driver = (att.driver or '').strip() if att is not None else ''
        vehicle = (att.vihecle or '').strip() if att is not None else ''

        if tr_id not in transporter_map:
            transporter_map[tr_id] = {
                'transpoter_id': tr_id,
                'name': tr_name,
                'vihecles': []
            }

        transporter_entry = transporter_map[tr_id]
        if att is not None and not any(v.get('puAttach_id') == att.id for v in transporter_entry['vihecles']):
            transporter_entry['vihecles'].append({
                'trasp_id': tr_id,
                'driver': driver,
                'vehicle': vehicle,
                'puAttach_id': att.id
            })

        if driver:
            drv_key = (tr_id, driver)
            if drv_key not in driver_seen:
                driver_seen.add(drv_key)
                trip_drivers.append({
                    'transpoter_id': tr_id,
                    'driver': driver
                })

        if vehicle:
            veh_key = (tr_id, vehicle)
            if veh_key not in vehicle_seen:
                vehicle_seen.add(veh_key)
                trip_vehicles.append({
                    'transpoter_id': tr_id,
                    'vehicle': vehicle
                })

        lines.append({
            'id': line.id,
            'Fuel': line.Fuel_id,
            'fname': line.Fuel.name,
            'qty': float(pending),
            'othTr': False,
            'pu': True,
            'tr': line.pu_id,
            'cost': float(line.cost or 0),
            'transp_id': tr_id,
            'transp_name': tr_name,
            'driver': driver,
            'vehicle': vehicle,
        })

    trip_transporters = sorted(
        transporter_map.values(),
        key=lambda x: (x.get('name') or '').lower()
    )

    return {
        'trip_transporters': trip_transporters,
        'trip_drivers': trip_drivers,
        'trip_vehicles': trip_vehicles,
        'lines': lines,
    }


@login_required(login_url='login')
def getVendorReceiveData(request):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    try:
        vendor_id = int(request.POST.get('vendor', 0))
        shell_id = int(request.POST.get('shell', 0))
        todo = todoFunct(request)
        kampuni = todo['kampuni']

        purchase_ids = list(
            Purchases.objects.filter(
                vendor_id=vendor_id,
                closed=False,
                record_by__company=kampuni,
            ).values_list('id', flat=True)
        )
        if not purchase_ids:
            return JsonResponse({
                'success': False,
                'swa': 'Hakuna manunuzi yasiyokamilika kwa msambazaji huyu',
                'eng': 'No open purchases found for this vendor',
            })

        pu_lines = PuList.objects.filter(
            pu_id__in=purchase_ids,
            qty__gt=F('rcvd'),
        ).select_related('Fuel', 'puAttach__transp', 'pu__vendor')

        payload = _build_purchase_trip_payload(pu_lines)
        if not payload['lines']:
            return JsonResponse({
                'success': False,
                'swa': 'Hakuna mafuta yanayosubiri kupokelewa kwa msambazaji huyu',
                'eng': 'No pending fuel to receive for this vendor',
            })

        primary_purchase = Purchases.objects.filter(pk__in=purchase_ids).select_related('vendor').order_by('pk').first()
        shell_tanks = fuel_tanks.objects.filter(
            Interprise_id=shell_id,
            Interprise__company=kampuni,
            moving=False,
        ).annotate(
            Fuel=F('fuel'),
            Fname=F('fuel__name'),
            shell=F('Interprise'),
        ).values()

        return JsonResponse({
            'success': True,
            'purchase_id': primary_purchase.id,
            'vendor_name': primary_purchase.vendor.jina if primary_purchase.vendor else '',
            'sta_tanks': list(shell_tanks),
            'otherF': payload['lines'],
            **payload,
        })
    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({'success': False})


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
            pumps = todo['tr_pump'].annotate(Fuel=F('tank__fuel'),price=F('tank__price'),Fname=F('tank__fuel__name'),disp_name=F('station__name'),AF_name=F('Incharge__user__first_name'),AL_name=F('Incharge__user__last_name')).values()
            
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
            'trFuel':othF,
            'pu_vendors': wasambazaji.objects.filter(
                pk__in=PuList.objects.filter(
                    pu__closed=False,
                    pu__record_by__company=kampuni,
                    pu__vendor__isnull=False,
                    qty__gt=F('rcvd'),
                ).values_list('pu__vendor_id', flat=True).distinct()
            ).order_by('jina'),
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
    isLastsh = shifts.objects.filter(record_by__Interprise=sh.record_by.Interprise).last() == sh  

    # print(isLastsh)  

    if sh.To is  None:
        shby = InterprisePermissions.objects.filter(user=sh.by,Interprise=shell.id).first()
        return redirect(f'/salepurchase/StartEndShift?usr={shby.id}')
       
  

    attach = attachments.objects.filter(Q(shift=sh.id)|Q(session=sh.session.id))
 
    sale = saleList.objects.filter(shift__shift=sh,sale__shiftBy=None,sale__mobile_pay__isnull=True).annotate(amount=F('qty_sold')*F('sa_price'))
    tr = transFromTo.objects.filter(shift__shift=sh).annotate(worth=F('qty')*F('saprice'))
    exp = rekodiMatumizi.objects.filter(fromShift__shift=sh)
    cashB = wekaCash.objects.filter(shift=sh.id,biforeShift=True)



    exclude = { 
        'cashB':cashB,
        'cashMobAmo':cashB.filter(sales__mobile_pay=True).aggregate(Amo=Sum('Amount'))['Amo'] or 0,
        'cashBDepoAmo':cashB.filter(sales__mobile_pay__isnull=True).aggregate(Amo=Sum('Amount'))['Amo'] or 0,
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
        'has_analog_pumps': shp.filter(analog_used=True).exists(),
        'spancer_shp':spancer_shp,
        'attach':attach,
        'trf':sh,
         'sale':sale,
         'expF':exp.filter(fuel_qty__gt=0),
         'expA':exp.filter(fuel_qty=0),
         'exp':exp,
         'trd':tr,
         'exclude':exclude,
        'isShiftView':True,
        'isLastsh':isLastsh
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
        rcd_qs = receivedFuel.objects.filter(receive=trf.id).annotate(thamani=(F('qty')*F('price')))
        Tqty = rcd_qs.aggregate(sumi=Sum('qty'))['sumi']
        Tworth = rcd_qs.aggregate(sumi=Sum('thamani'))['sumi']

        # For purchase receives, enrich each received row with transporter, driver and vehicle
        # from linked purchase lines (PuList -> puAttach).
        rcd = list(rcd_qs)
        if trf is not None and trf.FromPurchase is not None:
            pu_lines = list(
                PuList.objects.filter(pu=trf.FromPurchase)
                .select_related('Fuel', 'puAttach__transp')
                .order_by('pk')
            )

            fuel_groups = {}
            for pl in pu_lines:
                fuel_id = pl.Fuel_id
                if fuel_id not in fuel_groups:
                    fuel_groups[fuel_id] = []
                fuel_groups[fuel_id].append(pl)

            used_line_ids = set()

            for row in rcd:
                row.transporter = ''
                row.driver = ''
                row.vehicle = ''

                candidates = fuel_groups.get(row.Fuel_id, [])
                if not candidates:
                    continue

                available = [pl for pl in candidates if pl.pk not in used_line_ids]
                if not available:
                    available = candidates

                match = min(
                    available,
                    key=lambda pl: abs(float(pl.qty or 0) - float(row.qty or 0))
                )
                used_line_ids.add(match.pk)

                if match.puAttach is not None:
                    row.transporter = match.puAttach.transp.jina if match.puAttach.transp is not None else ''
                    row.driver = match.puAttach.driver or ''
                    row.vehicle = match.puAttach.vihecle or ''

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

# Payment Approval ..........................................//
@login_required(login_url='login')
def  approveShiftCustomerMobilePayments(request):
    if request.method == 'POST':
        try:   
            payIds = json.loads(request.POST.get('payment_ids'))
            todo = todoFunct(request)
            kampuni = todo['kampuni']
            useri = todo['useri']
            cashD = int(request.POST.get('cashD',0))
            expense = int(request.POST.get('expense',0))
           
            if not useri.admin:
                data = {
                    'success':False,
                    'msg_swa' : 'Huna ruhusa ya kuidhinisha malipo ya wateja tafadhari wasiliana na uongozi' ,
                    'msg_eng' : 'You have no permission to approve customer payments please contact admin',
                }
                return JsonResponse(data)
            for pid in payIds:
                pay = None
                if cashD:
                    pay = toaCash.objects.get(pk=pid,Interprise__company=kampuni)
                elif expense:
                    pay = rekodiMatumizi.objects.get(pk=pid,Interprise__company=kampuni)
                else:    
                    pay = wekaCash.objects.get(pk=pid,Interprise__company=kampuni)
                pay.admin_approval = True
                pay.save()
            data = {
                'success':True,
                'swa':'Malipo ya mteja yameidhinishwa kikamilifu',
                'eng':'Customer payment approved successfully',
            }
            return JsonResponse(data)
        except Exception as err:
            print(f"Error in DeletePayMents: {err}")
            traceback.print_exc() 
            data = {
                'success':False,
                'swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi',
                'eng':'the action was not successfully please try again correctly'
            }
            return JsonResponse(data)          


# Delete Payments .........................................//
@login_required(login_url='login')
def  DeletePayMents(request):
    if request.method == 'POST':
        try:
            payId=int(request.POST.get('payId'))
            customerId=int(request.POST.get('customerId',0))
            tr = int(request.POST.get('tr',0))
            todo = todoFunct(request)
            kampuni = todo['kampuni']
            useri = todo['useri']
            manager = todo['manager']
            if not useri.admin:
                data = {
                    'success':False,
                    'msg_swa' : 'Huna ruhusa ya kufuta malipo ya wateja tafadhari wasiliana na uongozi' ,
                    'msg_eng' : 'You have no permission to delete customer payments please contact admin',
                }
                return JsonResponse(data)
            pay = None
            if customerId: 
                pay = wekaCash.objects.get(pk=payId,Interprise__company=kampuni,customer=customerId)

                cust = wateja.objects.get(pk=customerId,Interprise__company=kampuni)
                payRecs = CustmDebtPayRec.objects.filter(pay=pay)
                hasCdOd = pay.cdOrder
                if hasCdOd is not None:
                    hasCdOd.paid = float(float(hasCdOd.paid) - float(pay.Amount)) if float(hasCdOd.paid )- float(pay.Amount) >=0 else 0
                    hasCdOd.prepaid_order = False
                    hasCdOd.save()      

                for pr in payRecs:
                    sale = pr.sale
                    sale.payed = float(float(sale.payed) - float(pr.Apay))
                    sale.save()
                    paid_cdOd = sale.cdorder
                    if paid_cdOd is not None and hasCdOd is None:
                        paid_cdOd.paid = float(float(paid_cdOd.paid) - float(pr.Apay))
                        paid_cdOd.prepaid_order = False
                        paid_cdOd.save()
                payRecs.delete()
                pay.delete()
            
            if tr:
                pay = toaCash.objects.get(pk=payId,Interprise__company=kampuni,kuhamisha=True)   
                fromAc = wekaCash.objects.filter(kutoka__icontains=pay.Akaunt.Akaunt_name,Interprise__company=kampuni,tarehe__gte=pay.tarehe,Amount=float(pay.Amount)).order_by('pk').first()
                toAcc = pay.Akaunt
                toAcc.Amount = float(float(toAcc.Amount) - float(pay.Amount)) if float(toAcc.Amount) - float(pay.Amount) >=0 else 0
                toAcc.save()
                # print(fromAc)
                if fromAc:
                    fromAcAcc = fromAc.Akaunt
                    fromAcAcc.Amount = float(float(fromAcAcc.Amount) + float(pay.Amount)) 
                    fromAcAcc.save()
                    fromAc.delete()  
                pay.delete()
                  

            data = {
                'success':True,
                'swa':'Malipo ya mteja yamefutwa kikamilifu',
                'eng':'Customer payment deleted successfully',
                
            }
            return JsonResponse(data)


        except Exception as err :
            print(f"Error in DeletePayMents: {err}")
            traceback.print_exc() 
            data = {
                'success':False,
                'swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi',
                'eng':'the action was not successfully please try again correctly'
            }
            return JsonResponse(data)
            

# pay  INVOINCE .........................................//
@login_required(login_url='login')
def  lipaInvo(request):
      
      if request.method == 'POST':
            try:
                  value=int(request.POST.get('invo'))
                  ac=int(request.POST.get('ac'))
                  pall=int(request.POST.get('all',0))
                  isCredit = int(request.POST.get('isCredit',0))
                  edit = int(request.POST.get('edit',0))
                  

                  paid_amo = float(request.POST.get('pay_amo'))  
                  pay_d = request.POST.get('date')
                  desc = request.POST.get('desc','')
                  
                  kutoka = ''
                  todo = todoFunct(request)
                  manager = todo['manager']
                  useri = todo['useri']
                  cheo = todo['cheo']
                #   shell = cheo.Interprise
                  kampuni = todo['kampuni']
                 
                  acc = PaymentAkaunts.objects.get(pk=ac,Interprise__company=kampuni)
                  shell = acc.Interprise
                  if not (useri.admin or acc.aina=='Cash'):

                    data = {
                        'success':False,
                        'msg_swa' : 'Huna ruhusa ya kutumia akaunti hii ya malipo tafadhari wasiliana na uongozi' ,
                        'msg_eng' : 'You have no permission to use this payment account please contact admin',
                    }
                    return JsonResponse(data)

                  if not (useri.admin or manager):
                        data = {
                            'pay':True,  
                            'success':False,
                            'msg_swa' : 'Huna ruhusa ya kufanya malipo ya ankara tafadhari wasiliana na uongozi' ,
                            'msg_eng' : 'You have no permission to make invoice payment please contact admin',
                      }
                        return JsonResponse(data)
                  
                  if edit and not useri.admin:
                      data = {
                        'success':False,
                        'msg_swa' : 'Huna ruhusa ya kufanya malipo ya ankara tafadhari wasiliana na uongozi' ,
                        'msg_eng' : 'You have no permission to make invoice payment please contact admin',
                      }  

                      return JsonResponse(data)
                  
                #   if paid_amo:
                #     print(paid_amo)     
                #     data = {'success':True}
                #     return JsonResponse(data)

                  ilolipwa = 0
                  malipo = 0
                  kiasi = 0
                  bill = None 
                  cust = None
                  custOder = None
                  order_due = 0
                  total_deni = 0
                  weka = wekaCash()
                  if edit:
                    weka = wekaCash.objects.get(pk=edit,Interprise__company=kampuni,customer=value)
                    #  clear all prev paid invoices amount 
                    prevPays = CustmDebtPayRec.objects.filter(pay=weka)
                    
                    for pp in prevPays:
                        sale = pp.sale
                        sale.payed = float(float(sale.payed) - float(pp.Apay))
                        sale.save()
                        paid_cdOd = sale.cdorder
                        if paid_cdOd is not None:
                            paid_cdOd.paid = float(float(paid_cdOd.paid) - float(pp.Apay))
                            paid_cdOd.prepaid_order = False
                            paid_cdOd.save()
                    prevPays.delete()
                    
                     

                  if pall:
                     cust = wateja.objects.get(pk=value,Interprise__company=kampuni.id)
                     bill = fuelSales.objects.filter(customer=cust,payed__lt=F('amount'))
                     total_deni = float(bill.aggregate(sumi=Sum(F('amount')-F('payed')))['sumi'] or 0)
                          
                     custOders = creditDebtOrder.objects.filter(customer=cust,paid__lt=F('amount')).order_by('-pk')
                     custOder = custOders.first() if custOders.exists() else None
                     order_due = float(custOder.amount - custOder.paid) if custOder is not None else 0

                     if not custOder and  total_deni < paid_amo and not edit:
                        data = {
                            'pay':True,  
                            'success':False,
                            'msg_swa' : 'kiasi kilicholipwa kimezidi fedha inayodaiwa' ,
                            'msg_eng' : 'The paid amount exceeds the total due amount',
                      }
                        return JsonResponse(data)


                     kutoka = cust.jina
                     ilolipwa = float(bill.aggregate(lipwa=Sum('payed'))['lipwa'] or 0)
                     malipo = float(paid_amo+ilolipwa) 
                     kiasi = float(bill.aggregate(kiasi=Sum('amount'))['kiasi'] or 0)
                     
                  if not (pall or edit):    
                        
                        bill = fuelSales.objects.get(by__Interprise=shell,pk=value)
                        ilolipwa = float(bill.payed)
                        malipo =   float(paid_amo+ilolipwa) 
                        kiasi = float(bill.amount) 
                        kutoka =f"INVO-{bill.code} Sales"
                        


                  after={
                        'pay':True,  
                        'success':True,
                        'msg_swa' : 'Data za Malipo ya ankara zimehifadhiwa kikamilifu' ,
                        'msg_eng' : 'Invoice Payment recorded succefully',
                  }
            
                  prepaid_order = total_deni < paid_amo and order_due > 0
                #   print(prepaid_order,total_deni, paid_amo, order_due)
                  
                  
                  if ((malipo <= kiasi  and malipo>0) or prepaid_order) or edit: 
                        lipwaAmo = paid_amo
                        wekakwa= acc
                        beforweka=float(wekakwa.Amount)    
                        
                        weka.Akaunt = wekakwa
                        weka.Amount = float(lipwaAmo)
                        weka.before = beforweka               
                        weka.After = float(beforweka + lipwaAmo) 
                        weka.kutoka = kutoka
                        weka.maelezo = desc
                        if not edit:
                            weka.tarehe = datetime.datetime.now(tz=timezone.utc)
                        weka.by=useri
                        weka.Interprise=shell
                        weka.mauzo=True
                        weka.tInvo = len(bill) if bill.exists() else 0
                        weka.tDebt = float(bill.aggregate(sumi=Sum(F('amount')-F('payed')))['sumi'] or 0)
                        weka.customer = cust

                        if prepaid_order and not edit:
                            weka.cdOrder = custOder
                            custOder.paid = float(float(custOder.paid) + paid_amo) if order_due <= paid_amo else float(custOder.amount)
                            custOder.prepaid_order = True if order_due <= paid_amo else False
                            custOder.save()

                        if edit and weka.cdOrder is not None:
                            cdOd = weka.cdOrder
                            pay_diff = float(paid_amo - float(weka.Amount))
                            cdOd.paid = float(float(cdOd.paid)+float(pay_diff))
                            cdOd.prepaid_order = prepaid_order
                            cdOd.save()
                            if float(cdOd.paid) > float(cdOd.amount):
                                cdOd.amount = float(cdOd.paid)
                                cdOd.save()

                        if not wekakwa.onesha:
                            weka.usiri =True               
                        wekakwa.Amount = float(beforweka + lipwaAmo)   
                        wekakwa.save()              
                        weka.save()



                        if not pall: 
                            bill.payed = malipo
                            bill.save()
                        else:
                            for b in bill.order_by('pk') if bill.exists() else []:
                                if paid_amo > 0:  
                                    deni = float(b.amount - b.payed)
                                    lipwa = float(b.payed)
                                    theP = paid_amo
                                    if deni < paid_amo:
                                        b.payed = float(lipwa + deni)
                                        paid_amo = paid_amo - deni
                                        theP = deni
                                        # print('paid item1',b.pk,deni)
                                        b.save()    
                                    else:
                                        b.payed = float(lipwa + paid_amo)
                                        paid_amo = 0  
                                        b.save()
                                        print('paid item2',b.pk,paid_amo,b.payed)
                                        break  
                                    # b.save()
                                    # print('paid item',b.pk,b.payed)

                                    if b.cdorder is not None and not prepaid_order:
                                        cdOd = b.cdorder
                                        cdOd.paid = float(float(cdOd.paid)+float(theP))
                                        cdOd.save()

                                    custP = CustmDebtPayRec()  
                                    custP.sale = b
                                    custP.pay = weka   
                                    custP.Debt =  deni 
                                    custP.Apay =  float(theP)
                                    custP.save()
                                    

                  else:
                              after={
                                    'pay':True,  
                                    'success':False,
                                    'msg_swa' : 'Data za Malipo ya ankara hazijafanikiwa  kutokana na kiasi kinacholipwa kuzidi kiasi halisi cha ankara' ,
                                    'msg_eng' : 'Invoice Payment was not recorded, because the paid amount exceeds the invoice amount',
                              }     
                  return JsonResponse(after)
            except Exception as err:
                  print('error in payment',err)
                  traceback.print_exc()
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
    has_no_shift = saL.filter(shift__shift__isnull=True).exists()
   
    akaunts = wekaCash.objects.filter(sales=trf.id,saRec=False).order_by('-pk')

    baki = trf.amount - trf.payed

    total_og = saL.aggregate(sumi=Sum('amounti'))['sumi'] or 0
    disc = total_og - trf.amount
  
    todo.update({
        'attach':attach,
        'trf':trf,
         'has_no_shift':has_no_shift,
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
            cust = int(request.POST.get('cust',0))
            is_pu = int(request.POST.get('purchaseId',0))
            is_pu_recept = int(request.POST.get('is_pu_receipt',0))
            is_pu_invo = int(request.POST.get('is_pu_invo',0))

            is_exp = int(request.POST.get('is_exp',0))

            attName = request.POST.get('attach_name')
            printDoc = int(request.POST.get('printedDoc',0))

            todo = todoFunct(request)
            manager = todo['manager']
            useri = todo['useri']
            kampuni = todo['kampuni']
                  
            if useri.admin or manager:
                gcs_storage = default_storage
                if not settings.DEBUG:
                    gcs_storage = settings.GCS_STORAGE_INSTANCE

                ext = file.name.split('.')[-1]
                filename = f"attachments/{kampuni.id}_{int(time.time())}.{ext}"
                path = gcs_storage.save(filename, file)

                att = attachments()
                
                att.file = path
                # att.file.save(file.name, file)
                att.date = datetime.datetime.now(tz=timezone.utc)
                att.by = useri
                # print(is_exp)
                if is_exp:
                    expense = rekodiMatumizi.objects.get(pk=is_exp,Interprise__company=kampuni)
                    att.expAttach = expense
                    attName = expense.matumizi.matumizi

                # print(printDoc)
                if is_pu:
                    if not useri.admin or useri.pu:
                        data = {
                            'success':False,
                            'msg_swa':'Hauna ruhusa ya kuunganisha kiambatanisho hiki tafadhari wasiliana na uongozi',
                            'msg_eng':'You have no permission to attach this attachment please contact admin'
                        }
                        return JsonResponse(data)
                    
                    puAtt = puAttachments.objects.get(pk=is_pu,purchase__vendor__compan=kampuni)
                    att.puAttach = puAtt
                    att.receipt = is_pu_recept
                    att.puInvo = is_pu_invo
                    att.purchase = puAtt.purchase
                    if is_pu_recept:
                        attName = f"PU-{puAtt.purchase.code} Receipt "
                    if is_pu_invo:
                        attName = f"PU-{puAtt.purchase.code} Invoice "    



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

                if cust:
                    ftr = wateja.objects.get(pk=cust) 
                    att.cust = ftr


                att.printedDocu = printDoc
                att.attach_name = attName
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
        except Exception as err:
            print(f"Error in addAttach: {err}")
            traceback.print_exc()
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
                sesDate = datetime.datetime.fromisoformat(tFrom).date()
                sesSh = shiftSesion.objects.filter(session=ssn, date=sesDate, complete=False)
                if sesSh.exists():
                   sesSt = sesSh.last()
                else:
                    sesSt = shiftSesion()
                    sesSt.date = sesDate
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
                    if p.get('analog') is not None:
                        pmp.analog_readings = float(p['analog'])
                        pmp.save(update_fields=['analog_readings'])
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

    sale = saleList.objects.filter(shift__shift=shift,sale__shiftBy=None,sale__mobile_pay=False).aggregate(Sum('qty_sold'))['qty_sold__sum'] or 0
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
                
                sh = shifts.objects.get(record_by__Interprise=shell,pk=shift,by=inch.user)
                
                

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
                    analog_used = bool(p.get('analog_used'))
                    closing = float(p['final'])

                    if analog_used:
                        opening = float(p.get('analog_initial') or pmp.analog_readings or pmpsh.initial)
                        sh_diff = float(closing - opening)
                        pmpsh.initial = opening
                        pmpsh.final = closing
                        pmpsh.analog_used = True
                        pmp.analog_readings = closing
                    else:
                        sh_diff = float(closing - float(pmp.readings))
                        pmpsh.final = closing
                        pmpsh.analog_used = False
                        pmp.readings = closing

                    pmpsh.qty = sh_diff
                    pmpsh.cost = float(pmp.tank.cost)
                    pmpsh.price = float(pmp.tank.price)
                    pmpsh.amount = float(sh_diff * float(pmp.tank.price))
                    pmpsh.save()

                    if analog_used:
                        usr = InterprisePermissions.objects.filter(Interprise=shell, Allow=True)
                        for us in usr:
                            notify = notifications()
                            notify.usr = us.user
                            notify.analog_readings_used = pmpsh
                            notify.desc = (
                                f'Mita ya analogi imetumika kwenye pampu {pmp.name} '
                                f'({pmp.station.name if pmp.station else ""}) zamu SHF-{sh.code}'
                            )
                            notify.date = datetime.datetime.now(tz=timezone.utc)
                            notify.save()

               
                    sale = saleList.objects.filter(shift=pmpsh.id,sale__customer__Interprise__company=kampuni,sale__mobile_pay=False).aggregate(Sum('qty_sold'))['qty_sold__sum'] or 0
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
                                shiftSale = saleList.objects.filter(sale__session=ses,shift__pump__tank=rt.tank,shift__shift__session=ses,sale__mobile_pay=False)
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
                
        except Exception as err:
            print('error end shift',err)
            traceback.print_exc() 
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
 
      'approval':toApprovalPayments(request),
      'Incharges':shiftAttend,
      'isShiftAttend':True,
      'payment_nav_active':'shifts',
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
     

      hasshift = shifts.objects.filter(by=by.user.id,To=None,record_by__Interprise=todo['shell'])
      if hasshift.exists():
            shift = hasshift.last()
            shp = shiftPump.objects.filter(shift=shift)
            fl_shp = shp.distinct('Fuel')
            spancer_shp = shp.distinct('pump__station')

            # print(spancer_shp.count())

            sale = saleList.objects.filter(shift__shift=shift.id,sale__shiftBy=None,sale__mobile_pay=False).annotate(amount=F('qty_sold')*F('sa_price'))
            tr = transFromTo.objects.filter(shift__shift=shift.id).annotate(worth=F('qty')*F('saprice'))
            exp = rekodiMatumizi.objects.filter(fromShift__shift=shift.id)

            cashB = wekaCash.objects.filter(shift=shift)

            tr_pump = fuel_pumps.objects.filter(Incharge=shift.by.id)
            disp = tr_pump.distinct('station')

            exclude = {
                'cashB':cashB,
                'cashBmobA':cashB.filter(sales__mobile_pay=True).aggregate(Amo=Sum('Amount'))['Amo'] or 0,
                'cashBcashD':cashB.filter(sales__mobile_pay__isnull=True).aggregate(Amo=Sum('Amount'))['Amo'] or 0,
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
      shiftStarted = None
      lastShift = shifts.objects.filter(record_by__Interprise=shell.id,To=None).order_by('pk')
      if lastShift.exists():
          shiftStarted = lastShift.last()



  todo.update({
      'trf':by,
      'shift':shift,
      'pumps':pmps.order_by('pk'),
      'fuel':fl,
      'shiftStarted':shiftStarted,
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
        isClosed = int(request.POST.get('closed', 0))

        if not (manager or useri.admin):
            return JsonResponse({'success': False, 'eng': 'Permission denied.', 'swa': 'Ruhusa haijarusiwa.'})
        if not shift_id:
            return JsonResponse({'success': False, 'eng': 'No shift ID provided.', 'swa': 'Hakuna ID ya zamu iliyotolewa.'})
        
        shiftToD = shifts.objects.get(pk=shift_id, record_by__Interprise=shell.id,To=None) if not isClosed else shifts.objects.get(pk=shift_id, record_by__Interprise=shell.id)

        ses = shiftToD.session
        isLastshift = shifts.objects.filter(record_by__Interprise=shiftToD.record_by.Interprise).last() == shiftToD
        if isClosed and not isLastshift:
            data = {
                'success':False,
                'eng':'Only the last closed shift can be deleted.',
                'swa':'Zamu iliyofungwa ya mwisho tu ndiyo inaweza kufutwa.'
            }
            return JsonResponse(data)

        if isClosed and isLastshift:
            shpmps = shiftPump.objects.filter(shift=shiftToD)
            for sp in shpmps:
                fuel_flow = sp.final - sp.initial
                tank = sp.pump.tank
                tank.qty = float(float(tank.qty) + float(fuel_flow))
                tank.save()

                pmp = sp.pump
                pmp.readings = float(sp.initial)
                pmp.save()

            #delete the session adj    
            adjustments.objects.filter(session=ses,container=None).delete()    



        sale = saleList.objects.filter(shift__shift=shiftToD.id)
        for s in sale:
            theSale = s.sale
            s.delete()
            rems = saleList.objects.filter(sale=theSale.id)

            if not rems.exists():
                saleAmo = theSale.amount
                payedAmo = theSale.payed
                

                IsCreditor = theSale.cdorder
                if IsCreditor is not None:
                    IsCreditor.consumed = float(float(IsCreditor.consumed) - float(saleAmo))
                    IsCreditor.save()
                    custm = IsCreditor.customer
                    custm.limited_order = True
                  
                    custm.save()

                sale_payed = CustmDebtPayRec.objects.filter(sale=theSale.id)
                for sp in sale_payed:
                    paytr = sp.pay
                    paytr.used_amount = float(float(paytr.used_amount) - float(sp.Apay))
                    paytr.save()
                accs = wekaCash.objects.filter(sales=theSale.id,cdOrder__isnull=True)
                for ac in accs:
                    acc = ac.Akaunt
                    acc.Amount = float(float(acc.Amount) - float(payedAmo))
                    acc.save()
                    ac.delete()

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
        traceback.print_exc() 
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
        # print(order_id)  
        saleL = saleList.objects.filter(Q(shift__shift__To=None)|Q(shift__shift__isnull=True),pk__in=order_id, sale__by__Interprise=shell.id)
        if saleL.exists():
            for saL in saleL:

                    sale = saL.sale

                    IsCreditor = sale.cdorder
                    if IsCreditor is not None:
                        IsCreditor.consumed = float(float(IsCreditor.consumed) - float(sale.amount))
                        IsCreditor.save()
                        custm = IsCreditor.customer
                        custm.limited_order = True
                        custm.save()
                    sale_payed = CustmDebtPayRec.objects.filter(sale=sale.id)
                    for sp in sale_payed:
                        paytr = sp.pay
                        paytr.used_amount = float(float(paytr.used_amount) - float(sp.Apay))
                        paytr.save()

                    accs = wekaCash.objects.filter(sales=sale.id,cdOrder__isnull=True)
                    for ac in accs:
                        acc = ac.Akaunt
                        acc.Amount = float(float(acc.Amount) - float(sale.payed))
                        acc.save()
                        ac.delete()                        

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

    except Exception as err:
        print(err) 
        traceback.print_exc() 
        data = {
            'success':False,
            'swa':'Kitendo hakikufanikiwa tafadhari jaribu tena',
            'eng':'The action was unsuccessfull please try again'
        }
        return JsonResponse(data)
    
@login_required(login_url='login')
@require_POST
def deleteCashDeposit(request):
    try:
        todo = todoFunct(request)
        shell = todo['shell']
        manager = todo['manager']
        useri = todo['useri']
        
        if not (manager or useri.admin):
            return JsonResponse({
                'success': False, 
                'eng': 'Permission denied.',
                'swa': 'Ruhusa haijaruhusiwa.'
            })
        
        cash_deposit_ids = request.POST.getlist('cash_deposit_ids[]')
        if not cash_deposit_ids:
            # Try as JSON string if not sent as array
            cash_deposit_ids = json.loads(request.POST.get('cash_deposit_ids', '[]'))
        
        # Ensure all ids are integers
        cash_deposit_ids = [int(cid) for cid in cash_deposit_ids if str(cid).isdigit()]
        
        if not cash_deposit_ids:
            return JsonResponse({
                'success': False, 
                'eng': 'No valid cash deposit IDs provided.',
                'swa': 'Hakuna vitambulisho halali vya amana za fedha vilivyotolewa.'
            })
        
        # Get cash deposits to delete
        cash_deposits = wekaCash.objects.filter(
            pk__in=cash_deposit_ids, 
            Interprise=shell.id,
            biforeShift=True
        )
        
        if not cash_deposits.exists():
            return JsonResponse({
                'success': False, 
                'eng': 'No cash deposits found.',
                'swa': 'Hakuna amana za fedha zilizopatikana.'
            })
        
        deleted_count = 0

        for deposit in cash_deposits:
            # Reduce amount from payment account
            isDeleted = False
            if deposit.Akaunt:
                acc = deposit.Akaunt
                acc.Amount = float(float(acc.Amount) - float(deposit.Amount))
                acc.save()
            isMobilePay = deposit.sales.mobile_pay if deposit.sales else False
            
            if isMobilePay:
                # if mobile pay delete the corresponding sales but if two shifts involved do not delete and throw error and end for loop
                sale = deposit.sales
                saL = saleList.objects.filter(sale=sale.id,shift__shift__To__isnull=False)
                if saL.exists():
                    return JsonResponse({
                        'success': False, 
                        'eng': 'Cannot delete deposit linked to sales from ended shifts.',
                        'swa': 'Haiwezi kufuta amana inayohusiana na mauzo kutoka zamu zilizomalizika.'
                    })
                else:
                    sale.delete()
                    isDeleted = True
                    deleted_count += 1
                    

            # Delete the deposit
            if not isDeleted:
                deposit.delete()
                deleted_count += 1
        
        if deleted_count > 0:
            return JsonResponse({
                'success': True, 
                'eng': 'Cash deposits deleted successfully.',
                'swa': 'Amana za fedha zimefutwa kwa mafanikio.'
            })
        else:
            return JsonResponse({
                'success': False, 
                'eng': 'No cash deposits deleted.',
                'swa': 'Hakuna amana za fedha zilizofutwa.'
            })
            
    except Exception as e:
        print(e)
        traceback.print_exc() 
        return JsonResponse({
            'success': False, 
            'eng': f'Error: {str(e)}',
            'swa': f'Hitilafu: {str(e)}'
        })



@login_required(login_url='login')
@require_POST
def deleteFuelTransfers(request):
    try:
        todo = todoFunct(request)
        shell = todo['shell']
        manager = todo['manager']
        useri = todo['useri']
        if not (manager or useri.admin):
            return JsonResponse({'success': False, 'eng': 'Permission denied.', 'swa': 'Ruhusa haijarusiwa.'})
        transfer_ids = json.loads(request.POST.get('transfer_ids', '[]'))
        if not transfer_ids:
            return JsonResponse({'success': False, 'eng': 'No transfer IDs provided.', 'swa': 'Hakuna ID za uhamisho zilizotolewa.'})
        transfr = transFromTo.objects.filter(pk__in=transfer_ids,shift__shift__record_by__Interprise=shell.id,shift__shift__To=None)
        if transfr.exists():
            for tf in transfr:
                totnk = tf.to
                totnk.qty = float(float(totnk.qty) - float(tf.qty))
                totnk.save()
                theTr = tf.transfer
                tf.delete()
                remft = transFromTo.objects.filter(transfer=theTr.id)
                if not remft.exists():
                    theTr.delete()
            data = {
                'success':True,
                'swa':'Uhamisho umefutwa kikamilifu',
                'eng':'Transfer deleted successfully'
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
        try:
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

        except:
            data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
                'msg_eng':'The action was not successfully please try again',
            }
            return JsonResponse(data)
    
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
        try:
            shift = int(request.POST.get('shift'))
            amoC = float(request.POST.get('amoC'))
            To_acco = int(request.POST.get('To_acco',0))
            giveTo = request.POST.get('To')
            desc = request.POST.get('desc')
            FromPmp = int(request.POST.get('FromPmp',0))
            FrmAcc = int(request.POST.get('FrmAcc',0))
            depo_to = int(request.POST.get('depo_to',0))
            depo_sup = int(request.POST.get('depo_sup',0))
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
                acount = None
                depoSupv = None
                if depo_to == 2:
                    acount=PaymentAkaunts.objects.get(pk=To_acco,Interprise__company=kampuni.id)
                if depo_to == 1:
                   supv_acc = PaymentAkaunts.objects.filter(Interprise__company=kampuni.id,supv_acc=True)
                   depoSupv = UserExtend.objects.get(Q(acc_supv=True)|Q(admin=True),pk=depo_sup,company=kampuni.id)
                   if supv_acc.exists():
                      acount = supv_acc.last()
                   else:
                      acount = PaymentAkaunts()
                      acount.Interprise = shell
                      acount.Akaunt_name = "SUPERVISOR"
                      acount.Amount = float(0)
                      acount.addedDate = datetime.datetime.now(tz=timezone.utc)
                      acount.aina = 'Supervisor'
                      acount.supv_acc = True
                      acount.onesha = True
                      acount.save()


                depoTo = None 
                if not FromPmp:
                    depoTo = DepositTo()
                    depoTo.supv = depoSupv
                    depoTo.save()

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
                        toa.admin_approval = useri.admin
                        toa.kuhamisha = True
                        
                        toa.kuhamishaNje =  acount.Interprise is not fA.Interprise
                        toa.depoTo = depoTo
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
                weka.admin_approval = useri.admin 
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

                if depoTo is not None:
                    depoTo.weka = weka
                    depoTo.save()

            
            else:
                data = {
                    'success':False,
                    'msg_swa':'Hauna Ruhusa ya kuongeza Pampu',
                    'msg_eng':'You have no permition to add Pump',
                }


            return JsonResponse(data)

        except Exception as err:
            print(err)
            data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
                'msg_eng':'The action was not successfully please try again',
            }
            return JsonResponse(data)
    

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
             kampuni = todo['kampuni']
             if useri.admin or manager:  
                isActive = int(request.POST.get('isActive',0))
                name=request.POST.get('jina')
                address=request.POST.get('adress')
                code=request.POST.get('code')
                simu1=request.POST.get('simu1')
                simu2=request.POST.get('simu2')
                mail=request.POST.get('mail')
                isActive=int(request.POST.get('isActive',1))
                value=request.POST.get('value')
                edit=int(request.POST.get('edit',0))
                valued=int(request.POST.get('valued',0))
                un = int(request.POST.get('u',0))
                  
                

                teja=wateja()
                wtj = wateja.objects.filter(added_by__company=kampuni,pk=valued)
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
                if edit:
                    teja.active = isActive  

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
def vendosAttachments(request):
    try:
        todo = todoFunct(request)
        pu_invo_recept = todo['pu_invo_recept']
        ven = int(request.GET.get('v',0))
        uns = int(request.GET.get('uns',0))
        kampuni = todo['kampuni']
        vend = wasambazaji.objects.get(pk=ven,compan=todo['kampuni'].id) if ven else None
        all_ven = wasambazaji.objects.filter(compan=todo['kampuni'].id,active=True)
        if vend is not None:
            all_ven = all_ven.exclude(pk=ven)
       
        if uns and not pu_invo_recept:
            uns = 0
        missingAttachments = []    
        all_attachments = None
        if uns and pu_invo_recept:
           puAttach = puAttachments.objects.filter(purchase__record_by__company=kampuni.id)     
           for pu in puAttach:
                 pu_recept = attachments.objects.filter(puAttach=pu.id,receipt=True)
                 pu_invo = attachments.objects.filter(puAttach=pu.id,puInvo=True)
                 if not pu_recept.exists() or not pu_invo.exists():
                     missingAttachments.append({
                         'pu':pu,
                         'hasRecept':pu_recept.exists(),
                         'hasInvo':pu_invo.exists(),
                         'transp_amount':PuList.objects.filter(puAttach=pu).aggregate(amo=Sum('trn_amo'))['amo'] or 0,
                         'fuel_amount':PuList.objects.filter(puAttach=pu).aggregate(amo=Sum(F('qty')*F('cost')))['amo'] or 0
                     })
        else:
            all_attachments = attachments.objects.filter(purchase__record_by__company=kampuni.id).order_by('-pk')  
            if ven:
                all_attachments = all_attachments.filter(purchase__vendor=ven)
            
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
                'pg_page':page.number,
                'num':num,
                'all_attachments':all_attachments,
            })
   

        todo.update({
            'attach_tab':True,
            'ven':vend,
            'vendors':all_ven,
            'thereisVen':True if vend is not None else False,
            'uns':uns,
            'missingAttachments':missingAttachments,
            
        
         
           
            })
        
        return render(request,'vendosAttachments.html',todo)
    
    except Exception as err:
        print(err)
        traceback.print_exc()
        return render(request,'pagenotFound.html',todoFunct(request))

@login_required(login_url='login')
def purchaseStatement(request):
    try:
        todo = todoFunct(request)
        ven = int(request.GET.get('v',0))
        vend = wasambazaji.objects.get(pk=ven,compan=todo['kampuni'].id) if ven else None
        all_ven = wasambazaji.objects.filter(compan=todo['kampuni'].id,active=True)
        todo.update({
            'statement_tab':True,
            'venIid':ven,
            'ven':vend,
            'thereisVen':True if vend is not None else False,
            'all_ven':all_ven
        })
        return render(request,'vendorsStatement.html',todo)
    except Exception as err:
        print(err)
        return render(request,'pagenotFound.html',todoFunct(request))


@login_required(login_url='login')
def transporterStatement(request):
    try:
        todo = todoFunct(request)
        t = int(request.GET.get('t', 0))
        trsp = transporter.objects.get(pk=t, compan=todo['kampuni'].id) if t else None
        all_trsp = transporter.objects.filter(compan=todo['kampuni'].id, active=True)
        if trsp is not None:
            all_trsp = all_trsp.exclude(pk=trsp.id)

        todo.update({
            'transporter_statement_tab': True,
            'trspIid': t,
            'trsp': trsp,
            'thereisTrsp': True if trsp is not None else False,
            'all_trsp': all_trsp,
            'isTranspoter': 1,
        })
        return render(request, 'transporterStatement.html', todo)
    except Exception as err:
        print(err)
        traceback.print_exc()
        return render(request, 'pagenotFound.html', todoFunct(request))


@login_required(login_url='login')
def transporterStatementData(request):
    try:
        trsp_id = int(request.POST.get('transporter', request.GET.get('transporter', 0)) or 0)
        tFr = request.POST.get('tFr', request.GET.get('tFr', ''))
        tTo = request.POST.get('tTo', request.GET.get('tTo', ''))

        todo = todoFunct(request)
        kampuni = todo['kampuni']
        useri = todo['useri']
        trsp_obj = None

        if trsp_id:
            trsp_obj = transporter.objects.filter(pk=trsp_id, compan=kampuni.id).first()

        def parse_dt(value):
            if not value:
                return None
            if isinstance(value, str):
                dt = parse_datetime(value)
                if dt:
                    return dt
                try:
                    return datetime.datetime.fromisoformat(value)
                except Exception:
                    return None
            return value

        tFr_dt = parse_dt(tFr)
        tTo_dt = parse_dt(tTo)

        purchases_qs = PuList.objects.filter(
            pu__record_by__company=kampuni.id,
            puAttach__isnull=False,
            puAttach__transp__compan=kampuni.id,
        )
        payments_qs = toaCash.objects.filter(
            Akaunt__isnull=False,
            trsp_bill__isnull=False,
            Interprise__company=kampuni,
            trsp_bill__compan=kampuni.id,
        )

        if trsp_obj is not None:
            purchases_qs = purchases_qs.filter(puAttach__transp=trsp_obj)
            payments_qs = payments_qs.filter(trsp_bill=trsp_obj)

        before_purchases_qs = purchases_qs
        before_payments_qs = payments_qs

        if tFr_dt is not None:
            purchases_qs = purchases_qs.filter(pu__date__gte=tFr_dt)
            payments_qs = payments_qs.filter(tarehe__gte=tFr_dt)
            before_purchases_qs = before_purchases_qs.filter(pu__date__lt=tFr_dt)
            before_payments_qs = before_payments_qs.filter(tarehe__lt=tFr_dt)

        if tTo_dt is not None:
            purchases_qs = purchases_qs.filter(pu__date__lte=tTo_dt)
            payments_qs = payments_qs.filter(tarehe__lte=tTo_dt)

        opening_purchases = float(before_purchases_qs.aggregate(total=Sum('trn_amo'))['total'] or 0)
        opening_payments = float(before_payments_qs.aggregate(total=Sum('Amount'))['total'] or 0)
        opening_balance = opening_purchases - opening_payments

        fuel_summary = []
        fuel_agg = purchases_qs.values('Fuel__name').annotate(
            total_qty=Sum('qty'),
            total_amount=Sum('trn_amo'),
        )
        for fa in fuel_agg:
            qty = float(fa.get('total_qty') or 0)
            amount = float(fa.get('total_amount') or 0)
            fuel_summary.append({
                'fuel': fa.get('Fuel__name') or '',
                'qty': qty,
                'amount': amount,
                'avg_price': amount / qty if qty else 0
            })

        payments_summary = []
        for p in payments_qs.order_by('pk'):
            payments_summary.append({
                'date': p.tarehe,
                'account': p.Akaunt.Akaunt_name if p.Akaunt else p.kwenda,
                'amount': float(getattr(p, 'Amount', 0) or 0)
            })

        txs = []
        if opening_balance != 0:
            date_val = tFr_dt if isinstance(tFr_dt, datetime.datetime) else parse_dt(tFr)
            txs.append({
                'st': trsp_obj.pk if trsp_obj else 0,
                'pay': False,
                'use': False,
                'opening': True,
                'date': date_val,
                'type': 'Kianzio' if useri.langSet == 0 else 'Opening',
                'station': trsp_obj.jina if trsp_obj else '',
                'details': '',
                'driver': '',
                'vehicle': '',
                'recorded_by': '',
                'fuel_price': 0,
                'qty': 0,
                'amount': opening_balance,
                'fuelN': ''
            })

        for item in purchases_qs.select_related('pu', 'pu__vendor', 'Fuel', 'pu__record_by', 'pu__record_by__user', 'puAttach', 'puAttach__transp').order_by('pu__date', 'pu__pk', 'pk'):
            purchase = item.pu
            if purchase is None:
                continue

            recorded_by = ''
            if purchase.record_by and hasattr(purchase.record_by, 'user') and purchase.record_by.user is not None:
                recorded_by = f"{purchase.record_by.user.first_name} {purchase.record_by.user.last_name}".strip()

            fuel_name = item.Fuel.name if item.Fuel else ''
            qty = float(item.qty or 0)
            amount = float(item.trn_amo or 0)
            unit_price = amount / qty if qty else 0

            vehicle = ''
            driver = ''
            transporter_name = ''
            if item.puAttach is not None:
                vehicle = item.puAttach.vihecle or ''
                driver = item.puAttach.driver or ''
                if item.puAttach.transp is not None:
                    transporter_name = item.puAttach.transp.jina or ''

            txs.append({
                'st': item.puAttach.transp.pk if item.puAttach and item.puAttach.transp else 0,
                'pay': False,
                'use': True,
                'opening': False,
                'date': purchase.date,
                'type': 'Safari' if useri.langSet == 0 else 'Trip',
                'station': purchase.vendor.jina if purchase.vendor else '',
                'details': purchase.code or purchase.ref or '',
                'transporter': transporter_name,
                'driver': driver,
                'vehicle': vehicle,
                'recorded_by': recorded_by,
                'fuel_price': unit_price,
                'qty': qty,
                'amount': amount,
                'fuelN': fuel_name
            })

        for p in payments_qs.order_by('tarehe', 'pk'):
            recorded_by = ''
            if p.by and getattr(p.by, 'user', None):
                recorded_by = f"{p.by.user.first_name} {p.by.user.last_name}".strip()

            payment_amount = float(getattr(p, 'Amount', 0) or 0)
            txs.append({
                'st': p.trsp_bill.pk if p.trsp_bill else 0,
                'pay': True,
                'use': False,
                'opening': False,
                'date': p.tarehe,
                'type': 'LipA' if useri.langSet == 0 else 'Pay',
                'station': p.trsp_bill.jina if p.trsp_bill else '',
                'details': p.Akaunt.Akaunt_name if p.Akaunt else p.kwenda,
                'transporter': p.trsp_bill.jina if p.trsp_bill else '',
                'driver': '',
                'vehicle': '',
                'recorded_by': recorded_by,
                'fuel_price': 0,
                'qty': 0,
                'amount': payment_amount,
                'payment_amount': payment_amount,
                'fuelN': ''
            })

        txs_sorted = sorted(txs, key=lambda x: x.get('date') or datetime.datetime.min)

        running_balance = float(opening_balance)
        transactions = []
        for t in txs_sorted:
            amt = float(t.get('amount') or 0)
            debt = 0.0
            credit = 0.0

            if t.get('opening'):
                running_balance = amt
                if amt >= 0:
                    debt = amt
                else:
                    credit = abs(amt)
            elif t.get('use'):
                debt = amt
                running_balance += debt
            elif t.get('pay'):
                credit = float(t.get('payment_amount') or amt or 0)
                running_balance -= credit

            transactions.append({
                'st': t.get('st'),
                'pay': t.get('pay'),
                'use': t.get('use'),
                'opening': t.get('opening'),
                'date': t.get('date'),
                'type': t.get('type'),
                'station': t.get('station'),
                'details': t.get('details'),
                'transporter': t.get('transporter'),
                'driver': t.get('driver'),
                'vehicle': t.get('vehicle'),
                'recorded_by': t.get('recorded_by'),
                'fuel_price': t.get('fuel_price'),
                'qty': t.get('qty'),
                'amount': amt,
                'credit': credit,
                'debt': debt,
                'balance': running_balance,
                'fuelN': t.get('fuelN'),
            })

        kituo = 'Wote' if useri.langSet == 0 else 'All Transporters'
        if trsp_obj is not None:
            kituo = trsp_obj.jina

        return JsonResponse({
            'success': True,
            'kituo': kituo,
            'fuel_summary': fuel_summary,
            'payments_summary': payments_summary,
            'transactions': transactions,
        }, safe=True)

    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(err)
        })



@login_required(login_url='login')
def vendorStatementData(request):
    try:
        ven = int(request.POST.get('vendor', request.GET.get('vendor', 0)) or 0)
        tFr = request.POST.get('tFr', request.GET.get('tFr', ''))
        tTo = request.POST.get('tTo', request.GET.get('tTo', ''))

        todo = todoFunct(request)
        kampuni = todo['kampuni']
        useri = todo['useri']
        vendor_obj = None

        if ven:
            vendor_obj = wasambazaji.objects.filter(pk=ven, compan=kampuni.id).first()

        def parse_dt(value):
            if not value:
                return None
            if isinstance(value, str):
                dt = parse_datetime(value)
                if dt:
                    return dt
                try:
                    return datetime.datetime.fromisoformat(value)
                except Exception:
                    return None
            return value

        tFr_dt = parse_dt(tFr)
        tTo_dt = parse_dt(tTo)

        purchases_qs = PuList.objects.filter(
            pu__record_by__company=kampuni.id,
            pu__vendor__compan=kampuni.id,
        )
        payments_qs = toaCash.objects.filter(Akaunt__isnull=False, bill__isnull=False, Interprise__company=kampuni, bill__compan=kampuni.id)

        if vendor_obj is not None:
            purchases_qs = purchases_qs.filter(pu__vendor=vendor_obj)
            payments_qs = payments_qs.filter(bill=vendor_obj)

        before_purchases_qs = purchases_qs
        before_payments_qs = payments_qs

        if tFr_dt is not None:
            purchases_qs = purchases_qs.filter(pu__date__gte=tFr_dt)
            payments_qs = payments_qs.filter(tarehe__gte=tFr_dt)
            before_purchases_qs = before_purchases_qs.filter(pu__date__lt=tFr_dt)
            before_payments_qs = before_payments_qs.filter(tarehe__lt=tFr_dt)

        if tTo_dt is not None:
            purchases_qs = purchases_qs.filter(pu__date__lte=tTo_dt)
            payments_qs = payments_qs.filter(tarehe__lte=tTo_dt)

        opening_purchases = float(before_purchases_qs.aggregate(total=Sum(F('qty') * F('cost')))['total'] or 0)
        opening_payments = float(before_payments_qs.aggregate(total=Sum('Amount'))['total'] or 0)
        opening_balance = opening_purchases - opening_payments

        fuel_summary = []
        fuel_agg = purchases_qs.values('Fuel__name').annotate(
            total_qty=Sum('qty'),
            total_amount=Sum(F('qty') * F('cost')),
        )
        for fa in fuel_agg:
            qty = float(fa.get('total_qty') or 0)
            amount = float(fa.get('total_amount') or 0)
            fuel_summary.append({
                'fuel': fa.get('Fuel__name') or '',
                'qty': qty,
                'amount': amount,
                'avg_price': amount / qty if qty else 0
            })

        payments_summary = []
        for p in payments_qs.order_by('pk'):
            payments_summary.append({
                'date': p.tarehe,
                'account': p.Akaunt.Akaunt_name if p.Akaunt else p.kwenda,
                'amount': float(getattr(p, 'Amount', 0) or 0)
            })

        txs = []
        if opening_balance != 0:
            date_val = tFr_dt if isinstance(tFr_dt, datetime.datetime) else parse_dt(tFr)
            if date_val is None and isinstance(tFr, str):
                try:
                    date_val = datetime.datetime.fromisoformat(tFr)
                except Exception:
                    date_val = tFr

            txs.append({
                'st': vendor_obj.pk if vendor_obj else 0,
                'pay': False,
                'use': False,
                'opening': True,
                'date': date_val,
                'type': 'Kianzio' if useri.langSet == 0 else 'Opening',
                'station': vendor_obj.jina if vendor_obj else '',
                'details': '',
                'driver': '',
                'vehicle': '',
                'recorded_by': '',
                'fuel_price': 0,
                'qty': 0,
                'amount': opening_balance,
                'fuelN': ''
            })

        for item in purchases_qs.select_related('pu', 'pu__vendor', 'Fuel', 'pu__record_by', 'pu__record_by__user', 'puAttach', 'puAttach__transp').order_by('pu__date', 'pu__pk', 'pk'):
            purchase = item.pu
            if purchase is None:
                continue

            recorded_by = ''
            if purchase.record_by:
                if hasattr(purchase.record_by, 'user') and purchase.record_by.user is not None:
                    recorded_by = f"{purchase.record_by.user.first_name} {purchase.record_by.user.last_name}".strip()
                else:
                    recorded_by = str(purchase.record_by)

            fuel_name = item.Fuel.name if item.Fuel else ''
            unit_price = float(item.cost or 0)
            qty = float(item.qty or 0)
            amount = unit_price * qty
            vehicle = ''
            driver = ''
            transporter_name = ''
            if item.puAttach is not None:
                vehicle = item.puAttach.vihecle or ''
                driver = item.puAttach.driver or ''
                if item.puAttach.transp is not None:
                    transporter_name = item.puAttach.transp.jina or ''

            txs.append({
                'st': purchase.vendor.pk if purchase.vendor else 0,
                'pay': False,
                'use': True,
                'opening': False,
                'date': purchase.date,
                'type': 'Manunuzi' if useri.langSet == 0 else 'Purchase',
                'station': purchase.vendor.jina if purchase.vendor else '',
                'details': purchase.code or purchase.ref or '',
                'transporter': transporter_name,
                'driver': driver,
                'vehicle': vehicle,
                'recorded_by': recorded_by,
                'fuel_price': unit_price,
                'qty': qty,
                'amount': amount,
                'fuelN': fuel_name
            })

        for p in payments_qs.order_by('tarehe', 'pk'):
            recorded_by = ''
            if p.by:
                user_obj = getattr(p.by, 'user', None)
                if user_obj:
                    recorded_by = f"{user_obj.first_name} {user_obj.last_name}".strip()

            payment_amount = float(getattr(p, 'Amount', 0) or 0)

            txs.append({
                'st': p.bill.pk if p.bill else 0,
                'pay': True,
                'use': False,
                'opening': False,
                'date': p.tarehe,
                'type': 'LipA' if useri.langSet == 0 else 'Pay',
                'station': p.bill.jina if p.bill else '',
                'details': p.Akaunt.Akaunt_name if p.Akaunt else p.kwenda,
                'transporter': '',
                'driver': '',
                'vehicle': '',
                'recorded_by': recorded_by,
                'fuel_price': 0,
                'qty': 0,
                'amount': payment_amount,
                'payment_amount': payment_amount,
                'fuelN': ''
            })

        txs_sorted = sorted(txs, key=lambda x: x.get('date') or datetime.datetime.min)

        running_balance = float(opening_balance)

        transactions = []
        for t in txs_sorted:
            amt = float(t.get('amount') or 0)
            debt = 0.0
            credit = 0.0

            if t.get('opening'):
                running_balance = amt
                if amt >= 0:
                    debt = amt
                else:
                    credit = abs(amt)
            elif t.get('use'):
                debt = amt
                running_balance += debt
            elif t.get('pay'):
                credit = float(t.get('payment_amount') or amt or 0)
                running_balance -= credit

            transactions.append({
                'st': t.get('st'),
                'pay': t.get('pay'),
                'use': t.get('use'),
                'opening': t.get('opening'),
                'date': t.get('date'),
                'type': t.get('type'),
                'station': t.get('station'),
                'details': t.get('details'),
                'transporter': t.get('transporter'),
                'driver': t.get('driver'),
                'vehicle': t.get('vehicle'),
                'recorded_by': t.get('recorded_by'),
                'fuel_price': t.get('fuel_price'),
                'qty': t.get('qty'),
                'amount': amt,
                'credit': credit,
                'debt': debt,
                'balance': running_balance,
                'fuelN': t.get('fuelN'),
            })

        kituo = 'Vyote' if useri.langSet == 0 else 'All Vendors'
        if vendor_obj is not None:
            kituo = vendor_obj.jina

        attachments_qs = attachments.objects.filter(
            puAttach__isnull=False,
            purchase__record_by__company=kampuni.id,
        ).exclude(file='').select_related('purchase', 'purchase__vendor', 'puAttach')

        if vendor_obj is not None:
            attachments_qs = attachments_qs.filter(purchase__vendor=vendor_obj)

        if tFr_dt is not None:
            attachments_qs = attachments_qs.filter(purchase__date__gte=tFr_dt)
        if tTo_dt is not None:
            attachments_qs = attachments_qs.filter(purchase__date__lte=tTo_dt)

        attachments_list = []
        invoice_count = 0
        receipt_count = 0

        for att in attachments_qs.order_by('purchase__date', 'pk'):
            is_receipt = bool(att.receipt)
            is_invoice = bool(att.puInvo)
            if not is_receipt and not is_invoice:
                continue
            if is_invoice:
                invoice_count += 1
            if is_receipt:
                receipt_count += 1

            file_url = ''
            if att.file:
                file_url = request.build_absolute_uri(att.file.url)

            purchase = att.purchase
            attachments_list.append({
                'id': att.id,
                'url': file_url,
                'receipt': is_receipt,
                'invoice': is_invoice,
                'type': 'invoice' if is_invoice else 'receipt',
                'purchase_code': purchase.code if purchase else '',
                'purchase_id': purchase.id if purchase else 0,
                'date': purchase.date.isoformat() if purchase and purchase.date else (att.date.isoformat() if att.date else ''),
                'vendor': purchase.vendor.jina if purchase and purchase.vendor else '',
                'attach_name': att.attach_name or '',
            })

        data = {
            'success': True,
            'kituo': kituo,
            'fuel_summary': fuel_summary,
            'payments_summary': payments_summary,
            'transactions': transactions,
            'attachments': attachments_list,
            'attachment_counts': {
                'invoices': invoice_count,
                'receipts': receipt_count,
            },
        }

        return JsonResponse(data, safe=True)

    except Exception as err:
        print(err)
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(err)
        })


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
        deni_count = sum(1 for item in vend if item['deni'] > 0)
        todo.update({
            'vendors':vend,
            'isVendor':1,
            'madeni':madeni,
            'deni_count': deni_count
        })
       
        return render(request,'vendors.html',todo)
  else:
      return redirect('/userdash')
  
@login_required(login_url='login')
def transporters(request):
  todo = todoFunct(request)
  useri = todo['useri']
  if useri.admin or (useri.ceo and useri.pu):
        kampuni = todo['kampuni']
        transport = transporter.objects.filter(compan = kampuni.id).order_by('-pk')
        vend = []
        madeni = 0
        for v in transport:
            denitr = PuList.objects.filter(puAttach__transp=v.id)
            deni = denitr.aggregate(sumi=Sum(F('trn_amo')-F('trn_paid')))['sumi'] or 0
            vend.append({
                'ven':v,
                'deni':deni
            })
            madeni += deni
            
        todo.update({
            'transport':vend,
            'isTranspoter':1,
            'madeni':madeni
        })
        return render(request,'vendortransport.html',todo)
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
                    trsp = transporter.objects.get(pk=rec['transporter'],compan=kampuni)

                    vihePu = puAttachments.objects.filter(purchase=pu,vihecle=rec['vehicle'])
                    vAtt = None
                    if not vihePu.exists():
                        vAtt = puAttachments()
                        vAtt.purchase = pu
                        vAtt.vihecle = rec['vehicle']
                        vAtt.driver = rec['driver']
                        vAtt.transp = trsp
                        vAtt.save()
                    else:
                        vAtt = vihePu.last()
                    pL = PuList()
                    fl = fuel.objects.get(pk=rec['fuel'])
                    pL.pu = pu
                    
                   
                    pL.trn_amo = rec['charges']
                    pL.cost = float(rec['puPr'])
                    pL.qty = float(rec['puQty'])
                    pL.Fuel = fl
                    pL.puAttach = vAtt
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
        except Exception as err:
             print(err)
             traceback.print_exc()  
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
                                    break

                    
                        
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
def lipaTransporter(request):
    if request.method == "POST":
        try:
            transp_id = int(request.POST.get('transp', 0))
            ac = int(request.POST.get('acc', 0))
            paid = Decimal(str(request.POST.get('pay', 0) or 0))
            desc = request.POST.get('desc', 'Transporter Payment')

            todo = todoFunct(request)
            kampuni = todo['kampuni']
            useri = todo['useri']

            if not (useri.admin or (useri.ceo and useri.pu)):
                return JsonResponse({
                    'success': False,
                    'swa': 'Hauna ruhusa kwa kitendo hiki tafadhari wasiliana na uongozi',
                    'eng': 'You have no permission for this please contact administration'
                })

            if not transp_id or not ac or paid <= 0:
                return JsonResponse({
                    'success': False,
                    'swa': 'Tafadhali jaza taarifa sahihi za malipo',
                    'eng': 'Please provide valid payment details'
                })

            trsp = transporter.objects.get(pk=transp_id, compan=kampuni)
            toakwa = PaymentAkaunts.objects.get(pk=ac, Interprise__company=kampuni)

            open_lines = PuList.objects.filter(
                puAttach__transp=trsp,
                pu__record_by__company=kampuni,
                trn_amo__gt=F('trn_paid')
            ).order_by('pu__date', 'id')

            daiwa = open_lines.aggregate(sumi=Sum(F('trn_amo') - F('trn_paid')))['sumi'] or Decimal('0')

            if paid > daiwa:
                return JsonResponse({
                    'success': False,
                    'swa': 'Malipo yamezidi deni halisi la msafirishaji',
                    'eng': 'Payment exceeds transporter outstanding debt'
                })

            if Decimal(str(toakwa.Amount)) < paid:
                return JsonResponse({
                    'success': False,
                    'swa': 'Akaunti haina kiasi cha kutosha kulipa',
                    'eng': 'Insufficient account balance for this payment'
                })

            with transaction.atomic():
                lipwa = paid
                for line in open_lines:
                    deni = Decimal(str(line.trn_amo)) - Decimal(str(line.trn_paid))
                    if deni <= 0:
                        continue

                    if deni <= lipwa:
                        line.trn_paid = line.trn_amo
                        lipwa = lipwa - deni
                    else:
                        line.trn_paid = Decimal(str(line.trn_paid)) + lipwa
                        lipwa = Decimal('0')

                    line.save(update_fields=['trn_paid'])
                    if lipwa <= 0:
                        break

                beforetoa = Decimal(str(toakwa.Amount))
                toakwa.Amount = beforetoa - paid
                toakwa.save(update_fields=['Amount'])

                toa = toaCash()
                toa.Akaunt = toakwa
                toa.Amount = paid
                toa.before = beforetoa
                toa.After = toakwa.Amount
                toa.kwenda = "Transporter Payment"
                toa.maelezo = desc or 'Transporter Payment'
                toa.tarehe = datetime.datetime.now(tz=timezone.utc)
                toa.by = useri
                toa.Interprise = toakwa.Interprise
                toa.usiri = toakwa.onesha
                toa.bill = None
                toa.trsp_bill = trsp
                toa.save()

            return JsonResponse({
                'success': True,
                'swa': 'Malipo ya msafirishaji yamehifadhiwa kikamilifu',
                'eng': 'Transporter payment recorded successfully'
            })

        except Exception as err:
            print(err)
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'swa': 'Imeshindwa kuhifadhi malipo ya msafirishaji',
                'eng': 'Failed to record transporter payment'
            })
    else:
        return render(request, 'pagenotFound.html', todoFunct(request))


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
            'rperc':100*rcvd/qty if qty else 0,
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
                'rperc':100*rcvd/qty if qty else 0,
                'rcd':RL,
                'dispatch': RL.exists()
            })
            html = 'venPurchasesView.html'
            pr = int(request.GET.get('t', 0))
            lang = int(request.GET.get('lang', 0))

            if pr:
                todo.update({
                    'langSet': lang
                })
                html = 'venPurchasesPrint.html'

            return render(request, html, todo)
        
        else:
            return redirect('/userdash')


    except Exception as e:
        print(e)
        traceback.print_exc()
        return render(request,'pagenotFound.html')

@login_required(login_url='login')
def deletePurchase(request):
    if request.method == "POST":
        try:
            todo = todoFunct(request)
            useri = todo['useri']
            if useri.admin or (useri.ceo and useri.pu):
                i = int(request.POST.get('pu',0))
                kampuni = todo['kampuni']
                
                pu = Purchases.objects.get(pk=i,vendor__compan=kampuni)
                pu.delete()
                data={
                    'success':True,
                    'swa':'Imefanikiwa kufuta bili',
                    'eng':'Purchase was deleted successfully'
                }
            else:
                data={
                    'success':False,
                    'swa':'Hauna ruhusa kwa kitendo hiki tafadhari wasiliana na uongozi',
                    'eng':'You have no permission for this please contanct administration'
                }
        except Exception as err:
            print(err)
            traceback.print_exc()
            data={
                'success':False,
                'swa':'Imeshindwa kufuta bili',
                'eng':'Failed to delete purchase'
            }
        return JsonResponse(data)
    else:
        return render(request,'pagenotFound.html')


@login_required(login_url='login')
def viewTransporter(request):
    try:
        todo = todoFunct(request)
        useri = todo['useri']
        if useri.admin or (useri.ceo and useri.pu):
            t = int(request.GET.get('t', 0))
            kampuni = todo['kampuni']

            trsp = transporter.objects.get(pk=t, compan=kampuni)
            pu_lines = PuList.objects.filter(puAttach__transp=trsp.id, pu__record_by__company=kampuni)

            leo = datetime.datetime.now().astimezone()
            thisMonth = leo.strftime('%Y-%m-01 00:00:00%z')

            month_lines = pu_lines.filter(pu__date__gte=thisMonth)
            prev_lines = pu_lines.filter(pu__date__lt=thisMonth, trn_paid__lt=F('trn_amo'))

            month_charges = month_lines.aggregate(Amo=Sum('trn_amo'))['Amo'] or 0
            month_paid = month_lines.aggregate(Paid=Sum('trn_paid'))['Paid'] or 0
            month_debt = month_charges - month_paid

            prev_charges = prev_lines.aggregate(Amo=Sum('trn_amo'))['Amo'] or 0
            prev_paid = prev_lines.aggregate(Paid=Sum('trn_paid'))['Paid'] or 0
            debtprev = prev_charges - prev_paid

            month_attach_qs = puAttachments.objects.filter(
                transp=trsp.id,
                purchase__record_by__company=kampuni,
                purchase__date__gte=thisMonth
            ).order_by('-purchase__date', '-pk')

            prev_attach_qs = puAttachments.objects.filter(
                transp=trsp.id,
                purchase__record_by__company=kampuni,
                purchase__date__lt=thisMonth
            ).order_by('-purchase__date', '-pk')

            month_trips = []
            for att in month_attach_qs:
                att_lines = PuList.objects.filter(puAttach=att.id)
                qty = att_lines.aggregate(sumi=Sum('qty'))['sumi'] or 0
                charges = att_lines.aggregate(sumi=Sum('trn_amo'))['sumi'] or 0
                paid = att_lines.aggregate(sumi=Sum('trn_paid'))['sumi'] or 0
                month_trips.append({
                    'att': att,
                    'qty': qty,
                    'charges': charges,
                    'paid': paid,
                    'debt': charges - paid,
                })

            prev_trips = []
            for att in prev_attach_qs:
                att_lines = PuList.objects.filter(puAttach=att.id)
                qty = att_lines.aggregate(sumi=Sum('qty'))['sumi'] or 0
                charges = att_lines.aggregate(sumi=Sum('trn_amo'))['sumi'] or 0
                paid = att_lines.aggregate(sumi=Sum('trn_paid'))['sumi'] or 0
                debt = charges - paid
                if debt > 0:
                    prev_trips.append({
                        'att': att,
                        'qty': qty,
                        'charges': charges,
                        'paid': paid,
                        'debt': debt,
                    })

            payacc = PaymentAkaunts.objects.filter(Interprise__company=kampuni)
            trsp_payments = toaCash.objects.filter(
                Interprise__company=kampuni,
                trsp_bill=trsp
            ).order_by('-tarehe', '-id')[:50]

            todo.update({
                'isTranspoter': 1,
                'isViewTransporter': 1,
                'trips_tab': 1,
                'thereisTrsp': 1,
                'trsp': trsp,
                'month_trips': month_trips,
                'month_trips_len': len(month_trips),
                'prev_trips': prev_trips,
                'prev_trips_len': len(prev_trips),
                'month_charges': month_charges,
                'month_paid': month_paid,
                'month_debt': month_debt,
                'debtprev': debtprev,
                'total_debt': debtprev + month_debt,
                'payacc': payacc,
                'trsp_payments': trsp_payments,
                'trsp_payments_len': len(trsp_payments),
            })

            return render(request, 'transporterView.html', todo)
        else:
            return redirect('/userdash')
    except Exception as err:
        print(err)
        traceback.print_exc()
        return render(request, 'pagenotFound.html', todoFunct(request))


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

            trnsp = transporter.objects.filter(compan=kampuni,active=True)
            
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
                    'rperc':100*rcvd/qty if qty else 0,
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
                    'rperc':100*rcvd/qty if qty else 0,
                })
        
        
            todo.update({
                'allfuel':TheFuel,
                'isVendor':1,
                'isViewVend':1,
                
                'ven':vendor,

                'sale':montBill,
                'saleLen':len(montBill),
                'totAmo':totAmo,
                'bakiM':debt,
                'baki':baki,
                'paid':paid,
                 'trnsp':trnsp,
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
    except Exception as err:
        print(err)
        traceback.print_exc()
        return render(request,'pagenotFound.html',todoFunct(request))

@login_required(login_url='login')
def addTransporter(request):
     if request.method == "POST":
        try: 
            #  intp= InterprisePermissions.objects.get(user__user=request.user,default=True)
             todo = todoFunct(request)
             useri = todo['useri']
             cheo = todo['cheo']
             admin = todo['admin']
             if useri.admin:  
                name=request.POST.get('name')
                address=request.POST.get('address')
                code=request.POST.get('code1')
                simu1=request.POST.get('phone1')
                simu2=request.POST.get('phone2')
                mail=request.POST.get('mail')
                isActive=int(request.POST.get('isActive',1))
                value=request.POST.get('value')
                edit=int(request.POST.get('edit',0))
                valued=int(request.POST.get('valued',0))

                kampuni = todo['kampuni']

                if not useri.admin:
                    data = {
                        'success':False,
                        'swa':'Hauna ruhusa ya kitendo hiki tafadhari wasiliana na uongozi',
                        'eng':'You have no permission on this please contact admin'
                    }

                    return JsonResponse(data)

                transp=transporter()
                trsp = transporter.objects.filter(pk=valued)
                if edit and trsp.exists():
                    transp = trsp.last()

                transp.jina = name
                transp.address = address
                transp.code = code
                transp.simu1 = simu1
                transp.simu2 = simu2
                transp.email = mail
                transp.active = bool(isActive)
                transp.compan = kampuni
                    
                if transporter.objects.filter(simu1=simu1,compan=kampuni).exists() and not edit:
                    data={
                        'success':False,
                        'swa':'Tayari kuna Msambazaji mwingine mwenye jina kama hili kama ni mwinginae unaweza kubadili jina au ondoa taarifa za Msambazaji zilizowekwa awali',
                        'eng':'The same  Supplier name  exists you can change the name or remove the previos saved Supplier details'
                    
                    }

                else:
                    transp.save()    
                    data={
                        'success':True,
                        'swa':'Taarifa za Msambazaji zimehifadhiwa kikamilifu',
                        'eng':'new Supplier added successfully',
                        'id':transp.id
                    }
                return JsonResponse(data)  
             else:
                 data={
                     'success':False,
                     'swa':'Hauna ruhusa ya kuongeza Msambazaji kwa sasa tafadhari wasiliana na uongozi wako kupata ruhusa',
                     'eng':'You have no permission to add Supplier please contact your administrator',
                 } 
                 return JsonResponse(data)    
        except Exception as err :
             print(err)
             traceback.print_exc()
             data={
                 'success':False,
                 'swa':'Taarifa za Msambazaji hazijahifadhiwa kutokana na hitilafu. tafadhari jaribu tena kuweka data kwa usahihi',
                 'eng':'Supplier info was not successfully saved. Please try again to fill correct Supplier informations'
             }
             return JsonResponse(data)          
     else:
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
                isActive=int(request.POST.get('isActive',0))
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
                
                if edit:
                    teja.active = bool(isActive)
                    
                if wasambazaji.objects.filter(simu1=simu1,compan=kampuni).exists() and not edit:
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
        manager = todo['manager']
        if useri.admin or manager:
            pu = Purchases.objects.get(pk=i,record_by__company=kampuni) 
            PL = PuList.objects.filter(pu=pu,qty__gt=F('rcvd')).select_related('puAttach', 'puAttach__transp', 'Fuel')
            Intp = Interprise.objects.filter(company=kampuni)
           

            tanks = fuel_tanks.objects.filter(Interprise__company=kampuni)
            tr_tank = tanks.filter(moving=True)
            shell_tanks = tanks.filter(moving=False)

            tankContainer = tr_tank.distinct('tank')
        
            tanksSup = InterprisePermissions.objects.filter(Interprise__company=kampuni,user__tankSup=True)

            transporter_map = {}
            driver_seen = set()
            vehicle_seen = set()
            trip_drivers = []
            trip_vehicles = []

            for line in PL:
                att = line.puAttach
                if att is None:
                    continue

                tr = att.transp
                tr_id = tr.id if tr is not None else 0
                tr_name = tr.jina if tr is not None else ''
                driver = (att.driver or '').strip()
                vehicle = (att.vihecle or '').strip()

                if tr_id not in transporter_map:
                    transporter_map[tr_id] = {
                        'transpoter_id': tr_id,
                        'name': tr_name,
                        'vihecles': []
                    }

                transporter_entry = transporter_map[tr_id]
                if not any(v.get('puAttach_id') == att.id for v in transporter_entry['vihecles']):
                    transporter_entry['vihecles'].append({
                        'trasp_id': tr_id,
                        'driver': driver,
                        'vehicle': vehicle,
                        'puAttach_id': att.id
                    })

                if driver:
                    drv_key = (tr_id, driver)
                    if drv_key not in driver_seen:
                        driver_seen.add(drv_key)
                        trip_drivers.append({
                            'transpoter_id': tr_id,
                            'driver': driver
                        })

                if vehicle:
                    veh_key = (tr_id, vehicle)
                    if veh_key not in vehicle_seen:
                        vehicle_seen.add(veh_key)
                        trip_vehicles.append({
                            'transpoter_id': tr_id,
                            'vehicle': vehicle
                        })

            trip_transporters = sorted(
                transporter_map.values(),
                key=lambda x: (x.get('name') or '').lower()
            )


            todo.update({
                'isreceive':True,
                 'trf':pu,
                 'list':PL,
                'Intp':Intp,
                'shell_tanks':shell_tanks,
                'tr_tank':tr_tank,
                'isPu':True,
                'tanksSup':tanksSup,
                'tankContainer':tankContainer,
                'trip_transporters': trip_transporters,
                'trip_drivers': trip_drivers,
                'trip_vehicles': trip_vehicles,
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
            elif prefix == 'SHF' or prefix == 'SHIFT' or prefix == 'SHFT' or prefix == 'SH':
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

def priveiw(request): 
    todo = todoFunct(request)
    return render(request,'test.html',todo)