$('#reg1Form').submit(function(e) {
    e.preventDefault()
   const f_name = $('#f_name').val(),
       l_name = $('#l_name').val(),
       phone = $('#Phone').val(),
       email = $('#email').val(),
       cheo = $('#cheo').val(),
       city = $('#city').val(),
       address = $('#address').val(),
       ceo = Number($('#ceo_member').prop('checked')),
       url = $(this).attr('action')
       

       if(f_name!=''&&l_name!=''&&phone!=''&&email!=''&&cheo!=''&&city!=''&&address!=''){
           $('#addStaff').modal('hide')
           $('#loadMe').modal('show')
           const data={
              data:{ f_name,
               l_name,
               phone,
               email,
               cheo,
               city,
               address,
               ceo},
               url
           },
           sendIt = POSTREQUEST(data)

           sendIt.then(resp=>{
            $('#loadMe').modal('hide')

                if(resp.success){
                    toastr.success(lang(resp.msg_swa,resp.msg_eng), lang('Imefanikiwa','Success '), {timeOut: 2000});
                    location.replace(`/staffs/viewStaff?usr=${resp.id}`)
                }else{
                        $('#loadMe').modal('hide')   
                        toastr.error(lang(resp.msg_swa,resp.msg_eng), lang('Haikufanikiwa','Error '), {timeOut: 2000});
            
                }
           })

       }else{
          if(f_name=='')redborder('#f_name')
          if(l_name=='')redborder('#l_name')
          if(phone=='')redborder('#Phone')
          if(email=='')redborder('#email')
          if(cheo=='')redborder('#cheo')
          if(city=='')redborder('#city')
          if(address=='')redborder('#address')
       }

})