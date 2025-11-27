let saData = [],FUEL = [], VDATA = {},ISVIEW = 0,SAOBJ=[],VOBJ={}
const filters = () =>{
    const  st = Number($('#staxnF').val()),
         
         
           today = {rname:lang('Leo','Today'),tFr:moment(moment().startOf('day')).format(),tTo:moment().format()},
           week = {rname:lang('Wiki hii','This Week'),tFr:moment(moment().startOf('isoWeek')).format(),tTo:moment().format()},
           month = {rname:lang('Mwezi huu','This Month'),tFr:moment(moment().startOf('month')).format(),tTo:moment().format()},
           isChart = Number($('#riportChatRist button.btn-secondary').data('r')),
           chartT = $('#riportSwitch .btn-primary').data('chart')
           return {st,today,week,month,isChart,chartT}
}


const getRData = d =>{
    $('#loadMe').modal('show')
    const {tFr,tTo,rname,init} = d,
          url = '/analytics/getExpenses' ,
          tdy = Number(moment(tTo).format('DD')),
          tmFr = tdy>=7||!init?tFr:moment(moment().subtract(7,'days')).format(),
          data = {data:{tFr:tmFr,tTo},url},
          
          
          sendIt = POSTREQUEST(data)
         
          sendIt.then(resp=>{
              $('#loadMe').modal('hide')
              hideLoading()
            //   console.log(resp);
                if(!resp.success){
                    toastr.error(lang('Tatizo limetokea jaribu tena','An error occurred please try again'), lang('Taarifa','info '), {timeOut: 2000})
                    return
                }
              
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

        let  exp = st?r.expenses?.filter(sa=>sa.st===st):r.expenses
                
        const     expxA = exp.filter(e=>Number(e.fuel_qty)===0),
                   expf = exp.filter(e=>Number(e.fuel_qty)>0)



 
                //  Sale Type filter (Customer or Pump Attendants)
            //  console.log({exp,expxA,expf});


                

            const  expAmo = Number(expxA?.reduce((a,b)=>a+Number(b.kiasi),0))||0,
                   fuelAmo = Number(expf?.reduce((a,b)=>a+Number(b.kiasi),0))||0,
                   totAmo = expAmo + fuelAmo,
                   
                    
  
                    check = Number($(`#MonthSale${r.id}`).prop('checked')),
                    show = check == 1 || check == 0 ?check:1,
    

                    hide = !init && !show

                 

        tr+=`<tr class="${r.id>3?'table-info':''}"  ${hide?'style="display:none"':''}   id="dataRow${r.id}" >
            <td> <a type="button" data-val=${r.id} class="bluePrint viewDetails" >${r.rname} </a> </td>
            <td>${Number(exp.length).toLocaleString()}  </td>
            <td>${Number(fuelAmo).toLocaleString()}  </td>
            <td>${Number(expAmo).toLocaleString()}  </td>
            <td>${Number(totAmo).toLocaleString()}  </td>
      
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
                    {st} = filters(),
                     expx = d.expenses?.filter(s=>moment(s.tarehe).format() >= tFr && moment(s.tarehe).format() <= tTo ),
                   
                    
                 
                    
            thedt = {
                id:saData.length + 1,
                rname,
                tFr,
                tTo,
                st,
                expenses: expx
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
                     const {expenses} = saDt[0],

                     dt = {expenses,tFr,tTo,rname}
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
        
          

         $('#summaryRiport').fadeOut();
        
         $('.riportOn').removeClass('btn-primary')
         $('#RBydate').addClass('btn-primary')

         detailReport()


        //  $('.DetailsTable').hide()
        

        //  $('#MoreDetails').hide()
        //  $('#Salecateg').show()

        // $('#detailReport').fadeIn(200)


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
     head = `${lang('Mchanganuo wa matumizi','Expense Report')} <span class="bluePrint"> ${Rdate} </span> ${isToday}`
   
    // let  sale = st?r.sale?.filter(sa=>sa.shell===st):r.sale,
    //      saL = st?r.saL?.filter(sa=>sa.shell===st):r.saL,
    //      pay =st?r.pay?.filter(sa=>sa.st===st):r.pay
    //      payRec =st?r.payRec?.filter(sa=>sa.st===st):r.payRec

 
       
        $('#detailRHeading').html(head)
        
   

        $('#riportChatRist .btn-secondary').addClass('btn-light').removeClass('btn-secondary')
        $('#riportChatRist button').first().addClass('btn-secondary').removeClass('btn-light')
        
       $('.DetailsTable').hide()
       $('#EvaluateByDate').fadeIn(100)
        $('#MoreDetails').fadeOut(100)
        $('#Salecateg').fadeIn(100)
        $('#detailReport').fadeIn(200)

        daterExpenses()
        byCategory()
        byStation()



}


// Create the daterExpenses  function that create the table and arrage the expenses with date
const daterExpenses = () =>{

    //  create the table from expenses array over date or month or year depending on the difference of tFr and tTo if exceed 31 days then month if exceed 365 then year

        const {tFr,tTo,expenses} = VDATA,
                from = moment(tFr),
                {st} = filters(),
                to = moment(tTo),
                diffDays = to.diff(from, 'days'),
                diffMonths = to.diff(from, 'months'),
                diffYears = to.diff(from, 'years');

                let groupBy = 'date',title=lang('Matumizi kwa siku','Expenses by Date')
                if(diffDays>31){
                    groupBy = 'month'
                    title=lang('Matumizi kwa miezi','Expenses by Month')
                }else if(diffYears>1){
                    groupBy = 'year'
                    title=lang('Matumizi kwa miaka','Expenses by Year')
                }

        $('#EvaluateByDate h6').html(title)
        // group the expenses by date or month or year
        let filteredExpenses = expenses;
        if (st) {
            filteredExpenses = expenses.filter(e => e.st === st);
        }
        const groupedExpenses = filteredExpenses;
        
        const grouped = groupedExpenses.reduce((acc, expense) => {
            let key = ''
            if(groupBy==='date'){
                key = moment(expense.tarehe).format('YYYY-MM-DD')
            }else if(groupBy==='month'){
                key = moment(expense.tarehe).format('YYYY-MM')
            }else if(groupBy==='year'){
                key = moment(expense.tarehe).format('YYYY')
            }
            if(!acc[key]) acc[key] = []
            acc[key].push(expense)
            return acc
        }, {})
   
        // create the table rows
        let tr = ''
        // Get keys and sort them in descending order (higher date at top)
        const sortedKeys = Object.keys(grouped).sort((a, b) => moment(b).valueOf() - moment(a).valueOf());
        const theData = []
        for(const key of sortedKeys){       
            const exp = grouped[key],
              expAmo = Number(exp.filter(e=>!Number(e.fuel_qty)).reduce((a,b)=>a+Number(b.kiasi),0))||0,
              fuelAmo = Number(exp.filter(e=>Number(e.fuel_qty)>0).reduce((a,b)=>a+Number(b.kiasi),0))||0,
              totAmo = expAmo + fuelAmo,
              date = groupBy==='date'?moment(key).format('DD/MM/YYYY'):groupBy==='month'?moment(key).format('MMMM YYYY'):moment(key).format('YYYY')  
            tr+=`<tr>
            <td>
                <a type="button" data-val="${key}" class="bluePrint viewDateDetails" title="${lang('Onesha zaidi','More Info')}">${date}</a>
            </td>
            <td>${Number(exp.length).toLocaleString()}</td>
            <td>${Number(expAmo.toFixed(2)).toLocaleString()}</td>
            <td>${Number(fuelAmo.toFixed(2)).toLocaleString()}</td>
            <td>${Number(totAmo.toFixed(2)).toLocaleString()}</td>
            </tr>`

            theData.push({
                
                name:date,
                expAmo,
                fuelAmo,

            })
        }
        // push the data to SAOBJ for charting
        SAOBJ=SAOBJ.filter(n=>n.name!='dt')
        SAOBJ.push({name:'dt',data:theData,title})
        // add the total row below
        const totalExp = Number(groupedExpenses.reduce((a,b)=>a+Number(b.kiasi),0))||0
        tr+=`<tr class="table-info weight600">
            <td>${lang('Jumla','Total')}</td>
            <td>${Number(groupedExpenses.length).toLocaleString()}</td>
            <td>${Number(groupedExpenses.filter(e=>!Number(e.fuel_qty)).reduce((a,b)=>a+Number(b.kiasi),0)).toLocaleString()}</td>
            <td>${Number(groupedExpenses.filter(e=>Number(e.fuel_qty)>0).reduce((a,b)=>a+Number(b.kiasi),0)).toLocaleString()}</td>
            <td>${Number(totalExp.toFixed(2)).toLocaleString()}</td>
        </tr>`  

        const table = `<table class="table table-bordered table-sm" >
                        <thead>
                            <tr class="smallFont">
                                <th>${lang('Tarehe','Date')}</th>
                                <th>${lang('Idadi ya Matumizi','No. of Expenses')}</th>
                                <th>${lang('Matumizi yasiyo ya mafuta','Non Fuel Expenses')}${fedha}</th>
                                <th>${lang('Matumizi ya mafuta','Fuel Expenses')}${fedha}</th>
                                <th>${lang('Jumla ya Matumizi','Total Expenses')}${fedha}</th>
                            </tr>
                            </thead>
                            <tbody>
                            ${tr}
                            </tbody>
                        </table>
                            `


        $('#EvaluateByDateTable').html(table)

        
    }   

// Expenses by category
const byCategory = () =>{
     
    const {expenses} = VDATA,
          {st} = filters(),
            filteredExpenses = st?expenses.filter(e=>e.st===st):expenses,
          categories = [...new Set(filteredExpenses.map(exp=>exp.expN))]

        // console.log({categories,expenses});

            let tr = '',theData = []
            categories.forEach(cat=>{
                const exp = filteredExpenses.filter(e=>e.expN===cat),
                      expAmo = Number(exp.filter(e=>!Number(e.fuel_qty)).reduce((a,b)=>a+Number(b.kiasi),0))||0,
                        fuelAmo = Number(exp.filter(e=>Number(e.fuel_qty)>0).reduce((a,b)=>a+Number(b.kiasi),0))||0,
                        totAmo = expAmo + fuelAmo,
                        
                        catId = exp[0]?.expId||0
                        tr+=`<tr>
                            <td>${categories.indexOf(cat) + 1}</td>
                            <td><a type="button" data-val=${catId} class="bluePrint viewCategoryDetails" >${cat} </a></td>
                            
                            <td>${Number(exp.length).toLocaleString()}</td>
                       
                            <td>${Number(totAmo.toFixed(2)).toLocaleString()}</td>
                        </tr>`
                        theData.push({name:cat,amount:totAmo})

            })

          SAOBJ = SAOBJ.filter(n => n.name != 'exp');
          SAOBJ.push({name:'exp',data:theData,title:lang('Matumizi kwa aina','Expenses by Category')});

            // add the total row below
            const totalExp = Number(filteredExpenses.reduce((a,b)=>a+Number(b.kiasi),0))||0
            tr+=`<tr class="table-info weight600">
                <td >${lang('Jumla','Total')}</td>
                <td></td>
                <td>${Number(filteredExpenses.length).toLocaleString()}</td>
                <td>${Number(totalExp.toFixed(2)).toLocaleString()}</td>
            </tr>`
            
            const table = `<table class="table table-bordered table-sm" >
                        <thead>
                            <tr class="smallFont">
                                <th>#</th>
                                <th>${lang('Aina ya Matumizi','Expense Category')}</th>
                                <th>${lang('Idadi ya Matumizi','No. of Expenses')}</th>
                                <th>${lang('Jumla ya Matumizi','Total Expenses')}${fedha}</th>
                            </tr>
                            </thead>
                            <tbody>
                            ${tr}
                            </tbody>
                        </table>
                            `


            $('#EvaluateByCategoryTable').html(table)
           

            setDataTable('#EvaluateByCategoryTable')


      
            window.SAOBJ = SAOBJ
            VOBJ = {data:SAOBJ[0]?.data,title:SAOBJ[0]?.title}
            // createChart()

}


// Expenses by Station
const byStation = () =>{
       
    const {expenses} = VDATA,
    
          stations = [...new Set(expenses.map(exp=>exp.stationName))]   
          
            let tr = '',theData = []
            stations.forEach(st=>{
                const exp = expenses.filter(e=>e.stationName===st),
                      expAmo = Number(exp.filter(e=>!Number(e.fuel_qty)).reduce((a,b)=>a+Number(b.kiasi),0))||0,
                        fuelAmo = Number(exp.filter(e=>Number(e.fuel_qty)>0).reduce((a,b)=>a+Number(b.kiasi),0))||0,
                        totAmo = expAmo + fuelAmo
                        tr+=`<tr>
                            <td>${stations.indexOf(st) + 1}</td>
                            <td><a type="button" data-val=${exp[0].st} class="bluePrint viewStationDetails" >${st} </a></td>
                            <td>${Number(exp.length).toLocaleString()}</td>
                            <td>${Number(fuelAmo.toFixed(2)).toLocaleString()}</td>
                            <td>${Number(expAmo.toFixed(2)).toLocaleString()}</td>
                            <td>${Number(totAmo.toFixed(2)).toLocaleString()}</td>
                        </tr>`

                        theData.push({
                            name:st,
                            expAmo,
                            fuelAmo,
                        })
            })

            SAOBJ =  SAOBJ.filter(n=>n.name!='st')
            SAOBJ.push({name:'st',data:theData,title:lang('Matumizi kwa kituo','Expenses by Station')})

            // add the total row below
            const totalExp = Number(expenses.reduce((a,b)=>a+Number(b.kiasi),0))||0
            tr+=`<tr class="table-info weight600">
                <td>${lang('Jumla','Total')}</td>
                <td></td>
                <td>${Number(expenses.length).toLocaleString()}</td>
                <td>${Number(expenses.filter(e=>Number(e.fuel_qty)>0).reduce((a,b)=>a+Number(b.kiasi),0)).toLocaleString()}</td>
                <td>${Number((totalExp - (expenses.filter(e=>Number(e.fuel_qty)>0).reduce((a,b)=>a+Number(b.kiasi),0))).toFixed(2)).toLocaleString()}</td>
                <td>${Number(totalExp.toFixed(2)).toLocaleString()}</td>
            </tr>`

            const table = `<table class="table table-bordered table-sm" >
                        <thead>
                            <tr class="smallFont">
                                <th>#</th>
                                <th>${lang('Kituo','Station')}</th>
                                <th>${lang('Idadi ya Matumizi','No. of Expenses')}</th>
                                <th>${lang('Matumizi ya mafuta','Fuel Expenses')} ${fedha}</th>
                                <th>${lang('Matumizi yasiyo ya mafuta','Non Fuel Expenses')} ${fedha}</th>
                                <th>${lang('Jumla ya Matumizi','Total Expenses')} ${fedha}</th>
                            </tr>
                            </thead>
                            <tbody>
                            ${tr}
                            </tbody>
                        </table>
                            `

            $('#EvaluateByStationTable').html(table)
            setDataTable('#EvaluateByStationTable')
}


// Function to set dataTable for category and station tables
const setDataTable = tableId => {
    $(`${tableId} table`).DataTable({
        "footerCallback": function () {},
        "rowCallback": function(row, data, index){
            // Add a class to the last row
            if ($(row).hasClass('weight600')) {
                $(row).addClass('no-search no-sort');
            }
        },
        "columnDefs": [
            {
                "targets": "_all",
                "orderable": true,
                "searchable": true
            }
        ]
    });
    // Exclude rows with .no-search and .no-sort from search and sort
    $.fn.dataTable.ext.search.push(function(settings, data, dataIndex, rowData, counter){
        var $row = $(settings.nTBody).find('tr').eq(dataIndex);
        return !$row.hasClass('no-search');
    });
    $(`${tableId} table`).on('order.dt search.dt', function () {
        $(`${tableId} table tbody tr.no-sort`).each(function(){
            $(this).detach().appendTo($(`${tableId} table tbody`));
        });
    });
    // Always keep the last row (total) at the bottom after sorting/searching
    $(`${tableId} table`).on('draw.dt', function () {
        var $tbody = $(`${tableId} table tbody`);
        var $totalRow = $tbody.find('tr.weight600');
        if ($totalRow.length) {
            $totalRow.detach().appendTo($tbody);
        }
    });

   
}   


//add the function to view expenses details by either date, category or station depending on the button clicked
$('body').on('click','.viewDateDetails',function(){
    const date = $(this).data('val'),
          exp = VDATA.expenses?.filter(e=>moment(e.tarehe).format('YYYY-MM-DD')===date)
            title = `${lang('Matumizi kwa siku','Expenses by Date')} <span class="bluePrint">${moment(date).format('DD/MM/YYYY')}</span>`
            VOBJ = {data:exp,title}
            moreDetails()
        }
)

$('body').on('click','.viewCategoryDetails',function(){
    const catId = $(this).data('val'),
          exp = VDATA.expenses?.filter(e=>e.expId===catId)
            title = `${lang('Matumizi kwa aina','Expenses by Category')} <span class="bluePrint">${exp[0]?.expN||''}</span>`
            VOBJ = {data:exp,title}
            moreDetails()
        }
)

// add one more for station
$('body').on('click','.viewStationDetails',function(){
    const station = $(this).data('val'),
            exp = VDATA.expenses?.filter(e=>e.st===station)
            title = `${lang('Matumizi kwa kituo','Expenses by Station')} <span class="bluePrint">${station} </span>`
            VOBJ = {data:exp,title}
            
            moreDetails()
        }
)


// create the chart
const createChart = () =>{

    const {isChart,chartT} = filters()
   
    if(!isChart)return

    const theObj = SAOBJ.find(n=>n.name===chartT)
    if(!theObj)return



    $('#Salecateg').hide()
    $('#MoreDetails').show()
    $('#MoredetailRHeading a').prop('hidden',1)
    $('#MoredetailRHeading span').html(theObj.title)




    VOBJ = {data:theObj?.data,title:theObj?.title}

    let data;
    if (chartT === 'exp') {
        // Expenses by category: single bar chart
        data = {
            labels: theObj.data.map(d => d.name),
            datasets: [
                {
                    label: lang('Jumla ya Matumizi', 'Total Expenses'),
                    data: theObj.data.map(d => Number(d.amount || 0).toFixed(2)),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }
            ]
        };
    } else {
        // Expenses by date or station: fuel/non-fuel split
        data = {
            labels: theObj.data.map(d => d.name),
            datasets: [
                {
                    label: lang('Matumizi yasiyo ya mafuta', 'Non Fuel Expenses'),
                    data: theObj.data.map(d => Number(d.expAmo || 0).toFixed(2)),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: lang('Matumizi ya mafuta', 'Fuel Expenses'),
                    data: theObj.data.map(d => Number(d.fuelAmo || 0).toFixed(2)),
                    backgroundColor: 'rgba(255, 99, 132, 0.6)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }
            ]
        };
    }
    const config = {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                },

            }
        }
    };

    if (chartT === 'st' || chartT === 'dt') {
        config.type = 'line';
    } else if (chartT === 'exp') {
        config.type = 'bar';
    }    

    // now draw the chart in the canvas with id chartRiport
    $('#MoredetailRContent').html('<canvas id="chartRiport"></canvas>')
    const myChart = new Chart(
        document.getElementById('chartRiport'),
        config
    );


}


const moreDetails = () =>{
    $('#Salecateg').fadeOut(100)
    $('#MoreDetails').fadeIn(100)
    $('#MoredetailRHeading span').html(VOBJ.title)
   
    //  create the table to display all the expenses in the VOBJ.data
    const {data} = VOBJ,
        {st} = filters()
        let filteredData = data;
        if (st) {
            filteredData = data.filter(e => e.st === st);
        }
    // console.log(filteredData);
    let tr = '' 
    filteredData.reverse().forEach((d,i)=>{
        tr+=`<tr>
            <td>${i + 1}</td>
           
            ${!st?`<td>${d.stationName}</td>`:''}
            <td>${d.expN}</td>
            <td>${d.maelezo}</td>
            <td>${d.givenTo}</td>
            <td>${d.byFName} ${d.byLname}</td>
            <td>${Number(d.kiasi).toLocaleString()}</td>
        </tr>`
    })

    // add the total row below
    const totalExp = Number(filteredData.reduce((a,b)=>a+Number(b.kiasi),0))||0
    tr+=`<tr class="table-info weight600">
        <td colspan="${st?5:6}">${lang('Jumla','Total')}</td>
        <td>${Number(totalExp.toFixed(2)).toLocaleString()}</td>
    </tr>`
    const table = `<table class="table table-bordered table-sm" >
                    <thead>
                        <tr class="smallFont">
                            <th>#</th>
                          
                            ${!st?`<th>${lang('Kituo','Station')}</th>`:''}
                            <th>${lang('Matumizi','Expense')}</th>
                            <th>${lang('Maelezo','Description')}</th>
                            <th>${lang('Aliyekabidhiwa','Recipient')}</th>
                            <th>${lang('Aliyerekodi','Recorded By')}</th>
                            <th>${lang('Kiasi','Amount')} ${fedha}</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tr}
                    </tbody>
                </table>`
    $('#MoredetailRContent').html(table)
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


// Change this to be resposive for js generated buttons
$('body').on('click','.riportListChatOn, .chartType',function(){

    $('.riportListChatOn').removeClass('btn-secondary')
    $('.riportListChatOn').addClass('btn-light')
    $(this).removeClass('btn-light')
    $(this).addClass('btn-secondary') 

    createChart()
 

        

})