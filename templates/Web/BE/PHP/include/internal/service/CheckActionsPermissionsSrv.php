<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');

/**
 * 
 * @author islegmar@gmail.com
 */
class CheckActionsPermissionsSrv extends Service {
  // ------------------------------------------------------------------- Service
  protected function performImpl() {
    $actionsAllowed=array();

    // @TODO : see note in php2js.js (function buildGlobalActions): I have tried
    // to pass directly the array with all the action siwthout success :-( so finally
    // I pass them as string. NOTE : do NOT use getParams() becuase this function
    // will quote the values, so use directly $_POST
    $actionsCfg = json_decode($_POST['actionsCfg']);

    foreach ($actionsCfg as $ind => $actionCfg) {
      $actionTitle = $actionCfg->name;

      if ( property_exists($actionCfg, 'checkSecurity') && !is_null($actionCfg->checkSecurity) ) {
        $checkSecurity = $actionCfg->checkSecurity;
        if ( $this->logger->isDebugEnabled() ) {
          $this->logger->debug('Rutime check need to be performed to "' . $actionTitle . '"');  
        }

        $srv = FactoryObject::newObject($checkSecurity->module . '/service/' . $checkSecurity->name . $checkSecurity->module . 'Srv');
        if ( $this->logger->isDebugEnabled() ) {
          $this->logger->debug('Instantiated class  "' . get_class($srv) . '"');  
        }

        // Add the params
        // $checkSecurity->params : [
        //   { "<paramName1>" : <paramValue1> },
        //   { "<paramName2>" : <paramValue2> }
        // ]
        if ( property_exists($checkSecurity, 'params') && !is_null($checkSecurity->params) ) {
          // $paramCfg : { "<paramName>" : <paramValue> }
          foreach ($checkSecurity->params as $indParam => $paramCfg) {
            // This will be always a loop of one single element, to get the 
            // paramName and paramValue
            foreach ($paramCfg as $paramName => $paramValue) {
              if ( $this->logger->isDebugEnabled() ) {
                $this->logger->debug('Add parameter (' . $paramName . ',' . $paramValue . ')'); 
              }
              $srv->addParam($paramName, $paramValue);
            }
          }
        }

        // Once the Service has ben configured with all the runtime params, 
        // checkSecurity to see if the permission is granted or denied
        try {
          $srv->checkSecurity();
          array_push($actionsAllowed, $actionCfg);
          if ( $this->logger->isDebugEnabled() ) {
            $this->logger->debug('Permission : Granted');
          }          
        // @TODO : check it is a "security" exception  
        } catch (Exception $e) {
          if ( $this->logger->isDebugEnabled() ) {
            $this->logger->debug('Permission : Denied');
          }
        }
        
      } else {
        if ( $this->logger->isDebugEnabled() ) {
          $this->logger->debug('NO Rutime check need to be performed to "' . $actionTitle . '"');  
        }        
        array_push($actionsAllowed, $actionCfg);
      }
      // $srv = FactoryObject::newObject($actionCfg->moduleName . '/service/' . $actionCfg->moduleName)
    }
     
    return $actionsAllowed;
  }
}
?>
