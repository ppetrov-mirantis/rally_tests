These tests are intended to create a workload to the Keystone S3 API.

Rally scripts create keystone projects as it's defined in a test description for each test and then start to load RADOS GW
which in its turn creates some load to the Keystone S3 API.
