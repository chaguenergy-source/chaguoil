let payData = [],isAdmin = false,customerId = 0,payId=0;
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
   let data={tFr,tTo,debt_pay:1};
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
            // Tunafuta ili zisipatikane tena refresh inayofuata
            sessionStorage.removeItem('py_Ids');
            sessionStorage.removeItem('simplifiedObjects');
            // payData = res.payments
            isAdmin = res.isadmin
            // console.log(res);
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
    
   
    payData.forEach(d=>{
        const payDataFiltered = st ? d.payments.filter(p => p.st === st) : d.payments;
        const payAmo = formatNumber(payDataFiltered?.reduce((a,b)=>a+Number(b.Amount),0)) || 0,
              recCount = payDataFiltered?.length || 0,
              approval = payDataFiltered?.filter(p=>!p.admin_approval).length || 0
        tr += `<tr data-report=${d.id} class="smallFont cursor-pointer moreDetails" >
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
    const val = $(this).data('report');
    customerId = 0;
    const data = payData.filter(d=>d.id===val)[0];
    renderPaymentDetails(data);
    
})

$('body').on('click','.customerLink',function(){
    const val = $(this).data('report');
    customerId = Number($(this).data('custid')) || 0;
    const data = payData.filter(d=>d.id===val)[0];
    // console.log(customerId);
    renderPaymentDetails(data);
    
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
    const {payments,rname,id} = d,
          modalTitle = lang('Malipo ya Wateja Wadaiwa - ','Customer Debt Payment Details - ') + `<span class="bluePrint">${rname}</span>`
    let tr = '',toFocus = ''; 
    // filter payments
    const {st} = filters();
    let filteredPayments = st ? payments.filter(p => p.st === st) : payments;
    // filter Customer if selected
    
   if(customerId){
       
        filteredPayments = filteredPayments.filter(p => p.customer_id === customerId);
        const customerName = filteredPayments[0]?.custN || '';
        const custmerId = filteredPayments[0]?.customer_id || 0;
        toFocus = `  
                <div id="selectedCustomerCard" class="card mb-3" >
                    <div class="card-body d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0">${lang('Mteja: ','Customer: ')}<a href="/salepurchase/ViewCustomer?i=${custmerId}" id="selectedCustomerName">${customerName}</a></h6>
                        </div>
                        <button type="button" data-report=${id} class="moreDetails btn btn-close btn-lg largerFont" id="closeCustomerCard" aria-label="Close">&times;</button>
                    </div>
                </div>`
    }

    // check how many are unapproved
    const unapprovedCount = filteredPayments?.filter(p => !p.admin_approval).length || 0;
    const approvedCount = filteredPayments?.filter(p => p.admin_approval).length || 0;
    let count = 0;
    filteredPayments.forEach(p=>{
        count += 1;
        tr += `<tr class="smallFont  cursor-pointer" data-custid="${p.customer_id}" data-report=${id}  >
                   ${isAdmin?`<td class="text-center cursor-pointer">
                       <input type="checkbox" class="selectPayment cursor-pointer" ${p.admin_approval ? 'checked disabled' : ''} data-id="${p.id}">
                    </td>` : ''} 
                    <td  data-custid="${p.customer_id}" data-report=${id} class="customerLink" >${count}</td>
                    <td  data-custid="${p.customer_id}" data-report=${id} class="customerLink" >${moment(p.tarehe).format('DD/MM/YYYY HH:mm')}</td>
                    <td  data-custid="${p.customer_id}" data-report=${id} class="customerLink" >${p.stN || ''}</td>
                    <td  data-custid="${p.customer_id}" data-report=${id} class="customerLink text-capitalize">${p.BFname || ''} ${p.BLname || ''}</td>

                    <td> <a type="button"   data-custid="${p.customer_id}" data-report=${id} class="customerLink">${p.custN || ''}</a></td> 
                    <td   data-custid="${p.customer_id}" data-report=${id} class="customerLink text-primary" >${p.account_name || ''}</td>
                    <td   data-custid="${p.customer_id}" data-report=${id} class="customerLink" >${formatNumber(p.Amount) || 0}</td>
                    <td>
                          <span type="button"   data-custid="${p.customer_id}" data-report=${id} class="customerLink"> ${p.admin_approval ? lang('Imethibitishwa','Approved') : lang('Haijathibitishwa','Unapproved')}</span>
                          ${!p.admin_approval && customerId && isAdmin ? `
                             <button type="button" class="btn btn-sm btn-primary editPayment" data-id="${p.id}" data-custid="${p.customer_id}" data-amount="${p.Amount}" data-account="${p.Akaunt_id}" data-custname="${p.custN}">Edit</button>
                             <button type="button" class="btn btn-sm btn-danger deletePayment"  data-id="${p.id}" data-custid="${p.customer_id}">Delete</button>
                          `:''}
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


    $('#toFocus').html(toFocus);
    $('#paymentDetailsTitle').html(modalTitle)
    $('#paymentsBody').html(tr)
    $('#paymentSummary').hide()
    $('#paymentDetails').show()

}
//Comment edit payment for unapproved ones
$('body').on('click','.editPayment',function(){
    const paymentId = Number($(this).data('id')) || 0,
            custId = Number($(this).data('custid')) || 0,
            amount = Number($(this).data('amount')) || 0,
            account = Number($(this).data('account')) || 0,
            custName = $(this).data('custname') || '';

    // populate modal fields
    $('#editPaymentId').val(paymentId);
    $('#editCustomerId').val(custId);
    $('#editCustomerName').val(custName);
    $('#editPaymentAmount').val(amount);
    $('#malipo-akaunti').selectpicker('val', account);
    // console.log(account);


    $('#editPaymentModal').modal('show');
});

// submit edit payment
$('#savePaymentChanges').on('click',function(){
    const paymentId = Number($('#editPaymentId').val()) || 0,
            custId = Number($('#editCustomerId').val()) || 0,
            amount = Number($('#editPaymentAmount').val()) || 0,
            account = Number($('#malipo-akaunti').val()) || 0;
    if(!amount || amount <= 0){
        redborder('#editPaymentAmount');
        toastr.error(lang('Tafadhali weka kiasi halali','Please enter a valid amount'), lang('Haikufanikiwa','Error '), {timeOut: 2000});
        return;
    }
    if(!account){
        $('#malipo-akaunti').selectpicker('setStyle', 'btn-danger');
        toastr.error(lang('Tafadhali weka jina la akaunti','Please enter account name'), lang('Haikufanikiwa','Error '), {timeOut: 2000});
        return;
    }
    // send ajax request to update payment
    $('#editPaymentModal').modal('hide');
    $('#loadMe').modal('show');
    const data = {
        edit: paymentId,
        invo:customerId,
        pay_amo:amount,
        all:1,
        ac:account
    };
    const req = POSTREQUEST({data, url:'/salepurchase/lipaInvo'});
    req.then(res=>{
        $('#loadMe').modal('hide');
        hideLoading();
        if(res.success){
            toastr.success(lang('Malipo yamehakikiwa kwa mafanikio','Payments approved successfully'), lang('Imekamilika','Success'), {timeOut: 2000});
            // reload payments
            sesStorage();
           location.reload();
        }else{
            toastr.error(lang(res.msg_swa,res.msg_eng), lang('Haikufanikiwa','Error '), {timeOut: 2000});
        }
    }).catch(err=>{
        hideLoading();
        toastr.error(lang('Tatizo la mtandao, jaribu tena','Network error, try again'), lang('Haikufanikiwa','Error '), {timeOut: 2000});
    });
}); 

//Delete payment
$('body').on('click','.deletePayment',function(){
    const paymentId = Number($(this).data('id')) || 0,
            custId = Number($(this).data('custid')) || 0;
            payId = paymentId;
            
    // show confirmation modal
    $('#deletePaymentId').val(paymentId);
    $('#deleteCustomerId').val(custId);
    $('#confirmDeleteModal').modal('show');
});

// submit delete payment
$('body').on('click','#confirmDeletePayment',function(){
     
    // send ajax request to delete payment
    $('#confirmDeleteModal').modal('hide');
    $('#loadMe').modal('show');
    const data = {
        payId,
        customerId
    };
    const req = POSTREQUEST({data, url:'/salepurchase/DeletePayMents'});
    req.then(res=>{
        $('#loadMe').modal('hide');
        hideLoading();
        if(res.success){
            toastr.success(lang('Malipo yamefutwa kwa mafanikio','Payments deleted successfully'), lang('Imekamilika','Success'), {timeOut: 2000});
            // reload payments
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