#!/bin/bash

if [ $# -lt 1 ]
then
  echo "Use : `basename $0` newVersion"
  exit 1
fi

newVersion=$1

cat<<EOF > genVersion.1
[ -f LOG.txt.tmp ] && rm LOG.txt.tmp
mv LOG.txt LOG.txt.tmp
cd scripts
python logs.py --tag $newVersion > ../LOG.txt
cd ..
cat LOG.txt.tmp >> LOG.txt

echo "Edit LOG.txt and follow the instructions"
EOF

cat<<EOF > genVersion.2
# Build the commit message
cat<<EOF2>/tmp/message.txt
See LOG.txt for info
  
EOF2
awk '
/^Detail list of changes/ { exit 0; }
/^Overview/ { doPrint=1; }
doPrint
' LOG.txt >> /tmp/message.txt
# git add LOG.txt                               
# git commit -m 'Added LOG for $newVersion'
# git tag -a $newVersion -F /tmp/message.txt
# git push origin develop --tags 

echo "The new version $newVersion has been created!"
EOF

cat<<EOF
Instructions:
+ Run . ./genVersion.1
+ Edit LOG.txt and follow the instructions
+ Run . ./genVersion.2
EOF
