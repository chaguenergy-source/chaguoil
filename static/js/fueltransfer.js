var TR_TANKS=[], STA_TANKS =[], DISPENSA=[],PUMPS=[]

const getdata = ()=>{
    $('#loadMe').modal('show')
     const data={data:{},url:'/salepurchase/getStationData'},
           sendIt = POSTREQUEST(data)

           sendIt.then(resp=>{
              $('#loadMe').modal('hide')
              hideLoading()
              TR_TANKS = resp.tr_tanks,
              STA_TANKS = resp.sta_tanks,
              DISPENSA = resp.disp
              PUMPS = resp.pumps
            //   console.log(resp);
           })

}

getdata()

$('#saveTrBtn').click(function(){
    
    const url = '/salepurchase/fueltranfer',
           {mv,Sto,cont,tr,pmp,tr_tank,trqty} = trT(),
           otherSto = $('#otherStorageInput').val(),
           op = Number($('#TankSupVisor').val()),
           desc = $('#TransRemarks').val(),
           gvenTo = $('#fuelGivenTo').val(),
           tr_date = $('#tr_date').val(),
           tr_dt = []
           let err = 0

           $(`${tr} tr`).each(function(){
               const pos = $(this).data('pos'),
                     tnk = Number($(`#${tr_tank}${pos}`).val())||0,
                     t_fuel = Number($(`#${tr_tank}${pos}`).find('option:selected').data('fuel'))||0,
                     trpmp = Number($(`#${pmp}${pos}`).val())||0,
                     p_fuel = Number($(`#${pmp}${pos}`).find('option:selected').data('fuel'))||0,
                   
                     tqty = Number($(`#${trqty}${pos}`).val())||0

                     if((tnk || (Sto && otherSto!=''))&&trpmp&&tqty){
                        tr_dt.push({
                            tnk,trpmp,tqty,pos,t_fuel,p_fuel
                        })
                     }else{
                        if(tnk||trpmp||tqty){
                            if(!tnk)redborder(`#${tr_tank}${pos}`)
                            if(!trpmp)redborder(`#${pmp}${pos}`)
                            if(!tqty)redborder(`#${trqty}${pos}`)
                             err += 1  
                            
                        }
                     }


           })
           
           let rednt = 0
            // Check whether the same tank is added fuel from different fuel pumps (fuel mixing to one tank)
            tr_dt.forEach(t=>{
                const tnki = tr_dt.filter(r=>r.tnk===t.tnk),
                    tlen = tnki.length
                    if(tlen>1){
                        const t_pl = tnki.filter(r=>r.p_fuel===t.p_fuel),
                              t_plen = t_pl.length   
                              
                        if((t_plen!=tlen) && !Sto){
                     
                            err+=1
                            rednt+=1

                            tnki.forEach(r=>{
                                redborder(`#${tr_tank}${r.pos}`);
                                redborder(`#${pmp}${r.pos}`)
                            })
                    }

                    

                    }
            })

            $('#fuelRed').prop('hidden',!rednt)
            // $('#saveTrBtn').prop('hidden',!err)

           

            if(tr_date&&op&&!err&&((mv&&gvenTo&&(cont || (Sto && otherSto!=''))  )||!mv)){
                       $('#loadMe').modal('show')
                        const data = {
                            data:{mv,tr_date:moment(tr_date).format(),Sto,cont,otherSto,op,desc,gvenTo,tr_dt:JSON.stringify(tr_dt)},
                            url
                        },
                        sendIt = POSTREQUEST(data)
                        sendIt.then(resp=>{
                             $('#loadMe').modal('hide')
                             hideLoading()
                             const msg = lang(resp.swa,resp.eng)
                             if(resp.success){
                                   toastr.success(msg, lang('Imefanikiwa','Success '), {timeOut: 2000})
                                   location.replace(`/salepurchase/viewTransfer?i=${resp.id}`)
                             }else{
                                toastr.error(msg, lang('Haikufanikiwa','Error '), {timeOut: 2000})
                             }
                        })
            }else{
                if(!tr_date)redborder('#tr_date')
                if(!op)$('#TankSupVisor').selectpicker('setStyle','redborder')  
                if((mv&&!Sto)&&!cont) $('#containerTr').selectpicker('setStyle','redborder') 
                if(mv&&!gvenTo)$('#fuelGivenTo').selectpicker('setStyle','redborder')      
            }
           
                    //  console.log(tr_dt);
    

           
})

$('#containerTr').change(function(){
     const cont = Number($(this).val()),
            gvn=Number($(this).find('option:selected').data('by'))||0;
            if(gvn){$('#fuelGivenTo').selectpicker('val',gvn);$('#fuelGivenTo').selectpicker('refresh');$('#fuelGivenTo').selectpicker('setStyle','bluePrint')}
            $('.Mv_Tanks').prop('disabled',!cont)
            
            $('.Mv_Tanks option[data-val!=0]').hide()
            $(`.Mv_Tanks option[data-tank=${cont}]`).show()
            $(`.Mv_Tanks`).val(0)
           $(this).selectpicker('setStyle', 'bluePrint')
           
})


// StationTrRow MovTrRow tr_pumpSt1 tr_pumpM1

const trT = () =>{
         const  mv=Number($('#moveTankAdj').hasClass('active')),
                tr = mv?'#MovTrRow':'#StationTrRow',
               
                pmp = mv?'tr_pumpM':'tr_pumpSt',
                rlen = $(tr).children('tr').length,
                cont =  Number($('#containerTr').val()),
                lpos = $(tr).children('tr').last().data('pos'),
                Sto = Number($('#OtherStorage').prop('checked')),
                trqty = mv?'mvqty':'stqty',
                tr_tank = mv?'Mv_Tanks':'pmp_Tanks'


                return {tr,rlen,mv,cont,Sto,pmp,lpos,trqty,tr_tank}
}

$('#AddTransfrow').click(function(){

        const {tr,rlen,mv,lpos,pmp,cont,Sto,trqty,tr_tank} = trT(),
             tanks = mv?TR_TANKS.filter(t=>t.tank_id===cont):STA_TANKS,
             pos = lpos + 1,
              
             lpump = Number($(`#${pmp}${lpos}`).val()) || 0,
             lqty = Number($(`#${trqty}${lpos}`).val()) || 0,
             ltank = Number($(`#${tr_tank}${lpos}`).val()) || 0

            let  tanks_opt,disp_opt,pmp_opt = ''
            tanks?.forEach(t=>{
                tanks_opt+=`<option data-val="${t.id}" data-pos=${pos} data-fname="${t.Fname}" data-qty=${t.qty} data-fuel="${t.Fuel}" value=${t.id}>${t.name}</option>`
                 
            })
            DISPENSA?.forEach(d=>{
                disp_opt+=` <option class="bluePrint" data-disp="${d.station_id}" value=${d.id}>${d.dis_name}</option> `
            })

            PUMPS?.forEach(p=>{
               pmp_opt+=`<option class="bluePrint" data-pos=${pos} data-fname="${p.Fname}" data-fuel="${p.Fuel}" data-tank="${p.tank_id}" data-station="${p.station_id}" data-incharge="${p.AF_name} ${p.AL_name}" data-incharger="${p.Incharge_id}" value=${p.id}>${p.disp_name} ${p.name}</option>
`
            })

            // mvqty1  stqty1 InchargeSt1 pmpSelect  data-incharge data-incharger
                   
            const tr_row = `
              <tr data-pos=${pos} >
                        <td class="IndexNo" data-pos=${pos} >${rlen+1}</td>
                            <td class="mx-1 ${mv?'containerStorage':''} ${tr_tank} "  ${mv&&Sto?'hidden':''}  >
                                <select class="tr_tanks Mv_Tanks form-control btn-sm bluePrint  " 
                                 data-pos=${pos}
                                name="${tr_tank}${pos}" id="${tr_tank}${pos}">
                                <option value=0 data-val=0 selected>-----------</option>
                               ${tanks_opt}
                         </select>
                            </td>

                            <td  class="mx-1"  >
                                            
                            <select data-filter="${pmp}${pos}" data-pos=${pos} id="dispe12${pos}" class=" btn-sm form-control DispensaSelector  bluePrint btn-sm"  >
                                <option value=0 selected>-----------</option>
                                ${disp_opt}
                            
                            </select>

                            </td>

                            <td  class="mx-1"  >
                                    <select data-pos=${pos} class="${pmp} form-control pmpSelect bluePrint btn-sm" 
                                         
                                            
                                            name="${pmp}${pos}" id="${pmp}${pos}">
                                                <option data-station=0 value=0 selected>-----------</option>
                                                ${pmp_opt}
                                            
                                            </select> 
                                           <div class="showError "></div>
                            </td>
                            <td class="AttendantName text-center text-capitalize bluePrint" ></td>
                           
                        
                                <td>

                                        <div class="input-group  pt-2" style="width:150px" >
                                            <div class="show_curency_inline show_curency position-absolute   px-3" style="display: none ;">
                                                <label class="mt-1 text-danger " for="FuelPriceTotal"></label> 
                                            <div class="box-pointer d-inline "></div>
                                            </div>
                                            <input type="number"   style="width: 150px;background-color: var(--whiteBg);color:var(--inputColor)"  step="0.01"  id="${trqty}${pos}"  class="${trqty} made-input money-fomat AllAdjTanks weight600">
                                        </div>                             
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
             if(!mv||(mv&&(cont||Sto))){
                if(lpump&&lqty&&(ltank||(Sto&&mv))){
                    $(tr).append(tr_row)
                }else{
                    if(!lpump)$(`#${pmp}${lpos}`).addClass('redborder')
                    if(!lqty)$(`#${trqty}${lpos}`).addClass('redborder')
                    if(!(ltank||Sto))$(`#${ltank}${lpos}`).addClass('redborder')   
                }
               
             }else{
               if(!cont&&mv)$('#containerTr').selectpicker('setStyle','redborder')
             }
             
        
})

$('body').on('change','.tr_tanks',function(){
     const pos = Number($(this).data('pos')),
           fuel = Number($(this).find('option:selected').data('fuel'))||0,
           {mv,pmp} = trT(),
           tank = Number($(this).val())||0

           if(!mv){
            $(`#${pmp}${pos} option`).hide()
            $(`#${pmp}${pos} option[data-fuel=${fuel}]`).show()
            $(`#${pmp}${pos} option[data-tank=${tank}]`).hide()              
           }
           MixCheck(pos)
})

$('body').on('change','.pmpSelect',function(){
    const at_id = Number($(this).find('option:selected').data('incharger')) || 0,
         att_name = $(this).find('option:selected').data('incharge'),
       
         pos = Number($(this).data('pos'))
       
     
         MixCheck(pos) 

         $(this).parent('td').siblings('.AttendantName').text(at_id?att_name:'------')

         
})


const MixCheck = pos => {
    const {tr_tank,pmp,mv} = trT(),
    tnk = Number($(`#${tr_tank}${pos}`).val())||0,
    t_fuel = Number($(`#${tr_tank}${pos}`).find('option:selected').data('fuel')),
    p_fuel = Number($(`#${pmp}${pos}`).find('option:selected').data('fuel'))||0,
    t_fuelName = $(`#${tr_tank}${pos}`).find('option:selected').data('fname'),
    tqty = Number($(`#${tr_tank}${pos}`).find('option:selected').data('qty')) || 0,
    ptnk = Number($(`#${pmp}${pos}`).find('option:selected').data('tank')) || 0,
    err = t_fuel!=p_fuel && tqty > 0 && mv && tnk && ptnk ?`
      <div class="d-flex ">
          <div class="px-1 brown" >
             <svg xmlns="http://www.w3.org/2000/svg" width="1.2em" height="1.2em" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather mx-1 feather-alert-triangle">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
          <div  >
            <span class="smallerFont " >${lang('Kwenye tanki tayari kuna','In the Tank, already there is ')} <span class="weight600 brown"> ${Number(tqty.toFixed(2)).toLocaleString()} <span class="text-primary"> LTRS</span></span>  <span class="brown"> ${t_fuelName}</span> </span>
          </div>
      </div>
       
    `:''
  

    $(`#${pmp}${pos}`).siblings('.showError').html(err)

}

//Remove Row Btn ...........................//
$('body').on('click','.rowRemoveBtn',function(){

    const {tr,rlen,lpos}= trT()
    if(rlen>1&&confirm(lang('Ondoa','Remove'))){
        let pos = Number($(this).parent('td').siblings('.IndexNo').last().text())
        $(this).parent('td').parent('tr').remove()
        
       if(pos!=lpos){
            $('.IndexNo').each(function(){
                const Ipos = Number($(this).text())
                console.log({Ipos,pos});
                if(Ipos>pos){
                    $(this).text(pos)
                    pos+=1
                }
            })        
       }



    }
})