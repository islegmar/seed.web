import json
import os
import sys
import codecs

# Convert a properties to a dictionary
def file2Dict(file):
  myprops = {}
  with codecs.open(file, 'r', encoding="utf-8") as f:
    for line in f:
      line = line.rstrip() #removes trailing whitespace and '\n' chars

      if "=" not in line: continue #skips blanks and comments w/o =
      if line.startswith("#"): continue #skips comments which contain =

      k, v = line.split("=", 1)
      myprops[k] = v
      
  return myprops

# Search in a list of dictionaries (as fields) the one that has a certain 
# value for the key
def search_dictionaries(key, value, list_of_dictionaries):
  ele = [element for element in list_of_dictionaries if element[key] == value]
  return ele[0] if ele else None

# Update a list of maps using another list of maps:
# - Adding missing elements
# - Updating
# Using key as name of the property to find the map in the list
def updateListMaps(srcListMaps, newListMaps, key):
  for newMap in newListMaps:
    if key not in newMap:
      raise Exception("{key} not found in {map}".format(key=key, map=json.dumps(newMap)))
    
    srcMap = search_dictionaries(key, newMap[key], srcListMaps)

    # Not exist previously, add it
    if not srcMap:
      # print "Append " + newMap[key]
      srcListMaps.append(newMap)
    # Update
    else:
      # print "Update " + newMap[key]
      srcMap.update(newMap)

# Testing
if __name__ == "__main__":
  srcListMaps = [ {"name" : "name1", "type"    : "type1"}, {"name" : "name2", "type" : "type2"   }, {"name" : "name3", "type" : "type3"}]
  newListMaps = [ {"name" : "name1", "newAttr" : "attr1"}, {"name" : "name2", "type" : "newType2"}, {"name" : "name4", "type" : "newType4"}]

  print """
===== BEFORE =====
[srcListMaps]
{srcListMaps} 

[newListMaps]
{newListMaps}
""".format(srcListMaps=json.dumps(srcListMaps), newListMaps=json.dumps(newListMaps))

  updateListMaps(srcListMaps, newListMaps, 'name')

  print """
===== AFTER =====
[srcListMaps]
{srcListMaps} 
""".format(srcListMaps=json.dumps(srcListMaps))

# Executes a command and check the error code
def system(cmd):
  ret = os.system(cmd)
  if ret>0:
    sys.exit(ret)