Seed.Web (RAD for web applications)
=================================
Seed.Web generate code using templates and metadata. 

In theory it will allow the generation of any kind of code (in fact, the  "only" thing it does is to generate files using templates), but it is specialized in web application. That means certain decisions have been taken:

* The templates are divided in two big categories : Front-end (FE) and Back-end (BE).
* For any of those categories, several implementations (templates) can be written. At the time of writting this, the existing implementations are:
 * FE : pure HTML based on [SOOCSS]
 * BE : a PHP implementation not based in any known framework (private code).
