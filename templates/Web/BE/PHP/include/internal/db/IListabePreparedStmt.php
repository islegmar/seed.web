<?php
require_once(INTERNAL_ROOT_DIR . '/db/IListable.php');

/**
 * IL - 30/01/15 - Support for Prepared Stament
 * 
 * @author islegmar@gmail.com
 *
 */
interface IListabePreparedStmt extends IListable {
  // Return a map of form {key:val,....} for the query with prepared statement
  public function getData4PreparedStmt();
}
?>
