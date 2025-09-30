var TR_TANKS=[], STA_TANKS =[],OTHERF = []


const trT = () =>{
         const  mv=Number($('#moveTankAdj').hasClass('active')),
                trTo = mv?'#Mv_Tanks':'#pmp_Tanks',
                ToCont = Number($('#containerTrTo').val()) ,
                ToSt = Number($('#ToStation').val()) || 0,
                cont = Number($('#containerTr').val()) ,
                is_othr = Number($('#containerTr').find('option:selected').data('is_othr'))||0 ,
                is_tnk = Number($('#containerTr').find('option:selected').data('is_tr')) ||0,
                is_pu = Number($('#containerTr').find('option:selected').data('is_pu')) ||0,
                rlen = $('#trRows').children('tr').length,
                lpos = $('#trRows').children('tr').last().data('pos')

                return {mv,trTo,ToCont,cont,lpos,rlen,is_othr,is_tnk,is_pu,ToSt}
}

const getdata = ()=>{
    $('#loadMe').modal('show')
     const {is_pu,cont} = trT(), data={data:{tt:1,is_pu,cont},url:'/salepurchase/getStationData'},
           sendIt = POSTREQUEST(data)

           sendIt.then(resp=>{
              $('#loadMe').modal('hide')
              hideLoading()
              TR_TANKS = resp.tr_tanks,
              STA_TANKS = resp.sta_tanks
              OTHERF = resp.otherF
         
            //   console.log(TR_TANKS);
           })

}

getdata()

// FOR PURCHASE RECEIVE PURPOSE...................//
$('#ToStation').change(function(){
    const  St = Number($(this).val())
    $('#TankSupVisor option[data-val!=0]').hide()
    $(`#TankSupVisor option[data-intp=${St}]`).show()

    
    $('#TankSupVisor').val(0) 

    $('#TankSupVisor').prop('disabled',!St) 

    $('.pmp_Tanks option[data-val!=0]').hide()
    $(`.pmp_Tanks option[data-intp!=${St}]`).show()
    $(`.pmp_Tanks`).val(0)
    $(`.pmp_Tanks`).prop('disabled',!St)

})



$('.tankContainers').change(function(){
    
    const by = Number($(this).find('option:selected').data('by'))||0,
          inch  = $(this).data('set') ,
          flt = $(this).data('filter'),
          val = $(this).val(),
          isFr = Number($(this).data('frm')) || 0,
          {mv,cont,ToCont,trTo} = trT()

         //  console.log({val,flt});
         if(val){
            $(`.${flt}`).each(function(){
                 const pos = $(this).data('pos')
               
                  $(`#${flt}${pos} option[data-val!=0]`).hide()
                  $(`#${flt}${pos} option[data-cont=${val}]`).show()
                  $(this).val(0)
                  $(this).prop('disabled',false)
            })


            $(this).selectpicker('setStyle','bluePrint')
            
         }
         if(by){   
            
            $(inch).selectpicker('val',by);$(inch).selectpicker('refresh');$(inch).selectpicker('setStyle','bluePrint')
         }

         if(!isFr&&mv){
            $('.Mv_Tanks').each(function(){
               const pos  = Number($(this).data('pos')),

                    Frm = Number($(`#FrmTank${pos}`).val())||0 
               
                   
                    if(Frm){

                  
                      $(`${trTo}${pos} option[data-val=${Frm}]`).hide()
              
                   }
            })


         }

         if(isFr){
                const oth = Number($(this).find('option:selected').data('is_othr'))||0 ,
                  tnk = Number($(this).find('option:selected').data('is_tr')) ||0,
                  pu = Number($(this).find('option:selected').data('is_pu')) ||0
                
                  $('.fromTanks').prop('hidden',!tnk)
                  $('.incaseIsFuel').prop('hidden',tnk)

                  if(oth){
                     $('.incaseIsFuel').each(function(){
                        const pos = $(this).data('pos')
                              $(`#FuelOpt${pos} option[data-val!=0]`).hide()
                              $(`#FuelOpt${pos} option[data-tr=${val}]`).show()
                              
                     })
                  }
                        
         }

         
          
})

$('body').on('change','.trFr_tanks,.incaseIsFuel',function(){
    const pos = Number($(this).data('pos')),
          {mv,trTo,ToCont,is_tnk,ToSt,is_pu} = trT(),
          val = Number($(this).val()),
          fname = $(this).find('option:selected').data('fname'),
          fuel = $(this).find('option:selected').data('fuel')
        //   console.log({fuel,ToCont});
          if(val){
              if(is_tnk)$(`#showFuel${pos}`).html(`<span class="brown">${fname}</span>`)
              $(`${trTo}${pos} option[data-val!=0]`).hide()
              $(`${trTo}${pos} option[data-fuel=${fuel}]`).show()
              if(is_pu&&!mv)$(`${trTo}${pos} option[data-intp!=${ToSt}]`).hide()
              if(mv)$(`${trTo}${pos} option[data-cont!=${ToCont}]`).hide()
              $(`${trTo}${pos}`).val(0)
              
          }else{
                $(`#showFuel${pos}`).html(`-----`)
                $(`${trTo}${pos} option[val!=0]`).show()
          }

})


$('#AddTransfrow').click(function(){
   const {mv,trTo,ToCont,cont,lpos,rlen,is_tnk,is_pu,is_othr,ToSt} = trT(),
          FrmT =  TR_TANKS?.filter(t=>t.tank_id===cont),
          ToTnkMv = TR_TANKS?.filter(t=>t.tank_id===ToCont),
          ToTnkSt = is_pu?STA_TANKS.filter(s=>s.shell===ToSt):STA_TANKS,
          fflt = is_othr? d => d.tr === cont && d.othTr : d => d.tr === cont && d.pu, 
          otherFuel = !is_tnk?OTHERF.filter(fflt):[],
          pos = lpos + 1,
          ltrFr = Number($(`#FrmTank${lpos}`).val()) || 0,
          ltrTo =  Number($(`${trTo}${lpos}`).val()) || 0,
          lqtyb = Number($(`#stickB${lpos}`).val()) || 0,
          lqtya = Number($(`#stickA${lpos}`).val()) || 0,
          lFuel = Number($(`#FuelOpt${lpos}`).val()) || 0
         


          let trFr_opt = '',trTo_optMv = '',trTo_optSt = '',othF_opt = ''
         FrmT?.forEach(t=>{
                trFr_opt+=`<option data-val="${t.id}" data-cost=${t.cost} data-pos=${pos} data-fname="${t.Fname}" data-qty=${t.qty} data-fuel="${t.Fuel}" value=${t.id}>${t.name}</option>`
            })
         ToTnkMv?.forEach(t=>{
                trTo_optMv+=`<option data-val="${t.id}" data-cont=${t.tank_id} data-pos=${pos} data-fname="${t.Fname}" data-qty=${t.qty} data-fuel="${t.Fuel}" value=${t.id}>${t.name}</option>`
            })
         ToTnkSt?.forEach(t=>{
                trTo_optSt+=`<option data-val="${t.id}" data-intp=${t.Interprise_id} data-pos=${pos} data-fname="${t.Fname}" data-qty=${t.qty} data-fuel="${t.Fuel}" value=${t.id}>${t.name}</option>`
            })
          
          otherFuel?.forEach(t=>{
              othF_opt+=`<option value=${t.Fuel} data-val=${is_pu?t.id:0} data-cost=${t.cost} data-tr="${t.tr}" data-fname="${t.fname}" data-fuel="${t.Fuel}" data-qty="${t.qty}" data-pu=0 data-value=${t.Fuel}  >${t.fname}</option> `
          })  

            const tr_row = `
                 <tr data-pos=${pos} >
                    <td  class="IndexNo" data-pos=${pos} >${rlen+1}</td>
                        <td ${!is_tnk?'hidden':''} class="px-1 fromTanks"> 
                            <select class="trFr_tanks  FrmTank form-control btn-sm bluePrint  " 
                                data-pos=${pos} 
                                    name="FrmTank${pos}" id="FrmTank${pos}">
                                    <option value=0 data-value=0 selected>-----------</option>
                                     ${trFr_opt}
                            </select>
                        </td>
                        <td class="px-1">
                              <div id="showFuel${pos}" ${!is_tnk?'hidden':''}  class="fromTanks">------</div>  
                               <select name="FuelOpt1" ${is_tnk?'hidden':''}  id="FuelOpt${pos}" data-pos=${pos} class="form-control brown incaseIsFuel">
                                 <option value=0 data-value=0 selected>-----------</option>
                                 ${othF_opt}
                              </select>
                        </td>

                        <td class="px-1">
                               <select ${!mv?'hidden':''}  class="Mv_Tanks  form-control border  trOpt trOpt2 btn-sm bluePrint  " 
                                        data-pos=${pos} 
                                        name="Mv_Tanks${pos}" id="Mv_Tanks${pos}">
                                        <option value=0 data-value=0 selected>-----------</option>
                                        ${trTo_optMv}
                                </select>

                                <select ${mv?'hidden':''} class=" pmp_Tanks form-control btn-sm bluePrint trOpt trOpt1" data-pos=1
                                    name="pmp_Tanks${pos}" id="pmp_Tanks${pos}">
                                    <option value=0 data-val=0 selected>-----------</option>
                                   ${trTo_optSt}
                                </select>
                        </td>   
                        <td class="px-1">
                                <div class="input-group  " >                   
                                    <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                        <label class="mt-1 text-danger " for="FuelPriceTotal"></label> 
                                    <div class="box-pointer d-inline "></div>
                                    </div>
                                    <input type="number" data-pos=${pos}   style="width: 150px;background-color: var(--whiteBg);color:var(--inputColor)"  step="0.01"  id="stickB${pos}"  class="mvqty money-fomat btnm-sm form-control AllAdjTanks weight600">
                                </div>
                        </td>                 
                        <td class="px-2">
                            <div class="input-group  " >                   
                                    <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                        <label class="mt-1 text-danger " for="FuelPriceTotal"></label> 
                                    <div class="box-pointer d-inline "></div>
                                    </div>
                                    <input type="number" data-pos=${pos}   style="width: 150px;background-color: var(--whiteBg);color:var(--inputColor)"  step="0.01"  id="stickA${pos}"  class="mvqty money-fomat form-control btn-sm AllAdjTanks weight600">
                                </div>        
                        </td>                 
                        <td class="px-1">
                             <input type="text" readonly  id="mvqty${pos}" class="form-control btn-sm">
                        </td>         
                            <td class="pl-2" >
                                    <a type="button" data-pos=${pos} class="brown rowRemoveBtn text-danger" >
                                       <svg xmlns="http://www.w3.org/2000/svg" width="1.3em" height="1.3em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-minus-circle">
                                           <circle cx="12" cy="12" r="10"></circle>
                                           <line x1="8" y1="12" x2="16" y2="12"></line>
                                       </svg>
                                    </a> 
                               </td>         
                </tr>
            
            `
        
            if( ((is_tnk && ltrFr)||(!is_tnk&&lFuel)) &&ltrTo&&lqtya>lqtyb){
                  if(((mv&&ToCont) || !mv) && cont ){
                      $('#trRows').append(tr_row)
                  }else{
                     if(mv&&!ToCont) $('#containerTrTo').selectpicker('setStyle','redborder')
                     if(!cont) $('#containerTr').selectpicker('setStyle','redborder')
                  }
            }else{
               if(!ltrFr)redborder(`#FrmTank${lpos}`)
               if(!ltrTo)redborder(`${trTo}${lpos}`)
               if(!(lqtya>lqtyb)){redborder(`#stickB${pos}`);redborder(`#stickA${pos}`)}
            }
        
})
//Remove Row Btn ...........................//
$('body').on('click','.rowRemoveBtn',function(){

    const {tr,rlen,lpos}= trT()
    if(rlen>1&&confirm(lang('Ondoa','Remove'))){
        let pos = Number($(this).parent('td').siblings('.IndexNo').last().text())
        $(this).parent('td').parent('tr').remove()
        
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



$('body').on('keyup','.mvqty',function(){
    const pos = Number($(this).data('pos'))
     
       getQty({pos})
})

const getQty = dt =>{
     const {pos} = dt,
     bqty = Number($(`#stickB${pos}`).val())||0,
     aqty = Number($(`#stickA${pos}`).val())||0,
     mvQty = aqty>bqty?aqty - bqty:0
     $(`#mvqty${pos}`).val(Number(mvQty).toLocaleString())
     
}


$('#saveTrBtn').click(function(){
    
    const url = '/salepurchase/saveReceive',
           {mv,trTo,ToCont,cont,is_othr,is_pu,is_tnk,ToSt} = trT(),

          
           op = Number($('#TankSupVisor').val()),
           desc = $('#tr_remarks').val(),
         
           tr_date = $('#tr_date').val(),
           tr_dt = []

           let err = 0

           $(`#trRows tr`).each(function(){
               const pos = $(this).data('pos'),
                     tnk = is_pu?Number($(`#FuelOpt${pos}`).find('option:selected').data('val'))||0:Number($(`#FrmTank${pos}`).val())||0,
                     tqty = is_tnk?Number($(`#FrmTank${pos}`).find('option:selected').data('qty'))||0:Number($(`#FuelOpt${pos}`).find('option:selected').data('qty')) || 0,
                     
                     t_fuel = !is_tnk?Number($(`#FuelOpt${pos}`).val()):Number($(`#FrmTank${pos}`).find('option:selected').data('fuel'))||0,
                     fcost = is_tnk?Number($(`#FrmTank${pos}`).find('option:selected').data('cost'))||0:Number($(`#FuelOpt${pos}`).find('option:selected').data('cost')) || 0,
                     toTnk = Number($(`${trTo}${pos}`).val()),
                      
                     qtyB = Number($(`#stickB${pos}`).val())||0,
                     qtyA = Number($(`#stickA${pos}`).val())||0

                     if(( (is_tnk&&tnk) || ((is_othr || is_pu)&&t_fuel)) &&toTnk && qtyB < qtyA){
                        tr_dt.push({
                            tnk,t_fuel,toTnk,qtyB,qtyA,tqty,pos,fcost
                        })

                     }else{
                        
                            if(!tnk)redborder(`#FrmTank${pos}`)
                            if(!toTnk)redborder(`${trTo}${pos}`)
                            if(!(qtyA>qtyB)){redborder(`#stickB${pos}`);redborder(`#stickA${pos}`)}
                            if(!is_tnk && !t_fuel)redborder(`#FuelOpt${pos}`)
                             err += 1  
                            
                     
                     }


           })
           
           let rednt = 0,exceed = 0
            // Check whether the same tank is added fuel from different fuel pumps (fuel mixing to one tank)
            tr_dt.forEach(t=>{
                const tnki = tr_dt.filter(r=>r.toTnk===t.toTnk),
                      frmT = tr_dt.filter(r=>r.tnk===t.tnk),
                      frmF =  tr_dt.filter(r=>r.t_fuel===t.t_fuel),
                      frmTqty =is_tnk? Number(frmT[0]?.tqty)||0:Number(frmF[0]?.tqty) || 0,
                      trqty = frmF.reduce((a,b)=> a + Number(b.qtyA-b.qtyB),0),
                      tlen = tnki.length
                  
                    if(trqty>frmTqty){
                        err+=1
                        exceed+=1
                         redborder(`#mvqty${t.pos}`);
                         redborder(`#${is_tnk?'FrmTank':'FuelOpt'}${t.pos}`)
                    }   

                    if(tlen>1){
                        const FuelIn = tnki.filter(r=>r.t_fuel===t.t_fuel),
                              FuelInLen = FuelIn.length   
                              
                        if(FuelInLen!=tlen){
                     
                            err+=1
                            rednt+=1

                            tnki.forEach(r=>{
                                redborder(`#${trTo}${r.pos}`);
                                redborder(`#${is_tnk?'FrmTank':'FuelOpt'}${r.pos}`)
                            })
                    }

                    

                    }
            })

            $('#fuelRed').prop('hidden',!rednt)
            $('#fuelexceed').prop('hidden',!exceed)
            // $('#saveTrBtn').prop('hidden',!err)

           

            if( tr_date&&op&&!err && cont && (ToCont||!mv) ){
                       $('#loadMe').modal('show')
                        const data = {
                            data:{mv,ToSt,is_tnk,is_othr,is_pu,tr_date:moment(tr_date).format(),cont,ToCont,op,desc,tr_dt:JSON.stringify(tr_dt)},
                            url
                        }
                        // console.log(tr_dt);
                        , sendIt = POSTREQUEST(data)
                        sendIt.then(resp=>{
                             $('#loadMe').modal('hide')
                             hideLoading()
                             const msg = lang(resp.msg_swa,resp.msg_eng)
                             if(resp.success){
                                   toastr.success(msg, lang('Imefanikiwa','Success '), {timeOut: 2000})
                                   location.replace(`/salepurchase/viewFuelReceive?i=${resp.id}`)
                             }else{
                                toastr.error(msg, lang('Haikufanikiwa','Error '), {timeOut: 2000})
                             }
                        })
            }else{
                if(!tr_date)redborder('#tr_date')
                if(!op)$('#TankSupVisor').selectpicker('setStyle','redborder')  
                if((mv&&!trTo)&&!cont) $('#containerTr').selectpicker('setStyle','redborder') 
               
            }
           
                    //  console.log(tr_dt);
    

           
})