<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');
require_once(INTERNAL_ROOT_DIR . '/db/DBConnectionManager.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');
require_once(INTERNAL_ROOT_DIR . '/db/ListaPaginable.php');


/**
 * Returns a pagged list for a certain DAO
 * 
 * @author islegmar@gmail.com
 */
class ListaPaginableSrv extends Service {
  // ------------------------------------------------------------------- Service
	protected function performImpl() {
    $db = DBConnectionManager::get();
		// Build a ListaPaginable object for this item
		$item = FactoryObject::newObject($this->params->getParam('_object'));
    // IL - 02/02/15 - If we send info about the filter and the order, those
    // will be in params
		$lista=new ListaPaginable($item, $this->params);
		
		// Get the parameters inidicating which items I want
		$indPage = $this->params->getParam('indPage', 0);
		$totPerPage = $this->params->getParam('totPerPage', 10);
		

		// Get the data
		$lista->setNumRegPerPagina($totPerPage);
		$data = $lista->getData($db, $indPage);
		
		
		// @todo : investigar, si no es así se devuelven como strings
		$indPage    = intval($lista->getIndCurrPag());
		$totPages   = intval($lista->getTotPags());
		$totPerPage = intval($lista->getNumRegPerPagina());
		$totRecords = intval($lista->getTotRecords());
		
		return array(
			'indPage'     => $indPage,
			'totPages'    => $totPages,
			'totRecords'  => $totRecords,
			'totPerPage'  => $totPerPage,
			'isFirstPage' => $indPage===0,
			'isLastPage'  => $indPage==($totPages-1),
			'data'        => $data
		);
	}
}
?>
