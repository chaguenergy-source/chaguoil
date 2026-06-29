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

                 

        tr+=`<tr class="${r.id>3?'table-info':''} cursor-pointer viewDetails" data-val=${r.id}  ${hide?'style="display:none"':''}   id="dataRow${r.id}" >
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
                expenses: expx,
                attachments: (d.attachments || []).filter(a => expx.some(e => e.id === a.rekodiMatumizi))
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
                     const {expenses, attachments} = saDt[0],

                     dt = {expenses, attachments, tFr,tTo,rname}
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
        byStaff()
        byTaxGroup()



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
            tr+=`<tr data-val="${key}" class="cursor-pointer viewDateDetails">
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

const escapeExpHtml = text => {
    if(text === null || text === undefined) return '';
    return String(text).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
}

const getAttachmentsForExpenses = expList => {
    const expIds = new Set((expList || []).map(e => e.id));
    return (VDATA.attachments || []).filter(a => expIds.has(a.rekodiMatumizi));
}

const receiptStats = items => {
    const amount = (items || []).reduce((s, a) => s + Number(a.kiasi || 0), 0);
    return { count: (items || []).length, amount, items: items || [] };
}

const getAttachmentsForCategory = (catId, isSalary) => {
    const {st} = filters();
    let expenses = VDATA.expenses || [];
    if(st) expenses = expenses.filter(e => e.st === st);
    const catExpenses = isSalary
        ? expenses.filter(e => e.salary)
        : expenses.filter(e => e.expId === catId);
    return getAttachmentsForExpenses(catExpenses);
}

const getAttachmentsForTaxGroup = (taxId, taxName) => {
    const {st} = filters();
    let expenses = VDATA.expenses || [];
    if(st) expenses = expenses.filter(e => e.st === st);
    const taxExpenses = taxId
        ? expenses.filter(e => Number(e.tax || 0) === Number(taxId))
        : expenses.filter(e => !Number(e.tax || 0) && (e.taxGroup || lang('Tax Group Haijabainishwa', 'Unspecified Tax Group')) === taxName);
    return getAttachmentsForExpenses(taxExpenses);
}

const buildExpReceiptBtn = (stats, btnData) => {
    if(!stats.count){
        return `<span class="text-muted small">—</span>`;
    }
    const attrs = Object.entries(btnData).map(([k, v]) => `data-${k}="${escapeExpHtml(v)}"`).join(' ');
    return `<button type="button" class="btn btn-outline-success btn-sm py-0 px-2 exp-receipts-btn" ${attrs}>
        ${stats.count} ${lang('risiti','receipts')} · ${Number(stats.amount.toFixed(2)).toLocaleString()} ${fedha}
    </button>`;
}

let expReceiptsData = [];
let expReceiptLayout = 1;

const buildExpReceiptItemHtml = att => {
    const title = att.attach_name || att.expN || lang('Risiti','Receipt');
    const meta = `${escapeExpHtml(att.expN || title)} · ${moment(att.date).format('DD/MM/YYYY HH:mm')} · ${Number(att.kiasi || 0).toLocaleString()} ${fedha}`;
    return `
      <div class="exp-att-item">
        <div class="exp-att-meta">
          <span class="badge badge-success mr-1">${lang('Risiti','Receipt')}</span>
          ${meta}
        </div>
        <img src="${escapeExpHtml(att.file)}" alt="${escapeExpHtml(title)}" loading="lazy">
      </div>
    `;
}

const renderExpReceiptsGallery = () => {
    const gallery = document.getElementById('expReceiptsGallery');
    const emptyEl = document.getElementById('expReceiptsEmpty');
    if(!gallery) return;

    gallery.className = `exp-att-gallery layout-${expReceiptLayout}`;

    if(!expReceiptsData.length){
        gallery.innerHTML = '';
        if(emptyEl) emptyEl.style.display = 'block';
        return;
    }

    if(emptyEl) emptyEl.style.display = 'none';

    const perPage = Number(expReceiptLayout) || 1;
    let html = '';
    for(let i = 0; i < expReceiptsData.length; i += perPage){
        const pageItems = expReceiptsData.slice(i, i + perPage);
        html += `<div class="exp-att-page">${pageItems.map(buildExpReceiptItemHtml).join('')}</div>`;
    }
    gallery.innerHTML = html;
}

const buildExpReceiptsPrintHtml = () => {
    const perPage = Number(expReceiptLayout) || 1;
    const modalTitle = $('#expReceiptsModalTitle').text() || lang('Risiti za Matumizi','Expense Receipts');
    const totalAmount = expReceiptsData.reduce((s, a) => s + Number(a.kiasi || 0), 0);
    const heading = `<h4 class="text-center mb-2">${escapeExpHtml(modalTitle)}</h4>
      <p class="text-center small mb-3">${expReceiptsData.length} ${lang('risiti','receipts')} · ${Number(totalAmount.toFixed(2)).toLocaleString()} ${fedha} · ${expReceiptLayout}/${lang('ukurasa','page')}</p>`;

    let pagesHtml = '';
    for(let i = 0; i < expReceiptsData.length; i += perPage){
        const pageItems = expReceiptsData.slice(i, i + perPage);
        pagesHtml += `<div class="print-page layout-${expReceiptLayout}">${pageItems.map(att => `
          <div class="print-item">
            <div class="print-meta">${escapeExpHtml(att.expN || att.attach_name || '')} · ${moment(att.date).format('DD/MM/YYYY HH:mm')} · ${Number(att.kiasi || 0).toLocaleString()} ${fedha}</div>
            <img src="${escapeExpHtml(att.file)}" alt="">
          </div>
        `).join('')}</div>`;
    }

    return `
      <style>
        @page { size: A4; margin: 8mm; }
        body { margin: 0; padding: 0; color: #000; font-family: Arial, sans-serif; }
        .print-page { page-break-after: always; box-sizing: border-box; }
        .print-page:last-child { page-break-after: auto; }
        .print-item { box-sizing: border-box; overflow: hidden; }
        .print-meta { font-size: 11px; margin-bottom: 4px; font-weight: 600; }
        .print-item img { width: 100%; object-fit: contain; display: block; background: #fff; }
        .layout-1.print-page { min-height: 277mm; display: flex; flex-direction: column; justify-content: center; }
        .layout-1 .print-item img { max-height: 255mm; }
        .layout-2.print-page { min-height: 277mm; display: grid; grid-template-rows: 1fr 1fr; gap: 6mm; }
        .layout-2 .print-item img { max-height: 125mm; }
        .layout-4.print-page { min-height: 277mm; display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 4mm; }
        .layout-4 .print-item img { max-height: 120mm; }
      </style>
      ${heading}${pagesHtml}
    `;
}

const openExpReceiptsModal = (items, title) => {
    expReceiptsData = items || [];
    expReceiptLayout = 1;
    $('.exp-att-layout').removeClass('btn-secondary active').addClass('btn-outline-secondary');
    $('.exp-att-layout[data-layout="1"]').addClass('active btn-secondary').removeClass('btn-outline-secondary');
    $('#expReceiptsModalTitle').text(title || lang('Risiti za Matumizi','Expense Receipts'));
    const totalAmount = expReceiptsData.reduce((s, a) => s + Number(a.kiasi || 0), 0);
    $('#expReceiptsModalSummary').html(
        `${expReceiptsData.length} ${lang('risiti','receipts')} · ${Number(totalAmount.toFixed(2)).toLocaleString()} ${fedha}`
    );
    renderExpReceiptsGallery();
    $('#expReceiptsModal').modal('show');
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
                        
                        catId = exp[0]?.expId||0,
                        isSalary = exp[0]?.salary ? 1 : 0,
                        receiptInfo = receiptStats(getAttachmentsForCategory(catId, isSalary))
                        tr+=`<tr data-val=${catId} data-salary=${isSalary} class="cursor-pointer viewCategoryDetails">
                            <td>${categories.indexOf(cat) + 1}</td>
                            <td><a type="button" data-val=${catId} data-salary=${isSalary} class="bluePrint viewCategoryDetails" >${cat||lang('Mshahara','Salary')} ${exp[0]?.salary_advance?`(${lang('Malipo ya awali ya mshahara','Salary Advance')})`:''} </a></td>
                            
                            <td>${Number(exp.length).toLocaleString()}</td>
                       
                            <td>${Number(totAmo.toFixed(2)).toLocaleString()}</td>
                            <td>${buildExpReceiptBtn(receiptInfo, {
                                'filter-type': 'category',
                                'cat-id': catId,
                                salary: isSalary,
                                title: cat || lang('Mshahara','Salary')
                            })}</td>
                        </tr>`
                        theData.push({name:cat,amount:totAmo})

            })

          SAOBJ = SAOBJ.filter(n => n.name != 'exp');
          SAOBJ.push({name:'exp',data:theData,title:lang('Matumizi kwa aina','Expenses by Category')});

            // add the total row below
            const totalExp = Number(filteredExpenses.reduce((a,b)=>a+Number(b.kiasi),0))||0
            const totalReceiptInfo = receiptStats(getAttachmentsForExpenses(filteredExpenses))
            tr+=`<tr class="table-info weight600">
                <td >${lang('Jumla','Total')}</td>
                <td></td>
                <td>${Number(filteredExpenses.length).toLocaleString()}</td>
                <td>${Number(totalExp.toFixed(2)).toLocaleString()}</td>
                <td>${totalReceiptInfo.count ? `${totalReceiptInfo.count} ${lang('risiti','receipts')} · ${Number(totalReceiptInfo.amount.toFixed(2)).toLocaleString()} ${fedha}` : '—'}</td>
            </tr>`
            
            const table = `<table class="table table-bordered table-sm" >
                        <thead>
                            <tr class="smallFont">
                                <th>#</th>
                                <th>${lang('Aina ya Matumizi','Expense Category')}</th>
                                <th>${lang('Idadi ya Matumizi','No. of Expenses')}</th>
                                <th>${lang('Jumla ya Matumizi','Total Expenses')}${fedha}</th>
                                <th>${lang('Risiti Zilizohifadhiwa','Saved Receipts')}</th>
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
                        tr+=`<tr data-val=${exp[0].st} class="viewStationDetails cursor-pointer" >
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


// Expenses by Staff
const byStaff = () => {
    const {expenses} = VDATA,
          {st} = filters(),
          filteredExpenses = st ? expenses.filter(e => e.st === st) : expenses,
          eligibleExpenses = filteredExpenses.filter(e => {
              const isSalaryOrPosho = !!e.salary || !!e.posho;
              const isFuelOrSupplies = !!e.mafuta || !!e.manunuzi;
              return isSalaryOrPosho && !isFuelOrSupplies;
          });

    const groups = eligibleExpenses.reduce((acc, exp) => {
        const sid = Number(exp.staffId || 0);
        const snameRaw = `${exp.staffFName || ''} ${exp.staffLName || ''}`.trim();
        const sname = snameRaw || exp.givenTo || lang('Haijabainishwa', 'Unspecified');
        const tin = (exp.tinNumber || exp.tin_number || '').toString().trim();
        const key = `${sid}-${sname}-${tin}`;
        if (!acc[key]) {
            acc[key] = {sid, sname, tin, rows: []};
        }
        acc[key].rows.push(exp);
        return acc;
    }, {});

    let tr = '', theData = [];
    const keys = Object.keys(groups);
    keys.forEach((key, idx) => {
        const grp = groups[key];
        const totAmo = Number(grp.rows.reduce((a, b) => a + Number(b.kiasi), 0)) || 0;
        tr += `<tr data-val="${grp.sid}" data-name="${grp.sname}" data-tin="${grp.tin || ''}" class="cursor-pointer viewStaffDetails">
                <td>${idx + 1}</td>
            <td class="text-capitalize"><a type="button" data-val="${grp.sid}" data-name="${grp.sname}" data-tin="${grp.tin || ''}" class="bluePrint viewStaffDetails text-capitalize">${grp.sname}</a></td>
                <td>${grp.tin || '-'}</td>
                <td>${Number(grp.rows.length).toLocaleString()}</td>
                <td>${Number(totAmo.toFixed(2)).toLocaleString()}</td>
            </tr>`;
        theData.push({name: grp.sname, amount: totAmo});
    });

    SAOBJ = SAOBJ.filter(n => n.name != 'sf');
    SAOBJ.push({name: 'sf', data: theData, title: lang('Matumizi kwa staff', 'Expenses by Staff')});

        const totalExp = Number(eligibleExpenses.reduce((a, b) => a + Number(b.kiasi), 0)) || 0;
    tr += `<tr class="table-info weight600">
            <td>${lang('Jumla', 'Total')}</td>
            <td></td>
            <td></td>
            <td>${Number(eligibleExpenses.length).toLocaleString()}</td>
            <td>${Number(totalExp.toFixed(2)).toLocaleString()}</td>
        </tr>`;

    const table = `<table class="table table-bordered table-sm" >
                    <thead>
                        <tr class="smallFont">
                            <th>#</th>
                            <th>${lang('Staff', 'Staff')}</th>
                            <th>${lang('TIN Number', 'TIN Number')}</th>
                            <th>${lang('Idadi ya Matumizi', 'No. of Expenses')}</th>
                            <th>${lang('Jumla ya Matumizi', 'Total Expenses')}${fedha}</th>
                        </tr>
                    </thead>
                    <tbody>${tr}</tbody>
                </table>`;

    $('#EvaluateByStaffTable').html(table);
    setDataTable('#EvaluateByStaffTable');
};


// Expenses by Tax Group
const byTaxGroup = () => {
    const {expenses} = VDATA,
          {st} = filters(),
          filteredExpenses = st ? expenses.filter(e => e.st === st) : expenses;

    const groups = filteredExpenses.reduce((acc, exp) => {
        const taxId = exp.tax || 0;
        const taxName = exp.taxGroup || lang('Tax Group Haijabainishwa', 'Unspecified Tax Group');
        const key = `${taxId}-${taxName}`;
        if (!acc[key]) {
            acc[key] = {taxId, taxName, rows: []};
        }
        acc[key].rows.push(exp);
        return acc;
    }, {});

    let tr = '', theData = [];
    const keys = Object.keys(groups);
    keys.forEach((key, idx) => {
        const grp = groups[key];
        const totAmo = Number(grp.rows.reduce((a, b) => a + Number(b.kiasi), 0)) || 0;
        const receiptInfo = receiptStats(getAttachmentsForTaxGroup(grp.taxId, grp.taxName));
        tr += `<tr data-val="${grp.taxId}" data-name="${grp.taxName}" class="cursor-pointer viewTaxGroupDetails">
                <td>${idx + 1}</td>
                <td><a type="button" data-val="${grp.taxId}" data-name="${grp.taxName}" class="bluePrint viewTaxGroupDetails">${grp.taxName}</a></td>
                <td>${Number(grp.rows.length).toLocaleString()}</td>
                <td>${Number(totAmo.toFixed(2)).toLocaleString()}</td>
                <td>${buildExpReceiptBtn(receiptInfo, {
                    'filter-type': 'tax',
                    'tax-id': grp.taxId,
                    'tax-name': grp.taxName,
                    title: grp.taxName
                })}</td>
            </tr>`;
        theData.push({name: grp.taxName, amount: totAmo});
    });

    SAOBJ = SAOBJ.filter(n => n.name != 'tax');
    SAOBJ.push({name: 'tax', data: theData, title: lang('Matumizi kwa tax group', 'Expenses by Tax Group')});

    const totalExp = Number(filteredExpenses.reduce((a, b) => a + Number(b.kiasi), 0)) || 0;
    const totalReceiptInfo = receiptStats(getAttachmentsForExpenses(filteredExpenses));
    tr += `<tr class="table-info weight600">
            <td>${lang('Jumla', 'Total')}</td>
            <td></td>
            <td>${Number(filteredExpenses.length).toLocaleString()}</td>
            <td>${Number(totalExp.toFixed(2)).toLocaleString()}</td>
            <td>${totalReceiptInfo.count ? `${totalReceiptInfo.count} ${lang('risiti','receipts')} · ${Number(totalReceiptInfo.amount.toFixed(2)).toLocaleString()} ${fedha}` : '—'}</td>
        </tr>`;

    const table = `<table class="table table-bordered table-sm" >
                    <thead>
                        <tr class="smallFont">
                            <th>#</th>
                            <th>${lang('Tax Group', 'Tax Group')}</th>
                            <th>${lang('Idadi ya Matumizi', 'No. of Expenses')}</th>
                            <th>${lang('Jumla ya Matumizi', 'Total Expenses')}${fedha}</th>
                            <th>${lang('Risiti Zilizohifadhiwa', 'Saved Receipts')}</th>
                        </tr>
                    </thead>
                    <tbody>${tr}</tbody>
                </table>`;

    $('#EvaluateByTaxGroupTable').html(table);
    setDataTable('#EvaluateByTaxGroupTable');
};


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
          is_month_format = moment(date,'YYYY-MM',true).isValid(),
          is_year_format = moment(date,'YYYY',true).isValid(),
          is_date_format = moment(date,'YYYY-MM-DD',true).isValid(),
          compare_format = is_month_format?'YYYY-MM':is_year_format?'YYYY':is_date_format?'YYYY-MM-DD':'YYYY-MM-DD',
          exp = VDATA.expenses?.filter(e=>moment(e.tarehe).format(compare_format)===date)
        //   console.log({exp,date,dta:VDATA.expenses})
            title = `${lang('Matumizi kwa siku','Expenses by Date')} <span class="bluePrint">${moment(date).format('DD/MM/YYYY')}</span>`
            VOBJ = {data:exp,title}
            moreDetails()
        }
)

$('body').on('click','.viewCategoryDetails',function(){
    const catId = $(this).data('val'),
          isSalary = Number($(this).data('salary')) === 1
          
       const   exp = isSalary ? VDATA.expenses?.filter(e=>e.salary) : VDATA.expenses?.filter(e=>e.expId===catId)
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

$('body').on('click','.viewStaffDetails',function(){
        const staffId = Number($(this).data('val')),
                    staffName = $(this).data('name') || '',
                    tin = ($(this).data('tin') || '').toString().trim(),
                    exp = VDATA.expenses?.filter(e => {
                        const isEligible = (!!e.salary || !!e.posho) && !e.mafuta && !e.manunuzi;
                        if (!isEligible) return false;
                        if (staffId) return Number(e.staffId || 0) === staffId;
                        const eTin = (e.tinNumber || e.tin_number || '').toString().trim();
                        return !Number(e.staffId || 0) && (e.givenTo || '') === staffName && eTin === tin;
                    });
        title = `${lang('Matumizi kwa staff','Expenses by Staff')} <span class="bluePrint text-capitalize">${staffName}</span>`;
        VOBJ = {data:exp,title};
        moreDetails();
})

$('body').on('click','.viewTaxGroupDetails',function(){
        const taxId = Number($(this).data('val')),
                    taxName = $(this).data('name') || '',
                    exp = taxId
                        ? VDATA.expenses?.filter(e => Number(e.tax || 0) === taxId)
                        : VDATA.expenses?.filter(e => !Number(e.tax || 0) && (e.taxGroup || lang('Tax Group Haijabainishwa','Unspecified Tax Group')) === taxName);
        title = `${lang('Matumizi kwa tax group','Expenses by Tax Group')} <span class="bluePrint">${taxName}</span>`;
        VOBJ = {data:exp,title};
        moreDetails();
})

$('body').on('click', '.exp-receipts-btn', function(e){
    e.preventDefault();
    e.stopPropagation();

    const filterType = $(this).data('filter-type');
    const title = $(this).data('title') || lang('Risiti za Matumizi','Expense Receipts');
    let items = [];

    if(filterType === 'category'){
        const catId = Number($(this).data('cat-id')) || 0;
        const isSalary = Number($(this).data('salary')) === 1;
        items = getAttachmentsForCategory(catId, isSalary);
    } else if(filterType === 'tax'){
        const taxId = Number($(this).data('tax-id')) || 0;
        const taxName = $(this).data('tax-name') || '';
        items = getAttachmentsForTaxGroup(taxId, taxName);
    }

    openExpReceiptsModal(items, `${lang('Risiti za Matumizi','Expense Receipts')} - ${title}`);
})

$('.exp-att-layout').on('click', function(){
    $('.exp-att-layout').removeClass('btn-secondary active').addClass('btn-outline-secondary');
    $(this).addClass('active btn-secondary').removeClass('btn-outline-secondary');
    expReceiptLayout = Number($(this).data('layout')) || 1;
    renderExpReceiptsGallery();
})

$('#printExpReceipts').on('click', function(){
    if(!expReceiptsData.length){
        toastr.info(lang('Hakuna risiti za kuchapisha','No receipts to print'), lang('Taarifa','Info'), {timeOut: 2500});
        return;
    }

    const printWindow = window.open('', '', 'height=800,width=1000');
    if(!printWindow){
        toastr.warning(lang('Kivinjari kimezuia popup ya print. Tafadhali ruhusu popups kisha jaribu tena.','Your browser blocked the print popup. Please allow popups and try again.'));
        return;
    }

    printWindow.document.write(company_header);
    printWindow.document.write(buildExpReceiptsPrintHtml());
    printWindow.document.write('</div></body></html>');
    printWindow.document.close();
    printWindow.focus();
    setTimeout(function(){
        printWindow.print();
        printWindow.close();
    }, 900);
})


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
    if (chartT === 'exp' || chartT === 'sf' || chartT === 'tax') {
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
            <td>${moment(d.tarehe).format('DD/MM/YYYY HH:mm')}</td>
            ${!st?`<td>${d.stationName}</td>`:''}
            <td>${d.expN||lang('Mshahara','Salary')} ${d.salary_advance?`(${lang('Malipo ya awali ya mshahara','Salary Advance')})`:''}</td>
            <td>${d.maelezo}</td>
            <td class="text-capitalize">${d.givenTo || ''}</td>
            <td class="text-capitalize">${d.byFName || ''} ${d.byLname || ''}</td>
            <td>${Number(d.kiasi).toLocaleString()}</td>
        </tr>`
    })

    // add the total row below
    const totalExp = Number(filteredData.reduce((a,b)=>a+Number(b.kiasi),0))||0
    tr+=`<tr class="table-info weight600">
        <td colspan="${st?6:7}">${lang('Jumla','Total')}</td>
        <td>${Number(totalExp.toFixed(2)).toLocaleString()}</td>
    </tr>`
    const table = `<table class="table table-bordered table-sm" >
                    <thead>
                        <tr class="smallFont">
                            <th>#</th>
                            <th>${lang('Tarehe','Date')}</th>
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

$('#printRBtn').click(function(){
    const userN = $(this).data('user')

    const summary = `<div class="row my-3">
                        <div class="col-9 row">
                            ${$('#SaLDetail .col-md-7').html() || ''}

                            <div class="col-6 col-lg-4">
                                ${lang('Imetolewa','Issued on')}:  
                            </div>
                            <div class="col-6 col-lg-8 ">
                                ${moment().format('DD/MM/YYYY HH:mm')}  
                            </div>

                            <div class="col-6 col-lg-4">
                                ${lang('Imetolewa na','Issued by')}:  
                            </div>
                            <div class="col-6 col-lg-8 text-capitalize">
                                ${userN}
                            </div>
                        </div>
                    </div>`

    let head = ''
    let tableHtml = ''

    const isDetailView = $('#MoreDetails').is(':visible')

    if (isDetailView) {
        head = `<h3>${$('#MoredetailRHeading span').html() || lang('Mchanganuo wa matumizi','Expense Details')}</h3>`
        tableHtml = $('#MoredetailRContent').find('table').first().prop('outerHTML') || ''
    } else {
        const activeSection = $('#Salecateg .DetailsTable:visible').first()
        const activeHeading = activeSection.find('h6').first().text() || lang('Ripoti ya Matumizi','Expenses Report')
        head = `<h3>${activeHeading}</h3>`
        tableHtml = activeSection.find('table').first().prop('outerHTML') || ''
    }

    if (!tableHtml) {
        toastr.info(lang('Hakuna jedwali la kuchapisha kwa sasa','No visible table to print right now'), lang('Taarifa','Info'), {timeOut: 2500})
        return
    }

    const printWindow = window.open('', '', 'height=650,width=980')
    printWindow.document.write(company_header)
    printWindow.document.write(`${head}${summary}${tableHtml}`)
    printWindow.document.write(`</div></body></html>`)
    printWindow.document.close()
    printWindow.focus()
})