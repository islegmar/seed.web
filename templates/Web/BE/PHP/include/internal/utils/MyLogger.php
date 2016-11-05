<?php
include_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');

/**
 * Now it's too late, but the idea should be use this logger and this logger uses
 * log4php, but we already use log4php in a lot of places.
 * Now, we use this class to configure the logger
 *
 * @author islegmar
 */

class MyLogger {
	// ------------------------------------------------------------------- IFilter		
	public static function config($cfg) {
		// To avoid 
		// Warning: date(): It is not safe to rely on the system's timezone settings. 
		// You are *required* to use the date.timezone setting or the 
		// date_default_timezone_set() function. In case you used any of those 
		// methods and you are still getting this warning, you most likely 
		// misspelled the timezone identifier. We selected the timezone 'UTC' for 
		// now, but please set date.timezone to select your timezone. in 
		// /home/islegmar/projects/myWebsite/www/external/log4php/helpers/LoggerDatePatternConverter.php on line 51
		// (and in other many files)
		date_default_timezone_set('UTC');
		
		// To avoid the warning message
		// Warning: log4php: Invalid level value [D] specified for logger [level]. 
		// Ignoring level definition. in 
		// .../external/log4php/configurators/LoggerConfiguratorDefault.php 
		// on line 483 Warning: Invalid argument supplied for foreach() in 
		// ..../external/log4php/configurators/LoggerConfiguratorDefault.php 
		// on line 426 
		// Warning: log4php: Invalid additivity value [D] specified for logger [level]. 
		// Ignoring additivity setting. in 
		// .../external/log4php/configurators/LoggerConfiguratorDefault.php 
		// on line 483
		@Logger::configure($cfg);
	}
}
?>