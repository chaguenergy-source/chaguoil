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
       kituo = !edit?Number($('#staff_kituo').val())||null:Number($('#editStaffKituo').val())||null,
       url = $(this).attr('action'),
       user = Number($(this).data('user'))||0,
       staff_type = !edit?$('#staff_type').val()||0:$('#editStaffType').val()||0,
       isPermanent = staff_type=='kudumu'?1:0,
       kibarua = staff_type=='kibarua'?1:0,
       parttime = staff_type=='parttime'?1:0,
       ceo = kituo == 0?1:0,
        tin = !edit?$('#tin_number').val():$('#edit_tin_number').val(),
        basic_salary = !edit?(Number($('#basic_salary').val())||0):(Number($('#editBasicSalary').val())||0),
            salary_payment_source = !edit?($('#salary_payment_source').val()||'headOffice'):($('#editSalaryPaymentSource').val()||'headOffice'),
            nin = !edit?$('#nin_number').val():$('#edit_nin_number').val(),
        salary_station = !edit?(Number($('#salary_station').val())||0):(Number($('#editSalaryStation').val())||0),
        salary_payment_period = !edit?($('#salary_payment_period').val()||'month'):($('#editSalaryPaymentPeriod').val()||'month'),
        salary_last_paid_date = !edit?($('#salary_last_paid_date').val()||''):($('#editSalaryLastPaidDate').val()||''),
        male = !edit?Number($('#male_gender').is(':checked')):Number($('#editMaleGender').is(':checked')),
        female = !edit?Number($('#female_gender').is(':checked')):Number($('#editFemaleGender').is(':checked')),
        tax_group = !edit?Number($('#TaxGroup').val())||0:Number($('#editTaxGroup').val())||0
      if(kituo==null){redborder(!edit?'#staff_kituo':'#editStaffKituo');return}

            if(!male && !female){
                    redborder(edit?'#gender_panel_edit':'#gender_panel');
                    return;
            }

      if(staff_type=='kudumu' || staff_type=='parttime'){
          if(salary_payment_source=='station' && (salary_station==0 || Number.isNaN(salary_station))){
              redborder(edit?'#editSalaryStation':'#salary_station');
              return;
          }
          if(!salary_payment_period){
              redborder(edit?'#editSalaryPaymentPeriod':'#salary_payment_period');
              return;
          }
          if(!salary_last_paid_date){
              redborder(edit?'#editSalaryLastPaidDate':'#salary_last_paid_date');
              return;
          }
      }

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
               kituo,
               isPermanent,
               ceo,
                    nin,
                    tin,
                    basic_salary,
                    salary_payment_source,
                    salary_station,
                    salary_payment_period,
                    salary_last_paid_date,
                    kibarua,
                    parttime,
                    male,
                    female,
                    tax_group
            },
               url
           },
           sendIt = POSTREQUEST(data)

           sendIt.then(resp=>{
            $('#loadMe').modal('hide')
            hideLoading()

                if(resp.success){
                    toastr.success(lang(resp.msg_swa,resp.msg_eng), lang('Imefanikiwa','Success '), {timeOut: 2000});
                    location.replace(`/staffs/viewStaff?usr=${resp.id}`)
                    // console.log(resp)
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