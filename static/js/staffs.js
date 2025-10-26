$('#reg1Form,#editStaffForm').submit(function(e) {
    e.preventDefault()

   const edit = Number($(this).data('edit'))||0,
       f_name = !edit?$('#f_name').val():$('#editFirstName').val(),
       l_name = !edit?$('#l_name').val():$('#editLastName').val(),
       phone = !edit?$('#Phone').val():$('#editPhone').val(),
       email = !edit?$('#email').val():$('#editEmail').val(),
       cheo = !edit?$('#cheo').val():$('#editPosition').val(),
       city = !edit?$('#city').val():$('#editCity').val(),
       address = !edit?$('#address').val():$('#editAddress').val(),
       ceo = Number($('#ceo_member').prop('checked')) || 0,
       url = $(this).attr('action'),
       user = Number($(this).data('user'))||0
       

       if(f_name!=''&&l_name!=''&&phone!=''&&email!=''&&cheo!=''&&city!=''&&address!=''){
           $(`${edit ? '#editStaffModal' : '#addStaff'}`).modal('hide')
           $('#loadMe').modal('show')
           const data={
              data:{ f_name,
               l_name,
               phone,
               email,
               cheo,
               city,
               address,
               user,
               edit,    
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