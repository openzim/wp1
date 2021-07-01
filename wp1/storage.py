import io
from kiwixstorage import KiwixStorage

s3 = KiwixStorage(
    "https://s3.us-west-1.wasabisys.com/?keyId=I9BI3Q2WJ228SZMTZIMJ&secretAccessKey=Ot8ldPPetvDEX5i7nCCuA2e5oYqa2prsmXGL0Fnb&bucketName=org-kiwix-dev-wp1"
)
s3.check_credentials(list_buckets=True, bucket=True, write=True, read=True)

data = io.BytesIO()
data.write(b"Hello world")
s3.upload_fileobj(data, key="test.txt")
s3.has_object("test.txt")
s3.download_file(key="test.txt", fpath="test.txt")
s3.delete_object(key="test.txt")
