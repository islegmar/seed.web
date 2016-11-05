$( document ).ready(function() {

	// LTR & RTL buttons
	$("#btn_ltr").click(function() {
		$("body").attr("dir", "ltr");
		$("#btn_rtl").removeClass("hidden");
		$(this).addClass("hidden");
	});
	$("#btn_rtl").click(function() {
		$("body").attr("dir", "rtl");
		$("#btn_ltr").removeClass("hidden");
		$(this).addClass("hidden");
	});

	// Launch panel-spinner
	$("#btn_panel_spinner").click(function() {
		$("body").addClass("loading");
	});
	$(".panel-spinner, .panel-spinner *").click(function() {
		$("body").removeClass("loading");
	});

	// Load the README.md
	$("#readme-md").load("README.md", function() {

		var converter = new Showdown.converter();
		var txt = $("#readme-md").html();
		var html = converter.makeHtml(txt);
		$("#readme-md").html(html);
	});

	// Load the versions log if needed
	$("#ajax-log").load("log.md", function() {

		var converter = new Showdown.converter();
		var txt = $("#ajax-log").html();
		var html = converter.makeHtml(txt);
		$("#ajax-log").html(html);
		//$("#html_result").val(html.replace(/>/g, ">\n").replace(/</g, "\n<").replace(/\n{2,}/g, "\n\n"));
	});

	// Paint the code snippets
	/*$("pre.code-html").snippet("html",{style:"zellner", menu:true, collapse:true, clipboard:"/js/ZeroClipboard.swf", showMsg:"Show code",hideMsg:"Hide code"});
	$("pre.code-html-open").snippet("html",{style:"zellner", menu:true, collapse:false, clipboard:"/js/ZeroClipboard.swf"});
	$("pre.code-html-clean").snippet("html",{style:"zellner", menu:false, collapse:false});
	$("pre.code-css").snippet("css",{style:"zellner", menu:true, collapse:true, clipboard:"/js/ZeroClipboard.swf", showMsg:"Show code",hideMsg:"Hide code"});
	$("pre.code-css-open").snippet("css",{style:"zellner", menu:true, collapse:false, clipboard:"/js/ZeroClipboard.swf"});
	$("pre.code-css-clean").snippet("css",{style:"zellner", menu:false, collapse:false});*/

	/* TOGGLE */
	$('.toggle').click(function(){

		var down = hasClassWithString(this,'-down');
		var up = hasClassWithString(this,'-up');

		var id = $($(this).attr('data-target'));

		if (down || up) {
			if (!id.hasClass('collapsing')) {
				if (!id.hasClass('in')) {
					if ($(this).hasClass(down)) {
						$(this).removeClass(down).addClass(down.replace("-down", "-up"));
					}

				} else {
					if ($(this).hasClass(up)) {
						$(this).removeClass(up).addClass(up.replace("-up", "-down"));
					}
				}
			}
		}

	});
	function hasClassWithString(obj,str) {
		var classes = $(obj).attr('class').split(' ');
	    for (var i=0; i<classes.length; i++)
	    {
	        if (classes[i].indexOf(str) >= 0)
	        {
	            return classes[i];
	        }
	    }
	    return false;
	}

	$('.datepicker').each(function(){
		var input  = $(this);
		if(input[0].dataset['config']){
			var obj = input.data('config');
			$(this).datepicker(obj);
		}
	});

	/*$('#myModal').on('show.bs.modal', function(e){

		var functionAction = $(e.relatedTarget).data('action');
		console.log(functionAction);
		
		$(this).find('.modal-title').html(functionAction.title);
		$(this).find('.modal-body').html(functionAction.message);
		$(this).find('#btn_save').attr('onclick', functionAction.action);
		//functionAction();
	});*/


});

/* Go up links funcionality */
//$(function() {

	/* some links are used to launch a functionality. In these cases it is not needed the page to scroll. Add this element to the excludedLinksArr. */
/*	excludedLinksArr = ['#nav-side1','#nav-side2'];

    $('a').click(function(e) {
    	if ($.inArray($(this).attr('href'),excludedLinksArr) < 0) {
	    	var posIni = $(document).scrollTop();
	    	var posObject = $($(this).attr('href')).position().top;

	    	$('html, body').scrollTop(posObject);

	    	if (typeof setStickyObjectsVisibility !== 'undefined' && $.isFunction(setStickyObjectsVisibility)) {
	    		setStickyObjectsVisibility();
	    	}

	    	var posEnd = posObject - $('#sticky-header').outerHeight();
	    	$('html, body').scrollTop(posIni);

	    	if (typeof setStickyObjectsVisibility !== 'undefined' && $.isFunction(setStickyObjectsVisibility)) {
	    		setStickyObjectsVisibility();
	    	}

		    $('html, body').animate({scrollTop: posEnd},'fast');
	    	e.preventDefault();
    	}

    });
});*/

// Get environtment
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
