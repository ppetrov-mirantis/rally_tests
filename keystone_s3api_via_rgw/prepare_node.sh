# configure node environment
apt-get update && apt-get install --yes --force-yes python-pip subversion
pip install rally==0.6.0 filechunkio

# download tests
## create directories
mkdir -p ~/files_to_upload ~/downloaded_files ~/.rally/plugins
## download rally plugins
cd ~/.rally/plugins
svn export https://github.com/ppetrov-mirantis/rally_tests/trunk/keystone_s3api_via_rgw/plugins_s3
svn export https://github.com/ppetrov-mirantis/rally_tests/trunk/keystone_s3api_via_rgw/tests
## download test data
svn export https://github.com/ppetrov-mirantis/rally_tests/trunk/keystone_s3api_via_rgw/test_data ~/
tar xf ~/test_data/kern_source.tar -C ~/files_to_upload

# configure rally
scp node-3:~/openrc .
. openrc admin admin
rally-manage db recreate
rally deployment create --fromenv --name=existing
rally deployment check
