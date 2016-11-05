/* table-adaptative.js ======================================== */
/* ============================================================ */


$(document).ready(function() {

	/* TABLE RESPONSIVE SELECT MENU */	
	$('.btn-table-adaptative-select-menu').click(function(){
		
		var menu = $(this).closest('table').find('.table-adaptative-select-menu');
		
		if (!menu.hasClass('animation')) {
		
			if (!menu.hasClass('in')) {		
				menu.fadeIn('fast', function(){
					menu.addClass('in');
					menu.removeClass('animation');
				});
				menu.addClass('animation');
			} else {
				menu.fadeOut('fast', function(){
					menu.removeClass('in');
					menu.removeClass('animation');
				});
				menu.addClass('animation');
			}
		}
	});
	
	// CLOSE TABLE RESPONSIVE SELECT MENU
	$('.table-adaptative-select-menu a').click(function(){
		
		var menu = $(this).closest('table').find('.table-adaptative-select-menu');
		
		menu.fadeOut('fast', function(){
			menu.removeClass('in');
			menu.removeClass('animation');
		});
	});
	
	$('.btn-table-subitem').click(function(e){
		$(this).toggleClass('collapsed');
		$(this).closest('table').find('tbody').toggleClass('hide');
		e.preventDefault();
	});
	
});

// CLOSE TABLE RESPONSIVE SELECT MENU
$(document).click(function(e) {
	var container = $(".table-adaptative-select-menu");
	if (!container.is(e.target) // if the target of the click isn't the container...
	&& container.has(e.target).length === 0 // ... nor a descendant of the container...
	&& container.hasClass("in")) // ... and is open
	{
		container.fadeOut('fast');
		container.removeClass('in');
	}
});