const switchMode = document.getElementById('switch-mode');

switchMode.addEventListener('change', function () {
	const val = Number(this.checked),
	      data = {data:{val},url:'/darkMode'},
		  sendIt = POSTREQUEST(data)
		  sendIt.then(resp=>{
			const msg = lang(resp.swa,resp.eng)
			toastr.success(msg, lang('Imefanikiwa','Success '), {timeOut: 2000});
		  })

	if(val) {
		document.body.classList.add('dark');
	} else {
		document.body.classList.remove('dark');
	}

	

})