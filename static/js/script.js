const allSideMenu = document.querySelectorAll('#sidebar .side-menu.top li a');

allSideMenu.forEach(item=> {
	const li = item.parentElement;

	item.addEventListener('click', function () {
		allSideMenu.forEach(i=> {
			i.parentElement.classList.remove('active');
		})
		li.classList.add('active');
	})
});




// TOGGLE SIDEBAR
const menuBar = document.querySelector('#content nav .bx.bx-menu');
const sidebar = document.getElementById('sidebar');

menuBar.addEventListener('click', function () {
	sidebar.classList.toggle('hide');
})







const searchButton = document.querySelector('#content nav form .form-input button');
const searchButtonIcon = document.querySelector('#content nav form .form-input button .bx');
const searchForm = document.querySelector('#content nav form');

searchButton.addEventListener('click', function (e) {
	if(window.innerWidth < 576) {
		e.preventDefault();
		searchForm.classList.toggle('show');

		// if(searchForm.classList.contains('show')) {
		// 	searchButtonIcon.classList.replace('bx-search', 'bx-x');
		// } else {
		// 	searchButtonIcon.classList.replace('bx-x', 'bx-search');
		// }
	}
})





if(window.innerWidth < 768) {
	sidebar.classList.add('hide');
} else if(window.innerWidth > 576) {
	// searchButtonIcon.classList.replace('bx-x', 'bx-search');
	searchForm.classList.remove('show');
}


window.addEventListener('resize', function () {
	if(this.innerWidth > 576) {
		// searchButtonIcon.classList.replace('bx-x', 'bx-search');
		searchForm.classList.remove('show');
	}
})






$('body').on('click','.tab_show',function(){
	$($(this).data('show')).siblings('.tab_div').hide()
	$($(this).data('show')).fadeIn(600)
  if($(this).hasClass('gotop')){
   topslider.top()
  
  }
  
  })

  
  
//tab animations

$(".tabs-animated a").click(function() {

	var position = $(this).parent().position();
	var width = $(this).parent().width();
  
	$(".floor").css({
	  "left": position.left, 
	  "width": width
	});
  
  });
  
  
  function getnavp(){
  var actWidth = $(".tabs-animated").find(".active").parent("li").width();
  var actPosition = $(".tabs-animated .nav-item .active").position();
  
  $(".floor").css({
	"left": actPosition.left,
	"width": actWidth
  });
  
  
  
  // console.log(actPosition)
  }



  