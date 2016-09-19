# set up RGW to use Keystone S3 API for authentication
ceph_controllers=$(fuel nodes | grep controller | cut -f 5 -d "|" | tr -d " " | sort)
for i in $ceph_controllers; do
  ssh root@$i "sed -i.bkp -- '/\[client.radosgw.gateway\]/a rgw_s3_auth_use_keystone = True' /etc/ceph/ceph.conf && /etc/init.d/radosgw restart"
done

