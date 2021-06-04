from hdfs.ext.kerberos import KerberosClient
from hdfs.util import HdfsError

# This is a temporary setting, required only if you run the code from inside a notebook, it shouldn't be required for batch code.
os.environ["REQUESTS_CA_BUNDLE"] = "/etc/pki/tls/certs/ca-bundle.trust.crt"

# Create the 'client' object to interact with HDFS
# Depending on which one is the active name node you need to use one of the two name nodes
try:
    client = KerberosClient('https://<namenode1-full-uri>:50470', mutual_auth='DISABLED')
    fl = client.list(hdfs_path='/')
except HdfsError:
    client = KerberosClient('https://<namenode2-full-uri>:50470', mutual_auth='DISABLED')
except:
    raise
    
# List all files inside a directory.
fnames = client.list(hdfs_path='/user/shivamg')
print(fnames)

# Retrieve a file or folder content summary.
content = client.content(hdfs_path='/user/shivamg')
print(content)

# Retrieving a file or folder status.
status = client.status(hdfs_path='/user/shivamg')
print(status)

# Renaming ("moving") a file.
client.rename(hdfs_src_path='/user/shivamg/test.csv', hdfs_dst_path='/user/shivamg/testRenamed.csv')

# Upload a file or folder to HDFS.
client.upload(hdfs_path='/user/shivamg/test.csv', local_path='/home/shivamg/test.csv', n_threads=5, overwrite=True)

# Download a file or folder locally.
client.download(hdfs_path='/user/shivamg/test.csv', local_path='/home/shivamg/test2.csv', overwrite=True, n_threads=5)

# Deleting a file or folder.
client.delete(hdfs_path='/user/shivamg/testRenamed.csv', recursive=False)

# Loading a file in memory.
with client.read(hdfs_path='/user/shivamg/test.csv') as reader:
  lineText = reader.read()
print lineText



# Writing files to HDFS is done using the write() method which returns a file-like writable object. 
# Writing part of a file (only lines shorter than 20 characters in this examples). See method documentation for other examples
client.delete(hdfs_path='/user/marcol/textFile2.txt', recursive=False)
with open('/home/marcol/test.csv') as reader, client.write(hdfs_path='/user/marcol/textFile2.txt') as writer:
  for line in reader:
    if len(line)<20:
      writer.write(line)
