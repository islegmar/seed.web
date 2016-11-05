#!/usr/bin/python
import os
import argparse
import json

# ------------------------------------------------------------------------------
# Convert the JSON from V1 to V2
# CHANGES
# - In the actions, 'filter' is renamed as 'params'
# - In the actions a new optional element 'listFilter' has been added. If not
#   defined the list of fields in the list will be used
# - Inside the itemActions/globalActions 
#     "map" : [ 
#       { "key" : "Id_Role", "value" : "Id" } 
#     ]
#   is converted to 
#     "params" : [ 
#       { "name" : "Id_Role", "value" : "$Id" } 
#     ]
#   where the $ is to indicate it is NOT a literal.
# - Some actions are not cerated by default and they must be defined in the JSON:
#   ListAll, ModAll, DelAll   
# ------------------------------------------------------------------------------


# ==============================================================================
# Main
# ==============================================================================
def main(cfgFile):
  if not os.path.exists(cfgFile):
    raise Exception("Config file {cfgFile} does not exist.".format(**locals()))

  dstCfg=json.load(open(cfgFile))

  # filter is called now params

  # Print the output
  print json.dumps(dstCfg, indent=2, sort_keys=False)
    
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Convert the JSON config file from V1 to V2')
  parser.add_argument('cfgFile', help='The condif file V1')

  args = parser.parse_args()
  
  main(args.cfgFile)