var inputAuto = angular.module('inputAuto', []);

inputAuto.controller('InputAutoController', function($scope) {
	$scope.options = [
		{name:'Barcelona'},
		{name:'Lérida'},
		{name:'Tarragona'},
		{name:'Gerona'},
		{name: 'Zaragoza'},
		{name: 'Teruel'},
		{name: 'Huesca'}
	];

	$scope.setValue = function(new_title) {
		 this.theValue = new_title;
	};

});

inputAuto.directive('autoSuggestion', function(){
	var checkActive = function(list) {
		var active;
		angular.forEach(list, function(item) {
			if (item.active) {
				active = list.indexOf(item);
			}
		});
		return active;
	};
	var clearActives = function(list) {
		angular.forEach(list, function(item) {
			item.active = (item.active) ? false : false;
		});
	};
	var setActive = function(list, index) {
		clearActives(list);
		var suggestion;
		if (index < list.length) {
			list[index].active = true;
			suggestion = list[index].name;
		}
		return suggestion;
	};
	return {
		link: function(scope, element, attrs) {
			var theList = scope.options;
			var optionsNumber = theList.length;
			var active;
			scope.focused = function() {
				active = 0;
				scope.theSuggestion = setActive(theList, active);
			};
			scope.blurred = function() {
				clearActives(theList);
				scope.theSuggestion = '';
				active = '';
			};
			scope.navActive = function(keyEvent) {
				if (keyEvent.which === 38 && active > 0) {
					active = --active;
					scope.theSuggestion = setActive(theList, active);
					console.log(active+1 + ' of ' + optionsNumber);
				}
				if (keyEvent.which === 40 && active < optionsNumber-1) {
					active = ++active;
					scope.theSuggestion = setActive(theList, active);
					console.log(active+1 + ' of ' + optionsNumber);
				}
				if (keyEvent.which === 13) {
					scope.setValue(scope.theSuggestion);
				}
			};
		}
	};
});