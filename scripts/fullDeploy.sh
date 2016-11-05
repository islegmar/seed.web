rm -fR ../build/

# Web
opts=""
opts="$opts --createDB"

echo "[Web] opts : $opts ..."
python createWebProject.py $opts

# Modules
opts=""
opts="$opts --all"
opts="$opts --createModuleTable"
opts="$opts --insertTestData"
opts="$opts --recreatePermissions"
opts="$opts --recreateI18N"
# opts="$opts --updateTblModule"

echo "[Modules] opts : $opts ..."
python createWebModule.py --all $opts
