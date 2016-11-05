<?php
/**
 * Represents a bean that can return a list of data from the db.
 * 
 * @author islegmar@gmail.com
 *
 */
interface IListable {
	public function getQuery($db, $params=null);
	// Modifica los datos, añadiendo pej. más campos
	public function completarData(&$data, $db);
	
}
?>