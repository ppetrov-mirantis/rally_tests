from rally.task import context
from rally.common.i18n import _
from rally.common import logging
from rally import consts, osclients
from rally.plugins.openstack.wrappers import keystone
import copy, sys

import boto
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.bucket import Bucket
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.prefix import Prefix

LOG = logging.getLogger(__name__)


@context.configure(name="s3_context", order=1000)
class KeystoneS3Context(context.Context):
    @logging.log_task_wrapper(LOG.info, _("Enter context: `s3context`"))
    def setup(self):
        self.ks_client = keystone.wrap(osclients.Clients(self.context["admin"]["credential"]).keystone())
        self.context['host'] = self.config.get('host')

        users = self.context["users"]
        new_users = []
        for user in users:
            self.ks_client.ec2.create(user['id'], user['tenant_id'])
            ec2_creds = self.ks_client.ec2.list(user['id'])[0]

            user['ec2'] = {}
            user['ec2']['secret_key'] = ec2_creds._info['secret']
            user['ec2']['access_key'] = ec2_creds._info['access']
            user['bucket_name'] = "bucket_for_" + user['id']
            new_users.append(user)
            
        self.context["users"] = new_users

    def cleanup(self):
        pass        

    @classmethod
    def validate(cls, *args, **kwargs):
        pass
