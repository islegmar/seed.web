<?php
require_once(INTERNAL_ROOT_DIR . '/utils/ConfigurableBean.php');
require_once(INTERNAL_ROOT_DIR . '/db/DBManager.php'); 

/**
 * This class is the natural replacement for DBManager and I had to take a HARD
 * decission:
 * 
 * 1) Put the DBManager's code here inside and deprecate DBManager.
 * 2) Convert this in a wrapper for DBManager. DBManager remains as a basic library
 *    and this class is a wrapper that is 'FactoryObject compatible'  
 * 
 * Finally, 2) is chosen (I'm sure I'll regret....)
 * 
 * The configuration this object receives is:
 *   'server'  => MYSQL_SERVER_NAME, 
 *	 'user'    => MYSQL_DB_USERID,
 *	 'password'=> MYSQL_DB_PASSWORD,
 *	 'name'    => MYSQL_DB_NAME 
 *
 * When the object is instantiated, automatically a connection is created  
 */
class DBConnection  extends ConfigurableBean {
	// DBManager instance
	protected $dbManager = null;
	
	// ------------------------------------------------------------ Public Methods
	public function get() {
		return $this->dbManager;
	}
	
	// ---------------------------------------------------------- ConfigurableBean
	/**
	 * Automatically, create a connection
	 * @param unknown_type $cfg
	 */
	public function config($cfg) {
		parent::config($cfg);
		
		$this->dbManager = new DBManager(
			$this->getOblCfgValue('server'),
			$this->getOblCfgValue('user'),
			$this->getOblCfgValue('password'),
			$this->getOblCfgValue('name'),
			'dummy param :-)'
		);

		// Do we do an autocommit? By default we do (see DBManager)
		$autocommit = $this->getCfgValue('autoCommit', null);
		if ( !is_null($autocommit) ) {
			$this->dbManager->setAutocommit($autocommit);
		}

		// Do we start a transaction? By default we start (NOTE: in this case we 
		// will have to perform at the te end a commit/rollback)
		if ( $this->getCfgValue('autoTransaction', true) ) {
			$this->dbManager->beginTransaction();
		}
	}
}
?>
