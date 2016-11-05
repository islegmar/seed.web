/* input-auto.js =================================================== */
/* ============================================================ */

$(document).ready(function(){

	var number = 1;

	$('.input-auto .form-control').focus(function() {
		$(this).siblings('.input-auto-suggestion').html('Option' + number);
	});

});
