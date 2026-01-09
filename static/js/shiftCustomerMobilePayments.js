let payData = [],isAdmin = false;
const filters = () =>{
    const  st = Number($('#stationFilter').val()),
         
         
           today = {rname:lang('Leo','Today'),tFr:moment(moment().startOf('day')).format(),tTo:moment().format()},
           week = {rname:lang('Wiki hii','This Week'),tFr:moment(moment().startOf('isoWeek')).format(),tTo:moment().format()},
           month = {rname:lang('Mwezi huu','This Month'),tFr:moment(moment().startOf('month')).format(),tTo:moment().format()}
           
           return {st,today,week,month}
}


const loadPayments = d =>{
  $('#loadMe').modal('show')

   const {tFr,tTo,rname,init} = d
   const savedIds = JSON.parse(sessionStorage.getItem('py_Ids'))||[];
   const savedObjects = JSON.parse(sessionStorage.getItem('simplifiedObjects')) || [];
   let data={tFr,tTo,mob:1};
   if (savedIds.length > 0 && savedObjects.length > 0) {
        // console.log("Data baada ya refresh:", savedIds, savedObjects);
        data = {
            ...data,
            from_session:1,
            py_Ids: JSON.stringify(savedIds),
    }}

  data = {
    data,
    url:'/salepurchase/getShiftCustomerMobilePayments'
  }
    const req = POSTREQUEST(data)
    req.then(res=>{
        $('#loadMe').modal('hide')
        hideLoading()
        if(res.success){
            // payData = res.payments
             sessionStorage.removeItem('py_Ids');
            sessionStorage.removeItem('simplifiedObjects');
            isAdmin = res.isadmin
            renderPayments({resp:res,rname,init,tFr,tTo,savedObjects})
        }else{
            toastr.error(lang(res.swa,res.eng), lang('Haikufanikiwa','Error '), {timeOut: 2000});
        }
    }).catch(err=>{
        $('#loadMe').modal('hide')
        hideLoading()
        toastr.error(lang('Tatizo la mtandao, jaribu tena','Network error, try again'), lang('Haikufanikiwa','Error '), {timeOut: 2000});
    })
}

$(document).ready(()=>{
        
         const {month} = filters(),
          {tFr,tTo,rname} = month
          loadPayments({tFr,tTo,rname,init:1});
 })



const renderPayments = d =>{
   const {resp,rname,init,tFr,tTo,savedObjects} = d,
          {today,week} = filters()
        //   {sale,saL,pay,payRec} = resp
         if(savedObjects.length && init){
                savedObjects.forEach(so=>{
                    const {tFr,tTo,rname} = so
                    createArray(rname,tFr,tTo)
                })
                 createtr()
                return
            }
    
         if(init){
                // Today report 
                ArryCreate({...resp,tFr:today.tFr,tTo:today.tTo,rname:today.rname})

                // week report 
                
                ArryCreate({...resp,tFr:week.tFr,tTo:week.tTo,rname:week.rname})
              
            }

                ArryCreate({...resp,tFr,tTo,rname})
               createtr()
}

// The seleted time duration Data....................................//
const ArryCreate = d =>{
            const {tFr,tTo,rname} = d,
                    {st} = filters(),
                     payments = d.payments?.filter(s=>moment(s.tarehe).format() >= tFr && moment(s.tarehe).format() <= tTo ),
                    
            thedt = {
                id:payData.length + 1,
                rname,
                tFr,
                tTo,
                st,
                payments
         }
         payData.push(thedt)

        }   

function createArray(rname,tFr,tTo){
        
            const saDt = payData.filter(d=>d.tFr<=tFr && d.tTo>=tTo),
                  isThere = payData.filter(d=>d.tFr===tFr && d.tTo===tTo),
                  msg = lang('tayari ipo','alread exists')
                if(isThere.length){
                     
                     toastr.info(msg, lang('Taarifa','info '), {timeOut: 2000})
                }else{
                if(saDt.length>0){
                     const {payments} = saDt[0],

                     dt = {payments,tFr,tTo,rname}
                     ArryCreate(dt)
                     createtr()

                }else{

                    loadPayments({tFr,tTo,rname,init:0});     

                }   }


                }
const createtr = () =>{
    let tr = ''
    // apply filters
    const {st} = filters();
    // let filteredData = st?payData.filter(d=>d.st===st):payData;

    payData.forEach(d=>{
        const filteredPayments = st ? d.payments.filter(p => p.st === st) : d.payments;
        const payAmo = formatNumber(filteredPayments?.reduce((a,b)=>a+Number(b.Amount),0)) || 0,
              recCount = filteredPayments?.length || 0
              approval = filteredPayments?.filter(p=>!p.admin_approval).length || 0
        tr += `<tr data-report=${d.id} class="smallFont cursor-pointer moreDetails"  >
                    <td><a type="button" data-report=${d.id} class=" moreDetails bluePrint" >${d.rname}</a></td>
                    <td>${recCount}</td>
                    <td>${payAmo}</td>
                    <td>
                        <a type="button" class="moreDetails" data-report=${d.id}>
                          <span class="badge  badge-${approval > 0 ? 'danger' : 'light'}">${approval}</span> Recs
                        </a>
                          </td>
                </tr>`
    })

    $('#paymentSummaryBody').html(tr)
}

// $(document).on('click','.moreDetails',function(){
//     const val = $(this).data('report'),
//             data = payData.filter(d=>d.id==val)[0]
// })

$('body').on('click','.moreDetails',function(){
    const val = $(this).data('report'),
            data = payData.filter(d=>d.id===val)[0]
    renderPaymentDetails(data)
    
})

$('#backToSummary').on('click',function(){
    $('#paymentDetails').hide()
    $('#paymentSummary').show()
    // reset approve all button
    $('#approveAllPayments').prop('disabled', true);
    $('#unapprovedCount').text('0');
    //uncheck all checkboxes
    $('#selectAllPayments').prop('checked', false);
})

const renderPaymentDetails = d =>{
    const {payments,rname} = d,
          modalTitle = lang('Maelezo ya Malipo ya Wateja kwa Simu - ','Customer Mobile Payment Details - ') + `<span class="bluePrint">${rname}</span>`
    let tr = '' 
    // filter payments
    const {st} = filters();
    const filteredPayments = st ? payments.filter(p => p.st === st) : payments;
    // check how many are unapproved

    const unapprovedCount = filteredPayments?.filter(p => !p.admin_approval).length || 0;
    const approvedCount = filteredPayments?.filter(p => p.admin_approval).length || 0;
    let count = 0;
    filteredPayments.forEach(p=>{
        count += 1;
        tr += `<tr class="smallFont" >
                   ${isAdmin?`<td class="text-center cursor-pointer">
                       <input type="checkbox" class="selectPayment cursor-pointer" ${p.admin_approval ? 'checked disabled' : ''} data-id="${p.id}">
                    </td>` : ''} 
                    <td>${count}</td>
                    <td>${moment(p.tarehe).format('DD/MM/YYYY HH:mm')}</td>
                    <td>${p.stN || ''}</td>
                    <td class="text-capitalize">${p.BFname || ''} ${p.BLname || ''}</td>
                    
                    <td>${p.maelezo || ''}</td> 
                    <td class="text-primary" >${p.account_name || ''}</td>
                    <td>${formatNumber(p.Amount) || 0}</td>
                    <td>
                           ${p.admin_approval ? lang('Imethibitishwa','Approved') : lang('Haijathibitishwa','Unapproved')}
                        
                    </td>
                </tr>`
    })

    //add a total row 
    const totalAmount = filteredPayments?.reduce((a,b)=>a+Number(b.Amount),0) || 0;
    tr += `<tr class="smallFont font-weight-bold">
                <td colspan="${isAdmin ? 7 : 6}">Total</td>
                <td>${formatNumber(totalAmount)}</td>
                <td> ${approvedCount}/${filteredPayments?.length || 0} ${lang('uhakiki','Approval')}</td>
            </tr>`



    $('#paymentDetailsTitle').html(modalTitle)
    $('#paymentsBody').html(tr)
    $('#paymentSummary').hide()
    $('#paymentDetails').show()

}


// checkboxe select payment to approve
$('body').on('change','.selectPayment, #selectAllPayments',function(){
    
    // check if select all
    const isCheckAll = Number($(this).data('ckeckall')) || 0;
    if(isCheckAll){
        const isChecked = $(this).is(':checked');
        // check or uncheck all checkboxes except disabled ones
        $('.selectPayment').each(function(){
            if(!$(this).is(':disabled')){
                $(this).prop('checked', isChecked);
            }
        });
    }
    // find all selected checkboxes
   const selectedPayments = $('.selectPayment:checked').filter(function() {
        return !$(this).is(':disabled');
    }).map(function() {
        return $(this).data('id');
    }).get();

    // enable or disable approve all button
    if(selectedPayments.length > 0){
        $('#approveAllPayments').prop('disabled', false);
    }else{
        $('#approveAllPayments').prop('disabled', true);
    }

    // update unapproved count
    $('#unapprovedCount').text(selectedPayments.length);
});


// approve all selected payments
$('#confirmApprovePayments').on('click',function(){
    const selectedPayments = $('.selectPayment:checked').filter(function() {
        return !$(this).is(':disabled');
    }).map(function() {
        return $(this).data('id');
    }).get();
    if(selectedPayments.length === 0){
        toastr.info(lang('Hakuna malipo yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote yaliyote iliyochaguliwa','No payments selected'), lang('Taarifa','info '), {timeOut: 2000});
        return;
    }


    // send ajax request to approve payments
    $('#confirmApprovalModal').modal('hide');
    $('#loadMe').modal('show');
    const data = {
        payment_ids: JSON.stringify(selectedPayments)
    };
    const req = POSTREQUEST({data, url:'/salepurchase/approveShiftCustomerMobilePayments'});
    req.then(res=>{
        $('#loadMe').modal('hide');
        hideLoading();
        if(res.success){
            toastr.success(lang('Malipo yamehakikiwa kwa mafanikio','Payments approved successfully'), lang('Imekamilika','Success'), {timeOut: 2000});
            // reload payments
            // $('#backToSummary').click();
            // const {tFr,tTo,rname} = payData.find(d=>d.payments.some(p=>selectedPayments.includes(p.id))) || {};
            // loadPayments({tFr,tTo,rname,init:0});

            sesStorage();
            location.reload();

        }else{
            toastr.error(lang(res.swa,res.eng), lang('Haikufanikiwa','Error '), {timeOut: 2000});
        }
    }).catch(err=>{
        hideLoading();
        toastr.error(lang('Tatizo la mtandao, jaribu tena','Network error, try again'), lang('Haikufanikiwa','Error '), {timeOut: 2000});
    });
});


// filter by station
$('#stationFilter').on('change',function(){
    createtr();
});

// custom date modal submit
$('#customDateSubmit').on('click',function(){
    const tFr = moment($('#startDate').val()).format(),
          tTo = moment($('#endDate').val()).format(),
          rname = $('#durationName').val();

          if(!rname){
            redborder('#durationName');
            toastr.error(lang('Tafadhali weka jina la muda','Please enter duration name'), lang('Haikufanikiwa','Error '), {timeOut: 2000});
            return;
          }

    if(!tFr || !tTo){
        toastr.error(lang('Tafadhali chagua tarehe zote mbili','Please select both dates'), lang('Haikufanikiwa','Error '), {timeOut: 2000});
        return;
    }
    $('#durationModal').modal('hide');
    createArray(rname,tFr,tTo);
});


function sesStorage() {
    // 1. Kutengeneza array ya IDs za payments (bila kujirudia)
    const allPaymentIds = payData.flatMap(item => item.payments.map(p => p.id));
    const py_Ids = [...new Set(allPaymentIds)];

    // 2. Kutengeneza array ya objects yenye rname, tFr, na tTo pekee
    const simplifiedObjects = payData.map(({ rname, tFr, tTo }) => ({
        rname,
        tFr,
        tTo
    }));

    // Tunageuza array kuwa string na kuzihifadhi
    sessionStorage.setItem('py_Ids', JSON.stringify(py_Ids));
    sessionStorage.setItem('simplifiedObjects', JSON.stringify(simplifiedObjects));

}