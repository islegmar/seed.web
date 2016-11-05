<?php
require_once('DBBean.php');

/**
 * Mantiene una lista (query) paginable- 
 * NOTE : It extends DBBean just tor the findMultiple utility
 * IL - 02/02/15 - Added filter capabilities
 * IL - 21/04/15 - Added oerderBy
 * 
 * @author Isi 
 */
class ListaPaginable extends DBBean {
  private $totPags;
  private $totRecords;
  private $indPag = 0; // 0....
  private $numRegPerPagina = 12;

  // Nos permite saber que tenemos que recalcular la query.
  // Optimizamos para que sólo se haga cuando sea necesario
  private $isDirty = true;
	// The bean data
	private $dbBean;
	// The params for perfoming the query
	private $params;
  
	function __construct($dbBean, $params=null) {
		parent::__construct();
		$this->dbBean = $dbBean;
		$this->params = $params;
	}
  
	// ---------------------------------------------------------- Métodos Públicos
  /**
   * Va a la página indicada por $ind
   */
  public function go2Page($ind) {
    if ( $ind<0 || $ind>=$this->totPags) return;
    $this->indPag = $ind;
  }
  
  public function go2NextPage() {
    $this->go2Page($this->indPag+1);
  }

  public function go2PrevPage() {
    $this->go2Page($this->indPag-1);
  }
  
  public function getTotPags() {
    return $this->totPags;
  }

  public function getTotRecords() {
    return $this->totRecords;
  }

  public function getIndCurrPag() {
    return $this->indPag;
  }

  public function setNumRegPerPagina($numRegPerPagina) {
  	$this->numRegPerPagina = $numRegPerPagina;  	
  }
  
  public function getNumRegPerPagina() {
  	return $this->numRegPerPagina;  	
  }

  /** 
   * Devuelve los datos de la página actual or from a certain page, if se specify
   * one.
   */
  public function getData($db=null,$indPage=null) {
    // Obtenemos la query
    $query = $this->dbBean->getQuery($db, $this->params);
    // IL - 30/01/15 - Added support for Prepared Stament
    $data4PreparedStmt = $this->dbBean instanceof IListabePreparedStmt ? $this->dbBean->getData4PreparedStmt() : null;
    
    // Necesitamos recalcular los totales
    if ( $this->isDirty ) $this->calculateTotPags($query, $db, $data4PreparedStmt);
    
    // A certain page has been specified: move it!
    if ( !is_null($indPage) ) {
    	$this->go2Page($indPage);
    }
    
    if ( $this->logger->isInfoEnabled() ) {
      $this->logger->info("[ListaPaginable] indPag : $this->indPag totPags :  $this->totPags");
    }

    // Added the orderBY
    if ( !is_null($this->params) ) {
      $orderByParams=$this->params->getParam('orderBy');
      if ( !is_null($orderByParams) ) {
        $query .= ' ORDER BY ';
        foreach ($orderByParams as $indOrderByParam => $orderByParam ) {
          if ( $indOrderByParam>0 ) {
            $query .= ',';
          }
          if ( $this->logger->isDebugEnabled() ) {
            $this->logger->info('Added param : ' . $orderByParam['name']);
          } 
          $query .= htmlentities($orderByParam['name']) . ' ' . ( array_key_exists('direcc', $orderByParam) ? htmlentities($orderByParam['direcc']) : 'ASC' );
        }
      }      
    }
    
    // Ejecutamos la query para obtener una página
    $sql = $query . ' LIMIT ' .  intval($this->indPag * $this->numRegPerPagina ) . ',' . intval($this->numRegPerPagina);
    // IL - 30/01/15 - Added support for Prepared Stament
    $data = $this->findMultiple($sql, $db, false, $data4PreparedStmt);

    $this->dbBean->completarData($data, $db);
    
    return $data;
  }

  /**
   * Marca la query como dirty para tener que recalcular los totales
   */
  public function setDirty($dirty) {
    $this->isDirty = $dirty;
  }
  
  // --------------------------------------------------------- Métodos Protected
  /**
   * Determina si un parámetro cambia de valor (para marcar la query como dirty)
   */
  protected function hasChanged($val1, $val2) {
  	return  is_null($val1) && !is_null($val2) ||
  	       !is_null($val1) &&  is_null($val2) ||
  	       !is_null($val1) && !is_null($val2) && $val1!=$val2;
  }
  /**
   * Inicializa variables.
   * Esta función se tiene que llamar "a mano" cada vez que se modifque la query
   * IL - 30/01/15 - Added $data, support for prepared stmt
   */
  protected function calculateTotPags($query, $db, $data4PreparedStmt) {
  	
    // Primero calculamos en número de registros
    
  	// IL - 14/10/13 - Calculate in an another way, better
    // Para ello montamos la query count(*)
  	//$countSql = 'SELECT count(*) ' . substr($query, strpos(strtolower($query), 'from'));
    // Quitamos el order by (si lo tiene)
    // $posOrderBy = strpos(strtolower($countSql), 'order by');
    // if ( !($posOrderBy===false) ) {
    //   $countSql = substr($countSql, 0, $posOrderBy);
    // }
  	$countSql = 'SELECT count(*) FROM (' . $query . ') tmpl';
    
    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug('COUNT (' . $countSql . ')');
    }

    // IL - 30/01/15 - Added $data, support por prepared stament
    $this->totRecords = $this->getCount($countSql, $db, $data4PreparedStmt);
    $this->totPags = ceil($this->totRecords/$this->numRegPerPagina);
    $this->indPag = 0;
    if ( $this->logger->isInfoEnabled() ) {
      $this->logger->info('Se han encontrado ' . $this->totRecords . ' registros que son ' . $this->totPags . ' páginas');
    }
    $this->setDirty(false);
  }
}
?>