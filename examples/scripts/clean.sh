# OneView Appliance hostname or IP address
HOST=${HOST:=oneview}
# OneView Appliance username
USER=${USER:=Administrator}
# OneView Appliance password
PASS=${PASS:=PASSWORD}
# Enclosure OA hostname or IP address
ENC_ADDR=${ENC_ADDR:=172.18.1.11}
# Enclosure OA username
ENC_USR=${ENC_USR:=Administrator}
# Enclosure OA password
ENC_PASS=${ENC_PASS:=PASSWORD}

echo  -- Removing profiles
./define-profile.py -a $HOST -u $USER -p $PASS -d
echo  -- Removing volumes
./add-volume.py -a $HOST -u $USER -p $PASS -d
echo  -- Removing Volume Templates
./add-volume-template.py -a $HOST -u $USER -p $PASS -d
echo  -- Removing Storage Pools
./add-storage-pool.py -a $HOST -u $USER -p $PASS -d
echo  -- Removing Storage Systems
./add-storage-system.py -a $HOST -u $USER -p $PASS -d
echo  -- Removing Enclosures
./del-enclosure.py -a $HOST -u $USER -p $PASS -d
echo  -- Removing Enclosure Groups
./del-enclosure-group.py -a $HOST -u $USER -p $PASS -d
echo  -- Removing Logical Interconnect Groups
./del-logical-interconnect-groups.py -a $HOST -u $USER -p $PASS -d
echo  -- Removing Network Sets
./del-network-set.py -a $HOST -u $USER -p $PASS -d
echo  -- Removing Logical Networks
./del-network.py -a $HOST -u $USER -p $PASS -d
