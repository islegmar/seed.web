<?php

/**
 * Handles all the communication with the database.
 */
interface IDBManager
{
	/**
	 * Execute the sql statement and returns with the result set.
	 *
	 * @param string $sql
	 * @return void
	 */
	public function executeQuery($sql);
	
	/**
	 * This function loads the previous query result into an array of rows.
	 *
	 * @return array
	 */
	public function loadResult();
	
	/**
	 * Returns with the number of selected rows in the previous sql statement.
	 *
	 * @return int
	 */
	public function getSelectedRows();
	
	/**
	 * Returns with the number of the affected rows in the previous sql statement.
	 *
	 * @return int
	 */
	public function getAffectedRows();
	
	/**
	 * Get the ID generated from the previous INSERT operation
	 *
	 * @return int
	 */
	public function getInsertId();
	
	/**
	 * Close the current connection
	 */
	public function cerrar();
	
	// Transactions
	public function beginTransaction();
	public function commit();
	public function rollback();
	
	
	//function Insertar_vector_en_tabla($Vector_datos,$Tabla);
	/*function Begin();
	function Rollback();
	function Commit();
	function begin2();
	function commit2();
	function rollback2();*/
}

?>
