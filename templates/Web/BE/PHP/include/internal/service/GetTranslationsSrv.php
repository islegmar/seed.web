<?php
require_once(INTERNAL_ROOT_DIR . '/service/Service.php');
require_once(INTERNAL_ROOT_DIR . '/service/IValidateBeanSrv.php');
require_once(INTERNAL_ROOT_DIR . '/BeanValidateException.php');
require_once(INTERNAL_ROOT_DIR . '/utils/FactoryObject.php');


/**
 * TODO : probably this is useful only for demo porpouses (missing cache,...)
 *
 * Returns a JSON with the translations
 *
 * @TODO : BIG TODO : Unify with I18N and _I18N, Fix all this mess with 
 * the Lang :-(
 * 
 * @author islegmar@gmail.com
 *
 */
class GetTranslationsSrv extends Service {
  // ------------------------------------------------------------------- Service
  protected function performImpl() {
    $retData=array();

    // -------------------------------------------------------- Get the language
    $setAsCurrLang = $this->getParamValue('setAsCurrLang', 1);
    $lang = $this->getParamValue('lang', null);

    // Not set the lang, so try to guess it
    if ( is_null($lang) ) {
      // We have LANG defined in _SESSION
      if ( isset($_SESSION['LANG']) && !is_null($_SESSION['LANG']) ) {
        $lang = $_SESSION['LANG'];
        if ( $this->logger->isDebugEnabled() ) {
          $this->logger->debug('Recover "' . $lang . '" from _SESSION');
        }
      // Not set the lang, choose the default one
      } else {
        // @TODO : choose the detault one from the browser's info or configurable
        $lang='en';
        $_SESSION['LANG'] = $lang;
        if ( $this->logger->isDebugEnabled() ) {
          $this->logger->debug('Choose the default lang "' . $lang . '"');
        }
      }
    // A new lang is set, keep it!  
    } else {
      if ( $setAsCurrLang ) {
        $_SESSION['LANG'] = $lang;
        if ( $this->logger->isDebugEnabled() ) {
          $this->logger->debug('Store "' . $lang . '" into _SESSION');
        }
      }
    }

    if ( $this->logger->isDebugEnabled() ) {
      $this->logger->debug('Use "' . $lang . '".');
    }
    
    // --------------------------------------------------------- Return the data
    // The current language
    $retData['currLang']=$lang;
    
    // All langs defined
    $retData['langs'] = FactoryObject::newObject('_Lang')->getAll();

    // The translations
    $retData['i18n'] = array();

    $dirI18N = FactoryObject::newObject('_ConfigApp')->loadActive()->getPath4I18N();
    
    // Get translations from the file, this should be only for development
    if ( !empty($dirI18N) ) {
      $fileI18N = $dirI18N . '/' . $lang . '.properties';       
      $this->logger->warn("For language $lang, getting translations from file '$fileI18N', this should be only in development mode!");

      $retData['i18n'] = $this->file2Map($fileI18N);
    // Normal in production mode : load from the database  
    } else {
      $sql=<<<EOD
      SELECT Name, 
             Text 
        FROM _I18N
        JOIN _Lang
          ON _I18N.Id_Lang = _Lang.Id
         AND _Lang.Locale = :Locale
    ORDER BY Name ASC 
EOD;

      $allTrans = 
        FactoryObject::newObject('_I18N')->findMultiple(
          $sql, 
          null, 
          false,
          array(':Locale' => $lang)
        );
      foreach ($allTrans as $row) {
        $key = $row['Name'];
        $value = $row['Text'];
        $retData['i18n'][$key] = $value;
      }
    }


    return $retData;
	}

  protected function file2Map($file) {
    $map=array();
    $handle = fopen($file, "r");
    if ($handle) {
      $patternEmpty="/^ *$/";
      $patternComment="/^ *#/";
      $patternVariable="/^([^=]*)=(.*)$/";

      while (($line = fgets($handle)) !== false) {
        if ( ! (preg_match($patternEmpty, $line) ||  
                preg_match($patternComment, $line) ) ) {
          $matches=null;
          if ( preg_match($patternVariable, $line, $matches) ) {
            $map[$matches[1]]=$matches[2];
          } else {
            throw new Exception("Unkown line '$line' in file '$file'.");
          }
        }
      }

      fclose($handle);

      return $map;
    } else {
      throw new Exception("File '$file' not found.");
    } 
  }
}
?>