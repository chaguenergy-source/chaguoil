from .models import UserExtend,wateja,shiftsTime,notifications,shifts,InterprisePermissions,fuel_tanks,fuel_pumps,PaymentAkaunts,matumizi
from django.utils import timezone
from django.db.models import Q
from datetime import date


# FOr mails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import requests, json


def confirmMailF(mail):
      html_content = render_to_string("mailtemp.html",{'num':mail['num']})
      if not mail['num']:
           html_content =  render_to_string("staffconfirm.html",mail['user'])  
      
      text_content = strip_tags(html_content)
      emaili =  EmailMultiAlternatives(
          "Confirmation",
          text_content,
          settings.EMAIL_HOST_USER,
          # 'Dont Reply <do_not_reply@gmail.com>',
          [mail['to']]
      )
      emaili.attach_alternative(html_content,"text/html")
      emaili.send()
class Todos:
  def __init__(self,request):
      self.request = request 
      
  def todoF(self):  
      todo = {}
      try:
        used = self.request.user
        user = UserExtend.objects.get(user = used.id ) 
        kampuni = user.company
        cheo = None
        shell = None
        general = user.ceo or user.admin
        admin = UserExtend.objects.get(admin=True,company=kampuni)
        manager = False
        allowed=InterprisePermissions.objects.filter(user=user.id,Allow=True)
        if not allowed.filter(default=True).exists() and not general:
             alloW = allowed.last()
             alloW.default = True
             alloW.save()     

        allowed = allowed.filter(default=True)
        payacc = PaymentAkaunts.objects.filter(Interprise__company=kampuni.id)
        tumizi = matumizi.objects.filter(owner__company=kampuni.id,duration=0)
        tr_pump =  fuel_pumps.objects.filter(tank__Interprise__company=kampuni)
       
       
        pumpAttend = None
        shell_tanks = None
        disp = None
        tankContainer = None
        fuel_price = None
        notify = notifications.objects.filter(usr=user,read=False).count()
        tanksSup = InterprisePermissions.objects.filter(Interprise__company=kampuni,user__tankSup=True)
        tr_by = UserExtend.objects.filter(op=True,company=kampuni.id)
        tanks = fuel_tanks.objects.filter(Interprise__company=kampuni)
        tr_tank = tanks.filter(moving=True)
      #   shifts.objects.all().delete()
      #   shiftsTime.objects.all().delete()

        
        if allowed.exists():
           cheo = allowed.last()
           general = False
           shell = cheo.Interprise
           payacc = payacc.filter(Interprise=shell.id) 
           manager = cheo.fullcontrol
           tr_pump = fuel_pumps.objects.filter(tank__Interprise=shell.id)
           
           pumpAttend =  shifts.objects.filter(record_by__Interprise=shell.id,To=None)

           
           tanksSup = tanksSup.filter(Interprise=shell)
           tanks = tanks.filter(Interprise=shell.id)

        disp = tr_pump.distinct('station')
        fuel_price = tanks.distinct('fuel')
      #   tr_tank = tanks.filter(moving=True)
        tankContainer = tr_tank.distinct('tank')
        shell_tanks = tanks.filter(moving=False)
           
        cust = wateja.objects.filter(Interprise__company=kampuni)
        if not general:
            cust = cust.filter(Q(Interprise=shell.id)|Q(allEntp=True))
            fuel_price = tanks.filter(Interprise=shell.id).distinct('fuel')

        todo = {
        'useri':user,
        'cheo':cheo,
        'shell':shell,
        'general':general,
        'shell_tanks':shell_tanks,
        'admin':admin,
        'disp':disp,
        'payacc':payacc,
        'matumizi':tumizi,
        'manager':manager,
        'tr_pump':tr_pump,
        'tr_tank':tr_tank,
        'tr_by':tr_by,
        'customers':cust,
        'currencii':user.currencii,
        'kampuni':kampuni,
        'PumpAttend':pumpAttend,
        'tankContainer':tankContainer,
        'fuel_price':fuel_price,
        'notify':notify,
         'tanksSup':tanksSup
  
        }

      except:
        todo={
           
            'useri':None,
            'shell':None
        }
      return todo
   
def invoCode(entry):
        invono = 1
        invo_str=''
        
        if entry.exists():
              invo_no = entry.last()
        
              invono = int(invo_no.Invo_no) + 1

        if invono <10:
              invo_str = '000'+str(invono)
        elif invono <100 and invono >=10:
              invo_str = '00' +str(invono)    
        elif invono <1000 and invono >=100:
              invo_str = '0' +str(invono)    
         
        elif invono >=1000 :
              invo_str =str(invono) 
        return invo_str      

def TCode(code):
      
      intpCode = str(code['shell'])+'/'+code['code']

      if code['shell'] < 10:
            intpCode = '0'+intpCode
           
      return intpCode