$(document).ready(function(){
	msieversion();
});

function msieversion() {

	var ua = window.navigator.userAgent;
	var msie = ua.indexOf("MSIE ");
	
	if (msie > 0 || !!navigator.userAgent.match(/Trident.*rv\:11\./)) {      // If Internet Explorer, return version number
		var version = 'ie' + parseInt(ua.substring(msie + 5, ua.indexOf(".", msie)));
		$("html").addClass(version);
	} else {                 // If another browser, return 0
		
	}

	return false;
}