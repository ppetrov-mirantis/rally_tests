apt-get update && apt-get install --yes --force-yes python-pip subversion
pip install rally==0.6.0 filechunkio

mkdir ~/downloaded_files ~/files_to_upload ~/.rally

cd ~/.rally
svn export https://github.com/ppetrov-mirantis/rally_tests/trunk/keystone_s3api_via_rgw/plugins
svn export https://github.com/ppetrov-mirantis/rally_tests/trunk/keystone_s3api_via_rgw/tests
