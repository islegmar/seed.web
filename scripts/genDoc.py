# ===================================================
# Convert the config from the customer into YAML.
# ===================================================
import os
import argparse
from argparse import RawTextHelpFormatter
import fnmatch
from lxml import etree
import zipfile
import shutil
import codecs
import csv
import re
import sys
import yaml
import json
import copy
import shutil
import glob
import utils

def genDoc(fOdt, fXslt, fXml, fOut):
  if not os.path.isfile(fOdt):
    raise Exception("File {fOdt} dies not exists!".format(**locals()))
  if not os.path.isfile(fXslt):
    raise Exception("File {fXslt} dies not exists!".format(**locals()))
  if not os.path.isfile(fXml):
    raise Exception("File {fXml} dies not exists!".format(**locals()))
  if os.path.isfile(fOut):
    os.remove(fOut)

  unzipFolder="/tmp/" + os.path.basename(fOdt)
  if os.path.exists(unzipFolder):
    shutil.rmtree(unzipFolder)
  if not os.path.exists(unzipFolder):
    os.makedirs(unzipFolder)
  
  # Unzip
  zip_ref = zipfile.ZipFile(fOdt, 'r')
  zip_ref.extractall(unzipFolder)
  zip_ref.close()

  fContentXml=os.path.join(unzipFolder, 'content.xml')
  
  xslt_content = open(fXslt).read()
  xslt_root = etree.XML(xslt_content)
  dom = etree.parse(fContentXml)
  transform = etree.XSLT(xslt_root)
  # fXml must have the form URI : file:///absolute/path
  result = transform(dom, fData=etree.XSLT.strparam('file://' + os.path.abspath(fXml)))
  f = open(fContentXml, 'w')
  f.write(str(result))
  f.close()

  # Zip
  shutil.make_archive(fOut, 'zip', unzipFolder)
  # It adds the 'zip' extension, remove it
  if os.path.isfile(fOut + '.zip'):
    os.rename(fOut + '.zip', fOut)


  # from shutil import copyfile
  # zf = zipfile.ZipFile(fOut, "w")
  # for dirname, subdirs, files in os.walk(unzipFolder):
  #   zf.write(dirname[len(unzipFolder)+1:])
  #   for filename in files:
  #     zf.write(os.path.join(dirname, filename)[len(unzipFolder)+1:])
  # zf.close()

  print ("File %s created" % (fOut))

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
  parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description='''
Generates a document based on:
- odt_file with the template
- xsl_file with the transformations
- xml_file with the dat

Example python genDoc.py --odt ../data/genDocs/list.odt --xsl ../data/genDocs/list.xsl --xml ../data/genDocs/list.xml --out /tmp/result.odt
''')
  parser.add_argument('--odt', help='odt file with the template')
  parser.add_argument('--xsl', help='xslt file with the transform')
  parser.add_argument('--xml', help='xml file with the data')
  parser.add_argument('--out', help='Out file')
  parser.add_argument('--csv', help='File with the CSV')

  args = parser.parse_args()

  genDoc(args.odt,args.xsl, args.xml, args.out)
