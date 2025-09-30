
var kata = [], vijiji = [], valid = 0,validmail = false
//confirmation on register


$('#email').keyup(function(){
	var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
	    mail=$(this).val();
		if(mail.match(mailformat)){
			validmail = true
			$(this).removeClass('redborder')
		}else{
			validmail = false
			$(this).addClass('redborder')
		}
checkValidity()
})

function checkValidity(){
	const f_name=$('#f_name').val(),
	      l_name = $('#l_name').val(),
	
		 // mail = $('#email').val(),
		  pconfirm = $('#passwordConfirm').val(),
		  pwd = $('#password').val(),
		  country = $('#countries').val(),
		company_name = $('#company_name').val(),
		phone1 = $('#phone1').val(),
		company_email = $('#company_email').val(),

		  city = $('#city').val(),
		  p_code = $('#Postal').val(),
		  address = $('#address').val(),
		//   accept = $('#TermsCondition').prop('checked'),
		  all = {
			f_name,
			l_name,
			pconfirm,
			pwd,
			country,
			city,
			p_code,
			address,
			// accept,
			validmail,
			valid,
			company_email,
			phone1,
			company_name
		  }



        //   console.log(all)

		if (
			f_name !== '' &&
			l_name !== '' &&
			city !== '' &&
			address !== '' &&
			p_code !== '' &&
			country !== "0" &&
			validmail &&
			pconfirm === pwd &&
			valid >= 60 &&
			company_name !== '' &&
			phone1 !== '' &&
			company_email !== ''
		) {
			$('#submitBtn').prop('disabled', false)
		} else {
			$('#submitBtn').prop('disabled', true)
		}
}

$('body').on('click','#TermsCondition,#Male,#Female', function(){
	checkValidity()
})

$('#password').keyup(function () {  
	$('#strengthMessage').html(checkStrength($(this).val()))  
	let cpwd = $('#passwordConfirm').val()
	     if(cpwd!=''&& $(this).val()!=cpwd){
			$('#passwordConfirm').addClass('redborder')
		 }else{
			$('#passwordConfirm').removeClass('redborder')
		 }
	    checkValidity()

})  
$('.form-control').keyup(function () {  
	
	    checkValidity()

})  

// $('#TermsCondition,#countries').change(function () {  
// 	    checkValidity()

// })  



function checkStrength(password) {  
	var strength = 0  

	// if (password.length < 6) {  
	// 	$('#strengthMessage').removeClass()  
	// 	$('#strengthMessage').addClass('Short')
	// 	$("#changepwd").prop("disabled",true) 

	// 	return lang('Dhaifu mno!','very weak !')  
	// }  


	if (password.length >= 6) strength += 1  
	// If password contains both lower and uppercase characters, increase strength value.  
	if (password.match(/([a-z].*[A-Z])|([A-Z].*[a-z])/)) strength += 1  
	// If it has numbers and characters, increase strength value.  
	if (password.match(/([a-zA-Z])/) && password.match(/([0-9])/)) strength += 1  
	// If it has one special character, increase strength value.  
	if (password.match(/([!,%,&,@,#,$,^,*,?,_,~])/)) strength += 1  
	// If it has two special characters, increase strength value.  
	if (password.match(/(.*[!,%,&,@,#,$,^,*,?,_,~].*[!,%,&,@,#,$,^,*,?,_,~])/)) strength += 1  
	// Calculated strength value, we can return messages  
	// If value is less than 2  


	const strong = strength * 100/5
    let txt = `` 
	
	if (strong <= 20 ) {  
		$('#strengthMessage').removeClass()  
		$('#strengthMessage').addClass('Short') 
		$("#changepwd").prop("disabled",false) 
        txt = lang('Dhaifu mno...!','Very Weak... !')
		}else if(strong == 40){
			$('#strengthMessage').removeClass()  
			$('#strengthMessage').addClass('weak') 
			$("#changepwd").prop("disabled",false) 
			txt = lang('Dhaifu... !',' Weak... !')	  

	   } else if (strong == 60) {  

		$('#strengthMessage').removeClass()  
		$('#strengthMessage').addClass('Good') 
		$("#changepwd").prop("disabled",false) 
		txt = lang('Angalau... !','At least... !') 

	   }else if(strong == 80){
        $('#strengthMessage').removeClass()  
		$('#strengthMessage').addClass('Strong') 
		$("#changepwd").prop("disabled",false) 
		txt = lang('Makini... ','Strong... ') 


	} else if(strong == 100){  

		$('#strengthMessage').removeClass()  
		$('#strengthMessage').addClass('Strong')  
		$("#changepwd").prop("disabled",false) 

		txt = lang('Makini Zaidi... ','Very Strong... ')
		
	}  

	valid = strong
    
	$('#pwdSign').css('width',(strong<=20?20:strong)+'%')
	$('#pwdSign').removeClass()
	$('#pwdSign').addClass(`Bg${strong>=80?80:strong<=20?20:strong}`)




	return txt
	
}  

$('#submitBtn,#sendMailBtn').click(function(){
	const mail = $('#email').val(),
	      mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,
		  pwd = Number($('#email').data('pwd')) || 0
 
		  if(mail.match(mailformat)){
			const dt={
				data:{
					mail,
					pwd
				},
				url:'/confirmMail'
			},
			kichwa = 0
			sendData = POSTREQUEST(dt)
			$('#loadMe').modal('show')
            // console.log(dt)   
			sendData.then(response=>{
				
				if(response.success){
					
					msg = lang('Tafadhari andika namba ya uthibitisho iliyotmwa kupitia ','Please write verification code sent to ')+`: <u class="weight500 darkblue"> <i>${response.mail}</i></u>`
					$('#loadMe').modal('hide')
					
					// alert(response.num)

					$('#email').data('valu',response.id)
					

					$('#ConfirmMailModal').modal('show')
					$('#mailtoConfirn').html(msg)
					countDown()
				}else{
					

					toastr.error(lang(response.msg_swa,response.msg_eng), lang('Haukufanikiwa','Error '), {timeOut: 2000});
                    $('#loadMe').modal('hide')
					hideLoading()
				} 
               $('#loadMe').modal('hide')
			   hideLoading()

			}).fail((jqXHR, exception)=>{
				failRequest(jqXHR, exception)
			})
		  }else{
			redborder('#mail')
		  }
	      
})


$('body').on('click','#tumabtn',function(){
	const f_name=$('#f_name').val(),
	      l_name = $('#l_name').val(),
		 
		  mail = $('#email').val(),
		  pwd = $('#password').val(),
		  country = $('#countries').val(),
		
			company_name = $('#company_name').val(),
			phone1 = $('#phone1').val(),
			company_email = $('#company_email').val(),
			phone2 = $('#phone2').val(),
			

		  city = $('#city').val(),
		  p_code = $('#Postal').val(),
		  address = $('#address').val(),
		//   accept = $('#TermsCondition').prop('checked'),
		  code = $('#emailCheck').val(),

		  dt = {
			data:{
			f_name,
			l_name,
			pwd,
			country,
			city,
			p_code,
			address,
			code,
			mail,
			company_name,
			phone1,
			company_email,
			phone2
			},
			url:'/register'
		  }
		  $('#confirmMailSpiner').prop('hidden',false)
		  const senddt = POSTREQUEST(dt)
		  senddt.then(resp=>{
			
			if(resp.success){
				clearTimeout(timerI)
				$('#the_phone').data('val',resp.id)
				$('#confirmMailSpiner').prop('hidden',true)
				$('#ConfirmMailModal').modal('hide')
				// $('#ConfirmPhoneModal').modal('show')
				location.replace('/userdash')


			} else{
			   $('#confirmMailSpiner').prop('hidden',true)
			   toastr.error(lang(resp.msg_swa,resp.msg_eng), lang('Haukufanikiwa','Error '), {timeOut: 5000});

			}
              $('#loadMe').modal('hide')
			  hideLoading()

		  }).fail((jqXHR, exception)=>{
			failRequest(jqXHR, exception)
		})



		  

})

$('body').on('click','#sendPhone',function(){
	
	
	const phone = $('#the_phone').val(),
	code = Number($('#countries').val())
	if(phone.length==9){
		$('#confirmphoneSpiner').prop('hidden',false)
		dt = {
			data:{
				phone,
				code
			},
			url:'/confirmMail'
			
		  },
		  sendIt = POSTREQUEST(dt)
		  sendIt.then(resp=>{
			if(resp.success){
				$('#confirmphoneSpiner').prop('hidden',true)
				// alert(resp.num)
				  countDown()
				$('#confirmPhone').show(300)
			}
		  })
	}else{
		redborder('#the_phone')
		$('#confirmphoneSpiner').prop('hidden',true)
	}





})

$('body').on('click','#tumabtnPhone',function(){
	$('#PhoneConfirmSpinner').prop('hidden',false)
	const code=$('#PhoneCheck').val(),
	      val =  $('#the_phone').data('val'),
		  mail = $('#email').val(),
		  phone = $('#the_phone').val(),
		  dta={
			data:{
				code,
				val,
				mail,
				phone
			},
			url:'/register2'
		  },
	
		  sendThedt = POSTREQUEST(dta)

		  sendThedt.then(resp=>{
			$('#PhoneConfirmSpinner').prop('hidden',true)
			if(resp.success){
				location.replace('/userdash')
			}else{
				toastr.error(lang(resp.msg_swa,resp.msg_eng), lang('Haukufanikiwa','Error '), {timeOut: 5000});
	
			}
		  }).fail((jqXHR, exception)=>{
			failRequest(jqXHR, exception)
		})

})

function failRequest(jqXHR, exception){
	$('#loadMe').modal('hide')
	if (exception === 'timeout' ||  jqXHR.status === 0) {
		
		toastr.error(lang("Tatitizo la mtandao tafadhari jaribu tena","Network error please try again"), lang('Haukufanikiwa','Error '), {timeOut: 7000});

	}
$('#loadMe').modal('hide')
hideLoading()
			
}

function countDown(){
	let cnt = 60
    
	function timer(){
		cnt=cnt-1
       

         $('.downCounter').text(cnt<10?'0'+cnt:cnt)
		if(cnt>0){
			timerI = setTimeout(timer, 1000); 
		}else{
			stop()
		} 
         
	}


	function stop(){
		if($("#ConfirmPhoneModal").data('bs.modal')?._isShown){
		    $('#confirmPhone').hide(100)
			$('#PhoneCheck').val('')
		}else{
				$('#emailCheck').val('')
				$('#loadMe').modal('hide')
				hideLoading()
				$('#ConfirmMailModal').modal('hide')
				$('#confirmMailSpiner').prop('hidden',true)
		}
		

		toastr.error(lang("Muda wa uhakiki umeisha tafadhari kusanya tena","The confirmation duration expired plese resubmit the form"), lang('Muda Umeisha','Time Out '), {timeOut: 7000});
        
		clearTimeout(timerI)
	}

    timer()
}

//PASWORD RESET PURPOSE ..............................................//
$('#pwdResetForm').submit(function (e) { 
	e.preventDefault();

    const pwd = $('#password').val(),
	      conf = $('#passwordConfirm').val()
		  

		  if(pwd==conf && valid >=60 ){
			$('#loadMe').modal('show')
			const  dtSend = {
				data:{pwd},
				url:'/changePwd'
			},
			sendThen = POSTREQUEST(dtSend)
			sendThen.then(resp=>{
				if(resp.success){
                  toastr.success(lang(resp.msg_swa,resp.msg_eng), lang('Imefanikiwa','Success '), {timeOut: 2000});
				  location.replace('/userdash')
				}else{
					toastr.error(lang(resp.msg_swa,resp.msg_eng), lang('Haukufanikiwa','Error '), {timeOut: 5000});

				}
				$('#loadMe').modal('hide')
				hideLoading()
			})
              
		  }



	
});