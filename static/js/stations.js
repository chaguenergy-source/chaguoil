$('#addStationForm').submit(function(e) {
    e.preventDefault()
    const url = $(this).attr('action'),
     name = $('#station_name').val(),
     address = $('#station_address').val(),
     city = $('#station_distric').val(),
     region = $('#station_mkoa').val(),
     data = {
        data:{
            name,
            address,
            city,
            region
        },
        url
     }

     if(name!=''&&address!=''&&city!=''&&region!=''){
            const sendIt = POSTREQUEST(data)
           $('#addStations').modal('hide')
           $('#loadMe').modal('show')
            sendIt.then(resp=>{
               if(resp.success){
                  toastr.success(lang(resp.msg_swa,resp.msg_eng), lang('Imefanikiwa','Success '), {timeOut: 2000});
                  location.reload()
               }else{
                      toastr.error(lang(resp.msg_swa,resp.msg_eng), lang('Haikufanikiwa','Error '), {timeOut: 2000});
            
               }

               $('#loadMe').modal('hide')

            })

     }else{
        if(name=='')redborder('#station_name')
        if(address=='')redborder('#station_address')
        if(city=='')redborder('#station_distric')
        if(region=='')redborder('#station_mkoa')
     }
 
})