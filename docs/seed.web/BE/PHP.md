# Back End in PHP

This document explain specific topics that only have sense in the PHP Provider, that means not only with the PHP language but with the specific "framework" used.
In case that a certain topic applies to all the possible BE providers, this info must not appear here but in a generic document where all the possible "implementation" can be easily compared.

It has been used any PHP's framework (CakePHP,...)?
---------------------------------------------------

No, the current code has been "donated" by islegmar@gamil.com` and it is a PHP code "from scratch" adapting some of the well known ideas from the Java World (dispatcher, IoC,...). Its origin is some old code that has been slightly adapted for seed.web, so it is not optimized and there are some TODOs. 

Please, describe a steps followed by a request
-----------------------------------------------
Sure! The first thing that needs to be noticed is the file .htaccess that can be found at the PHP's root folder:

    RewriteEngine On

    RewriteRule ^service/(.*)$  php/dispatcher.php?controllerName=Service2AjaxController&serviceName=$1Srv [QSA,NC,L]

    RewriteRule ^action/(.*)$   php/dispatcher.php?controllerName=$1Ctr [QSA,NC,L]

    RewriteRule ^list/(.*)$     service/ListaPaginable?_object=$1 [QSA,NC,L]

**TODO** :  minimize's this file contents taking into account that now all the application is "module based". For example the URL to accees the service AddAll_User is `/service/_User/service/AddAll_User` and it executes the file located at `/_User/service/AddAll_UserSrv.php`.

As we can see, there are 2 maibn requests handled by PHP : services and actions.
* services : in the current implementation it represents the AJAX calls.
* actions : in the current implementation it represents the calls that are NOT AJAX (**TODO** : review if they can be removed).

Let's analyze step by step thow 2 kind of calls.

### Services (AJAX calls)

* The request /service/_User/service/AddAll_User is translated by .htaccess in the call
* /php/dispatcher.php?controllerName=Service2AjaxController&serviceName=_User/service/AddAll_UserSrv 
* The /php/dispatcher.php will:
  * Execute the config file located at /php/config.php (more info later about configuration)
  * Instantite 'Dispatcher' to handle the request. The PHP file used depends on the FactoryObject's configuration but usually it corresponds to `/include/internal/Dispatcher.php`
* The Dispather will:
  * Get the controller that will handle this request (indicate by the request param 'cntrollerName'). In this case it is 'Service2AjaxController'. NOTE : as we have said before the current code has not been fully adapted to seed.web; in the past more controllers where defined, like the one used by the presentation, but actually only the AJAX is used (except the 'actions' as we will see later)
  * Instantiate the controller (usually the file '/include/internal/controller/Service2AjaxController.php'), call its metod 'perform()' and return the result. With the current use/configuration that means:
    * **Instantiate the service** : the class pointed by the request parameter 'serviceName' (in this case '_User/service/AddAll_UserSrv') is instantiated (in this case it is resolved as the file '/_User/service/AddAll_UserSrv.php').
    * **Set the service's params** : read the channel 'php://input', convert it in JSON using json_decode() and set the result as the service's params using 'setParams(...)'.
    * **Return the service's result as JSON** : once the service has been instantiated and configured, execute it. It will return a JSON that is converted into String using json_encode and returned to the client with the header 'Content-type: application/json; charset=utf-8'
