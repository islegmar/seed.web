/* sticky-header.js =========================================== */
/* ============================================================ */


$(document).ready(function(){

	// create the sticky-header element on the top of the page
	$('body').prepend('<div id="sticky-header"><div id="sticky-header-container" class="container"></div></div>');
	
	//load sticky objects to sticky-header
	loadStickyObjects();
	
	// show/hide sticky header objects on scroll
	$(window).scroll(function(e){
		setStickyObjectsVisibility();
	});
	
	// check which object must be sticky on load the page (example: if the user refreshes when the page is scrolled, some element should be sticky at the begining)
	setStickyObjectsVisibility();
});

function loadStickyObjects() {
	
	$.each($('.sticky'),function(i){
		$(this).addClass('sticky-'+i);
					
		var stickyObj = $(this).clone(true).removeClass('sticky').addClass('is-sticky').removeAttr('id');
		
		stickyObj.find('*').removeAttr('id');
		
		// if only a child of the object should be sticky (must has the class sticky-just-me), remove the rest of the children
		if (stickyObj.find('.sticky-just-me').length > 0) {
			$.each(stickyObj.children(),function(){
				if (!$(this).hasClass('sticky-just-me')) { 
					$(this).css('display','none'); 
				}
			});
		}
		
		//special case: table header - set columns widths
		if ($(this).is('table')) {
			stickyObj = setTableRowsWidths($(this),stickyObj);
		}
		
		stickyObj.hide();
		
		
		
		if ($(this).hasClass('page-title')) {
		
			$('#sticky-header').append("<div class='page-wrapper-heading'><div class='container'></div></div>");
			$('#sticky-header .page-wrapper-heading .container').append(stickyObj);
				
			
		} else {
		
			// check if the original element goes inside or outside the container, and then copy the element inside the sticky-header
			if ($(this).parents('.container').length != 0 ) {
				$('#sticky-header-container').append(stickyObj);	
			} else {
				if ($(this).is('header') || $(this).is('nav')) {
					$('#sticky-header').prepend(stickyObj);
				} else {
					$('#sticky-header').append(stickyObj);	
				}
			}
		
		}
		
		if ($(this).is('table')) {
			$('#sticky-header .sticky-'+i).wrap('<div class="hidden-xs"></div>');
		}
		
	});
	
}

function setStickyObjectsVisibility() {
	
	$.each($('.sticky'),function(i){
	
		if (getEnv() != 'xs' && $(this).hasClass('page-title') && $('.breadcrumb').length == 0) {
			
			if ( window.pageYOffset != 0 && (window.pageYOffset + $('#sticky-header').outerHeight()) > $(this).position().top + 38) {
				$('#sticky-header .sticky-'+i).show();
				if( (window.pageYOffset + $('#sticky-header').outerHeight() - $('#sticky-header .sticky-'+i).outerHeight(true)) - 38 <= ($(this).position().top) ) {
					$('#sticky-header .sticky-'+i).hide();
				}
			} else {
				$('#sticky-header .sticky-'+i).hide();
			}
		} else if (getEnv() != 'xs' && $(this).hasClass('page-title') && $('.breadcrumb').length > 0) {
			if ( window.pageYOffset != 0 && (window.pageYOffset + $('#sticky-header').outerHeight()) > $(this).position().top - 10) {
				$('#sticky-header .sticky-'+i).show();
				if( (window.pageYOffset + $('#sticky-header').outerHeight() - $('#sticky-header .sticky-'+i).outerHeight(true)) + 10 <= ($(this).position().top) ) {
					$('#sticky-header .sticky-'+i).hide();
				}
			} else {
				$('#sticky-header .sticky-'+i).hide();
			}
			
		} else if ( window.pageYOffset != 0 && (window.pageYOffset + $('#sticky-header').outerHeight()) > $(this).position().top) {
			if ($(this).hasClass('sticky-actions')) {
				if (anyTableCheckboxSelected()) {
					$('#sticky-header .sticky-'+i).show();
				}
			} else {
				$('#sticky-header .sticky-'+i).show();
			}
			if( (window.pageYOffset + $('#sticky-header').outerHeight() - $('#sticky-header .sticky-'+i).outerHeight(true)) <= ($(this).position().top) ) {
				$('#sticky-header .sticky-'+i).hide();
			}
		} else {
			$('#sticky-header .sticky-'+i).hide();
		}
	});
}

function removeElement(obj,i) {
	$('#sticky-header .sticky-'+i).remove();
	$(obj).removeClass('sticky-'+i);
}

function setTableRowsWidths(originalObj, stickyObj) {
	
	$.each(originalObj.find('th'),function(i){
		stickyObj.find('th').eq(i).css('width', $(this).outerWidth());
	});
	
	return stickyObj;
}

function anyTableCheckboxSelected() {
	var checkboxes = $('table.sticky tbody tr td:first-child input[type="checkbox"]');
	var anyChecked = false;
	$.each(checkboxes,function(){
		$.each(checkboxes,function(i){
			if ($(this).is(':checked')) {
				anyChecked = true;
			}
		});
	});
	return anyChecked;
}

function getEnv() {
    var envs = ['xs', 'sm', 'md', 'lg'];

    $el = $('<div>');
    $el.appendTo($('body'));

    for (var i = envs.length - 1; i >= 0; i--) {
        var env = envs[i];

        $el.addClass('hidden-'+env);
        if ($el.is(':hidden')) {
            $el.remove();
            return env
        }
    };
}