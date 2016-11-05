#!/usr/bin/python

import os
import sys
import argparse
import utils
import re
import subprocess 
import datetime

def _execCmd(cmd, oneLineOnly=False):
  p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  lines = p.stdout.readlines()
  retval = p.wait()

  return lines[0].rstrip('\n') if oneLineOnly else lines

def logs(idLastCommit, idNewCommit="<current>"):
  now=datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
  print """
{now} : {idNewCommit} (previous : {idLastCommit})
================================================================================

Overview            
--------

[TBD]

Detail list of changes
----------------------
""".format(**locals())

  #cmd='git log --since="2017-07-01" --pretty=format:"%h"'
  cmd='git log {idLastCommit}.. --pretty=format:"%h"'.format(**locals())
  commits = _execCmd(cmd)
  for commit in commits:
    cmd = 'git log -n 1 --pretty=format:"%s" ' + commit
    message = _execCmd(cmd, True)
    if not message.startswith("Merge branch "):
      # ------------------------------------------------------ Date and Comments    
      # The lines here returned have the format
      #
      # commit e76e60c3e9b7adc88bf089f1cd7d3c1185b1bf29
      # Author: Isidoro Legido Martinez <islegmar@gmail.com>
      # Date:   2015-10-10 
      # [empty line]
      # [4spaces]Comment
      # [4spaces]...
      # [4spaces]Comment
      cmd = 'git log -n 1 --date=short ' + commit
      for idx,line  in enumerate(_execCmd(cmd)):
        line = line.rstrip('\n')

        # The commit id
        if idx==0:
          commit = line[7:]

        # Print the date
        if idx==2:
          # date has the format YYYY-MM-DD and we're going to transform to
          # DD/MM/YYYY
          date = line[8:]
          print '[' + date[8:10] + '/' + date[5:7] + '/' + date[0:4] + '] ' + commit + '\n' 

        # The comments start 
        if idx > 3:
          print line[4:]
      print""
       
      # ---------------------------------------------------------- List fo Files    
      files=_execCmd('git show --pretty="format:" --name-only ' + commit)
      for file in files:
        if not file.isspace():
          print file,
      print ""  
      #print commit,      

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Show logs from git')
  parser.add_argument('commit', nargs="?", help='The id of the last commit ')
  parser.add_argument('--tag', help='The id of the NEW tag')

  args = parser.parse_args()
  
  # If we have not specified a commit ID, the last tag will be used
  if not args.commit:
    # Get the ID of the last tag, so we can see the logs between this tag and the 
    # current point that will be tagged with newTag   
    cmd="git describe --abbrev=0 --tags"
    lastTag=_execCmd(cmd, True)

    # Error if we have not specified the new tag (used to document)
    if not args.tag:
      raise Exception("No new tag specified. Please use --tag (last tag was {lastTag})".format(**locals()))

    # This is the tag we WILL put
    newTag=args.tag

    logs(lastTag, newTag)
  # Let's see the logs since una commit until now
  else:
    logs(args.commit)
