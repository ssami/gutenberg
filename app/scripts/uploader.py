from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
import sys
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', dest='endpoint', default='127.0.0.1:9000')
    parser.add_argument('--access', dest='access_key', default='admin')
    parser.add_argument('--secret', dest='secret_key', default='password')
    parser.add_argument('--bucket', dest='bucket', required=True)
    parser.add_argument('--object', dest='object_name', required=True)
    parser.add_argument('--path', dest='path', required=True)
    args = parser.parse_args()
    minioClient = Minio(
        endpoint=args.endpoint,
        access_key=args.access_key,
        secret_key=args.secret_key,
        secure=False
    )
    try:
        minioClient.make_bucket(args.bucket)
    except BucketAlreadyOwnedByYou as err:
        print(err)
    except BucketAlreadyExists as err:
        print(err)
    except ResponseError as err:
        raise

    try:
        minioClient.fput_object(args.bucket, args.object_name, args.path)
        print("Success, model uploaded")
    except ResponseError as e:
        print(e)

