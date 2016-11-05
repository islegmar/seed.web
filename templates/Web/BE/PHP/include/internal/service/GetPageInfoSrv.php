<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');
require_once(INTERNAL_ROOT_DIR . '/service/IValidateBeanSrv.php');
require_once(INTERNAL_ROOT_DIR . '/BeanValidateException.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');


/**
 * This is a composed service that retrieves a bunch of information to be sent
 * to the client. We do it that way to minimize the number of requests that the
 * client foest to the server
 * 
 * @author islegmar@gmail.com
 */
class GetPageInfoSrv extends Service {
  // ------------------------------------------------------------------- Service
  protected function performImpl() {
    $retData=array();

    // ------------------
    // Translations
    // ------------------
    $cfgApp = FactoryObject::newObject('_ConfigApp')->loadActive();

    if ( $this->getParamValue('i18n',1) || $cfgApp->getServerReturnAlwaysI18N() ) {
      if ( $cfgApp->getServerReturnAlwaysI18N() ) {
        $this->logger->warn('Always return translations, this is suitable ONLY in development mode!');
      }

      $srvTranslations = FactoryObject::newObject('GetTranslationsSrv');
      $srvTranslations->addParam('setAsCurrLang', $this->getParamValue('setAsCurrLang', 1));
      $srvTranslations->addParam('lang', $this->getParamValue('lang', null));
      $retData['i18n'] = $srvTranslations->perform();    
    }

    // ------------------
    // Connected user (or anonymous)
    // ------------------
    $ppal = WebSession::getInstance()->getPrincipal();
    $retData['user'] =  $ppal->isAnonymous() ? 
      array( 'role' => '', 'permissions' => array()) : $ppal->getAsArray();
    // Remove the sensible data
    unset($retData['user']['Password']);
       
    return $retData;
  }
}
?>
