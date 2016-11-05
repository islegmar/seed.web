/* nav-side.js ================================================ */
/* ============================================================ */

$(document).ready(function(){
	
	$('.nav-side-open').click(function(e){
		$($(this).attr('href')).addClass('in');
		e.preventDefault();
	});
	
	$('.nav-side-close').click(function(e){
		$(this).closest('.nav-side').removeClass('in');
		e.preventDefault();
	});
	
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
	
});
