// TODO : Revisar....
function Logger() {
	this.$logPanel = null;
}

Logger.instance = null;
Logger.eNewLine = document.createElement("br");
Logger.getInstance = function() {
	if ( Logger.instance==null ) {
		Logger.instance = new Logger(); 
	}
	
	return Logger.instance;
}

// --------------------------------------------------------------------- Setters
Logger.prototype.setLogPanel = function ($logPanel) {
	this.logPanel= $logPanel;
}

// ------------------------------------------------------------ Métodos Públicos
Logger.prototype.log = function(msg) {
  if ( this.$logPanel==null ) {
    this.$logPanel=$("<p class='logPanel'></p>");
    $("body").append(this.$logPanel);
  }
  this.$logPanel.append(msg);
}
