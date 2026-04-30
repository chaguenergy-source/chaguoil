   $('body').on('keyup','.fuelPurchases',function(){
       PriceSett()
        
   })

   const PriceSett = () =>{
                let totPrice = 0,totQty = 0,totCost = 0,totTrasp = 0
                    $('.puRow').each(function(){
                        const rpos = Number($(this).data('pos')),
                            rpuPr = Number($(`#puPrice${rpos}`).val()) || 0,
                            rpuQty = Number($(`#puQty${rpos}`).val()) || 0,
                            trasp = Number($(`#charges${rpos}`).val()) || 0,
                            rTot = Number(rpuPr*rpuQty)
                            totQty +=  rpuQty   
                            totPrice += rTot
                            totTrasp += trasp
                            totCost += rTot + trasp
                            $(`#totPrice${rpos}`).val(rTot)
                            //    console.log({totPrice,rTot,rpuPr,rpuQty});
                    })
                     
                    $('#TotPuPrice').text(Number(totPrice).toLocaleString())
                    $('#TotTransportFee').text(Number(totTrasp).toLocaleString())
                    $('#TotQty').text(Number(totQty).toLocaleString())
                    $('#TotPurchaseCost').text(Number(totCost).toLocaleString())
   }



   $('#addPubtn').click(function(){
      const {lpos,rlen} = trT(),
            lpuPr = Number($(`#puPrice${lpos}`).val()) || 0,
            lpuQty = Number($(`#puQty${lpos}`).val()) || 0,
            fuel = Number($(`#fuelSelect${lpos}`).val()) || 0,
            ltrasp = Number($(`#transporter${lpos}`).val()) || 0,
            lvehicle = $(`#vehicle${lpos}`).val(),
            ldriver = $(`#driver${lpos}`).val(),
            
            
            pos = lpos + 1
            const torecyle_fuel = $(`#recylebtnFuel${lpos}`).hasClass('btn-warning')
            const torecyle_transporter = $(`#recylebtnTransp${lpos}`).hasClass('btn-warning')
            const torecyle_vihecle = $(`#recylebtnVehicle${lpos}`).hasClass('btn-warning')
            const torecyle_driver = $(`#recylebtnDriver${lpos}`).hasClass('btn-warning')
            const torecyle_charges = $(`#recylebtnCharges${lpos}`).hasClass('btn-warning')
            if(!ltrasp){redborder(`#transporter${lpos}`);return}
            if(!lvehicle){redborder(`#vehicle${lpos}`);return}
            if(!ldriver){redborder(`#driver${lpos}`);return}
           

            if(fuel&&lpuPr&&lpuQty){

                const tr = `  
                                <tr data-pos=${pos} class="puRow" >
                                    <td class="IndexNo" data-pos=${pos} >${rlen+1}</td>
                                    <td>
                                      <div>
                                            <select name="fuelSelect${pos}" id="fuelSelect${pos}" class="form-control table-input brown btn-sm">
                                                ${$('#allFuel').html()}
                                        </select>
                                        </div>
                                        <div class="text-right " style="margin-top:-3px" >
                                            <span type="button" id="recylebtnFuel${pos}" data-pos=${pos} data-recycle="fuelSelect${pos}" data-classi="recylebtnFuel" class="recylebtn recylebtnFuel ${torecyle_fuel?'btn-warning':''}"  title="${lang('Tumia Tena','Re-use')}" >
                                                <!-- sync svg icon -->
                                                <svg xmlns="http://www.w3.org/2000/svg" height=".8em" viewBox="0 -960 960 960" stroke-width="1" width=".8em"  fill="currentColor">
                                                    <path d="M80-180v-80h57q-47-42-72-99.5T40-480q0-107 67-189.5T280-774v82q-72 20-116 78.5T120-481q0 50 21 93.5t59 75.5v-68h80v200H80Zm320-6v-82q72-20 116-78.5T560-479q0-50-21-93.5T480-648v68h-80v-200h200v80h-57q47 42 72 99.5T640-480q0 107-67 189.5T400-186Zm380 26L640-300l57-56 43 43v-487h80v488l44-44 56 56-140 140Z"/>
                                                </svg>
                                            </span>
                                        </div>
                                    </td>  

                                <td>   
                                 <div>
                                    <select name="transporter1" id="transporter${pos}" class="form-control  transporterSelect table-input bluePrint btn-sm">
                                        ${$('#transporter_select').html()}
                                    </select>
                                    </div>  
                                      <div class="text-right " style="margin-top:-3px" >
                                    <span type="button" id="recylebtnTransp${pos}"  data-pos=${pos} data-recycle="transporter${pos}" data-classi="recylebtnTransp" class="recylebtn recylebtnVehicle recylebtnTransp ${torecyle_transporter?'btn-warning':''}"  title="${lang('Tumia Tena','Re-use')}" >
                                        <!-- sync svg icon -->
                                        <svg xmlns="http://www.w3.org/2000/svg" height=".8em" viewBox="0 -960 960 960" stroke-width="1" width=".8em"  fill="currentColor">
                                            <path d="M80-180v-80h57q-47-42-72-99.5T40-480q0-107 67-189.5T280-774v82q-72 20-116 78.5T120-481q0 50 21 93.5t59 75.5v-68h80v200H80Zm320-6v-82q72-20 116-78.5T560-479q0-50-21-93.5T480-648v68h-80v-200h200v80h-57q47 42 72 99.5T640-480q0 107-67 189.5T400-186Zm380 26L640-300l57-56 43 43v-487h80v488l44-44 56 56-140 140Z"/>
                                        </svg>
                                    </span>
                                </div>
                            </td>

                        <td>
                            <div>
                                <input type="text"  id="vehicle${pos}" ${torecyle_vihecle?'value="'+$(`#vehicle${lpos}`).val()+'"':''}  name="vehicle${pos}"  class=" form-control table-input btn-sm weight600">
                            </div>
                             <div class="text-right " style="margin-top:-3px" >
                                    <span type="button" id="recylebtnVehicle${pos}" data-pos=${pos} data-recycle="vehicle${pos}" data-classi="recylebtnVehicle" class="recylebtn recylebtnVehicle ${torecyle_vihecle?'btn-warning':''}"  title="${lang('Tumia Tena','Re-use')}" >
                                        <!-- sync svg icon -->
                                        <svg xmlns="http://www.w3.org/2000/svg" height=".8em" viewBox="0 -960 960 960" stroke-width="1" width=".8em"  fill="currentColor">
                                            <path d="M80-180v-80h57q-47-42-72-99.5T40-480q0-107 67-189.5T280-774v82q-72 20-116 78.5T120-481q0 50 21 93.5t59 75.5v-68h80v200H80Zm320-6v-82q72-20 116-78.5T560-479q0-50-21-93.5T480-648v68h-80v-200h200v80h-57q47 42 72 99.5T640-480q0 107-67 189.5T400-186Zm380 26L640-300l57-56 43 43v-487h80v488l44-44 56 56-140 140Z"/>
                                        </svg>
                                    </span>
                                </div>

                        </td>
                        <td>
                            <div>   
                               <input type="text"  id="driver${pos}" ${torecyle_driver?'value="'+$(`#driver${lpos}`).val()+'"':''}  name="driver${pos}"  class=" form-control table-input btn-sm weight600">
                            </div>
                                <div class="text-right " style="margin-top:-3px" >
                                    <span type="button" id="recylebtnDriver${pos}" data-pos=${pos} data-recycle="driver${pos}" data-classi="recylebtnVehicle" class="recylebtn recylebtnVehicle ${torecyle_driver?'btn-warning':''}"  title="${lang('Tumia Tena','Re-use')}" >
                                        <!-- sync svg icon -->
                                        <svg xmlns="http://www.w3.org/2000/svg" height=".8em" viewBox="0 -960 960 960" stroke-width="1" width=".8em"  fill="currentColor">
                                            <path d="M80-180v-80h57q-47-42-72-99.5T40-480q0-107 67-189.5T280-774v82q-72 20-116 78.5T120-481q0 50 21 93.5t59 75.5v-68h80v200H80Zm320-6v-82q72-20 116-78.5T560-479q0-50-21-93.5T480-648v68h-80v-200h200v80h-57q47 42 72 99.5T640-480q0 107-67 189.5T400-186Zm380 26L640-300l57-56 43 43v-487h80v488l44-44 56 56-140 140Z"/>
                                        </svg>
                                    </span>
                                </div>

                        </td>
                        <td>
                        <div class="input-group  " >  
                        <div>
                                <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                        <label class="mt-1 text-danger " for="charges${pos}"></label> 
                                       <div class="box-pointer d-inline "></div>
                                    </div>

                            <input type="number" ${torecyle_charges?'value="'+$(`#charges${lpos}`).val()+'"':''} id="charges${pos}" data-pos=${pos} placeholder="0" name="charges${pos}" step="0.01"  class="table-input fuelPurchases form-control money-fomat btn-sm weight600">
                      </div>
                      </div>
                      <div class="text-right " style="margin-top:-3px" >
                                    <span type="button" id="recylebtnCharges${pos}" data-pos=${pos} data-recycle="charges${pos}" data-classi="recylebtnCharges" class="recylebtn recylebtnCharges ${torecyle_charges?'btn-warning':''}"  title="${lang('Tumia Tena','Re-use')}" >
                                        <!-- sync svg icon -->
                                        <svg xmlns="http://www.w3.org/2000/svg" height=".8em" viewBox="0 -960 960 960" stroke-width="1" width=".8em"  fill="currentColor">
                                            <path d="M80-180v-80h57q-47-42-72-99.5T40-480q0-107 67-189.5T280-774v82q-72 20-116 78.5T120-481q0 50 21 93.5t59 75.5v-68h80v200H80Zm320-6v-82q72-20 116-78.5T560-479q0-50-21-93.5T480-648v68h-80v-200h200v80h-57q47 42 72 99.5T640-480q0 107-67 189.5T400-186Zm380 26L640-300l57-56 43 43v-487h80v488l44-44 56 56-140 140Z"/>
                                        </svg>
                                    </span>
                                </div>

                        </td>
                                <td>
                                      
                                        <div class="input-group  " >  
                                        <div>                 
                                            <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                                <label class="mt-1 text-danger " for="puPrice${pos}"></label> 
                                            <div class="box-pointer d-inline "></div>
                                            </div>
                                            <input type="number" data-pos=${pos}   style="background-color: var(--whiteBg);color:var(--inputColor)"  step="0.01"  id="puPrice${pos}" name="puPrice${pos}"  class="table-input money-fomat btn-sm form-control fuelPurchases weight600">
                                        </div>
                                        </div>
                                </td>    

                                <td>
                                    <div class="input-group  " >         
                                       <div>          
                                            <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                                <label class="mt-1 text-danger " for="puQty${pos}"></label> 
                                            <div class="box-pointer d-inline "></div>
                                            </div>
                                            <input type="number" data-pos=${pos}   style="background-color: var(--whiteBg);color:var(--inputColor)"  step="0.01"  id="puQty${pos}" name="puQty${pos}"  class="table-input money-fomat btn-sm form-control fuelPurchases weight600">
                                        </div>
                                        </div>
                                
                                </td>                      
                                <td>
                                    <input type="text" readonly id="totPrice${pos}" name="totPrice${pos}"  class="form-control table-input btn-sm weight600">
                                </td> 
                                
                                <td>
                                    <a type="button" data-pos=${pos} class="brown rowRemoveBtn text-danger" >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="1.3em" height="1.3em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-minus-circle">
                                            <circle cx="12" cy="12" r="10"></circle>
                                            <line x1="8" y1="12" x2="16" y2="12"></line>
                                        </svg>
                                        </a>                             
                                </td>
                        
                                </tr>
                `
                $('#puRows').append(tr)
                
             if(torecyle_fuel)$(`#fuelSelect${pos}`).val($(`#fuelSelect${lpos}`).val())
             if(torecyle_transporter)$(`#transporter${pos}`).val($(`#transporter${lpos}`).val())

            }else{
              if(!fuel)redborder(`#fuelSelect${lpos}`)
              if(!lpuPr)redborder(`#puPrice${lpos}`)
              if(!lpuQty)redborder(`#puQty${lpos}`)
            }

   })

// Recycle Btns ...........................//
$('body').on('click','.recylebtn',function(){
   const allclass = $(this).data('classi')
   const isActive = $(this).hasClass('btn-warning')
   $(`.${allclass}`).each(function(){
    const isActive_too = $(this).hasClass('btn-warning')
    if(isActive==isActive_too)$(this).toggleClass('btn-warning')
})
  

})

   //Remove Row Btn ...........................//
$('body').on('click','.rowRemoveBtn',function(){

    const {rlen,lpos}= trT()
    if(rlen>1&&confirm(lang('Ondoa','Remove'))){
        let pos = Number($(this).parent('td').siblings('.IndexNo').last().text())
        $(this).parent('td').parent('tr').remove()
        PriceSett()
       if(pos!=lpos){
            $('.IndexNo').each(function(){
                const Ipos = Number($(this).text())
               //  console.log({Ipos,pos});
                if(Ipos>pos){
                    $(this).text(pos)
                    pos+=1
                }
            })        
       }



    }
})

const trT = () =>{
         const  rlen = $('#puRows').children('tr').length,
                lpos = $('#puRows').children('tr').last().data('pos')

                return {lpos,rlen}
}

$('#saveBtn').click(function(){
    let  err = 0
    const puDate =$('#pu_date').val(),
          puRef = $('#pu_reference').val(),
          ven = Number($(this).data('vendor')),
          url = '/salepurchase/addPurchase'
          puData = []
          $('.puRow').each(function(){
            const pos = Number($(this).data('pos')),
                    puPr = Number($(`#puPrice${pos}`).val()) || 0,
                    puQty = Number($(`#puQty${pos}`).val()) || 0,
                    fuel = Number($(`#fuelSelect${pos}`).val()) || 0 ,
                    transporter = Number($(`#transporter${pos}`).val()) || 0,
                    vehicle = $(`#vehicle${pos}`).val(),
                    driver = $(`#driver${pos}`).val(),
                    charges = Number($(`#charges${pos}`).val()) || 0
                 if(puPr&&puQty&&fuel&&transporter&&vehicle&&driver){
                        puData.push({
                        puPr,puQty,fuel,transporter,vehicle,driver,charges
                    })   
                 }else{
                    if((puPr||puQty||fuel)&&(!puPr||!fuel||!puQty)){
                        if(!puQty)redborder(`#puQty${pos}`)
                        if(!puPr)redborder(`#puPrice${pos}`)
                        if(!fuel)redborder(`#fuelSelect${pos}`)
                            err += 1
                    }
                 }   
                 
                    
             
          })


          if(!err&&puDate){
            $('#loadMe').modal('show')
               const data = {data:{puRef,puDate:moment(puDate).format(),ven,puDt:JSON.stringify(puData)},url},
                sendIt = POSTREQUEST(data)
                sendIt.then(resp=>{
                    $('#loadMe').modal('hide')
                        hideLoading()
                        const msg = lang(resp.swa,resp.eng)
                        if(resp.success){
                            toastr.success(msg, lang('Imefanikiwa','Success '), {timeOut: 2000})
                            location.replace(`/salepurchase/viewPurchase?i=${resp.pu}`)
                        }else{
                        toastr.error(msg, lang('Haikufanikiwa','Error '), {timeOut: 2000})
                        }
                })

          }else{
            if(!puDate)redborder('#pu_date')
          }

})