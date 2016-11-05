/* modal-side.js ============================================== */
/* ============================================================ */

$(document).ready(function(){
	
	var h;
	
	$('.input-comment').focus(function(){
		$(this).next('.btn-comment').fadeIn('fast');
		
		h = $('.input-comment').outerHeight();
		
		$(this).animate({
	        height: 100
	    }, "normal");
	    
	});
	
	$('.input-comment').focusout(function(){		
		$(this).next('.btn-comment').fadeOut('fast');
		
		$(this).animate({
	        height: h
	    }, "normal");
		
	});
	
	$('.btn-comment').hide();
	
});