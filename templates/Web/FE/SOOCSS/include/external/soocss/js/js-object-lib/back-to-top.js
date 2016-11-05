/* back-to-top.js ============================================= */
/* ============================================================ */

var lastScrollTop = $(window).scrollTop();
var hide_timeout;

$(document).ready(function(){

	addHTML();
	
	$('#back-to-top').click(function(e){
		$('html, body').animate({scrollTop:'0px'});
	});
	
	$(window).scroll(function(){
		setVisibility('500',lastScrollTop);
		lastScrollTop = $(window).scrollTop();
	});
	
	$('#back-to-top').hide();
	setVisibility(0,lastScrollTop);
	
});

function addHTML() {
	$('body').append('<div id="back-to-top" class="back-to-top" href="#"><i class="ci ci-chevron-up ci-2x mts"></i><div class="back-to-top-text">Top</div></div>');
}

function setVisibility(vel,lastScrollTop) {

	if (getEnv() == 'lg') {
		if ($(window).scrollTop() > 0) {
			$('#back-to-top').fadeIn(vel);
		} else {
			$('#back-to-top').fadeOut(vel);
		}
	} else {
		if ($(window).scrollTop() == 0) {
			$('#back-to-top').stop().fadeOut(vel);
		} else if (lastScrollTop - 50 > $(window).scrollTop()) {
			clearTimeout(hide_timeout);
			hide_timeout = setTimeout('timeout_trigger()', 3000);
			$('#back-to-top').fadeIn(vel);
		}
	}
}

function timeout_trigger() {
	$('#back-to-top').fadeOut(500);
}

function hideBackToTop() {
	$('#back-to-top').fadeOut(500);
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