

      $('.chooseBdate').change(function(){
       

          checkTimeError()
                


      })



      function checkTimeError(){
           const DFrom = moment($('#dateFrom').val()),
                DTo = moment($('#dateTo').val()) || moment(),
                startbook = moment().add(40,'minutes'),
                start_at = moment(DFrom.format('YYYY-MM-DDT07:00')),
                end_at = moment(DFrom.format('YYYY-MM-DDT15:00')),
                stop_at = moment(DTo.format('YYYY-MM-DDT18:00')),
                dura = moment(DTo.format('YYYY-MM-DD')).diff(moment(DFrom.format('YYYY-MM-DD')),'days'),
                memb = Number($('#membersNum').val()),
                price = Number($('#membersNum').data('price')),
                valu = Number($('#membersNum').data('value'))




                let error = '',err = 0,drxn = 1

                 if(DTo.format()=='Invalid date' || DFrom.format()=='Invalid date' ){
                  err += 1
                  
                 }

                if(DFrom.format() < moment(startbook).format() ){
                   error+=`<li>
                   <span class="ml-1" >
                   <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-alert-triangle">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    </span>

                   the time must be starting at least <i>40minutes</i> from now 
                   
                   </li>
                   
                   `
                   err+=1
                }

                if(!(DFrom.format()>=start_at.format() && DFrom.format()<=end_at.format())){
                     error+=`<li>
                   <span class="ml-1" >
                   <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-alert-triangle">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    </span>

                      Booking must start from <i>07:00 to 15:00 </i> .
                   
                   </li>
                   
                   `
                   err+=1
                }

                if(DTo.format()>stop_at.format()){
                     error+=`<li>
                   <span class="ml-1" >
                   <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-alert-triangle">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    </span>

                      Booking must not exceed at <i>18:00</i> .
                   
                   </li>
                   
                   `

                   err+=1
                }

                if(DTo.diff(DFrom,'hours')<3){
                   error+=`<li>
                   <span class="ml-1" >
                   <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-alert-triangle">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>  
                     </span>      
                        
                   The Tour time must be at least <i>3hours</i> 
                   
                   </li>`


                 err+=1
                    
                }

                if(err==0){
                 
                      if(dura>1){
                        drxn = dura
                      }

                    const  totPrice = memb * price * drxn

                   $('#totalPrice').text(totPrice)
                   $('#totalDays').text(drxn)

                  //  console.log(totPrice,drxn)
                }



               //  console.log(err)




               //     console.log({
               //                   diff:DTo.diff(DFrom,'hours'),
               //                   DFrom:DFrom.format(),
               //                   DTo:DTo.format(),
               //                   is40:DFrom.format() < moment(startbook).format() ,
               //                   start:moment(startbook).format()
               //  })

                $('#timeerrors').html(error)

                data = {
                    err,
                    memb,
                    servId:valu,
                    DFrom:DFrom.format(),
                    DTo:DTo.format(),
                    drxn
                }

                return data

      }

      $('#membersNum').change(function(){
         checkTimeError()
      })
      $('#membersNum').keyup(function(){
         checkTimeError()
      })

      $('#paynow').click(function(){
         const check = checkTimeError(),
                dta = {
                  data:check,
                  url:'/services/booknow'
                }
               if(check.err==0){
                  loadMe.show()
                   const sendit = POSTREQUEST(dta)
                          sendit.then(resp=>{
                           loadMe.hide()

                            if(resp.success){
                              loadMe.hide()
                              toastr.success('Booking successfull', 'Success', {timeOut: 3000});
                                 
                              location.replace(`/services/ViewBooking?b=${resp.id}`)
                            }else{
                                toastr.error(resp.err, 'error', {timeOut: 4000});

                            } 
                            
                            loadMe.hide()
                          })
               }

               if(check.DTo=='Invalid date' || check.DFrom=='Invalid date' ){
                 let error=`<li>
                   <span class="ml-1" >
                   <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="feather feather-alert-triangle">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>  
                     </span>      
                        
                   Please Set Valid Date
                   
                   </li>`

                   $('#timeerrors').html(error)
               }

               
      })

      