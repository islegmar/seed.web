<?php
require_once( INTERNAL_ROOT_DIR . '/controller/AjaxController.php');
require_once( INTERNAL_ROOT_DIR . '/utils/WebParams.php');

/**
 * Executes a service and return its data
 * 
 * @author islegmar@gmail.com
 *
 */
class Service2AjaxController extends AjaxController {
	// ------------------------------------------------------------ AjaxController
	protected function returnData() {    
		// -------------------------------------------------- Instantiate the Service		
		$WEB_PARAMS = new WebParams(); 
		$serviceName       = $WEB_PARAMS->getOblParam('serviceName');
		$serviceDataFormat = $WEB_PARAMS->getParam('serviceDataFormat');

		if ( $this->logger->isDebugEnabled() ) {
			$this->logger->debug('Invocando servicio [' . $serviceName . ']');
		}
		$service = FactoryObject::newObject($serviceName);

		// ---------------------------------------------------------- Set the params 
		// @todo : what to do if we receive get parameters and a JSON in the body?
		// They can be sent via JSON or Request
		// JSON in the body
		/*
		if ( $serviceDataFormat =='JSON' ) {
			$data = file_get_contents('php://input');
			if ( $this->logger->isDebugEnabled() ) {
				$this->logger->debug('Recibido en el body del POST los datos [' . $data . ']');
			}
			$service->setParams(json_decode($data));
		// GET & POST parameters	
		} else {
			$service->setParams($WEB_PARAMS);
		}
		*/
		// IL - 06/11/13 - Big Change!!!
		// Now we don't need to pass an special parameter to say if we send the data 
		// via AJAX or REQUEST
		// Unfortunatelly, that's not always true :-(
		/*		
		if ( !is_null($serviceDataFormat) ) {
			throw new Exception('Parameter "serviceDataFormat" is obsolete! Please, review the code.');	
		}
		*/
		
		if ( !is_null($serviceDataFormat) && $serviceDataFormat=='request' ) {
			$service->setParams($WEB_PARAMS);
		} else {
			$data = file_get_contents('php://input');
			// Empty data : the params are sent via the REQUEST
			if ( empty($data) ) {
				$service->setParams($WEB_PARAMS);
			// The data is a JSON	
			} else {
				$service->setParams(json_decode($data));
			}
		}
		
		// ------------------------------------------- Execute and send the response
		return $service->perform();
	}
}
?>
