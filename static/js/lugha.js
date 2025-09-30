  
const FIXED_VALUE = 2,DUKANI = Number($('#accountType').val()),PERSONAL = Number($('#accountType').data('personal')),
        CSRF={csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()},
        SMALLMEDIA = window.outerWidth < 767,
     
         POSTREQUEST = (data)=>{
            return   $.ajax({
                         type: "POST",
                         url: data.url,
                         data: {...CSRF,...data.data},
                       
               })
               
         },        
         GETREQUEST = (data)=>{
            return   $.ajax({
                         type: "GET",
                         url: data.url,
                         data: data.data,
                       
               })
               
         },       
         autoComp = SMALLMEDIA?$('#serchAutoCompleteSmall'):$('#serchAutoComplete'),
floatValue = n => Number(Number(n).toFixed(FIXED_VALUE)).toLocaleString(),
lugaVal = $('#lugha').val(),
lang = (swa,eng) => lugaVal==0?swa:eng,
hela = $('#fedha').val(),
fedha =`<span class="weight100 text-primary smallfont" > ${hela} </span>` 

function hideLoading() {
  $('#loadMe').on('shown.bs.modal', function (e) {
      $("#loadMe").modal('hide');
  })
}



function redborder(el){
  $(el).addClass('redborder')
}


function removeRedboder(){
  $('.form-control,.made-input').each(function(){
    if($(this).hasClass("redborder")){
      $(this).removeClass("redborder")
    }
    })
}


//Save attachment...........................//
$('#attachform').submit(function(e){
  e.preventDefault()
  const formData = new FormData(this),
       name = $('#printedDoc').val(),
       isDocu = Number($('#printedDocIn').prop('checked'))
      //  console.log(name);
      
       if(isDocu||name!=''){
                       $('#addAttachment').modal('hide')
     
             $('#loadMe').modal('show')
           $.ajax({
                 url: $(this).attr("action"),
                 type: 'POST',
                 data: formData,
                 cache: false,
                 processData: false,
                 contentType: false,
                 success: function (resp) {

                     $("#loadMe").modal('hide');
                     hideLoading()

                     const msg = lang(resp.msg_swa,resp.msg_eng)
                     if(resp.success){

                         toastr.success(msg, lang('Imefanikiwa','Success'), {timeOut: 2000});
                         location.reload()
                     }else{
                         toastr.error(msg, lang('Haikufanikiwa','Error'), {timeOut: 2000});

                     }

                 
                 },
                 cache: false,
                 contentType: false,
                 processData: false
             });

       }else{
         redborder('#attach_name')
       }


})



// PRINT TABLE OR DOCU
function Printable(p) {
  var divToPrint = p;
  var newWin = window.open("");
  newWin.document.write(divToPrint.outerHTML);
  newWin.print();
  newWin.close();
}


// loadModal = document.querySelector('#loadMe')

// const loadMe = new bootstrap.Modal(loadModal, {
//     backdrop: 'static'
// });


const company_header = `
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <title>Document</title>
    <link rel="stylesheet" href="/static/css/bootstrap5.min.css" >
    <link rel="stylesheet" href="/static/css/companyheader.css">
    <style>
    
    </style>
  </head>
  <body>

  ${$('#CompanyTitle').html()}
`
