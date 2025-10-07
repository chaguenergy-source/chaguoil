import os
from pathlib import Path
from django.shortcuts import render,redirect
from .models import UserExtend,PhoneMailConfirm,company,notifications,Interprise,InterprisePermissions,PaymentAkaunts,staff_akaunt_permissions
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
from django.core.paginator import Paginator,EmptyPage
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



from .todos import Todos,confirmMailF
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


def todoFunct(request):
  usr = Todos(request)
  return usr.todoF()


def login(request):
   if request.user.is_authenticated:
    #  u=User.objects.get(pk = request.user.id)
    #  u.last_login = datetime.datetime.now(tz=timezone.utc)
    #  u.save()
     return redirect('userdash')
   else:  
    
    if request.method== 'POST':
      try:
        email= request.POST.get('email') 
        password= request.POST['password']  
        val= int(request.POST.get('lang',1))
        code = int(request.POST.get('code',0))
        
        user = auth.authenticate(username=email, password=password)

       
        if user is not None:
 
          Sessions = Session.objects.all()
          otherLog = 0
          for row in Sessions:
              if str(row.get_decoded().get("_auth_user_id")) == str(user.id):
                  # print('Same sessions')
                  if code == 0:
                     otherLog = 1
                  else:   
                     mail = PhoneMailConfirm.objects.get(PhoneMail__icontains=email,code=code,duration__gte=datetime.datetime.now(tz=timezone.utc))
                     row.delete()
          # request.session['logged'] = user.id     
                  break 
          
          
    
        
          if not otherLog:  
             
            auth.login(request, user) 
            todo = todoFunct(request)
            useri = todo['useri']
            general = todo['general']

            if  useri.admin or useri.ceo or (useri.staff and not general): 
                return redirect("/userdash")
            else:
               return redirect('/logout')
          else:
              conf = PhoneMailConfirm.objects.filter(PhoneMail__icontains=email)
              tm = datetime.datetime.now(tz=timezone.utc) + timedelta(seconds=90)
              randNum = random.randint(10000,99999)
              if conf.exists():
                  conf.update(code=randNum,duration=tm)
              else:
                  conf =  PhoneMailConfirm()
                  conf.PhoneMail = email
                  conf.code = randNum
                  conf.duration = tm
                  conf.save()
              try: 
                confirmMailF({
                  'to':email,
                  'num':randNum
                }) 
              except:
                 pass  

              # print(randNum)
            
              

              todo = {
                  'lang':val,
                  'email':email,
                  'password':password,
                  'confirm':True
              }
              return render(request,'login.html',todo)
        
        else:
            msg = "Invalid credidentials"
            if not val:
              msg="Vitambulisho Havikubaliki"

            messages.error(request, msg)   
            return redirect(f"/?lang={val}")
      except:
        todo = {'lang':int(request.GET.get('lang',1))}
        return render(request,'login.html',todo)  
    else:  
      val= int(request.GET.get('lang',1)) 
      todo = {'lang':val}
     
      return render(request, "login.html",todo)


def register(request):
  users = UserExtend.objects.all()

  if request.user.is_authenticated or users.exists():
     return redirect('userdash')
  else:   
    if request.method == 'POST':
      
      try:
        first_name= request.POST['f_name'] 
        last_name= request.POST['l_name'] 

        mail= request.POST['mail'] 
        password= request.POST['pwd'] 
        city= request.POST['city'] 
        p_code= request.POST['p_code'] 
        address= request.POST['address'] 
        country= request.POST['country'] 
        code = int(request.POST.get('code',0))
        company_name = request.POST.get('company_name', '')
        company_phone1 = request.POST.get('phone1', '')
        company_phone2 = request.POST.get('phone2', '')
        company_email = request.POST.get('company_email', '')

     
        confirm = PhoneMailConfirm.objects.get(PhoneMail__icontains=mail,code=code,duration__gte=datetime.datetime.now(tz=timezone.utc))
        confirm.confirm = True
        confirm.save()

      
        
        if User.objects.filter(email__icontains=mail).exists():
            # messages.error(request,'Namba ya simu uliyoingiza Tayari inatumika !')
            data = {
              'success':False,
              'msg_swa':'Anwani ya barua pepe tayari imeshasajiriwa tafadhari igiza akaunti nyingine',
              'msg_eng':'The email address has already registered taken please use another email address'
            }

            if PhoneMailConfirm.objects.filter(PhoneMail=mail,confirm=False):
              data = {
                'success':True
              }


      
            return JsonResponse(data)

        else:  
          kampuni = company()
          kampuni.jina = company_name
          kampuni.phone = company_phone1
          kampuni.phone2 = company_phone2
          kampuni.email = company_email
          kampuni.address = address
          kampuni.country = country
          kampuni.save()

          user = User.objects.create_user(email=mail,username=mail,first_name=first_name, last_name=last_name, password=password )
          ext = UserExtend()
          # user.save()
          ext.regstatue = 1
          
          ext.user = user
          ext.company = kampuni
          ext.region = city
          ext.country = country
          ext.address = address
          ext.postal = p_code
          ext.admin = True
          ext.cheo = 'Admin'

          ext.save()

          auth.login(request, ext.user)


          data = {
            'success':True,
            'id':ext.id
            }

          return JsonResponse(data)

      except:
          data = {
            'success':False,
            'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena',
            'msg_eng':'The action was not successfully due to error please try again'
          }

          return JsonResponse(data)


    else:

      return render(request, 'register.html')


# Create your views here.

def confirmMail(request):
  if request.method == "POST":
    pwd = int(request.POST.get('pwd',0))
    try:
      mail = request.POST.get('mail',None)
      codeN = int(request.POST.get('code',0))

      if pwd:
         getmail = User.objects.get(email__icontains=mail)
         mail = getmail.email
         

      conf = PhoneMailConfirm.objects.filter(PhoneMail__icontains=mail)
      tm = datetime.datetime.now(tz=timezone.utc) + timedelta(seconds=90)
      randNum = random.randint(10000,99999)
      cnf = {
                   'num':randNum,
                   'to':mail,
                   'code':codeN
            }
      try:
        confirmMailF(cnf)
      except:
        pass  

      dura = None
      if conf.exists():
        conf.update(duration = tm,code = randNum,confirm=False)
        dura = conf.last().duration
      else:
        conf =  PhoneMailConfirm()
        conf.PhoneMail = mail
        conf.code = randNum
        conf.duration = tm
        conf.save()

        dura = conf.duration

      data = {
        'success':True,
        # 'num':randNum,
        'mail':mail,
        'id':dura

      }

      return JsonResponse(data)
 
    except:
      data = {
        'success':False,
        'msg_swa':"Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi",
        'msg_eng':"The action was not successfully please try again correctly"
      }


      return JsonResponse(data)


  else:
    return render(request,'register.html')

def resetpwd(request):
   try:
      usr = int(request.GET.get('usr',0))
      useri = UserExtend.objects.get(pk=usr,pwdResets=True)
      auth.login(request, useri.user)

      return redirect('/passWordResset')

   except:
      return redirect('/login')   

def logout(request):
    # User.objects.all().delete()
    auth.logout(request)
    return redirect('/')


def fogotpwd(request):
   lang = int(request.GET.get('lang'))
   todo = {
    'lang':lang
   }

   return render(request,'foggopwd.html',todo)

def confirmMailPwdFoggot(request):
  if request.method == "POST":
    try:
      mail = request.POST.get('mail')
      code = request.POST.get('code')
 
      confirm=PhoneMailConfirm.objects.get(confirm=False,PhoneMail__icontains=mail,code=code,duration__gte=datetime.datetime.now(tz=timezone.utc))
      confirm.confirm = True
      confirm.save()

      userI = User.objects.get(email__icontains=mail)
      UserExtend.objects.filter(user=userI.id).update(pwdResets=True)
      auth.login(request, userI)

      data = {
        'success':True,
        'msg_swa':'Uhakiki wa namba umefanikiwa kikamilifu',
        'msg_eng':'Verification code confirmed successfully'
      }


      return JsonResponse(data)

    except:
      data = {
        'success':False,
        'msg_eng':'The action was not successfully due to error please try again correctly',
        'msg_swa':'Kitendo hakikufanikiwa tafadhari jaribu tena kwa usahihi'
       
      }
      return JsonResponse(data)       

@login_required(login_url='login')
def changePwd(request):
   try:
      todo = todoFunct(request)
      useri= todo['useri']
      pwd = request.POST.get('pwd')

      data = {
        'success':True,
        'msg_eng':'Password has been reset successfully',
        'msg_eng':'Neno la siri limebadilishwa kikamilifu'
      }     
      if useri.pwdResets:
         userI = useri.user
         userI.set_password(pwd)
         userI.save()

         useri.pwdResets = False
         useri.save()
      else:
        data = {
                'success':False,
                'msg_swa':'Kitendo hakikufanikiwa tafadhari tena kwa usahihi',
                'msg_eng':'Action was not successfully please try again correctly'
              } 
      return JsonResponse(data)
   except:
    data={
      'success':False,
      'msg_swa':'Kitendo hakikufanikiwa tafadhari tena kwa usahihi',
      'msg_eng':'Action was not successfully please try again correctly'
    }
    return JsonResponse(data)
   
@login_required(login_url='login')
def passWordResset(request):
  todo = todoFunct(request)
  lang = int(request.GET.get('lang',0))
  
  useri = todo['useri']
  if useri.pwdResets:
    todo.update({
       'lang':lang
    })
    return render(request,'passReset.html',todo)
  else:
     return redirect('/userdash')
  

@login_required(login_url='login')
def userdash(request):
      #  try:
        todo = todoFunct(request)
        useri = todo['useri']
        

        return render(request, 'home.html',todo)

      #  except:
      #     return render(request, 'pagenotFound.html')

@login_required(login_url='login')
def enterstation(request):
   try:
      shel = int(request.GET.get('sh',0))
      todo = todoFunct(request)
      useri = todo['useri']
      perm = InterprisePermissions.objects.filter(Allow=True,Interprise=shel,user=useri.id)
     
      if perm.exists() or not shel:
         InterprisePermissions.objects.filter(user=useri.id).update(default=False)
         if perm.exists():
            perm.update(default=True)
               
         return redirect('/userdash')
         
      else:
         return redirect('/stations')

   except:
      return render(request,'pagenotFound.html')
   
@login_required(login_url='login')
def stations(request):
   
   todo = todoFunct(request)
   useri = todo['useri']
   admin = todo['admin']

   
   stations = InterprisePermissions.objects.filter(Interprise__owner=admin.id,Allow=True,user=useri.id).distinct('Interprise')


  #  Interprise.objects.filter(pk__gt=0).delete()

   todo.update({
      'stations':stations
   })
   return render(request,'stations.html',todo)

# language settings ................................................//
@login_required(login_url='login')
def langSet(request):
  if request.method== "GET":
      val = int(request.GET.get('lang',1))
      usr = UserExtend.objects.filter(user=request.user)
      if val==0 or val ==1:
        usr.update(langSet = val)
        
      return redirect('userdash')
  else:
      return render(request,'pagenotFound.html',todoFunct(request))


@login_required(login_url='login')
def markreadNotify(request):
   if request.method == "POST":
      todo = todoFunct(request)
      useri = todo['useri']
      notifications.objects.filter(usr=useri).update(read=True)
      data = {'success':True}
      return JsonResponse(data)
   
   else:
      return render(request,'pagenotFound.html')
   
@login_required(login_url='login')
def kuseti(request):
   todo = todoFunct(request)
   return render(request,'setting.html',todo)


@login_required(login_url='login')
def companyDetails(request):
   todo = todoFunct(request)
   return render(request,'settingCompanyDetails.html',todo)


# @login_required(login_url='login')
# def upload_company_logo(request):
#     if request.method == 'POST' and request.FILES.get('companyLogo'):
#         try:
#           todo = todoFunct(request)
#           useri = todo['useri']
#           logo = request.FILES['companyLogo']
#           ext = logo.name.split('.')[-1].lower()
#           allowed = ['jpg', 'jpeg', 'png', 'gif']
#           data = {}

#           if ext not in allowed:
#               data = {
#                   'success': False,
#                   'eng': 'Invalid file type. Only images are allowed.',
#                   'swa': 'Aina ya faili si sahihi. Ruhusiwa picha tu.'
#               }
#               return JsonResponse(data)
              
#           # 1. DELETE KAMA IPO
#           if useri.company.logo:
#               try:
#                   # Hakikisha unatumia default_storage kwa ajili ya kufuta GCS
#                   default_storage.delete(useri.company.logo.name)
#               except Exception as e:
#                   # Log kosa la kufuta, lakini usiache lizuie upload
#                   print(f"Error deleting old logo: {e}")
                  
#                   pass
              
#           # 2. UPAKIAJI SAHIHI KWA GCS:
#           filename = f"company_logos/{useri.company.id}_{int(time.time())}.{ext}"

#           path = default_storage.save(filename, logo)

#           # 3. Hifadhi Model
#           useri.company.logo = path
#           useri.company.save()

#           data = {
#               'success': True,
#               'eng': 'Logo uploaded successfully.',
#               'swa': 'Nembo imepakiwa kikamilifu.',
#               'logo_url': default_storage.url(path)
#           }
#           return JsonResponse(data)
#         except Exception as e:
#           data = {
#               'success': False,
#               'eng': f'Error uploading logo: {e}',
#               'swa': f'Hitilafu katika kupakia nembo: {e}'
#           }
#           return JsonResponse(data)
#     else:
#         # Ikiwa sio POST, bado unaweza kutaka kurudisha ukurasa wa logo
#         return render(request, 'pagenotFound.html')

from google.oauth2 import service_account
from google.cloud import storage # Hii inahitajika kwa GCS direct client
from django.core.files.storage import default_storage # Hii inahitajika kwa kufuta faili la zamani


# Chukua BASE_DIR kutoka settings (kwa sababu ya msimbo wa GCS)
BASE_DIR = settings.BASE_DIR


@login_required(login_url='login')
def upload_company_logo(request):
    if request.method == 'POST' and request.FILES.get('companyLogo'):
        todo = todoFunct(request)
        useri = todo['useri']
        logo = request.FILES['companyLogo']
        ext = logo.name.split('.')[-1].lower()
        kampuni = todo['kampuni']
        allowed = ['jpg', 'jpeg', 'png', 'gif']
        data = {}


            
        # 1. DELETE KAMA IPO (Kwa kutumia default_storage)
        if kampuni.logo:
            try:
                kampuni.logo.delete(save=True)
                print(f"Error deleting old logo (via default_storage): Success")
            except Exception as e:
                print(f"Error deleting old logo (via default_storage): {e}")
                pass
            
        # ------------------------------------------------------------------
        # HATUA 2: KULAZIMISHA UPAKIAJI WA MOJA KWA MOJA KWENYE GCS
        # Hili litatoa 403 Forbidden Error ikiwa ruhusa za GCP haziko sawa.
        # ------------------------------------------------------------------
        try:

            if ext not in allowed:
              data = {
                  'success': False,
                  'eng': 'Invalid file type. Only images are allowed.',
                  'swa': 'Aina ya faili si sahihi. Ruhusiwa picha tu.'
              }
            else:  
                  
                  # # Panga jina la faili
                  # filename = f"pics/{useri.company.id}_{int(time.time())}.{ext}"
                  # uploadname = f"media/{filename}"
                  
                  # # --- HATUA A: Pakia Credentials Moja kwa Moja ---
                  # # Hii inatumia faili la JSON moja kwa moja bila kutegemea environment vars (kama faili linaweza kusomwa)
                  # credentials_path = os.path.join(BASE_DIR, 'gcs_service_account.json')
                  # credentials = service_account.Credentials.from_service_account_file(credentials_path)
                  
                  # # --- HATUA B: Anzisha GCS Client ---
                  # storage_client = storage.Client(
                  #     credentials=credentials, 
                  #     project=credentials.project_id
                  # )
                  # bucket = storage_client.bucket('chagufilling') 
                  # blob = bucket.blob(uploadname) # Tunatumia 'media/' kama location 
                  
                  # # --- HATUA C: Piga Upload ---
                  # # Tunatumia logo (UploadedFile) moja kwa moja
                  # blob.upload_from_file(logo, rewind=True, content_type=logo.content_type)
                  
                  # 3. Hifadhi Model (kwa kutumia URL kamili)
                  kampuni.logo = logo # Tunaweka jina tu, si URL kamili
                  kampuni.save()

                  
                  
                  data = {
                      'success': True,
                      'eng': 'Logo forced uploaded successfully .',
                      'swa': 'Nembo imepakiwa kikamilifu .',
                      # 'logo_url': blob.public_url # Tunapata URL moja kwa moja kutoka kwa blob
                  }
            return JsonResponse(data)

        except Exception as e:
            # HII NDIYO TRACEBACK TUNAYOHITAJI KUONA KOSA KAMILI LA GCS API!
            print("="*80)
            print("!!! CRITICAL GCS UPLOAD FAILURE TRACEBACK !!!")
            import traceback
            traceback.print_exc()
            print("="*80)
            data = {
                'success': False,
                'eng': 'CRITICAL UPLOAD ERROR. Check Gunicorn logs immediately!',
                'swa': 'Kosa kubwa la upakiaji. Angalia logi za Gunicorn haraka!',
            }
            return JsonResponse(data)
            
    else:
        # Ikiwa sio POST, bado unaweza kutaka kurudisha ukurasa
        return render(request, 'pagenotFound.html')



def darkMode(request):
   if request.method == "POST":
      todo = todoFunct(request)
      val = int(request.POST.get('val',0))
      useri = todo['useri']   
      useri.darkMode = val
      useri.save()
      
      data = {
         'swa':'Rangi ya muonekano imebadishwa kikamilifu',
         'eng':'Color Mode changed successfully'
      }
      return JsonResponse(data)
   else:
      return render(request,'pagenotFound.html')
   
   
@login_required(login_url='login')
def notify(request):
    todo = todoFunct(request)
    useri = todo['useri']
    notify = notifications.objects.filter(usr=useri)
    unrd = notify.filter(read=False).exists()
    num = notify.count()
    tsa = notify.order_by("-pk")

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
        'unrd':unrd
    })

    return render(request,'notifications.html',todo)

   
@login_required(login_url='login')
def addstetion(request):
   if request.method == 'POST':
      try:
        todo = todoFunct(request)
        useri = todo['useri']
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        region = request.POST.get('region')
        kampuni = useri.company
        data = {
          'success':True,
          'msg_swa':'Stesheni ya mafuta imeongezwa kikamilifu',
          'msg_eng':'Fuel station added successfully'
        }
        if useri.admin:
          av = Interprise.objects.filter(name__icontains=name,sehemu__icontains=address,mkoa__icontains=region,wilaya__icontains=city)
          if not av.exists():
            st = Interprise()
            st.name = name
            st.sehemu = address
            st.mkoa = region
            st.wilaya = city
            st.company = kampuni
            st.vatper = 18.000
            st.vat_allow = True
            st.owner = useri
            st.created = datetime.datetime.now(tz=timezone.utc)
            st.save()
              
            users = UserExtend.objects.filter(Q(ceo=True)|Q(admin=True))  
            for usr in users: 
                pm = InterprisePermissions()
                pm.Interprise = st
                pm.user = usr
                pm.cheo = usr.cheo
                pm.Allow = True
                pm.save()

            payA = PaymentAkaunts()
            payA.Interprise=st
            payA.Akaunt_name = name + ' cash'
            payA.Amount = 0
            # payA.owner = request.user
            payA.onesha = True
            payA.aina = "Cash"
            payA.save()


            payAp = staff_akaunt_permissions()
            payAp.Akaunt = payA
            payAp.user = useri
            payAp.Allow = True
            payAp.owner = True
            payAp.save()

          else:
             data = {
                'success':False,
                'msg_eng':'Station has already added',
                'msg_swa':'Stasheni ya mafuta tayari imeshahifadhiwa'
             }  
        else:
           data = {
              'success':False,
              'msg_eng':'You have no permissions to add station',
              'msg_swa':'Hauna ruhusa ya kuongeza station'
           } 

        return JsonResponse(data)

      except:
         data = {
            'success':False,
            'msg_eng':'The action was not successfully due to error try again correctly',
            'msg_swa':'Kitendo hakikufanikiwa kutokana na hitilafu tafadhari jaribu tena kwa usahihi'
         }   


   

   return render(request,'stations.html',todo)