================================================================================
V2 - RELEASE NOTES
================================================================================
[12/10/13]
Create internalPHP_V2 that will contain ONLY server code (php).
This folder is reference in the code as INTERNAL_ROOT_DIR (another name 
as INTERNAL_SERVER_ROOT_DIR should be better but we shpuld change too much)
The client code (JS, CSS,...) is removed from this folder and stored in internalClient

IMPORTANT : This is a major release with a lot of changes and impact in the 
applications that already exist

First, we distinguis between filters and managers:
- Filter : class that NEED to be execute for EVERY REQUEST. There are FEW of 
  them, basically those related with security 
- Managers : singleton that need to be configured and then can be used for the 
  entire application. There are a LOT of them. Until now the approach was to 
  configure all of them for every request, even when they are not used, but this
  is not efficient.
  
Actual approach:
- All classes are instantiated through FactoryObjects. 
- The managers (singletons) are regular classes but FactoryObjects keep only one
  instance of them
- Only when the class is used, it is configured.

Migration notes:

Change
  FactoryObject::newObject(...)
for
  FactoryObject::newObject()

All singletons are obtained via FactoryObject
FactoryObject::getInstance()->    FactoryObject::
FileManager::getInstance()        FactoryObject::newObject('FileManager')
ViewRender::getInstance()         FactoryObject::newObject('ViewRender')
WebApp::getInstance()             FactoryObject::newObject('WebApp')
DBFileMgr::getInstance()          FactoryObject::newObject('DBFileMgr')


WebSession::getInstance()  -> FactoryObject::newObject('WebSession')
     
check also
AnonymousPrincipal
LoginFilter
LogoutFilter
AnonymousUserFilter
SecurityFilter

- Review both config.php and the configs in config/*, they have changed
- Some unused files are _OLD* 
  + ServiceAuthenticated
  + DBBeanFactory
  + AllBeanSrv
  + Folder startup/

- Some code from projects have been added to the generic
  + controller/GetFileCtr
  + controller/ImportI18NCtr
  + controller/ImportAppCSSCtr
  + utils/DBFileMgr
  + service/SaveBeanSrv                 -> renamed to SaveDBFileSrv
  + service/GetBeanSrv                  -> renamed to GetDBFileSrv
  + service/ListBeanSrv.php             -> renamed to ListDBFileSrv.php
  + service/GetTranslations4BeanSrv.php -> renamed to GetTranslations4DBFileSrv.php
  + controller/BorrarDBBeanTypeCtr.php  -> changed DBBean for DBFile
  + controller/DetailBeanCtr.php        -> changed DBBean for DBFile
  + controller/GetDBBeanFileCtr.php     -> changed DBBean for DBFile 
  + controller/ImportDBBeanCtr.php      -> changed DBBean for DBFile      
  + controller/ListBeanCtr.php          -> changed DBBean for DBFile

================================================================================
V1 - RELEASE NOTES
================================================================================
All paths to other files can be
- To external => $_SERVER['DOCUMENT_ROOT'] . '/external/....'
- To other files in interal => relative paths
- To files in the application. In this case, a file that uses one of the internals
  has been loaded BEFORE and it has loaded the application, that means the global
  variable APP_ROOT_DIR pointing to the root exists => APP_ROOT_DIR . '/php/....'
  
