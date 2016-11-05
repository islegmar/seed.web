Clone & Code : create your own project
======================================

When creating a new project based on seed.web, these are the steps:

* Clone seed.web

  `git clone https://github.com/islegmar/seed.web.git myPrj`

* Create the setenv.sh based on a template and adaptt it. For example, if we are going to use
  * FE : SOOCSS
  * BD : PHP
  * DB : MySQL

  then:

  <pre>
  cp setenv.sh.SOOCSS_PHP setenv.sh
  Edit the file setenv.sh and adapt the paths
  </pre>

While developing your ouwn project, those are the main actions you will have to do:

* **New entity** : when creating a new entity, you will have to create a new JSON file.

  <pre>
  model/<MyEntity>.json
  </pre>  
* **SQL config data** : `model/custom/ModuleCustom/Database/<MySQL>/<MyEntity>/{sqlOrder}-cfgData_Lang.sql` 
* **SQL test data** : `model/custom/ModuleCustom/Database/<MySQL>/<MyEntity>/{sqlOrder}-testData_Lang.sql` 
* **BE : Custom code** : `model/custom/ModuleCustom/BE/<PHP>/<MyEntity>/<file to update>` 
* **FE : Custom code** : `model/custom/ModuleCustom/FE/<SOOCSS>/<MyEntity>/<file to update>` 

seed.web : create stable versions
-------------------------------

* Drecide the id for the new version (newTag)
* Update the file LOG.txt with the last changes:

  <pre>
  mv LOG.txt LOG.txt.tmp
  cd scripts
  python logs.py --tag newTag > ../LOG.txt
  cd ..
  cat LOG.txt.tmp >> LOG.txt
  </pre>

  Edit LOG.txt file and follow the instructions

* Tag the version new version and push

  <pre>
  git add LOG.txt                               
  git commit -m 'Added LOG for newTag'
  git tag -a newTag (1)
  git push origin develop --tags                      
  </pre>

  (1) In the tag commit message put


  <pre>
  See LOG.txt for info
  
  Overview:
  Copy the info from LOG.txt
  </pre>  

Your project : add latest changes from seed.web
---------------------------------------------

Once you have cloned, you can update your own project with the latest changes from seed.web:

* (Only Once) : If not alreday done, add the repo seed.web to your project
  
  <pre>
  git remote add seed.web https://github.com/islegmar/seed.web.git
  </pres

* (Only Once) : If not alreday done, create a specific branch `updSeedWeb` where seed.web with will be merged & tested before goes to develop

  <pre>
  git checkout develop  
  git checkout -b updSeedWeb
  git push origin updSeedWeb
  </pre>

* Update updSeedWeb with the latest from develop

  <pre>
    git checkout develop
    git pull origin develop
    git checkout updSeedWeb
    git push origin updSeedWeb
    git merge develop
  </pre>  

* Fetch (no not merge yet) the latest version of seed.web locally with tags:

  <pre>
    git fetch seed.web develop --tags
  </pre>  

* Find the latest tag in seed.web (newTag)

  <pre>
    git tag | grep seed.web
  </pre>  

* Merge seed.web/develop -> updSeedWeb

  <pre>
    git merge --no-ff seed.web/develop
  </pre>
   
* Resolve the conflicts. You can see the list running

  <pre>
  git status
  </pre>

* Finish the commit running

  <pre>
  git commit
  </pre>

  In the commit message put a reference to the seed.web's version merged

  <pre>
    Merged newTag
  </pre> 

* Merge to develop

  <pre>
    git checkout develop
    git merge --no-ff updSeedWeb
  </pre>

   
* Push the changes

  <pre>
    git push origin develop
  </pre>
