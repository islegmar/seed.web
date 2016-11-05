/* list-options.js ============================================ */
/* ============================================================ */

$(document).ready(function(){

	$('.filtered-search-filters-list').click(function(event){
	     event.stopPropagation();
	 });

	$('.filtered-search-filters-list input[type=checkbox]').change(function(e){

		var obj = $(this).closest('.filtered-search');

		var isAll;
		if ($(this).val() == 'all') { isAll = true } else { isAll = false }

		showSelectedFilters(obj,isAll);
	});

	$(window).resize(function(){
		$.each($('.filtered-search'),function(){
			showSelectedFilters($(this));			
		});
	});
	
	$.each($('.filtered-search'),function(){
		showSelectedFilters($(this));
	});

});

// Close search filter
$(document).click(function(e) {
	$.each($('.filtered-search-filters-list'),function(){	
		var container = $(this);

		if (!container.is(e.target) // if the target of the click isn't the container...
		&& container.has(e.target).length === 0 // ... nor a descendant of the container...
		&& container.hasClass("in")) // ... and is open
		{
			//alert("yes");
			container.collapse('hide');
		}
	});
});

function showSelectedFilters(obj, isAll) {
	var strFilters = '';
	var allSelected = true;
	var num = 0;
	var filters = obj.find('.filtered-search-filters-list input[type=checkbox]');

	if (filters.length > 1) {

		if (isAll) {
			$.each(filters, function(){
				if ($(this).val() == 'all') {
					$(this).prop('checked',true);
				} else {
					$(this).prop('checked',false);
				}
			});
		} else {
			$.each(filters, function(){
				if ($(this).prop('checked') && $(this).val() != 'all') {
					if (strFilters != '') {
						strFilters = strFilters + ', ' + $.trim($(this).closest('label').text());
					} else {
						strFilters = $.trim($(this).closest('label').text());
					}
					num++;
				}
			});
		}

		if (filters.length == num+1 || num == 0) {
			filters.first().prop('checked',true);
			$.each(filters, function(){
				if ($(this).val() != 'all') {
					$(this).prop('checked',false);
				}
			});
			allSelected = true;
		} else {
			filters.first().prop('checked',false);
			allSelected = false;
		}
		
		if (strFilters != '' && !allSelected) {
			if (getEnv() == 'xs' && strFilters.length >= 10) {
				strFilters = 'Some';
			}
			obj.find('.filtered-search-filters-selected').text(strFilters);
		} else {
			obj.find('.filtered-search-filters-selected').text('All');
		}

	} else {

		if (getEnv() != 'xs') {
			obj.find('.filtered-search-filters-selected').text($.trim(filters.closest('label').text()));
		} else {
			obj.find('.filtered-search-filters-selected').text('All');
		}
		filters.prop('checked',true);
		filters.attr('disabled','disabled');

	}
}