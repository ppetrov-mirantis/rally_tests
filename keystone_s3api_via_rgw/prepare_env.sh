# set up RGW to use Keystone S3 API for authentication
ceph_computes=$(fuel nodes | grep controller | grep ceph | cut -f 5 -d "|" | tr -d " " | sort)

for i in $ceph_computes; do
  ssh root@$i "sed -i.bkp -- '/\[client.radosgw.gateway\]/a rgw_s3_auth_use_keystone = True' /etc/ceph/ceph.conf && /etc/init.d/radosgw restart"
done

# configure node environment
apt-get update && apt-get install --yes --force-yes python-pip subversion
pip install rally==0.6.0 filechunkio

# download tests
cd ~/.rally
svn export https://github.com/ppetrov-mirantis/rally_tests/trunk/keystone_s3api_via_rgw
