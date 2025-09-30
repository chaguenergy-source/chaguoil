   $('body').on('keyup','.fuelPurchases',function(){
       PriceSett()
        
   })

   const PriceSett = () =>{
                let totPrice = 0
                    $('.puRow').each(function(){
                        const rpos = Number($(this).data('pos')),
                            rpuPr = Number($(`#puPrice${rpos}`).val()) || 0,
                            rpuQty = Number($(`#puQty${rpos}`).val()) || 0,
                            rTot = Number(rpuPr*rpuQty)
                                
                            totPrice += rTot
                            $(`#totPrice${rpos}`).val(rTot)
                            //    console.log({totPrice,rTot,rpuPr,rpuQty});
                    })

                    $('#TotPuPrice').text(Number(totPrice).toLocaleString())
   }

   $('#addPubtn').click(function(){
      const {lpos,rlen} = trT(),
            lpuPr = Number($(`#puPrice${lpos}`).val()) || 0,
            lpuQty = Number($(`#puQty${lpos}`).val()) || 0,
            fuel = Number($(`#fuelSelect${lpos}`).val()) || 0,
            pos = lpos + 1
            if(fuel&&lpuPr&&lpuQty){

                const tr = `
                                <tr data-pos=${pos} class="puRow" >
                                    <td class="IndexNo" data-pos=${pos} >${rlen+1}</td>
                                    <td>
                                        <select name="fuelSelect${pos}" id="fuelSelect${pos}" class="form-control brown btn-sm">
                                             ${$('#allFuel').html()}
                                      </select>
                                </td>  
                                <td>
                                    
                                        <div class="input-group  " >                   
                                            <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                                <label class="mt-1 text-danger " for="FuelPriceTotal"></label> 
                                            <div class="box-pointer d-inline "></div>
                                            </div>
                                            <input type="number" data-pos=${pos}   style="width: 150px;background-color: var(--whiteBg);color:var(--inputColor)"  step="0.01"  id="puPrice${pos}" name="puPrice${pos}"  class=" money-fomat btn-sm form-control fuelPurchases weight600">
                                        </div>
                                </td>                      
                                <td>
                                    <div class="input-group  " >                   
                                            <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                                <label class="mt-1 text-danger " for="FuelPriceTotal"></label> 
                                            <div class="box-pointer d-inline "></div>
                                            </div>
                                            <input type="number" data-pos=${pos}   style="width: 150px;background-color: var(--whiteBg);color:var(--inputColor)"  step="0.01"  id="puQty${pos}" name="puQty${pos}"  class=" money-fomat btn-sm form-control fuelPurchases weight600">
                                        </div>
                                
                                </td>                      
                                <td>
                                    <input type="text" readonly id="totPrice${pos}" name="totPrice${pos}"  class="form-control btn-sm weight600">
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
            }else{
              if(!fuel)redborder(`#fuelSelect${lpos}`)
              if(!lpuPr)redborder(`#puPrice${lpos}`)
              if(!lpuQty)redborder(`#puQty${lpos}`)
            }

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
                    fuel = Number($(`#fuelSelect${pos}`).val()) || 0  
                 if(puPr&&puQty&&fuel){
                        puData.push({
                        puPr,puQty,fuel
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