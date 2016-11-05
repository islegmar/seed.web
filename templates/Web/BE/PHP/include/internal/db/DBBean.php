<?php

require_once(EXTERNAL_ROOT_DIR . '/log4php/Logger.php');
require_once(INTERNAL_ROOT_DIR . '/db/DBConnectionManager.php');
require_once(INTERNAL_ROOT_DIR . '/db/MultipleRowsSelectedException.php');
require_once(INTERNAL_ROOT_DIR . '/db/NoRowSelectedException.php');

/**
 * Base class to all the persistant beans in database.
 * *All beans* are identified with a field 'Id', so this class has the field 'Id' 
 *
 * IL - 04/10/13 - BIG CHANGE
 * Now, all the DB Connections are get via DBConnectionManager
 *
 * @author islegmar@gmail.com
 */
class DBBean {
	protected $logger;
	// ALL the beans have a field Id
	protected $Id;

	public function __construct() {
		$this->logger = Logger::getLogger("sql");
	} 

  // --------------------------------------------------------- Getters & Setters
	public function setId($id) {
		$this->Id = $id;
	}

	public function getId() {
		return $this->Id;
	}

	// ------------------------------------------------------------ Public Methods
	// --- Database Related
	// NAMING CONVENTION:
	// + loadXXX : return objects
	// + getXXX  : return arrays 
	
	// Select one record using Id
	public function loadById($id, $pDb=null) {
		return $this->findOneWithStmt('SELECT * FROM ' . $this->TABLE_NAME . ' WHERE Id=:Id', array(':Id'=>$id), true, $pDb);
	}
	public function getById($id, $pDb=null) {
		return $this->findOneWithStmt('SELECT * FROM ' . $this->TABLE_NAME . ' WHERE Id=:Id', array(':Id'=>$id), false, $pDb);
	}

	// IL - 03/07/15 - Select one usign query
	public function loadOne($sql, $data, $pDb=null) {
		return $this->findOneWithStmt($sql, $data, true, $pDb);
	}
	public function getOne($sql, $data, $pDb=null) {
		return $this->findOneWithStmt($sql, $data, false, $pDb);
	}

    // IL - 04/02/15 - Select one by a certain field	
	public function loadByField($fieldName, $fieldValue, $pDb=null) {
		return $this->findOneWithStmt('SELECT * FROM ' . $this->TABLE_NAME . ' WHERE ' . $fieldName . '=:' . $fieldName, array(':' . $fieldName =>$fieldValue), true, $pDb);
	}
	public function getByField($fieldName, $fieldValue, $pDb=null) {
		return $this->findOneWithStmt('SELECT * FROM ' . $this->TABLE_NAME . ' WHERE ' . $fieldName . '=:' . $fieldName, array(':' . $fieldName =>$fieldValue), false, $pDb);
	}

	/**
	 * IL - 19/11/13 - GetAll records from a table
	 */
	public function getAll($pDb=null) {
		return $this->findMultiple('SELECT * FROM ' . $this->TABLE_NAME, $pDb, false);
	}
	public function loadAll($pDb=null) {
		return $this->findMultiple('SELECT * FROM ' . $this->TABLE_NAME, $pDb, true);
	}

	/**
	 * IL - 06/11/13 - For the I18N
	 */
	public function getAllByIdParent($idParent, $parentField, $pDb=null) {
		return $this->findMultiple('SELECT * FROM ' . $this->TABLE_NAME . ' WHERE ' . $parentField . ' = ' . $idParent , $pDb, false);
	}
	public function loadAllByIdParent($idParent, $parentField, $pDb=null) {
		return $this->findMultiple('SELECT * FROM ' . $this->TABLE_NAME . ' WHERE ' . $parentField . ' = ' . $idParent , $pDb, true);
	}

	public function getAllByField($fieldName, $fieldValue, $pDb=null) {
		if ( is_null($fieldValue) ) {
			return $this->findMultiple(
				'SELECT * FROM ' . $this->TABLE_NAME . ' WHERE ' . $fieldName . ' IS NULL', 
				$pDb,
				false
			);			
		} else {
			return $this->findMultiple(
				'SELECT * FROM ' . $this->TABLE_NAME . ' WHERE ' . $fieldName . '=:' . $fieldName, 
				$pDb,
				false,
				array(':' . $fieldName =>$fieldValue)
			);			
		}
	}
	public function loadAllByField($fieldName, $fieldValue, $pDb=null) {
		if ( is_null($fieldValue) ) {
			return $this->findMultiple(
				'SELECT * FROM ' . $this->TABLE_NAME . ' WHERE ' . $fieldName . ' IS NULL', 
				$pDb,
				true
			);			
		} else {
			return $this->findMultiple(
				'SELECT * FROM ' . $this->TABLE_NAME . ' WHERE ' . $fieldName . '=:' . $fieldName, 
				$pDb,
				true,
				array(':' . $fieldName =>$fieldValue)
			);
		}
	}

	// --- Utilities that follow the load/get convention
	public function loadMultiple($sql, $data4PreparedStmt=null, $pDb=null) {
		return $this->findMultiple($sql, $pDb, true, $data4PreparedStmt);
	}

	public function getMultiple($sql, $data4PreparedStmt=null, $pDb=null) {
		return $this->findMultiple($sql, $pDb, false, $data4PreparedStmt);
	}

	/** 
	 * IL - 10/01/13
	 * Check if a certain query returns a single record or not
	 */
	public function checkExists($sql, $pDb=null) {
		$db = !is_null($pDb) ? $pDb : DBConnectionManager::get();
		
		$retExists = null;
		try {
			$this->findOne($sql, false, $db);
		
			$retExists=true;
		} catch(NoRowSelectedException $e){
			$retExists=false;
		}
		
		return $retExists;
	}

	/**
	 * Executes a query that is expected to return one row and return the value
	 * of one of the fields
	 */
	public function getOneFiledValue($sql, $fieldName, $pDb=null) {
		$db = !is_null($pDb) ? $pDb : DBConnectionManager::get();
		
		$row = $this->findOne($sql, false, $db);

		if ( !isset($fieldName) ) {
			throw new Exception('No existe el campo "' . $fieldName .
					' en la query "' . $sql . '"');
		}

		return $row[$fieldName];
	}

	/* Utility : Delete */
	public function doDelete($sql, $pDb=null) {
		return $this->updateOrInsert($sql, $pDb, true, false);
	}
	/* Utility : Insert */
	public function doInsert($sql, $pDb=null) {
		return $this->updateOrInsert($sql, $pDb, false, false);
	}
	/* Utility : Update */
	public function doUpdate($sql, $pDb=null) {
		return $this->updateOrInsert($sql, $pDb, false, true);
	}

	/**
	 * Ejecuta una query del tipo count(*) y devuelve el n�mero
	 * @param $sql
	 * @return unknown_type
	 */
  // IL - 30/01/15 - Added $data for the prepraredStmt
	public function getCount($sql, $pDb=null, $data=null) {
		$db = !is_null($pDb) ? $pDb : DBConnectionManager::get();
		
		$db->executeQuery($sql, $data);
		$data = $db->loadResult();

		return $data[0]['count(*)'];
	}

	// --- NOT Database Related

	/**
	 * Return an array containing the fields from that bean
	 */
  function getAsArray($pData=null) {
  	$data = is_null($pData) ? array() : $pData;
  
  	$data['Id'] = $this->Id;
  
  	return $data;
  } 

	// ------------------------------------------------------- "Protected" Methods
	// Well, those metods are not protected because they are already used by other
  // projects, but they SHPULD BE AVOIDED, use an utility method instead

  /**
   * @warning Do not use it, use an utility method instead
   *
   * Executes a query that returns a single record (otherwise an exception is thrown).
   * It can return an object or an array with the data
   * 
   * NOTE : before this query was called findOne that received the query with 
   * already prepared with all the values, but has been replaced for this version
   * more secure, that uses prepared statmenets.
   *
   * @param String $sql The prepared statement with :<Param> as placehoders. 
   * Example SELECT * FROM _User WHERE Login = :Login AND Status = :Status
   * @param Array $data An array with all the param values 
   * Example array(':Login'=>'johndoe',':Status'=1)
   * @param Bool $doFillBean If true the return data will be the current object
   * filled, if false an array with the data is returned 
   */ 
  public function findOneWithStmt($sql, $data, $doFillBean=true, $pDb=null) {
    if ( $this->logger->isDebugEnabled() ) {
	  $this->logger->debug('findOneWithStmt(sql:' . $sql . ', data : ' . json_encode($data) . ', doFillBean:'. $doFillBean . ')');
	}
		
	$db = !is_null($pDb) ? $pDb : DBConnectionManager::get();
	        
    $db->executeQuery($sql, $data);
	$results = $db->loadResult();
	if ( $this->logger->isDebugEnabled() ) {
	  $this->logger->debug('[DBBean]. numRows : ' . count($results));
	}
	if ( count($results)==1 ) {
	  $result=$results[0];
	  if ( $doFillBean ) {
	    $this->fillBeanFromArray($result);

        // Return the object, useful for chaining
        return $this;
	  }
	} else if ( count($results)==0 ) {
	  throw new NoRowSelectedException();
	} else {
	  throw new MultipleRowsSelectedException();
	}

	// Return the array with data
    return $result;
  }

	/**
	 * @warning Do not use it, use an utility method instead
   *
	 * Ejecuta un query y devuelve un array con los resultados.
	 * IL - 30/01/15 - Added $data, support for preparedStmt
   *
	 * @param unknown_type $sql
	 * @return unknown_type
	 */
	public function findMultiple($sql, $pDb=null, $doFillBean=false, $data4PreparedStmt=null) {
  	/*if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('[DBBean]. findMultiple(sql:' . $sql . ',doFillBean:'. $doFillBean . ')');
		}*/
		
		$db = !is_null($pDb) ? $pDb : DBConnectionManager::get();
		
    // IL - 30/01/15 - Added $data, support for preparedStmt
		$db->executeQuery($sql, $data4PreparedStmt);
		$data = $db->loadResult();
		
		if ( $doFillBean ) {
			$listaBeans=array();
			$className = get_class($this);
			foreach($data as $item)  {
				// Create a new instance of this bean
				$bean = new $className();
				// Fill the bean with the info from the database
				$bean->fillBeanFromArray($item);
				array_push($listaBeans, $bean);
			}
			 
			return $listaBeans;
		} else {
			return $data;
		}
	}

	/**
	 * @warning Do not use it, use an utility method instead
   *
   * Ejecuta un query y devuelve un array con los resultados.
	 *
	 * @param unknown_type $sql
	 * @return int or nothing If INSERT, the id of the created record. If UPDATE, the
	 * nomber of affected rows, id DELETE nothing
	 */
	public function updateOrInsert($sql, $pDb=null, $isDelete=false, $isUpdate=false) {
		/*
		TODO - Da error
		if ( $this->logger->isDebugEnabled() ) {
		$this->logger->debug("[DBBean] '" . $sql . "'");
		}
		*/
		$db = !is_null($pDb) ? $pDb : DBConnectionManager::get();
		
		$db->executeQuery($sql);

		// Update or Delete
		if ( $isUpdate || $isDelete) {
			return $db->getAffectedRows();
		// INSERT
		} else if ( !$isDelete ) {
			return $db->getInsertId();
		}
	}
	
	// ----------------------------------------------------------- Obsolte Methods
	// public function findOne($sql, $doFillBean=true, $pDb=null)
	// ==> Use findOneWithStmt

	// public function fillBeanFromArray($data,$emptyAsNull=true)
	// ===> Every class extending this one should have its own method 
	//      public function fillBeanFromArray($data,$emptyAsNull=true,$prefix='')

	// public function getInsertId($db)
	// ===> Use instead $db->getInsertId()
}
?>