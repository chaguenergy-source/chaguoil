let saData = [],FUEL = [], VDATA = {},ISVIEW = 0,SAOBJ=[],VOBJ={}
const filters = () =>{
    const  st = Number($('#staxnF').val()),
         
         
           today = {rname:lang('Leo','Today'),tFr:moment(moment().startOf('day')).format(),tTo:moment().format()},
           week = {rname:lang('Wiki hii','This Week'),tFr:moment(moment().startOf('isoWeek')).format(),tTo:moment().format()},
           month = {rname:lang('Mwezi huu','This Month'),tFr:moment(moment().startOf('month')).format(),tTo:moment().format()}
           
           return {st,today,week,month}
}


const getRData = d =>{
    $('#loadMe').modal('show')
    const {tFr,tTo,rname,init} = d,
          url = '/analytics/getEvaluation' ,
          tdy = Number(moment(tTo).format('DD')),
          tmFr = tdy>=7||!init?tFr:moment(moment().subtract(7,'days')).format(),
          data = {data:{tFr:tmFr,tTo},url},
          
          
          sendIt = POSTREQUEST(data)
         
          sendIt.then(resp=>{
              $('#loadMe').modal('hide')
              hideLoading()
            //   console.log(resp);
              
              summaryR({resp,rname,init,tFr,tTo})

         
          })

}


$(document).ready(function(){
    const {month} = filters(),
          {tFr,tTo,rname} = month
          getRData({tFr,tTo,rname,init:1});

})

const summaryR = d =>{
        const {resp,rname,init,tFr,tTo} = d,
          {today,week} = filters()
        //   {sale,saL,pay,payRec} = resp
    
         if(init){
                // Today report 
                ArryCreate({...resp,tFr:today.tFr,tTo:today.tTo,rname:today.rname})

                // week report 
                
                ArryCreate({...resp,tFr:week.tFr,tTo:week.tTo,rname:week.rname})
              
            }

                ArryCreate({...resp,tFr,tTo,rname})
               createtr()
     }

const createtr = () =>{
const {st} = filters()
let tr = '',chk=''
const init = Number($('#generalSaleR tr').length==0)
        
        saData.forEach(r=>{
        
        let  sale = st?r.sale?.filter(sa=>sa.st===st):r.sale,
             saL = st?r.saL?.filter(sa=>sa.st===st):r.saL
             expx = st?r.expx?.filter(sa=>sa.st===st):r.expx
             puch = st?r.puch?.filter(sa=>sa.st===st):r.puch
             adj = st?r.adj?.filter(sa=>sa.st===st):r.adj
             recv = st?r.recv?.filter(sa=>sa.st===st):r.recv
             trf = st?r.trf?.filter(sa=>sa.st===st):r.trf,
             stock = st?r.stock?.filter(sa=>sa.stationId===st):r.stock
 
                //  Sale Type filter (Customer or Pump Attendants)
             


                

            const  
                    expAmo=Number(expx.filter(f=>Number(f.fuel_qty)===0)?.reduce((a,b)=>a+Number(b.kiasi),0))||0,
                    expFuel=Number(expx.filter(f=>Number(f.fuel_qty)>0)?.reduce((a,b)=>a+Number(b.fuel_qty*b.fuel_cost),0))||0,
                    expTotal=Number(expAmo)+Number(expFuel),
                    saleAmo=Number(sale?.reduce((a,b)=>a+Number(b.amount),0))||0,
                    payAmo=Number(sale?.reduce((a,b)=>a+Number(b.payed),0))||0,
                    purchAmo = Number(puch?.reduce((a,b)=>a+Number(Number(b.cost)*Number(b.qty)),0))||0,      
                    transfAmo = Number(trf?.reduce((a,b)=>a+Number(Number(b.cost)*Number(b.qty)),0))||0,      
                    wastege = Number(adj?.reduce((a,b)=>a+Number(Number(b.diff)*Number(b.cost)),0))||0,   
                    puWastage =  Number(puch?.filter(p=>p.closed).reduce((a,b)=>a+Number(Number(b.cost)*(Number(b.qty)-Number(b.rcvd))),0)) || 0,  
                    totWastge = st?Number(puWastage)+Number(wastege):wastege,
            
                    rcvAmo = recv.reduce((a,b)=>a+Number(Number(b.cost)*Number(b.qty)),0),  
                        
                    opening = stock.reduce((a,b)=>a+Number(b.opening*b.OpenCost),0) || 0,
                    closing = stock.reduce((a,b)=>a+Number(b.closing*b.CloseCost),0) || 0,
                    saleCost = saL.reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0) || 0,
                    profit = payAmo - (saleCost + expAmo - totWastge),
                    
  
                    check = Number($(`#MonthSale${r.id}`).prop('checked')),
                    show = check == 1 || check == 0 ?check:1,
    

                    hide = !init && !show

                 

        tr+=`<tr class="${r.id>3?'table-info':''}"  ${hide?'style="display:none"':''}   id="dataRow${r.id}" >
            <td> <a type="button" data-val=${r.id} class="bluePrint viewDetails" >${r.rname} </a> </td>
            <td>${Number(opening).toLocaleString()}  </td>
            <td ${st?'hidden':''} >${Number(purchAmo).toLocaleString()}  </td>
            <td >${Number(rcvAmo).toLocaleString()}  </td>
            <td ${!st?'hidden':''} >${Number(transfAmo).toLocaleString()}  </td>
            <td>${Number(totWastge).toLocaleString()}  </td>
            <td>${Number(saleCost).toLocaleString()}  </td>
            <td>${Number(payAmo).toLocaleString()}  </td>

            <td>${Number(expFuel).toLocaleString()}  </td>
            <td>${Number(expAmo).toLocaleString()}  </td>
            <td>${Number(expTotal).toLocaleString()}  </td>

            <td>${Number(profit).toLocaleString()}  </td>
            <td>${Number(closing).toLocaleString()}  </td>
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

    $('.theSt').prop('hidden',!st)
    $('.allSt').prop('hidden',st)

    $('#generalSaleR').html(tr)
    $('#mapSelector').html(chk)
}

// The seleted time duration Data....................................//
const ArryCreate = d =>{
            const {tFr,tTo,rname} = d,
                     sale = d.sale?.filter(s=>moment(s.date).format() >= tFr && moment(s.date).format() <= tTo ),
                     saL = d.saL?.filter(s=>moment(s.date).format() >= tFr && moment(s.date).format() <= tTo ),
                     puch = d.puch?.filter(s=>moment(s.date).format() >= tFr && moment(s.date).format() <= tTo ),
                     adj = d.adj?.filter(s=>moment(s.date).format() >= tFr && moment(s.date).format() <= tTo ),
                     expx = d.expx?.filter(s=>moment(s.tarehe).format() >= tFr && moment(s.tarehe).format() <= tTo ),
                     recv = d.recv?.filter(s=>moment(s.date).format() >= tFr && moment(s.date).format() <= tTo ),
                     trf = d.trf?.filter(s=>moment(s.date).format() >= tFr && moment(s.date).format() <= tTo )
                     let  stock = d.stock?.filter(s=>moment(s.tFr).format() === tFr && moment(s.tTo).format() === tTo )

                    //  on this the stock if the time range  does not march and is within the range of the data available we have to create the stock
                    if (stock?.length === 0 && d.stock?.length > 0) {
                        // Use the domain stock data to calculate opening and closing for the given time range
                        stock = d.stock.map(s => {
                            // Find the stock entry with the earliest OpnDate before or at tFr for opening
                            

                            let opening = Number(s.opening);
                            let openCost = Number(s.OpenCost);
                            let openingDate = moment(s.tFr);

                            // Sum all movements after openingDate but before tFr
                            const recvdBefore = d.recv
                                .filter(r => r.To_id === s.tank && moment(r.date).isAfter(openingDate) && moment(r.date).isBefore(tFr))
                                .reduce((a, b) => a + Number(b.qty), 0);
                            const trfOutBefore = d.trf
                                .filter(r => r.trFr === s.tank && moment(r.date).isAfter(openingDate) && moment(r.date).isBefore(tFr))
                                .reduce((a, b) => a + Number(b.qty), 0);
                            const trfInBefore = d.trf
                                .filter(r => r.To_id === s.tank && moment(r.date).isAfter(openingDate) && moment(r.date).isBefore(tFr))
                                .reduce((a, b) => a + Number(b.qty), 0);
                            const soldBefore = d.saL
                                .filter(r => r.tank_id === s.tank && moment(r.date).isAfter(openingDate) && moment(r.date).isBefore(tFr))
                                .reduce((a, b) => a + Number(b.qty_sold), 0);
                            const usedBefore = d.expx
                                .filter(r => r.tank === s.tank && moment(r.tarehe).isAfter(openingDate) && moment(r.tarehe).isBefore(tFr))
                                .reduce((a, b) => a + Number(b.fuel_qty), 0);

                             const wastageBefore = d.adj   
                                .filter(r => r.tank === s.tank && moment(r.tarehe).isAfter(openingDate) && moment(r.tarehe).isBefore(tFr))
                                .reduce((a, b) => a + Number(b.diff), 0);

                            // Calculate opening stock at tFr
                            opening = opening + recvdBefore + wastageBefore + trfInBefore - trfOutBefore - soldBefore - usedBefore;
                            //  In the cases above we calculated the all movements in terms of quantity, now we need to calculate all in terms of cost

                            // console.log({tank:s.tank,opening,recvdBefore,trfInBefore,trfOutBefore,soldBefore,usedBefore});
                            let openingValue = Number(s.opening) * Number(s.OpenCost);
                            
                            const recvdValue = d.recv
                                .filter(r => r.To_id === s.tank && moment(r.date).isAfter(openingDate) && moment(r.date).isBefore(tFr))
                                .reduce((a, b) => a + (Number(b.qty) * Number(b.cost)), 0);
                            const trfInValue = d.trf
                                .filter(r => r.To_id === s.tank && moment(r.date).isAfter(openingDate) && moment(r.date).isBefore(tFr))
                                .reduce((a, b) => a + (Number(b.qty) * Number(b.cost)), 0);
                            const trfOutValue = d.trf
                                .filter(r => r.trFr === s.tank && moment(r.date).isAfter(openingDate) && moment(r.date).isBefore(tFr))    
                                .reduce((a, b) => a + (Number(b.qty) * Number(b.cost)), 0);
                            const soldValue = d.saL
                                .filter(r => r.tank_id === s.tank && moment(r.date).isAfter(openingDate) && moment(r.date).isBefore(tFr))
                                .reduce((a, b) => a + (Number(b.qty_sold) * Number(b.cost_sold)), 0);
                            const usedValue = d.expx
                                .filter(r => r.tank === s.tank && moment(r.tarehe).isAfter(openingDate) && moment(r.tarehe).isBefore(tFr))
                                .reduce((a, b) => a + (Number(b.fuel_qty) * Number(b.fuel_cost)), 0);
                            const wastageValue = d.adj
                                .filter(r => r.tank === s.tank && moment(r.tarehe).isAfter(openingDate) && moment(r.tarehe).isBefore(tFr))
                                .reduce((a, b) => a + (Number(b.diff) * Number(b.cost)), 0);

                            openingValue = openingValue + recvdValue + wastageValue + trfInValue - trfOutValue - soldValue - usedValue;

                            // From this we can calculate the average cost for the opening stock at tFr
                            const averageOpenCost = openingValue / opening;
                           


                            let closing = Number(s.closing);
                            let closeCost = Number(s.CloseCost);
                            let closingDate = moment(s.tFr);

                            // Sum all movements after closingDate but before or at tTo
                            const recvdAfter = d.recv
                                .filter(r => r.To_id === s.tank && moment(r.date).isAfter(closingDate) && moment(r.date).isSameOrBefore(tTo))
                                .reduce((a, b) => a + Number(b.qty), 0);
                            const trfOutAfter = d.trf
                                .filter(r => r.trFr === s.tank && moment(r.date).isAfter(closingDate) && moment(r.date).isSameOrBefore(tTo))
                                .reduce((a, b) => a + Number(b.qty), 0);
                            const trfInAfter = d.trf
                                .filter(r => r.To_id === s.tank && moment(r.date).isAfter(closingDate) && moment(r.date).isSameOrBefore(tTo))
                                .reduce((a, b) => a + Number(b.qty), 0);
                            const soldAfter = d.saL
                                .filter(r => r.tank_id === s.tank && moment(r.date).isAfter(closingDate) && moment(r.date).isSameOrBefore(tTo))
                                .reduce((a, b) => a + Number(b.qty_sold), 0);
                            const usedAfter = d.expx
                                .filter(r => r.tank === s.tank && moment(r.tarehe).isAfter(closingDate) && moment(r.tarehe).isSameOrBefore(tTo))
                                .reduce((a, b) => a + Number(b.fuel_qty), 0);
                            const wastageAfter = d.adj
                                .filter(r => r.tank === s.tank && moment(r.tarehe).isAfter(closingDate) && moment(r.tarehe).isSameOrBefore(tTo))
                                .reduce((a, b) => a + Number(b.diff), 0);
                            // Calculate closing stock at tTo
                            closing = s.opening + recvdAfter + wastageAfter + trfInAfter - trfOutAfter - soldAfter - usedAfter;

                            //  In the cases above we calculated the all movements in terms of quantity, now we need to calculate all in terms of cost
                            let closingValue = Number(s.opening) * Number(s.OpenCost);
                            

                            const recvdValueAfter = d.recv
                                .filter(r => r.To_id === s.tank && moment(r.date).isAfter(closingDate) && moment(r.date).isSameOrBefore(tTo))
                                .reduce((a, b) => a + (Number(b.qty) * Number(b.cost)), 0);
                            const trfInValueAfter = d.trf
                                .filter(r => r.To_id === s.tank && moment(r.date).isAfter(closingDate) && moment(r.date).isSameOrBefore(tTo))
                                .reduce((a, b) => a + (Number(b.qty) * Number(b.cost)), 0);
                            const trfOutValueAfter = d.trf
                                .filter(r => r.trFr === s.tank && moment(r.date).isAfter(closingDate) && moment(r.date).isSameOrBefore(tTo))
                                .reduce((a, b) => a + (Number(b.qty) * Number(b.cost)), 0);
                            const soldValueAfter = d.saL
                                .filter(r => r.tank_id === s.tank && moment(r.date).isAfter(closingDate) && moment(r.date).isSameOrBefore(tTo))
                                .reduce((a, b) => a + (Number(b.qty_sold) * Number(b.cost_sold)), 0);
                            const usedValueAfter = d.expx
                                .filter(r => r.tank === s.tank && moment(r.tarehe).isAfter(closingDate) && moment(r.tarehe).isSameOrBefore(tTo))
                                .reduce((a, b) => a + (Number(b.fuel_qty) * Number(b.fuel_cost)), 0);
                            const wastageValueAfter = d.adj
                                .filter(r => r.tank === s.tank && moment(r.tarehe).isAfter(closingDate) && moment(r.tarehe).isSameOrBefore(tTo))
                                .reduce((a, b) => a + (Number(b.diff) * Number(b.cost)), 0);
                            
                                closingValue = closingValue + recvdValueAfter + wastageValueAfter + trfInValueAfter - trfOutValueAfter - soldValueAfter - usedValueAfter;
                         
                            // From this we can calculate the average cost for the closing stock at tTo
                            const AverageCloseCost = closingValue / closing;

                            // console.log({AverageCloseCost,closingValue,closing,recvdValueAfter,trfInValueAfter,trfOutValueAfter,soldValueAfter,usedValueAfter,wastageValueAfter});

                            //  console.log({averageOpenCost,openingValue,AverageCloseCost,closingValue,closing});

                            return {
                                tank: s.tank,
                                TankName: s.TankName,
                                fuelName: s.fuelName,
                                stationId: s.stationId,
                                st: s.st,
                                stationName: s.stationName,
                                fuel: s.fuel,
                                opening: Number(opening.toFixed(4)),
                                closing: Number(closing.toFixed(4)),
                                tFr,
                                tTo,
                                OpnDate: s.OpnDate,
                                OpenCost: averageOpenCost,
                                CloseCost: AverageCloseCost
                            };
                        });
                    }
                    
       
                    
            thedt = {
                id:saData.length + 1,
                rname,
                sale,
                saL,
                adj,
                expx, 
                recv, 
                trf,
                tFr,
                tTo,
                puch,
                stock
           
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
                     const {sale,pay,saL,expx,recv,trf,stock,puch,adj} = saDt[0],

                     dt = {sale,pay,saL,tFr,tTo,rname,expx,recv,trf,stock,puch,adj}
                     ArryCreate(dt)
                     createtr()

                }else{

                    getRData({tFr,tTo,rname,init:0});     

                }   }


                }



$('.filter').change(function(){
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

        $('.DetailsTable').hide()
          detailReport()

         $('#summaryRiport').fadeOut();
         

         $('.riportOn').removeClass('btn-primary')
         $('#RBydate').addClass('btn-primary')

        
        

        //  $('#saleByDate').show()
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
    
     Rdate = DFrom==DTo?moment(tFr).format('DD/MM/YYYY'):`${moment(tFr).format('DD/MM/YYYY')} - ${moment(tTo).format('DD/MM/YYYY')}`,
     isToday = DTo == tdy?`${lang('Hadi','To')} ${moment(tTo).format('HH:mm')}`:'',
     head = `${lang('Mchanganuo na mwenendo wa Stoku','Stock Evaluation and Analysis')} <span class="bluePrint"> ${Rdate} </span> ${isToday}`
   
    // let  sale = st?r.sale?.filter(sa=>sa.shell===st):r.sale,
    //      saL = st?r.saL?.filter(sa=>sa.shell===st):r.saL,
    //      pay =st?r.pay?.filter(sa=>sa.st===st):r.pay
    //      payRec =st?r.payRec?.filter(sa=>sa.st===st):r.payRec

 
       
        $('#detailRHeading').html(head)
        
   

        $('#riportChatRist .btn-secondary').addClass('btn-light').removeClass('btn-secondary')
        $('#riportChatRist button').first().addClass('btn-secondary').removeClass('btn-light')

        $('#MoreDetails').fadeOut(100)
        $('#Salecateg').fadeIn(100)
        // find all the div elements inside the Salecateg div if all are hidden show the first one
        if($('#Salecateg .DetailsTable:visible').length==0){
            $('#Salecateg .DetailsTable').first().fadeIn(100)
        }

        daterAnalyze()

        fuelAnalyze()
        tankAnalyze()
        stationAnalyze()



}


const daterAnalyze = () =>{

    // $('.DetailsTable').hide()
    // $('#EvaluateByDate').fadeIn(100)

   
//    create set of date by combining recv, pu ,transfer, exp, adj and others
// Combine all relevant date arrays into one set of unique dates
let {recv = [], puch = [], trf = [], expx = [], adj = [], saL = [], sale = [],stock=[]} = VDATA;

// Extract all dates from each array (use correct date field for each)
const start = moment(VDATA.tFr);
const end = moment(VDATA.tTo);
let allDates = [];
const {st} = filters()

// filter all data if st is set
if (st) {
    recv = recv.filter(r => r.st === st);
    trf = trf.filter(t => t.st === st);
    expx = expx.filter(e => e.st === st);
    adj = adj.filter(a => a.st === st);
    saL = saL.filter(s => s.st === st);
    sale = sale.filter(s => s.st === st);
    stock = stock.filter(s => s.st === st);
}

// if (end.diff(start, 'months', true) > 1) {
//    allDates = [
//         ...recv.map(r => moment(r.date).format('YYYY-MM')),
//         ...puch.map(p => moment(p.date).format('YYYY-MM')),
//         ...trf.map(t => moment(t.date).format('YYYY-MM')),
//         ...expx.map(e => moment(e.tarehe).format('YYYY-MM')),
//         ...adj.map(a => moment(a.date).format('YYYY-MM')),
//         ...saL.map(s => moment(s.date).format('YYYY-MM')),
        
//    ]
// } else {
//     // Else, extract set of dates (YYYY-MM-DD)
//     allDates = [
//         ...recv.map(r => moment(r.date).format('YYYY-MM-DD')),
//         ...puch.map(p => moment(p.date).format('YYYY-MM-DD')),
//         ...trf.map(t => moment(t.date).format('YYYY-MM-DD')),
//         ...expx.map(e => moment(e.tarehe).format('YYYY-MM-DD')),
//         ...adj.map(a => moment(a.date).format('YYYY-MM-DD')),
//         ...saL.map(s => moment(s.date).format('YYYY-MM-DD')),
      
//     ];
// }

// allDates = [];
let current = start.clone();
while (current.isSameOrBefore(end, 'day')) {
    allDates.push(current.format('YYYY-MM-DD'));
    // If the difference exceeds 1 month, create a set of months instead of days
    if (end.diff(start, 'months', true) > 1) {
        // Only add the first of each month
        allDates = [];
        let monthCursor = start.clone().startOf('month');
        while (monthCursor.isSameOrBefore(end, 'month')) {
            allDates.push(monthCursor.format('YYYY-MM'));
            monthCursor.add(1, 'month');
        }
        break; // Exit the day loop since we're using months
    } else {
        current.add(1, 'day');
    }
}


// Create a unique sorted set of dates
const uniqueDates = [...new Set(allDates)].sort();

// console.log(stock);

// Now you can use uniqueDates for further analysis
let tableRows = '';
uniqueDates.reverse().forEach(dateKey => {
    // Determine date format (month or day)
    let isMonth = dateKey.length === 7;
    let dateStart, dateEnd;
    let dtF = 'YYYY-MM-DD';
    if (isMonth) {
        dateStart = moment(dateKey, 'YYYY-MM').startOf('month');
        dateEnd = moment(dateKey, 'YYYY-MM').endOf('month');
        dtF = 'YYYY-MM'
    } else {
        dateStart = moment(dateKey, 'YYYY-MM-DD').startOf('day');
        dateEnd = moment(dateKey, 'YYYY-MM-DD').endOf('day');
    }

    // Filter data for the period
    let saleF = sale.filter(s => moment(s.date).isBetween(dateStart, dateEnd, null, '[]'));
    let saLF = saL.filter(s => moment(s.date).isBetween(dateStart, dateEnd, null, '[]'));
    let puchF = puch.filter(p => moment(p.date).isBetween(dateStart, dateEnd, null, '[]'));
    let trfF = trf.filter(t => moment(t.date).isBetween(dateStart, dateEnd, null, '[]'));
    let expxF = expx.filter(e => moment(e.tarehe).isBetween(dateStart, dateEnd, null, '[]'));
    let adjF = adj.filter(a => moment(a.date).isBetween(dateStart, dateEnd, null, '[]'));
    let recvF = recv.filter(r => moment(r.date).isBetween(dateStart, dateEnd, null, '[]'));
 
    
    // Opening stock: sum opening for stocks at the start of the period
    let opening = stock.reduce((a, b) => a + Number(b.opening) * Number(b.OpenCost), 0);
        
        const   recvdO = recv.filter(r=> moment(r.date).format(dtF)<dateKey ).reduce((a,b)=>a+Number(b.qty)*b.cost,0) || 0,
                transfrO = trf.filter(r=> moment(r.date).format(dtF)<dateKey ).reduce((a,b)=>a+Number(b.qty*b.cost),0) || 0,
                
                trToO = trf.filter(r=> moment(r.date).format(dtF)<dateKey ).reduce((a,b)=>a+Number(b.qty*b.cost),0) || 0,
                wastageO = adj.filter(r=> moment(r.date).format(dtF)<dateKey ).reduce((a,b)=>a+Number(b.diff)*Number(b.cost),0) || 0,
                soldO = saL.filter(r=> moment(r.date).format(dtF)<dateKey ).reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0) || 0,
                usedO = expx.filter(r=> moment(r.tarehe).format(dtF)<dateKey ).reduce((a,b)=>a+Number(b.fuel_qty*b.fuel_cost),0) || 0,
                theTrO = transfrO - trToO 

                // console.log({dateKey,opening,recvdO,theTrO,soldO,usedO});
                opening = (opening + recvdO + wastageO) - (soldO + usedO )
 

    // Purchases: sum of purchases (cost * qty)
    let purchases = puchF.reduce((a, b) => a + Number(b.cost) * Number(b.qty), 0);
    // Received: sum of received (cost * qty)
    let received = recvF.reduce((a, b) => a + Number(b.cost) * Number(b.qty), 0);
    // Transfers: sum of transfers (cost * qty)
    let transferred = trfF.reduce((a, b) => a + Number(b.cost) * Number(b.qty), 0);
    // Wastage: sum of wastage (diff * cost)
    let wastage = adjF.reduce((a, b) => a + Number(b.diff) * Number(b.cost), 0);
    // Sales: sum of sales (amount)
    let sales = saleF.reduce((a, b) => a + Number(b.amount), 0);
    // Income: sum of sales (payed)
    let income = saleF.reduce((a, b) => a + Number(b.payed), 0);
    // Expenses: sum of expenses (kiasi)
    

    let expensesF = expxF.reduce((a, b) => a + Number(b.fuel_qty*b.fuel_cost), 0);
    let expensesA = expxF.filter(exp=>Number(exp.fuel_qty)===0).reduce((a, b) => a + Number(b.kiasi), 0);

    let expensesT = expensesF + expensesA;

    // Sale cost: sum of saL (qty_sold * cost_sold)
    let saleCost = saLF.reduce((a, b) => a + Number(b.qty_sold) * Number(b.cost_sold), 0);
    // Profit: income - (saleCost + expenses + wastage)
    let profit = income - (saleCost + expensesT + wastage);
    // Closing stock: sum closing for stocks at the end of the period
    closing = (opening + received + wastage ) - (saleCost + expensesF )
    

    tableRows += `
        <tr>
            <td> <a role="button" class="moreDetailsBtn" data-date="${dateKey}">${isMonth ? moment(dateKey, 'YYYY-MM').format('MMM YYYY') : moment(dateKey, 'YYYY-MM-DD').format('DD/MM/YYYY')}</a></td>
            <td>${Number(opening).toLocaleString()}</td>
            
            <td ${st?'hidden':''}>${Number(purchases ).toLocaleString()}</td>
            <td>${Number(received).toLocaleString()}</td>
            <td ${!st?'hidden':''} > ${Number(transferred).toLocaleString()}</td>
            <td>${Number(wastage).toLocaleString()}</td>
            <td>${Number(sales).toLocaleString()}</td>
            <td>${Number(income).toLocaleString()}</td>
            <td>${Number(expensesF).toLocaleString()}</td>
            <td>${Number(expensesA).toLocaleString()}</td>
            <td>${Number(expensesT).toLocaleString()}</td>
            <td>${Number(profit).toLocaleString()}</td>
            <td>${Number(closing).toLocaleString()}</td>
        </tr>
    `;
});

let tableHtml = `

    <table class="table table-bordered table-sm table-hover smallFont ">
        <thead>
            <tr class="smallFont table-primary" >
                <th rowspan=2 >${lang('Tarehe','Date')}</th>
                <th rowspan=2 >${lang('Stock ya Mwanzo','Opening Stock')} ${fedha}</th>
                <th rowspan=2 ${st?'hidden':''}>${lang('Manunuzi','Purchases')} ${fedha}</th>

                <th rowspan=2 >${lang('Kupokea','Received')} ${fedha}</th>
                <th rowspan=2  ${!st?'hidden':''} >${lang('Uhamisho','Transferred')} ${fedha}</th>
                <th rowspan=2 >${lang('Upotevu','Wastage')} ${fedha}</th>
                <th rowspan=2 >${lang('Mauzo','Sales')} ${fedha}</th>
                <th rowspan=2 >${lang('Mapato','Income')} ${fedha}</th>
                <th colspan=3 >${lang('Matumizi','Expenses')}</th>
                <th rowspan=2 >${lang('Faida','Profit')} ${fedha}</th>
                <th rowspan=2 >${lang('Stock ya Mwisho','Closing Stock')} ${fedha}</th>
            </tr>
            <tr class="smallFont table-primary" >
                <th >${lang('Mafuta','Fuel')} ${fedha}</th>
                <th >${lang('Mengineyo','Others')} ${fedha}</th>
                <th >${lang('Jumla','Total')} ${fedha}</th>
            </tr>

        </thead>
        <tbody>
            ${tableRows}
        </tbody>
    </table>
  
`;

$('#EvaluateByDateTable').html(tableHtml);



}

// function for fuel category analysis
const fuelAnalyze = () => {
    let { saL = [], puch = [], recv = [], trf = [], expx = [], adj = [], stock = [] } = VDATA;
    const { st } = filters();

    // Filter data if st is set except the purchases which are always for st 0
    if (st) {
        recv = recv.filter(r => r.st === st);
        trf = trf.filter(t => t.st === st);
        expx = expx.filter(e => e.st === st);
        adj = adj.filter(a => a.st === st);
        saL = saL.filter(s => s.st === st);
        stock = stock.filter(s => s.st === st);
    }

    let fuelMap = {};

    // Aggregate all fuel types from stock
    stock.forEach(s => {
        if (!fuelMap[s.fuelName]) {
            fuelMap[s.fuelName] = {
                openingQty: 0,
                openingCost: 0,
                purchasesQty: 0,
                purchasesCost: 0,
                receivedQty: 0,
                receivedCost: 0,
                transferredQty: 0,
                transferredCost: 0,
                wastageQty: 0,
                wastageCost: 0,
                salesQty: 0,
                salesCost: 0,
                usageQty: 0,
                usageCost: 0,
                closingQty: 0,
                closingCost: 0
            };
        }
        fuelMap[s.fuelName].openingQty += Number(s.opening);
        fuelMap[s.fuelName].openingCost += Number(s.opening) * Number(s.OpenCost);
        fuelMap[s.fuelName].closingQty += Number(s.closing);
        fuelMap[s.fuelName].closingCost += Number(s.closing) * Number(s.CloseCost);
    });

    // Purchases (only when st == 0)
    if (st === 0) {
        puch.forEach(p => {
            const fuel = p.fuelName || p.fuel;
            if (!fuelMap[fuel]) fuelMap[fuel] = {
                openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
                transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
                usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
            };
            fuelMap[fuel].purchasesQty += Number(p.qty);
            fuelMap[fuel].purchasesCost += Number(p.cost) * Number(p.qty);
        });
    }

    // Received (when st != 0)
    if (st !== 0) {
        recv.forEach(r => {
            const fuel = r.fuelName || r.fuel;
            if (!fuelMap[fuel]) fuelMap[fuel] = {
                openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
                transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
                usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
            };
            fuelMap[fuel].receivedQty += Number(r.qty);
            fuelMap[fuel].receivedCost += Number(r.cost) * Number(r.qty);
        });
        trf.forEach(t => {
            const fuel = t.fuelName || t.fuel;
            if (!fuelMap[fuel]) fuelMap[fuel] = {
                openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
                transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
                usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
            };
            fuelMap[fuel].transferredQty += Number(t.qty);
            fuelMap[fuel].transferredCost += Number(t.cost) * Number(t.qty);
        });
    }

    // Wastage
    adj.forEach(a => {
        const fuel = a.fuelName || a.fuel;
        if (!fuelMap[fuel]) fuelMap[fuel] = {
            openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
            transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
            usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
        };
        fuelMap[fuel].wastageQty += Number(a.diff);
        fuelMap[fuel].wastageCost += Number(a.diff) * Number(a.cost);
    });

    // Sales
    saL.forEach(s => {
        const fuel = s.fuelName || s.fuel;
        if (!fuelMap[fuel]) fuelMap[fuel] = {
            openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
            transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
            usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
        };
        fuelMap[fuel].salesQty += Number(s.qty_sold);
        fuelMap[fuel].salesCost += Number(s.qty_sold) * Number(s.cost_sold);
    });

    // Fuel usage (expenses with fuel_qty > 0)
    expx.filter(e => Number(e.fuel_qty) > 0).forEach(e => {
        const fuel = e.fuelName || e.fuel;
        if (!fuelMap[fuel]) fuelMap[fuel] = {
            openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
            transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
            usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
        };
        fuelMap[fuel].usageQty += Number(e.fuel_qty);
        fuelMap[fuel].usageCost += Number(e.fuel_qty) * Number(e.fuel_cost);
    });

    // Assign background colors for each column group
    const bgColors = {
        opening: 'background-color:rgba(0,123,255,0.08);',      // blue-ish
        purchases: 'background-color:rgba(40,167,69,0.08);',    // green-ish
        received: 'background-color:rgba(255,193,7,0.08);',     // yellow-ish
        transferred: 'background-color:rgba(23,162,184,0.08);', // cyan-ish
        wastage: 'background-color:rgba(220,53,69,0.08);',      // red-ish
        sales: 'background-color:rgba(108,117,125,0.08);',      // gray-ish
        usage: 'background-color:rgba(255,87,34,0.08);',        // orange-ish
        closing: 'background-color:rgba(40,167,69,0.08);'       // green-ish (darker)
    };
    // Build table
    let fuelRows = '';
    Object.keys(fuelMap).forEach(fuel => {
        const f = fuelMap[fuel];
        fuelRows += `
            <tr>
            <td class="text-capitalize">${fuel}</td>
            <td style="${bgColors.opening}">${Number(f.openingQty).toLocaleString()}</td>
            <td style="${bgColors.opening}">${f.openingQty ? Number((f.openingCost / f.openingQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.opening}">${Number(f.openingCost).toLocaleString()}</td>
            ${st === 0 ? `
                <td style="${bgColors.purchases}">${Number(f.purchasesQty).toLocaleString()}</td>
                <td style="${bgColors.purchases}">${f.purchasesQty ? Number((f.purchasesCost / f.purchasesQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td style="${bgColors.purchases}">${Number(f.purchasesCost).toLocaleString()}</td>
                
                <td style="${bgColors.received}">${Number(f.receivedQty).toLocaleString()}</td>
                <td style="${bgColors.received}">${f.receivedQty ? Number((f.receivedCost / f.receivedQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td style="${bgColors.received}">${Number(f.receivedCost).toLocaleString()}</td>
            ` : `

                
                <td style="${bgColors.received}">${Number(f.receivedQty).toLocaleString()}</td>
                <td style="${bgColors.received}">${f.receivedQty ? Number((f.receivedCost / f.receivedQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td style="${bgColors.received}">${Number(f.receivedCost).toLocaleString()}</td>

                <td style="${bgColors.transferred}">${Number(f.transferredQty).toLocaleString()}</td>
                <td style="${bgColors.transferred}">${f.transferredQty ? Number((f.transferredCost / f.transferredQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td style="${bgColors.transferred}">${Number(f.transferredCost).toLocaleString()}</td>
            `}
            <td style="${bgColors.wastage}">${Number(f.wastageQty).toLocaleString()}</td>
            <td style="${bgColors.wastage}">${f.wastageQty ? Number((f.wastageCost / f.wastageQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.wastage}">${Number(f.wastageCost).toLocaleString()}</td>
            <td style="${bgColors.sales}">${Number(f.salesQty).toLocaleString()}</td>
            <td style="${bgColors.sales}">${f.salesQty ? Number((f.salesCost / f.salesQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.sales}">${Number(f.salesCost).toLocaleString()}</td>
            <td style="${bgColors.usage}">${Number(f.usageQty).toLocaleString()}</td>
            <td style="${bgColors.usage}">${f.usageQty ? Number((f.usageCost / f.usageQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.usage}">${Number(f.usageCost).toLocaleString()}</td>
            <td style="${bgColors.closing}">${Number(f.closingQty).toLocaleString()}</td>
            <td style="${bgColors.closing}">${f.closingQty ? Number((f.closingCost / f.closingQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.closing}">${Number(f.closingCost).toLocaleString()}</td>
            </tr>
        `;
    });

    if (Object.keys(fuelMap).length > 0) {
        let total = {
            openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
            transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
            usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
        };
        Object.values(fuelMap).forEach(f => {
            total.openingQty += f.openingQty;
            total.openingCost += f.openingCost;
            total.purchasesQty += f.purchasesQty;
            total.purchasesCost += f.purchasesCost;
            total.receivedQty += f.receivedQty;
            total.receivedCost += f.receivedCost;
            total.transferredQty += f.transferredQty;
            total.transferredCost += f.transferredCost;
            total.wastageQty += f.wastageQty;
            total.wastageCost += f.wastageCost;
            total.salesQty += f.salesQty;
            total.salesCost += f.salesCost;
            total.usageQty += f.usageQty;
            total.usageCost += f.usageCost;
            total.closingQty += f.closingQty;
            total.closingCost += f.closingCost;
        });
        fuelRows += `
            <tr class="table-secondary font-weight-bold">
                <td>${lang('Jumla','Total')}</td>
                <td>${Number(total.openingQty).toLocaleString()}</td>
                <td>${total.openingQty ? Number((total.openingCost / total.openingQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.openingCost).toLocaleString()}</td>
                ${st === 0 ? `
                    <td>${Number(total.purchasesQty).toLocaleString()}</td>
                    <td>${total.purchasesQty ? Number((total.purchasesCost / total.purchasesQty).toFixed(2)).toLocaleString() : '-'}</td>
                    <td>${Number(total.purchasesCost).toLocaleString()}</td>
                    <td>${Number(total.receivedQty).toLocaleString()}</td>
                    <td>${total.receivedQty ? Number((total.receivedCost / total.receivedQty).toFixed(2)).toLocaleString() : '-'}</td>
                    <td>${Number(total.receivedCost).toLocaleString()}</td>                    
                ` : `
                    <td>${Number(total.receivedQty).toLocaleString()}</td>
                    <td>${total.receivedQty ? Number((total.receivedCost / total.receivedQty).toFixed(2)).toLocaleString() : '-'}</td>
                    <td>${Number(total.receivedCost).toLocaleString()}</td>
                   
                    <td>${Number(total.transferredQty).toLocaleString()}</td>
                    <td>${total.transferredQty ? Number((total.transferredCost / total.transferredQty).toFixed(2)).toLocaleString() : '-'}</td>
                    <td>${Number(total.transferredCost).toLocaleString()}</td>
                `}
                <td>${Number(total.wastageQty).toLocaleString()}</td>
                <td>${total.wastageQty ? Number((total.wastageCost / total.wastageQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.wastageCost).toLocaleString()}</td>
                <td>${Number(total.salesQty).toLocaleString()}</td>
                <td>${total.salesQty ? Number((total.salesCost / total.salesQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.salesCost).toLocaleString()}</td>
                <td>${Number(total.usageQty).toLocaleString()}</td>
                <td>${total.usageQty ? Number((total.usageCost / total.usageQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.usageCost).toLocaleString()}</td>
                <td>${Number(total.closingQty).toLocaleString()}</td>
                <td>${total.closingQty ? Number((total.closingCost / total.closingQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.closingCost).toLocaleString()}</td>
            </tr>
        `;
    }

    let fuelTable = `
        <table class="table table-bordered table-sm smallFont">
            <thead>
                <tr class="table-primary">
                    <th rowspan="2">${lang('Aina ya Mafuta','Fuel Name')}</th>
                    <th colspan="3">${lang('Stock ya Mwanzo','Opening Stock')}</th>
                    ${st === 0 ? `
                        <th colspan="3">${lang('Manunuzi','Purchases')}</th>
                         <th colspan="3">${lang('Kupokelewa','Received')}</th>
                    ` : `
                        <th colspan="3">${lang('Kupokelewa','Received')}</th>
                        <th colspan="3">${lang('Uhamisho','Transferred')}</th>
                    `}
                    <th colspan="3">${lang('Upotevu','Wastage')}</th>
                    <th colspan="3">${lang('Mauzo','Sales')}</th>
                    <th colspan="3">${lang('Matumizi','Fuel Usage')}</th>
                    <th colspan="3">${lang('Stock ya Mwisho','Closing Stock')}</th>
                </tr>
                <tr class="table-primary">
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    ${st === 0 ? `
                        <th>${lang('Qty','Qty (LTRS)')}</th>
                        <th>${lang('Cost/LTR','Cost/LTR')}</th>
                        <th>${lang('Total','Total Cost')} ${fedha}</th>
                        <th>${lang('Qty','Qty (LTRS)')}</th>
                        <th>${lang('Cost/LTR','Cost/LTR')}</th>
                        <th>${lang('Total','Total Cost')} ${fedha}</th>
                        
                    ` : `
                        <th>${lang('Qty','Qty (LTRS)')}</th>
                        <th>${lang('Cost/LTR','Cost/LTR')}</th>
                        <th>${lang('Total','Total Cost')} ${fedha}</th>

                        <th>${lang('Qty','Qty (LTRS)')}</th>
                        <th>${lang('Cost/LTR','Cost/LTR')}</th>
                        <th>${lang('Total','Total Cost')} ${fedha}</th>
                    `}
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                </tr>
            </thead>
            <tbody>
                ${fuelRows}
            </tbody>
        </table>
    `;

    $('#fuelAnalyzeTable').html(fuelTable);
}

// function for fuel tanks analysis
const tankAnalyze = () =>{
    // Build tank analysis table with qty in LTRS, cost/LTRS, and total cost for each stage
    let { saL = [], puch = [], recv = [], trf = [], expx = [], adj = [], stock = [] } = VDATA;
    const { st } = filters();
    let tankMap = {};

    // Filter data if st is set except the purchases which are always for st 0
    if (st) {
        recv = recv.filter(r => r.st === st);
        trf = trf.filter(t => t.st === st);
        expx = expx.filter(e => e.st === st);
        adj = adj.filter(a => a.st === st);
        saL = saL.filter(s => s.st === st);
        stock = stock.filter(s => s.st === st);
    }

    // Aggregate all tanks from stock
    stock.forEach(s => {
        const key = s.tank;
        if (!tankMap[key]) {
            tankMap[key] = {
                tankName: s.TankName,
                fuelName: s.fuelName || s.fuel,
                stationName: s.stationName,
                openingQty: 0,
                openingCost: 0,
                purchasesQty: 0,
                purchasesCost: 0,
                receivedQty: 0,
                receivedCost: 0,
                transferredQty: 0,
                transferredCost: 0,
                wastageQty: 0,
                wastageCost: 0,
                salesQty: 0,
                salesCost: 0,
                usageQty: 0,
                usageCost: 0,
                closingQty: 0,
                closingCost: 0
            };
        }
        tankMap[key].openingQty += Number(s.opening);
        tankMap[key].openingCost += Number(s.opening) * Number(s.OpenCost);
        tankMap[key].closingQty += Number(s.closing);
        tankMap[key].closingCost += Number(s.closing) * Number(s.CloseCost);
    });

    // Purchases (only when st == 0)
    if (st === 0) {
        puch.forEach(p => {
            if (!p.tank) return;
            const key = p.tank;
            if (!tankMap[key]) tankMap[key] = { tankName: p.TankName || '', fuelName: p.fuelName || p.fuel, stationName: p.stationName || '', openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0, transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0, usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0 };
            tankMap[key].purchasesQty += Number(p.qty);
            tankMap[key].purchasesCost += Number(p.cost) * Number(p.qty);
        });
    }

    // Received (when st != 0)
    if (st !== 0) {
        recv.forEach(r => {
            if (!r.tank) return;
            const key = r.tank;
            if (!tankMap[key]) tankMap[key] = { tankName: r.TankName || '', fuelName: r.fuelName || r.fuel, stationName: r.stationName || '', openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0, transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0, usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0 };
            tankMap[key].receivedQty += Number(r.qty);
            tankMap[key].receivedCost += Number(r.cost) * Number(r.qty);
        });
        trf.forEach(t => {
            if (!t.tank) return;
            const key = t.tank;
            if (!tankMap[key]) tankMap[key] = { tankName: t.TankName || '', fuelName: t.fuelName || t.fuel, stationName: t.stationName || '', openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0, transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0, usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0 };
            tankMap[key].transferredQty += Number(t.qty);
            tankMap[key].transferredCost += Number(t.cost) * Number(t.qty);
        });
    }

    // Wastage
    adj.forEach(a => {
        if (!a.tank) return;
        const key = a.tank;
        if (!tankMap[key]) tankMap[key] = { tankName: a.TankName || '', fuelName: a.fuelName || a.fuel, stationName: a.stationName || '', openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0, transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0, usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0 };
        tankMap[key].wastageQty += Number(a.diff);
        tankMap[key].wastageCost += Number(a.diff) * Number(a.cost);
    });

    // Sales
    saL.forEach(s => {
        if (!s.tank_id) return;
        const key = s.tank_id;
        if (!tankMap[key]) tankMap[key] = { tankName: s.TankName || '', fuelName: s.fuelName || s.fuel, stationName: s.stationName || '', openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0, transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0, usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0 };
        tankMap[key].salesQty += Number(s.qty_sold);
        tankMap[key].salesCost += Number(s.qty_sold) * Number(s.cost_sold);
    });

    // Fuel usage (expenses with fuel_qty > 0)
    expx.filter(e => Number(e.fuel_qty) > 0).forEach(e => {
        if (!e.tank) return;
        const key = e.tank;
        if (!tankMap[key]) tankMap[key] = { tankName: e.TankName || '', fuelName: e.fuelName || e.fuel, stationName: e.stationName || '', openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0, transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0, usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0 };
        tankMap[key].usageQty += Number(e.fuel_qty);
        tankMap[key].usageCost += Number(e.fuel_qty) * Number(e.fuel_cost);
    });

    const bgColors = {
        opening: 'background-color:rgba(0,123,255,0.08);',      // blue-ish
        purchases: 'background-color:rgba(40,167,69,0.08);',    // green-ish
        received: 'background-color:rgba(255,193,7,0.08);',     // yellow-ish
        transferred: 'background-color:rgba(23,162,184,0.08);', // cyan-ish
        wastage: 'background-color:rgba(220,53,69,0.08);',      // red-ish
        sales: 'background-color:rgba(108,117,125,0.08);',      // gray-ish
        usage: 'background-color:rgba(255,87,34,0.08);',        // orange-ish
        closing: 'background-color:rgba(40,167,69,0.08);'       // green-ish (darker)
    };

    // Build table
    let tankRows = '';
    Object.keys(tankMap).forEach(key => {
        const t = tankMap[key];
        tankRows += `
            <tr>
            <td class="text-capitalize"><a role="button" class="moreDetailsBtn" data-tnk_id="${key}">${t.tankName}</a></td>
            <td class="text-capitalize">${t.fuelName}</td>
            <td class="text-capitalize">${t.stationName}</td>
            <td style="${bgColors.opening}">${Number(t.openingQty).toLocaleString()}</td>
            <td style="${bgColors.opening}">${t.openingQty ? Number((t.openingCost / t.openingQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.opening}">${Number(t.openingCost).toLocaleString()} </td>
          
            <td style="${bgColors.received}">${Number(t.receivedQty).toLocaleString()}</td>
            <td style="${bgColors.received}">${t.receivedQty ? Number((t.receivedCost / t.receivedQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.received}">${Number(t.receivedCost).toLocaleString()} </td>
            <td style="${bgColors.transferred}">${Number(t.transferredQty).toLocaleString()}</td>
            <td style="${bgColors.transferred}">${t.transferredQty ? Number((t.transferredCost / t.transferredQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.transferred}">${Number(t.transferredCost).toLocaleString()} </td>
            
            <td style="${bgColors.wastage}">${Number(t.wastageQty).toLocaleString()}</td>
            <td style="${bgColors.wastage}">${t.wastageQty ? Number((t.wastageCost / t.wastageQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.wastage}">${Number(t.wastageCost).toLocaleString()} </td>
            <td style="${bgColors.sales}">${Number(t.salesQty).toLocaleString()}</td>
            <td style="${bgColors.sales}">${t.salesQty ? Number((t.salesCost / t.salesQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.sales}">${Number(t.salesCost).toLocaleString()} </td>
            <td style="${bgColors.usage}">${Number(t.usageQty).toLocaleString()}</td>
            <td style="${bgColors.usage}">${t.usageQty ? Number((t.usageCost / t.usageQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.usage}">${Number(t.usageCost).toLocaleString()} </td>
            <td style="${bgColors.closing}">${Number(t.closingQty).toLocaleString()}</td>
            <td style="${bgColors.closing}">${t.closingQty ? Number((t.closingCost / t.closingQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.closing}">${Number(t.closingCost).toLocaleString()} </td>
            </tr>
        `;
    });

    if (Object.keys(tankMap).length > 0) {
        let total = {
            openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
            transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
            usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
        };
        Object.values(tankMap).forEach(t => {
            total.openingQty += t.openingQty;
            total.openingCost += t.openingCost;
            total.purchasesQty += t.purchasesQty;
            total.purchasesCost += t.purchasesCost;
            total.receivedQty += t.receivedQty;
            total.receivedCost += t.receivedCost;
            total.transferredQty += t.transferredQty;
            total.transferredCost += t.transferredCost;
            total.wastageQty += t.wastageQty;
            total.wastageCost += t.wastageCost;
            total.salesQty += t.salesQty;
            total.salesCost += t.salesCost;
            total.usageQty += t.usageQty;
            total.usageCost += t.usageCost;
            total.closingQty += t.closingQty;
            total.closingCost += t.closingCost;
        });
        tankRows += `
            <tr class="table-secondary font-weight-bold">
                <td>${lang('Jumla','Total')}</td>
                <td></td>
                <td></td>
                <td>${Number(total.openingQty).toLocaleString()}</td>
                <td>${total.openingQty ? Number((total.openingCost / total.openingQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.openingCost).toLocaleString()} </td>
            
                <td>${Number(total.receivedQty).toLocaleString()}</td>
                <td>${total.receivedQty ? Number((total.receivedCost / total.receivedQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.receivedCost).toLocaleString()} </td>
                <td>${Number(total.transferredQty).toLocaleString()}</td>
                <td>${total.transferredQty ? Number((total.transferredCost / total.transferredQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.transferredCost).toLocaleString()} </td>
             
                <td>${Number(total.wastageQty).toLocaleString()}</td>
                <td>${total.wastageQty ? Number((total.wastageCost / total.wastageQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.wastageCost).toLocaleString()} </td>
                <td>${Number(total.salesQty).toLocaleString()}</td>
                <td>${total.salesQty ? Number((total.salesCost / total.salesQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.salesCost).toLocaleString()} </td>
                <td>${Number(total.usageQty).toLocaleString()}</td>
                <td>${total.usageQty ? Number((total.usageCost / total.usageQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.usageCost).toLocaleString()} </td>
                <td>${Number(total.closingQty).toLocaleString()}</td>
                <td>${total.closingQty ? Number((total.closingCost / total.closingQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.closingCost).toLocaleString()} </td>
            </tr>
        `;
    }

    let tankTable = `
        <table class="table table-bordered table-sm table-hover smallFont">
            <thead>
                <tr class="table-primary">
                    <th rowspan="2">${lang('Tank','Tank')}</th>
                    <th rowspan="2">${lang('Aina ya Mafuta','Fuel Name')}</th>
                    <th rowspan="2">${lang('Kituo','Station')}</th>
                    <th colspan="3">${lang('Stock ya Mwanzo','Opening Stock')}</th>
                 
                    <th colspan="3">${lang('Kupokelewa','Received')}</th>
                    <th colspan="3">${lang('Uhamisho','Transferred')}</th>
                   
                    <th colspan="3">${lang('Upotevu','Wastage')}</th>
                    <th colspan="3">${lang('Mauzo','Sales')}</th>
                    <th colspan="3">${lang('Matumizi','Fuel Usage')}</th>
                    <th colspan="3">${lang('Stock ya Mwisho','Closing Stock')}</th>
                </tr>
                <tr class="table-primary">
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                 
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                  
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                </tr>
            </thead>
            <tbody>
                ${tankRows}
            </tbody>
        </table>
    `;

    $('#tankAnalyzeTable').html(tankTable);
  
}

// ANALYSIS BY STATION
const stationAnalyze = () =>{
let { saL = [], recv = [], trf = [], expx = [], adj = [], sale = [], stock = [] } = VDATA;
const { st } = filters();



// Aggregate by station
let stationMap = {};
stock.forEach(s => {
    const key = s.stationId || s.st;
    if (!stationMap[key]) {
        stationMap[key] = {
            stationName: s.stationName || '-',
            opening: 0,
            received: 0,
            transferred: 0,
            wastage: 0,
            sales: 0,
            income: 0,
            expFuel: 0,
            expOther: 0,
            expTotal: 0,
            profit: 0,
            closing: 0
        };
    }
    stationMap[key].opening += Number(s.opening) * Number(s.OpenCost);
    stationMap[key].closing += Number(s.closing) * Number(s.CloseCost);
});

// Received
recv.forEach(r => {
    const key = r.st || r.stationId;
    if (!stationMap[key]) stationMap[key] = { stationName: r.stationName || '-', opening: 0, received: 0, transferred: 0, wastage: 0, sales: 0, income: 0, expFuel: 0, expOther: 0, expTotal: 0, profit: 0, closing: 0 };
    stationMap[key].received += Number(r.cost) * Number(r.qty);
});

// Transferred
trf.forEach(t => {
    const key = t.st || t.stationId;
    if (!stationMap[key]) stationMap[key] = { stationName: t.stationName || '-', opening: 0, received: 0, transferred: 0, wastage: 0, sales: 0, income: 0, expFuel: 0, expOther: 0, expTotal: 0, profit: 0, closing: 0 };
    stationMap[key].transferred += Number(t.cost) * Number(t.qty);
});

// Wastage
adj.forEach(a => {
    const key = a.st || a.stationId;
    if (!stationMap[key]) stationMap[key] = { stationName: a.stationName || '-', opening: 0, received: 0, transferred: 0, wastage: 0, sales: 0, income: 0, expFuel: 0, expOther: 0, expTotal: 0, profit: 0, closing: 0 };
    stationMap[key].wastage += Number(a.diff) * Number(a.cost);
});

// Sales and Income
sale.forEach(s => {
    const key = s.st || s.stationId;
    if (!stationMap[key]) stationMap[key] = { stationName: s.stationName || '-', opening: 0, received: 0, transferred: 0, wastage: 0, sales: 0, income: 0, expFuel: 0, expOther: 0, expTotal: 0, profit: 0, closing: 0 };
    stationMap[key].sales += Number(s.amount);
    stationMap[key].income += Number(s.payed);
});

// Expenses
expx.forEach(e => {
    const key = e.st || e.stationId;
    if (!stationMap[key]) stationMap[key] = { stationName: e.stationName || '-', opening: 0, received: 0, transferred: 0, wastage: 0, sales: 0, income: 0, expFuel: 0, expOther: 0, expTotal: 0, profit: 0, closing: 0 };
    if (Number(e.fuel_qty) > 0) {
        stationMap[key].expFuel += Number(e.fuel_qty) * Number(e.fuel_cost);
    } else {
        stationMap[key].expOther += Number(e.kiasi);
    }
});

// Sale cost for profit calculation
let saleCostMap = {};
saL.forEach(s => {
    const key = s.st || s.stationId;
    if (!saleCostMap[key]) saleCostMap[key] = 0;
    saleCostMap[key] += Number(s.qty_sold) * Number(s.cost_sold);
});

// Calculate total expenses and profit
Object.keys(stationMap).forEach(key => {
    const stn = stationMap[key];
    stn.expTotal = stn.expFuel + stn.expOther;
    stn.profit = stn.income - ((saleCostMap[key] || 0) + stn.expTotal + stn.wastage);
});

// Build table rows
let rows = '';
Object.keys(stationMap).forEach(key => {
    const s = stationMap[key];
    rows += `
        <tr>
            <td class="text-capitalize"> <a role="button" class="moreDetailsBtn" data-st_id="${key}">${s.stationName}</a></td>
            <td>${Number(s.opening).toLocaleString()}</td>
            <td>${Number(s.received).toLocaleString()}</td>
            <td>${Number(s.transferred).toLocaleString()}</td>
            <td>${Number(s.wastage).toLocaleString()}</td>
            <td>${Number(s.sales).toLocaleString()}</td>
            <td>${Number(s.income).toLocaleString()}</td>
            <td>${Number(s.expFuel).toLocaleString()}</td>
            <td>${Number(s.expOther).toLocaleString()}</td>
            <td>${Number(s.expTotal).toLocaleString()}</td>
            <td>${Number(s.profit).toLocaleString()}</td>
            <td>${Number(s.closing).toLocaleString()}</td>
        </tr>
    `;
});

// Totals row
if (Object.keys(stationMap).length > 0) {
    let total = {
        opening: 0, received: 0, transferred: 0, wastage: 0, sales: 0, income: 0,
        expFuel: 0, expOther: 0, expTotal: 0, profit: 0, closing: 0
    };
    Object.values(stationMap).forEach(s => {
        total.opening += s.opening;
        total.received += s.received;
        total.transferred += s.transferred;
        total.wastage += s.wastage;
        total.sales += s.sales;
        total.income += s.income;
        total.expFuel += s.expFuel;
        total.expOther += s.expOther;
        total.expTotal += s.expTotal;
        total.profit += s.profit;
        total.closing += s.closing;
    });
    rows += `
        <tr class="table-secondary font-weight-bold">
            <td>${lang('Jumla','Total')}</td>
            <td>${Number(total.opening).toLocaleString()}</td>
            <td>${Number(total.received).toLocaleString()}</td>
            <td>${Number(total.transferred).toLocaleString()}</td>
            <td>${Number(total.wastage).toLocaleString()}</td>
            <td>${Number(total.sales).toLocaleString()}</td>
            <td>${Number(total.income).toLocaleString()}</td>
            <td>${Number(total.expFuel).toLocaleString()}</td>
            <td>${Number(total.expOther).toLocaleString()}</td>
            <td>${Number(total.expTotal).toLocaleString()}</td>
            <td>${Number(total.profit).toLocaleString()}</td>
            <td>${Number(total.closing).toLocaleString()}</td>
        </tr>
    `;
}

let tableHtml = `
    <table class="table table-bordered table-sm smallFont">
        <thead>
            <tr class="table-primary">
                <th>${lang('Kituo','Station')}</th>
                <th>${lang('Stock ya Mwanzo','Opening Stock')}</th>
                <th>${lang('Kupokelewa','Received')}</th>
                <th>${lang('Uhamisho','Transferred')}</th>
                <th>${lang('Upotevu','Wastage')}</th>
                <th>${lang('Mauzo','Sales')}</th>
                <th>${lang('Mapato','Income')}</th>
                <th>${lang('Matumizi ya Mafuta','Fuel Expenses')}</th>
                <th>${lang('Matumizi Mengineyo','Other Expenses')}</th>
                <th>${lang('Jumla ya Matumizi','Total Expenses')}</th>
                <th>${lang('Faida','Profit')}</th>
                <th>${lang('Stock ya Mwisho','Closing Stock')}</th>
            </tr>
        </thead>
        <tbody>
            ${rows}
        </tbody>
    </table>
`;

$('#stationAnalyzeTable').html(tableHtml);

}

$('body').on('click', '.moreDetailsBtn', function() {
    const stxn = Number($(this).data('st_id')) || 0;
    const tnk = Number($(this).data('tnk_id')) || 0;
    const theDate = $(this).data('date') || null ;
    const dt = { stxn, tnk, dte: theDate };
    MoreDetailsFuel(dt);
    
});

// function for fuel category analysis
const MoreDetailsFuel = dt => {
    $('#Salecateg').hide();
    $('#MoreDetails').fadeIn(100);

    let { saL = [], puch = [], recv = [], trf = [], expx = [], adj = [], stock = [] } = VDATA;
    const { st } = filters();
    const { stxn,dte,tnk } = dt;
    // Filter data if st is set except the purchases which are always for st 0
    // create title for details and filter all the data above by the details
    let title = '';
    if (stxn) {
        const stn = stock.find(s => s.st === stxn);
        title = `${lang('Maelezo Zaidi Ya Kituo','More Details For Station')} : <span class="bluePrint" >${stn ? stn.stationName : ''}</span>`;
        recv = recv.filter(r => r.st === stxn);
        trf = trf.filter(t => t.st === stxn);
        expx = expx.filter(e => e.st === stxn);
        adj = adj.filter(a => a.st === stxn);
        saL = saL.filter(s => s.st === stxn);
        stock = stock.filter(s => s.stationId === stxn);
    }

    if (st) {
        recv = recv.filter(r => r.st === st);
        trf = trf.filter(t => t.st === st);
        expx = expx.filter(e => e.st === st);
        adj = adj.filter(a => a.st === st);
        saL = saL.filter(s => s.st === st);
        stock = stock.filter(s => s.st === st);
    }

    if (tnk) {
        const tnkObj = stock.find(t => t.tank === tnk);
        
        title = `${lang('Maelezo Zaidi Ya Tanki','More Details For Tank')} : <span class="bluePrint">${tnkObj ? tnkObj.TankName : ''}</span>`;
        puch = puch.filter(p => p.tank === tnk);
        recv = recv.filter(r => r.tank === tnk);
        trf = trf.filter(t => t.tank === tnk);
        expx = expx.filter(e => e.tank === tnk);
        adj = adj.filter(a => a.tank === tnk);
        saL = saL.filter(s => s.tank_id === tnk);
        stock = stock.filter(s => s.tank === tnk);
    }
    if (dte!=null) {
        title = `${lang('Maelezo Zaidi Ya Tarehe','More Details For Date')} : <span class="bluePrint">${moment(dte).format('DD/MM/YYYY')}</span>`;
        // the date is stored in dte field in either YYYY-MM-DD or YYYY-MM depending on the context we can use moment to filter
        // first check if it's a full date or just month
        const isFullDate = /^\d{4}-\d{2}-\d{2}$/.test(dte);
        let dtFormat = 'YYYY-MM';
        if (isFullDate) {
            dtFormat = 'YYYY-MM-DD';
        }

      



        // create another stock for the date by tracking all stock movements for the date and calculating opening and closing stock
        // since this date is just a range from the stock data we can calculate opening and closing stock from the stock data
        
        stock.forEach(s => {
            
            // Adjust opening and closing based on movements on that date
                    // Opening stock: sum opening for stocks at the start of the period
        let opening = s.opening*s.OpenCost;

            const   recvdO = recv.filter(r=>r.To_id===s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.qty)*b.cost,0) || 0,
                    transfrO = trf.filter(r=> r.trFr===s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.qty*b.cost),0) || 0,

                    trToO = trf.filter(r=> r.To_id===s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.qty*b.cost),0) || 0,
                    wastageO = adj.filter(r=> r.tank===s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.diff)*Number(b.cost),0) || 0,
                    soldO = saL.filter(r=> r.tank_id===s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0) || 0,
                    usedO = expx.filter(r=>r.tank===s.tank && moment(r.tarehe).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.fuel_qty*b.fuel_cost),0) || 0,
                    theTrO = transfrO - trToO
                    opening = (opening + recvdO + wastageO) - (soldO + usedO )

                    // get the opening stock quantity from the stock data since we have the opening stock value and cost
                   
             let openingQty = s.opening;
             const recvdQty = recv.filter(r=> r.To_id === s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.qty),0) || 0,
                   transfrQty = trf.filter(r=> r.trFr===s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.qty),0) || 0,
                   trToQty = trf.filter(r=> r.To_id===s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.qty),0) || 0,
                     wastageQty = adj.filter(r=> r.tank===s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.diff),0) || 0,
                    soldQty = saL.filter(r=> r.tank_id===s.tank && moment(r.date).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.qty_sold),0) || 0,
                    usedQty = expx.filter(r=> r.tank===s.tank && moment(r.tarehe).format(dtFormat)<dte ).reduce((a,b)=>a+Number(b.fuel_qty),0) || 0,
                    theTrQty = transfrQty - trToQty
                    openingQty = (openingQty + recvdQty + wastageQty) - (soldQty + usedQty + theTrQty)
                    s.OpenCost = openingQty ? (opening / openingQty) : 0;
                    // Closing stock: opening + received + wastage - sold - used - net transfer for the date
          

                    // get the stock movements qty for the date since we have got the opening stock value
                    const   recvd = recv.filter(r=>r.To_id===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.qty)*b.cost,0) || 0,
                            transfr = trf.filter(r=> r.trFr===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.qty*b.cost),0) || 0,
                            trTo = trf.filter(r=> r.To_id===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.qty*b.cost),0) || 0,
                            wastage = adj.filter(r=> r.tank===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.diff)*Number(b.cost),0) || 0,
                            sold = saL.filter(r=> r.tank_id===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.qty_sold*b.cost_sold),0) || 0,
                            used = expx.filter(r=> r.tank===s.tank && moment(r.tarehe).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.fuel_qty*b.fuel_cost),0) || 0,
                            theTr = transfr - trTo
                    // closing stock is opening + received + wastage - sold - used - net transfer
                    let closing = (opening + recvd + wastage) - (sold + used + theTr);
                    // get the closing stock quantity from the stock data since we have the closing stock value and cost
                    let closingQty = openingQty;
                    const recvdQtyC = recv.filter(r=> r.To_id===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.qty),0) || 0,
                          transfrQtyC = trf.filter(r=> r.trFr===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.qty),0) || 0,
                          trToQtyC = trf.filter(r=> r.To_id===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.qty),0) || 0,
                          wastageQtyC = adj.filter(r=> r.tank===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.diff),0) || 0,
                          soldQtyC = saL.filter(r=> r.tank_id===s.tank && moment(r.date).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.qty_sold),0) || 0,
                          usedQtyC = expx.filter(r=> r.tank===s.tank && moment(r.tarehe).format(dtFormat)===dte ).reduce((a,b)=>a+Number(b.fuel_qty),0) || 0,
                          theTrQtyC = transfrQtyC - trToQtyC
                        closingQty = (closingQty + recvdQtyC + wastageQtyC) - (soldQtyC + usedQtyC + theTrQtyC)
                    s.CloseCost = closingQty ? (closing / closingQty) : 0;

                    s.opening = openingQty;
                    s.closing = closingQty;

           
      

        });

        

        puch = puch.filter(p => moment(p.date).format(dtFormat) === dte);
        recv = recv.filter(r => moment(r.date).format(dtFormat) === dte);
        trf = trf.filter(t => moment(t.date).format(dtFormat) === dte);
        expx = expx.filter(e => moment(e.tarehe).format(dtFormat) === dte);
        adj = adj.filter(a => moment(a.date).format(dtFormat) === dte);
        saL = saL.filter(s => moment(s.date).format(dtFormat) === dte);

        

    }

    

    let fuelMap = {};

    // Aggregate all fuel types from stock
    stock.forEach(s => {
        if (!fuelMap[s.fuelName]) {
            fuelMap[s.fuelName] = {
                openingQty: 0,
                openingCost: 0,
                purchasesQty: 0,
                purchasesCost: 0,
                receivedQty: 0,
                receivedCost: 0,
                transferredQty: 0,
                transferredCost: 0,
                wastageQty: 0,
                wastageCost: 0,
                salesQty: 0,
                salesCost: 0,
                usageQty: 0,
                usageCost: 0,
                closingQty: 0,
                closingCost: 0
            };
        }
        fuelMap[s.fuelName].openingQty += Number(s.opening);
        fuelMap[s.fuelName].openingCost += Number(s.opening) * Number(s.OpenCost);
        fuelMap[s.fuelName].closingQty += Number(s.closing);
        fuelMap[s.fuelName].closingCost += Number(s.closing) * Number(s.CloseCost);
    });

    // Purchases (only when st == 0)
    if (st === 0) {
        puch.forEach(p => {
            const fuel = p.fuelName || p.fuel;
            if (!fuelMap[fuel]) fuelMap[fuel] = {
                openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
                transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
                usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
            };
            fuelMap[fuel].purchasesQty += Number(p.qty);
            fuelMap[fuel].purchasesCost += Number(p.cost) * Number(p.qty);
        });
    }

    // Received (when st != 0)
    if (st !== 0) {
        recv.forEach(r => {
            const fuel = r.fuelName || r.fuel;
            if (!fuelMap[fuel]) fuelMap[fuel] = {
                openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
                transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
                usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
            };
            fuelMap[fuel].receivedQty += Number(r.qty);
            fuelMap[fuel].receivedCost += Number(r.cost) * Number(r.qty);
        });
        trf.forEach(t => {
            const fuel = t.fuelName || t.fuel;
            if (!fuelMap[fuel]) fuelMap[fuel] = {
                openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
                transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
                usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
            };
            fuelMap[fuel].transferredQty += Number(t.qty);
            fuelMap[fuel].transferredCost += Number(t.cost) * Number(t.qty);
        });
    }

    // Wastage
    adj.forEach(a => {
        const fuel = a.fuelName || a.fuel;
        if (!fuelMap[fuel]) fuelMap[fuel] = {
            openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
            transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
            usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
        };
        fuelMap[fuel].wastageQty += Number(a.diff);
        fuelMap[fuel].wastageCost += Number(a.diff) * Number(a.cost);
    });

    // Sales
    saL.forEach(s => {
        const fuel = s.fuelName || s.fuel;
        if (!fuelMap[fuel]) fuelMap[fuel] = {
            openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
            transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
            usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
        };
        fuelMap[fuel].salesQty += Number(s.qty_sold);
        fuelMap[fuel].salesCost += Number(s.qty_sold) * Number(s.cost_sold);
    });

    // Fuel usage (expenses with fuel_qty > 0)
    expx.filter(e => Number(e.fuel_qty) > 0).forEach(e => {
        const fuel = e.fuelName || e.fuel;
        if (!fuelMap[fuel]) fuelMap[fuel] = {
            openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
            transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
            usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
        };
        fuelMap[fuel].usageQty += Number(e.fuel_qty);
        fuelMap[fuel].usageCost += Number(e.fuel_qty) * Number(e.fuel_cost);
    });

    // Assign background colors for each column group
    const bgColors = {
        opening: 'background-color:rgba(0,123,255,0.08);',      // blue-ish
        purchases: 'background-color:rgba(40,167,69,0.08);',    // green-ish
        received: 'background-color:rgba(255,193,7,0.08);',     // yellow-ish
        transferred: 'background-color:rgba(23,162,184,0.08);', // cyan-ish
        wastage: 'background-color:rgba(220,53,69,0.08);',      // red-ish
        sales: 'background-color:rgba(108,117,125,0.08);',      // gray-ish
        usage: 'background-color:rgba(255,87,34,0.08);',        // orange-ish
        closing: 'background-color:rgba(40,167,69,0.08);'       // green-ish (darker)
    };
    // Build table
    let fuelRows = '';
    Object.keys(fuelMap).forEach(fuel => {
        const f = fuelMap[fuel];
        fuelRows += `
            <tr>
            <td class="text-capitalize">${fuel}</td>
            <td style="${bgColors.opening}">${Number(f.openingQty).toLocaleString()}</td>
            <td style="${bgColors.opening}">${f.openingQty ? Number((f.openingCost / f.openingQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.opening}">${Number(f.openingCost).toLocaleString()}</td>
     
        
            <td style="${bgColors.received}">${Number(f.receivedQty).toLocaleString()}</td>
            <td style="${bgColors.received}">${f.receivedQty ? Number((f.receivedCost / f.receivedQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.received}">${Number(f.receivedCost).toLocaleString()}</td>


            ${st !=0 ? `

                <td style="${bgColors.transferred}">${Number(f.transferredQty).toLocaleString()}</td>
                <td style="${bgColors.transferred}">${f.transferredQty ? Number((f.transferredCost / f.transferredQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td style="${bgColors.transferred}">${Number(f.transferredCost).toLocaleString()}</td>
            ` : `  `}

            
            <td style="${bgColors.wastage}">${Number(f.wastageQty).toLocaleString()}</td>
            <td style="${bgColors.wastage}">${f.wastageQty ? Number((f.wastageCost / f.wastageQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.wastage}">${Number(f.wastageCost).toLocaleString()}</td>
            <td style="${bgColors.sales}">${Number(f.salesQty).toLocaleString()}</td>
            <td style="${bgColors.sales}">${f.salesQty ? Number((f.salesCost / f.salesQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.sales}">${Number(f.salesCost).toLocaleString()}</td>
            <td style="${bgColors.usage}">${Number(f.usageQty).toLocaleString()}</td>
            <td style="${bgColors.usage}">${f.usageQty ? Number((f.usageCost / f.usageQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.usage}">${Number(f.usageCost).toLocaleString()}</td>
            <td style="${bgColors.closing}">${Number(f.closingQty).toLocaleString()}</td>
            <td style="${bgColors.closing}">${f.closingQty ? Number((f.closingCost / f.closingQty).toFixed(2)).toLocaleString() : '-'}</td>
            <td style="${bgColors.closing}">${Number(f.closingCost).toLocaleString()}</td>
            </tr>
        `;
    });

    if (Object.keys(fuelMap).length > 0) {
        let total = {
            openingQty: 0, openingCost: 0, purchasesQty: 0, purchasesCost: 0, receivedQty: 0, receivedCost: 0,
            transferredQty: 0, transferredCost: 0, wastageQty: 0, wastageCost: 0, salesQty: 0, salesCost: 0,
            usageQty: 0, usageCost: 0, closingQty: 0, closingCost: 0
        };
        Object.values(fuelMap).forEach(f => {
            total.openingQty += f.openingQty;
            total.openingCost += f.openingCost;
            total.purchasesQty += f.purchasesQty;
            total.purchasesCost += f.purchasesCost;
            total.receivedQty += f.receivedQty;
            total.receivedCost += f.receivedCost;
            total.transferredQty += f.transferredQty;
            total.transferredCost += f.transferredCost;
            total.wastageQty += f.wastageQty;
            total.wastageCost += f.wastageCost;
            total.salesQty += f.salesQty;
            total.salesCost += f.salesCost;
            total.usageQty += f.usageQty;
            total.usageCost += f.usageCost;
            total.closingQty += f.closingQty;
            total.closingCost += f.closingCost;
        });
        fuelRows += `
            <tr class="table-secondary font-weight-bold">
                <td>${lang('Jumla','Total')}</td>
                <td>${Number(total.openingQty).toLocaleString()}</td>
                <td>${total.openingQty ? Number((total.openingCost / total.openingQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.openingCost).toLocaleString()}</td>
            
            
                <td>${Number(total.receivedQty).toLocaleString()}</td>
                <td>${total.receivedQty ? Number((total.receivedCost / total.receivedQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.receivedCost).toLocaleString()}</td>    

                ${st !=0 ? `


                    <td>${Number(total.transferredQty).toLocaleString()}</td>
                    <td>${total.transferredQty ? Number((total.transferredCost / total.transferredQty).toFixed(2)).toLocaleString() : '-'}</td>
                    <td>${Number(total.transferredCost).toLocaleString()}</td>
                ` : ` `}

                <td>${Number(total.wastageQty).toLocaleString()}</td>
                <td>${total.wastageQty ? Number((total.wastageCost / total.wastageQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.wastageCost).toLocaleString()}</td>
                <td>${Number(total.salesQty).toLocaleString()}</td>
                <td>${total.salesQty ? Number((total.salesCost / total.salesQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.salesCost).toLocaleString()}</td>
                <td>${Number(total.usageQty).toLocaleString()}</td>
                <td>${total.usageQty ? Number((total.usageCost / total.usageQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.usageCost).toLocaleString()}</td>
                <td>${Number(total.closingQty).toLocaleString()}</td>
                <td>${total.closingQty ? Number((total.closingCost / total.closingQty).toFixed(2)).toLocaleString() : '-'}</td>
                <td>${Number(total.closingCost).toLocaleString()}</td>
            </tr>
        `;
    }

    let fuelTable = `
        <table class="table table-bordered table-sm smallFont">
            <thead>
                <tr class="table-primary">
                    <th rowspan="2">${lang('Aina ya Mafuta','Fuel Name')}</th>
                    <th colspan="3">${lang('Stock ya Mwanzo','Opening Stock')}</th>
                   
                    <th colspan="3">${lang('Kupokelewa','Received')}</th>

                    ${st !=0 ? `
                        <th colspan="3">${lang('Uhamisho','Transferred')}</th>
                    ` : `  `}
                   
                    <th colspan="3">${lang('Upotevu','Wastage')}</th>
                    <th colspan="3">${lang('Mauzo','Sales')}</th>
                    <th colspan="3">${lang('Matumizi','Fuel Usage')}</th>
                    <th colspan="3">${lang('Stock ya Mwisho','Closing Stock')}</th>
                </tr>
                <tr class="table-primary">
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
               ${st != 0 ? `
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                ` : `  `}

                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                  
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                    <th>${lang('Qty','Qty (LTRS)')}</th>
                    <th>${lang('Cost/LTR','Cost/LTR')}</th>
                    <th>${lang('Total','Total Cost')} ${fedha}</th>
                </tr>
            </thead>
            <tbody>
                ${fuelRows}
            </tbody>
        </table>
    `;
    $('#MoreDetailsRHeading span').html(title);

    $('#MoreDetailsTable').html(fuelTable);
}


// SWITCH BUTTONS....................//
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


$('#backBtn').click(function(){
   
              $('#MoreDetails').fadeOut();
              $('#Salecateg').fadeIn(100)

})


