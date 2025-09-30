   // save Customer.............................................
$('#form-mteja').submit(function(e){
    e.preventDefault()
    const url=$(this).attr("action")

    const jina = $('#mteja-jina').val(),
       adress=$('#mteja-sehemu').val(),
       code=$('#mteja-simu-code').val(),
       simu1=$('#mteja-simu').val(),
       simu2=$('#mteja-simu2').val(),
       mail=$('#mteja-mail').val(),
       u=Number($('#uni_cust').prop('checked')),
       edit = $(this).data('edit'),
       valued = $(this).data('valued')
       
    if(jina!=''){
        if(adress!=''){

            if(simu1.length==9){
                if(code.length>2){
                     var csrfToken =   $('input[name=csrfmiddlewaretoken]').val()

        const data={
       data:{
             jina:jina,
             adress:adress,
             code:code,
             simu1:simu1,
             simu2:simu2,
             u,
             value:$(this).data('customer_value'),
             mail:mail,
             edit:edit,
             valued:valued,
            csrfmiddlewaretoken:csrfToken, 
        } ,    
            url,
           
        
        }


        if(simu2=='' || simu2.length==9){
            // supplier_selected.state=false
              $('#wateja-modal').modal('hide')
              $('#loadMe').modal('show')

             const  sendIt = POSTREQUEST(data)

             sendIt.then(resp=>{
            $('#loadMe').modal('hide')
            hideLoading()   
                if(resp.success){
                    toastr.success(lang(resp.message_swa,resp.message_eng), lang('Imefanikiwa','Success '), {timeOut: 2000});
                    location.reload()
                }else{
                        toastr.error(lang(resp.message_swa,resp.message_eng), lang('Haikufanikiwa','Error '), {timeOut: 2000});
            
                }
           })


        }else{
            // alert(lang("Tafadhali Andika namba ya simu kwa simu2 kwa usahihi","Please write Vender contact 2 correctly"))
            redborder('#mteja-simu2')
            $('#mteja-simu2').siblings('small').prop('hidden',false)
        }

                }else{
                    //  alert(lang("Tafadhali Andika code ya simu kwa usahihi","Please write country code correctly"))
                    redborder('#mteja-simu-code') 
                    $('#mteja-simu-code').siblings('small').prop('hidden',false)
                }
               
            }else{
            //    alert(lang("Tafadhali Andika namba ya simu kwa simu1 kwa usahihi","Please write Vender contact 1 correctly"))
            redborder('#mteja-simu')
            $('#mteja-simu').siblings('small').prop('hidden',false)

            }
            
        }else{
            // alert(lang("Tafadhali Andika mahali mmteja anapatikana","Please write Vender Address"))
            redborder('#mteja-sehemu')
            $('#mteja-sehemu').siblings('small').prop('hidden',false)

        }
      
    }else {
        // alert(lang("Tafadhali andika jina la mmteja","Please write Vendor Name"))
        $('#mteja-jina').siblings('small').prop('hidden',false)

        redborder('#mteja-jina')
    }
})

$('#customerStatement').click(function(){
    const userN = $(this).data('user'),
         prev = Number($(this).data('prev')),
         this_month = Number($(this).data('month')),
         station = $(this).data('station')
    const head=lang(`<h3 class="text-center brown weight600">Taarifa za Mteja ${moment().format('MMMM YYYY')} </h3>`,`<h3 class="text-center brown weight600">Customer Statement ${moment().format('MMMM YYYY')} </h3>`)
    const custDetails = ` <div class="row">
                              <div class="col-12"><strong> ${lang('Taarifa za Mteja','Customer Details')}</strong></div>
                              <div class="col-md-5 row">
                              ${$('#customerDetails .col-md-5').html()}
                              <hr class="col-12">
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
                                    <div class="col-6 col-lg-4">
                                        ${lang('Kituo','Station')}:  
                                    </div>
                                    <div class="col-6  col-lg-8 ">
                                        ${station}    
                                    </div>
                              </div>
                        </div> `
          
    const summary = `<div class="row mt-3"  >${$('#customerSummary').html()}</div>`

    const thisMonthTable = `
            <div class=" this_Month " >
                     <strong>
                        ${lang(' Ankara kwa Mwezi','Invoices On')} ${moment().format('MMMM YYYY')}
                    </strong> </div>
             
                  ${this_month?$('#this_Month').html():`<div class="alert alert-light text-center" >${lang('Hakuna Ankara kwa mwezi huu','No Invoices On This Month')}</div>`}   
           
    `

    const prevSaleTable = `
            <div class=" prev_Sale " >
                     <strong>
                        ${lang(' Ankara Miezi ya Nyuma','Previous Month(s) Invoices')}
                        </strong>
                         </div>

                       
                       ${prev?$('#last_Month').html():`<div class="alert alert-light text-center" >${lang('Hakuna Ankara za miezi ya nyuma','No Previous Month(s) Invoices')}</div>`}
                        
                        `

    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write(company_header);
    printWindow.document.write(`${head} ${custDetails} ${summary} <hr> ${thisMonthTable} <hr> ${prevSaleTable}`); 
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
    // create a delay to allow the content to render before printing
    // setTimeout(() => {
    //     printWindow.print();
    //     printWindow.close();
    // }, 700);
  })