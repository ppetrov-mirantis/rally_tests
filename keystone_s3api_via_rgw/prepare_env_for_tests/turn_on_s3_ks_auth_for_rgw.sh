
ceph_computes=$(fuel nodes | grep controller | grep ceph | cut -f 5 -d "|" | tr -d " " | sort)

for i in $ceph_computes; do
  ssh root@$i "sed -i.bkp -- '/\[client.radosgw.gateway\]/a rgw_s3_auth_use_keystone = True' /etc/ceph/ceph.conf && /etc/init.d/radosgw restart"
done


