/* forms.js =================================================== */
/* ============================================================ */

// input file stuff
//
// gets the name of the file and writes it iniside the form-control div

$("input[type=file]").on("change", function() {
	var fileName = this.value.replace("C:\\fakepath\\", "");
	$(this).closest(".input-file").children(".input-file-name").text(fileName);
	$(this).closest(".input-file").children(".input-file-name").attr('title', fileName);
});

$(document).ready(function(){

	$.each($('.select-control'),function(){
		$(this).prepend('<span class="ci select-control-icon"></span>');
		$(this).prepend('<div class="select-label">' + $(this).find('select').val() + '</div>');
	});

	$('select').change(function(){
		$(this).closest('.select-control').find('.select-label').text($(this).val());
	});

	$(window).resize(function(){
		setSelectWidth();
	});

	setSelectWidth();

});

function setSelectWidth() {
	$.each($('.select-control select'),function(){

		$(this).css('width','auto');
		$(this).closest('.select-control').css('width','auto');

		var wParent = $(this).closest('.select-control').width();
		$(this).css('width',wParent);
		$(this).closest('.select-control').css('width',wParent);
		$(this).closest('.select-control').find('.select-label').css('width',wParent - 35);
	});
}