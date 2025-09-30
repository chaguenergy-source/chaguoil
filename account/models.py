from django.db import models

# Create your models here.

from django.db import models


from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from django.utils import timezone
import time  
import pytz
import datetime




    # class Meta:
    #     managed = False
    #     # db_table = 'kanda'
class company(models.Model):
    phone = models.CharField(max_length=100,null=True, blank=True)
    phone2 = models.CharField(max_length=100,null=True, blank=True)
    country = models.CharField(max_length=50,null=True, blank=True)        
    jina = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    email = models.EmailField(null=True)
    logo = models.ImageField(upload_to="pics",null=True, blank=True)

class UserExtend(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    picha = models.ImageField(upload_to="pics",null=True, blank=True) 
    regstatue = models.IntegerField()
    region = models.CharField(max_length=100,null=True, blank=True)
    phone = models.CharField(max_length=100,null=True, blank=True)
    country = models.CharField(max_length=50,null=True, blank=True)
    address = models.CharField(max_length=200,null=True, blank=True)
    currencii = models.CharField(max_length=14,default="TZS")
    admin = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    cheo = models.CharField(max_length=100,blank=True,null=True)
    pwdResets = models.BooleanField(default=False)
    pu = models.BooleanField(default=False)
    ceo = models.BooleanField(default=False)
    op = models.BooleanField(default=False)
    tankSup = models.BooleanField(default=False)
    company = models.ForeignKey(company,on_delete=models.CASCADE,null=True)
    langSet =  models.IntegerField(default=1)
    postal = models.IntegerField(default=0)
    # darkmode = models.BooleanField(default=False)
    hakikiwa = models.BooleanField(default=False)
    darkMode = models.BooleanField(default=False)
  

    
    def __str__(self):
       return self.user.username
    
class PhoneMailConfirm(models.Model):
    PhoneMail = models.CharField(max_length=100)
    confirm = models.BooleanField(default=False)
    code = models.IntegerField()
    duration = models.DateTimeField()

class Interprise(models.Model):
    name = models.CharField(max_length=200)
    # int_type = models.CharField(max_length=100)
    slogan = models.TextField(null=True,blank=True)
    owner = models.ForeignKey(UserExtend,on_delete = models.CASCADE,null=True,blank=True)
    company = models.ForeignKey(company,on_delete=models.CASCADE,null=True)

    sehemu = models.CharField(max_length=200,blank=True)
    wilaya = models.CharField(max_length=200,blank=True)
    mkoa = models.CharField(max_length=200,blank=True)
    
    prof_pic = models.ImageField(null=True, blank=True)

    # country = models.CharField(max_length=100)

   
    vatper =  models.DecimalField(default=0,max_digits=10,decimal_places=3)
    vat_allow = models.BooleanField(default=False)

    created = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.name

class InterprisePermissions(models.Model):
    Interprise = models.ForeignKey(Interprise,on_delete=models.CASCADE)
    user = models.ForeignKey(UserExtend, on_delete=models.CASCADE)

    Allow = models.BooleanField(default=False)
    discount = models.BooleanField(default=False)
    addsupplier=models.BooleanField(default=False)
    addproduct=models.BooleanField(default=False)

    stokAdjs = models.BooleanField(default=False)
    hamisha = models.BooleanField(default=False)

    pumpIncharge = models.BooleanField(default=False)

    codeChange = models.BooleanField(default=False)
    ProfitView = models.BooleanField(default=False)
    default = models.BooleanField(default=False)
    product_edit = models.BooleanField(default=True)

    manunuziOda = models.BooleanField(default=False)
    expenses = models.BooleanField(default=False)

    cheo = models.CharField(max_length=100)

    akaunti =models.BooleanField(default=False)

    viewi = models.BooleanField(default=False)
    miamala_siri_show = models.BooleanField(default=False)
    miamala_Rekodi = models.BooleanField(default=False)  

    msaidizi = models.BooleanField(default=False)
    fullcontrol = models.BooleanField(default=False)

    onesha_profile = models.BooleanField(default=False)
    mauzo_na_matumizi = models.BooleanField(default=False)


    # if is employee


    def __str__(self):
        return self.Allow
 

class PaymentAkaunts(models.Model):
      Interprise = models.ForeignKey(Interprise,on_delete=models.CASCADE)
      Akaunt_name = models.CharField(max_length=500)
      Amount = models.DecimalField(max_digits=20,decimal_places=2)
      onesha = models.BooleanField(default=True)
    #   owner = models.ForeignKey(User,on_delete=models.CASCADE)
      addedDate = models.DateTimeField(null=True,blank=True)
      aina = models.CharField(max_length = 300)

class staff_akaunt_permissions(models.Model):
    Akaunt = models.ForeignKey(PaymentAkaunts,on_delete=models.CASCADE)
    user = models.ForeignKey(UserExtend,on_delete=models.CASCADE)
    Allow = models.BooleanField(default=False)
    owner = models.BooleanField(default=False)


class wateja(models.Model):
    added_by = models.ForeignKey(UserExtend,on_delete = models.CASCADE)
    # Interprise = models.ForeignKey(Interprise,on_delete = models.CASCADE,null=True,blank=True)
    jina = models.CharField(max_length=500)
    address = models.CharField(max_length=500)
    code = models.CharField(max_length=6)
    simu1 = models.CharField(max_length=15)
    simu2 = models.CharField(max_length=15,null=True, blank=True)
    email = models.EmailField(max_length=100,null=True, blank=True)
    allEntp = models.BooleanField(default=False)
    Interprise = models.ForeignKey(Interprise,on_delete=models.SET_NULL,null=True,blank=True)
   

class wasambazaji(models.Model):
      compan = models.ForeignKey(company,on_delete = models.CASCADE)
      jina = models.CharField(max_length=500)
      address = models.CharField(max_length=500)
      code = models.CharField(max_length=6)
      simu1 = models.CharField(max_length=15)
      simu2 = models.CharField(max_length=15,null=True, blank=True)
      email = models.EmailField(max_length=100,null=True, blank=True)
      active = models.BooleanField(default=False)



class fuel(models.Model):
    name = models.CharField(max_length=100)
    units = models.CharField(max_length=100)


class fuelPriceChange(models.Model):
    fuel = models.ForeignKey(fuel,on_delete=models.SET_NULL,null=True,blank=True)   
    Bprice = models.DecimalField(max_digits=20,decimal_places=4) 
    Aprice = models.DecimalField(max_digits=20,decimal_places=4) 
    date = models.DateTimeField()
    Interprise = models.ForeignKey(Interprise,on_delete=models.CASCADE,null=True,blank=True)
    desc = models.TextField(blank=True) 
    by = models.ForeignKey(UserExtend,on_delete=models.CASCADE,null=True,blank=True)

class tankContainer(models.Model):
    name = models.CharField(max_length=100)   
    compan = models.ForeignKey(company,on_delete = models.CASCADE)
    by = models.ForeignKey(UserExtend,on_delete=models.CASCADE,null=True,blank=True)


class fuel_tanks(models.Model):
    name = models.CharField(max_length=100)
    Interprise = models.ForeignKey(Interprise,on_delete=models.CASCADE,null=True,blank=True)
    tank = models.ForeignKey(tankContainer,on_delete=models.CASCADE,null=True,blank=True)
    fuel = models.ForeignKey(fuel,on_delete=models.SET_NULL,null=True,blank=True)
    qty = models.DecimalField(max_digits=20,decimal_places=4)
    price = models.DecimalField(max_digits=20,decimal_places=4)
    cost = models.DecimalField(max_digits=20,decimal_places=4)
    maxm = models.DecimalField(max_digits=20,decimal_places=4)
    minm = models.DecimalField(max_digits=20,decimal_places=4,default=0)

    moving = models.BooleanField(default=False)


class PumpStation(models.Model):
    name = models.CharField(max_length=100) 
    Interprise = models.ForeignKey(Interprise,on_delete=models.CASCADE,null=True,blank=True)
 
     

class fuel_pumps(models.Model):
    name = models.CharField(max_length=100)
    station =  models.ForeignKey(PumpStation,on_delete=models.SET_NULL,null=True,blank=True)
    tank = models.ForeignKey(fuel_tanks,on_delete=models.SET_NULL,null=True,blank=True)
    readings = models.DecimalField(max_digits=20,decimal_places=4)
    Incharge = models.ForeignKey(UserExtend,on_delete=models.SET_NULL,null=True,blank=True)
    fromi = models.DateTimeField(blank=True,null=True)


class shiftsTime(models.Model):
    name =  models.CharField(max_length=100,null=True)
    shFrom = models.TimeField()
    shTo = models.TimeField()
    Interprise = models.ForeignKey(Interprise,on_delete=models.CASCADE,null=True,blank=True)
    active = models.BooleanField(default=False)

   

class shiftSesion(models.Model):
    date = models.DateField()
    session =  models.ForeignKey(shiftsTime,on_delete=models.CASCADE,null=True,blank=True)
    complete = models.BooleanField(default=False)

class shifts(models.Model):
    code =  models.CharField(max_length=20,null=True)
    Invo_no = models.IntegerField(default=0)
    From =  models.DateTimeField(blank=True,null=True)
    To =  models.DateTimeField(blank=True,null=True)
    by = models.ForeignKey(UserExtend,on_delete=models.SET_NULL,null=True,blank=True)
    record_by = models.ForeignKey(InterprisePermissions, on_delete=models.CASCADE,null=True)
    amount = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    paid =  models.DecimalField(max_digits=20,decimal_places=4,default=0)
    remarks = models.TextField(blank=True)
    lossprof = models.BooleanField(default=False)
    session = models.ForeignKey(shiftSesion,on_delete=models.SET_NULL,null=True,blank=True)


class shiftPump(models.Model):    
    pump = models.ForeignKey(fuel_pumps,on_delete=models.SET_NULL,null=True,blank=True)
    Fuel = models.ForeignKey(fuel,on_delete=models.SET_NULL,null=True,blank=True)
    shift = models.ForeignKey(shifts,on_delete=models.SET_NULL,null=True,blank=True)
    initial = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    final = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    qty = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    price = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    cost = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    amount = models.DecimalField(max_digits=20,decimal_places=4,default=0)

class transfer_from(models.Model):
    tank = models.ForeignKey(fuel_tanks,on_delete=models.SET_NULL,null=True,blank=True)

class tr_supervisor(models.Model):
    sup = models.ForeignKey(UserExtend,on_delete=models.SET_NULL,null=True,blank=True)

class Purchases(models.Model):
    vendor = models.ForeignKey(wasambazaji,on_delete=models.SET_NULL,null=True,blank=True)
    code =  models.CharField(max_length=20,null=True)
    ref =  models.CharField(max_length=500,null=True)
    Invo_no = models.IntegerField(default=0)
    date = models.DateTimeField()
    recDate = models.DateTimeField(null=True)
    record_by = models.ForeignKey(UserExtend,on_delete=models.SET_NULL,null=True,blank=True)
    amount = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    payed = models.DecimalField(max_digits=20,decimal_places=4,default=0) 
    closed =  models.BooleanField(default=False)  


class PuList(models.Model):
    pu = models.ForeignKey(Purchases,on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    qty = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    rcvd = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    Fuel = models.ForeignKey(fuel,on_delete=models.CASCADE)


class TransferFuel(models.Model):
    code =  models.CharField(max_length=20,null=True)
    Invo_no = models.IntegerField(default=0)
    container =  models.ForeignKey(tankContainer,on_delete=models.SET_NULL,null=True,blank=True)
    otherCont = models.TextField(blank=True) 

    date = models.DateTimeField()
    recDate = models.DateTimeField(null=True)
    
    record_by = models.ForeignKey(InterprisePermissions,on_delete=models.SET_NULL,null=True,blank=True)
    Transfer_by = models.ForeignKey(UserExtend,on_delete=models.SET_NULL,null=True,blank=True)
    trSup = models.ForeignKey(tr_supervisor,on_delete=models.SET_NULL,null=True,blank=True)
    desc = models.TextField(blank=True)    
       
class transFromTo(models.Model):  
    transfer = models.ForeignKey(TransferFuel,on_delete=models.CASCADE,null=True,blank=True)
    shift =  models.ForeignKey(shiftPump,on_delete=models.SET_NULL,null=True,blank=True)
    pump =  models.ForeignKey(fuel_pumps,on_delete=models.SET_NULL,null=True,blank=True)
    Fuel =  models.ForeignKey(fuel,on_delete=models.SET_NULL,null=True,blank=True)

    cost = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    saprice = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    FuelAmo = models.DecimalField(max_digits=20,decimal_places=4,default=0)

    qty = models.DecimalField(max_digits=20,decimal_places=4,default=0)

    From = models.ForeignKey(transfer_from,on_delete=models.SET_NULL,null=True,blank=True)
    to = models.ForeignKey(fuel_tanks,on_delete=models.SET_NULL,null=True,blank=True)

    # qty_trans = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    # qty_sales = models.DecimalField(max_digits=20,decimal_places=4,default=0)

    taken = models.DecimalField(max_digits=20,decimal_places=4,default=0)

    closed = models.BooleanField(default=False)    

class ToContena(models.Model):
    cont = models.ForeignKey(tankContainer,on_delete=models.SET_NULL,null=True,blank=True)
    Incharge =  models.ForeignKey(UserExtend,on_delete=models.SET_NULL,null=True,blank=True)

class ReceveFuel(models.Model):
    code =  models.CharField(max_length=20,null=True)
    Invo_no = models.IntegerField(default=0)
    date = models.DateTimeField(null=True)
    recDate = models.DateTimeField(null=True)
    by = models.ForeignKey(InterprisePermissions,on_delete=models.SET_NULL,null=True,blank=True)

    op = models.ForeignKey(tr_supervisor,on_delete=models.SET_NULL,null=True,blank=True)
    
    ses = models.ForeignKey(shiftSesion,on_delete=models.SET_NULL,null=True,blank=True)

    Fromcont = models.ForeignKey(tankContainer,on_delete=models.SET_NULL,null=True,blank=True)
    Incharge = models.ForeignKey(UserExtend,on_delete=models.SET_NULL,null=True,blank=True)

    Tocont = models.ForeignKey(ToContena,on_delete=models.SET_NULL,null=True,blank=True)
    FromTransf = models.ForeignKey(TransferFuel,on_delete=models.SET_NULL,null=True,blank=True)
    FromPurchase = models.ForeignKey(Purchases,on_delete=models.SET_NULL,null=True,blank=True)
    desc = models.TextField(blank=True)   

class receivedFuel(models.Model):
    receive = models.ForeignKey(ReceveFuel,on_delete=models.SET_NULL,null=True,blank=True)
    To = models.ForeignKey(fuel_tanks,on_delete=models.SET_NULL,null=True,blank=True)
    From = models.ForeignKey(transfer_from,on_delete=models.SET_NULL,null=True,blank=True)
    qty =  models.DecimalField(max_digits=20,decimal_places=4,default=0)
    qtyB =  models.DecimalField(max_digits=20,decimal_places=4,default=0)
    qtyA =  models.DecimalField(max_digits=20,decimal_places=4,default=0)
    price =  models.DecimalField(max_digits=20,decimal_places=4,default=0)
    cost = models.DecimalField(max_digits=20,decimal_places=4,default=0)   
    Fuel = models.ForeignKey(fuel,on_delete=models.SET_NULL,null=True,blank=True)


class saleOnReceive(models.Model):
    receive = models.ForeignKey(receivedFuel, on_delete=models.CASCADE,null=True)
    tank = models.ForeignKey(fuel_tanks, on_delete=models.CASCADE,null=True)
    ses = models.ForeignKey(shiftSesion, on_delete=models.CASCADE,null=True)
    qty =  models.DecimalField(max_digits=20,decimal_places=4,default=0)
    cost = models.DecimalField(max_digits=20,decimal_places=4,default=0)   

class adjustments(models.Model):
    code =  models.CharField(max_length=20,null=True)
    Invo_no = models.IntegerField(default=0)
    tarehe =  models.DateTimeField(blank=True,null=True)
    session = models.ForeignKey(shiftSesion,on_delete=models.SET_NULL,null=True,blank=True)
    container = models.ForeignKey(tankContainer,on_delete=models.SET_NULL,null=True,blank=True)
    Interprise = models.ForeignKey(Interprise,on_delete=models.SET_NULL,null=True,blank=True)
    by = models.ForeignKey(InterprisePermissions,on_delete=models.SET_NULL,null=True,blank=True)
    operator = models.ForeignKey(UserExtend,on_delete=models.SET_NULL,null=True,blank=True)
    maelezo = models.TextField(blank=True)
    receive = models.ForeignKey(ReceveFuel,on_delete=models.SET_NULL,null=True,blank=True)

class tankAdjust(models.Model):   
    adj =  models.ForeignKey(adjustments,on_delete=models.SET_NULL,null=True,blank=True)
    tank = models.ForeignKey(fuel_tanks,on_delete=models.SET_NULL,null=True,blank=True)
    fuel = models.ForeignKey(fuel,on_delete=models.SET_NULL,null=True,blank=True)
    read = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    stick = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    diff = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    price = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    cost = models.DecimalField(max_digits=20,decimal_places=4,default=0)
   

class fuelSales(models.Model):
    code =  models.CharField(max_length=20,null=True)
    Invo_no = models.IntegerField(default=0)
    by = models.ForeignKey(InterprisePermissions, on_delete=models.CASCADE,null=True)
    contInchage = models.ForeignKey(UserExtend, on_delete=models.CASCADE,null=True)
    cont = models.ForeignKey(tankContainer, on_delete=models.CASCADE,null=True)
    session = models.ForeignKey(shiftSesion,on_delete=models.SET_NULL,null=True,blank=True)
    driver=models.CharField(max_length=200,blank=True)
    vihecle=models.CharField(max_length=700,blank=True)
    customer = models.ForeignKey(wateja, on_delete=models.CASCADE,null=True)
    phone = models.CharField(max_length=200,blank=True)
    
    amount = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    payed = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    recDate = models.DateTimeField(null=True)
    date = models.DateTimeField(null=True) 
    shiftBy = models.ForeignKey(shifts,on_delete=models.SET_NULL,null=True,blank=True) 


class saleList(models.Model):    
    sale = models.ForeignKey(fuelSales, on_delete=models.CASCADE,null=True)
    tank = models.ForeignKey(fuel_tanks, on_delete=models.CASCADE,null=True)
    theFuel = models.ForeignKey(fuel, on_delete=models.CASCADE,null=True)
    shift = models.ForeignKey(shiftPump, on_delete=models.CASCADE,null=True)
    qty_sold = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    cost_sold = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    sa_price = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    sa_price_og = models.DecimalField(max_digits=20,decimal_places=4,default=0)





class receiveFromTr(models.Model):
    From = models.ForeignKey(TransferFuel,on_delete=models.SET_NULL,null=True,blank=True) 
    To_Rc = models.ForeignKey(ReceveFuel,on_delete=models.SET_NULL,null=True,blank=True) 
    rc_qty = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    To_Sa = models.ForeignKey(fuelSales,on_delete=models.SET_NULL,null=True,blank=True)

class matumizi(models.Model):
    owner = models.ForeignKey(UserExtend, on_delete=models.CASCADE,null=True)
    shell = models.ForeignKey(Interprise, on_delete=models.CASCADE,null=True)
    matumizi=models.CharField(max_length=700)
    period_type = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    last_paid = models.DateField(null=True,blank=True)
    next_pay = models.DateField(null=True,blank=True)
    amount = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    depends = models.BooleanField(default=True)
    general = models.BooleanField(default=False)

class matumiziTarehe(models.Model):
    date = models.DateTimeField(null=True,blank=True)
    Na =models.ForeignKey(InterprisePermissions, on_delete=models.CASCADE,blank=True, null=True)

class rekodiMatumizi(models.Model):
    Interprise = models.ForeignKey(Interprise, on_delete=models.CASCADE,null=True)
    matumizi = models.ForeignKey(matumizi, on_delete=models.CASCADE)
    manunuzil = models.BooleanField(default=False)
    date = models.DateField(null=True,blank=True)
    tarehe = models.DateTimeField()
    matumiziDeti = models.ForeignKey(matumiziTarehe, on_delete=models.CASCADE,blank=True, null=True)

    # manunuzi_id = models.ForeignKey(manunuzi, on_delete=models.CASCADE,blank=True, null=True)
    # adjst= models.ForeignKey(stokAdjustment, on_delete=models.CASCADE,blank=True, null=True)
    
    kiasi = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    fuel_qty = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    fuel_cost = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    fuel_price = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    ilolipwa = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    akaunti = models.ForeignKey(PaymentAkaunts, on_delete=models.CASCADE,blank=True, null=True)
    fromShift = models.ForeignKey(shiftPump, on_delete=models.CASCADE,blank=True, null=True)
    Fuel = models.ForeignKey(fuel, on_delete=models.CASCADE,blank=True, null=True)
    
    by = models.ForeignKey(UserExtend, on_delete=models.CASCADE,blank=True, null=True)
    kabidhiwa = models.CharField(max_length=500,blank=True,null=True)
    maelezo = models.TextField(blank=True)


class wekaCash(models.Model):
    Interprise=models.ForeignKey(Interprise,on_delete=models.CASCADE)
    tarehe = models.DateTimeField()
    Akaunt = models.ForeignKey(PaymentAkaunts,on_delete=models.CASCADE,null=True)
    Amount = models.DecimalField(max_digits=20,decimal_places=4)
    tDebt = models.DecimalField(max_digits=20,decimal_places=4,default=0)
    tInvo = models.IntegerField(default=0)
    before = models.DecimalField(max_digits=20,decimal_places=4)
    After = models.DecimalField(max_digits=20,decimal_places=4)
    kutoka =  models.CharField(max_length=500) 
    maelezo = models.CharField(max_length=500,blank=True,null=True)
    by= models.ForeignKey(UserExtend,on_delete=models.CASCADE,null=True)
    usiri = models.BooleanField(default=False)
    kutoka_siri = models.BooleanField(default=False)

    mauzo = models.BooleanField(default=False)
    shift = models.ForeignKey(shifts,on_delete=models.CASCADE,null=True)
    biforeShift = models.BooleanField(default=False)
    giveTo = models.CharField(max_length=500,blank=True,null=True)
    
    sales = models.ForeignKey(fuelSales,on_delete=models.CASCADE,null=True)
    customer = models.ForeignKey(wateja,on_delete=models.CASCADE,null=True)

    order = models.BooleanField(default=False)
    saRec = models.BooleanField(default=False)

    # invo = models.ForeignKey(mauzoni,on_delete=models.SET_NULL,null=True)
    # bill_ref = models.ForeignKey(bil_return,on_delete=models.SET_NULL,null=True)

    huduma = models.BooleanField(default=False)
    kuhamisha = models.BooleanField(default=False)
    kuhamishaNje = models.BooleanField(default=False)
    mtaji = models.BooleanField(default=False)

    # huduma_nyingine = models.ForeignKey(HudumaNyingine,on_delete=models.SET_NULL,null=True)

class  toaCash(models.Model):
    Interprise=models.ForeignKey(Interprise,on_delete=models.CASCADE,null=True)     
    tarehe = models.DateTimeField()  
    Akaunt = models.ForeignKey(PaymentAkaunts,on_delete=models.CASCADE)
    Amount = models.DecimalField(max_digits=20,decimal_places=4)
    before = models.DecimalField(max_digits=20,decimal_places=4)
    After = models.DecimalField(max_digits=20,decimal_places=4)
    kwenda =  models.CharField(max_length=500) 
    maelezo = models.CharField(max_length=500)
    makato = models.IntegerField(default=0)
    by= models.ForeignKey(UserExtend,on_delete=models.CASCADE,null=True)
  
    usiri = models.BooleanField(default=False)
    kwenda_siri = models.BooleanField(default=False)

    kuhamishaNje = models.BooleanField(default=False)
    kuhamisha = models.BooleanField(default=False)
    personal = models.BooleanField(default=False)

    matumizi = models.ForeignKey(rekodiMatumizi,on_delete=models.SET_NULL,null=True)

#INCASE OF BILL PAYMENT......................................//
    # pu = models.BooleanField(default=False)
    bill = models.ForeignKey(wasambazaji,on_delete=models.SET_NULL,null=True)

class CustmDebtPayRec(models.Model):
    pay =  models.ForeignKey(wekaCash, on_delete=models.CASCADE,blank=True, null=True)
    sale = models.ForeignKey(fuelSales, on_delete=models.CASCADE,blank=True, null=True)
    Debt = models.DecimalField(max_digits=20,decimal_places=4)
    Apay = models.DecimalField(max_digits=20,decimal_places=4)

class pumpTemper(models.Model):
    by = models.ForeignKey(InterprisePermissions, on_delete=models.CASCADE,blank=True, null=True)
    pump = models.ForeignKey(fuel_pumps, on_delete=models.CASCADE,blank=True, null=True)
    BRead = models.DecimalField(max_digits=20,decimal_places=4)
    ARead = models.DecimalField(max_digits=20,decimal_places=4)
    desc = models.TextField(blank=True)
    date = models.DateTimeField(null=True)

class notifications(models.Model):
    usr =  models.ForeignKey(UserExtend, on_delete=models.CASCADE,blank=True, null=True)
    price = models.ForeignKey(fuelPriceChange, on_delete=models.CASCADE,blank=True, null=True)
    temper = models.ForeignKey(pumpTemper, on_delete=models.CASCADE,blank=True, null=True)
    desc = models.TextField(blank=True)
    read = models.BooleanField(default=False)
    date = models.DateTimeField(null=True)

class attachments(models.Model):
    file = models.FileField(upload_to="attachments",null=True,blank=True)
    receive = models.ForeignKey(ReceveFuel, on_delete=models.CASCADE,blank=True, null=True)
    shift = models.ForeignKey(shifts, on_delete=models.CASCADE,blank=True, null=True)
    transfer = models.ForeignKey(TransferFuel, on_delete=models.CASCADE,blank=True, null=True)
    sales = models.ForeignKey(fuelSales, on_delete=models.CASCADE,blank=True, null=True)
    session = models.ForeignKey(shiftSesion, on_delete=models.CASCADE,blank=True, null=True)
    adj = models.ForeignKey(adjustments, on_delete=models.CASCADE,blank=True, null=True)
    purchase = models.ForeignKey(Purchases, on_delete=models.CASCADE,blank=True, null=True)
    
    attach_name = models.CharField(max_length=500,blank=True)
    printedDocu = models.BooleanField(default=False)
    by = models.ForeignKey(UserExtend, on_delete=models.SET_NULL,blank=True, null=True)
    date = models.DateTimeField(null=True)