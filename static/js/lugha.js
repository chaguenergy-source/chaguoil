  
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

  function formatNumber(v){
    return Number(v||0).toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
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
    
    <link rel="stylesheet" href="https://storage.googleapis.com/chagufilling/static/css/bootstrap5.min.css" >
    <link rel="stylesheet" href="https://storage.googleapis.com/chagufilling/static/css/companyheader.css">
   
    <style>
      body { 
        margin:0;
        padding:0;
        font-family: Arial, Helvetica, sans-serif;
        line-height: 1.6;
        font-weight: 600;
        color: #000;
     }

     .document-header {
            width: 100%;
            font-family: Arial, sans-serif;
            color: #333;
            text-align: center;
        }

/* Sehemu ya details: Sasa hivi tunazisogeza karibu na logo */
.header-details {
    display: flex;
    justify-content: center; /* Inazileta zote katikati */
    align-items: center;    /* Inazipanga mstari mmoja usawa wa logo */
    gap: 40px;              /* Huu ndio umbali kati ya contacts, logo, na address */
    padding: 10px 0;
    width: 100%;
}

/* Contacts (Kushoto kwa logo) */
.contact-info {
    text-align: right;     /* Maandishi yaegemee upande wa logo */
    font-size: 16px;
    line-height: 1;
    flex: 1;               /* Inaruhusu kuchukua nafasi iliyobaki upande wake */
}

/* Logo (Katikati) */
.logo-container {
    flex: 0 0 auto;        /* Logo ibaki na saizi yake asilia bila kusogezwa */
    text-align: center;
}

.logo-container img {
    width: 80px;           /* Rekebisha kulingana na picha yako */
    display: block;
    margin: 0 auto;
}

/* Address (Kulia kwa logo) */
.address-info {
    text-align: left;      /* Maandishi yaegemee upande wa logo */
    font-size: 16px;
    line-height: 1;
    flex: 1;               /* Inaruhusu kuchukua nafasi iliyobaki upande wake */
}

/* Jina la Kampuni Juu */
.header-main-title {
    color: #007bff; /* Blue ya Chagu Energies */
    font-size: 32px;
    font-weight: bold;
    letter-spacing: 2px;
    margin-bottom: 10px;
    text-transform: uppercase;
    text-align:center;
}

/* Mstari wa Blue wa chini */
.blue-line {
    height: 3px;
    background-color: #007bff;
    margin-top: 15px;
    width: 100%;
}

     .page {
            width: auto;
            
            margin: 10mm auto;
            background: white;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
            box-sizing: border-box;
            overflow: hidden;
            position: relative;
        }

        /* Print-specific overrides */
        @media print {
           
            .page {
                margin: 0;
                box-shadow: none;
                page-break-after: always;
            }
            /* Hides UI elements like buttons when printing */
            .no-print {
                display: none;
            }
        }

     

        table th, table td, table tr {
          padding: 8px 12px;
          color: #000;
          font-size: 14px;
          border-color: #000;

      }
      table {
       border-color: #000;
       border-width: 1px;
       border-style: solid;
      }

    </style>
  </head>
  <body>

  ${$('#CompanyTitle').html()}
  `

  const printProperties =`
              <script>
                        // JavaScript ya kuangalia upana na kubadilisha layout
                    window.onbeforeprint = () => {
                        const contentWidth = document.getElementById('myDocument').offsetWidth;
                        const style = document.getElementsByTagName('style');
                        
                        // Ikiwa upana ni mkubwa kuliko A4 (takriban 794px), weka Landscape
                        console.log('Content Width:', contentWidth);
                        if (contentWidth > 800) {
                            style.innerHTML = "@page { size: landscape; }";
                        } else {
                            style.innerHTML = "@page { size: portrait; }";
                        }


                        document.head.appendChild(style);
                    };
            </script>
  
  `

//  function that compress the fimagefile if the file exceeds 200kb  and return the file else return the file as it is
      function compressImage(file, callback) {
    if (file.size > 200 * 1024) { // Kama imezidi 200Kb
        var reader = new FileReader();
        reader.onload = function(event) {
            var img = new Image();
            img.onload = function(e) {
                var canvas = document.createElement('canvas');
                
                // Punguza vipimo (Width & Height)
                var maxWidth = 1000; // Unaweza kuongeza hapa badala ya 600
                var ratio = maxWidth / img.width;
                
                // Kama picha tayari ni ndogo kuliko maxWidth, usikuze
                if(ratio > 1) ratio = 1; 

                canvas.width = img.width * ratio;
                canvas.height = img.height * ratio;
                
                var ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                // Hapa ndipo uchawi ulipo: 
                // 1. Tunalazimisha iwe image/jpeg
                // 2. Tunaweka quality ya 0.7 (70%)
                canvas.toBlob(function(blob) {
                    var compressedFile = new File([blob], file.name.replace(/\.[^/.]+$/, "") + ".jpg", {
                        type: "image/jpeg"
                    });
                    
                    // Ikiwa bado ni kubwa, unaweza kurudia kwa quality ndogo zaidi (mfano 0.5)
                    callback(compressedFile);
                }, "image/jpeg", 0.7); 
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    } else {
        callback(file);
    }
}
