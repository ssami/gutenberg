# https://docs.couchbase.com/python-sdk/2.5/managing-clusters.html
from couchbase.admin import Admin
from couchbase.bucket import Bucket

if __name__ == "__main__":
    adm = Admin('admin', 'password', host='localhost', port=8091)
    try:
        adm.bucket_create('model-info',
                          bucket_type='couchbase')
        # Wait for bucket to become ready
        adm.wait_ready('model-info', timeout=30)
        adm.bucket_create('feedback',
                          bucket_type='couchbase')
        # Wait for bucket to become ready
        adm.wait_ready('feedback', timeout=30)
    except:
        pass

    bucket = Bucket('couchbase://localhost:8091/feedback', username='admin', password='password')
    bucket_model = Bucket('couchbase://localhost:8091/model-info', username='admin', password='password')
    bucket_model.diagnostics()
    bucket.diagnostics()
    print("done")