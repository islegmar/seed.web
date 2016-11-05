#!/bin/bash                                                            
                                                                       
if [ $# -lt 1 ]                                                        
then                                                                   
  echo "Use : `basename $0` appName"                                   
  exit 1                                                               
fi                                                                     
                                                                       
distFile=~/apps/$1.tar                                                 
srcDir=~/apps/$1                                                       
                                                                       
if [ ! -f $distFile ]                                                  
then                                                                   
  echo "Dist file $distFile does not exist!"                           
  exit 2                                                               
fi                                                                     
                                                                       
                                                                       
function rebuildDir() {                                                
  dir=$1                                                               
  if [ -d $dir ]                                                       
  then                                                                 
    echo "Removing $dir ..."                                           
    rm -fR $dir                                                        
  fi                                                                   
                                                                       
  if [ ! -d $dir ]                                                     
  then                                                                 
    echo "Creating $dir ..."                                           
    mkdir -p $dir                                                      
  fi                                                                   
}                                                                      
                                                                       
# ------------------------------------------ Untar                     
rebuildDir "$srcDir"                                                   
                                                                       
echo "Untar $distFile into $srcDir ..."                                
tar -xf $distFile -C $srcDir                                           
echo "Done!"                                                           
