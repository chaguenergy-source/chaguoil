$('#containerSale').change(function(){
     const cont = Number($(this).val()),
            gvn=Number($(this).find('option:selected').data('by'))||0;
          
            if(gvn){$('#tank_incharge2').selectpicker('val',gvn);$('#tank_incharge2').selectpicker('refresh');$('#fuelGivenTo').selectpicker('setStyle','bluePrint')}
            $('.safrm_tank').prop('disabled',!cont)
            
            $('.safrm_tank option[data-val!=0]').hide()
            $(`.safrm_tank option[data-tank=${cont}]`).show()
            $(`.safrm_tank`).val(0)
           $(this).selectpicker('setStyle', 'bluePrint')
           $(`.showFuel`).text('------')
           
})

$('body').on('change','.pmpSelect, .safrm_tank',function(){
    const pos = Number($(this).data('pos')),
          fname = $(this).find('option:selected').data('fname'), 
          fPrice = Number($(this).find('option:selected').data('saprice')),
          inch =  Number($(this).find('option:selected').data('incharger'))||0,
          pmpAttend = $(this).find('option:selected').data('incharge')
          $(`#showFuel${pos}`).text(fname)
          
          if(inch){$(`#showAttend${pos}`).text(pmpAttend)}else{$(`#showAttend${pos}`).text('-------')}

          $(`#saPrice${pos}`).attr('placeholder',fPrice.toLocaleString())
          $(`#saQty${pos}`).val('')  
           setAmo()
})

$('body').on('keyup','.fuelSalesSet',function(){
           const val = Number($(this).val())||0
           const isTotPrice = Number($(this).data('tprice'))||0
           const pos = Number($(this).data('pos'))
           const isQty = Number($(this).data('qty'))||0,
            isPrice = Number($(this).data('price'))||0 ,
            {mv} = trT(),
            saPrice = Number(mv?$(`#safrm_tank${pos}`).find('option:selected').data('saprice'):$(`#sa_pumpSt${pos}`).find('option:selected').data('saprice')),
            price = Number($(`#saPrice${pos}`).val()) || saPrice || 0,
            Qty =  Number($(`#saQty${pos}`).val())

            if(isPrice || isQty)$(`#totPrice${pos}`).val(Number(price*Qty))
            if(isTotPrice)$(`#saQty${pos}`).val(Number(val/price).toFixed(2))
             
           setAmo()
        })


 const setAmo  = () =>{
        const {mv} = trT()
         let tot = 0

          $('#saRows tr').each(function(){
             const pos = Number($(this).data('pos')),
             saPrice = Number(mv?$(`#safrm_tank${pos}`).find('option:selected').data('saprice'):$(`#sa_pumpSt${pos}`).find('option:selected').data('saprice')),
             price = Number($(`#saPrice${pos}`).val()) || saPrice || 0,

             totT = Number($(`#totPrice${pos}`).val()) || 0,
             qtyT = Number(totT/price)
             tot+=totT

            //  $(`#saQty${pos}`).val(qtyT.toFixed(3))
             
          })

          $('#there_is_err').html('')

          $('#TotSaPrice').text(Number(tot).toLocaleString())
 }


const trT = () =>{
         const  rlen = $('#saRows').children('tr').length,
                lpos = $('#saRows').children('tr').last().data('pos'),
                mv = Number($('#sale_opt').val()) == 2

                return {lpos,rlen,mv}
}

   $('#addPubtn').click(function(){
      const {lpos,rlen,mv} = trT(),
           
            lsaQty = Number($(`#saQty${lpos}`).val()) || 0,
            frm = mv?Number($(`#safrm_tank${lpos}`).val())||0:Number($(`#sa_pumpSt${lpos}`).val())|| 0,
            pos = lpos + 1
            
            if(frm&&lsaQty){

                const tr = `
                        <tr data-pos=${pos} class="saRow" >
                            <td class="IndexNo" data-pos=${pos} >${rlen+1}</td>
                            <td  class="mx-1 sale_opt sale_opt1" ${mv?'hidden':''}  >
                                            
                            <select data-pos=${pos} data-filter="sa_pumpSt${pos}" id="dispe${pos}" class=" form-control DispensaSelector  bluePrint btn-sm"  >
                                ${$('#Pdispensa').html()}
                            </select>

                            </td>

                            <td  class="mx-1 sale_opt sale_opt1" ${mv?'hidden':''} >
                                    <select class="tr_pumpSt form-control pmpSelect  bluePrint btn-sm" 
                                           
                                            data-pos=${pos}
                                            name="sa_pumpSt${pos}" id="sa_pumpSt${pos}"  >
                                               ${$('#sa_pumpSt').html()}
                                            
                                    </select> 
                                            <div class="showError "></div>
                            </td>

                            <td  class="mx-1 sale_opt sale_opt2" ${!mv?'hidden':''} >
                                 <select class=" form-control bluePrint safrm_tank btn-sm" 
									
									 name="safrm_tank${pos}" data-pos=${pos} id="safrm_tank${pos}">
										${$('#safrm_tank').html()}
							  </select>
                            </td>

                            <td>
                                <span class="showFuel brown" id="showFuel${pos}">------</span>
                            </td>  
                            <td class=" sale_opt sale_opt1" ${mv?'hidden':''} >
                                <span class="fuel_disp bluePrint showAttend"  id="showAttend${pos}">------</span>
                            </td>  
                        <td>
                               <div class="input-group  " >                   
                                    <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                        <label class="mt-1 text-danger " for="saQty1"></label> 
                                    <div class="box-pointer d-inline "></div>
                                    </div>
                                    <input type="number" data-pos=${pos}   style="width: 150px;background-color: var(--whiteBg);color:var(--inputColor)" data-qty=1  step="0.00000001"   id="saQty${pos}" name="saQty${pos}"  class=" money-fomat btn-sm form-control  fuelSalesSet weight600">
                                </div>
                           
                        </td>      
                        <td>
                            
                                <div class="input-group  " >                   
                                    <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                        <label class="mt-1 text-danger " for="saPrice1"></label> 
                                    <div class="box-pointer d-inline "></div>
                                    </div>
                                    <input type="number" data-pos=${pos} data-price=1  style="width: 150px;background-color: var(--whiteBg);color:var(--inputColor)" step="0.01"  id="saPrice${pos}" name="saPrice${pos}"  class=" money-fomat btn-sm form-control fuelSalesSet weight600">
                                </div>
                        </td>                      
                    
                         <td>
                            <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                    <label class="mt-1 text-danger " for="saPrice1"></label> 
                                <div class="box-pointer d-inline "></div>
                            </div>
                            <input type="number" data-pos=${pos} step=0.001 id="totPrice${pos}" name="totPrice${pos}" data-tprice=1  class="form-control money-fomat btn-sm weight600 fuelSalesSet">
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
                $('#saRows').append(tr)
            }else{
              if(!frm){redborder(`#safrm_tank${lpos}`);redborder(`#sa_pumpSt${lpos}`)}
              if(!lsaQty)redborder(`#saQty${lpos}`)
            }

   })


   //Remove Row Btn ...........................//
$('body').on('click','.rowRemoveBtn',function(){

    const {rlen,lpos}= trT()
    if(rlen>1&&confirm(lang('Ondoa','Remove'))){
        let pos = Number($(this).parent('td').siblings('.IndexNo').last().text())
        $(this).parent('td').parent('tr').remove()

        setAmo()
        
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

$('#saveBtn').click(function(){
    const cust = Number($(this).data('cust')),
           url = '/salepurchase/fuelsales',
           {mv} = trT(),
           saDate = $('#sa_date').val(),
           cont = Number($('#containerSale').val()),
           rcvd = $('#Custom_driver').val(),
           phone = $('#Driver_phone').val(),
           vihecle = $('#vihecle_details').val(),
           arert = `<span class="mr-1" >
                        <svg xmlns="http://www.w3.org/2000/svg" width="1.2em" height="1.2em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-x-circle">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="15" y1="9" x2="9" y2="15"></line>
                        <line x1="9" y1="9" x2="15" y2="15"></line>
                        </svg>    
                    </span>`

           let err = 0 ,exceed = 0
           if(saDate&&(cont||!mv)&&rcvd&&vihecle){
             $('#loadMe').modal('show')
                const saDt = []
                $('#saRows tr').each(function(){
                        const pos = Number($(this).data('pos')),
                        saPrice = Number(mv?$(`#safrm_tank${pos}`).find('option:selected').data('saprice'):$(`#sa_pumpSt${pos}`).find('option:selected').data('saprice')),
                        price = Number($(`#saPrice${pos}`).val()) || saPrice || 0,
                        qty = Number($(`#saQty${pos}`).val()) || 0 ,
                        totAmo = Number($(`#totPrice${pos}`).val()) || 0 ,
                        tnk =  Number($(`#safrm_tank${pos}`).val()) || 0 ,
                        tnkQty = Number($(`#safrm_tank${pos}`).find('option:selected').data('qty')) || 0 ,
                        pmp = Number($(`#sa_pumpSt${pos}`).val()) || 0 
                        if((pmp&&!mv||tnk&&mv)&&qty){
                            saDt.push({
                                pos,price,qty,tnk,tnkQty,pmp,totAmo
                            })                            
                        }else{
                            err += 1
                            if(!pmp&&!mv)redborder(`#sa_pumpSt${pos}`)
                            if(!tnk&&mv)redborder(`#safrm_tank${pos}`)
                        }


                      })
                      
                      if(mv){
                        // /asess  tank qty if is there is enought qty for sales.....//
                         const  tnks =  [...new Set(saDt.map(s=>s.tnk))]
                         tnks.forEach(t=>{
                            const tnkDt =  saDt.filter(s=>s.tnk===t),
                                   tqty = tnkDt[0].tnkQty,
                                  saqty = tnkDt.reduce((a,b)=> a + Number(b.qty),0)
                                  if(tqty<saqty)exceed+=1

                                  tnkDt.forEach(tn=>{
                                     redborder(`#safrm_tank${tn.pos}`)
                                     redborder(`#saQty${tn.pos}`)
                                  })
                         })
                                 
                      }

                      if(!err&&!exceed){
                              const Data = {url,data:{saDt:JSON.stringify(saDt),cust,mv:Number(mv),saDate:moment(saDate).format(),cont,rcvd,phone,vihecle}},
                              sendIt = POSTREQUEST(Data)
                              sendIt.then(resp=>{
                                    $('#loadMe').modal('hide')
                                    hideLoading()
                                    const msg = lang(resp.msg_swa,resp.msg_eng)
                                        if(resp.success){
                                        toastr.success(msg, lang('Imefanikiwa','Success '), {timeOut: 2000});
                                        location.replace(`/salepurchase/viewFuelSales?i=${resp.id}`)
						    //  location.reload()
						}else{
								toastr.error(msg, lang('Haikufanikiwa','Error '), {timeOut: 2000});
					
						}
                              })
                      }else{
                       
                        if(err)$('#there_is_err').html(arert+lang('Hakikisha kila  sehemu muhimu imejazwa kikamilifu','make sure all required fields are fiiled correctly '))
                        if(exceed)$('#there_is_err').html(arert+lang('Kiasi cha mafuta kinachouzwa kimezidi kiasi halisi kilichopo kwenye tamk','The qty of fuel to be sold exceeded the actual tank fuel qty '))
                        }
           }else{
             if(!saDate)redborder('#sa_date')
             if(mv&&!cont)redborder('#containerSale')   
            //  if(phone='')redborder('#Driver_phone')
             if(vihecle=='')redborder('#vihecle_details')  
             if(rcvd=='')redborder('#Custom_driver')  
            $('#there_is_err').html(arert+lang('Hakikisha kila  sehemu muhimu imejazwa kikamilifu','make sure all required fields are fiiled correctly '))
           }
})