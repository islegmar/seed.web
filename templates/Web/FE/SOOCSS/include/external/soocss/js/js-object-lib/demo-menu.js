$(document).ready(function() {
	$('.open-submenu').click(function(e) {
		$('.sub-head').toggleClass('open-sub');
		$('.open-submenu').toggleClass('active');
		$('.open-submenu > span.ci').toggleClass('ci-chevron-up');


	});
	$('.open-search').click(function(e) {
		$(this).parents('.d-table').next('.search-head').toggleClass('open');
		//$('.search-head').toggleClass('open');
		$(this).toggleClass('advanced-search-open');


	});
		$('.goto-rtl').click(function(e) {
			if ($('body').attr('dir') == 'rtl') {
				$('body').attr("dir", "ltr");
			}else {
				$('body').attr("dir", "rtl");

			}
	});

});
