import os, sys, math, uuid
from rally.task import scenario
from rally.task import atomic
from rally.common import logging
from rally import consts

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.bucket import Bucket
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.prefix import Prefix

from filechunkio import FileChunkIO

LOG = logging.getLogger(__name__)

class KeystoneS3API(scenario.Scenario):

    #@atomic.action_timer("connect")
    def connect(self):                
        cred = self.context['user']['ec2']
        self.s3_connection = S3Connection(
            aws_access_key_id=cred['access_key'],
            aws_secret_access_key=cred['secret_key'],
            host=self.context['host'],
            port=8080,
            is_secure=False,
            calling_format=OrdinaryCallingFormat())

    def disconnect(self):
        self.s3_connection.close()

    @atomic.action_timer("create_bucket")
    def create_bucket(self):
        self.bucket = self.s3_connection.create_bucket(self.context['user']['bucket_name'])
        self.bucket.make_public()

    @atomic.action_timer("delete_bucket")
    def delete_bucket(self):
        #self.bucket.delete()
        self.s3_connection.get_bucket(self.context['user']['bucket_name']).delete()

    @atomic.action_timer("upload_small_files")
    def upload_small_files(self):
        key = Key(self.s3_connection.get_bucket(self.context['user']['bucket_name']))
        source_path = "/root/files_to_upload/kern_source/"
        dest_path = "/tmp/"
        files = os.listdir(source_path)
        for file_name in files:
            key.key = dest_path + file_name
            key.set_contents_from_filename(source_path + file_name) # s3 requested operation
    
    @atomic.action_timer("upload_1_small_file")
    def upload_1_small_file(self):
        key = Key(self.s3_connection.get_bucket(self.context['user']['bucket_name']))
        key.key = "/tmp/aes_generic.c" 
        key.set_contents_from_filename("/root/files_to_upload/kern_source/aes_generic.c") # s3 requested operation

    @atomic.action_timer("upload_big_file")
    def upload_big_file(self):
        source_file_to_upload = "/root/files_to_upload/CentOS-7-x86_64-Everything-1511.iso"
        source_size = os.stat(source_file_to_upload).st_size
        
        # Create a multipart upload request
        bkt = self.s3_connection.get_bucket(self.context['user']['bucket_name'])
        mpu_handler = bkt.initiate_multipart_upload(os.path.basename(source_file_to_upload))

        # Use a chunk size of ...
        chunk_size = '5242880'
        chunk_count = int(math.ceil(source_size / float(chunk_size)))

        # Send the file parts, using FileChunkIO to create a file-like object
        # that points to a certain byte range within the original file. We
        # set bytes to never exceed the original file size.
        for chunks_transferred in range(chunk_count):
            offset = chunk_size * chunks_transferred
            bytes = min(chunk_size, source_size - offset)
            with FileChunkIO(source_file_to_upload, 'r', offset=offset, 
                             bytes=bytes) as file_part:
                mpu_handler.upload_part_from_file(file_part, part_num = chunks_transferred + 1)
            # Finish the upload
            mpu_handler.complete_upload()

    @atomic.action_timer("download_small_files")
    def download_small_files(self):
        '''get files'''
        path = "/root/downloaded_files/" + str(uuid.uuid4()) + "/"
        os.mkdir(path, 0755)
        
        bkt = self.s3_connection.get_bucket(self.context['user']['bucket_name'])
        bucket_content = bkt.list(prefix='', delimiter='')
        for bkt_item in bucket_content:
            key = self.bucket.get_key(bkt_item)
            fl = path + str(uuid.uuid4()) + '.tmp'
            key.get_contents_to_filename(fl)

        os.system("rm -rf " + path)

    @atomic.action_timer("list_files")
    def list_files(self):        
        # keystone s3 requested operation - only in case when bucket_content will be requested for reading
        # so, we need to iterate over this list
        bkt = self.s3_connection.get_bucket(self.context['user']['bucket_name'])
        bucket_content = bkt.list(prefix='', delimiter='')
        for bkt_item in bucket_content:
            pass

    @atomic.action_timer("delete_bucket_files_sequentially")
    def delete_bucket_files_sequentially(self):
        '''cleans all files sequentially'''
        bkt = self.s3_connection.get_bucket(self.context['user']['bucket_name'])
        bucket_content = bkt.list(prefix='', delimiter='')
        for bkt_item in bucket_content:
            bkt_item.delete()

    def delete_bucket_files_at_once(self):
        '''cleans all files at once'''
        # s3 requested operation - in this case - only deletion requested because of using already created bucket object 
        #self.bucket.delete_keys(self.bucket.list())
        bkt = self.s3_connection.get_bucket(self.context['user']['bucket_name'])
        bkt.delete_keys(bkt.list())

    @scenario.configure()
    def test_all(self):
        self.connect()
        self.create_bucket()
        self.upload_small_files()
        self.list_files()
        self.download_small_files()
        self.upload_big_file()
        self.list_files()
        self.delete_bucket_files_sequentially()
        self.list_files()
        self.delete_bucket()
        self.disconnect()

    @scenario.configure()
    def test_01(self):
        self.connect() # no s3 request
        self.create_bucket() #s3 requested operation inside
        self.upload_small_files() # s3 requested operations inside
        self.list_files() # s3 requested operation
        self.download_small_files() # s3 requested operations inside
        self.list_files() # s3 requested operation
        self.delete_bucket_files_sequentially() # 2 s3 requested operations inside
        self.list_files() # s3 requested operation
        self.delete_bucket()
        self.disconnect()
        
    @scenario.configure()
    def test_01_1(self):
        try:
            self.connect() # no s3 request
            self.create_bucket() #s3 requested operation inside
            self.upload_1_small_file() # s3 requested operations inside
            self.list_files() # s3 requested operation
            self.download_small_files() # s3 requested operations inside
            self.list_files() # s3 requested operation
            self.delete_bucket_files_at_once() # 2 s3 requested operations inside
            self.list_files() # s3 requested operation
            self.delete_bucket()
            self.disconnect()
        except Exception,e:
            print e
            print "username: " + self.context['user']['credential'].username
            print "password: " + self.context['user']['credential'].password
            print "ec2 access_key: " + self.context['user']['ec2']['access_key']
            print "bucket_name: " + self.context['user']['bucket_name']

    @scenario.configure()
    def test_02(self):
        self.connect()
        self.create_bucket() #s3 requested operation inside
        self.upload_big_file()
        self.list_files()
        self.delete_bucket_files_sequentially()
        self.list_files()
        self.delete_bucket()
        self.disconnect()

    @scenario.configure()
    def test_03(self):
        self.connect()
        self.create_bucket() #s3 requested operation inside
        self.list_files()
        self.delete_bucket()
        self.disconnect()
