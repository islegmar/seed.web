<?php
require_once(INTERNAL_ROOT_DIR . '/db/DBManager.php');

/**
 * IL - 21/11/13 - REFRACTORING
 * 
 * This class is OBSOLETE and it should disappear. We keep it as utility becasuse
 * it's used everywhere but finally it will disappear, I'm sure!
 * 
 * Instead, the new DBConnection class (that is a wrapper for DBManager should 
 * be used)
 * 
 * Basically, we should write things like:
 * FactoryObject::newObject('DBConnection')->get() to get the old DBManager object 
 */
class DBConnectionManager {
	/**
	 * Get the current db connection. If it is not exist, make one and begin a 
	 * transation.
	 * IMPORTANT : to close, the methods commit/rollback MUST BE CALLED
	 */
	public static function get() {
		return FactoryObject::newObject('DBConnection')->get();
	}

	public static function commit() {
		/* Only commit if a transaction has been started */
		if ( FactoryObject::hasBeenAlreadyInstantiated('DBConnection') ) {
			$conn = FactoryObject::newObject('DBConnection')->get();
			$conn->commit();
			$conn->cerrar();
		} 
	}

	public static function rollback() {
		/* Only rollback if a transaction has been started */
		if ( FactoryObject::hasBeenAlreadyInstantiated('DBConnection') ) {
			$conn = FactoryObject::newObject('DBConnection')->get();
			$conn->rollback();
			$conn->cerrar();
		}
	}
}
?>
