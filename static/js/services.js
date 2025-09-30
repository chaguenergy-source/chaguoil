
// loadMe.show()

$('#submitService').submit(function (e) { 
    e.preventDefault();
    const  desc = $('#richTextField').contents().find("body").html(),
           name =  $('#servName').val(),
           categ =  Number(($('#servCateg').val())),
           price =  Number($('#servPrice').val()),
           address1 =  $('#servAddress1').val(),
           address2 =  $('#servAddress2').val(),
           form = $(this),

           imgs = $('#AddImg').val()

           if(desc!='' && name!='' && categ>0 && price!='' && price!=0 && address1.length > 5 && address2.length > 5 && imgs.length>0 ){
          
          

            loadMe.show()    
            let formData = new FormData(this);
                formData.append('desc',desc) 
            $.ajax({
                url: form.attr("action"),
                type: 'POST',
                data: formData,
                cache: false,
                processData: false,
                contentType: false,
                success: function (resp) {
                    loadMe.hide()

                    if(resp.success){
                        toastr.success('Service added', 'Success', {timeOut: 2000});

                        location.reload()
                    }else{
                        toastr.error('Service not added due to error', 'Error', {timeOut: 2000});

                    }

                },
                cache: false,
                contentType: false,
                processData: false,

            });

            
            
            
            // const data = {
            //         data:{
            //             desc,
            //             name,
            //             categ,
            //             price,
            //             address1,
            //             address2,
            //             img:0
            //         },
            //         url:'/services/addtheServ'
            //     },
            //     sendit = POSTREQUEST(data)
            //     sendit.then(resp=>{
            //         if(resp.success){
            //             saveImg({id:resp.id,form})
            //         }else{
            //             toastr.error('There is error', 'Error', {timeOut: 2000});

            //         }
            //     })
                

                


           }

});

function saveImg(dta){
    const form =dta.form
        console.log(form)

    let formData = new FormData(form);
        formData.append('id',dta.id)
        formData.append('img',1)

        

    $.ajax({
        url: form.attr("action"),
        type: 'POST',
        data: formData,
        cache: false,
        processData: false,
        contentType: false,
        success: function (resp) {
               loadMe.hide

               if(resp.sucess){
                toastr.success('Service added', 'Success', {timeOut: 2000});

               }else{
                  toastr.error('Service not added due to error', 'Error', {timeOut: 2000});

               }

        },
        cache: false,
        contentType: false,
        processData: false
    });


}


$('#savecateg').click(function () { 
  $(this).prop('hidden',true)
    $('#SaveCategLoad').prop('hidden',false)

    const categ = $('#addCateg').val()
     if(categ!=''){
         data = {
            data:{categ},
            url:'/services/addcateg'
         }
     }

     const sendit = POSTREQUEST(data)

     sendit.then(data=>{
           $(this).prop('hidden',false)
           $('#SaveCategLoad').prop('hidden',true)

           $('#addCateg').val('')

           if(data.success){
            toastr.success('Category added', 'Success', {timeOut: 2000});

                let opt = '<option value=0 >--Select category--</option>'
                data.categs.reverse().forEach(t => {
                    opt += `<option value=${t.id} >${t.name}</option>` 
                });

                $('#servCateg').html(opt)
                    

           }else{
             toastr.error('Category not added due to error', 'Error', {timeOut: 2000});
           }
     })


});


