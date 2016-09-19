These tests are intended to create a workload to the Keystone S3 API.

Rally scripts create keystone projects as it's defined in a test description for each test and then start to load RADOS GW
which in its turn creates some load to the Keystone S3 API.

------------------
1. Download script prepare_controllers.sh to a master-node and start it there. 
It will turn on usage of Keystone S3 API authentication by Rados GW on all controllers.

2. Download script prepare_node.sh to a dedicated compute-node.
It will install rally 0.6.0, download the rest of the test infrastructure and properly install it.
Before it started it's necessary to find section "# configure rally" and to set a controller-host for getting an openrc-file.

3. !!! Don't forget to change Keystone IP in Rally JSON test configurations !!!
------------------

