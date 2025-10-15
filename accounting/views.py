from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from account.models import UserExtend,shifts,shiftPump,fuel_pumps,matumizi,rekodiMatumizi,wekaCash,toaCash,PhoneMailConfirm,wateja,wasambazaji,Interprise,InterprisePermissions,PaymentAkaunts,staff_akaunt_permissions
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db.models import F
from django.core import serializers
from django.db.models import Q
from django.core.paginator import Paginator,EmptyPage

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
def pdcBillsView(request):
    try:
        i = int(request.GET.get('i',0))
        todo = todoFunct(request)
        kampuni = todo['kampuni']
        exp = matumizi.objects.get(pk=i,owner__company=kampuni)
        todo.update({
            'exp':exp,
            'isPdBills':True

        }) 

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
  pbills = matumizi.objects.filter(owner__company=kampuni,duration__gt=0) 
  if not general:
      pbills = pbills.filter(shell=shell)

  todo.update({
     'stations':stations,
    #   'payacc':payacc,
      'pbills':pbills,
      'isPdBills':True
  })
  return render(request,'paypdcBills.html',todo)

@login_required(login_url='login')
def payaccounts(request):
  todo = todoFunct(request)
  general = todo['general']
  kampuni = todo['kampuni']
  stations = None
  if general:
     stations = Interprise.objects.filter(company = kampuni)


  AccSum = todo['payacc'].aggregate(sumi=Sum('Amount'))['sumi'] or 0

  todo.update({
      'stations':stations,
    #   'payacc':payacc,
      'AccSum':AccSum,
      'isAkaunti':True
  })
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
    
            todo = todoFunct(request)
            kampuni = todo['kampuni']
            admin = todo['admin']
            theShell = None
            if not is_general:
                theShell = Interprise.objects.get(pk=station,company=kampuni)

            Eexp = matumizi.objects.filter(matumizi__icontains=name,shell=theShell,owner__company=kampuni)   

            data = {
                'success':True,
                'swa':'Bili imehifadhiwa kikamilifu',
                'eng':'Bill added successfully'
            }

            if not Eexp.exists():
                exp = matumizi()
                exp.matumizi = name
                exp.owner = admin
                exp.period_type = Period
                exp.general = is_general
                exp.amount = amount
                exp.duration = dura
                exp.shell = theShell
                exp.depends = it_depends
                exp.next_pay = nextPay
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
            idn= request.POST.get('value')
            todo = todoFunct(request)
            cheo = todo['cheo']

            

           

            
            if idn !='':
                
                ak = PaymentAkaunts.objects.get(pk=idn ) 
                #  ak.Interprise = InterprisePermissions.objects.get(user=request.user.id, default=True).Interprise
                ak.Akaunt_name = name
                # ak.Amount = int(amount)
                ak.onesha = allow
                ak.aina = aina

                ak.save()

                data={
                    'success':True
                }

                return JsonResponse(data) 


            else: 
                data={
                    'success':False
                }

                return JsonResponse(data)
        else:
          return render(request,'pagenotFound.html',todoFunct(request))         
    except:
        data={
            'success':False
        }

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
            amounti= int(request.POST.get('kiasi'))
            baki= int(request.POST.get('baki'))
            acid= int(request.POST.get('is'))
            todo = todoFunct(request)
            cheo = todo['cheo']
            useri = todo['useri']
            admin = todo['admin']
            manager = todo['manager']
            #  kuapdate inapoenda
            if manager or useri.admin : 
                # entp=cheo.Interprise
                toakwa= PaymentAkaunts.objects.get(pk=acid)
                beforweka=toakwa.Amount
                akaunti = toakwa # Initialize the other destination account ...............//
                if ac:
                    akaunti=PaymentAkaunts.objects.get(pk=idn)

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
                toa.makato = beforweka-(baki+amounti)
                toa.tarehe = datetime.datetime.now(tz=timezone.utc)
                toa.by=useri
                toa.Interprise=toakwa.Interprise
                toa.kuhamisha = ac  
                toa.personal = not ac  
                toa.kuhamishaNje =  akaunti.Interprise is not toakwa.Interprise
                toa.save()

                toakwa.Amount = float(baki)
                toakwa.save()

                # kuapdate inapotoka
                if ac:
                    before=akaunti.Amount
                    PaymentAkaunts.objects.filter(pk=idn).update(Amount=F('Amount')+amounti)

                    #  akaunti.kiasi=akaunti.Amount-amounti
                    #  akaunti.save()

                    Change=wekaCash()
                    Change.Akaunt=akaunti
                    Change.Amount = amounti
                    Change.before=before
                    Change.After=before + amounti
                    Change.kutoka= PaymentAkaunts.objects.get(pk=acid, Interprise__owner=admin.id).Akaunt_name
                    Change.maelezo = eleza
                    Change.tarehe = datetime.datetime.now(tz=timezone.utc)
                    Change.by=todoFunct(request)['useri']
                    Change.Interprise=akaunti.Interprise
                    Change.kuhamisha = ac
                    Change.kuhamishaNje =  akaunti.Interprise is not toakwa.Interprise
                    if not PaymentAkaunts.objects.get(pk=idn, Interprise__owner=admin.id).onesha:
                        Change.usiri = True
                    if not toakwa.onesha:
                        Change.kutoka_siri = True    
                    Change.save()

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
        except:
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

        return render(request,'payawithdraw.html',todo)

    except:
        return render(request,'pagenotFound.html')


@login_required(login_url='login')
def addExpense(request):
      if request.method == "POST":

            try:
                  data={
                        'success':True,
                        'message_eng':'Expense was saved successfully',
                        'message_swa':'matumizi yamerekodiwa kikamilifu'
                        
                       }  
                            
                  bil = request.POST.get('bill')
                  mpya = int(request.POST.get('mpya'))
                  name = request.POST.get('name')
                  tumi = request.POST.get('select')
                  amo = float(request.POST.get('amo'))
                  bal = int(request.POST.get('bak'))
                  kwa = request.POST.get('kwa')
                  bal_set = int(request.POST.get('bal_set'))
                  ac = request.POST.get('ac')
                  maelezo = request.POST.get('maelezo')
                  opt = int(request.POST.get('opt'))
                  pump = int(request.POST.get('pump'))
                  isfuel = int(request.POST.get('fuel'))
                  
                  todo=todoFunct(request)
                #   duka=todo['duka']
                  useri = todo['useri']
                  cheo = todo['cheo']
                  admin = todo['admin']
                  paid = amo
                  shell = todo['shell']

                  

                  if useri.admin or cheo is not None :  
                        matum = None
                        if  mpya:
                                # print('new')
                                if matumizi.objects.filter(matumizi__istartswith=name,owner=admin).exists():
                                    matum = matumizi.objects.filter(matumizi__istartswith=name,owner=admin).last()
                                else:
                                        matum = matumizi()
                                        matum.owner = admin
                                        matum.matumizi = name
                                        matum.save()
                                        
                        else:
                                # print('old')
                                matum = matumizi.objects.get(pk=tumi,owner=admin) 
                        # print(matum.id)
                        rec = rekodiMatumizi()
                        rec.Interprise=shell
                        rec.matumizi = matum 
                        # if is_bill:         
                        #       rec.manunuzil = True  
                        #       bill =  manunuzi.objects.get(pk=bil,Interprise=duka.id)         
                        #       rec.manunuzi_id = bill        
                        #       manunuzi.objects.filter(pk=bil,Interprise=duka.id).update(amount=F('amount')+float(amo),ilolipwa=F('ilolipwa')+float(amo)) 

                        rec.tarehe = datetime.datetime.now(tz=timezone.utc)
                        rec.kiasi = float(amo)
                        rec.by = useri
                        rec.kabidhiwa = kwa
                        rec.maelezo = maelezo
                        rec.date = date.today()
                        rec.save()
                        if opt == 1:
                            sh_pump = fuel_pumps.objects.get(pk=pump,tank__Interprise=cheo.Interprise)
                            shiftP = shiftPump.objects.filter(pump=sh_pump,shift__To=None)
                            shift = shiftP.last()
                            rec.fromShift = shift
                            if isfuel:
                               fuel_cost = float(sh_pump.tank.price)   
                               Fqty =   paid/fuel_cost
                               rec.kiasi = float(amo)

                               rec.fuel_qty = float(Fqty)

                               rec.fuel_cost = float(sh_pump.tank.cost)
                               rec.fuel_price  = fuel_cost   
                               rec.Fuel = sh_pump.tank.fuel
                      
                        if opt == 2:
                            acc =   PaymentAkaunts.objects.get(pk=ac)   
                            duka = acc.Interprise
 

                            desk = matum.matumizi + '('+ maelezo +')' 

                            rec.akaunti=acc

                            toakwa= acc
                            beforweka=toakwa.Amount 
                
                            toa = toaCash()
                            toa.Akaunt = toakwa
                            toa.Amount = paid
                            toa.matumizi = rec
                            toa.before = beforweka
                            if bool(bal_set):
                                bal = int(bal)
                                toa.After = bal 
                                toa.makato = beforweka-(bal+paid)
                
                            else :
                                toa.After = float(beforweka) - paid 
                                toa.makato = 0
                                                    
                            toa.kwenda = matum.matumizi
                            toa.maelezo = desk
                            toa.tarehe = datetime.datetime.now(tz=timezone.utc)
                            toa.by=useri
                            toa.Interprise=duka
                            toa.pu=True
                            # if is_bill:
                            #       toa.bill = bill
                            if not toakwa.onesha:
                                toa.usiri =True 
                
                            if paid <=  beforweka :  
                              if bool(bal_set): 
                                    toakwa.Amount =  bal
                              else:
                                    toakwa.Amount = float(toakwa.Amount) - paid
            
                              toakwa.save()              
                              toa.save() 
                        rec.save()         
                      
                  else:
                        data={
                             'success':False,
                        'message_eng':'You have no permission to add expenses',
                        'message_swa':'Hauna ruhusa ya kuongeza matumizi'
                  
                        }            

                  return JsonResponse(data)
            except:
                  data={
                        'success':False,
                        'message_eng':'Expense was not seved please try again',
                        'message_swa':'matumizi hayakurekodiwa kutokana na hitilafu tafadhhari jaribu tena kwa usahihi'
                  }

                  return JsonResponse(data)      
      else:
           return render(request,'pagenotFound.html',todoFunct(request))

