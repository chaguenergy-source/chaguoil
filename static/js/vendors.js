   // save Vendor.............................................
$('#form-mteja').submit(function(e){
    e.preventDefault()
    const url=$(this).attr("action")

    const jina = $('#mteja-jina').val(),
       adress=$('#mteja-sehemu').val(),
       code=$('#mteja-simu-code').val(),
       simu1=$('#mteja-simu').val(),
       simu2=$('#mteja-simu2').val(),
       mail=$('#mteja-mail').val(),
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
              $('#wasambazaji-modal').modal('hide')
              $('#loadMe').modal('show')

             const  sendIt = POSTREQUEST(data)

             sendIt.then(resp=>{
            $('#loadMe').modal('hide')

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
