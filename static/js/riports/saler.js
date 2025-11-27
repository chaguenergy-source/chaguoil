
let saData = [],FUEL = [], VDATA = {},ISVIEW = 0,SAOBJ=[],VOBJ={}
const filters = () =>{
    const  st = Number($('#staxnF').val()),
           ses = $('#SessF').val(),
           fl = Number($('#fuelFt').val()),
           pA = Number($('#PAttend').val()),
           saT = Number($('#satype').val()),
           today = {rname:lang('Leo','Today'),tFr:moment(moment().startOf('day')).format(),tTo:moment().format()},
           week = {rname:lang('Wiki hii','This Week'),tFr:moment(moment().startOf('isoWeek')).format(),tTo:moment().format()},
           month = {rname:lang('Mwezi huu','This Month'),tFr:moment(moment().startOf('month')).format(),tTo:moment().format()},
           isChart = Number($('#riportChatRist btn-secondary').data('r')),
           chartT = $('#riportSwitch .btn-primary').data('chart')
           return {st,ses,fl,pA,saT,today,week,month,isChart,chartT}
}

const getRData = d =>{
    $('#loadMe').modal('show')
    const {tFr,tTo,rname,init} = d,
          url = '/analytics/getsaler' ,
          tdy = Number(moment(tTo).format('DD')),
          tmFr = tdy>=7||!init?tFr:moment(moment().subtract(7,'days')).format(),
          data = {data:{tFr:tmFr,tTo},url},
          
          
          sendIt = POSTREQUEST(data)
         
          sendIt.then(resp=>{
              $('#loadMe').modal('hide')
              hideLoading()
              FUEL = resp.fuel
              
              summaryR({resp,rname,init,tFr,tTo})

         
          })

}

const summaryR = d =>{
        const {resp,rname,init,tFr,tTo} = d,
          {today,week} = filters(),
          {sale,saL,pay,payRec} = resp
    
         if(init){
                // Today report 
                ArryCreate({sale,saL,pay,payRec,tFr:today.tFr,tTo:today.tTo,rname:today.rname})

                // week report 
                
                ArryCreate({sale,saL,pay,payRec,tFr:week.tFr,tTo:week.tTo,rname:week.rname})
              
            }

                ArryCreate({sale,saL,pay,payRec,tFr,tTo,rname})
               createtr()
     }

const createtr = () =>{
const {st,ses,fl,pA,saT} = filters()
let tr = '',chk=''
const init = Number($('#generalSaleR tr').length==0)
        
        saData.forEach(r=>{
        
        let  sale = st?r.sale?.filter(sa=>sa.shell===st):r.sale,
                saL = st?r.saL?.filter(sa=>sa.shell===st):r.saL

                //  Sale Type filter (Customer or Pump Attendants)
                sale = saT==1?sale?.filter(sa=>sa.shiftBy_id!=null):sale
                sale = saT==2?sale?.filter(sa=>sa.customer_id!=null):sale

                saL = saT==1?saL?.filter(sa=>sa.pAtt!=null):saL
                saL = saT==2?saL?.filter(sa=>sa.cust!=null):saL

                //  Sessesion filter 
                sale = ses?sale?.filter(sa=>sa.ses===ses):sale
                saL = ses?saL?.filter(sa=>sa.ses===ses):saL

        


                

            const   cost=saL.reduce((a,b)=>a+Number(b.Tcost),0),
                amo=sale.reduce((a,b)=>a+Number(b.amount),0),
                paid=sale.reduce((a,b)=>a+Number(b.payed),0),
                due=sale.filter(sa=>sa.due>=0 && sa.customer_id!=null).reduce((a,b)=>a+Number(b.due),0),
                
                check = Number($(`#MonthSale${r.id}`).prop('checked')),
                show = check == 1 || check == 0 ?check:1,

                hide = !init && !show

               

        tr+=`<tr class="${r.id>3?'table-info':''}"  ${hide?'style="display:none"':''}   id="dataRow${r.id}" >
            <td> <a type="button" data-val=${r.id} class="bluePrint viewDetails" >${r.rname} </a> </td>
            <td>${Number(cost).toLocaleString()}  </td>
            <td>${Number(amo).toLocaleString()}  </td>
            <td>${Number(paid).toLocaleString()}  </td>
            <td>${Number(due).toLocaleString()}  </td>
            <td>
                <div class="d-flex">
                <button type="button" data-val=${r.id} data-show=".detailReport" data-hide=".summaryRiport" class="btn viewDetails btn-sm border0 showDtBtn smallerFont btn-light" title="${lang('Onesha zaidi','More Info')}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z">
                        </path><circle cx="12" cy="12" r="3"></circle>
                        </svg>
                </button>
            `

            if(r.id>3){
            tr+=`
                <button type="button" data-val=${r.id} class="btn btn-sm text-danger removeTherow border0 smallerFont btn-danger btn-light" title="${lang('Ondoa','Remove')}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trash-2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                </button>
            `
            }
            
        tr+=`</td></tr>`


            chk+=` <div class="custom-control smallFont d-inline mx-2 custom-checkbox"  >
                    <input type="checkbox" onchange="$('#dataRow${r.id}').toggle(100)"  ${hide?'':'checked'} name="MonthSale" id="MonthSale${r.id}" class="custom-control-input" style="cursor: pointer !important;"><label class="custom-control-label" style="cursor: pointer !important;" for="MonthSale${r.id}">${r.rname}</label>
                </div>`


    })

    $('#generalSaleR').html(tr)
    $('#mapSelector').html(chk)
}

// The seleted time duration Data....................................//
const ArryCreate = d =>{
            const {tFr,tTo,rname} = d,
                     sale = d.sale?.filter(s=>moment(s.date).format() >= tFr && moment(s.date).format() <= tTo ),
                     saL = d.saL?.filter(s=>moment(s.date).format() >= tFr && moment(s.date).format() <= tTo ),
                     pay = d.pay?.filter(s=>moment(s.tarehe).format() >= tFr && moment(s.tarehe).format() <= tTo ),
                     payRec = d.payRec?.filter(s=>moment(s.date).format() >= tFr && moment(s.date).format() <= tTo )
            thedt = {
                id:saData.length + 1,
                rname,
                sale,
                saL,
                pay,
                tFr,
                tTo,
                payRec
           
         }
         saData.push(thedt)


}



function createArray(rname,tFr,tTo){
        
            const saDt = saData.filter(d=>d.tFr<=tFr && d.tTo>=tTo),
                  isThere = saData.filter(d=>d.tFr===tFr && d.tTo===tTo),
                  msg = lang('tayari ipo','alread exists')
                if(isThere.length){
                     
                     toastr.info(msg, lang('Taarifa','info '), {timeOut: 2000})
                }else{
                if(saDt.length>0){
                     const theDt = saDt[0],
                     dt = {sale:theDt.sale,pay:theDt.pay,saL:theDt.saL,tFr,tTo,rname}
                     ArryCreate(dt)
                     createtr()

                }else{

                    getRData({tFr,tTo,rname,init:0});     

                }   }


                }



$(document).ready(function(){
    const {month} = filters(),
          {tFr,tTo,rname} = month
          getRData({tFr,tTo,rname,init:1});

})


$('.filter').change(function(){
    SAOBJ=[]
    createtr()
    if(ISVIEW)detailReport()

})

$('body').on('click','.removeTherow',function(){
    if(confirm(lang('Ondoa','Remove'))){
         const id = Number($(this).data('val'))
            saData = saData.filter(sa=>sa.id!=id)
            createtr()
    }
})


$('body').on('click','.viewDetails',function(){
    const id = Number($(this).data('val'))
          VDATA = saData.filter(d=>d.id===id)[0]
  
          detailReport()

         $('#summaryRiport').fadeOut();
        
         $('.riportOn').removeClass('btn-primary')
         $('#RBydate').addClass('btn-primary')

         $('.DetailsTable').hide()
        

         $('#saleByDate').show()
         $('#Salecateg').show()

        $('#detailReport').fadeIn(200)

      
        
         
         

})

$('#calenderBack').click(function(){
    $('#detailReport').fadeOut();
    $('#summaryRiport').fadeIn(200)
    ISVIEW = 0
    SAOBJ = []
    
})

const detailReport = () =>{
     ISVIEW = 1
     const {rname,tFr,tTo} = VDATA,
     r = VDATA,
     DFrom = moment(tFr).format('YYYY-MM-DD'),
     DTo = moment(tTo).format('YYYY-MM-DD'),
     tdy = moment().format('YYYY-MM-DD'),
     {st,ses,saT} = filters(),

     Rdate = DFrom==DTo?moment(tFr).format('DD/MM/YYYY'):`${moment(tFr).format('DD/MM/YYYY')} - ${moment(tTo).format('DD/MM/YYYY')}`,
     isToday = DTo == tdy?`${lang('Hadi','To')} ${moment(tTo).format('HH:mm')}`:'',
     head = `${lang('Mchanganuo wa Mauzo','Sales Analysis')} <span class="bluePrint"> ${Rdate} </span> ${isToday}`
   
    let  sale = st?r.sale?.filter(sa=>sa.shell===st):r.sale,
         saL = st?r.saL?.filter(sa=>sa.shell===st):r.saL,
         pay =st?r.pay?.filter(sa=>sa.st===st):r.pay
         payRec =st?r.payRec?.filter(sa=>sa.st===st):r.payRec

        //  Sale Type filter (Customer or Pump Attendants)
        // sale = saT==1?sale?.filter(sa=>sa.shiftBy_id!=null):sale
        // sale = saT==2?sale?.filter(sa=>sa.customer_id!=null):sale

        // saL = saT==1?saL?.filter(sa=>sa.pAtt!=null):saL
        // saL = saT==2?saL?.filter(sa=>sa.cust!=null):saL

        //  Sessesion filter 
        // sale = ses?sale?.filter(sa=>sa.ses===ses):sale
        // saL = ses?saL?.filter(sa=>sa.ses===ses):saL
       
        $('#detailRHeading').html(head)
        
        pAttTable({sale,saL})
        customerTable({sale,saL})
        detSummaryTable({sale,saL})
        OverallTable({sale,saL})
        dateSaleTable({sale,saL})
        // salePay({pay,payRec,sale})

        $('#riportChatRist .btn-secondary').addClass('btn-light').removeClass('btn-secondary')
        $('#riportChatRist button').first().addClass('btn-secondary').removeClass('btn-light')

        $('#MoreDetails').fadeOut(100)
        $('#Salecateg').fadeIn(100)
        const chart = $('#riportSwitch button.btn-primary').data('chart')
        const theObj = SAOBJ.find(n=>n.name===chart)
        VOBJ = {data:theObj.data,title:theObj.title}



}

const pAttTable = d =>{
    const {sale,saL} = d,
          
        PASale = sale?.filter(att=>att.pAtt!=null),
        PASaL = saL.filter(a=>a.pAtt!=null),
        totCost = PASaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
        totPay = PASale.reduce((a,b)=>a+Number(b.payed),0),
        totSale = PASale.reduce((a,b)=>a+Number(b.amount),0),
        totBonus =totPay-totSale,
        totProf = totPay - totCost,
        GStatus = totBonus>1?lang('Bonasi','Bonus'):totBonus==0?lang('Sawa','Clear'):lang('Hasara','Loss'),

        pA = [... new Set(PASale.map(att=>att.pAtt))],
        AttendData = (at) =>{
        const Atsa = PASale.filter(a=>a.pAtt===at),
              AtsaL = PASaL.filter(a=>a.pAtt===at),
              atF = FUEL.map(f=>attendFuel(f))
             
         function  attendFuel(f){
              
               const fAtsaL = AtsaL.filter(a=>a.theFuel_id===f.fuel) ,
                fDt = {
                  fuel:f.fname,
                  id:f.fuel,
                  qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                  cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                  sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
               } 
               
               return fDt
         }    
         
        const tot = Atsa.reduce((a,b)=>a+Number(b.amount),0),
              pay=Atsa.reduce((a,b)=>a+Number(b.payed),0),
              cost = AtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
              bonus = pay-tot,
              dt= {
              name:`${Atsa[0].pAtt_fname} ${Atsa[0].pAtt_lname}`,
              att:Atsa[0].pAtt,
              shift:Atsa.length,
              fuel: atF,
              tot,
              pay,
              bonus,
              due:bonus,
              cost,
              status:bonus>1?lang('Bonasi','Bonus'):bonus==0?lang('Sawa','Clear'):lang('Hasara','Loss')
            }

            return dt
    },
    pAtt = pA.map(at=>AttendData(at))
      
    SAOBJ.push({name:'att',title:lang('Mchanganuo kwa wahusika wa Pampu','Pump Attendant sales Analyisis'),data:pAtt})

    let fn = '',fr='',tr='',rcount = 0,totr=''

    FUEL.forEach(fl=>{
        const fSales = PASaL.filter(f=>f.theFuel_id===fl.fuel)
        fn+=`<td class="pl-1" colspan=3 >${fl.fname} </td>`
        fr+=`<td>${lang('Kiasi','Qty')}<span class="text-primary">LTRS</span></td>
            <td>${lang('Ghalama','Cost')}<span class="text-primary">${fedha}</span></td>
            <td>${lang('Mauzo','Sales')}<span class="text-primary">${fedha}</span></td>
               `
        totr+=`
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0)).toLocaleString()}</td>
     
        
        `      
    })

    pAtt.forEach(att=>{
        let frw = ''
        const prof = Number(att.pay) - Number(att.cost)
        att.fuel.forEach(f=>{
            frw+=`
               <td class="text-capitalize" >${Number(f.qty).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.cost).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.sales).toLocaleString()}</td> 
            `
        })
      
        tr+= `
              
             <tr class="smallFont" >
                <td>${rcount+=1}</td>         
                <td class="text-capitalize" > <a type="button" data-att=${att.att} class="bluePrint moreDetails" >${att.name}</a></td>         
                <td>${att.shift}</td> 
            
                <td>${Number(att.cost).toLocaleString()}</td>         
                <td>${Number(att.tot).toLocaleString()}</td>         
                <td>${Number(att.pay).toLocaleString()}</td> 

                        
                <td class=" ${att.bonus>0?'green':''} ${att.bonus<0?'brown':'' } " >${Number(att.bonus).toLocaleString()}</td>         
                <td class=" ${att.bonus>0?'green':''} ${att.bonus<0?'brown':'' } weight200" >${att.status}</td>         
                <td class="${prof>0?"green":'brown'} weight600" >${Number(prof).toLocaleString()}</td>         
                      
             </tr>
        `
    })

    const  tb = `
    <table class="table table-bordered table-sm" id="attTable" >
            <thead>
                <tr class="weight600 smallerFont" >
                    <th class="pl-1"  >#</th>
                    <th class="pl-1"  >${lang('Mhusika/Pampu','Pampu/Attendant')} </th>
                    <th class="pl-1"  >${lang('Zamu','Shifts')} </th>

                    

                    <th class="pl-1"  >${lang('Ghalama Jumla','Total Cost')}<span class="text-primary">${fedha}</span> </th>
                    <th class="pl-1"  >${lang('Mauzo Jumla','Total Sales')}<span class="text-primary">${fedha}</span> </th>
                    <th class="pl-1"  >${lang('Ilolipwa','Paid')} <span class="text-primary">${fedha}</span></th>
                    <th class="pl-1"  >${lang('Bonasi/Hasara','Bonus/Loss')}<span class="text-primary">${fedha}</span> </th>
                    <th class="pl-1"  >${lang('Statasi Bonasi ','Bonus Status')} </th>
                    <th class="pl-1"  >${lang('Faida','Profit')} <span class="text-primary">${fedha}</span></th>
           


            </thead> 
            <tbody>
               ${tr}

                               <tr class="weight600 smallFont" > 
                                    <td> ${lang('Jumla','Total')} </td>
                                    <td></td>
                                    <td>${PASale.length}</td>
                                  
                                     <td class="text-capitalize" >${Number(totCost).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totSale).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totPay).toLocaleString()}</td> 

                                     <td class=" ${totBonus>0?'green':''} ${totBonus<0?'brown':'' } " >${Number(totBonus).toLocaleString()}</td>         
                                    <td class=" ${totBonus>0?'green':''} ${totBonus<0?'brown':'' } weight200" >${GStatus}</td>         
                                    <td class="${totProf>0?"green":'brown'} weight600" >${Number(totProf).toLocaleString()}</td>  
                                </tr>    
            </tbody>
            </table>
    `
    
 
    $('#pAttendtable').html(tb)
    $('#attTable').DataTable()
}

const customerTable = d =>{
    const {sale,saL} = d,
          
        PASale = sale?.filter(att=>att.cust!=null),
        PASaL = saL.filter(a=>a.cust!=null),
        totCost = PASaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
        totPay = PASale.reduce((a,b)=>a+Number(b.payed),0),
        totSale = PASale.reduce((a,b)=>a+Number(b.amount),0),
        Totdue =totPay-totSale,
        totProf = totPay - totCost,
        

        pA = [... new Set(PASale.map(att=>att.cust))],
        AttendData = (at) =>{
        const Atsa = PASale.filter(a=>a.cust===at),
              AtsaL = PASaL.filter(a=>a.cust===at),
              atF = FUEL.map(f=>attendFuel(f))
             
         function  attendFuel(f){
              
               const fAtsaL = AtsaL.filter(a=>a.theFuel_id===f.fuel) ,
                fDt = {
                  fuel:f.fname,
                  id:f.fuel,
                  qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                  cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                  sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
               } 
               
               return fDt
         }    
         
        const tot = Atsa.reduce((a,b)=>a+Number(b.amount),0),
              pay=Atsa.reduce((a,b)=>a+Number(b.payed),0),
              cost = AtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
              due = pay-tot,
              dt= {
              name:`${Atsa[0].custN} `,
              cust:Atsa[0].cust,
              shift:Atsa.length,
              fuel: atF,
              tot,
              pay,
              due,
              cost,
          
            }

            return dt
    },
    pAtt = pA.map(at=>AttendData(at))

    SAOBJ.push({name:'cust',title:lang('Mchanganuo wa Mauzo kwa wateja Muhimu','Credit Order customer sales Analyisis'),data:pAtt})

    let fn = '',fr='',tr='',rcount = 0,totr=''

    FUEL.forEach(fl=>{
        const fSales = PASaL.filter(f=>f.theFuel_id===fl.fuel)
        fn+=`<td class="pl-1" colspan=3 >${fl.fname} </td>`
        fr+=`<td>${lang('Kiasi','Qty')}<span class="text-primary">LTRS</span></td>
            <td>${lang('Ghalama','Cost')}<span class="text-primary">${fedha}</span></td>
            <td>${lang('Mauzo','Sales')}<span class="text-primary">${fedha}</span></td>
               `
        totr+=`
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0)).toLocaleString()}</td>
     
        
        `      

    })

    pAtt.forEach(att=>{
        let frw = ''
        const prof = Number(att.pay) - Number(att.cost)
        att.fuel.forEach(f=>{
            frw+=`
               <td class="text-capitalize" >${Number(f.qty).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.cost).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.sales).toLocaleString()}</td> 
            `
        })
      
        tr+= `
              
             <tr class="smallFont" >
                <td>${rcount+=1}</td>         
                <td class="text-capitalize" > <a type="button" data-cust=${att.cust} class="bluePrint moreDetails" >${att.name}</a></td>         
                <td>${att.shift}</td> 
               
                <td>${Number(att.cost).toLocaleString()}</td>         
                <td>${Number(att.tot).toLocaleString()}</td>         
                <td>${Number(att.pay).toLocaleString()}</td> 

                        
                <td class=" ${att.due>0?'green':''} ${att.due<0?'brown':'' } " >${Number(att.due).toLocaleString()}</td>         
                    
                <td class="${prof>0?"green":'brown'} weight600" >${Number(prof).toLocaleString()}</td>         
                      
             </tr>
        `
    })

    const  tb = `
          <table class="table table-bordered table-sm" id="custmerTable" >
            <thead>
                <tr class="weight600 smallerFont" >
                    <th class="pl-1"  >#</th>
                    <th class="pl-1"  >${lang('Customer','Mteja')} </th>
                    <th class="pl-1"  >${lang('Ankara','Invoices')} </th>

                 

                    <th class="pl-1"  >${lang('Ghalama Jumla','Total Cost')}<span class="text-primary">${fedha}</span> </th>
                    <th class="pl-1"  >${lang('Mauzo Jumla','Total Sales')}<span class="text-primary">${fedha}</span> </th>
                    <th class="pl-1"  >${lang('Ilolipwa','Paid')} <span class="text-primary">${fedha}</span></th>
                    <th class="pl-1"  >${lang('Deni','Due')}<span class="text-primary">${fedha}</span> </th>
                    <th class="pl-1"  >${lang('Faida','Profit')} <span class="text-primary">${fedha}</span></th>
                  
                    </tr>



            </thead> 
            <tbody>
               ${tr}

                               <tr class="weight600 smallerFont" > 

                                    <td> ${lang('Jumla','Total')} </td>
                                    <td></td>
                                    <td>${PASale.length}</td>
                                 
                                     <td class="text-capitalize" >${Number(totCost).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totSale).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totPay).toLocaleString()}</td> 

                                     <td class=" ${Totdue>0?'green':''} ${Totdue<0?'brown':'' } " >${Number(Totdue).toLocaleString()}</td>         
                                            
                                    <td class="${totProf>0?"green":'brown'} weight600" >${Number(totProf).toLocaleString()}</td>  
                                </tr>    
            </tbody>
    `
    
   

    $('#custSaTable').html(tb)


    $('#custmerTable').DataTable()
}
    
const dateSaleTable = d =>{
        const {sale,saL} = d,
            PASale = sale,
            PASaL = saL,
            totCost = PASaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
            totPay = PASale.reduce((a,b)=>a+Number(b.payed),0),
            totSale = PASale.reduce((a,b)=>a+Number(b.amount),0),
            Totdue =  PASale.filter(sa=>sa.due>=0 && sa.customer_id!=null).reduce((a,b)=>a+Number(b.due),0),
            totProf = totPay - totCost,
            {tFr,tTo} = VDATA,
            diff = moment(tTo).diff(moment(tFr),'months'),
            formt = diff>0?'MMMM, YYYY':'DD/MM/YYYY',

            flter = st=>moment(st.date).format(formt),
            Stxns = [... new Set(PASale.map(st=>flter(st)))],
            StationData = (at) =>{
            const ftr = a=>moment(a.date).format(formt)===at,
                    Atsa = PASale.filter(a=>ftr(a)),
                AtsaL = PASaL.filter(a=>ftr(a)),
                atF = FUEL.map(f=>StaxnFuel(f))
                
            function  StaxnFuel(f){
                
                const fAtsaL = AtsaL.filter(a=>a.theFuel_id===f.fuel) ,
                    fDt = {
                    fuel:f.fname,
                    id:f.fuel,
                    qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                    cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                    sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                } 
                
                return fDt
            }    
            
            const tot = Atsa.reduce((a,b)=>a+Number(b.amount),0),
                pay=Atsa.reduce((a,b)=>a+Number(b.payed),0),
                cost = AtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                due = Atsa.filter(sa=>sa.due>=0 && sa.customer_id!=null).reduce((a,b)=>a+Number(b.due),0),
                dt= {
                name:at,
                shift:Atsa.length,
                fuel: atF,
                //   st:Atsa[0].st,
                tot,
                pay,
                due,
                cost,
            
                }

                return dt
        },
        Staxns = Stxns.map(at=>StationData(at))
        
        let fn = '',fr='',tr='',rcount = 0,totr=''

    FUEL.forEach(fl=>{
        const fSales = PASaL.filter(f=>f.theFuel_id===fl.fuel)
        fn+=`<td class="pl-1" colspan=3 >${fl.fname} </td>`
        fr+=`<td>${lang('Kiasi','Qty')}<span class="text-primary">LTRS</span></td>
            <td>${lang('Ghalama','Cost')}<span class="text-primary">${fedha}</span></td>
            <td>${lang('Mauzo','Sales')}<span class="text-primary">${fedha}</span></td>
               `
        totr+=`
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0)).toLocaleString()}</td>
     
        
        `      

    })
    const durxn = diff>0?lang('Mwezi','Monthly'):lang('Siku','Daily')
    SAOBJ.push({name:'dt',title:lang(`Mauzo kwa kila ${durxn}`,`${durxn} sales Analyisis`),data:Staxns})

    Staxns.forEach(att=>{
        let frw = ''
        const prof = Number(att.pay) - Number(att.cost)
        att.fuel.forEach(f=>{
            frw+=`
               <td class="text-capitalize" >${Number(f.qty).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.cost).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.sales).toLocaleString()}</td> 
            `
        })
      
        tr+= `
              
             <tr class="smallFont" >
                <td>${rcount+=1}</td>         
                <td class="text-capitalize" > <a type="button" data-format="${formt}" data-date="${att.name}" class="bluePrint moreDetails" >${att.name}</a></td>         
                <td>${att.shift}</td> 
                 ${frw} 
                <td>${Number(att.cost).toLocaleString()}</td>         
                <td>${Number(att.tot).toLocaleString()}</td>         
                <td>${Number(att.pay).toLocaleString()}</td> 

                        
                <td class=" ${att.due>0?'brown':''}  } " >${Number(att.due).toLocaleString()}</td>         
                    
                <td class="${prof>0?"green":'brown'} weight600" >${Number(prof).toLocaleString()}</td>         
                      
             </tr>
        `
    })

    const  tb = `
      
            <thead>
                <tr class="weight600 smallerFont" >
                    <td class="pl-1" rowspan=2 >#</td>
                    <td class="pl-1" rowspan=2 >${diff>0?lang('Mwezi','Month'):lang('Tarehe','Date')} </td>
                    <td class="pl-1" rowspan=2 >${lang('Ankara/Zamu','Shifts/Invoices')} </td>

                    ${fn}

                    <td class="pl-1" rowspan=2 >${lang('Ghalama Jumla','Total Cost')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Mauzo Jumla','Total Sales')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Ilolipwa','Paid')} <span class="text-primary">${fedha}</span></td>
                    <td class="pl-1" rowspan=2 >${lang('Deni','Due')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Faida','Profit')} <span class="text-primary">${fedha}</span></td>
                  
                    </tr>

                    <tr class="weight600 smallerFont" >
                        ${fr}

                    </tr>


            </thead> 
            <tbody>
               ${tr}

                               <tr class="weight600 smallerFont" > 
                                    <td colspan=2 > ${lang('Jumla','Total')} </td>
                                    <td>${PASale.length}</td>
                                    ${totr}
                                     <td class="text-capitalize" >${Number(totCost).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totSale).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totPay).toLocaleString()}</td> 

                                     <td class=" ${Totdue>0?'brown':''} " > ${Number(Totdue).toLocaleString()}</td>         
                                            
                                    <td class="${totProf>0?"green":'brown'} weight600" >${Number(totProf).toLocaleString()}</td>  
                                </tr>    
            </tbody>
    `

    $('#saleByDateTable').html(tb)

}

const detSummaryTable = d =>{
        const {sale,saL} = d,
       
        PASale = sale,
        PASaL = saL,
        totCost = PASaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
        totPay = PASale.reduce((a,b)=>a+Number(b.payed),0),
        totSale = PASale.reduce((a,b)=>a+Number(b.amount),0),
        Totdue =  PASale.filter(sa=>sa.due>=0 && sa.customer_id!=null).reduce((a,b)=>a+Number(b.due),0),
        totProf = totPay - totCost,
        Stxns = [... new Set(PASale.map(st=>st.st))],
        StationData = (at) =>{
        const Atsa = PASale.filter(a=>a.st===at),
              AtsaL = PASaL.filter(a=>a.st===at),
              atF = FUEL.map(f=>StaxnFuel(f))
             
         function  StaxnFuel(f){
              
               const fAtsaL = AtsaL.filter(a=>a.theFuel_id===f.fuel) ,
                fDt = {
                  fuel:f.fname,
                  id:f.fuel,
                  qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                  cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                  sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
               } 
               
               return fDt
         }    
         
        const tot = Atsa.reduce((a,b)=>a+Number(b.amount),0),
              pay=Atsa.reduce((a,b)=>a+Number(b.payed),0),
              cost = AtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
              due = Atsa.filter(sa=>sa.due>=0 && sa.customer_id!=null).reduce((a,b)=>a+Number(b.due),0),
              dt= {
              name:Atsa[0].stName,
              shift:Atsa.length,
              fuel: atF,
              st:Atsa[0].st,
              tot,
              pay,
              due,
              cost,
          
            }

            return dt
    },
    Staxns = Stxns.map(at=>StationData(at))
    SAOBJ.push({name:'delt',title:lang(`Mauzo kwa kila Kituo`,`Station sales Analyisis`),data:Staxns})

        let fn = '',fr='',tr='',rcount = 0,totr=''

    FUEL.forEach(fl=>{
        const fSales = PASaL.filter(f=>f.theFuel_id===fl.fuel)
        fn+=`<td class="pl-1" colspan=3 >${fl.fname} </td>`
        fr+=`<td>${lang('Kiasi','Qty')}<span class="text-primary">LTRS</span></td>
            <td>${lang('Ghalama','Cost')}<span class="text-primary">${fedha}</span></td>
            <td>${lang('Mauzo','Sales')}<span class="text-primary">${fedha}</span></td>
               `
        totr+=`
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0)).toLocaleString()}</td>
     
        
        `      

    })

    Staxns.forEach(att=>{
        let frw = ''
        const prof = Number(att.pay) - Number(att.cost)
        att.fuel.forEach(f=>{
            frw+=`
               <td class="text-capitalize" >${Number(f.qty).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.cost).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.sales).toLocaleString()}</td> 
            `
        })
      
        tr+= `
              
             <tr class="smallFont" >
                <td>${rcount+=1}</td>         
                <td class="text-capitalize" > <a type="button" data-st=${att.st} class="bluePrint moreDetails" >${att.name}</a></td>         
                <td>${att.shift}</td> 
                 ${frw} 
                <td>${Number(att.cost).toLocaleString()}</td>         
                <td>${Number(att.tot).toLocaleString()}</td>         
                <td>${Number(att.pay).toLocaleString()}</td> 

                        
                <td class=" ${att.due>0?'brown':''}  } " >${Number(att.due).toLocaleString()}</td>         
                    
                <td class="${prof>0?"green":'brown'} weight600" >${Number(prof).toLocaleString()}</td>         
                      
             </tr>
        `
    })

    const  tb = `
            <thead>
                <tr class="weight600 smallerFont" >
                    <td class="pl-1" rowspan=2 >#</td>
                    <td class="pl-1" rowspan=2 >${lang('Kituo','Station')} </td>
                    <td class="pl-1" rowspan=2 >${lang('Mauzo','Sales')} </td>

                    ${fn}

                    <td class="pl-1" rowspan=2 >${lang('Ghalama Jumla','Total Cost')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Mauzo Jumla','Total Sales')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Ilolipwa','Paid')} <span class="text-primary">${fedha}</span></td>
                    <td class="pl-1" rowspan=2 >${lang('Deni','Due')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Faida','Profit')} <span class="text-primary">${fedha}</span></td>
                  
                    </tr>

                    <tr class="weight600 smallerFont" >
                        ${fr}

                    </tr>


            </thead> 
            <tbody>
               ${tr}

                               <tr class="weight600 smallerFont" > 
                                    <td colspan=2 > ${lang('Jumla','Total')} </td>
                                    <td>${PASale.length}</td>
                                    ${totr}
                                     <td class="text-capitalize" >${Number(totCost).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totSale).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totPay).toLocaleString()}</td> 

                                     <td class=" ${Totdue>0?'brown':''} " > ${Number(Totdue).toLocaleString()}</td>         
                                            
                                    <td class="${totProf>0?"green":'brown'} weight600" >${Number(totProf).toLocaleString()}</td>  
                                </tr>    
            </tbody>
    `

    $('#staxnsTable').html(tb)

}


const OverallTable = d =>{
        const {sale,saL} = d,
       
        PASale = sale,
        PASaL = saL,
        totCost = PASaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
        totPay = PASale.reduce((a,b)=>a+Number(b.payed),0),
        totSale = PASale.reduce((a,b)=>a+Number(b.amount),0),
        Totdue =  PASale.filter(sa=>sa.due>=0 && sa.customer_id!=null).reduce((a,b)=>a+Number(b.due),0),
        totProf = totPay - totCost,
        Stxns = [0,1], //0 for pump attentant and 1 for customers
        StationData = (at) =>{
        const Atsa = at?PASale.filter(a=>a.cust!=null):PASale.filter(a=>a.pAtt!=null),
              AtsaL = at?PASaL.filter(a=>a.cust!=null):PASaL.filter(a=>a.pAtt!=null),
              atF = FUEL.map(f=>StaxnFuel(f))
             
         function  StaxnFuel(f){
              
               const fAtsaL = AtsaL.filter(a=>a.theFuel_id===f.fuel) ,
                fDt = {
                  fuel:f.fname,
                  id:f.fuel,
                  qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                  cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                  sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
               } 
               
               return fDt
         }    
         
        const tot = Atsa.reduce((a,b)=>a+Number(b.amount),0),
              pay=Atsa.reduce((a,b)=>a+Number(b.payed),0),
              cost = AtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
              due = Atsa.filter(sa=>sa.due>=0 && sa.customer_id!=null).reduce((a,b)=>a+Number(b.due),0),
              dt= {
              name:at?lang('Wateja Muhimu','Important Customer'):lang('Mhusika wa Pampu','Pump Attendant'),
              sale:Atsa.length,
              fuel: atF,
            //   st:Atsa[0].st,
              at,
              tot,
              pay,
              due,
              cost,
          
            }

            return dt
    },
    Staxns = Stxns.map(at=>StationData(at))
    SAOBJ.push({name:'ovr',title:lang(`Mauzo kwa wahusika wa pampu na wateja Muhimu kwa ujumla`,`Pump Attendant and Credit sales Analyisis`),data:Staxns})

        let fn = '',fr='',tr='',rcount = 0,totr=''

    FUEL.forEach(fl=>{
        const fSales = PASaL.filter(f=>f.theFuel_id===fl.fuel)
        fn+=`<td class="pl-1" colspan=3 >${fl.fname} </td>`
        fr+=`<td>${lang('Kiasi','Qty')}<span class="text-primary">LTRS</span></td>
            <td>${lang('Ghalama','Cost')}<span class="text-primary">${fedha}</span></td>
            <td>${lang('Mauzo','Sales')}<span class="text-primary">${fedha}</span></td>
               `
        totr+=`
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0)).toLocaleString()}</td>
     
        
        `      

    })

    Staxns.forEach(att=>{
        let frw = ''
        const prof = Number(att.pay) - Number(att.cost)
        att.fuel.forEach(f=>{
            frw+=`
               <td class="text-capitalize" >${Number(f.qty).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.cost).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.sales).toLocaleString()}</td> 
            `
        })
      
        tr+= `
              
             <tr class="smallFont" >
                    
                <td class="text-capitalize" > <label type="button" for="${att.at?'saleByCustomerBtn':'saleByAttBtn'}" data-st=${att.st} class="bluePrint" >${att.name}</label></td>         
                <td>${Number(att.sale).toLocaleString()}</td>
                 ${frw} 
                <td>${Number(att.cost).toLocaleString()}</td>         
                <td>${Number(att.tot).toLocaleString()}</td>         
                <td>${Number(att.pay).toLocaleString()}</td> 

                        
                <td class=" ${att.due>0?'brown':''}  } " >${Number(att.due).toLocaleString()}</td>         
                    
                <td class="${prof>0?"green":'brown'} weight600" >${Number(prof).toLocaleString()}</td>         
                      
             </tr>
        `
    })

    const  tb = `
            <thead>
                <tr class="weight600 smallerFont" >
                 
                   
                    <td class="pl-1" rowspan=2 >${lang('Mauzo Kutoka','Sales From')} </td>
                    <td class="pl-1" rowspan=2 >${lang('Ankara/Zamu','Shifts/Ivoices')} </td>

                    ${fn}

                    <td class="pl-1" rowspan=2 >${lang('Ghalama Jumla','Total Cost')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Mauzo Jumla','Total Sales')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Ilolipwa','Paid')} <span class="text-primary">${fedha}</span></td>
                    <td class="pl-1" rowspan=2 >${lang('Deni','Due')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Faida','Profit')} <span class="text-primary">${fedha}</span></td>
                  
                    </tr>

                    <tr class="weight600 smallerFont" >
                        ${fr}

                    </tr>


            </thead> 
            <tbody>
               ${tr}

                               <tr class="weight600 smallerFont" > 
                                    <td  > ${lang('Jumla','Total')} </td>
                                    <td>${PASale.length}</td>
                                    ${totr}
                                     <td class="text-capitalize" >${Number(totCost).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totSale).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totPay).toLocaleString()}</td> 

                                     <td class=" ${Totdue>0?'brown':''} " > ${Number(Totdue).toLocaleString()}</td>         
                                            
                                    <td class="${totProf>0?"green":'brown'} weight600" >${Number(totProf).toLocaleString()}</td>  
                                </tr>    
            </tbody>
    `

    $('#generalSaleTable').html(tb)

}

// const salePay = d =>{
//         const {pay,sale} = d,
//         phd = lang('Malipo ya Mauzo','Sales Payments'),
//         custPay = pay.filter(c=>c.cust!=null),
//         totAmo = pay.reduce((a,b)=>a+Number(b.Amount),0),
//         custDue = Number(custPay[Number(custPay.length)-1]?.rem),
//         totDue = sale.reduce((a,b)=>a+Number(b.due),0),
       
//         totreqAmo =  custDue+totAmo
        
       

//  const  {st} = filters(),
        
//         acc = [0,1],
//         payb = acc.map(p=>custAttpay(p))

//               function custAttpay(p){
                   
//                    const payf = p?p=>p.cust!=null:p=>p.pAtt!=null,
//                         saleP = sale.filter(payf),
//                         paymt = pay.filter(payf),
//                          pAmo = paymt.reduce((a,b)=>a+Number(b.Amount),0),
//                          rem = Number(paymt[Number(paymt.length)-1]?.rem), 
//                          loss = saleP.reduce((a,b)=>a+Number(b.due),0),
                        
//                          reqAmo =   p?rem+pAmo:saleP.reduce((a,b)=>a+Number(b.amount),0),    
//                         dt = {
                            
//                             val:p,
//                             name:p?lang('Wateja','Customer'):lang('MWahusika wa Pampu','Pump Attendants'),
//                             amount:pAmo,
//                             payT:paymt.filter(pm=>!pm.saRec).length,
//                             reqAmo,
//                             rem,
//                             loss

//                     }  
                    
//                     return dt
//               }

//         SAOBJ.push({name:'pay',title:lang(`Malipo ya mauzo kutoka Wahusika wa pampu na wateja Muhimu`,`Credit customer and pump attendats sales payments`),data:payb})      

//               let rw='', payTT = 0;
//               payb.forEach(p=>{
//                 let payT = 0;
//                 if(p.amount){payT=p.payT; payTT+=payT;}
//                  rw+=`<tr>
//                         <td><a type="button" class="bluePrint moreDetails" data-val=${p.val} data-hasamo=${p.amount}  data-pay=1 >${p.name}</a> </td>
//                         <td>${Number(payT).toLocaleString()}</td>
//                         <td>${Number(p.reqAmo).toLocaleString()}</td>
//                         <td>${Number(p.amount).toLocaleString()}</td>
//                         <td>${p.val?Number(p.rem).toLocaleString():'--'}</td>
//                         <td class="${p.loss<0?'green':p.loss>0?'brown':''}" >${Number(Math.abs(p.loss)).toLocaleString()}</td>
//                     </tr>`
//               })

//               rw+=`
//                     <tr class="weight600 smallFont" >
//                         <td> ${lang('Jumla','Total')} </td>
//                         <td> ${payTT} </td>
//                         <td>${Number(totreqAmo).toLocaleString()}</td>
//                         <td>${Number(totAmo).toLocaleString()}</td>
//                         <td>${Number(custDue).toLocaleString()}</td>
//                         <td class="${totDue>0?'brown':totDue<0?'green':''}" >${Number(Math.abs(totDue)).toLocaleString()}</td>
//                     </tr>
//               `
//               $('#payHead').text(phd)
//               $('#paymntData').html(rw)
            
              
       
// }



// More info....//

$('body').on('click','.moreDetails',function(){
 const att = Number($(this).data('att')) || 0 ,
       cust = Number($(this).data('cust')) || 0 ,
       st = Number($(this).data('st')) || 0 ,
       pay = Number($(this).data('pay')) || 0 ,
       val = Number($(this).data('val')) || 0 ,
       dt = $(this).data('date'),
       isMonth = $(this).data('month') ,
       fomat = $(this).data('format'),
       {tFr,tTo,rname} = VDATA,
        DFrom = moment(tFr).format('YYYY-MM-DD'),
        DTo = moment(tTo).format('YYYY-MM-DD'),
        tdy = moment().format('YYYY-MM-DD'),

        Rdate = DFrom==DTo?moment(tFr).format('DD/MM/YYYY'):`${moment(tFr).format('DD/MM/YYYY')} - ${moment(tTo).format('DD/MM/YYYY')}`,
        isToday = DTo == tdy?`${lang('Hadi','To')} ${moment(tTo).format('HH:mm')}`:'',
        hdt = `<span class="bluePrint"> ${Rdate} </span> ${isToday}`
        if(isMonth)$('#backBtn').data({cust,st,att,pay})
 

      $('#Salecateg').fadeOut()
      $('#MoreDetails').fadeIn(100)

    
   
      if(att)saleLAtt({hdt,att,fomat,isMonth})
      if(cust)saleLCustomer({hdt,cust,fomat,isMonth})
      if(st)saleLStaxn({hdt,st,fomat,isMonth}) 
      if(pay)paymentsView({hdt,val})
      if(dt&&!(att||cust||st))saleLDate({hdt,fomat,dt}) 

})




//Back Btn
$('#backBtn').click(function(){
    const cust = $(this).data('cust'),
          att = $(this).data('att'),
          st = $(this).data('st'),
          pay = $(this).data('pay'),
          val = $(this).data('payBy'),
          yr = $(this).data('val')
    
          if(!(cust||att||st||pay)){
              $('#MoreDetails').fadeOut();
              $('#Salecateg').fadeIn(100)
                   const chart = $('#riportSwitch button.btn-primary').data('chart')
                //    VOBJ=SAOBJ.find(n=>n.name===chart).data
                 const theObj = SAOBJ.find(n=>n.name===chart)
                 VOBJ = {data:theObj?.data,title:theObj?.title}
          }else{

            const       {tFr,tTo,rname} = VDATA,
                        DFrom = moment(tFr).format('YYYY-MM-DD'),
                        DTo = moment(tTo).format('YYYY-MM-DD'),
                        tdy = moment().format('YYYY-MM-DD'),

                        Rdate = DFrom==DTo?moment(tFr).format('DD/MM/YYYY'):`${moment(tFr).format('DD/MM/YYYY')} - ${moment(tTo).format('DD/MM/YYYY')}`,
                        isToday = DTo == tdy?`${lang('Hadi','To')} ${moment(tTo).format('HH:mm')}`:'',
                        hdt = `<span class="bluePrint"> ${Rdate} </span> ${isToday}`
                    
                
                    $('#backBtn').data({cust:0,st:0,att:0,pay:0})     
                    $('#Salecateg').fadeOut()
                    $('#MoreDetails').fadeIn(100)

                    if(att)saleLAtt({hdt,att})
                    if(cust)saleLCustomer({hdt,cust})
                    if(st)saleLStaxn({hdt,st}) 
                    if(pay&&!yr)paymentsView({hdt,val})
                    if(pay&&yr)custAttPayView({cust:val?yr:0,att:!val?yr:0})

          }
})

const saleLAtt = d =>{
    const {sale,saL} = VDATA,
           {st} = filters(),
           {hdt,att} = d,
           isMonth = d?.isMonth,
           fomat = d?.fomat,
           h = `${lang('Orodha ya mauzo na Mhusika wa Pampu','Sales List By Pump Attendant')}  ${isMonth?`<span class="bluePrint">${isMonth}</span>`:hdt}`,
           {tFr,tTo} = VDATA,
           diff = moment(tTo).diff(moment(tFr),'months'),
           formt = diff>0?'MMMM, YYYY':'DD/MM/YYYY'
             
        let  AttSa = sale.filter(sa=>sa.pAtt===att),
             AttSaL = saL.filter(sa=>sa.pAtt===att)
             if(st) AttSa = AttSa.filter(sa=>sa.st===st)
             if(st) AttSaL = AttSaL.filter(sa=>sa.st===st)
             if(isMonth) AttSa = AttSa.filter(sa=>moment(sa.date).format(fomat)===isMonth)
             if(isMonth) AttSaL = AttSaL.filter(sa=>moment(sa.date).format(fomat)===isMonth)

    const   totCost = AttSaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
            totPay = AttSa.reduce((a,b)=>a+Number(b.payed),0),
            totSale = AttSa.reduce((a,b)=>a+Number(b.amount),0),

            totBonus =totPay-totSale,
            totProf = totPay - totCost,
            GStatus = totBonus>1?lang('Bonasi','Bonus'):totBonus==0?lang('Sawa','Clear'):lang('Hasara','Loss') ,
            attN = `${AttSa[0]?.pAtt_fname} ${AttSa[0]?.pAtt_lname}`,
                staxn = AttSa[0]?.stName,
                reportD = `<div class="col-6 col-lg-4">
                                      ${lang('Mhusika wa Pampu','Pump attendant')}:
                                </div>
                                <div class="col-6 col-lg-8 bluePrint text-capitalize">
                                   ${attN}
                                </div>
                                <div class="col-6 col-lg-4">
                                    ${lang('Kituo','Station')}:  
                                </div>
                                <div class="col-6 col-lg-8 bluePrint">
                                     ${staxn}  
                                </div>
                                <div class="col-6 col-lg-4">
                                    ${lang('Zamu','Shifts')}:  
                                </div>
                                <div class="col-6 col-lg-8 bluePrint">
                                     ${AttSa.length}  
                                </div>
                                
                                `
                      
                function  mapListDt(d){

                    const saLst = AttSaL.filter(a=>a.sale_id===d.id),
                           atF = FUEL.map(f=>attendFuel(f))
             
                    function  attendFuel(f){
                        
                        const fAtsaL = saLst.filter(a=>a.theFuel_id===f.fuel) ,
                            fDt = {
                            fuel:f.fname,
                            id:f.fuel,
                            qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                            cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                            sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                        } 
                        
                        return fDt
                    } 
                         
                    const theFuel = {fuel:atF}, 
                          tot = {   
                                    name:moment(d.date).format('DD/MM/YYYY HH:mm'),
                                    qty:saLst.reduce((a,b)=>a+Number(b.qty_sold),0),
                                    cost:saLst.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                                    sales:saLst.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                                    status:d.due<0?lang('Bonasi','Bonus'):d.due==0?lang('Sawa','Clear'):lang('Hasara','Loss'),
                                    due:d.payed - d.amount
                                } ,
                          LData = {...d,...theFuel,...tot}
                      
                    return LData

                } 

           const  flter = st=>moment(st.date).format(formt),
            Stxns = [... new Set(AttSa.map(st=>flter(st)))],
            StationData = (at) =>{
            const ftr = a=>moment(a.date).format(formt)===at,
                    Atsa = AttSa.filter(a=>ftr(a)),
                AtsaL = AttSaL.filter(a=>ftr(a)),
                atF = FUEL.map(f=>StaxnFuel(f))
                
            function  StaxnFuel(f){
                
                const fAtsaL = AtsaL.filter(a=>a.theFuel_id===f.fuel) ,
                    fDt = {
                    fuel:f.fname,
                    id:f.fuel,
                    qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                    cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                    sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                } 
                
                return fDt
            }    
            
            const sales = Atsa.reduce((a,b)=>a+Number(b.amount),0),
                payed=Atsa.reduce((a,b)=>a+Number(b.payed),0),
                cost = AtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                due = payed-sales,
                dt= {
                name:at,
                shift:Atsa.length,
                fuel: atF,
                //   st:Atsa[0].st,
                att:Atsa[0].pAtt,
                sales,
                payed,
                due,
                cost,
                status:due>0?lang('Bonasi','Bonus'):due==0?lang('Sawa','Clear'):lang('Hasara','Loss')
                }

                return dt
        },
        ListData = isMonth||diff==0?AttSa.map(sa=>mapListDt(sa)):Stxns.map(at=>StationData(at))

        
                
                $('#MoredetailRHeading span').html(h)
                $('#SaLDetail .row').html(reportD)

                    let fn = '',fr='',tr='',rcount = 0,totr=''

    FUEL.forEach(fl=>{
        const fSales = AttSaL.filter(f=>f.theFuel_id===fl.fuel)
        fn+=`<td class="pl-1" colspan=3 >${fl.fname} </td>`
        fr+=`<td>${lang('Kiasi','Qty')}<span class="text-primary">LTRS</span></td>
            <td>${lang('Ghalama','Cost')}<span class="text-primary">${fedha}</span></td>
            <td>${lang('Mauzo','Sales')}<span class="text-primary">${fedha}</span></td>
               `
        totr+=`
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0)).toLocaleString()}</td>
     
        
        `      
    })
   
    ListData.forEach(att=>{
        let frw = ''
        const prof = Number(att.payed) - Number(att.cost)
        att.fuel.forEach(f=>{
            frw+=`
               <td class="text-capitalize" >${Number(f.qty).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.cost).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.sales).toLocaleString()}</td> 
            `
        })
      
        tr+= `
              
             <tr class="smallFont">
                <td>${rcount+=1}</td>       
                ${isMonth||diff==0?`
                <td class="text-capitalize" >${att.name} </td> 
                <td class="text-capitalize" > <a type="button" data-sh=${att.shiftBy_id} class="bluePrint viewShift" >SH-${att.shCode}</a></td>         
                <td class="text-capitalize" > <a type="button" data-ses=${att.session_id} class="bluePrint viewSession" >${att.ses}</a></td>         
               
                    `:
                    `
                       <td class="text-capitalize" > <a type="button" data-format="${formt}" data-month="${att.name}" data-att=${att.att} data-date="${att.name}" class="bluePrint moreDetails" >${att.name}</a></td>         
                       <td>${att.shift}</td> 
                    `
                }


                 ${frw} 
                <td>${Number(att.cost).toLocaleString()}</td>         
                <td>${Number(att.sales).toLocaleString()}</td>         
                <td>${Number(att.payed).toLocaleString()}</td> 

                        
                <td class=" ${att.due>0?'green':''} ${att.due<0?'brown':'' } " >${Number(att.due).toLocaleString()}</td>         
                <td class=" ${att.due>0?'green':''} ${att.due<0?'brown':'' } weight200" >${att.status}</td>         
                <td class="${prof>0?"green":'brown'} weight600" >${Number(prof).toLocaleString()}</td>         
                      
             </tr>
        `
    })

    const  tb = `
         <table class="table table-sm table-bordered"  >
            <thead>
                <tr class="weight600 smallerFont" >
                    <td class="pl-1" rowspan=2 >#</td>

                    
                    ${isMonth||diff==0?`
                    <td class="pl-1" rowspan=2 >${lang('Tarehe','date')} </td>
                    <td class="pl-1" rowspan=2 >${lang('Zamu','Shifts')} </td>
                    <td class="pl-1" rowspan=2 >${lang('Mpango Zamu','Session')} </td>                        
                        `:`
                    <td class="pl-1" rowspan=2 >${lang('Mwezi','Month')} </td>
                    <td class="pl-1" rowspan=2 >${lang('Zamu','Shifts')} </td>
                        
                        `}


                    ${fn}

                    <td class="pl-1" rowspan=2 >${lang('Ghalama Jumla','Total Cost')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Mauzo Jumla','Total Sales')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Ilolipwa','Paid')} <span class="text-primary">${fedha}</span></td>
                    <td class="pl-1" rowspan=2 >${lang('Bonasi/Hasara','Bonus/Loss')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Statasi Bonasi ','Bonus Status')} </td>
                    <td class="pl-1" rowspan=2 >${lang('Faida','Profit')} <span class="text-primary">${fedha}</span></td>
                  
                    </tr>

                    <tr class="weight600 smallerFont" >
                        ${fr}

                    </tr>


            </thead> 
            <tbody>
               ${tr}

                               <tr class="weight600 smallFont" > 
                                    <td colspan=${isMonth||diff==0?4:2} > ${lang('Jumla','Total')} </td>
                                    ${isMonth||diff==0?'':`<td class="text-capitalize" >${Number(AttSa.length).toLocaleString()}</td> `}
                                    ${totr}
                                     <td class="text-capitalize" >${Number(totCost).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totSale).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totPay).toLocaleString()}</td> 

                                     <td class=" ${totBonus>0?'green':''} ${totBonus<0?'brown':'' } " >${Number(totBonus).toLocaleString()}</td>         
                                    <td class=" ${totBonus>0?'green':''} ${totBonus<0?'brown':'' } weight200" >${GStatus}</td>         
                                    <td class="${totProf>0?"green":'brown'} weight600" >${Number(totProf).toLocaleString()}</td>  
                                </tr>    
            </tbody>
            </table>
    `
    
    $('#saleList').html(tb)

           

}

const saleLCustomer = d =>{
    const {sale,saL} = VDATA,
           {st} = filters(),
           {hdt,cust} = d,
           isMonth = d?.isMonth,
           fomat = d?.fomat,
           {tTo,tFr} = VDATA,
           h = `${lang('Orodha ya mauzo kwa Mteja Muhimu','Sales List By Important Customer')}  ${isMonth?`<span class="bluePrint">${isMonth}</span>`:hdt}`,
           diff = moment(tTo).diff(moment(tFr),'months'),
           formt = diff>0?'MMMM, YYYY':'DD/MM/YYYY'

        let  AttSa = sale.filter(sa=>sa.cust===cust),
             AttSaL = saL.filter(sa=>sa.cust===cust)
             if(st) AttSa = AttSa.filter(sa=>sa.st===st)
             if(st) AttSaL = AttSaL.filter(sa=>sa.st===st)
             if(isMonth) AttSa = AttSa.filter(sa=>moment(sa.date).format(fomat)===isMonth)
             if(isMonth) AttSaL = AttSaL.filter(sa=>moment(sa.date).format(fomat)===isMonth)   

    const   totCost = AttSaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
            totPay = AttSa.reduce((a,b)=>a+Number(b.payed),0),
            totSale = AttSaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price_og),0),
            Payable = AttSa.reduce((a,b)=>a+Number(b.amount),0),
            disc = totSale - Payable,
            totBonus =totPay-totSale,
            totProf = totPay - totCost,

            avPrice = AttSaL.reduce((a,b)=>a+Number(b.sa_price_og),0)/(AttSaL.length||1),

            custN = AttSa[0]?.custN,
            custId = AttSa[0]?.customer_id,
            custAddr = AttSa[0]?.custAddr,
                staxn = st? AttSa[0]?.stName:lang('Vituo Vyote','All Stations'),
                reportD = `<div class="col-6 col-lg-4">
                                      ${lang('Mteja','Customer')}:
                                </div>
                                <div class="col-6  col-lg-8  text-capitalize">
                                   <a href="/salepurchase/ViewCustomer?i=${custId}"> ${custN} </a>
                                </div>

                                <div class="col-6 col-lg-4">
                                    ${lang('Anwani','Address')}:  
                                </div>
                                <div class="col-6  col-lg-8 bluePrint">
                                      <a href="/salepurchase/ViewCustomer?i=${custId}">${custAddr} </a>
                                </div>

                                <div class="col-6 col-lg-4">
                                    ${lang('Kituo','Station')}:  
                                </div>
                                <div class="col-6  col-lg-8 bluePrint">
                                     ${staxn}  
                                </div>
                                <div class="col-6 col-lg-4">
                                    ${lang('Ankara','Invoice(s)')}:  
                                </div>
                                <div class="col-6  col-lg-8 bluePrint">
                                     ${AttSa.length}  
                                </div>
                                <div class="col-6 col-lg-4">
                                    ${lang('Kiasi','Amount')}:  
                                </div>
                                <div class="col-6  col-lg-8 ">
                                     ${fedha}.${totSale.toLocaleString()} 
                                </div>
                                <div class="col-6 col-lg-4">
                                    ${lang('Ilolipwa','Paid')}:  
                                </div>
                                <div class="col-6  col-lg-8 ">
                                     ${fedha}.${totPay.toLocaleString()} 
                                </div>
                                <div class="col-6 ${Math.abs(totBonus)>0?'brown':''} col-lg-4">
                                    ${lang('Deni','Due')}:  
                                </div>
                                <div class="col-6 ${Math.abs(totBonus)>0?'brown':''}   col-lg-8 ">
                                     ${fedha}.${totBonus.toLocaleString()} 
                                </div>
                                
                                `
                // ListData = AttSa.map(sa=>mapList(sa))     
                const only_used_fuel = AttSaL.map(s=>s.theFuel_id)  
                function  mapListDt(d){

                    const saLst = AttSaL.filter(a=>a.sale_id===d.id),
                        //    atF = FUEL.map(f=>attendFuel(f))
                        atF = FUEL.filter(f=>only_used_fuel.includes(f.fuel)).map(f=>attendFuel(f))
                    function  attendFuel(f){
                        
                        const fAtsaL = saLst.filter(a=>a.theFuel_id===f.fuel) ,
                            fDt = {
                            fuel:f.fname,
                            id:f.fuel,
                            price:Number(fAtsaL.reduce((a,b)=>a+Number(b.sa_price_og),0))/fAtsaL.length||0,
                            qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                            cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                            sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price_og),0),
                        } 
                        
                        return fDt
                    } 
                         
                    const theFuel = {fuel:atF}, 
                          tot = {   qty:saLst.reduce((a,b)=>a+Number(b.qty_sold),0),
                                    cost:saLst.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                                    sales:saLst.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                                    price:Number(saLst.reduce((a,b)=>a+Number(b.sa_price_og),0))/saLst.length||0, 
                                    due:d.payed - d.amount,
                                    totAmo:saLst.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price_og),0),
                                    disc:Number(saLst.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price_og),0) - d.amount),
                                } ,
                          LData = {...d,...theFuel,...tot}
                      
                    return LData

                }  


                  
            const  flter = st=>moment(st.date).format(formt),
            Stxns = [... new Set(AttSa.map(st=>flter(st)))],
                StationData = (at) =>{
                const ftr = a=>moment(a.date).format(formt)===at,
                        Atsa = AttSa.filter(a=>ftr(a)),
                    AtsaL = AttSaL.filter(a=>ftr(a)),
                    atF = FUEL.filter(f=>only_used_fuel.includes(f.fuel)).map(f=>StaxnFuel(f))
                    
                function  StaxnFuel(f){
                    
                    const fAtsaL = AtsaL.filter(a=>a.theFuel_id===f.fuel) ,
                        fDt = {
                        fuel:f.fname,
                        id:f.fuel,
                        qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                        price:Number(fAtsaL.reduce((a,b)=>a+Number(b.sa_price_og),0))/fAtsaL.length||0,
                        cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                        sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                    } 
                    
                    return fDt
                }    
                
                const sales = Atsa.reduce((a,b)=>a+Number(b.amount),0),
                    payed=Atsa.reduce((a,b)=>a+Number(b.payed),0),
                    
                    totAmo = AtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price_og),0),
                    due = payed-sales,
                    dt= {
                    name:at,
                    shift:Atsa.length,
                    fuel: atF,
                    //   st:Atsa[0].st,
                    cust:Atsa[0].cust,
                   
                    sales,
                    payed,
                    due,
                    totAmo,
                    disc:Number(totAmo - sales),
                    // status:due>0?lang('Bonasi','Bonus'):due==0?lang('Sawa','Clear'):lang('Hasara','Loss')
                    }

                    return dt
            },
            ListData = isMonth||diff==0?AttSa.map(sa=>mapListDt(sa)):Stxns.map(at=>StationData(at)) 
                
                $('#MoredetailRHeading span').html(h)
                $('#SaLDetail .row').html(reportD)

                    let fn = '',fr='',tr='',rcount = 0,totr=''

    
    FUEL.filter(f=>only_used_fuel.includes(f.fuel)).forEach(fl=>{
        const fSales = AttSaL.filter(f=>f.theFuel_id===fl.fuel)
        fn+=`<td class="pl-1" colspan=3 >${fl.fname} </td>`
        fr+=`<td>${lang('Kiasi','Qty')}<span class="text-primary">LTRS</span></td>
            <td>${lang('Bei','Price')}<span class="text-primary">${fedha}</span></td>
            <td>${lang('Jumla','Total')}<span class="text-primary">${fedha}</span></td>
               `
        totr+=`
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.sa_price_og),0)/(fSales?.length||1)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0)).toLocaleString()}</td>
     
        
        `      
    })

   
    ListData.forEach(att=>{
        let frw = ''
        const prof = Number(att.payed) - Number(att.cost)
        att.fuel.forEach(f=>{
            
            frw+=`
               <td class="text-capitalize" >${Number(f.qty).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.price).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.sales).toLocaleString()}</td> 
            `
        })
      
        tr+= `
              
             <tr class="smallFont">
                <td>${rcount+=1}</td>         
                       
               
                ${isMonth||diff==0?`
                        <td class="text-capitalize" >${moment(att.date).format('DD/MM/YYYY HH:mm')} </td>      

                        ${!st?`<td>${att.stName}</td>`:''}
                        <td class="text-capitalize" > <a type="button" data-sa=${att.id} class="bluePrint viewSale" >INVO-${att.code}</a></td>         
                        <td class="text-capitalize" > <a type="button"  class="bluePrint viewSession" >${att.driver}</a></td>         
                        <td class="text-capitalize" > <a type="button"  class="bluePrint viewSession" >${att.vihecle}</a></td>         
                        <td class="text-capitalize" > <a type="button" data-ses=${att.by_id} class="bluePrint text-capitalize" >${att.byFn} ${att.byLn}</a></td>         
                    `:
                    `
                       <td class="text-capitalize" > <a type="button" data-format="${formt}" data-month="${att.name}" data-cust=${att.cust} data-date="${att.name}" class="bluePrint moreDetails" >${att.name}</a></td>         
                       <td>${att.shift}</td> 
                    `}


                 ${frw} 
                <td>${Number(att.totAmo).toLocaleString()}</td>         
                      
                <td>${Number(att.payed).toLocaleString()}</td> 

                        
                <td class=" ${att.due>0?'green':''} ${att.due<0?'brown':'' } " >${Number(att.due).toLocaleString()}</td>         
                       
                    
                      
             </tr>
        `
    })

    const  tb = `
    <table class="table table-sm table-bordered"  >
            <thead>
                <tr class="weight600 smallerFont" >
                    <td class="pl-1" rowspan=2 >#</td>
                

                    ${isMonth||diff==0?`
                        <td class="pl-1" rowspan=2 >${lang('Tarehe','date')} </td>
                        ${!st?`<td class="pl-1" rowspan=2 >${lang('Kituo','Station')} </td>`:''}
                        <td class="pl-1" rowspan=2 >${lang('Ankara','Invoice')} </td>
                        <td class="pl-1" rowspan=2 >${lang('Jina la Deleva','Driver Name')} </td>
                        <td class="pl-1" rowspan=2 >${lang('Gari/Chombo','Vihecle')} </td>
                        <td class="pl-1" rowspan=2 >${lang('Na','By')} </td>                 
                        `:`
                        <td class="pl-1" rowspan=2 >${lang('Mwezi','Month')} </td>
                        <td class="pl-1" rowspan=2 >${lang('Ankara','Invoices')} </td>
                        
                        `}

                    ${fn}

                    <td class="pl-1" rowspan=2 >${lang(' Jumla','Total')}<span class="text-primary">${fedha}</span> </td>
              
                    
                    <td class="pl-1" rowspan=2 >${lang('Ilolipwa','Paid')} <span class="text-primary">${fedha}</span></td>
                    <td class="pl-1" rowspan=2 >${lang('Deni','Debt')}<span class="text-primary">${fedha}</span> </td>
                  
                    </tr>

                    <tr class="weight600 smallerFont" >
                        ${fr}

                    </tr>


            </thead> 
            <tbody>
               ${tr}

                               <tr class="weight600 smallFont" > 
                                    <td colspan=${isMonth||diff==0?(!st?7:6):3} > ${lang('Jumla','Total')} </td>
                                   
                                    ${totr}
                                     <td class="text-capitalize" >${Number(totSale).toLocaleString()}</td> 
                            
                                     <td class="text-capitalize" >${Number(totPay).toLocaleString()}</td> 

                                     <td class=" ${totBonus>0?'green':''} ${totBonus<0?'brown':'' } " >${Number(totBonus).toLocaleString()}</td>         
                                          
                                </tr>    
            </tbody>
            </table>
    `
    
    $('#saleList').html(tb)

           

}

const saleLDate = d =>{
    const {sale,saL} = VDATA,
           {st} = filters(),
           {hdt,dt,fomat} = d,
           h = `${lang('Orodha ya Mauzo ','Sales List ')} <span class="bluePrint"> ${dt} </span>`

        let  AttSa = sale.filter(sa=>moment(sa.date).format(fomat)===dt),
             AttSaL = saL.filter(sa=>moment(sa.date).format(fomat)===dt)
         

    const   totCost = AttSaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
            totPay = AttSa.reduce((a,b)=>a+Number(b.payed),0),
            totSale = AttSa.reduce((a,b)=>a+Number(b.amount),0),
            totBonus =totPay-totSale,
            totProf = totPay - totCost,
       
                staxn = st? AttSa[0]?.stName:lang('Vituo Vyote','All Stations'),
                reportD = `

                                <div class="col-6 col-lg-4">
                                    ${lang('Kituo','Station')}:  
                                </div>
                                <div class="col-6  col-lg-8 bluePrint">
                                     ${staxn}  
                                </div>
                                <div class="col-6 col-lg-4">
                                    ${lang('Ankara','Invoice(s)')}:  
                                </div>
                                <div class="col-6  col-lg-8 bluePrint">
                                     ${AttSa.length}  
                                </div>
                                
                                `,
                ListData = AttSa.map(sa=>mapList(sa))       
                function  mapList(d){

                    const saLst = AttSaL.filter(a=>a.sale_id===d.id),
                           atF = FUEL.map(f=>attendFuel(f))
             
                    function  attendFuel(f){
                        
                        const fAtsaL = saLst.filter(a=>a.theFuel_id===f.fuel) ,
                            fDt = {
                            fuel:f.fname,
                            id:f.fuel,
                            qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                            cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                            sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                        } 
                        
                        return fDt
                    } 
                         
                    const theFuel = {fuel:atF}, 
                          tot = {   qty:saLst.reduce((a,b)=>a+Number(b.qty_sold),0),
                                    cost:saLst.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                                    sales:saLst.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                                    status:d.due<0?lang('Bonasi','Bonus'):d.due==0?lang('Sawa','Clear'):lang('Hasara','Loss')
                                } ,
                          LData = {...d,...theFuel,...tot}
                      
                    return LData

                }  
                
                $('#MoredetailRHeading span').html(h)
                $('#SaLDetail .row').html(reportD)

                    let fn = '',fr='',tr='',rcount = 0,totr=''

    FUEL.forEach(fl=>{
        const fSales = AttSaL.filter(f=>f.theFuel_id===fl.fuel)
        fn+=`<td class="pl-1" colspan=3 >${fl.fname} </td>`
        fr+=`<td>${lang('Kiasi','Qty')}<span class="text-primary">LTRS</span></td>
            <td>${lang('Ghalama','Cost')}<span class="text-primary">${fedha}</span></td>
            <td>${lang('Mauzo','Sales')}<span class="text-primary">${fedha}</span></td>
               `
        totr+=`
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0)).toLocaleString()}</td>
     
        
        `      
    })
   
    ListData.forEach(att=>{
        let frw = ''
        const prof = Number(att.payed) - Number(att.cost),
              due = att.cust?att.due:0
        att.fuel.forEach(f=>{
            frw+=`
               <td class="text-capitalize" >${Number(f.qty).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.cost).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.sales).toLocaleString()}</td> 
            `
        })
         
    
        tr+= `
              
             <tr class="smallFont">
                <td>${rcount+=1}</td>         
                <td class="text-capitalize" >${moment(att.date).format('DD/MM/YYYY HH:mm')} </td>      
                
               ${att.cust?`<td class="text-capitalize" > <a type="button" data-sa=${att.id} class="bluePrint viewSale" >SA-${att.code}</a></td> `:`
               <td class="text-capitalize" > <a type="button" data-sh=${att.shiftBy_id} class="bluePrint viewShift" >SH-${att.shCode}</a></td>
               `}  

                <td class="text-capitalize" > <a type="button" data-cust=${att.customer_id} class="bluePrint viewCustomer" >${att.cust?att.custN:'----'}</a></td>         
                <td class="text-capitalize" > <a type="button" data-att=${att.shiftBy_id} class="bluePrint viewSession" >${att.shiftBy_id?`${att.pAtt_fname}  ${att.pAtt_lname}`:'----'}</a></td>   

                <td class="text-capitalize" > <a type="button" data-ses=${att.session_id} class="bluePrint viewSession" >${att.ses}</a></td>         
               
                 ${frw} 
                <td>${Number(att.cost).toLocaleString()}</td>         
                <td>${Number(att.sales).toLocaleString()}</td>         
                <td>${Number(att.payed).toLocaleString()}</td> 

                        
                <td class=" ${due<0?'green':''} ${due>0?'brown':'' } " >${Number(due).toLocaleString()}</td>         
                       
                <td class="${prof>0?"green":'brown'} weight600" >${Number(prof).toLocaleString()}</td>         
                      
             </tr>
        `
    })

    const  tb = `
          <table class="table table-sm table-bordered"  >
            <thead>
                <tr class="weight600 smallerFont" >
                    <td class="pl-1" rowspan=2 >#</td>
                    <td class="pl-1" rowspan=2 >${lang('Tarehe','date')} </td>
                    
                    <td class="pl-1" rowspan=2 >${lang('Ankara/Zamu','Invoice/shift')} </td>

                    <td class="pl-1" rowspan=2 >${lang('Mteja','Customer')} </td>
                    <td class="pl-1" rowspan=2 >${lang('Mhusika','Attendand')} </td>

                    <td class="pl-1" rowspan=2 >${lang('Mpango Zamu','Session')} </td>

                    ${fn}

                    <td class="pl-1" rowspan=2 >${lang('Ghalama Jumla','Total Cost')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Mauzo Jumla','Total Sales')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Ilolipwa','Paid')} <span class="text-primary">${fedha}</span></td>
                    <td class="pl-1" rowspan=2 >${lang('Deni','Debt')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Faida','Profit')} <span class="text-primary">${fedha}</span></td>
                  
                    </tr>

                    <tr class="weight600 smallerFont" >
                        ${fr}

                    </tr>


            </thead> 
            <tbody>
               ${tr}

                               <tr class="weight600 smallFont" > 
                                    <td colspan=6 > ${lang('Jumla','Total')} </td>
                                   
                                    ${totr}
                                     <td class="text-capitalize" >${Number(totCost).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totSale).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totPay).toLocaleString()}</td> 

                                     <td class=" ${totBonus>0?'green':''} ${totBonus<0?'brown':'' } " >${Number(totBonus).toLocaleString()}</td>         
                                          
                                    <td class="${totProf>0?"green":'brown'} weight600" >${Number(totProf).toLocaleString()}</td>  
                                </tr>    
            </tbody>
            </table>
    `
    
    $('#saleList').html(tb)

           

}

const saleLStaxn = d =>{
    const {sale,saL} = VDATA,
        
           {hdt,st} = d,
       
           isMonth = d?.isMonth,
           fomat = d?.fomat,
           {tTo,tFr} = VDATA,
           h = `${lang('Orodha ya mauzo kwa Kituo','Sales List by Station')}  ${isMonth?`<span class="bluePrint">${isMonth}</span>`:hdt}`,
           diff = moment(tTo).diff(moment(tFr),'months'),
           formt = diff>0?'MMMM, YYYY':'DD/MM/YYYY'

        let  AttSa = sale.filter(sa=>sa.st===st),
             AttSaL = saL.filter(sa=>sa.st===st)
            if(isMonth) AttSa = AttSa.filter(sa=>moment(sa.date).format(fomat)===isMonth)
             if(isMonth) AttSaL = AttSaL.filter(sa=>moment(sa.date).format(fomat)===isMonth)
         

    const   totCost = AttSaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
            totPay = AttSa.reduce((a,b)=>a+Number(b.payed),0),
            totSale = AttSa.reduce((a,b)=>a+Number(b.amount),0),
            totBonus =totPay-totSale,
            totProf = totPay - totCost,

                staxn = AttSa[0]?.stName,
                reportD = `

                                <div class="col-6 col-lg-4">
                                    ${lang('Kituo','Station')}:  
                                </div>
                                <div class="col-6  col-lg-8 bluePrint">
                                     ${staxn}  
                                </div>
                                <div class="col-6 col-lg-4">
                                    ${lang('Ankara','Invoice(s)')}:  
                                </div>
                                <div class="col-6  col-lg-8 bluePrint">
                                     ${AttSa.length}  
                                </div>
                                
                                `
                // ListData = AttSa.map(sa=>mapList(sa))       
                function  mapListDt(d){

                    const saLst = AttSaL.filter(a=>a.sale_id===d.id),
                           atF = FUEL.map(f=>attendFuel(f))
             
                    function  attendFuel(f){
                        
                        const fAtsaL = saLst.filter(a=>a.theFuel_id===f.fuel) ,
                            fDt = {
                            fuel:f.fname,
                            id:f.fuel,
                            qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                            cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                            sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                        } 
                        
                        return fDt
                    } 
                         
                    const theFuel = {fuel:atF}, 
                          tot = {   qty:saLst.reduce((a,b)=>a+Number(b.qty_sold),0),
                                    cost:saLst.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                                    sales:saLst.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                                    due:d.cust?d.payed-d.amount:0
                                } ,
                          LData = {...d,...theFuel,...tot}
                      
                    return LData

                } 

                            const  flter = st=>moment(st.date).format(formt),
            Stxns = [... new Set(AttSa.map(st=>flter(st)))],
                StationData = (at) =>{
                const ftr = a=>moment(a.date).format(formt)===at,
                        Atsa = AttSa.filter(a=>ftr(a)),
                    AtsaL = AttSaL.filter(a=>ftr(a)),
                    atF = FUEL.map(f=>StaxnFuel(f))
                    
                function  StaxnFuel(f){
                    
                    const fAtsaL = AtsaL.filter(a=>a.theFuel_id===f.fuel) ,
                        fDt = {
                        fuel:f.fname,
                        id:f.fuel,
                        qty:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold),0),
                        cost:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                        sales:fAtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0),
                    } 
                    
                    return fDt
                }    
                
                const sales = Atsa.reduce((a,b)=>a+Number(b.amount),0),
                    payed=Atsa.reduce((a,b)=>a+Number(b.payed),0),
                    cost = AtsaL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0),
                    due = Atsa.filter(c=>c.cust!=null).reduce((a,b)=>a+Number(b.payed-b.amount),0),
                    dt= {
                    name:at,
                    shift:Atsa.length,
                    fuel: atF,
                    //   st:Atsa[0].st,
                    st:Atsa[0].st,
                    sales,
                    payed,
                    due,
                    cost,
                    // status:due>0?lang('Bonasi','Bonus'):due==0?lang('Sawa','Clear'):lang('Hasara','Loss')
                    }

                    return dt
            },
            ListData = isMonth||diff==0?AttSa.map(sa=>mapListDt(sa)):Stxns.map(at=>StationData(at)) 
                

                
                $('#MoredetailRHeading span').html(h)
                $('#SaLDetail .row').html(reportD)

                    let fn = '',fr='',tr='',rcount = 0,totr=''

    FUEL.forEach(fl=>{
        const fSales = AttSaL.filter(f=>f.theFuel_id===fl.fuel)
        fn+=`<td class="pl-1" colspan=3 >${fl.fname} </td>`
        fr+=`<td>${lang('Kiasi','Qty')}<span class="text-primary">LTRS</span></td>
            <td>${lang('Ghalama','Cost')}<span class="text-primary">${fedha}</span></td>
            <td>${lang('Mauzo','Sales')}<span class="text-primary">${fedha}</span></td>
               `
        totr+=`
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0)).toLocaleString()}</td>
        <td>${Number(fSales.reduce((a,b)=>a+Number(b.qty_sold*b.sa_price),0)).toLocaleString()}</td>
     
        
        `      
    })
  
    ListData.forEach(att=>{
        let frw = ''
        const prof = Number(att.payed) - Number(att.cost),
              due = att.due
        att.fuel.forEach(f=>{
            frw+=`
               <td class="text-capitalize" >${Number(f.qty).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.cost).toLocaleString()}</td> 
               <td class="text-capitalize" >${Number(f.sales).toLocaleString()}</td> 
            `
        })
         
    
        tr+= `
              
             <tr class="smallFont">
                <td>${rcount+=1}</td>         
              
                 ${isMonth||diff==0?`
                          <td class="text-capitalize" >${moment(att.date).format('DD/MM/YYYY HH:mm')} </td>      
                
                            ${att.cust?`<td class="text-capitalize" > <a type="button" data-sa=${att.id} class="bluePrint viewSale" >SA-${att.code}</a></td> `:`
                            <td class="text-capitalize" > <a type="button" data-sh=${att.shiftBy_id} class="bluePrint viewShift" >SH-${att.shCode}</a></td>
                            `}  


                            <td class="text-capitalize" > <a type="button" data-cust=${att.customer_id} class="bluePrint viewCustomer" >${att.cust?att.custN:'----'}</a></td>         
                            <td class="text-capitalize" > <a type="button" data-att=${att.shiftBy_id} class="bluePrint viewSession" >${att.shiftBy_id?`${att.pAtt_fname}  ${att.pAtt_lname}`:'----'}</a></td>   

                            <td class="text-capitalize" > <a type="button" data-ses=${att.session_id} class="bluePrint viewSession" >${att.ses}</a></td>  
                                                `:
                    `
                       <td class="text-capitalize" > <a type="button" data-format="${formt}" data-month="${att.name}" data-st=${att.st} data-date="${att.name}" class="bluePrint moreDetails" >${att.name}</a></td>         
                       <td>${att.shift}</td> 
                    `}

               
                 ${frw} 
                <td>${Number(att.cost).toLocaleString()}</td>         
                <td>${Number(att.sales).toLocaleString()}</td>         
                <td>${Number(att.payed).toLocaleString()}</td> 

                        
                <td class=" ${due>0?'green':''} ${due<0?'brown':'' } " >${Number(due).toLocaleString()}</td>         
                       
                <td class="${prof>0?"green":'brown'} weight600" >${Number(prof).toLocaleString()}</td>         
                      
             </tr>
        `
    })

    const  tb = `
           <table class="table table-sm table-bordered"  >
            <thead>
                <tr class="weight600 smallerFont" >
                    <td class="pl-1" rowspan=2 >#</td>
                  

                    ${isMonth||diff==0?`
                            <td class="pl-1" rowspan=2 >${lang('Tarehe','date')} </td>
                            
                            <td class="pl-1" rowspan=2 >${lang('Ankara/Zamu','Invoice/shift')} </td>

                            <td class="pl-1" rowspan=2 >${lang('Mteja','Customer')} </td>
                            <td class="pl-1" rowspan=2 >${lang('Mhusika','Attendand')} </td>

                            <td class="pl-1" rowspan=2 >${lang('Mpango Zamu','Session')} </td>              
                        `:`
                    <td class="pl-1" rowspan=2 >${lang('Mwezi','Month')} </td>
                    <td class="pl-1" rowspan=2 >${lang('Ankara','Invoices')} </td>
                        
                        `}

                    ${fn}

                    <td class="pl-1" rowspan=2 >${lang('Ghalama Jumla','Total Cost')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Mauzo Jumla','Total Sales')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Ilolipwa','Paid')} <span class="text-primary">${fedha}</span></td>
                    <td class="pl-1" rowspan=2 >${lang('Deni','Debt')}<span class="text-primary">${fedha}</span> </td>
                    <td class="pl-1" rowspan=2 >${lang('Faida','Profit')} <span class="text-primary">${fedha}</span></td>
                  
                    </tr>

                    <tr class="weight600 smallerFont" >
                        ${fr}

                    </tr>


            </thead> 
            <tbody>
               ${tr}

                               <tr class="weight600 smallFont" > 
                                    <td colspan=${isMonth||diff==0?6:3} > ${lang('Jumla','Total')} </td>
                                   
                                    ${totr}
                                     <td class="text-capitalize" >${Number(totCost).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totSale).toLocaleString()}</td> 
                                     <td class="text-capitalize" >${Number(totPay).toLocaleString()}</td> 

                                     <td class=" ${totBonus>0?'green':''} ${totBonus<0?'brown':'' } " >${Number(totBonus).toLocaleString()}</td>         
                                          
                                    <td class="${totProf>0?"green":'brown'} weight600" >${Number(totProf).toLocaleString()}</td>  
                                </tr>    
            </tbody>
            </table>
    `
    
    $('#saleList').html(tb)

           

}

const paymentsView = d =>{
    const {sale,pay} = VDATA,
          {st} = filters()
         let theSale = st?sale.filter(stn=>stn.st===st):sale,
             thePay = st?pay.filter(py=>py.st===st):pay  

    const {val,hdt} = d,
          
          hdg = val?`${lang('Malipo kutoka kwa wateja','Customer Payments')}  ${hdt}`:`${lang('Malipo kutoka kwa Wahusika wa Pampu','Pump Attendants Payments')}  ${hdt}`,
          payf = val?p=>p.cust!=null&&Number(p.Amount)>0:p=>p.pAtt!=null , 
          mapf = val?p=>p.cust:p=>p.pAtt,
          payMnt = thePay.filter(payf),
          Tsale = theSale.filter(payf)

         
   
    const    totAmo = payMnt.reduce((a,b)=>a+Number(b.Amount),0),
            custDue = val?Number(payMnt[Number(payMnt.length)-1]?.rem):0,
            totDue = Tsale.reduce((a,b)=>a+Number(b.due),0),
            totreqAmo =  custDue+totAmo,
        
        invoAmo = Tsale.reduce((a,b)=>a+Number(b.amount),0),
        postDue = totreqAmo - invoAmo,
          setVal = [...new Set(payMnt.map(mapf))],
          theDt = setVal.map(p=>getPayData(p))
          function getPayData(p){
                        const payfn = val?py=>py.cust===p:py=>py.pAtt===p,
                         saleP = theSale.filter(payfn),
                         paymt = payMnt.filter(payfn),
                         pAmo = paymt.reduce((a,b)=>a+Number(b.Amount),0),
                         rem = val?Number(paymt[Number(paymt.length)-1]?.rem):0, 
                         loss = saleP.reduce((a,b)=>a+Number(b.due),0),
                         invoAmo = saleP.reduce((a,b)=>a+Number(b.amount),0),
                         reqAmo =   val?(rem+pAmo):invoAmo,    
                        dt = {
                            
                            val:p,
                            name:val?paymt[0]?.custN:`${paymt[0]?.pAtt_fname}  ${paymt[0]?.pAtt_lname}`,
                            amount:pAmo,
                            payT:paymt.filter(pm=>!pm.saRec).length,
                            reqAmo,
                            rem,
                            loss,
                            postDue:reqAmo - invoAmo,
                            invoAmo

                    }

                
                    return dt
          }


            let rw='',payTT = 0; 
              
            theDt.forEach(p=>{
                let payT=0;
                if(p.amount>0) {payT=p.payT; payTT+=payT}
                rw+=`<tr>
                    <td><a type="button" class="bluePrint morePayDetails text-capitalize" data-has_amount=${payT}  ${val?`data-custm=${p.val}`:`data-attnd=${p.val}`}  >${p.name}</a> </td>
                    <td>${Number(payT).toLocaleString()}</td>
                    ${val?`<td>${Number(Number(p.postDue).toFixed(2)).toLocaleString()}</td>`:''}
                    ${val?`<td>${Number(Number(p.invoAmo).toFixed(2)).toLocaleString()}</td>`:''}


                    <td>${Number(Number(p.reqAmo).toFixed(2)).toLocaleString()}</td>
                    <td>${Number(Number(p.amount).toFixed(2)).toLocaleString()}</td>
                    ${val?`<td class="${p.rem>0?'brown':''}" >${val?Number(p.rem).toLocaleString():'--'}</td>`:''}
                    ${!val?`<td class="${p.loss<0?'green':p.loss>0?'brown':''}" >${Number(Math.abs(p.loss)).toLocaleString()}</td>`:''}
                </tr>`
            })

            rw+=`
                <tr  class="weight600 smallFont" >
                    <td > ${lang('Jumla','Total')} </td>
                    <td> ${payTT} </td>
                    ${val?`<td>${Number(postDue).toLocaleString()}</td>`:''}
                    ${val?`<td>${Number(invoAmo).toLocaleString()}</td>`:''}
                    
                    <td>${Number(totreqAmo).toLocaleString()}</td>
                    <td>${Number(totAmo).toLocaleString()}</td>
                    ${val?`<td class="${custDue>0?'brown':''}" >${Number(custDue).toLocaleString()}</td>`:''}
                    ${!val?`<td class="${totDue>0?'brown':totDue<0?'green':''}" >${Number(Math.abs(totDue)).toLocaleString()}</td>`:''}
                </tr>
            `

            const tb = `
            <table class="table table-sm table-bordered" id="payMntyiewTable" >
                    <thead>
                     <tr class="smallerFont" >
                            <th>${lang('Jina','Name')}</th>
                            <th>${lang('Malipo Yaliyofanyika','Payments Made')}</th>
                            ${val?`<th>${lang('Deni Nyuma','Post Due')} <span class="text-primary">${fedha}</span> </th>`:''}
                            ${val?`<th>${lang('Manunuzi','Invoice(s) Amount')} <span class="text-primary">${fedha}</span> </th>`:''}
                           
                            <th>${lang('Deni Jumla','Net Due Amount')} <span class="text-primary">${fedha}</span> </th>
                            <th>${lang('Pesa Ilolipwa','Paid Amount')} <span class="text-primary">${fedha}</span> </th>
                            ${val?`<th>${lang('Deni','Due')} <span class="text-primary">${fedha}</span> </th>`:''}
                            ${!val?`<th>${lang('Hasara','Loss')} <span class="text-primary">${fedha}</span> </th>`:''}
                          </tr>  
                        </thead>

                        <tbody id="paymntDataView" >
                            ${rw}
                        </tbody>
                        </table>
            `

          $('#SaLDetail .row').html('')
          $('#saleList').html(tb)
          $('#payMntyiewTable').DataTable()
          $('#MoredetailRHeading span').html(hdg)
     
}


// SWITCH BUTTONS......................//
$('.riportOn').click(function(){
    $('.riportOn').removeClass('btn-primary')
    $(this).addClass('btn-primary')
    
    
    $('#MoreDetails').hide()
    $('#Salecateg .DetailsTable').hide()

    $('#Salecateg').show()

    $('#MoredetailRHeading a').prop('hidden',0)
    $($(this).data('r')).fadeIn(100)
        $('#riportChatRist .btn-secondary').addClass('btn-light').removeClass('btn-secondary')
        $('#riportChatRist button').first().addClass('btn-secondary').removeClass('btn-light')


     const chart = $(this).data('chart')
      const theObj = SAOBJ.find(n=>n.name===chart)
      VOBJ = {data:theObj?.data,title:theObj?.title}
})

// For Pamnts more Details
$('body').on('click','.morePayDetails',function(){
 const att = Number($(this).data('attnd')) || 0 ,
       cust = Number($(this).data('custm')) || 0 ,
       {tFr,tTo} = VDATA,
       diff = moment(tTo).diff(moment(tFr),'months')
       hasAmo = Number($(this).data('has_amount')) || 0
       if(hasAmo<=0){
              return toastr.info(lang('Hakuna Malipo Yaliyopatikana','No Payments Found'),lang('Taarifa','Info'),{timeOut: 5000});
       }    
       if(diff){
           custAttPayView({att,cust})
       }else{
         if(att)pAttPayList({att})
         if(cust)custmPayList({cust})
       }

       $('#backBtn').data({pay:1,payBy:cust})
})

// For Pamnts more Details
$('body').on('click','.PayDetails',function(){
 const att = Number($(this).data('attnd')) || 0 ,
       cust = Number($(this).data('custm')) || 0 ,
       hasAmo = Number($(this).data('amo')) || 0 ,
       month = $(this).data('month')
      
       if(hasAmo<=0){
              return toastr.info(lang('Hakuna Malipo Yaliyopatikana','No Payments Found'),lang('Taarifa','Info'),{timeOut: 5000});  
       }
         if(att)pAttPayList({att,month})
         if(cust)custmPayList({cust,month})
      
      
       $('#backBtn').data({pay:1,payBy:cust,val:cust?cust:att})
})

const custAttPayView = d =>{
    const {pay,sale} = VDATA,
          {att,cust} = d,
          {st} = filters(),
          val = cust,
          fltr = att?p=>p.pAtt===att:p=>p.cust===cust

          let theSale = st?sale.filter(s=>s.st===st):sale,
              thePay = st?pay.filter(s=>s.st===st):pay
               
              theSale = theSale.filter(fltr)
              thePay = thePay.filter(fltr)
           
          const     totAmo = thePay.reduce((a,b)=>a+Number(b.Amount),0),
                    custDue = val?Number(thePay[Number(thePay.length)-1]?.rem):0,
                    totDue = theSale.reduce((a,b)=>a+Number(b.due),0),
                    totreqAmo =  custDue+totAmo,
                    payT = thePay.filter(pm=>!pm.saRec).length  ,
                    invoAmo = theSale.reduce((a,b)=>a+Number(b.amount),0),
                    postDue = totreqAmo - invoAmo  ,
                    hideAtt = att?'hidden':''

          const  attN = `${thePay[0]?.pAtt_fname} ${thePay[0]?.pAtt_lname}`,
                 custN = thePay[0]?.custN,
                staxn = st?thePay[0]?.stName:lang('Vito Vyote','All Stations'),
                reportD = `<div class="col-6 col-lg-4">
                                      ${att?lang('Mhusika wa Pampu','Pump attendant'):lang('Jina la Mteja','Customer Name')}:
                                </div>
                                <div class="col-6 col-lg-8 bluePrint text-capitalize">
                                   ${att?attN:custN}
                                </div>
                                <div class="col-6 col-lg-4">
                                    ${lang('Kituo','Station')}:  
                                </div>
                                <div class="col-6 col-lg-8 bluePrint">
                                     ${staxn}  
                                </div>


                                
                                <div class="col-6 col-lg-4">
                                    ${lang('Malipo','Payments')}:  
                                </div>
                                <div class="col-6 col-lg-8 bluePrint">
                                     ${payT}  
                                </div>

                                <div class="col-6 col-lg-4" ${hideAtt}  >
                                    ${lang('Deni Nyuma','Post Due')}:  
                                </div>
                                <div class="col-6 col-lg-8 " ${hideAtt} >
                                    <span class="text-primary">${fedha}</span>.${Number(postDue).toLocaleString()}  
                                </div>                               
                                <div class="col-6 col-lg-4" ${hideAtt} >
                                    ${lang('Manunuzi','Invoice(s) Amount')}:  
                                </div>
                                <div class="col-6 col-lg-8 " ${hideAtt} >
                                    <span class="text-primary">${fedha}</span>.${Number(invoAmo).toLocaleString()}  
                                </div>    

                                <div class="col-6 col-lg-4"  >
                                    ${lang('Kiasi Kinachotakiwa','Net Required Amount')}:  
                                </div>
                                <div class="col-6 col-lg-8 ">
                                    <span class="text-primary">${fedha}</span>.${Number(totreqAmo).toLocaleString()}  
                                </div>                               
                                <div class="col-6 col-lg-4">
                                    ${lang('Iliyolipwa','Paid Amount')}:  
                                </div>
                                <div class="col-6 col-lg-8 ">
                                    <span class="text-primary">${fedha}</span>.${Number(totAmo).toLocaleString()}  
                                </div>                               
                                <div class="col-6 col-lg-4 ">
                                     ${val?lang('Deni','Due'):totDue>0?lang('Hasara','Loss'):totDue==0?lang('Hasara/Bonasi','Loss/Bonus'):lang('Bonasi','Bonus')}:  
                                </div>
                                <div class="col-6 col-lg-8 ${totDue>0?'brown':''} ${totDue<0?'green':''}">
                                    <span class="text-primary">${fedha}</span>.${Number(Math.abs(val?custDue:totDue)).toLocaleString()}  
                                </div>                               
                                
                                `,
                
                months = [...new Set(thePay.map(m=>moment(m.tarehe).format('MMMM, YYYY')))],
                thePayDt = months.map(p=>paymnt(p))             
                function paymnt(p){
                    const payfn = py=>moment(py.date).format('MMMM, YYYY')===p,
                         saleP = theSale.filter(payfn),
                         paymt = thePay.filter(payfn),
                         pAmo = paymt.reduce((a,b)=>a+Number(b.Amount),0),
                         rem = val?Number(paymt[Number(paymt.length)-1]?.rem):0, 
                         loss = saleP.reduce((a,b)=>a+Number(b.due),0),
                         invoAmo = saleP.reduce((a,b)=>a+Number(b.amount),0),
                         reqAmo =   val?rem+pAmo:saleP.reduce((a,b)=>a+Number(b.amount),0),    
                        dt = {
                            
                            val:val?cust:att,
                            name:p,
                            amount:pAmo,
                            payT:paymt.filter(pm=>!pm.saRec).length,
                            reqAmo,
                            rem,
                            loss,
                            invoAmo,
                            postDue:reqAmo-invoAmo

                    }

                
                    return dt
                 }               
                     
         let rw='',payTT=0   
            thePayDt.reverse().forEach(p=>{
                if(p.amount>0)payTT+=1
                rw+=`<tr>
                    <td><a type="button" class="bluePrint PayDetails" data-amo=${p.amount} data-month="${p.name}"  ${val?`data-custm=${p.val}`:`data-attnd=${p.val}`}  >${p.name}</a> </td>
                    <td>${Number(p.amount>0?p.payT:0).toLocaleString()}</td>
                    ${val?`<td>${Number(p.postDue).toLocaleString()}</td>`:''}
                    ${val?`<td>${Number(p.invoAmo).toLocaleString()}</td>`:''}
                    <td>${Number(p.reqAmo).toLocaleString()}</td>
                    <td>${Number(p.amount||0).toLocaleString()}</td>
                    ${val?`<td class="${p.rem>0?'brown':''}" >${val?Number(p.rem).toLocaleString():'--'}</td>`:''}
                    ${!val?`<td class="${p.loss<0?'green':p.loss>0?'brown':''}" >${Number(Math.abs(p.loss)).toLocaleString()}</td>`:''}
                    ${!val?`<td class="${p.loss<0?'green':p.loss>0?'brown':''}" >${p.loss>0?lang('Hasara','Loss'):p.loss==0?lang('Sawa','Clear'):lang('Bonasi','Bonus')}</td>`:''}
                </tr>`
            })

            rw+=`
                <tr class="weight600 smallFont" >
                    <td> ${lang('Jumla','Total')} </td>
                    <td> ${payTT} </td>
                     ${val?`<td>${Number(postDue).toLocaleString()}</td>`:''}
                    ${val?`<td>${Number(invoAmo).toLocaleString()}</td>`:''}
                    <td>${Number(totreqAmo).toLocaleString()}</td>
                    <td>${Number(totAmo).toLocaleString()}</td>
                    ${val?`<td class="${custDue>0?'brown':''}" >${Number(custDue).toLocaleString()}</td>`:''}
                    ${!val?`<td class="${totDue>0?'brown':totDue<0?'green':''}" >${Number(Math.abs(totDue)).toLocaleString()}</td>`:''}
                    ${!val?`<td class="${totDue<0?'green':totDue>0?'brown':''}" >${totDue>0?lang('Hasara','Loss'):totDue==0?lang('Sawa','Clear'):lang('Bonasi','Bonus')}</td>`:''}  
                    </tr>
            `

            const tb = `
                 <table class="table table-sm table-bordered"  >
                    <thead>
                         <tr class="smallerFont" >
                            <th>${lang('Mwezi','Month')}</th>
                            <th>${lang('Malipo Yaliyofanyika','Payments Made')}</th>
                            ${val?`<th>${lang('Deni Nyuma','Post Due')} <span class="text-primary">${fedha}</span> </th>`:''}
                            ${val?`<th>${lang('Manunuzi','Invoice(s) Amount')} <span class="text-primary">${fedha}</span> </th>`:''}
                           
                            <th>${lang('Deni Jumla','Net Due Amount')} <span class="text-primary">${fedha}</span> </th>
                            <th>${lang('Pesa Ilolipwa','Paid Amount')} <span class="text-primary">${fedha}</span> </th>
                            ${val?`<th>${lang('Deni','Due')} <span class="text-primary">${fedha}</span> </th>`:''}
                            ${!val?`<th>${lang('Hasara/Bonasi','Loss/Bonus')} <span class="text-primary">${fedha}</span> </th>`:''}
                            ${!val?`<th>${lang('Statasi','Bonus Status')}  </th>`:''}
                         </tr>
                        </thead>

                            <tbody id="paymntDataView" >
                                ${rw}
                            </tbody>
                            </table>
            `

                              
          
              $('#backBtn').data({val:0})

              $('#SaLDetail .row').html(reportD)
              $('#saleList').html(tb)
}

const pAttPayList = d =>{
    const {att} = d,
          month = d?.month
    const {pay,sale,} = VDATA,
          {st} = filters(),
          fltr = p=>p.pAtt===att

    let theSale = st?sale.filter(s=>s.st===st):sale,
        thePay = st?pay.filter(s=>s.st===st):pay
        
        theSale = theSale.filter(fltr)
        thePay = thePay.filter(fltr)
        theSale = month?theSale.filter(sa=>moment(sa.date).format('MMMM, YYYY')===month):theSale
        thePay = month?thePay.filter(sa=>moment(sa.date).format('MMMM, YYYY')===month):thePay

        const  attN = `${thePay[0]?.pAtt_fname} ${thePay[0]?.pAtt_lname}`

        const     totAmo = thePay.reduce((a,b)=>a+Number(b.Amount),0),
                    custDue = 0,
                    totDue = theSale.reduce((a,b)=>a+Number(b.due),0),
                    totreqAmo =  custDue+totAmo,
                    payT = thePay.filter(pm=>!pm.saRec).length  ,
                    invoAmo = theSale.reduce((a,b)=>a+Number(b.amount),0),
                 
                    staxn = st?thePay[0]?.stName:lang('Vito Vyote','All Stations'),
                    reportD = `<div class="col-6 col-lg-4">
                                            ${lang('Mhusika wa Pampu','Pump attendant')}:
                                    </div>
                                    <div class="col-6 col-lg-8 bluePrint text-capitalize">
                                        ${attN}
                                    </div>

                                    <div class="col-6 col-lg-4">
                                        ${lang('Kituo','Station')}:  
                                    </div>
                                    <div class="col-6 col-lg-8 bluePrint">
                                            ${staxn}  
                                    </div>

                                    ${month?`
                                             <div class="col-6 col-lg-4">
                                                ${lang('Muda','Duration')}:  
                                            </div>
                                            <div class="col-6 col-lg-8 bluePrint">
                                                    ${month}  
                                            </div> 
                                        `:''}



                                    
                                    <div class="col-6 col-lg-4">
                                        ${lang('Malipo','Payments')}:  
                                    </div>
                                    <div class="col-6 col-lg-8 bluePrint">
                                            ${thePay.length}  
                                    </div>

                                

                                    <div class="col-6 col-lg-4"  >
                                        ${lang('Kiasi Kinachotakiwa','Net Required Amount')}:  
                                    </div>
                                    <div class="col-6 col-lg-8 ">
                                        <span class="text-primary">${fedha}</span>.${Number(totreqAmo).toLocaleString()}  
                                    </div>                               
                                    <div class="col-6 col-lg-4">
                                        ${lang('Iliyolipwa','Paid Amount')}:  
                                    </div>
                                    <div class="col-6 col-lg-8 ">
                                        <span class="text-primary">${fedha}</span>.${Number(totAmo).toLocaleString()}  
                                    </div>                               
                                    <div class="col-6 col-lg-4 ">
                                            ${totDue>0?lang('Hasara','Loss'):totDue==0?lang('Hasara/Bonasi','Loss/Bonus'):lang('Bonasi','Bonus')}:  
                                    </div>
                                    <div class="col-6 col-lg-8 ${totDue>0?'brown':''} ${totDue<0?'green':''}">
                                        <span class="text-primary">${fedha}</span>.${Number(Math.abs(totDue)).toLocaleString()}  
                                    </div>                               
                                    
                                    `

                    const  shDta = [...new Set(thePay.map(pm=>pm.shift_id))]   , 
                            tbData =   shDta.map(sh=>shPayment(sh))    
                            function   shPayment(sh){
                             const   shD = thePay.filter(ft=>ft.sh===sh),
                                     bshift = Number(shD.filter(bf=>bf.biforeShift).reduce((a,b)=>a+Number(b.Amount),0)),
                                     {shcode,shfr,shto,shAmo,shPaid,ses} = shD[0],
                                     tAmont = bshift + Number(shAmo),
                                     tPamount = bshift + Number(shAmo),
                                        dt = {
                                            sh,
                                            shcode,
                                            shfr,
                                            shto,
                                            shAmo:tAmont,
                                            shPaid:tPamount,
                                            ses,
                                            pay:shD,
                                            bonus:Number(tPamount)-Number(tAmont)
                                        }

                                        return dt
                            }

                            

                          let  tr = ``
                            tbData.forEach(p => {
                                 const pm = p,
                                       rec1 = p.pay[0],
                                       otherRec = p.pay.filter(i=>i.id!=rec1.id),
                                       othrL = Number(otherRec.length)+1

                                      

                                tr+=`
                              
                                        <tr>
                                            <td ${othrL?`rowspan=${othrL}`:""} >${moment(pm.date).format('DD/MM/YYYY HH:mm')}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""}>${pm.ses}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""}>SH-${pm.shcode}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""}>${Number(pm.shAmo).toLocaleString()}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""}>${Number(pm.shPaid).toLocaleString()}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""} class="${pm.bonus>0?'green':''} ${pm.bonus<0?'brown':''}" >${Number(pm.bonus).toLocaleString()}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""}>${pm.bonus<0?lang('Hasara','Loss'):pm.bonus==0?lang('Sawa','Clear'):lang('Bonasi','Bonus')}</td>
                                        
                                            
                                            <td>${rec1?.accauntN}</td>
                                            <td>${rec1.biforeShift?lang('Kabla ya Zamu','Deposit Before'):lang('Mwisho wa Zamu','Shift End')}</td>
                                            <td>${Number(rec1?.Amount).toLocaleString()}</td>
                                            
                                         
                                        </tr>
                                `

                                if(otherRec.length){
                                    otherRec.forEach(pd=>{
                                            tr+=`
                                                <tr>
                                                <td>${pd?.accauntN}</td>
                                                <td>${pd.biforeShift?lang('Kabla ya Zamu','Deposit Before'):lang('Mwisho wa Zamu','Shift End')}</td>
                                                <td>${Number(pd?.Amount).toLocaleString()}</td>
                                            </tr>
                                            `

                                    })

                                }


                            });


                    const tb = `
                               <table class="table table-bordered table-sm nested-table">
                                    <thead class=" weight600 smallerFont">
                                    <tr>
                                        <td rowspan="2" >${lang('TareheMuda','DateTime')}</td>
                                        <td rowspan="2" >${lang('MpangoZamu','Session')} </td>
                                        <td rowspan="2" >${lang('Zamu','Shift')} </td>
                                        <td rowspan="2" >${lang('Kiasi','Amount')} (${fedha})</td>
                                        <td rowspan="2" >${lang('Ilolipwa','Paid')} (${fedha})</td>
                                        <td rowspan="2" >${lang('Loss/Bonasi','Loss/Bonus')} (${fedha})</td>
                                        <td rowspan="2" >${lang('Statasi','Status')} </td>

                                        <td colspan="3">${lang('Akaunti za Malipo','Payment Accounts')}</td>
                                    </tr>
                                    <tr>
                                        
                                        <td>${lang('Akaunti','Account')}</td>
                                        <td>${lang('Statasi','status')}</td>
                                       
                                        <td>${lang('Kiasi','Amount')} (${fedha})</td>
                                    </tr>
                                    </thead>
                                    <tbody>
                                        ${tr}   
                                   </tbody> 
                                   </table>
                              `   
                              
                              
             $('#SaLDetail .row').html(reportD)
              $('#saleList').html(tb)
                       
}


const custmPayList = d =>{
    const {cust} = d,
          month = d?.month
    const {pay,sale,payRec} = VDATA,
          {st} = filters(),
          fltr = p=>p.cust===cust&&p.Amount>0

    let theSale = st?sale.filter(s=>s.st===st):sale,
        thePay = st?pay.filter(s=>s.st===st):pay
        thePayRec = st?payRec.filter(s=>s.st===st):payRec
        
        theSale = theSale.filter(fltr)
        thePay = thePay.filter(fltr)

        theSale = month?theSale.filter(sa=>moment(sa.date).format('MMMM, YYYY')===month):theSale
        thePay = month?thePay.filter(sa=>moment(sa.date).format('MMMM, YYYY')===month):thePay

        const   custN = thePay[0]?.custN

        const       totAmo = thePay.reduce((a,b)=>a+Number(b.Amount),0),
                    custDue = Number(thePay[Number(thePay.length)-1]?.rem),
                    totDue = theSale.reduce((a,b)=>a+Number(b.due),0),
                    totreqAmo =  custDue+totAmo,
                    payT = thePay.filter(pm=>!pm.saRec).length  ,
                    invoAmo = theSale.reduce((a,b)=>a+Number(b.amount),0),
                    postDue = totreqAmo - invoAmo  ,
                 
                    staxn = st?thePay[0]?.stName:lang('Vito Vyote','All Stations'),
                    reportD = `<div class="col-6 col-lg-4">
                                      ${lang('Jina la Mteja','Customer Name')}:
                                </div>
                                <div class="col-6 col-lg-8 bluePrint text-capitalize">
                                   ${custN}
                                </div>
                                <div class="col-6 col-lg-4">
                                    ${lang('Kituo','Station')}:  
                                </div>
                                <div class="col-6 col-lg-8 bluePrint">
                                     ${staxn}  
                                </div>


                                    ${month?`
                                             <div class="col-6 col-lg-4">
                                                ${lang('Muda','Duration')}:  
                                            </div>
                                            <div class="col-6 col-lg-8 bluePrint">
                                                    ${month}  
                                            </div> 
                                        `:''}
                                
                                <div class="col-6 col-lg-4">
                                    ${lang('Malipo','Payments')}:  
                                </div>
                                <div class="col-6 col-lg-8 bluePrint">
                                     ${payT}  
                                </div>

                                <div class="col-6 col-lg-4" >
                                    ${lang('Deni Nyuma','Post Due')}:  
                                </div>
                                <div class="col-6 col-lg-8 "  >
                                    <span class="text-primary">${fedha}</span>.${Number(postDue).toLocaleString()}  
                                </div>                               
                                <div class="col-6 col-lg-4"  >
                                    ${lang('Manunuzi','Invoice(s) Amount')}:  
                                </div>
                                <div class="col-6 col-lg-8 "  >
                                    <span class="text-primary">${fedha}</span>.${Number(invoAmo).toLocaleString()}  
                                </div>    

                                <div class="col-6 col-lg-4"  >
                                    ${lang('Kiasi Kinachotakiwa','Net Required Amount')}:  
                                </div>
                                <div class="col-6 col-lg-8 ">
                                    <span class="text-primary">${fedha}</span>.${Number(totreqAmo).toLocaleString()}  
                                </div>                               
                                <div class="col-6 col-lg-4">
                                    ${lang('Iliyolipwa','Paid Amount')}:  
                                </div>
                                <div class="col-6 col-lg-8 ">
                                    <span class="text-primary">${fedha}</span>.${Number(totAmo).toLocaleString()}  
                                </div>                               
                                <div class="col-6 col-lg-4 ">
                                     ${lang('Deni','Due')} 
                                </div>
                                <div class="col-6 col-lg-8 ${totDue>0?'brown':''} ${totDue<0?'green':''}">
                                    <span class="text-primary">${fedha}</span>.${Number(Math.abs(custDue)).toLocaleString()}  
                                </div>   
                                    `

                    const   
                            tbData =   thePay.map(tp=>shPayment(tp))    
                            function   shPayment(tp){
                             const   shD = thePayRec.filter(ft=>ft.py===tp.id),
                                        dt = {
                                            tp,
                                            pay:shD
                                        }

                                        return dt
                            }

                           


                            let  tr = ``
                            tbData.forEach(p => {
                                 const pm = p.tp,
                                       rec1 = p.pay[0],
                                       otherRec = p.pay.filter(i=>i.id!=rec1.id),
                                       othrL = Number(p.pay.length)

                                tr+=`
                              
                                        <tr>
                                            <td ${othrL?`rowspan=${othrL}`:""} >${moment(pm.date).format('DD/MM/YYYY HH:mm')}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""}>${pm.accauntN}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""}>${Number(pm.tDebt).toLocaleString()}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""}>${Number(pm.Amount).toLocaleString()}</td>
                                            <td ${othrL?`rowspan=${othrL}`:""}>${Number(pm.rem).toLocaleString()}</td>
                                            
                                        
                                            <td>${moment(rec1?.invoDate).format('DD/MM/YYYY HH:mm')}</td>
                                            <td>INVO-${rec1?.invoCode}</td>
                                            <td>${Number(rec1?.invoAmo).toLocaleString()}</td>
                                            <td>${Number(rec1?.postDue).toLocaleString()}</td>
                                            <td>${Number(rec1?.Debt).toLocaleString()}</td>

                                            <td>${Number(rec1?.Apay).toLocaleString()}</td>
                                            <td>${Number(rec1?.due).toLocaleString()}</td>
                                         
                                        </tr>
                                `

                                if(otherRec.length){
                                    otherRec.forEach(pd=>{
                                            tr+=`
                                             <tr>
                                                <td>${moment(pd.date).format('DD/MM/YYYY HH:mm')}</td>
                                                <td>INVO-${pd.invoCode}</td>
                                                <td>${Number(pd.invoAmo).toLocaleString()}</td>
                                                <td>${Number(pd.postDue).toLocaleString()}</td>
                                                <td>${Number(pd.Debt).toLocaleString()}</td>

                                                <td>${Number(pd.Apay).toLocaleString()}</td>
                                                <td>${Number(pd.due).toLocaleString()}</td>
                                              </tr>  
                                            `

                                    })

                                }


                            });

                        const tb = `
                               <table class="table table-bordered table-sm nested-table">
                                    <thead class=" weight600 smallerFont">
                                    <tr>
                                        <td rowspan="2" >${lang('TareheMuda','DateTime')}</td>
                                        <td rowspan="2" >${lang('Akaunti','Account')} ${fedha}</td>
                                        <td rowspan="2" >${lang('Deni','Due')} ${fedha}</td>
                                        <td rowspan="2" >${lang('Ilolipwa','Paid')} ${fedha}</td>
                                        <td rowspan="2" >${lang('Ilobaki','Remaining')} ${fedha}</td>
                                        <td colspan="7">${lang('Ankara Zilizolipwa','Paid Invoices')}</td>
                                    </tr>
                                    <tr>
                                        
                                        <td>${lang('AnkaraTarehe','InvoDate')}</td>
                                        <td>${lang('Ankara','Invoice')}</td>
                                        <td>${lang('Kiasi','INVO Amount')} ${fedha}</td>
                                        <td>${lang('Malipo Awali','Post paid')} ${fedha}</td>
                                        <td>${lang('Deni','Due')} ${fedha}</td>
                                        <td>${lang('Malipo','Paid')} ${fedha}</td>
                                        <td>${lang('Ilobaki','Remaining')} ${fedha}</td>
                                    </tr>
                                    </thead>
                                    <tbody>
                                        ${tr}   
                                   </tbody> 
                                   </table>
                              `   
                              
                              
             $('#SaLDetail .row').html(reportD)
              $('#saleList').html(tb)
                              
                              

}

// Change this to be resposive for js generated buttons
$('body').on('click','.riportListChatOn, .chartType',function(){

   const inGeneral = $('#MoreDetails').is(":hidden"),
         chart = Number($(this).data('r')),
         thereIsfuel = VOBJ.data[0]?.fuel,
         changeR = Number($(this).data('changer'))||0,
         {chartT} = filters()

         if((inGeneral||!chart)&&chartT!='pay'){
            if(!changeR){
                  $('.riportListChatOn').removeClass('btn-secondary')
                    $('.riportListChatOn').addClass('btn-light')
                    $(this).removeClass('btn-light')
                    $(this).addClass('btn-secondary')
            }
          
         }


      if(chart&&(inGeneral||changeR)&&chartT!='pay'){


        
              $('#Salecateg').fadeOut()
             $('#MoreDetails').fadeIn(100)

             const 
                   summryData =  {
                    labels: VOBJ.data.map(d=>d.name),
                    text: VOBJ.title,
                    datasets: [
                    //     {
                    //         label: lang('Kiasi cha Mauzo','Sales Amount'),
                    //         data: VOBJ.data.map(d=>d.tot),
                    //         backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    //   },
                    {
                        label: lang('Ghalama ya Mauzo','Cost of fuel Sold'),
                        data: VOBJ.data.map(d=>d.cost),
                        backgroundColor: 'rgba(153, 102, 255, 0.7)',
                      },
                      {
                        label: lang('Kiasi Kilicholipwa','Paid Amount'),
                        data: VOBJ.data.map(d=>d.pay),
                        backgroundColor: '#6ec6e6',
                      },
                   
                      {
                            label: chartT==='att'?lang('Hasara','Loss'):lang('Kiasi cha Deni','Due Amount'),
                            data: VOBJ.data.map(d=>d.due>0&&chartT=='att'?0:Math.abs(d.due)),
                            backgroundColor: 'rgba(255, 99, 132, 0.7)',
                      },
                    ],
                    thereIsfuel
                }



                if(chart==1)chartView(summryData)

                if(chart==2){
               
                // VOBJ = { "data": [
                //         {
                //             "name": "August, 2025",
                //             "shift": 3,
                //             "fuel": [
                //                 {
                //                     "fuel": "Petrol",
                //                     "id": 1,
                //                     "qty": 842,
                //                     "cost": 1592070.2716,
                //                     "sales": 2526000
                //                 },
                //                 {
                //                     "fuel": "Disel",
                //                     "id": 2,
                //                     "qty": 1011,
                //                     "cost": 2009914.3037999999,
                //                     "sales": 3033000
                //                 }
                //             ],
                //             "tot": 5559000,
                //             "pay": 5159000,
                //             "due": 400000,
                //             "cost": 3601984.5754
                //         }
                //     ],
                //     "title": "Monthly sales Analyisis"}
                // that is the structure of VOBJ i want to extract fuel data for chart
                // the lablels  and dataset should be as follows
                // labels: ["August, 2025","September, 2025","October, 2025"],
                // datasets: [
                // {
                //     label: "Petrol",
                //     data: [2526000, 2800000, 3100000],
                //     backgroundColor: "orange"
                // },
                // {
                //     label: "Diesel",
                //     data: [3033000, 2900000, 3200000],
                //     backgroundColor: "blue"
                // }
                // ]
                // so we need to loop through VOBJ.data and extract fuel data
                // then we need to loop through fuel data and extract fuel names and sales  
                const fuelNames = [...new Set(thereIsfuel.map(f=>f.fuel))],
                        fuelDatasets = fuelNames.map(fn => ({
                            label: fn,
                            data: VOBJ.data.map(d => {
                                let fuelData = d.fuel.find(f => f.fuel === fn);
                                return fuelData ? fuelData.sales : 0;
                            }),
                            backgroundColor: fn.toLowerCase().includes('petrol') ? '#b7e000dc' : '#004fe2bb'
                        }));

                    // Add total sales bar (sum of all fuel types per period)
                        fuelDatasets.push({
                            label: lang('Mauzo Jumla','Total Sales'),
                            data: VOBJ.data.map(d => d.fuel.reduce((sum, f) => sum + (f.sales || 0), 0)),
                            backgroundColor: '#1d8a02dc'
                        });

                    fuelData =  {
                        labels: VOBJ.data.map(d=>d.name),
                        text: lang('Mauzo ya Mafuta ','Fuel Sales  '),
                        datasets: fuelDatasets,
                        thereIsfuel,
                        chart:2

               
             }
                    
                   
                
                    chartView(fuelData)
                }

              
             
      }else{
            $('#MoreDetails').fadeOut(100)
            $('#Salecateg').fadeIn(100)
        if(chartT=='pay')toastr.info(lang('Hakuna Chati kwa iliyoptatikana tafadhari rejea ripoti ya Mauzo kutoka mhusika wa pampu au mteja muhimu kupata chati ya malipo na mauzo',
            'No chart found, please click on pump attendant and Credit sales to view payment charts and sales'),'',{timeOut:5e3})

      }
     $('#MoredetailRHeading a').prop('hidden',chart)

        

})

const chartView = (d) =>{
    const {labels,text,datasets,thereIsfuel} = d,
          chartT = d?.chart||1
    const fuelGenBtns = `  <div class="btn-group d-flex mb-2 justify-content-center"   role="group" aria-label="Basic example">
                                <button class="btn btn-light border btn-sm chartType ${chartT==1?'grey':''}" data-r=1 data-changer=1 id="summaryBtn">General Chart</button>

                                <button class="btn btn-light border btn-sm chartType ${chartT==2?'grey':''}" data-r=2 data-changer=1 id="fuelBtn">Fuel Sales Chart</button>
                            </div>`
    const canva = `
       
        ${thereIsfuel.length?fuelGenBtns:''}
       <div id="fuelTitle">
             <canvas id="salesChart"></canvas>
        </div>
    `
    $('#SaLDetail .row').html('')
    $('#saleList').html(canva)
    $('#MoredetailRHeading span').html('')
    
    
    const ctx = document.getElementById('salesChart').getContext('2d');
    const salesChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'top' },
          title: {
            display: true,
            text
          }
        },
        scales: {
          x: {
            barPercentage: 0.6,
            categoryPercentage: 0.7,
            stacked: chartT==2?false:true
          },
          y: {
            stacked: chartT==2?false:true,
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return value.toLocaleString()+' '+hela;
              }
            }
          }
        }
      }
    });
}

// Print report
$('#printRBtn').click(function(){
    
    const inGeneral = $('#MoreDetails').is(":hidden")
    const generalR = Array.from(document.getElementById('Salecateg').querySelectorAll('.DetailsTable')).filter(table => table.hidden === false)
    const  generT = generalR[0]?.querySelector('table')?.innerHTML // Get the first visible table
    const  generH = generalR[0]?.querySelector('h6')?.innerText// Get the first visible h6
    const userN = $(this).data('user')
    const detR = document.getElementById('saleList')?.querySelector('table')?.innerHTML; // Get the table inside #saleList
    const summary = `<div class="row my-3">
                        <div class="col-9  row ">
                        ${$('#SaLDetail .col-md-7').html()}

                        <div class="col-6 col-lg-4">
                            ${lang('Imetolewa','Issued on')}:  
                        </div>
                        <div class="col-6  col-lg-8 ">
                            ${moment().format('DD/MM/YYYY HH:mm')}  
                        </div>

                        <div class="col-6 col-lg-4">
                            ${lang('Imetolewa na','Issued by')}:  
                        </div>
                        <div class="col-6  col-lg-8 text-capitalize">
                            ${userN}    
                        </div>

                        </div>

                     </div>`,
          head = `<h6>${inGeneral?generH:$('#MoredetailRHeading span').html()}</h6>`,
          table = inGeneral?generT:summary+detR
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write(company_header);
    printWindow.document.write(`${head}<table class="table table-bordered" style="max-width:100%" >${table}</table>`); 
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
    // create a delay to allow the content to render before printing
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 700);
    
})
