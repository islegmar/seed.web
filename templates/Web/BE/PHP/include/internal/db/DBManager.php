<?php
require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once('IDBManager.php');

/**
 * Handles all the communication with the database, using PDO_MYSQL.
 * @todo : this represents a single instance and it should be called in fact
 * DBConnection BUT we laredy have a DBConnection that is a "wrapper" over that
 * and we keep this for historical reasons.....
 */
class DBManager implements IDBManager
{
	/**
	 * Logger, category 'sql'.
	 * 
	 * @var unknown_type
	 */
	private $logger = null;
	
	/**
	 * Current connnection to the database
	 * @var unknown_type
	 */
	private $conn = null;
	
	/**
	 * Active PDOStatement
	 */
	private $pdoStmt = null;
	
	/**
	 * Constructor of the class.
	 * Connects to the server and selects the database.
	 * IL - 04/10/13 - We've changed the constructor just to be sure that this 
	 * is ONLY called by DBCOnnectionManager
	 */
	public function __construct($host, $user, $pass, $db, $dummyParam=null) {
		if ( is_null($dummyParam) ) {
			echo ('Who is calling DBManager() that is not DBConnectionManager?');
			exit();	
		}
		
		$this->logger = Logger::getLogger('sql');
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('[DBManager] host "' . $host . '" user "' . $user . '" db "' . $db . '"');
		}
		
		$this->conn = new PDO('mysql:host=' . $host . ';dbname=' . $db, $user, $pass, 
				array(PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8"));
		$this->conn->setAttribute(PDO::ATTR_AUTOCOMMIT,FALSE);
		// Throws exception in case integroty violation,... before it just failed
		// silently!!
		$this->conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	}

	/* Free resources */
	public function __destruct() {
		if ( $this->logger && $this->logger->isDebugEnabled() ) {
			$this->logger->debug('[DBManager] Free DBManager');
		}
	  $this->pdoStmt = null;
		$this->conn=null;
	}
	
	// ------------------------------------------------------------ Public Methods
	/**
	 * IL - 21/11/13
	 * Now the the connection is PDO, with a lot of features, has no sense to 
	 * wrap all the functionalities with an abstract layer, so in some cases 
	 * we have just to return the POD connection and allow the client to work with it
	 */
	public function getPDOConnection() {
		return $this->conn;
	}	
	
	// IL - 21/11/13 _ By default autocmmit is false, but we can change it
	public function setAutocommit($autocommit) {
		$this->conn->setAttribute(PDO::ATTR_AUTOCOMMIT,$autocommit);
	}
	
	
	// ---------------------------------------------------------------- IDBManager
	public function executeQuery($sql, $data=null) {
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('[DBManager] executeQuery(' . $sql . ')');
		}		
		
    // IL - 26/01/15 - Support for prepared stmt
    if ( is_null($data) ) { 
		  $this->pdoStmt = $this->conn->query($sql);
		} else {
      $this->pdoStmt = $this->conn->prepare($sql);
      $this->pdoStmt->execute($data);
    }
  
		if ( $this->pdoStmt === false ) {
			throw new Exception('Error al ejecutar la query "' . $sql . '"');
		}
	}

	public function loadResult() {
		if ( !isset($this->pdoStmt) || is_null($this->pdoStmt) ) {
			throw new Exception('pdoStmt es null o no está establecido');
		}
		
		//@todo : can be done better with fetchAll()?
		$data = array();
		while ( ($row = $this->pdoStmt->fetch(PDO::FETCH_ASSOC, PDO::FETCH_ORI_NEXT))!== false ) {
			array_push($data, $row);
		}

		return $data;
	}
	 
	public function getSelectedRows() {
		if ( !isset($this->pdoStmt) || is_null($this->pdoStmt) ) {
			throw new Exception('pdoStmt es null o no está establecido');
		}

		return $this->pdoStmt->rowCount();
	}


	public function getAffectedRows() {
		if ( !isset($this->pdoStmt) || is_null($this->pdoStmt) ) {
			throw new Exception('pdoStmt es null o no está establecido');
		}

		return $this->pdoStmt->rowCount();
	}

	public function getInsertId() {
		return $this->conn->lastInsertId();
	}
	
	public function quote($val) {
		return $this->conn->quote($val);
	}
	
	public function cerrar() {
		$this->pdoStmt = null;
		$this->conn=null;
	}

	public function beginTransaction() {
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('[DBManager] beginTransaction');
		}		
		$this->conn->beginTransaction();
	}
	
	public function commit() {
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('[DBManager] commit');
		}		
		$this->conn->commit();
	}
	
	public function rollback() {
		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('[DBManager] rollback');
		}
		
		$this->conn->rollback();
	}
	
}
?>
