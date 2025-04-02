#!/bin/sh

# Configure MinIO client and create bucket
/usr/bin/mc config host add dev_minio http://minio:9000 minio_key minio_secret #configure client
/usr/bin/mc mb dev_minio/org-kiwix-dev-wp1 --ignore-existing #create bucket
/usr/bin/mc policy set public dev_minio/org-kiwix-dev-wp1 #set policy

exit 0
