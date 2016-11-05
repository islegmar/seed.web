# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------
import os
import shutil

# Return 'value' if defined, otherwise tries environment and default value
def getValue(value, envVar, defVal=None):
  if value is not None:
    return value
  else:
    if defVal is not None:
      return defVal
    else:  
      if envVar:
        if not envVar in  os.environ:
          raise Exception ("Environment variable '{envVar}' not defined".format(**locals()))
        return os.environ[envVar]  
      else:
        raise Exception("Nor possible to retrieve value")

# Recreate a folder
def recreateDir(dir):
  if os.path.exists(dir):
    shutil.rmtree(dir)

  if not os.path.exists(dir):
    os.makedirs(dir)