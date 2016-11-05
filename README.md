Seed.Web (RAD for web applications)
=================================
Seed.Web generate code using templates and metadata. 

In theory it will allow the generation of any kind of code (in fact, the  "only" thing it does is to generate files using templates), but it is specialized in web application. That means certain decisions have been taken:

* The templates are divided in two big categories : Front-end (FE) and Back-end (BE).
* For any of those categories, several implementations (templates) can be written. At the time of writting this, the existing implementations are:
 * FE : pure HTML based on [SOOCSS]
 * BE : a PHP implementation not based in any known framework (private code).

Index
=====
* [Clone & Code : how to use seed.web as basis for your own projects](docs/seed.web/CLONE_AND_CODE.md)
* [Multitenant : some thoughts about how can be multitenat applied](docs/seed.web/MULTITENANCE.md)
* [Install : probably outdated](docs/seed.web/INSTALL.md)
* [Model : description of JSON files](docs/seed.web/MODEL.md)
* [Not persistent fields : how to work with non persistent data](docs/seed.web/NOT_PERSISTENT_FIELDS.md)
* [Action params : actions in the JSON](docs/seed.web/ACTION_PARAMS.md)
* [BE > PHP : the PHP provider for the BE](docs/seed.web/BE/PHP.md)
* [FE > SOOCSS : the SOOCSS provider for the FE](docs/seed.web/FE-SOOCSS.md)
* [I18N : how is implemented the i18n](docs/seed.web/I18N.md)
* [Old : some old stuff](docs/seed.web/OLD.md)
